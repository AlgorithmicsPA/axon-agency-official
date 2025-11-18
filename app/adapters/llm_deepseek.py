import httpx
from app.core.types import LLMInput, LLMResponse, LLMProvider, LLMInputKind
from loguru import logger


class DeepSeekAdapter:
    """Adapter for DeepSeek API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
    
    async def infer(
        self,
        model: str,
        input_data: LLMInput,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Perform DeepSeek inference."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        messages = [{"role": "user", "content": input_data.prompt}]
        
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
                    provider=LLMProvider.DEEPSEEK,
                    model=model,
                    output=data["choices"][0]["message"]["content"],
                    usage=data.get("usage"),
                )
                
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise Exception(f"DeepSeek inference failed: {str(e)}")
