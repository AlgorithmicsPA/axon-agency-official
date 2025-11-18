"""OpenAI provider for LLM operations."""

import logging
import httpx
from typing import AsyncIterator
from app.core.config import settings

logger = logging.getLogger(__name__)


async def openai_chat(messages: list[dict], model: str | None = None, tools: list[dict] | None = None) -> str:
    """Call OpenAI chat completion API (non-streaming)."""
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key not configured")
    
    url = f"{settings.openai_base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model or settings.openai_model,
        "messages": messages
    }
    
    if tools:
        payload["tools"] = tools
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]["content"]


async def openai_chat_stream(messages: list[dict], model: str | None = None) -> AsyncIterator[str]:
    """Call OpenAI chat completion API (streaming)."""
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key not configured")
    
    url = f"{settings.openai_base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model or settings.openai_model,
        "messages": messages,
        "stream": True
    }
    
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=payload, headers=headers, timeout=60.0) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        import json
                        data = json.loads(data_str)
                        delta = data["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]
                    except Exception as e:
                        logger.warning(f"Stream parse error: {e}")
                        continue
