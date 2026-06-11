"""Records endpoints — list, view, organize study records with folders."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..deps import get_db, get_current_user
from ...models.user import User
from ...models.record import Record
from ...models.folder import Folder
from ...schemas.record import RecordRead, RecordDetail, RecordListResponse

router = APIRouter()


@router.get("/records", response_model=RecordListResponse)
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    folder_id: str = Query("all"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's study records, paginated. Filter by folder_id (all, none, or UUID)."""
    base_where = Record.user_id == current_user.id
    if folder_id == "none":
        base_where = base_where & (Record.folder_id == None)
    elif folder_id != "all":
        try: fid = uuid.UUID(folder_id); base_where = base_where & (Record.folder_id == fid)
        except ValueError: pass

    total = (await db.execute(select(func.count()).select_from(Record).where(base_where))).scalar() or 0
    offset = (page - 1) * page_size
    records = (await db.execute(select(Record).where(base_where).order_by(Record.created_at.desc()).offset(offset).limit(page_size))).scalars().all()

    items = [RecordRead(id=r.id, title=r.title, status=r.status, share_code=r.share_code, folder_id=r.folder_id, created_at=r.created_at) for r in records]
    return RecordListResponse(items=items, total=total, page=page, page_size=page_size)


# --- Folder CRUD ---

@router.get("/folders")
async def list_folders(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List user's folders with note counts and 1-level hierarchy."""
    folders = (await db.execute(select(Folder).where(Folder.user_id == current_user.id).order_by(Folder.name))).scalars().all()
    result = []
    for f in folders:
        if f.parent_id is None:
            count = (await db.execute(select(func.count()).select_from(Record).where(Record.folder_id == f.id))).scalar() or 0
            children = []
            for sf in folders:
                if sf.parent_id == f.id:
                    sc = (await db.execute(select(func.count()).select_from(Record).where(Record.folder_id == sf.id))).scalar() or 0
                    children.append({"id": str(sf.id), "name": sf.name, "parent_id": str(f.id), "count": sc})
                    count += sc
            result.append({"id": str(f.id), "name": f.name, "parent_id": None, "count": count, "children": children if children else None})
    return result


@router.post("/folders")
async def create_folder(req: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    name = req.get("name", "").strip()
    if not name: raise HTTPException(400, "Folder name required")
    parent_id = req.get("parent_id")
    parent_uid = uuid.UUID(parent_id) if parent_id else None
    f = Folder(user_id=current_user.id, name=name[:200], parent_id=parent_uid)
    db.add(f); await db.commit(); await db.refresh(f)
    return {"id": str(f.id), "name": f.name, "parent_id": str(f.parent_id) if f.parent_id else None}


@router.put("/folders/{folder_id}")
async def rename_folder(folder_id: uuid.UUID, req: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    f = (await db.execute(select(Folder).where(Folder.id == folder_id, Folder.user_id == current_user.id))).scalar_one_or_none()
    if not f: raise HTTPException(404, "Folder not found")
    f.name = req.get("name", "").strip()[:200]
    await db.commit()
    return {"id": str(f.id), "name": f.name}


@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    f = (await db.execute(select(Folder).where(Folder.id == folder_id, Folder.user_id == current_user.id))).scalar_one_or_none()
    if not f: raise HTTPException(404, "Folder not found")
    # Unlink notes
    await db.execute(select(Record).where(Record.folder_id == folder_id))
    records = (await db.execute(select(Record).where(Record.folder_id == folder_id))).scalars().all()
    for r in records: r.folder_id = None
    await db.delete(f); await db.commit()
    return {"ok": True}


@router.put("/records/{record_id}/move")
async def move_record(record_id: uuid.UUID, req: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = (await db.execute(select(Record).where(Record.id == record_id, Record.user_id == current_user.id))).scalar_one_or_none()
    if not r: raise HTTPException(404, "Record not found")
    fid = req.get("folder_id")
    r.folder_id = uuid.UUID(fid) if fid else None
    await db.commit()
    return {"ok": True}


@router.get("/records/{record_id}", response_model=RecordDetail)
async def get_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single record with full Markdown content."""
    result = await db.execute(
        select(Record).where(
            Record.id == record_id,
            Record.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )

    return RecordDetail(
        id=record.id,
        title=record.title,
        original_markdown=record.original_markdown,
        status=record.status,
        share_code=record.share_code,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.delete("/records/{record_id}")
async def delete_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a study record."""
    result = await db.execute(
        select(Record).where(Record.id == record_id, Record.user_id == current_user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    await db.delete(record)
    await db.commit()
    return {"ok": True}


@router.put("/records/{record_id}/rename")
async def rename_record(
    record_id: uuid.UUID,
    req: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rename a study record."""
    result = await db.execute(
        select(Record).where(Record.id == record_id, Record.user_id == current_user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    new_title = req.get("title", "").strip()
    if not new_title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title required")
    record.title = new_title
    await db.commit()
    return {"ok": True, "title": new_title}
