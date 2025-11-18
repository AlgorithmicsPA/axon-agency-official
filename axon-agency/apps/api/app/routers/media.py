"""Media upload and management endpoints."""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.core.security import get_current_user, TokenData
from app.models import Media

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Upload a media file."""
    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4()}{ext}"
    file_path = Path(settings.storage_root) / "media" / filename
    
    content = await file.read()
    file_path.write_bytes(content)
    
    media = Media(
        filename=filename,
        original_filename=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        url=f"/media/{filename}",
        uploaded_by=1
    )
    
    session.add(media)
    session.commit()
    session.refresh(media)
    
    return {"url": media.url, "id": media.id, "filename": filename}


@router.get("/list")
async def list_media(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all uploaded media files."""
    media_items = session.exec(select(Media).order_by(Media.created_at.desc())).all()
    
    return {
        "items": [
            {
                "id": m.id,
                "filename": m.filename,
                "original_filename": m.original_filename,
                "mime_type": m.mime_type,
                "size_bytes": m.size_bytes,
                "url": m.url,
                "created_at": m.created_at.isoformat()
            }
            for m in media_items
        ]
    }


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a media file."""
    media = session.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    file_path = Path(settings.storage_root) / "media" / media.filename
    if file_path.exists():
        file_path.unlink()
    
    session.delete(media)
    session.commit()
    
    return {"ok": True}
