import httpx
from app.core.types import LLMInput, LLMResponse, LLMProvider
from loguru import logger


class SDXLAdapter:
    """Adapter for local SDXL image generation (Automatic1111/ComfyUI)."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
    
    async def infer(
        self,
        model: str,
        input_data: LLMInput,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Perform SDXL image generation (Automatic1111 API)."""
        payload = {
            "prompt": input_data.prompt,
            "negative_prompt": "",
            "steps": 20,
            "cfg_scale": 7,
            "width": 512,
            "height": 512,
        }
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/sdapi/v1/txt2img",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                image_base64 = data.get("images", [""])[0]
                
                return LLMResponse(
                    provider=LLMProvider.SDXL,
                    model=model,
                    output=f"Image generated (base64 length: {len(image_base64)})",
                    metadata={
                        "image_base64": image_base64,
                        "parameters": data.get("parameters", {}),
                    }
                )
                
        except httpx.ConnectError:
            logger.error(f"Cannot connect to SDXL at {self.base_url}")
            raise Exception(f"SDXL not available at {self.base_url}")
        except Exception as e:
            logger.error(f"SDXL error: {e}")
            raise Exception(f"SDXL inference failed: {str(e)}")
