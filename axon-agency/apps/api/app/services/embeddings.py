import os
import hashlib
from typing import List, Optional
from loguru import logger
from starlette.concurrency import run_in_threadpool

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class EmbeddingService:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        self.dimension = 3072 if "large" in self.model else 1536
        self.use_openai = bool(self.openai_key)
        
        if self.use_openai:
            logger.info(f"Using OpenAI embeddings: {self.model}")
        else:
            logger.warning("No OpenAI API key found, using fallback embeddings")
            try:
                from sentence_transformers import SentenceTransformer
                self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.dimension = 384
                logger.info("Loaded sentence-transformers model")
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers: {e}")
                self.local_model = None
    
    async def embed_text(self, text: str) -> List[float]:
        if self.use_openai:
            return await self._embed_openai(text)
        elif hasattr(self, 'local_model') and self.local_model:
            return await run_in_threadpool(self._embed_local, text)
        else:
            return await run_in_threadpool(self._embed_fallback, text)
    
    async def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            if self.use_openai:
                batch_embeddings = await self._embed_openai_batch(batch)
            elif hasattr(self, 'local_model') and self.local_model:
                batch_embeddings = await run_in_threadpool(self._embed_local_batch, batch)
            else:
                batch_embeddings = [await run_in_threadpool(self._embed_fallback, t) for t in batch]
            embeddings.extend(batch_embeddings)
        return embeddings
    
    async def _embed_openai(self, text: str) -> List[float]:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={"input": text, "model": self.model},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
    
    async def _embed_openai_batch(self, texts: List[str]) -> List[List[float]]:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={"input": texts, "model": self.model},
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
    
    def _embed_local(self, text: str) -> List[float]:
        embedding = self.local_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def _embed_local_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.local_model.encode(texts, convert_to_tensor=False, batch_size=32)
        return embeddings.tolist()
    
    def _embed_fallback(self, text: str) -> List[float]:
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        if HAS_NUMPY:
            import numpy as np
            np.random.seed(seed)
            embedding = np.random.randn(self.dimension).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        else:
            import random
            random.seed(seed)
            embedding = [random.gauss(0, 1) for _ in range(self.dimension)]
            norm = sum(x*x for x in embedding) ** 0.5
            return [x / norm for x in embedding]
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if HAS_NUMPY:
            import numpy as np
            a_arr = np.array(a)
            b_arr = np.array(b)
            return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))
        else:
            dot = sum(x*y for x, y in zip(a, b))
            norm_a = sum(x*x for x in a) ** 0.5
            norm_b = sum(y*y for y in b) ** 0.5
            return dot / (norm_a * norm_b)


embedding_service = EmbeddingService()
