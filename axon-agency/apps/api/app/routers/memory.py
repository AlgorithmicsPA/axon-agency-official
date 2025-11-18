"""Agent Memory endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from loguru import logger

from app.core.database import get_session
from app.core.security import get_current_user
from app.models import User
from app.models.rag import AgentMemory
from app.services.embeddings import embedding_service


router = APIRouter()


class MemorySaveRequest(BaseModel):
    agent_id: str
    note: str
    session_id: Optional[str] = None
    is_pinned: bool = False
    importance: int = 5


class MemoryResponse(BaseModel):
    id: int
    agent_id: str
    note: str
    is_pinned: bool
    importance: int
    created_at: str
    accessed_at: str


@router.post("/save", response_model=MemoryResponse)
async def save_memory(
    request: MemorySaveRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Save a new memory for an agent."""
    embedding = await embedding_service.embed_text(request.note)
    
    memory = AgentMemory(
        agent_id=request.agent_id,
        session_id=request.session_id,
        note=request.note,
        is_pinned=request.is_pinned,
        importance=request.importance,
        embedding=str(embedding[:10])
    )
    
    session.add(memory)
    session.commit()
    session.refresh(memory)
    
    logger.info(f"Saved memory for agent {request.agent_id}")
    
    return MemoryResponse(
        id=memory.id,
        agent_id=memory.agent_id,
        note=memory.note,
        is_pinned=memory.is_pinned,
        importance=memory.importance,
        created_at=memory.created_at.isoformat(),
        accessed_at=memory.accessed_at.isoformat()
    )


@router.get("/list", response_model=List[MemoryResponse])
async def list_memories(
    agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    pinned_only: bool = False,
    limit: int = 50,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List memories for an agent."""
    stmt = select(AgentMemory)
    
    if agent_id:
        stmt = stmt.where(AgentMemory.agent_id == agent_id)
    
    if session_id:
        stmt = stmt.where(AgentMemory.session_id == session_id)
    
    if pinned_only:
        stmt = stmt.where(AgentMemory.is_pinned == True)
    
    stmt = stmt.order_by(AgentMemory.created_at.desc()).limit(limit)
    
    memories = session.exec(stmt).all()
    
    return [
        MemoryResponse(
            id=m.id,
            agent_id=m.agent_id,
            note=m.note,
            is_pinned=m.is_pinned,
            importance=m.importance,
            created_at=m.created_at.isoformat(),
            accessed_at=m.accessed_at.isoformat()
        )
        for m in memories
    ]


@router.patch("/{memory_id}/pin")
async def pin_memory(
    memory_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Pin/unpin a memory."""
    memory = session.get(AgentMemory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    memory.is_pinned = not memory.is_pinned
    session.commit()
    
    return {"id": memory.id, "is_pinned": memory.is_pinned}


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a memory."""
    memory = session.get(AgentMemory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    session.delete(memory)
    session.commit()
    
    return {"deleted": True, "id": memory_id}
