"""Prompt Refiner PRO - Professional prompt engineering and improvement system."""

import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.providers.gemini import gemini_chat
from app.providers.openai import openai_chat
from app.providers.ollama import ollama_chat

logger = logging.getLogger(__name__)

router = APIRouter()


class PromptImproveRequest(BaseModel):
    """Request schema for prompt improvement."""
    text: str = Field(..., description="The prompt text to improve")
    context: Optional[str] = Field(None, description="Optional context about the use case")
    goal: Optional[str] = Field(None, description="Optional goal for the prompt")


class PromptImproveResponse(BaseModel):
    """Response schema for prompt improvement."""
    improved: str = Field(..., description="The improved version of the prompt")
    changes: list[str] = Field(..., description="List of changes made")
    reasoning: str = Field(..., description="Explanation of why changes were made")
    original: str = Field(..., description="Original text for reference")
    provider: str = Field(..., description="LLM provider used for improvement")


PROMPT_ENGINEERING_SYSTEM = """Eres un experto en ingeniería de prompts especializado en AXON Agency, una plataforma de agentes de IA y desarrollo de software.

Tu tarea es mejorar el siguiente mensaje del usuario para que sea más claro, profesional y efectivo, manteniendo su intención original.

PRINCIPIOS DE MEJORA:
1. **Claridad**: Elimina ambigüedades y haz el mensaje más específico y directo
2. **Precisión Técnica**: Usa términos técnicos apropiados cuando sea relevante (API, REST, FastAPI, JWT, OAuth, endpoints, etc.)
3. **Estructura**: Organiza el contenido de forma lógica y fácil de entender
4. **Contexto**: Mantén el tono, idioma y contexto original del usuario
5. **Accionabilidad**: Haz el mensaje más concreto y ejecutable para un desarrollador o agente IA

CONTEXTO DE DOMINIO (AXON Agency):
- Especialización en agentes de IA, desarrollo de software, automatización
- Stack técnico: FastAPI (backend), React/Next.js (frontend), Python, TypeScript
- Servicios comunes: APIs REST, bots (Telegram, WhatsApp), sistemas de IA/ML, RAG, LLM orchestration
- Usuarios son desarrolladores o empresarios que necesitan soluciones técnicas de IA

PROCESO DE MEJORA:
1. Identifica la intención principal del usuario
2. Detecta ambigüedades, falta de detalles o imprecisiones
3. Expande la solicitud con detalles técnicos relevantes sin cambiar la esencia
4. Mantén el idioma original (español/inglés)
5. Si es muy vago, agrega especificaciones técnicas comunes

EJEMPLOS DE TRANSFORMACIÓN:
- "crea una api" → "Desarrolla una API REST usando FastAPI con endpoints para operaciones CRUD, autenticación JWT y documentación OpenAPI automática"
- "haz un bot" → "Desarrolla un bot de Telegram usando Python con comandos básicos, manejo de estados y persistencia de datos"
- "implementa oauth2" → "Implementa autenticación OAuth2 con flujo de autorización code grant, refresh tokens y almacenamiento seguro de tokens"
- "mejora el código" → "Refactoriza el código para mejorar la legibilidad, aplicar principios SOLID, agregar type hints y documentación"

RESPONDE SIEMPRE EN FORMATO JSON VÁLIDO (sin markdown):
{
  "improved": "versión mejorada del mensaje con detalles técnicos relevantes",
  "changes": ["cambio específico 1", "cambio específico 2", "cambio específico 3"],
  "reasoning": "explicación concisa de por qué se hicieron estos cambios y cómo mejoran el mensaje original"
}"""


async def improve_with_gemini(text: str, context: Optional[str], goal: Optional[str]) -> dict:
    """Improve prompt using Gemini with professional prompt engineering."""
    user_prompt = f"Mensaje original: {text}"
    
    if context:
        user_prompt += f"\n\nContexto adicional: {context}"
    
    if goal:
        user_prompt += f"\n\nObjetivo: {goal}"
    
    user_prompt += "\n\nMejora este mensaje siguiendo los principios descritos. Responde SOLO con el JSON, sin markdown ni texto adicional."
    
    messages = [
        {"role": "user", "content": PROMPT_ENGINEERING_SYSTEM},
        {"role": "model", "content": "Entendido. Mejoraré los prompts siguiendo estos principios profesionales de ingeniería de prompts, manteniendo la intención original y agregando detalles técnicos relevantes. Responderé siempre en formato JSON válido."},
        {"role": "user", "content": user_prompt}
    ]
    
    response = await gemini_chat(messages, model=settings.gemini_flash_model)
    
    response_clean = response.strip()
    if response_clean.startswith("```json"):
        response_clean = response_clean[7:]
    if response_clean.startswith("```"):
        response_clean = response_clean[3:]
    if response_clean.endswith("```"):
        response_clean = response_clean[:-3]
    response_clean = response_clean.strip()
    
    try:
        return json.loads(response_clean)
    except json.JSONDecodeError as e:
        logger.warning(f"Gemini returned invalid JSON, using fallback: {e}")
        return {
            "improved": response_clean or text,
            "changes": ["Auto-formatted output (JSON parse failed)"],
            "reasoning": "Model returned non-JSON response",
        }


