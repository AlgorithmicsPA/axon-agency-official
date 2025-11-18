"""Ollama provider for local LLM operations."""

import logging
import httpx
from typing import AsyncIterator
from app.core.config import settings

logger = logging.getLogger(__name__)


async def ollama_chat(messages: list[dict], model: str | None = None) -> str:
    """Call Ollama chat completion API (non-streaming).
    
    Ollama runs locally and doesn't require API keys.
    """
    if not settings.ollama_enabled:
        raise ValueError("Ollama is not enabled")
    
    url = f"{settings.ollama_base_url}/api/chat"
    
    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            
            return data["message"]["content"]
    except httpx.ConnectError:
        raise ValueError("Ollama service is not running. Start it with: ollama serve")
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise


async def ollama_chat_stream(messages: list[dict], model: str | None = None) -> AsyncIterator[str]:
    """Call Ollama chat completion API (streaming).
    
    Ollama supports streaming responses for better UX.
    """
    if not settings.ollama_enabled:
        raise ValueError("Ollama is not enabled")
    
    url = f"{settings.ollama_base_url}/api/chat"
    
    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": True
    }
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=120.0) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    try:
                        import json
                        data = json.loads(line)
                        
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        
                        if data.get("done", False):
                            break
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Ollama stream parse error: {e}")
                        continue
                        
    except httpx.ConnectError:
        raise ValueError("Ollama service is not running. Start it with: ollama serve")
    except Exception as e:
        logger.error(f"Ollama stream error: {e}")
        raise
