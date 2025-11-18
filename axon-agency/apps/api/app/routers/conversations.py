"""Conversation history endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select, func, desc, asc
from datetime import datetime
from app.core.database import get_session
from app.core.security import get_current_user
from app.models import Conversation

router = APIRouter()


class CreateConversationRequest(BaseModel):
    """Request to create a conversation message."""
    session_id: str
    role: str
    content: str
    meta: dict = {}


@router.get("/list")
async def list_conversations(
    session_id: str | None = None,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List conversation history."""
    query = select(Conversation).order_by(desc(Conversation.created_at)).limit(100)
    
    if session_id:
        query = query.where(Conversation.session_id == session_id)
    
    conversations = session.exec(query).all()
    
    return {
        "items": [
            {
                "id": c.id,
                "session_id": c.session_id,
                "role": c.role,
                "content": c.content,
                "created_at": c.created_at.isoformat(),
                "meta": c.meta
            }
            for c in conversations
        ]
    }


@router.post("/create")
async def create_conversation(
    request: CreateConversationRequest,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new conversation message."""
    try:
        conversation = Conversation(
            session_id=request.session_id,
            role=request.role,
            content=request.content,
            meta=request.meta,
            user_id=current_user.id if current_user else None,
            created_at=datetime.utcnow()
        )
        
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        return {
            "id": conversation.id,
            "session_id": conversation.session_id,
            "role": conversation.role,
            "content": conversation.content,
            "created_at": conversation.created_at.isoformat(),
            "meta": conversation.meta
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")


@router.get("/sessions")
async def list_sessions(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List unique conversation sessions with metadata."""
    try:
        query = (
            select(
                Conversation.session_id,
                func.min(Conversation.created_at).label("first_message_at"),
                func.max(Conversation.created_at).label("last_message_at")
            )
            .group_by(Conversation.session_id)
            .order_by(func.max(Conversation.created_at).desc())
        )
        
        results = session.exec(query).all()
        
        sessions = []
        for result in results:
            session_id, first_msg_at, last_msg_at = result
            
            first_user_msg = session.exec(
                select(Conversation)
                .where(Conversation.session_id == session_id)
                .where(Conversation.role == "user")
                .order_by(asc(Conversation.created_at))
                .limit(1)
            ).first()
            
            last_msg = session.exec(
                select(Conversation)
                .where(Conversation.session_id == session_id)
                .order_by(desc(Conversation.created_at))
                .limit(1)
            ).first()
            
            title = "Nueva conversación"
            if first_user_msg:
                title = first_user_msg.content[:50]
                if len(first_user_msg.content) > 50:
                    title += "..."
            
            last_message_preview = ""
            if last_msg:
                last_message_preview = last_msg.content[:100]
                if len(last_msg.content) > 100:
                    last_message_preview += "..."
            
            sessions.append({
                "session_id": session_id,
                "title": title,
                "first_message_at": first_msg_at.isoformat(),
                "last_message_at": last_msg_at.isoformat(),
                "last_message_preview": last_message_preview,
                "last_message_role": last_msg.role if last_msg else None
            })
        
        return {"sessions": sessions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")
