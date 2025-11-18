import httpx
from app.core.types import LLMInput, LLMResponse, LLMProvider, LLMInputKind
from loguru import logger


class GeminiAdapter:
    """Adapter for Google Gemini API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    async def infer(
        self,
        model: str,
        input_data: LLMInput,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Perform Gemini inference."""
        parts = [{"text": input_data.prompt}]
        
        if input_data.kind in [LLMInputKind.IMAGE, LLMInputKind.TEXT_AND_IMAGE]:
            if input_data.image_base64:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": input_data.image_base64
                    }
                })
        
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{model}:generateContent?key={self.api_key}",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                output = data["candidates"][0]["content"]["parts"][0]["text"]
                
                return LLMResponse(
                    provider=LLMProvider.GEMINI,
                    model=model,
                    output=output,
                    usage=data.get("usageMetadata"),
                )
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise Exception(f"Gemini inference failed: {str(e)}")
