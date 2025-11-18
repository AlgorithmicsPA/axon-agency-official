"""Content posts/landing pages endpoints."""

import logging
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.core.security import get_current_user, TokenData
from app.models import Post, PostStatus

logger = logging.getLogger(__name__)

router = APIRouter()


class DraftRequest(BaseModel):
    """Create draft request."""
    topic: str
    brief: str | None = None


@router.post("/draft")
async def create_draft(
    request: DraftRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new draft post/landing page."""
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', request.topic.lower()).strip('-')
    
    existing = session.exec(select(Post).where(Post.slug == slug)).first()
    if existing:
        slug = f"{slug}-{datetime.utcnow().timestamp()}"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{request.topic}</title>
    <style>
        body {{ font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #6366f1; }}
    </style>
</head>
<body>
    <h1>{request.topic}</h1>
    <p>{request.brief or 'Content coming soon...'}</p>
</body>
</html>"""
    
    draft_path = Path(settings.storage_root) / "drafts" / slug
    draft_path.mkdir(parents=True, exist_ok=True)
    (draft_path / "index.html").write_text(html_content)
    
    post = Post(
        slug=slug,
        title=request.topic,
        topic=request.topic,
        brief=request.brief,
        content=html_content,
        status=PostStatus.DRAFT.value,
        created_by=1
    )
    
    session.add(post)
    session.commit()
    session.refresh(post)
    
    return {
        "slug": slug,
        "preview_url": f"/preview/{slug}/index.html",
        "id": post.id
    }


@router.post("/publish/{slug}")
async def publish_post(
    slug: str,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Publish a draft post."""
    post = session.exec(select(Post).where(Post.slug == slug)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    draft_path = Path(settings.storage_root) / "drafts" / slug / "index.html"
    if not draft_path.exists():
        raise HTTPException(status_code=404, detail="Draft file not found")
    
    published_path = Path(settings.storage_root) / "published" / slug
    published_path.mkdir(parents=True, exist_ok=True)
    
    import shutil
    shutil.copy(draft_path, published_path / "index.html")
    
    post.status = PostStatus.PUBLISHED.value
    post.published_at = datetime.utcnow()
    session.add(post)
    session.commit()
    
    return {
        "ok": True,
        "site_url": f"/site/{slug}/index.html"
    }


@router.get("/list")
async def list_posts(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all posts."""
    posts = session.exec(select(Post).order_by(Post.created_at.desc())).all()
    
    return {
        "items": [
            {
                "id": p.id,
                "slug": p.slug,
                "title": p.title,
                "topic": p.topic,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
                "published_at": p.published_at.isoformat() if p.published_at else None
            }
            for p in posts
        ]
    }
