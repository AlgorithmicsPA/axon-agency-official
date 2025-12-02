"""LLM orchestration router - intelligently selects best model for each task."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.config import settings
from app.providers.openai import openai_chat, openai_chat_stream
from app.providers.gemini import gemini_chat, gemini_chat_stream
from app.providers.ollama import ollama_chat, ollama_chat_stream
from app.services.llm_router import get_llm_router
from app.models.llm import TaskType, LLMResponse, ProviderStatus
from app.services.super_axon_agent import super_axon_chat_stream, detect_mode

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: list[dict]
    model: str | None = None
    provider: str | None = None  # "auto", "openai", "gemini", "ollama"
    stream: bool = False
    images: list[str] | None = None


class ChatResponse(BaseModel):
    """Chat completion response."""
    content: str
    model: str
    provider: str


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """Chat completion with automatic provider selection.
    
    Provider selection logic:
    - If images provided -> Gemini (best multimodal)
    - If model specified -> Use that provider
    - If provider="auto" -> Select based on task complexity
    - Default: OpenAI (most reliable)
    """
    try:
        provider = request.provider or "auto"
        
        # Auto-select provider
        if provider == "auto":
            if request.images:
                provider = "gemini"
                logger.info("Auto-selected Gemini for multimodal request")
            elif settings.openai_api_key:
                provider = "openai"
            elif settings.gemini_api_key:
                provider = "gemini"
            elif settings.ollama_enabled:
                provider = "ollama"
                logger.info("Auto-selected Ollama (local)")
            else:
                raise HTTPException(status_code=503, detail="No LLM providers configured")
        
        # Execute based on selected provider
        if provider == "gemini":
            if not settings.gemini_api_key:
                raise HTTPException(status_code=503, detail="Gemini API key not configured")
            
            content = await gemini_chat(
                request.messages,
                model=request.model,
                images=request.images
            )
            model_used = request.model or settings.gemini_model
            
        elif provider == "openai":
            if not settings.openai_api_key:
                raise HTTPException(status_code=503, detail="OpenAI API key not configured")
            
            if request.images:
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI vision not implemented yet. Use provider='gemini' for images"
                )
            
            content = await openai_chat(
                request.messages,
                model=request.model
            )
            model_used = request.model or settings.openai_model
            
        elif provider == "ollama":
            if not settings.ollama_enabled:
                raise HTTPException(status_code=503, detail="Ollama not enabled")
            
            if request.images:
                raise HTTPException(
                    status_code=400,
                    detail="Ollama vision not supported. Use provider='gemini' for images"
                )
            
            content = await ollama_chat(
                request.messages,
                model=request.model or settings.ollama_model
            )
            model_used = request.model or settings.ollama_model
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        return ChatResponse(
            content=content,
            model=model_used,
            provider=provider
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_completion_stream(request: ChatRequest):
    """Streaming chat completion con Super Axon Agent.
    
    Este endpoint usa el Super Axon Agent con:
    - Prompt de sistema especializado para AXON Agency
    - Detección automática de modos (estratega/implementador/tutor)
    - Tags soportados: #estratega, #implementador, #tutor
    """
    try:
        provider = request.provider or "auto"
        
        # Detectar modo del mensaje del usuario (para logging)
        mode = None
        if request.messages:
            last_user_msg = None
            for msg in reversed(request.messages):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break
            if last_user_msg:
                mode = detect_mode(last_user_msg)
                logger.info(f"Super Axon Agent: Modo detectado '{mode}' para mensaje del usuario")
        
        # Auto-select provider
        if provider == "auto":
            if request.images:
                provider = "gemini"
            elif settings.openai_api_key:
                provider = "openai"
            elif settings.gemini_api_key:
                provider = "gemini"
            elif settings.ollama_enabled:
                provider = "ollama"
            else:
                raise HTTPException(status_code=503, detail="No LLM providers configured")
        
        # Stream based on provider usando Super Axon Agent
        if provider == "gemini":
            if not settings.gemini_api_key:
                raise HTTPException(status_code=503, detail="Gemini not configured")
            
            async def stream_generator():
                async for chunk in super_axon_chat_stream(
                    request.messages,
                    gemini_chat_stream,
                    mode=mode,
                    model=request.model,
                    images=request.images
                ):
                    yield chunk
            
            return StreamingResponse(stream_generator(), media_type="text/plain")
            
        elif provider == "openai":
            if not settings.openai_api_key:
                raise HTTPException(status_code=503, detail="OpenAI not configured")
            
            async def stream_generator():
                async for chunk in super_axon_chat_stream(
                    request.messages,
                    openai_chat_stream,
                    mode=mode,
                    model=request.model
                ):
                    yield chunk
            
            return StreamingResponse(stream_generator(), media_type="text/plain")
            
        elif provider == "ollama":
            if not settings.ollama_enabled:
                raise HTTPException(status_code=503, detail="Ollama not enabled")
            
            async def stream_generator():
                async for chunk in super_axon_chat_stream(
                    request.messages,
                    ollama_chat_stream,
                    mode=mode,
                    model=request.model or settings.ollama_model
                ):
                    yield chunk
            
            return StreamingResponse(stream_generator(), media_type="text/plain")
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def list_providers():
    """List available LLM providers and their status."""
    providers = {
        "openai": {
            "available": bool(settings.openai_api_key),
            "models": [settings.openai_model, settings.openai_vision_model],
            "capabilities": ["text", "vision"]
        },
        "gemini": {
            "available": bool(settings.gemini_api_key),
            "models": [settings.gemini_model, settings.gemini_flash_model],
            "capabilities": ["text", "vision", "multimodal", "long_context"]
        },
        "ollama": {
            "available": settings.ollama_enabled,
            "models": [settings.ollama_model],
            "capabilities": ["text", "local", "free"]
        }
    }
    
    return {"providers": providers}


# ============================================================================
# FASE 7: Multi-LLM Router Endpoints
# ============================================================================

class RouterRequest(BaseModel):
    """Request for LLM router with auto-classification."""
    prompt: str
    task_type: Optional[str] = None
    context: Optional[dict] = None


@router.post("/router/execute", response_model=LLMResponse)
async def router_execute(request: RouterRequest):
    """Execute a prompt using the LLM router with automatic provider selection and fallback.
    
    The router will:
    1. Auto-classify the task type if not provided
    2. Select the best provider based on task type and availability
    3. Execute with retry logic and fallback chain
    4. Track metrics for monitoring
    """
    try:
        llm_router = get_llm_router()
        
        # Ensure router is initialized
        await llm_router.initialize()
        
        # Parse task type if provided
        task_type = None
        if request.task_type:
            try:
                task_type = TaskType(request.task_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid task_type. Must be one of: {[t.value for t in TaskType]}"
                )
        
        # Execute with router
        result = await llm_router.route_and_execute(
            prompt=request.prompt,
            task_type=task_type,
            context=request.context
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Router execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/router/metrics")
async def get_router_metrics():
    """Get usage metrics for all LLM providers.
    
    Returns aggregated statistics including:
    - Total requests per provider
    - Success/failure rates
    - Average latency
    - Token usage
    """
    try:
        llm_router = get_llm_router()
        metrics = llm_router.get_metrics()
        
        return {
            "metrics": metrics,
            "router_enabled": settings.llm_router_enabled
        }
        
    except Exception as e:
        logger.error(f"Error fetching router metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/router/status")
async def get_router_status():
    """Get current status and availability of all LLM providers.
    
    Returns real-time provider health information including:
    - Availability status
    - Average latency
    - Success rate
    - Request statistics
    """
    try:
        llm_router = get_llm_router()
        
        # Ensure router is initialized for accurate status
        await llm_router.initialize()
        
        statuses = await llm_router.get_provider_status()
        
        return {
            "providers": [status.model_dump() for status in statuses],
            "router_enabled": settings.llm_router_enabled,
            "ollama_available": settings.ollama_available,
            "preferences": settings.llm_preferences
        }
        
    except Exception as e:
        logger.error(f"Error fetching router status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
