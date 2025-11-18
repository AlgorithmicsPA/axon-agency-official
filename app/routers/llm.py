from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.deps import get_current_user
from app.core.types import TokenPayload, LLMProvider, LLMInput, LLMResponse
from app.core.utils import write_audit_log
from app.config import settings
from app.adapters.llm_openai import OpenAIAdapter
from app.adapters.llm_gemini import GeminiAdapter
from app.adapters.llm_deepseek import DeepSeekAdapter
from app.adapters.llm_ollama import OllamaAdapter
from app.adapters.llm_sdxl_local import SDXLAdapter
from loguru import logger


router = APIRouter(prefix="/api", tags=["llm"])


class LLMInferRequest(BaseModel):
    provider: LLMProvider
    model: str
    input: LLMInput
    temperature: float = 0.7
    max_tokens: int = 1000


@router.post("/llm/infer", response_model=LLMResponse)
async def llm_infer(
    request: LLMInferRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    """Perform LLM inference."""
    try:
        if request.provider == LLMProvider.OPENAI:
            if not settings.openai_api_key:
                raise HTTPException(status_code=503, detail="OpenAI API key not configured")
            adapter = OpenAIAdapter(settings.openai_api_key)
            
        elif request.provider == LLMProvider.GEMINI:
            if not settings.gemini_api_key:
                raise HTTPException(status_code=503, detail="Gemini API key not configured")
            adapter = GeminiAdapter(settings.gemini_api_key)
            
        elif request.provider == LLMProvider.DEEPSEEK:
            if not settings.deepseek_api_key:
                raise HTTPException(status_code=503, detail="DeepSeek API key not configured")
            adapter = DeepSeekAdapter(settings.deepseek_api_key)
            
        elif request.provider == LLMProvider.OLLAMA:
            adapter = OllamaAdapter(settings.ollama_base_url)
            
        elif request.provider == LLMProvider.SDXL:
            adapter = SDXLAdapter(settings.sdxl_base_url)
            
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        result = await adapter.infer(
            model=request.model,
            input_data=request.input,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        write_audit_log(
            "llm_infer",
            current_user.sub,
            {"provider": request.provider, "model": request.model},
            settings.audit_log_path,
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM inference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/llm/providers")
async def get_llm_providers(
    current_user: TokenPayload = Depends(get_current_user),
):
    """Get available LLM providers and their status."""
    providers = {
        "openai": {
            "available": bool(settings.openai_api_key),
            "name": "OpenAI",
        },
        "gemini": {
            "available": bool(settings.gemini_api_key),
            "name": "Google Gemini",
        },
        "deepseek": {
            "available": bool(settings.deepseek_api_key),
            "name": "DeepSeek",
        },
        "ollama": {
            "available": True,
            "name": "Ollama (Local)",
            "base_url": settings.ollama_base_url,
        },
        "sdxl": {
            "available": True,
            "name": "SDXL (Local)",
            "base_url": settings.sdxl_base_url,
        },
    }
    
    return {"providers": providers}
