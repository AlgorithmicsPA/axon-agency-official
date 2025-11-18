"""Agent chat endpoints."""

import logging
import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlmodel import Session
from openai import AsyncOpenAI
from app.core.security import get_current_user_optional
from app.core.config import settings
from app.core.database import get_session
from app.models import Conversation
from app.services.chat_orchestration import get_chat_orchestrator, ChatOrchestrationService

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request."""
    text: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Chat response."""
    output: str
    session_id: str | None = None
    session_url: Optional[str] = None
    provider: Optional[str] = Field(default=None)
    type: Optional[str] = "direct"


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user = Depends(get_current_user_optional),
    orchestrator: ChatOrchestrationService = Depends(get_chat_orchestrator),
    db_session: Session = Depends(get_session)
):
    """
    Super Axon Agent - Interfaz conversacional que delega al Agente Autónomo.
    
    Clasifica la intención del usuario y:
    - Responde directamente preguntas simples (INFO, SMALL_HELP)
    - Delega construcciones complejas al Autonomous Agent (AUTONOMOUS_BUILD)
    
    Además, guarda automáticamente todas las conversaciones en la base de datos.
    """
    if not current_user and not settings.dev_mode:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        logger.info(f"Chat request: {request.text[:100]}")
        
        session_id = request.session_id or str(uuid.uuid4())
        
        user_conversation = Conversation(
            session_id=session_id,
            role="user",
            content=request.text,
            meta={},
            user_id=current_user.id if current_user else None,
            created_at=datetime.utcnow()
        )
        db_session.add(user_conversation)
        db_session.commit()
        
        result = await orchestrator.handle_message(request.text, current_user)
        
        response_meta = {
            "provider": result.provider,
            "type": result.type
        }
        
        if result.type == "direct":
            assistant_conversation = Conversation(
                session_id=session_id,
                role="assistant",
                content=result.message,
                meta=response_meta,
                user_id=current_user.id if current_user else None,
                created_at=datetime.utcnow()
            )
            db_session.add(assistant_conversation)
            db_session.commit()
            
            return ChatResponse(
                output=result.message,
                session_id=session_id,
                provider=result.provider,
                type="direct"
            )
        else:
            meta_data = response_meta.copy()
            autonomous_session_url = None
            
            if result.session:
                meta_data["autonomous_session_id"] = result.session.session_id
                meta_data["session_url"] = result.session.url
                autonomous_session_url = result.session.url
            
            assistant_conversation = Conversation(
                session_id=session_id,
                role="assistant",
                content=result.message,
                meta=meta_data,
                user_id=current_user.id if current_user else None,
                created_at=datetime.utcnow()
            )
            db_session.add(assistant_conversation)
            db_session.commit()
            
            return ChatResponse(
                output=result.message,
                session_id=session_id,
                session_url=autonomous_session_url,
                provider=result.provider,
                type="autonomous_session"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    current_user = Depends(get_current_user_optional)
):
    """Speech-to-text usando OpenAI Whisper."""
    if not current_user and not settings.dev_mode:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        audio_bytes = await audio.read()
        
        if not settings.openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        transcription = await client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.webm", audio_bytes, "audio/webm"),
            language="es"
        )
        
        return {
            "text": transcription.text,
            "language": "es"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
