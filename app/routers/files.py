import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.deps import get_current_user
from app.core.types import TokenPayload
from app.core.utils import safe_path_join, write_audit_log
from app.config import settings
from app.security import require_admin
from loguru import logger


router = APIRouter(prefix="/api", tags=["files"])


class FileInfo(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int
    modified: str


class ListFilesRequest(BaseModel):
    path: str = ""


class ListFilesResponse(BaseModel):
    files: List[FileInfo]
    current_path: str


@router.post("/files/list", response_model=ListFilesResponse)
async def list_files(
    request: ListFilesRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    """List files in a directory."""
    try:
        target_path = safe_path_join(settings.files_root, request.path)
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not target_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        files = []
        for item in target_path.iterdir():
            stat = item.stat()
            files.append(FileInfo(
                name=item.name,
                path=str(item.relative_to(settings.files_root)),
                is_dir=item.is_dir(),
                size=stat.st_size,
                modified=str(stat.st_mtime),
            ))
        
        return ListFilesResponse(
            files=sorted(files, key=lambda x: (not x.is_dir, x.name)),
            current_path=request.path,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list files")


@router.post("/files/upload")
async def upload_file(
    path: str,
    file: UploadFile = File(...),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Upload a file."""
    require_admin(current_user)
    
    try:
        target_dir = safe_path_join(settings.files_root, path)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / file.filename
        
        content = await file.read()
        file_path.write_bytes(content)
        
        write_audit_log(
            "file_upload",
            current_user.sub,
            {"path": str(file_path.relative_to(settings.files_root)), "size": len(content)},
            settings.audit_log_path,
        )
        
        return {"message": "File uploaded", "path": str(file_path.relative_to(settings.files_root))}
        
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")


class DownloadRequest(BaseModel):
    path: str


@router.post("/files/download")
async def download_file(
    request: DownloadRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    """Download a file."""
    try:
        file_path = safe_path_join(settings.files_root, request.path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type="application/octet-stream",
        )
        
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail="Failed to download file")
