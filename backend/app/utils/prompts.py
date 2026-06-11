"""Prompt templates for study note generation."""


def detect_language(text: str) -> str:
    """Detect dominant language by character ratio."""
    if not text:
        return "en"
    chinese_chars = sum(1 for c in text if '一' <= c <= '鿿')
    total_chars = len(text.replace(' ', '').replace('\n', ''))
    if total_chars > 0 and chinese_chars / max(total_chars, 1) > 0.3:
        return "zh"
    return "en"


SYSTEM_PROMPT_EN = (
    "You are a study notes assistant. Your job is to CLARIFY and EXPLAIN the document, "
    "NOT to reorganize or restructure it.\n\n"
    "CRITICAL RULES:\n"
    "- Go through EVERY slide and section - do NOT skip or omit any content\n"
    "- Use ALL available output space to cover every slide fully\n"
    "- Do NOT add general intro or outro - go straight into the content\n"
    "- Cover every section completely from start to finish. Do not summarize or skip.\n"
    "- IMPORTANT: Complete each section before moving to the next. Finish the entire response.\n"
    "- PRESERVE the original document structure and slide order exactly as-is\n"
    "- Do NOT create your own outline, sections, or reorganized framework\n"
    "- Simply go through the content in order, clarifying unclear parts\n"
    "- Explain technical terms and concepts in plain language\n"
    "- Bold key terminology\n"
    "- Add brief clarifications where the original text is vague or complex\n"
    "- Keep all original data, numbers, and formulas\n"
    "- Use the SAME LANGUAGE as the document\n"
    "- Output in clean Markdown suitable for reading"
)

SYSTEM_PROMPT_ZH = (
    "You are a study notes assistant. Your job is to CLARIFY and EXPLAIN, NOT reorganize.\n\n"
    "Rules:\n"
    "- PRESERVE the original document structure and order exactly\n"
    "- Do NOT create outlines or restructure the content\n"
    "- Go through content in original order, clarifying unclear parts\n"
    "- Explain technical terms in plain language, bold key terms\n"
    "- Keep all original data and formulas\n"
    "- Output in the SAME LANGUAGE as the document"
)

SYSTEM_PROMPT = SYSTEM_PROMPT_EN

DETAIL_LEVELS = {
    "brief": (
        "BRIEF MODE: Keep notes concise.\n"
        "- Knowledge Outline: top-level framework only (max 5 items)\n"
        "- Key Points: 3-5 most critical concepts, 1 sentence each\n"
        "- Skip Key Concepts, Exam Tips, and Self-Assessment sections entirely\n"
    ),
    "default": (
        "DEFAULT MODE: Standard detail level.\n"
        "- Knowledge Outline: full framework\n"
        "- Key Points: 5-8 concepts, 2-3 sentences each\n"
        "- Key Concepts: explain major terms\n"
        "- Exam Tips: include if content supports it\n"
        "- Self-Assessment: 3 questions\n"
    ),
    "detailed": (
        "DETAILED MODE: Maximum depth.\n"
        "- Knowledge Outline: exhaustive framework with sub-points\n"
        "- Key Points: 8-12 concepts with full explanations\n"
        "- Key Concepts: explain ALL technical terms, include comparison tables\n"
        "- Exam Tips: comprehensive tips with star ratings and mnemonics\n"
        "- Self-Assessment: 5 questions with detailed reference answers\n"
    ),
}


def build_user_prompt(parsed_content: dict, title: str = "", detail_level: str = "default", custom_notes: str = "") -> str:
    doc_title = title or parsed_content.get("title", "Untitled Document")

    parts = [f"# Document Title: {doc_title}\n"]
    parts.append("Here is the document content:\n")

    sections = parsed_content.get("sections", [])
    for sec in sections:
        heading = sec.get("heading", "")
        level = sec.get("level", 2)
        content = sec.get("content", "")
        tables = sec.get("tables", [])

        prefix = "#" * min(level + 1, 4)
        parts.append(f"{prefix} {heading}\n")
        parts.append(content)
        parts.append("")

        for table in tables:
            parts.append(table)
            parts.append("")

    detail_instruction = DETAIL_LEVELS.get(detail_level, DETAIL_LEVELS["default"])
    parts.append("---")
    parts.append(detail_instruction)

    if custom_notes.strip():
        parts.append(f"\nAdditional user instructions: {custom_notes.strip()}")

    # Language hint
    lang = detect_language("\n".join(s.get("content", "") for s in sections))
    if lang == "zh":
        parts.append("\n---")
        parts.append("IMPORTANT: This document is in Chinese. You MUST output all notes in Chinese. Do NOT use English.")
    else:
        parts.append("\n---")
        parts.append("IMPORTANT: This document is in English. You MUST output all notes in English. Do NOT use Chinese.")

    return "\n".join(parts)


def estimate_tokens(text: str) -> int:
    return len(text) // 4