async def improve_with_openai(text: str, context: Optional[str], goal: Optional[str]) -> dict:
    """Improve prompt using OpenAI with professional prompt engineering."""
    user_prompt = f"Mensaje original: {text}"
    
    if context:
        user_prompt += f"\n\nContexto adicional: {context}"
    
    if goal:
        user_prompt += f"\n\nObjetivo: {goal}"
    
    user_prompt += "\n\nMejora este mensaje siguiendo los principios descritos. Responde SOLO con el JSON, sin markdown ni texto adicional."
    
    messages = [
        {"role": "system", "content": PROMPT_ENGINEERING_SYSTEM},
        {"role": "user", "content": user_prompt}
    ]
    
    response = await openai_chat(messages, model=settings.openai_model)
    
    response_clean = response.strip()
    if response_clean.startswith("```json"):
        response_clean = response_clean[7:]
    if response_clean.startswith("```"):
        response_clean = response_clean[3:]
    if response_clean.endswith("```"):
        response_clean = response_clean[:-3]
    response_clean = response_clean.strip()
    
    try:
        return json.loads(response_clean)
    except json.JSONDecodeError as e:
        logger.warning(f"OpenAI returned invalid JSON, using fallback: {e}")
        return {
            "improved": response_clean or text,
            "changes": ["Auto-formatted output (JSON parse failed)"],
            "reasoning": "Model returned non-JSON response",
        }


async def improve_with_ollama(text: str, context: Optional[str], goal: Optional[str]) -> dict:
    """Improve prompt using Ollama with professional prompt engineering."""
    user_prompt = f"{PROMPT_ENGINEERING_SYSTEM}\n\nMensaje original: {text}"
    
    if context:
        user_prompt += f"\n\nContexto adicional: {context}"
    
    if goal:
        user_prompt += f"\n\nObjetivo: {goal}"
    
    user_prompt += "\n\nMejora este mensaje siguiendo los principios descritos. Responde SOLO con el JSON, sin markdown ni texto adicional."
    
    messages = [{"role": "user", "content": user_prompt}]
    
    response = await ollama_chat(messages, model=settings.ollama_model)
    
    response_clean = response.strip()
    if response_clean.startswith("```json"):
        response_clean = response_clean[7:]
    if response_clean.startswith("```"):
        response_clean = response_clean[3:]
    if response_clean.endswith("```"):
        response_clean = response_clean[:-3]
    response_clean = response_clean.strip()
    
    try:
        return json.loads(response_clean)
    except json.JSONDecodeError as e:
        logger.warning(f"Ollama returned invalid JSON, using fallback: {e}")
        return {
            "improved": response_clean or text,
            "changes": ["Auto-formatted output (JSON parse failed)"],
            "reasoning": "Model returned non-JSON response",
        }


@router.post("/api/prompt/improve", response_model=PromptImproveResponse)
async def improve_prompt(request: PromptImproveRequest):
    """Improve a prompt using professional prompt engineering.
    
    This endpoint uses a specialized prompt engineering system to:
    - Analyze user intent and identify ambiguities
    - Improve structure, grammar, and precision
    - Add relevant technical details without changing the essence
    - Maintain the original tone and context
    
    The system is domain-aware (AXON Agency, AI agents, software development)
    and will expand vague requests with appropriate technical specifications.
    
    Provider selection logic (with fallback chain):
    1. Gemini 2.0 Flash (preferred - best for refinement tasks)
    2. OpenAI GPT-4 (fallback)
    3. Ollama (local fallback)
    
    Configuration:
    - Timeout: 10 seconds
    - Temperature: 0.3 (deterministic)
    - Max tokens: 1000
    - JSON schema validation
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        logger.info(f"Improving prompt (length: {len(request.text)})")
        
        provider_chain = []
        if settings.gemini_api_key:
            provider_chain.append(("gemini", improve_with_gemini))
        if settings.openai_api_key:
            provider_chain.append(("openai", improve_with_openai))
        if settings.ollama_available:
            provider_chain.append(("ollama", improve_with_ollama))
        
        if not provider_chain:
            raise HTTPException(
                status_code=503,
                detail="No LLM providers available for prompt improvement"
            )
        
        last_error = None
        
        for provider_name, improve_func in provider_chain:
            try:
                logger.info(f"Attempting improvement with {provider_name}")
                
                result = await improve_func(request.text, request.context, request.goal)
                
                improved_text = result.get("improved", "")
                changes = result.get("changes", [])
                reasoning = result.get("reasoning", "")
                
                if not improved_text or not isinstance(changes, list):
                    raise ValueError("Invalid response format from LLM")
                
                logger.info(f"✅ Successfully improved prompt with {provider_name}")
                
                return PromptImproveResponse(
                    improved=improved_text,
                    changes=changes,
                    reasoning=reasoning,
                    original=request.text,
                    provider=provider_name
                )
                
            except json.JSONDecodeError as e:
                logger.warning(f"{provider_name} returned invalid JSON: {e}")
                last_error = f"JSON parsing error with {provider_name}"
                continue
                
            except Exception as e:
                logger.warning(f"{provider_name} failed: {e}")
                last_error = str(e)
                continue
        
        raise HTTPException(
            status_code=500,
            detail=f"All providers failed. Last error: {last_error}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prompt improvement error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/api/prompt/status")
async def get_prompt_service_status():
    """Get status of the prompt improvement service and available providers."""
    providers_status = {
        "gemini": {
            "available": bool(settings.gemini_api_key),
            "model": settings.gemini_flash_model,
            "preferred": True
        },
        "openai": {
            "available": bool(settings.openai_api_key),
            "model": settings.openai_model,
            "preferred": False
        },
        "ollama": {
            "available": settings.ollama_available,
            "model": settings.ollama_model,
            "preferred": False
        }
    }
    
    available_providers = [
        name for name, status in providers_status.items()
        if status["available"]
    ]
    
    return {
        "service": "Prompt Refiner PRO",
        "status": "operational" if available_providers else "no_providers",
        "providers": providers_status,
        "available_providers": available_providers,
        "fallback_chain": available_providers,
        "configuration": {
            "timeout": "10s",
            "temperature": 0.3,
            "max_tokens": 1000,
            "deterministic": True
        }
    }
