import os
import pickle
from pathlib import Path
from typing import List, Tuple, Optional
from loguru import logger

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class VectorStore:
    def __init__(self, storage_root: str = "./storage/vectors"):
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.use_faiss = self._init_faiss()
        
        if not self.use_faiss:
            if HAS_NUMPY:
                logger.warning("FAISS not available, using simple numpy search")
            else:
                logger.warning("FAISS and numpy not available, using basic fallback")
    
    def _init_faiss(self) -> bool:
        try:
            import faiss
            self.faiss = faiss
            logger.info("FAISS initialized successfully")
            return True
        except ImportError:
            logger.warning("FAISS not available, falling back to numpy")
            return False
    
    def create_index(self, corpus_id: str, dimension: int = 3072):
        index_path = self.storage_root / f"{corpus_id}.index"
        meta_path = self.storage_root / f"{corpus_id}.meta"
        
        if self.use_faiss:
            index = self.faiss.IndexFlatIP(dimension)
            self.faiss.write_index(index, str(index_path))
        else:
            if HAS_NUMPY:
                import numpy as np
                data = {
                    "vectors": np.array([], dtype=np.float32).reshape(0, dimension),
                    "ids": [],
                }
            else:
                data = {
                    "vectors": [],
                    "ids": [],
                }
            with open(index_path, 'wb') as f:
                pickle.dump(data, f)
        
        meta = {"dimension": dimension, "count": 0}
        with open(meta_path, 'wb') as f:
            pickle.dump(meta, f)
        
        logger.info(f"Created index for corpus {corpus_id} (dimension={dimension})")
    
    def add_vectors(
        self,
        corpus_id: str,
        vectors: List[List[float]],
        ids: List[int]
    ):
        index_path = self.storage_root / f"{corpus_id}.index"
        meta_path = self.storage_root / f"{corpus_id}.meta"
        
        if not index_path.exists():
            dimension = len(vectors[0]) if vectors else 3072
            self.create_index(corpus_id, dimension)
        
        if HAS_NUMPY:
            import numpy as np
            vectors_array = np.array(vectors, dtype=np.float32)
        else:
            vectors_array = vectors
        
        if self.use_faiss:
            index = self.faiss.read_index(str(index_path))
            
            norms = np.linalg.norm(vectors_array, axis=1, keepdims=True)
            norms[norms == 0] = 1
            vectors_array = vectors_array / norms
            
            index.add(vectors_array)
            self.faiss.write_index(index, str(index_path))
        else:
            with open(index_path, 'rb') as f:
                data = pickle.load(f)
            
            norms = np.linalg.norm(vectors_array, axis=1, keepdims=True)
            norms[norms == 0] = 1
            vectors_array = vectors_array / norms
            
            if data["vectors"].shape[0] == 0:
                data["vectors"] = vectors_array
            else:
                data["vectors"] = np.vstack([data["vectors"], vectors_array])
            data["ids"].extend(ids)
            
            with open(index_path, 'wb') as f:
                pickle.dump(data, f)
        
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)
        meta["count"] += len(vectors)
        with open(meta_path, 'wb') as f:
            pickle.dump(meta, f)
        
        logger.info(f"Added {len(vectors)} vectors to corpus {corpus_id}")
    
    def search(
        self,
        corpus_id: str,
        query_vector: List[float],
        k: int = 10
    ) -> List[Tuple[int, float]]:
        index_path = self.storage_root / f"{corpus_id}.index"
        
        if not index_path.exists():
            logger.warning(f"Index not found for corpus {corpus_id}")
            return []
        
        query_array = np.array([query_vector], dtype=np.float32)
        norm = np.linalg.norm(query_array)
        if norm > 0:
            query_array = query_array / norm
        
        if self.use_faiss:
            index = self.faiss.read_index(str(index_path))
            distances, indices = index.search(query_array, k)
            
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx != -1:
                    results.append((int(idx), float(dist)))
            return results
        else:
            with open(index_path, 'rb') as f:
                data = pickle.load(f)
            
            if data["vectors"].shape[0] == 0:
                return []
            
            similarities = np.dot(data["vectors"], query_array.T).flatten()
            top_indices = np.argsort(similarities)[::-1][:k]
            
            results = []
            for idx in top_indices:
                chunk_id = data["ids"][idx]
                score = float(similarities[idx])
                results.append((chunk_id, score))
            
            return results
    
    def get_stats(self, corpus_id: str) -> dict:
        meta_path = self.storage_root / f"{corpus_id}.meta"
        
        if not meta_path.exists():
            return {"exists": False, "count": 0, "dimension": 0}
        
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)
        
        return {
            "exists": True,
            "count": meta.get("count", 0),
            "dimension": meta.get("dimension", 0),
            "backend": "faiss" if self.use_faiss else "numpy"
        }
    
    def delete_index(self, corpus_id: str):
        index_path = self.storage_root / f"{corpus_id}.index"
        meta_path = self.storage_root / f"{corpus_id}.meta"
        
        if index_path.exists():
            index_path.unlink()
        if meta_path.exists():
            meta_path.unlink()
        
        logger.info(f"Deleted index for corpus {corpus_id}")


vector_store = VectorStore()
