"""
Autonomous Agent Service: Self-improving AI that learns from every action.

This service orchestrates the complete autonomous loop:
1. Introspect own codebase
2. Identify improvement opportunities
3. Consult Learning Layer for success prediction
4. Execute high-probability improvements
5. Log outcomes for continuous learning
6. Repeat indefinitely

Architecture:
- IntrospectionService: AST analysis, metrics, dependency graph
- LearningService: RAG-based prediction, success rate analytics
- SelfModificationEngine: Safe code generation and validation
- This service: Orchestration and decision-making
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from app.services.introspection import IntrospectionService
from app.services.learning import LearningService
from app.services.self_modification import SelfModificationEngine
from app.services.architect import ArchitectAgentService
from app.services.review_council import ReviewCouncilService
from app.models import ImprovementType, ImprovementJob, ImprovementJobStatus, ImprovementProposal, ArchitectDecision, CouncilDecision
from app.core.config import settings


class CancelToken:
    """
    Cooperative cancellation token for autonomous sessions.
    
    Allows graceful interruption of long-running operations by checking
    cancellation status at strategic points.
    """
    def __init__(self):
        self._cancelled = False
    
    def cancel(self):
        """Mark this token as cancelled."""
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if cancellation was requested."""
        return self._cancelled
    
    def check(self):
        """Raise exception if cancelled (for immediate exit)."""
        if self._cancelled:
            raise CancellationError("Operation cancelled by user")


class CancellationError(Exception):
    """Raised when an operation is cancelled."""
    pass


class AgentMode(str, Enum):
    """Agent operation modes."""
    CONSERVATIVE = "conservative"  # Only execute improvements with >80% predicted success
    BALANCED = "balanced"          # Execute improvements with >60% predicted success
    AGGRESSIVE = "aggressive"      # Execute improvements with >40% predicted success
    EXPLORATORY = "exploratory"    # Execute all improvements to gather data


@dataclass
class ImprovementOpportunity:
    """Potential improvement identified by introspection."""
    type: ImprovementType
    file_path: str
    severity: str
    message: str
    metadata: Dict[str, Any]
    predicted_success_rate: float = 0.0
    similar_outcomes_count: int = 0


@dataclass
class IterationDetail:
    """Detailed information about a single iteration."""
    iteration_number: int
    opportunity: Optional[Dict[str, Any]]  # ImprovementOpportunity serialized
    proposal: Optional[Dict[str, Any]]  # ImprovementProposal serialized
    council_decision: Optional[Dict[str, Any]]  # CouncilDecision serialized
    architect_decision: Optional[Dict[str, Any]]  # ArchitectDecision serialized
    execution_result: Optional[Dict[str, Any]]  # Result from _execute_improvement
    success: bool
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "iteration_number": self.iteration_number,
            "opportunity": self.opportunity,
            "proposal": self.proposal,
            "council_decision": self.council_decision,
            "architect_decision": self.architect_decision,
            "execution_result": self.execution_result,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AutonomousSession:
    """Active autonomous improvement session."""
    session_id: str
    started_at: datetime
    mode: AgentMode
    max_iterations: int
    current_iteration: int = 0
    improvements_attempted: int = 0
    improvements_succeeded: int = 0
    improvements_failed: int = 0
    status: str = "running"
    last_action: Optional[str] = None
    cancel_token: CancelToken = None  # type: ignore
    
    def __post_init__(self):
        self.errors: List[str] = []
        self.iterations: List[IterationDetail] = []
        if self.cancel_token is None:
            self.cancel_token = CancelToken()


