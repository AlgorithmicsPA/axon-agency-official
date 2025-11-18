"""Melvis RAG/Vector Search Client for WhatsApp Sales Agent."""

import httpx
from typing import Optional
from loguru import logger


class MelvisClient:
    """Client for querying Melvis vector database for knowledge base chunks."""
    
    def __init__(self, api_url: str, api_key: str, collection: str):
        """
        Initialize Melvis client.
        
        Args:
            api_url: Melvis API base URL
            api_key: Melvis API key for authentication
            collection: Collection name to query
        """
        self.api_url = api_url
        self._api_key = api_key
        self.collection = collection
        
        truncated_key = api_key[:15] + "..." if len(api_key) > 15 else "***"
        logger.info(f"Melvis client initialized. Collection: {collection}, Key: {truncated_key}")
    
    async def query_knowledge_base(self, query: str, limit: int = 3) -> Optional[str]:
        """
        Query Melvis vector store for relevant knowledge base chunks.
        
        Args:
            query: User's question or search term
            limit: Number of results to return (default: 3)
        
        Returns:
            Formatted string with top chunks, or None if error/empty
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.api_url}/search",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "collection": self.collection,
                        "query": query,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    logger.info("Melvis query returned no results")
                    return None
                
                chunks = [
                    f"- {result.get('text', result.get('content', 'N/A'))}"
                    for result in results[:limit]
                ]
                formatted = "\n".join(chunks)
                
                logger.info(f"Melvis query successful. Chunks: {len(results)}")
                return formatted
                
        except httpx.HTTPStatusError as e:
            error_msg = str(e)[:200]
            logger.error(f"Melvis HTTP error: {error_msg}")
            return None
        except Exception as e:
            error_msg = str(e)[:200]
            logger.error(f"Melvis query failed: {error_msg}")
            return None
