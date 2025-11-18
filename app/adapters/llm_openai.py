import httpx
from app.core.types import LLMInput, LLMResponse, LLMProvider, LLMInputKind
from loguru import logger


class OpenAIAdapter:
    """Adapter for OpenAI API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    async def infer(
        self,
        model: str,
        input_data: LLMInput,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Perform OpenAI inference."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        messages = []
        
        if input_data.kind == LLMInputKind.TEXT:
            messages.append({"role": "user", "content": input_data.prompt})
        elif input_data.kind in [LLMInputKind.IMAGE, LLMInputKind.TEXT_AND_IMAGE]:
            content = [{"type": "text", "text": input_data.prompt}]
            
            if input_data.image_url:
                content.append({"type": "image_url", "image_url": {"url": input_data.image_url}})
            elif input_data.image_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{input_data.image_base64}"}
                })
            
            messages.append({"role": "user", "content": content})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                return LLMResponse(
                    provider=LLMProvider.OPENAI,
                    model=model,
                    output=data["choices"][0]["message"]["content"],
                    usage=data.get("usage"),
                )
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI inference failed: {str(e)}")
