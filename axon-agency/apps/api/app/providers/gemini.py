"""Google Gemini provider for multimodal LLM operations."""

import logging
import httpx
import base64
from typing import AsyncIterator
from app.core.config import settings

logger = logging.getLogger(__name__)


async def gemini_chat(
    messages: list[dict],
    model: str | None = None,
    images: list[str] | None = None
) -> str:
    """Call Google Gemini API (non-streaming).
    
    Args:
        messages: Chat history in OpenAI format
        model: Model name (default: gemini-1.5-pro-latest)
        images: Optional list of base64 images or URLs
    
    Returns:
        Generated text response
    """
    if not settings.gemini_api_key:
        raise ValueError("Gemini API key not configured")
    
    model_name = model or settings.gemini_model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    
    headers = {
        "x-goog-api-key": settings.gemini_api_key,
        "Content-Type": "application/json"
    }
    
    # Convert OpenAI format to Gemini format
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        parts = [{"text": msg["content"]}]
        
        # Add images if provided and this is the last user message
        if images and msg == messages[-1] and msg["role"] == "user":
            for img in images:
                if img.startswith("data:image"):
                    # Extract base64 data
                    img_data = img.split(",")[1]
                    mime_type = img.split(";")[0].split(":")[1]
                    parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": img_data
                        }
                    })
                elif img.startswith("http"):
                    # URL-based image
                    parts.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": await _download_image_base64(img)
                        }
                    })
        
        contents.append({
            "role": role,
            "parts": parts
        })
    
    payload = {"contents": contents}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        
        if "candidates" not in data or not data["candidates"]:
            raise ValueError(f"No response from Gemini: {data}")
        
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def gemini_chat_stream(
    messages: list[dict],
    model: str | None = None,
    images: list[str] | None = None
) -> AsyncIterator[str]:
    """Call Google Gemini API (streaming).
    
    Args:
        messages: Chat history in OpenAI format
        model: Model name (default: gemini-1.5-pro-latest)
        images: Optional list of base64 images or URLs
    
    Yields:
        Text chunks as they arrive
    """
    if not settings.gemini_api_key:
        raise ValueError("Gemini API key not configured")
    
    model_name = model or settings.gemini_model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent"
    
    headers = {
        "x-goog-api-key": settings.gemini_api_key,
        "Content-Type": "application/json"
    }
    params = {"alt": "sse"}
    
    # Convert messages
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        parts = [{"text": msg["content"]}]
        
        if images and msg == messages[-1] and msg["role"] == "user":
            for img in images:
                if img.startswith("data:image"):
                    img_data = img.split(",")[1]
                    mime_type = img.split(";")[0].split(":")[1]
                    parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": img_data
                        }
                    })
        
        contents.append({"role": role, "parts": parts})
    
    payload = {"contents": contents}
    
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=payload, headers=headers, params=params, timeout=120.0) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    
                    try:
                        import json
                        data = json.loads(data_str)
                        
                        if "candidates" in data and data["candidates"]:
                            candidate = data["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                for part in candidate["content"]["parts"]:
                                    if "text" in part:
                                        yield part["text"]
                    except Exception as e:
                        logger.warning(f"Gemini stream parse error: {e}")
                        continue


async def _download_image_base64(url: str) -> str:
    """Download image from URL and convert to base64."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")


async def gemini_analyze_image(image_data: str, prompt: str) -> str:
    """Analyze an image with Gemini Vision.
    
    Args:
        image_data: Base64 image data or URL
        prompt: Analysis prompt
    
    Returns:
        Analysis result
    """
    messages = [{"role": "user", "content": prompt}]
    return await gemini_chat(messages, images=[image_data])
