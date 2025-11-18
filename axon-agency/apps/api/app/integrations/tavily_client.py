"""Tavily Web Search Client for WhatsApp Sales Agent."""

import httpx
from typing import Optional
from loguru import logger


class TavilyClient:
    """Client for performing web searches using Tavily API."""
    
    def __init__(self, api_key: str):
        """
        Initialize Tavily client.
        
        Args:
            api_key: Tavily API key for authentication
        """
        self.api_url = "https://api.tavily.com/search"
        self._api_key = api_key
        
        truncated_key = api_key[:15] + "..." if len(api_key) > 15 else "***"
        logger.info(f"Tavily client initialized. Key: {truncated_key}")
    
    async def search_web(self, query: str, max_results: int = 3) -> Optional[str]:
        """
        Search the web using Tavily API.
        
        Args:
            query: Search query
            max_results: Maximum number of results (default: 3)
        
        Returns:
            Formatted string with search results, or None if error/empty
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "api_key": self._api_key,
                        "query": query,
                        "max_results": max_results,
                        "search_depth": "basic",
                        "include_answer": True,
                        "include_raw_content": False
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                answer = data.get("answer")
                
                if not results and not answer:
                    logger.info("Tavily search returned no results")
                    return None
                
                output_parts = []
                
                if answer:
                    output_parts.append(f"Respuesta: {answer}")
                
                if results:
                    output_parts.append("Fuentes:")
                    for result in results[:max_results]:
                        title = result.get("title", "Sin título")
                        url = result.get("url", "")
                        snippet = result.get("content", "")[:150]
                        output_parts.append(f"- {title}: {snippet}... ({url})")
                
                formatted = "\n".join(output_parts)
                logger.info(f"Tavily search successful. Results: {len(results)}")
                return formatted
                
        except httpx.HTTPStatusError as e:
            error_msg = str(e)[:200]
            logger.error(f"Tavily HTTP error: {error_msg}")
            return None
        except Exception as e:
            error_msg = str(e)[:200]
            logger.error(f"Tavily search failed: {error_msg}")
            return None