class AutonomousAgentService:
    """
    Autonomous self-improving agent with learning capabilities.
    
    This is the core orchestrator that makes the agent truly autonomous:
    - Continuously analyzes its own code
    - Learns from past successes and failures
    - Makes intelligent decisions about which improvements to pursue
    - Executes improvements safely
    - Updates its knowledge base automatically
    """
    
    def __init__(
        self,
        learning_service: LearningService,
        introspection_service: Optional[IntrospectionService] = None,
        modification_engine: Optional[SelfModificationEngine] = None,
        architect_service: Optional[ArchitectAgentService] = None,
        review_council_service: Optional[ReviewCouncilService] = None
    ):
        self.learning = learning_service
        self.introspection = introspection_service or IntrospectionService()
        self.modification = modification_engine or SelfModificationEngine()
        self.architect = architect_service or ArchitectAgentService(learning_service=learning_service)
        self.review_council = review_council_service or ReviewCouncilService()
        
        self.active_sessions: Dict[str, AutonomousSession] = {}
        
        architect_status = "enabled" if settings.autonomous_agent_architect_enabled else "disabled"
        council_status = "enabled" if settings.autonomous_agent_review_council_enabled else "disabled"
        logger.info(f"Autonomous Agent Service initialized (architect: {architect_status}, council: {council_status})")
    
    async def start_autonomous_session(
        self,
        mode: AgentMode = AgentMode.BALANCED,
        max_iterations: int = 10,
        session_id: Optional[str] = None
    ) -> AutonomousSession:
        """
        Start an autonomous improvement session.
        
        Args:
            mode: Agent operation mode (affects risk tolerance)
            max_iterations: Maximum number of improvement cycles
            session_id: Optional custom session ID
        
        Returns:
            AutonomousSession object with session details
        """
        import uuid
        
        if session_id is None:
            session_id = f"auto_{uuid.uuid4().hex[:12]}"
        
        session = AutonomousSession(
            session_id=session_id,
            started_at=datetime.now(),
            mode=mode,
            max_iterations=max_iterations
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Started autonomous session {session_id} in {mode} mode")
        
        # Start autonomous loop in background
        asyncio.create_task(self._autonomous_loop(session))
        
        return session
    
    async def start_external_goal_session(
        self,
        goal: str,
        mode: str = "balanced",
        tenant_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
        origin: str = "chat"
    ) -> Dict[str, Any]:
        """
        Start an autonomous session with an external goal from chat or other sources.
        
        This method creates a session specifically for external goals (e.g., from chat),
        storing the goal and origin for tracking and monitoring.
        
        Args:
            goal: The user's goal in natural language
            mode: Agent operation mode (conservative, balanced, aggressive, exploratory)
            tenant_id: Tenant identifier for multi-tenancy
            metadata: Additional metadata to store with the session
            origin: Origin of the request (e.g., "chat", "api", "cli")
            
        Returns:
            Dictionary with session details:
            {
                "session_id": str,
                "mode": str,
                "status": str,
                "started_at": str,
                "goal": str,
                "origin": str
            }
        """
        import uuid
        
        # Convert mode string to AgentMode enum
        mode_mapping = {
            "conservative": AgentMode.CONSERVATIVE,
            "balanced": AgentMode.BALANCED,
            "aggressive": AgentMode.AGGRESSIVE,
            "exploratory": AgentMode.EXPLORATORY
        }
        
        agent_mode = mode_mapping.get(mode.lower(), AgentMode.BALANCED)
        
        # Generate session ID
        session_id = f"chat_{uuid.uuid4().hex[:12]}"
        
        # Create session
        session = AutonomousSession(
            session_id=session_id,
            started_at=datetime.now(),
            mode=agent_mode,
            max_iterations=10  # Default for chat-initiated sessions
        )
        
        # Store session metadata (goal, origin, etc.)
        if not hasattr(session, 'metadata'):
            session.metadata = {}
        
        session.metadata = {
            "goal": goal,
            "origin": origin,
            "tenant_id": tenant_id,
            **(metadata or {})
        }
        
        # Add to active sessions
        self.active_sessions[session_id] = session
        
        logger.info(f"Started external goal session {session_id} from {origin}: {goal[:80]}")
        
        # Start autonomous loop in background
        asyncio.create_task(self._autonomous_loop(session))
        
        return {
            "session_id": session.session_id,
            "mode": session.mode.value,
            "status": session.status,
            "started_at": session.started_at.isoformat(),
            "goal": goal,
            "origin": origin
        }
    
    async def _autonomous_loop(self, session: AutonomousSession):
        """
        Main autonomous loop: analyze → predict → execute → learn → repeat.
        
        This is where the magic happens - the agent continuously improves itself.
        """
        logger.info(f"Starting autonomous loop for session {session.session_id}")
        
        try:
            while session.current_iteration < session.max_iterations and session.status == "running":
                # Check for cancellation at start of each iteration
                try:
                    session.cancel_token.check()
                except CancellationError:
                    logger.info(f"Session {session.session_id} cancelled via token")
                    session.status = "stopped"
                    session.last_action = "cancelled"
                    break
                
                session.current_iteration += 1
                logger.info(f"Iteration {session.current_iteration}/{session.max_iterations}")
                
                # PHASE 1: Introspect - analyze own codebase
                session.last_action = "introspecting"
                opportunities = await self._identify_opportunities(session.cancel_token)
                
                if not opportunities:
                    logger.info("No improvement opportunities found")
                    session.last_action = "no_opportunities"
                    # Sleep in small chunks to allow responsive cancellation
                    for _ in range(10):  # 10 x 0.5s = 5s total
                        try:
                            session.cancel_token.check()
                        except CancellationError:
                            logger.info(f"Session cancelled (no opportunities)")
                            session.status = "stopped"
                            break
                        await asyncio.sleep(0.5)
                    if session.status != "running":
                        break
                    continue
                
                # PHASE 2: Predict - use Learning Layer to estimate success
                session.last_action = "predicting"
                ranked_opportunities = await self._rank_by_predicted_success(
                    opportunities,
                    mode=session.mode,
                    cancel_token=session.cancel_token
                )
                
                if not ranked_opportunities:
                    logger.info("No opportunities meet success threshold")
                    session.last_action = "threshold_not_met"
                    # Sleep in small chunks to allow responsive cancellation
                    for _ in range(10):  # 10 x 0.5s = 5s total
                        try:
                            session.cancel_token.check()
                        except CancellationError:
                            logger.info(f"Session cancelled (threshold not met)")
                            session.status = "stopped"
                            break
                        await asyncio.sleep(0.5)
                    if session.status != "running":
                        break
                    continue
                
                # PHASE 3: Execute - apply the best improvement
                # Check for cancellation before expensive execution
                try:
                    session.cancel_token.check()
                except CancellationError:
                    logger.info(f"Session cancelled before execution")
                    session.status = "stopped"
                    break
                
                best_opportunity = ranked_opportunities[0]
                session.last_action = f"executing_{best_opportunity.type}"
                
                # Track iteration details
                iteration_detail = IterationDetail(
                    iteration_number=session.current_iteration,
                    opportunity=self._serialize_opportunity(best_opportunity),
                    proposal=None,
                    council_decision=None,
                    architect_decision=None,
                    execution_result=None,
                    success=False,
                    timestamp=datetime.now()
                )
                
                result = await self._execute_improvement(best_opportunity, session)
                
                # Update iteration detail with results
                iteration_detail.execution_result = result
                iteration_detail.success = result["success"]
                iteration_detail.council_decision = result.get("council_decision")
                iteration_detail.architect_decision = result.get("architect_decision")
                
                # Store iteration in session
                session.iterations.append(iteration_detail)
                
                # PHASE 4: Learn - log outcome for future decisions
                session.last_action = "learning"
                await self._log_outcome(best_opportunity, result)
                
                # Update session stats
                session.improvements_attempted += 1
                if result["success"]:
                    session.improvements_succeeded += 1
                    logger.info(f"✅ Improvement succeeded: {best_opportunity.message[:60]}")
                else:
                    session.improvements_failed += 1
                    session.errors.append(result.get("error", "Unknown error"))
                    logger.warning(f"❌ Improvement failed: {result.get('error', 'Unknown')[:60]}")
                
                # Brief pause between iterations (in chunks for responsive cancellation)
                for _ in range(4):  # 4 x 0.5s = 2s total
                    try:
                        session.cancel_token.check()
                    except CancellationError:
                        logger.info(f"Session {session.session_id} cancelled during iteration pause")
                        session.status = "stopped"
                        break
                    await asyncio.sleep(0.5)
                if session.status != "running":
                    break
            
            # Only mark as completed if not manually stopped
            if session.status == "running":
                session.status = "completed"
                session.last_action = "session_complete"
                logger.info(f"Autonomous session {session.session_id} completed")
                logger.info(f"Results: {session.improvements_succeeded}/{session.improvements_attempted} succeeded")
            
        except CancellationError:
            # Handle cancellation gracefully
            session.status = "stopped"
            session.last_action = "cancelled"
            logger.info(f"Autonomous session {session.session_id} cancelled cooperatively")
        except Exception as e:
            session.status = "failed"
            session.last_action = f"error: {str(e)[:100]}"
            session.errors.append(str(e))
            logger.error(f"Autonomous loop failed: {e}")
    
    async def _identify_opportunities(self, cancel_token: Optional[CancelToken] = None) -> List[ImprovementOpportunity]:
        """
        Scan codebase and identify improvement opportunities.
        
        Args:
            cancel_token: Optional cancellation token for cooperative cancellation
        
        Returns:
            List of potential improvements
        """
        # Map introspection types to ImprovementType enum
        type_mapping = {
            "high_complexity": ImprovementType.REFACTOR_COMPLEXITY,
            "large_file": ImprovementType.SPLIT_LARGE_FILE,
            "high_coupling": ImprovementType.REDUCE_COUPLING,
            "missing_docs": ImprovementType.ADD_DOCUMENTATION,
            "complex_imports": ImprovementType.OPTIMIZE_IMPORTS,
            "code_smell": ImprovementType.FIX_CODE_SMELL,
            "missing_tests": ImprovementType.ADD_TESTS,
        }
        
        try:
            # Offload heavy introspection to thread pool to avoid blocking event loop
            structure = await asyncio.to_thread(self.introspection.scan_repository)
            
            # Check for cancellation after scanning
            if cancel_token:
                cancel_token.check()
            
            raw_opportunities = await asyncio.to_thread(
                self.introspection.find_improvement_opportunities, structure
            )
            
            # Check for cancellation after finding opportunities
            if cancel_token:
                cancel_token.check()
            
            # Convert to our enhanced format
            opportunities = []
            for opp in raw_opportunities[:20]:  # Limit to top 20
                opp_type = opp["type"]
                
                # Map to enum or skip unknown types
                if opp_type not in type_mapping:
                    logger.warning(f"Unknown opportunity type: {opp_type}, skipping")
                    continue
                
                opportunities.append(ImprovementOpportunity(
                    type=type_mapping[opp_type],
                    file_path=opp["file"],
                    severity=opp["severity"],
                    message=opp["message"],
                    metadata=opp.get("metadata", {})
                ))
            
            logger.info(f"Identified {len(opportunities)} improvement opportunities")
            return opportunities
            
        except CancellationError:
            logger.info("Opportunity identification cancelled")
            return []
        except Exception as e:
            logger.error(f"Failed to identify opportunities: {e}")
            return []
    
    async def _rank_by_predicted_success(
        self,
        opportunities: List[ImprovementOpportunity],
        mode: AgentMode,
        cancel_token: Optional[CancelToken] = None
    ) -> List[ImprovementOpportunity]:
        """
        Rank opportunities by predicted success rate using Learning Layer.
        
        Args:
            opportunities: List of potential improvements
            mode: Agent mode (affects filtering threshold)
            cancel_token: Optional cancellation token for cooperative cancellation
        
        Returns:
            Filtered and sorted list of opportunities
        """
        # Define success thresholds by mode
        thresholds = {
            AgentMode.CONSERVATIVE: 0.80,
            AgentMode.BALANCED: 0.60,
            AgentMode.AGGRESSIVE: 0.40,
            AgentMode.EXPLORATORY: 0.0
        }
        
        threshold = thresholds[mode]
        
        # Query Learning Layer for each opportunity
        for opp in opportunities:
            # Check for cancellation in prediction loop
            if cancel_token:
                cancel_token.check()
            
            try:
                # Find similar past outcomes
                similar = await self.learning.get_similar_outcomes(
                    improvement_type=opp.type.value,
                    target_file=opp.file_path,
                    limit=10
                )
                
                if similar:
                    # Calculate predicted success rate from similar outcomes
                    successes = sum(1 for s in similar if s.get("success", False))
                    opp.predicted_success_rate = successes / len(similar)
                    opp.similar_outcomes_count = len(similar)
                else:
                    # No historical data - use type-level success rate
                    # Offload to thread to avoid blocking
                    type_stats = await asyncio.to_thread(
                        self.learning.get_success_rate, opp.type.value
                    )
                    opp.predicted_success_rate = type_stats.get("success_rate", 0.5)
                    opp.similar_outcomes_count = 0
                
            except CancellationError:
                logger.info("Prediction cancelled during learning query")
                raise
            except Exception as e:
                logger.warning(f"Failed to predict success for {opp.file_path}: {e}")
                opp.predicted_success_rate = 0.5  # Default to neutral
        
        # Filter by threshold and sort by predicted success
        filtered = [
            opp for opp in opportunities 
            if opp.predicted_success_rate >= threshold
        ]
        
        sorted_opps = sorted(
            filtered,
            key=lambda x: (x.predicted_success_rate, x.severity == "high"),
            reverse=True
        )
        
        logger.info(
            f"Ranked {len(sorted_opps)} opportunities "
            f"(threshold: {threshold:.0%}, filtered from {len(opportunities)})"
        )
        
        return sorted_opps
    
    async def _generate_proposal_preview(
        self,
        opportunity: ImprovementOpportunity,
        session: AutonomousSession
    ) -> Optional[ImprovementProposal]:
        """
        Generate a proposal preview WITHOUT applying changes.
        
        This allows the architect to review the proposed changes before execution.
        
        Args:
            opportunity: The improvement opportunity
            session: The current autonomous session
            
        Returns:
            ImprovementProposal with diff preview, or None if generation failed
        """
        try:
            from pathlib import Path
            import difflib
            
            # Create temporary job for generation
            job = ImprovementJob(
                job_id=f"preview_{datetime.now().timestamp():.0f}",
                improvement_type=opportunity.type,
                target_file=opportunity.file_path,
                title=opportunity.message[:100],
                description=opportunity.message,
                rationale=f"Predicted success: {opportunity.predicted_success_rate:.0%}",
                status=ImprovementJobStatus.PENDING,
                priority=10 if opportunity.severity == "high" else 5,
                success_criteria={},
                before_metrics=opportunity.metadata,
                after_metrics={},
                meta={}
            )
            
            # Read original code
            target_path = Path(self.modification.repo_root) / opportunity.file_path
            if not target_path.exists():
                logger.error(f"Target file not found: {opportunity.file_path}")
                return None
            
            original_code = await asyncio.to_thread(target_path.read_text)
            
            # Generate improved code WITHOUT applying it
            improved_code = await self.modification._generate_improvement(
                job=job,
                original_code=original_code
            )
            
            if not improved_code:
                logger.error("Failed to generate improved code for proposal")
                return None
            
            # Generate diff
            diff_lines = difflib.unified_diff(
                original_code.splitlines(keepends=True),
                improved_code.splitlines(keepends=True),
                fromfile=f"a/{opportunity.file_path}",
                tofile=f"b/{opportunity.file_path}",
                lineterm=""
            )
            diff = "".join(diff_lines)
            
            # Build proposal
            proposal = ImprovementProposal(
                session_id=session.session_id,
                iteration=session.current_iteration,
                files=[opportunity.file_path],
                diff=diff,
                summary=opportunity.message[:200],
                reason=f"{opportunity.type.value}: {opportunity.message}",
                before_metrics=opportunity.metadata,
                predicted_success=opportunity.predicted_success_rate
            )
            
            logger.info(f"Generated proposal preview for {opportunity.file_path}")
            return proposal
            
        except Exception as e:
            logger.error(f"Failed to generate proposal preview: {e}")
            return None
    
    async def _execute_improvement(
        self,
        opportunity: ImprovementOpportunity,
        session: AutonomousSession
    ) -> Dict[str, Any]:
        """
        Execute a single improvement safely, with optional architect review.
        
        Args:
            opportunity: The improvement to execute
            session: The current autonomous session
        
        Returns:
            Result dict with success, metrics, error, architect_decision (if any)
        """
        try:
            # Check for cancellation before starting expensive execution
            session.cancel_token.check()
            
            architect_decision = None
            council_decision = None
            
            # REVIEW COUNCIL + ARCHITECT REVIEW FLOW (if enabled)
            if settings.autonomous_agent_architect_enabled or settings.autonomous_agent_review_council_enabled:
                logger.info("Review system enabled - generating proposal preview")
                
                max_revisions = 2
                revision_count = 0
                
                while revision_count <= max_revisions:
                    # Generate proposal preview
                    proposal = await self._generate_proposal_preview(opportunity, session)
                    
                    if not proposal:
                        return {
                            "success": False,
                            "error": "Failed to generate proposal preview",
                            "architect_decision": None,
                            "council_decision": None
                        }
                    
                    # PHASE 1: Review Council (if enabled)
                    if settings.autonomous_agent_review_council_enabled:
                        logger.info("🔍 Review Council enabled - executing multi-expert review")
                        session.last_action = "council_reviewing"
                        
                        # Council reviews proposal and provides expert analysis
                        # Council runs BEFORE Architect, so no architect_decision yet
                        council_decision = await self.review_council.review_with_council(
                            proposal=proposal
                        )
                        
                        logger.info(
                            f"Council decision: {council_decision.final_decision} "
                            f"(risk: {council_decision.overall_risk_level}, "
                            f"confidence: {council_decision.overall_confidence:.2f})"
                        )
                        
                        # If council strongly rejects (all reviewers agree), skip architect
                        if council_decision.final_decision == "reject" and council_decision.overall_confidence > 0.8:
                            logger.warning(f"❌ Council rejected with high confidence: {council_decision.summary}")
                            return {
                                "success": False,
                                "error": f"Rejected by Review Council: {council_decision.summary}",
                                "council_decision": {
                                    "decision": council_decision.final_decision,
                                    "risk_level": council_decision.overall_risk_level,
                                    "confidence": council_decision.overall_confidence,
                                    "summary": council_decision.summary
                                },
                                "architect_decision": None
                            }
                    
                    # PHASE 2: Architect review (if enabled)
                    if settings.autonomous_agent_architect_enabled:
                        session.last_action = "architect_reviewing"
                        # Pass council decision to architect for informed decision-making
                        architect_decision = await self.architect.review_proposal(
                            proposal=proposal,
                            council_decision=council_decision
                        )
                    
                    # Only log architect decision if architect is enabled
                    if settings.autonomous_agent_architect_enabled and architect_decision:
                        logger.info(
                            f"Architect decision: {architect_decision.decision} "
                            f"(risk: {architect_decision.risk_level}, "
                            f"confidence: {architect_decision.confidence:.2f})"
                        )
                    
                    # Handle architect decision (if architect is enabled)
                    if settings.autonomous_agent_architect_enabled and architect_decision:
                        if architect_decision.decision == "approve":
                            logger.info("✅ Architect approved")
                            break
                        
                        elif architect_decision.decision == "reject":
                            logger.warning(f"❌ Architect rejected: {architect_decision.comments}")
                            return {
                                "success": False,
                                "error": f"Rejected by architect: {architect_decision.comments}",
                                "architect_decision": {
                                    "decision": architect_decision.decision,
                                    "risk_level": architect_decision.risk_level,
                                    "confidence": architect_decision.confidence,
                                    "comments": architect_decision.comments
                                },
                                "council_decision": {
                                    "decision": council_decision.final_decision,
                                    "risk_level": council_decision.overall_risk_level,
                                    "confidence": council_decision.overall_confidence,
                                    "summary": council_decision.summary
                                } if council_decision else None
                            }
                        
                        elif architect_decision.decision == "revise":
                            revision_count += 1
                            if revision_count > max_revisions:
                                logger.warning(
                                    f"⚠️ Max revisions ({max_revisions}) reached - rejecting improvement"
                                )
                                return {
                                    "success": False,
                                    "error": f"Max revisions reached. Last feedback: {architect_decision.comments}",
                                    "architect_decision": {
                                        "decision": "reject_after_revisions",
                                        "risk_level": architect_decision.risk_level,
                                        "confidence": architect_decision.confidence,
                                        "comments": architect_decision.comments
                                    },
                                    "council_decision": {
                                        "decision": council_decision.final_decision,
                                        "risk_level": council_decision.overall_risk_level,
                                        "confidence": council_decision.overall_confidence,
                                        "summary": council_decision.summary
                                    } if council_decision else None
                                }
                            
                            logger.info(
                                f"🔄 Architect requested revision ({revision_count}/{max_revisions}): "
                                f"{architect_decision.comments}"
                            )
                            
                            # Update opportunity with feedback for regeneration
                            opportunity.message = (
                                f"{opportunity.message}\n\n"
                                f"ARCHITECT FEEDBACK (revision {revision_count}):\n"
                                f"{architect_decision.comments}\n"
                                f"Required changes: {', '.join(architect_decision.required_changes)}"
                            )
                            
                            # Loop will regenerate proposal with updated opportunity
                            continue
                    else:
                        # No architect enabled, or only council enabled - if council approved, proceed
                        if council_decision and council_decision.final_decision == "approve":
                            logger.info("✅ Council approved (architect disabled)")
                            break
                        elif not council_decision:
                            # Neither enabled, shouldn't happen but break anyway
                            break
            
            # EXECUTE IMPROVEMENT (architect disabled or approved)
            session.last_action = f"executing_{opportunity.type}"
            
            # Create improvement job
            job = ImprovementJob(
                job_id=f"auto_{datetime.now().timestamp():.0f}",
                improvement_type=opportunity.type,
                target_file=opportunity.file_path,
                title=opportunity.message[:100],
                description=opportunity.message,
                rationale=f"Predicted success: {opportunity.predicted_success_rate:.0%}",
                status=ImprovementJobStatus.APPROVED,
                priority=10 if opportunity.severity == "high" else 5,
                success_criteria={},
                before_metrics=opportunity.metadata,
                after_metrics={},
                meta={}
            )
            
            # Execute using modification engine
            result = await self.modification.execute_improvement(job)
            
            # Check for cancellation after execution
            session.cancel_token.check()
            
            return {
                "success": result["status"] == "success",
                "job_id": job.job_id,
                "metrics_before": job.before_metrics,
                "metrics_after": result.get("after_metrics", {}),
                "error": result.get("error"),
                "architect_decision": {
                    "decision": architect_decision.decision,
                    "risk_level": architect_decision.risk_level,
                    "confidence": architect_decision.confidence,
                    "comments": architect_decision.comments
                } if architect_decision else None,
                "council_decision": {
                    "decision": council_decision.final_decision,
                    "risk_level": council_decision.overall_risk_level,
                    "confidence": council_decision.overall_confidence,
                    "summary": council_decision.summary,
                    "voting_breakdown": council_decision.voting_breakdown
                } if council_decision else None
            }
            
        except CancellationError:
            logger.info("Improvement execution cancelled - propagating")
            # Re-raise to let outer loop handle cancellation properly
            raise
        except Exception as e:
            logger.error(f"Failed to execute improvement: {e}")
            return {
                "success": False,
                "error": str(e),
                "architect_decision": None
            }
    
    async def _log_outcome(
        self,
        opportunity: ImprovementOpportunity,
        result: Dict[str, Any]
    ):
        """
        Log improvement outcome to Learning Layer.
        
        This is critical - it's how the agent learns from experience.
        Includes review decisions metadata when available:
        - metadata['architect_review']: Architect decision fields
        - metadata['council_review']: Full council decision (3 expert reviewers)
        """
        try:
            # Build metadata with review decisions
            metadata = {}
            
            # Include Architect decision if available
            if result.get("architect_decision"):
                architect_decision = result["architect_decision"]
                metadata["architect_decision"] = architect_decision["decision"]
                metadata["architect_risk_level"] = architect_decision["risk_level"]
                metadata["architect_confidence"] = architect_decision["confidence"]
                metadata["architect_comments"] = architect_decision["comments"]
            
            # Include Review Council decision if available
            # This preserves complete multi-expert analysis for learning
            if result.get("council_decision"):
                metadata["council_review"] = result["council_decision"]
            
            # Merge with any existing metadata
            if result.get("metrics_before"):
                metadata.update(result["metrics_before"])
            
            await self.learning.log_outcome_from_fields(
                job_id=result.get("job_id", "unknown"),
                success=result["success"],
                improvement_type=opportunity.type.value,
                target_file=opportunity.file_path,
                metrics_before=metadata,
                metrics_after=result.get("metrics_after"),
                error_message=result.get("error"),
                code_changes=opportunity.message
            )
            
            # Log with review context
            review_info = []
            if result.get("council_decision"):
                review_info.append(f"council: {result['council_decision']['decision']}")
            if result.get("architect_decision"):
                review_info.append(f"architect: {result['architect_decision']['decision']}")
            
            review_str = f" ({', '.join(review_info)})" if review_info else ""
            logger.info(f"Logged outcome for {opportunity.file_path}{review_str}")
            
        except Exception as e:
            logger.error(f"Failed to log outcome: {e}")
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an autonomous session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        success_rate = 0.0
        if session.improvements_attempted > 0:
            success_rate = session.improvements_succeeded / session.improvements_attempted
        
        # Build current iteration details if session is running
        current_iteration_details = None
        if session.status == "running" and session.current_iteration > 0:
            # Get the last (current) iteration if it exists
            current_iter = None
            if session.iterations and len(session.iterations) > 0:
                current_iter = session.iterations[-1]
            
            # Determine phase from last_action
            phase = "unknown"
            if session.last_action:
                if "introspect" in session.last_action:
                    phase = "introspecting"
                elif "predict" in session.last_action:
                    phase = "predicting"
                elif "council_reviewing" in session.last_action:
                    phase = "council_review"
                elif "architect_reviewing" in session.last_action:
                    phase = "architect_review"
                elif "executing" in session.last_action:
                    phase = "executing"
                elif "learning" in session.last_action:
                    phase = "learning"
            
            current_iteration_details = {
                "iteration_number": session.current_iteration,
                "phase": phase,
                "opportunity": current_iter.opportunity if current_iter else None,
                "status": session.status
            }
        
        return {
            "session_id": session.session_id,
            "status": session.status,
            "mode": session.mode,
            "iteration": f"{session.current_iteration}/{session.max_iterations}",
            "improvements_attempted": session.improvements_attempted,
            "improvements_succeeded": session.improvements_succeeded,
            "improvements_failed": session.improvements_failed,
            "success_rate": success_rate,
            "last_action": session.last_action,
            "started_at": session.started_at.isoformat(),
            "errors": session.errors[-5:],  # Last 5 errors
            "current_iteration_details": current_iteration_details
        }
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all autonomous sessions."""
        sessions = []
        for session_id in self.active_sessions.keys():
            status = self.get_session_status(session_id)
            if status:
                sessions.append(status)
        return sessions
    
    async def stop_session(self, session_id: str) -> bool:
        """
        Stop an active autonomous session using cooperative cancellation.
        
        Activates the session's cancel token, causing the autonomous loop
        to exit at the next cancellation checkpoint (typically < 2 seconds).
        """
        session = self.active_sessions.get(session_id)
        if session and session.status == "running":
            # Activate cancel token for cooperative cancellation
            session.cancel_token.cancel()
            session.status = "stopping"
            session.last_action = "cancellation_requested"
            logger.info(f"Requested cancellation of autonomous session {session_id}")
            return True
        return False
    
    def _serialize_opportunity(self, opportunity: ImprovementOpportunity) -> Dict[str, Any]:
        """Serialize ImprovementOpportunity to dictionary."""
        return {
            "type": opportunity.type.value,
            "file_path": opportunity.file_path,
            "severity": opportunity.severity,
            "message": opportunity.message,
            "metadata": opportunity.metadata,
            "predicted_success_rate": opportunity.predicted_success_rate,
            "similar_outcomes_count": opportunity.similar_outcomes_count
        }
    
    def get_session_iterations(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get all iterations for a session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return [iteration.to_dict() for iteration in session.iterations]
    
    def get_session_improvements(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get all improvements attempted in a session with detailed review info."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        improvements = []
        for iteration in session.iterations:
            if iteration.opportunity and iteration.execution_result:
                improvement = {
                    "file_path": iteration.opportunity.get("file_path"),
                    "improvement_type": iteration.opportunity.get("type"),
                    "diff": iteration.execution_result.get("diff"),
                    "council_review": iteration.council_decision,
                    "architect_review": iteration.architect_decision,
                    "applied": iteration.success,
                    "outcome": {
                        "success": iteration.success,
                        "error": iteration.execution_result.get("error"),
                        "metrics_before": iteration.execution_result.get("metrics_before"),
                        "metrics_after": iteration.execution_result.get("metrics_after")
                    },
                    "timestamp": iteration.timestamp.isoformat()
                }
                improvements.append(improvement)
        
        return improvements
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics across all sessions."""
        total_sessions = len(self.active_sessions)
        total_improvements_attempted = 0
        total_improvements_succeeded = 0
        improvements_by_type: Dict[str, Dict[str, int]] = {}
        improvements_by_mode: Dict[str, Dict[str, int]] = {}
        total_iterations = 0
        
        for session in self.active_sessions.values():
            total_improvements_attempted += session.improvements_attempted
            total_improvements_succeeded += session.improvements_succeeded
            total_iterations += session.current_iteration
            
            # Track by mode
            mode_key = session.mode.value
            if mode_key not in improvements_by_mode:
                improvements_by_mode[mode_key] = {"attempted": 0, "succeeded": 0}
            improvements_by_mode[mode_key]["attempted"] += session.improvements_attempted
            improvements_by_mode[mode_key]["succeeded"] += session.improvements_succeeded
            
            # Track by improvement type
            for iteration in session.iterations:
                if iteration.opportunity:
                    imp_type = iteration.opportunity.get("type", "unknown")
                    if imp_type not in improvements_by_type:
                        improvements_by_type[imp_type] = {"attempted": 0, "succeeded": 0}
                    improvements_by_type[imp_type]["attempted"] += 1
                    if iteration.success:
                        improvements_by_type[imp_type]["succeeded"] += 1
        
        # Calculate success rates
        overall_success_rate = 0.0
        if total_improvements_attempted > 0:
            overall_success_rate = total_improvements_succeeded / total_improvements_attempted
        
        success_rate_by_type = {}
        for imp_type, stats in improvements_by_type.items():
            if stats["attempted"] > 0:
                success_rate_by_type[imp_type] = stats["succeeded"] / stats["attempted"]
            else:
                success_rate_by_type[imp_type] = 0.0
        
        success_rate_by_mode = {}
        for mode, stats in improvements_by_mode.items():
            if stats["attempted"] > 0:
                success_rate_by_mode[mode] = stats["succeeded"] / stats["attempted"]
            else:
                success_rate_by_mode[mode] = 0.0
        
        avg_iterations_per_session = 0.0
        if total_sessions > 0:
            avg_iterations_per_session = total_iterations / total_sessions
        
        return {
            "total_sessions": total_sessions,
            "total_improvements_attempted": total_improvements_attempted,
            "total_improvements_succeeded": total_improvements_succeeded,
            "overall_success_rate": overall_success_rate,
            "success_rate_by_improvement_type": success_rate_by_type,
            "success_rate_by_mode": success_rate_by_mode,
            "avg_iterations_per_session": avg_iterations_per_session
        }
