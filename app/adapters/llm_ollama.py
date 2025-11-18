import httpx
from app.core.types import LLMInput, LLMResponse, LLMProvider
from loguru import logger


class OllamaAdapter:
    """Adapter for Ollama local LLM."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
    
    async def infer(
        self,
        model: str,
        input_data: LLMInput,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Perform Ollama inference."""
        payload = {
            "model": model,
            "prompt": input_data.prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                return LLMResponse(
                    provider=LLMProvider.OLLAMA,
                    model=model,
                    output=data.get("response", ""),
                    metadata={
                        "total_duration": data.get("total_duration"),
                        "load_duration": data.get("load_duration"),
                    }
                )
                
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise Exception(f"Ollama not available at {self.base_url}")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise Exception(f"Ollama inference failed: {str(e)}")
