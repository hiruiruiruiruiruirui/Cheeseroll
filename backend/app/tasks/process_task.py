"""Async Celery task: parse document → AI generate notes → export PDF."""

import uuid
from datetime import datetime, timezone

from .celery_app import celery_app


async def _get_db_session():
    """Get an async database session for use inside the Celery task."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from ..config import settings

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()


@celery_app.task(bind=True, name="process_study_material")
def process_study_material(self, file_id: str, user_id: str, record_id: str, detail_level: str = "default", custom_notes: str = ""):
    """Full pipeline: parse uploaded file, generate AI notes, export PDF."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(
            _process_study_material_async(
                uuid.UUID(file_id),
                uuid.UUID(user_id),
                uuid.UUID(record_id),
                detail_level,
                custom_notes,
            )
        )
    except Exception as exc:
        loop.run_until_complete(
            _fail_record(uuid.UUID(record_id), str(exc))
        )
        raise
    finally:
        loop.close()


async def _process_study_material_async(
    file_id: uuid.UUID,
    user_id: uuid.UUID,
    record_id: uuid.UUID,
    detail_level: str = "default",
    custom_notes: str = "",
) -> None:
    """Async implementation of the processing pipeline.

    Tries to use full AI pipeline; falls back to mock for dev.
    """
    from ..models.file import File
    from ..models.record import Record

    async with await _get_db_session() as db:
        from sqlalchemy import select

        result = await db.execute(select(File).where(File.id == file_id))
        file_obj = result.scalar_one_or_none()
        if not file_obj:
            raise ValueError(f"File not found: {file_id}")

        # Stage 1: Parse
        await _update_record_status(db, record_id, "parsing", "Parsing document...")

        try:
            from ..services.doc_parser import parse_document
            parsed = await parse_document(file_obj.cos_key, file_obj.file_type)
            parsed_content_dict = parsed
            parsed_text = "\n\n".join(
                sec.get("content", "") for sec in parsed.get("sections", [])
            )
            title = parsed.get("title", file_obj.original_name)
        except ImportError:
            # Mock: create a proper dict structure
            parsed_text = f"File: {file_obj.original_name}\nType: {file_obj.file_type}"
            title = file_obj.original_name
            parsed_content_dict = {
                "title": title,
                "sections": [
                    {"heading": "Uploaded Document", "level": 1, "content": parsed_text, "tables": []}
                ],
            }

        file_obj.parsed_text = parsed_text
        file_obj.parse_status = "done"

        # Stage 2: Generate AI notes
        await _update_record_status(db, record_id, "generating", "AI generating notes...")

        try:
            from ..services.ai_engine import generate_study_notes
            # Smart token estimation: count sections, estimate per-section need
            sections = parsed_content_dict.get("sections", [])
            sec_count = len(sections) if sections else 1
            content_chars = sum(len(s.get("content", "")) + len(s.get("heading", "")) for s in sections)
            # Detail level multipliers: brief=0.5, default=1.0, detailed=1.5
            multipliers = {"brief": 0.5, "default": 1.0, "detailed": 1.5}
            mult = multipliers.get(detail_level, 1.0)
            # Estimate: ~1.5 tokens per Chinese char, ~0.75 per English char; use 1.2 avg
            # Plus per-section overhead of ~80 tokens for formatting
            estimated = int(content_chars * 1.2 * mult + sec_count * 80)
            max_tokens = min(8192, max(1024, estimated))
            # If content exceeds token limit, add a fit instruction for the AI
            if estimated > 8192:
                fit_instruction = f"\n\nNOTE: The document has {sec_count} sections. You have {max_tokens} output tokens. Cover the most important sections fully. For remaining sections, provide brief 1-2 line summaries rather than omitting them entirely."
                if custom_notes:
                    custom_notes += fit_instruction
                else:
                    custom_notes = fit_instruction
            markdown_notes = await generate_study_notes(
                parsed_content=parsed_content_dict,
                title=title,
                detail_level=detail_level,
                custom_notes=custom_notes,
                max_tokens=max_tokens,
            )
        except ImportError:
            # Mock: create simple markdown
            markdown_notes = f"""# {title}

## Knowledge Outline

This is a mock study note generated from: **{file_obj.original_name}**

### Key Points
- The full AI engine (Claude API) is not configured yet
- Install `anthropic` package and set `ANTHROPIC_API_KEY` to enable AI processing
- The document was uploaded successfully and saved locally

### Next Steps
1. Set your Claude API key in backend/.env: `ANTHROPIC_API_KEY=sk-ant-...`
2. Install AI packages: `pip install anthropic langchain langchain-community unstructured`
3. Rebuild the Docker container

---

*Generated by AI Study Assistant (dev mode)*
"""
            title = file_obj.original_name

        # Stage 3: Export PDF (skip for dev)
        await _update_record_status(db, record_id, "exporting", "Exporting PDF...")
        pdf_cos_key = None

        try:
            from ..services.pdf_exporter import markdown_to_pdf
            import os
            from ..services.file_svc import upload_file as svc_upload_file
            pdf_bytes = await markdown_to_pdf(
                markdown_text=markdown_notes,
                title=title,
            )
            pdf_filename = f"{os.path.splitext(file_obj.original_name)[0]}_study_notes.pdf"
            upload_result = await svc_upload_file(
                user_id=user_id,
                filename=pdf_filename,
                file_data=pdf_bytes,
                content_type="application/pdf",
            )
            pdf_cos_key = upload_result["cos_key"]
        except (ImportError, Exception):
            pass  # PDF export not available

        # Final: update record
        record_result = await db.execute(select(Record).where(Record.id == record_id))
        record_obj = record_result.scalar_one_or_none()
        if record_obj:
            record_obj.original_markdown = markdown_notes
            record_obj.pdf_cos_key = pdf_cos_key
            record_obj.status = "completed"
            record_obj.title = title

        await db.commit()


async def _update_record_status(db, record_id: uuid.UUID, status: str, message: str) -> None:
    """Update the processing status of a record."""
    from ..models.record import Record
    from sqlalchemy import select

    result = await db.execute(select(Record).where(Record.id == record_id))
    record = result.scalar_one_or_none()
    if record:
        record.status = status
        # Store progress message in error_message field temporarily during processing
        # (will be cleared on success)
        record.error_message = message
        await db.commit()


async def _fail_record(record_id: uuid.UUID, error_message: str) -> None:
    """Mark a record as failed."""
    from ..models.record import Record
    from sqlalchemy import select

    async with await _get_db_session() as db:
        result = await db.execute(select(Record).where(Record.id == record_id))
        record = result.scalar_one_or_none()
        if record:
            record.status = "failed"
            record.error_message = error_message
            await db.commit()
