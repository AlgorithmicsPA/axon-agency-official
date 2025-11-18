"""
Learning Service: Captures improvement outcomes and learns from success patterns.

This service integrates with RAG to build a knowledge base of what works and what doesn't,
enabling the agent to continuously improve its own improvement capabilities.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger
from pathlib import Path
import json
import asyncio

from app.services.vector_store import VectorStore
from app.services.embeddings import EmbeddingService
from app.models.self_improve import ImprovementJob


class ImprovementOutcome:
    """Structured outcome from an improvement job."""
    
    def __init__(
        self,
        job_id: str,
        success: bool,
        improvement_type: str,
        target_file: str,
        metrics_before: Dict[str, Any],
        metrics_after: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        code_changes: Optional[str] = None,
        lsp_errors_before: int = 0,
        lsp_errors_after: Optional[int] = None,
        timestamp: Optional[datetime] = None
    ):
        self.job_id = job_id
        self.success = success
        self.improvement_type = improvement_type
        self.target_file = target_file
        self.metrics_before = metrics_before
        self.metrics_after = metrics_after
        self.error_message = error_message
        self.code_changes = code_changes
        self.lsp_errors_before = lsp_errors_before
        self.lsp_errors_after = lsp_errors_after
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "job_id": self.job_id,
            "success": self.success,
            "improvement_type": self.improvement_type,
            "target_file": self.target_file,
            "metrics_before": self.metrics_before,
            "metrics_after": self.metrics_after,
            "error_message": self.error_message,
            "code_changes": self.code_changes,
            "lsp_errors_before": self.lsp_errors_before,
            "lsp_errors_after": self.lsp_errors_after,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_text(self) -> str:
        """Convert to searchable text for RAG embedding."""
        status = "SUCCESS" if self.success else "FAILURE"
        
        text = f"""Improvement Job: {self.job_id}
Status: {status}
Type: {self.improvement_type}
Timestamp: {self.timestamp.isoformat()}

Target File: {self.target_file}

Metrics Before:
  LOC: {self.metrics_before.get('loc', 'N/A')}
  Complexity: {self.metrics_before.get('complexity', 'N/A')}
  LSP Errors: {self.lsp_errors_before}

"""
        
        if self.success and self.metrics_after:
            text += f"""Metrics After:
  LOC: {self.metrics_after.get('loc', 'N/A')}
  Complexity: {self.metrics_after.get('complexity', 'N/A')}
  LSP Errors: {self.lsp_errors_after}

