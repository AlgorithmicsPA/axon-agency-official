"""
Learning API endpoints: Access learning patterns and improvement analytics.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.services.learning import LearningService
from app.services.vector_store import VectorStore
from app.services.embeddings import EmbeddingService


router = APIRouter(prefix="/api/learning", tags=["learning"])


# Initialize services (rehydration happens in FastAPI startup)
vector_store = VectorStore()
embeddings = EmbeddingService()
learning_service = LearningService(vector_store, embeddings)


async def initialize_learning_service():
    """Initialize learning service - called from FastAPI startup."""
    await learning_service.initialize()


class OutcomeQuery(BaseModel):
    """Query parameters for finding similar outcomes."""
    improvement_type: str
    target_file: str
    limit: int = 5


class SuccessRateResponse(BaseModel):
    """Success rate statistics."""
    total: int
    success: int
    failure: int
    success_rate: float
    improvement_type: Optional[str] = None


class FailureModeResponse(BaseModel):
    """Common failure mode."""
    error_pattern: str
    count: int
    improvement_types: List[str]
    example_job_id: str


class ImprovementTypeStats(BaseModel):
    """Statistics for an improvement type."""
    improvement_type: str
    total: int
    success: int
    success_rate: float


class LogOutcomeRequest(BaseModel):
    """Request body for logging improvement outcome."""
    job_id: str
    success: bool
    improvement_type: str
    target_file: str
    metrics_before: Dict[str, Any]
    metrics_after: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    code_changes: Optional[str] = None
    lsp_errors_before: int = 0
    lsp_errors_after: Optional[int] = None


@router.post("/log-outcome")
async def log_outcome(request: LogOutcomeRequest):
    """
    Log an improvement outcome to the learning system.
    
    Args:
        request: Outcome details including success, metrics, and changes
    
    Returns:
        Confirmation message
    """
    try:
        await learning_service.log_outcome_from_fields(
            job_id=request.job_id,
            success=request.success,
            improvement_type=request.improvement_type,
            target_file=request.target_file,
            metrics_before=request.metrics_before,
            metrics_after=request.metrics_after,
            error_message=request.error_message,
            code_changes=request.code_changes,
            lsp_errors_before=request.lsp_errors_before,
            lsp_errors_after=request.lsp_errors_after
        )
        return {
            "status": "success",
            "message": f"Outcome logged for job {request.job_id}",
            "job_id": request.job_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log outcome: {str(e)}")


@router.get("/stats/success-rate", response_model=SuccessRateResponse)
async def get_success_rate(improvement_type: Optional[str] = None):
    """
    Get success rate for improvement jobs.
    
    Args:
        improvement_type: Filter by specific improvement type (optional)
    
    Returns:
        Success rate statistics
    """
    stats = learning_service.get_success_rate(improvement_type)
    return SuccessRateResponse(**stats, improvement_type=improvement_type)


@router.get("/stats/failure-modes", response_model=List[FailureModeResponse])
async def get_failure_modes(limit: int = 10):
    """
    Get most common failure modes from past improvements.
    
    Args:
        limit: Maximum number of failure modes to return
    
    Returns:
        List of common failure patterns
    """
    return learning_service.get_common_failure_modes(limit)


@router.get("/stats/best-types", response_model=List[ImprovementTypeStats])
async def get_best_performing_types():
    """
    Get improvement types ranked by success rate.
    
    Returns:
        List of improvement types sorted by performance
    """
    return learning_service.get_best_performing_types()


@router.post("/similar-outcomes")
async def find_similar_outcomes(query: OutcomeQuery) -> List[Dict[str, Any]]:
    """
    Find similar past improvement outcomes using RAG.
    
    Args:
        query: Query parameters (improvement type, target file, limit)
    
    Returns:
        List of similar outcomes with similarity scores
    """
    results = await learning_service.get_similar_outcomes(
        improvement_type=query.improvement_type,
        target_file=query.target_file,
        limit=query.limit
    )
    return results


@router.get("/outcomes/count")
async def get_outcomes_count() -> Dict[str, int]:
    """
    Get total count of logged outcomes.
    
    Returns:
        Count statistics
    """
    total = len(learning_service.outcomes)
    success = sum(1 for o in learning_service.outcomes if o.success)
    failure = total - success
    
    return {
        "total": total,
        "success": success,
        "failure": failure
    }


@router.get("/health")
async def learning_health():
    """Check learning service health."""
    return {
        "status": "healthy",
        "outcomes_loaded": len(learning_service.outcomes),
        "vector_store": "connected"
    }
