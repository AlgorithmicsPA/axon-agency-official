"""
Autonomous Agent API: Control the self-improving AI agent.

This router exposes endpoints to start, monitor, and control autonomous
improvement sessions where the agent continuously improves itself.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from loguru import logger

from app.services.autonomous_agent import (
    AutonomousAgentService,
    AgentMode
)
from app.core.security import get_current_user_optional, get_current_user, require_admin


router = APIRouter(prefix="/api/agent/autonomous", tags=["autonomous-agent"])


# Initialize autonomous agent service (learning_service imported from learning router)
autonomous_agent: Optional[AutonomousAgentService] = None


async def get_autonomous_agent():
    """Get or create autonomous agent instance."""
    global autonomous_agent
    if autonomous_agent is None:
        from app.routers.learning import learning_service
        autonomous_agent = AutonomousAgentService(learning_service=learning_service)
    return autonomous_agent


class StartSessionRequest(BaseModel):
    """Request to start an autonomous session."""
    mode: AgentMode = AgentMode.BALANCED
    max_iterations: int = 10
    session_id: Optional[str] = None


class StartSessionResponse(BaseModel):
    """Response from starting a session."""
    session_id: str
    mode: str
    max_iterations: int
    status: str
    started_at: str


class CurrentIterationDetails(BaseModel):
    """Current iteration details."""
    iteration_number: int
    phase: str
    opportunity: Optional[Dict[str, Any]] = None
    status: str


class SessionStatusResponse(BaseModel):
    """Current status of an autonomous session."""
    session_id: str
    status: str
    mode: str
    iteration: str
    improvements_attempted: int
    improvements_succeeded: int
    improvements_failed: int
    success_rate: float
    last_action: Optional[str]
    started_at: str
    errors: List[str]
    current_iteration_details: Optional[CurrentIterationDetails] = None


class IterationResponse(BaseModel):
    """Detailed iteration information."""
    iteration_number: int
    opportunity: Optional[Dict[str, Any]]
    proposal: Optional[Dict[str, Any]]
    council_decision: Optional[Dict[str, Any]]
    architect_decision: Optional[Dict[str, Any]]
    execution_result: Optional[Dict[str, Any]]
    success: bool
    timestamp: str


class ImprovementResponse(BaseModel):
    """Detailed improvement information."""
    file_path: Optional[str]
    improvement_type: Optional[str]
    diff: Optional[str]
    council_review: Optional[Dict[str, Any]]
    architect_review: Optional[Dict[str, Any]]
    applied: bool
    outcome: Dict[str, Any]
    timestamp: str


class GlobalStatsResponse(BaseModel):
    """Global statistics across all sessions."""
    total_sessions: int
    total_improvements_attempted: int
    total_improvements_succeeded: int
    overall_success_rate: float
    success_rate_by_improvement_type: Dict[str, float]
    success_rate_by_mode: Dict[str, float]
    avg_iterations_per_session: float


@router.post("/start", response_model=StartSessionResponse)
async def start_autonomous_session(
    request: StartSessionRequest,
    current_user = Depends(get_current_user_optional),  # DEV_MODE compatible
    agent: AutonomousAgentService = Depends(get_autonomous_agent)
):
    """
    Start an autonomous self-improvement session.
    
    The agent will:
    1. Analyze its own codebase
    2. Identify improvement opportunities
    3. Predict success using Learning Layer
    4. Execute high-probability improvements
    5. Learn from outcomes
    6. Repeat until max_iterations reached
    
    Args:
        request: Session configuration
        
    Returns:
        Session details
    """
    try:
        logger.info(f"Starting autonomous session in {request.mode} mode")
        
        session = await agent.start_autonomous_session(
            mode=request.mode,
            max_iterations=request.max_iterations,
            session_id=request.session_id
        )
        
        return StartSessionResponse(
            session_id=session.session_id,
            mode=session.mode.value,
            max_iterations=session.max_iterations,
            status=session.status,
            started_at=session.started_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to start autonomous session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[SessionStatusResponse])
async def list_sessions(
    current_user = Depends(get_current_user_optional),
    agent: AutonomousAgentService = Depends(get_autonomous_agent)
):
    """
    List all autonomous sessions.
    
    Returns:
        List of session statuses
    """
    try:
        sessions = agent.list_sessions()
        return [SessionStatusResponse(**s) for s in sessions]
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    current_user = Depends(get_current_user_optional),
    agent: AutonomousAgentService = Depends(get_autonomous_agent)
):
    """
    Get status of a specific autonomous session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session status details
    """
    try:
        status = agent.get_session_status(session_id)
        
        if not status:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return SessionStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/stop")
async def stop_session(
    session_id: str,
    current_user = Depends(get_current_user_optional),  # DEV_MODE compatible
    agent: AutonomousAgentService = Depends(get_autonomous_agent)
):
    """
    Stop a running autonomous session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
    """
    try:
        stopped = await agent.stop_session(session_id)
        
        if not stopped:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found or already stopped"
            )
        
        return {
            "status": "success",
            "message": f"Session {session_id} stopped",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def autonomous_health(agent: AutonomousAgentService = Depends(get_autonomous_agent)):
    """
    Check autonomous agent health.
    
    Returns:
        Health status including active sessions count
    """
    try:
        sessions = agent.list_sessions()
        active = sum(1 for s in sessions if s["status"] == "running")
        
        return {
            "status": "healthy",
            "active_sessions": active,
            "total_sessions": len(sessions),
            "learning_service": "connected"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }


@router.get("/modes")
async def list_agent_modes():
    """
    List available agent operation modes.
    
    Returns:
        Available modes with descriptions
    """
    return {
        "modes": [
            {
                "name": "conservative",
                "threshold": 0.80,
                "description": "Only execute improvements with >80% predicted success. Safest option."
            },
            {
                "name": "balanced",
                "threshold": 0.60,
                "description": "Execute improvements with >60% predicted success. Recommended for production."
            },
            {
                "name": "aggressive",
                "threshold": 0.40,
                "description": "Execute improvements with >40% predicted success. More experimental."
            },
            {
                "name": "exploratory",
                "threshold": 0.0,
                "description": "Execute all improvements to gather data. Best for building knowledge base."
            }
        ]
    }


@router.get("/sessions/{session_id}/iterations", response_model=List[IterationResponse])
async def get_session_iterations(
    session_id: str,
    current_user = Depends(get_current_user_optional),
    agent: AutonomousAgentService = Depends(get_autonomous_agent)
):
    """
    Get detailed list of all iterations for a session.
    
    Returns iteration-by-iteration breakdown including:
    - Opportunity detected
    - Proposal generated
    - Council decision (if review council enabled)
    - Architect decision (if architect enabled)
    - Execution result
    - Success/failure status
    - Timestamp
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of detailed iteration information
    """
    try:
        iterations = agent.get_session_iterations(session_id)
        
        if iterations is None:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return [IterationResponse(**iteration) for iteration in iterations]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session iterations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/improvements", response_model=List[ImprovementResponse])
async def get_session_improvements(
    session_id: str,
    current_user = Depends(get_current_user_optional),
    agent: AutonomousAgentService = Depends(get_autonomous_agent)
):
    """
    Get detailed list of all improvements attempted in a session.
    
    Returns improvement-by-improvement breakdown including:
    - File path
    - Improvement type
    - Diff (code before/after)
    - Council review (Security/Performance/QA decisions)
    - Architect review
    - Applied (boolean)
    - Outcome details
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of detailed improvement information
    """
    try:
        improvements = agent.get_session_improvements(session_id)
        
        if improvements is None:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return [ImprovementResponse(**improvement) for improvement in improvements]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session improvements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=GlobalStatsResponse)
async def get_global_stats(
    current_user = Depends(get_current_user_optional),
    agent: AutonomousAgentService = Depends(get_autonomous_agent)
):
    """
    Get global statistics across all autonomous sessions.
    
    Returns aggregated metrics including:
    - Total sessions
    - Total improvements attempted/succeeded
    - Overall success rate
    - Success rate by improvement type
    - Success rate by agent mode
    - Average iterations per session
    
    Returns:
        Global statistics
    """
    try:
        stats = agent.get_global_stats()
        return GlobalStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get global stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