"""
        
        if self.error_message:
            text += f"Error: {self.error_message}\n\n"
        
        if self.code_changes:
            text += f"Code Changes:\n{self.code_changes}\n"
        
        return text


class LearningService:
    """
    Service to capture and learn from improvement outcomes.
    
    Current implementation (Opción A - MVP):
    - Persists outcomes to JSONL on disk
    - Re-embeds all historical outcomes on startup
    - Simple, robust, no state corruption risk
    
    TODO: Future optimization (Opción C - Hybrid FAISS persistence):
    When corpus grows >500-1000 outcomes or startup time >5s:
    1. Persist FAISS index to disk (index.faiss + meta.json with checksum)
    2. Load from disk on startup if compatible (model/dim/metric match)
    3. Fallback to re-embed if index outdated/corrupted
    4. Background rebuild while serving traffic
    See design doc in attached_assets/Pasted-eredicto-*.txt for full spec
    """
    
    def __init__(self, vector_store: VectorStore, embeddings: EmbeddingService, storage_path: str = "storage/learning"):
        """Initialize learning service with vector store for RAG integration."""
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.corpus_id = "improvement_outcomes"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Document ID mapping
        self.doc_id_map_file = self.storage_path / "doc_id_map.json"
        self.doc_id_map: Dict[str, int] = {}
        self._load_doc_id_map()
        
        # Load historical outcomes
        self.outcomes_file = self.storage_path / "outcomes.jsonl"
        self.outcomes: List[ImprovementOutcome] = []
        self._load_outcomes()
        
        # Rehydration flag
        self._rehydrated = False
    
    def _load_doc_id_map(self):
        """Load document ID mapping."""
        if self.doc_id_map_file.exists():
            try:
                with open(self.doc_id_map_file, 'r') as f:
                    self.doc_id_map = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load doc ID map: {e}")
                self.doc_id_map = {}
    
    def _save_doc_id_map(self):
        """Save document ID mapping."""
        try:
            with open(self.doc_id_map_file, 'w') as f:
                json.dump(self.doc_id_map, f)
        except Exception as e:
            logger.error(f"Failed to save doc ID map: {e}")
    
    def _load_outcomes(self):
        """Load historical outcomes from disk."""
        if not self.outcomes_file.exists():
            return
        
        try:
            with open(self.outcomes_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.outcomes.append(self._dict_to_outcome(data))
            logger.info(f"Loaded {len(self.outcomes)} historical improvement outcomes")
        except Exception as e:
            logger.error(f"Failed to load outcomes: {e}")
    
    async def initialize(self):
        """
        Initialize the learning service asynchronously.
        Must be called during FastAPI startup to rehydrate vector store.
        """
        if self._rehydrated:
            logger.warning("LearningService already initialized")
            return
        
        await self._rehydrate_vector_store()
        self._rehydrated = True
    
    async def _rehydrate_vector_store(self):
        """
        Rehydrate vector store from historical outcomes.
        
        Current approach (Opción A): Re-embed all outcomes on each startup.
        - Pros: Simple, always consistent with JSONL source, no corruption
        - Cons: Slower startup as corpus grows (acceptable for MVP)
        
        TODO: Migrate to Opción C when corpus >500 entries for instant startup
        """
        if not self.outcomes:
            logger.info("No historical outcomes to rehydrate")
            return
        
        import time
        start_time = time.time()
        
        logger.info(f"Rehydrating vector store with {len(self.outcomes)} outcomes...")
        
        # Clear existing index to prevent duplication on restart
        try:
            self.vector_store.delete_index(self.corpus_id)
            logger.info(f"Cleared existing index for {self.corpus_id}")
        except Exception as e:
            logger.warning(f"Failed to clear index (may not exist yet): {e}")
        
        # Collect texts to embed
        texts = [outcome.to_text() for outcome in self.outcomes]
        job_ids = [outcome.job_id for outcome in self.outcomes]
        
        # Embed all texts
        embed_start = time.time()
        try:
            embeddings = await self.embeddings.embed_batch(texts)
            embed_time = time.time() - embed_start
            logger.info(f"Embedded {len(texts)} outcomes in {embed_time:.2f}s ({len(texts)/embed_time:.1f} outcomes/s)")
            
            # Update doc_id_map if needed
            for job_id in job_ids:
                if job_id not in self.doc_id_map:
                    self.doc_id_map[job_id] = len(self.doc_id_map)
            
            # Get doc IDs in order
            doc_ids = [self.doc_id_map[jid] for jid in job_ids]
            
            # Add all vectors to store
            self.vector_store.add_vectors(
                corpus_id=self.corpus_id,
                vectors=embeddings,
                ids=doc_ids
            )
            
            # Save updated map
            self._save_doc_id_map()
            
            total_time = time.time() - start_time
            logger.info(f"✅ Rehydrated {len(embeddings)} outcomes to vector store in {total_time:.2f}s")
        except Exception as e:
            logger.error(f"❌ Failed to rehydrate vector store after {time.time() - start_time:.2f}s: {e}")
            logger.error("Rehydration failure - service may have incomplete data")
            # Don't raise - allow service to start with empty store rather than crash
            # This provides graceful degradation for MVP
    
    def _dict_to_outcome(self, data: Dict[str, Any]) -> ImprovementOutcome:
        """Convert dictionary to ImprovementOutcome."""
        return ImprovementOutcome(
            job_id=data["job_id"],
            success=data["success"],
            improvement_type=data["improvement_type"],
            target_file=data["target_file"],
            metrics_before=data["metrics_before"],
            metrics_after=data.get("metrics_after"),
            error_message=data.get("error_message"),
            code_changes=data.get("code_changes"),
            lsp_errors_before=data.get("lsp_errors_before", 0),
            lsp_errors_after=data.get("lsp_errors_after"),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
    
    def _save_outcome(self, outcome: ImprovementOutcome):
        """Append outcome to JSONL file."""
        try:
            with open(self.outcomes_file, 'a') as f:
                f.write(json.dumps(outcome.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Failed to save outcome: {e}")
    
    async def log_outcome_from_fields(
        self,
        job_id: str,
        success: bool,
        improvement_type: str,
        target_file: str,
        metrics_before: Dict[str, Any],
        metrics_after: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        code_changes: Optional[str] = None,
        lsp_errors_before: int = 0,
        lsp_errors_after: Optional[int] = None
    ) -> int:
        """
        Log an improvement outcome from individual fields (used by API endpoint).
        
        Args:
            job_id: Unique job identifier
            success: Whether the improvement was successful
            improvement_type: Type of improvement attempted
            target_file: Target file path
            metrics_before: Code metrics before improvement
            metrics_after: Code metrics after improvement (if successful)
            error_message: Error message (if failed)
            code_changes: Git diff or code changes made
            lsp_errors_before: LSP errors before improvement
            lsp_errors_after: LSP errors after improvement
        
        Returns:
            Document ID in vector store
        """
        # Create outcome
        outcome = ImprovementOutcome(
            job_id=job_id,
            success=success,
            improvement_type=improvement_type,
            target_file=target_file,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            error_message=error_message,
            code_changes=code_changes,
            lsp_errors_before=lsp_errors_before,
            lsp_errors_after=lsp_errors_after,
        )
        
        # Save to disk
        self._save_outcome(outcome)
        self.outcomes.append(outcome)
        
        # Embed text for RAG
        text = outcome.to_text()
        embedding = await self.embeddings.embed_text(text)
        
        # Get next doc ID
        next_id = len(self.doc_id_map)
        self.doc_id_map[job_id] = next_id
        self._save_doc_id_map()
        
        # Add to vector store
        self.vector_store.add_vectors(
            corpus_id=self.corpus_id,
            vectors=[embedding],
            ids=[next_id]
        )
        
        logger.info(f"Logged improvement outcome {job_id} (success={success}) to RAG (doc_id={next_id})")
        return next_id
    
    async def log_improvement_outcome(
        self,
        job: ImprovementJob,
        success: bool,
        metrics_after: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        code_changes: Optional[str] = None,
        lsp_errors_after: Optional[int] = None
    ) -> int:
        """
        Log an improvement outcome to both disk and RAG memory.
        
        Args:
            job: The improvement job that was executed
            success: Whether the improvement was successful
            metrics_after: Code metrics after improvement (if successful)
            error_message: Error message (if failed)
            code_changes: Git diff or code changes made
            lsp_errors_after: LSP errors after improvement
        
        Returns:
            Document ID in vector store
        """
        # Extract metrics from job
        metrics_before = {
            "loc": job.before_metrics.get("lines_of_code", 0),
            "complexity": job.before_metrics.get("complexity", 0),
            "dependencies": len(job.before_metrics.get("dependencies", []))
        }
        
        # Create outcome
        outcome = ImprovementOutcome(
            job_id=job.job_id,
            success=success,
            improvement_type=job.improvement_type.value,
            target_file=job.target_file,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            error_message=error_message,
            code_changes=code_changes,
            lsp_errors_before=0,  # TODO: Track LSP errors from job
            lsp_errors_after=lsp_errors_after,
        )
        
        # Save to disk
        self._save_outcome(outcome)
        self.outcomes.append(outcome)
        
        # Embed text for RAG
        text = outcome.to_text()
        embedding = await self.embeddings.embed_text(text)
        
        # Get next doc ID
        next_id = len(self.doc_id_map)
        self.doc_id_map[job.job_id] = next_id
        self._save_doc_id_map()
        
        # Add to vector store
        self.vector_store.add_vectors(
            corpus_id=self.corpus_id,
            vectors=[embedding],
            ids=[next_id]
        )
        
        logger.info(f"Logged improvement outcome {job.job_id} (success={success}) to RAG (doc_id={next_id})")
        return next_id
    
    async def get_similar_outcomes(
        self,
        improvement_type: str,
        target_file: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar past improvement outcomes to learn from.
        
        Args:
            improvement_type: Type of improvement to search for
            target_file: File being targeted
            limit: Maximum number of results
        
        Returns:
            List of similar outcomes with scores
        """
        query = f"Improvement type: {improvement_type}\nTarget file: {target_file}"
        
        # Embed query
        query_vector = await self.embeddings.embed_text(query)
        
        # Offload vector store search to thread pool (numpy operations)
        results = await asyncio.to_thread(
            self.vector_store.search,
            corpus_id=self.corpus_id,
            query_vector=query_vector,
            k=limit
        )
        
        # Map results to outcomes
        similar_outcomes = []
        for doc_id, score in results:
            # Find outcome by doc_id
            job_id = next((jid for jid, did in self.doc_id_map.items() if did == doc_id), None)
            if job_id:
                outcome = next((o for o in self.outcomes if o.job_id == job_id), None)
                if outcome:
                    similar_outcomes.append({
                        "job_id": outcome.job_id,
                        "success": outcome.success,
                        "improvement_type": outcome.improvement_type,
                        "target_file": outcome.target_file,
                        "similarity_score": float(score),
                        "timestamp": outcome.timestamp.isoformat()
                    })
        
        return similar_outcomes
    
    def get_success_rate(self, improvement_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate success rate for improvement jobs.
        
        Args:
            improvement_type: Filter by improvement type (optional)
        
        Returns:
            Success rate statistics
        """
        outcomes = self.outcomes
        if improvement_type:
            outcomes = [o for o in outcomes if o.improvement_type == improvement_type]
        
        if not outcomes:
            return {
                "total": 0,
                "success": 0,
                "failure": 0,
                "success_rate": 0.0
            }
        
        success_count = sum(1 for o in outcomes if o.success)
        failure_count = len(outcomes) - success_count
        
        return {
            "total": len(outcomes),
            "success": success_count,
            "failure": failure_count,
            "success_rate": success_count / len(outcomes) if outcomes else 0.0
        }
    
    def get_common_failure_modes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Identify most common failure modes.
        
        Args:
            limit: Maximum number of failure modes to return
        
        Returns:
            List of common failure patterns
        """
        failures = [o for o in self.outcomes if not o.success and o.error_message]
        
        # Group by error message prefix (first 100 chars)
        error_counts: Dict[str, List[ImprovementOutcome]] = {}
        for outcome in failures:
            error_prefix = outcome.error_message[:100] if outcome.error_message else "Unknown"
            if error_prefix not in error_counts:
                error_counts[error_prefix] = []
            error_counts[error_prefix].append(outcome)
        
        # Sort by frequency
        common_errors = sorted(
            error_counts.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:limit]
        
        return [
            {
                "error_pattern": error,
                "count": len(outcomes),
                "improvement_types": list(set(o.improvement_type for o in outcomes)),
                "example_job_id": outcomes[0].job_id
            }
            for error, outcomes in common_errors
        ]
    
    def get_best_performing_types(self) -> List[Dict[str, Any]]:
        """
        Identify which improvement types perform best.
        
        Returns:
            List of improvement types sorted by success rate
        """
        type_stats: Dict[str, Dict[str, int]] = {}
        
        for outcome in self.outcomes:
            if outcome.improvement_type not in type_stats:
                type_stats[outcome.improvement_type] = {"total": 0, "success": 0}
            
            type_stats[outcome.improvement_type]["total"] += 1
            if outcome.success:
                type_stats[outcome.improvement_type]["success"] += 1
        
        # Calculate success rates and sort
        results = []
        for imp_type, stats in type_stats.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            results.append({
                "improvement_type": imp_type,
                "total": stats["total"],
                "success": stats["success"],
                "success_rate": success_rate
            })
        
        return sorted(results, key=lambda x: x["success_rate"], reverse=True)
    
    async def get_success_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive success statistics for the Architect.
        
        Returns:
            Dictionary with overall and type-specific success rates
        """
        # Get overall success rate
        overall = self.get_success_rate()
        
        # Get type-specific rates
        type_rates = {}
        improvement_types = set(o.improvement_type for o in self.outcomes)
        for imp_type in improvement_types:
            type_stats = self.get_success_rate(improvement_type=imp_type)
            type_rates[imp_type] = type_stats["success_rate"]
        
        return {
            "overall_success_rate": overall["success_rate"],
            "by_type": type_rates,
            "total_outcomes": overall["total"]
        }
