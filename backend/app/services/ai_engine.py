"""AI Engine — supports Claude (Anthropic) and DeepSeek/OpenAI-compatible APIs."""

import json
from ..config import settings
from ..utils.prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_EN, SYSTEM_PROMPT_ZH, build_user_prompt, detect_language

# Detect API type from key prefix
_API_KEY = settings.ANTHROPIC_API_KEY
_IS_ANTHROPIC = _API_KEY.startswith("sk-ant-")
CACHE_THRESHOLD_TOKENS = 8000


def _get_openai_client():
    """Create an async OpenAI-compatible client (works for DeepSeek too)."""
    from openai import AsyncOpenAI
    return AsyncOpenAI(api_key=_API_KEY, base_url="https://api.deepseek.com/v1")


async def _call_openai(system_prompt: str, user_content: str, model: str, max_tokens: int) -> str:
    client = _get_openai_client()
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content


async def _call_anthropic(system_prompt: str, user_content: str, model: str, max_tokens: int) -> str:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=_API_KEY)
    message = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return "\n".join(block.text for block in message.content if block.type == "text")


async def generate_study_notes(
    parsed_content,
    title: str = "",
    detail_level: str = "default",
    custom_notes: str = "",
    model: str = "claude-sonnet-4-6-20250514",
    max_tokens: int = 4096,
) -> str:
    # Detect language from extracted text
    lang = "en"
    if isinstance(parsed_content, dict):
        all_text = " ".join(s.get("content", "") for s in parsed_content.get("sections", []))
        lang = detect_language(all_text)
    system_prompt = SYSTEM_PROMPT_ZH if lang == "zh" else SYSTEM_PROMPT_EN

    user_prompt = build_user_prompt(parsed_content, title, detail_level, custom_notes)

    if _IS_ANTHROPIC:
        return await _call_anthropic(system_prompt, user_prompt, model, max_tokens)
    else:
        return await _call_openai(system_prompt, user_prompt, "deepseek-chat", max_tokens)


async def generate_similar_question(
    question: str,
    answer: str,
    subject: str = "",
    model: str = "claude-sonnet-4-6-20250514",
    max_tokens: int = 1024,
) -> dict[str, str]:
    subject_hint = f"（科目：{subject}）" if subject else ""
    system_prompt = "你是一位出题老师，根据给出的题目和答案，生成一道类似但不完全相同的练习题。"

    user_prompt = f"""原题{subject_hint}：
{question}

原题答案：
{answer}

请生成一道考察相同知识点的类似题目，并附上参考答案。
输出格式：
## 题目
[题目内容]

## 参考答案
[答案内容]"""

    if _IS_ANTHROPIC:
        text = await _call_anthropic(system_prompt, user_prompt, model, max_tokens)
    else:
        text = await _call_openai(system_prompt, user_prompt, "deepseek-chat", max_tokens)

    result = {"question": "", "answer": ""}
    if "## 题目" in text and "## 参考答案" in text:
        parts = text.split("## 参考答案")
        result["question"] = parts[0].replace("## 题目", "").strip()
        result["answer"] = parts[1].strip()
    else:
        result["question"] = text
        result["answer"] = ""

    return result
