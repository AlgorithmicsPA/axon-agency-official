"""
Review Council Service: Multi-expert review orchestrator.

This service coordinates three specialized reviewers (Security, Performance, QA)
to provide comprehensive code review through parallel evaluation and voting.
"""

import asyncio
from typing import Optional, Literal, cast
from loguru import logger

from app.models import ImprovementProposal, ReviewerDecision, CouncilDecision, ArchitectDecision
from app.services.security_reviewer import SecurityReviewerService
from app.services.performance_reviewer import PerformanceReviewerService
from app.services.qa_reviewer import QAReviewerService


class ReviewCouncilService:
    """
    Orchestrates multi-expert code review through parallel reviewer execution.
    
    The Review Council coordinates:
    - SecurityReviewerService: Identifies security vulnerabilities
    - PerformanceReviewerService: Detects performance bottlenecks
    - QAReviewerService: Ensures quality, tests, and maintainability
    
    Decision aggregation logic:
    - 2+ reject → final reject
    - 1+ revise and 0 reject → final revise
    - All approve → final approve
    """
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize Review Council with all reviewers."""
        self.config = config or {}
        
        # Initialize specialized reviewers
        self.security_reviewer = SecurityReviewerService(config)
        self.performance_reviewer = PerformanceReviewerService(config)
        self.qa_reviewer = QAReviewerService(config)
        
        logger.info("Review Council Service initialized with 3 reviewers")
    
    async def review_with_council(
        self,
        proposal: ImprovementProposal
    ) -> CouncilDecision:
        """
        Execute multi-expert review through parallel reviewer coordination.
        
        The Council runs BEFORE the Architect to provide expert analysis that
        the Architect can use in making the final decision.
        
        Args:
            proposal: The improvement proposal to review
            
        Returns:
            CouncilDecision with aggregated results and voting breakdown
        """
        logger.info(f"Starting Review Council for session {proposal.session_id}")
        
        # PHASE 1: Execute all reviewers in parallel
        security_decision, performance_decision, qa_decision = await self._execute_parallel_reviews(proposal)
        
        # PHASE 2: Aggregate decisions through voting
        final_decision, voting_breakdown = self._aggregate_decisions(
            security_decision,
            performance_decision,
            qa_decision
        )
        
        # PHASE 3: Calculate overall metrics
        overall_risk_level = self._calculate_overall_risk(
            security_decision,
            performance_decision,
            qa_decision
        )
        
        overall_confidence = self._calculate_overall_confidence(
            security_decision,
            performance_decision,
            qa_decision
        )
        
        # PHASE 4: Generate summary
        summary = self._generate_summary(
            final_decision,
            security_decision,
            performance_decision,
            qa_decision,
            voting_breakdown
        )
        
        # Build final council decision (with explicit type casting for Literals)
        # Note: architect_decision will be added later by AutonomousAgent after Architect reviews
        council_decision = CouncilDecision(
            final_decision=cast(Literal["approve", "revise", "reject"], final_decision),
            overall_risk_level=cast(Literal["low", "medium", "high"], overall_risk_level),
            overall_confidence=overall_confidence,
            summary=summary,
            architect_decision=None,  # Council runs BEFORE Architect
            security_decision=security_decision,
            performance_decision=performance_decision,
            qa_decision=qa_decision,
            voting_breakdown=voting_breakdown
        )
        
        logger.info(
            f"Council final decision: {final_decision} "
            f"(risk: {overall_risk_level}, confidence: {overall_confidence:.2f})"
        )
        logger.info(f"Voting breakdown: {voting_breakdown}")
        
        return council_decision
    
    async def _execute_parallel_reviews(
        self,
        proposal: ImprovementProposal
    ) -> tuple[Optional[ReviewerDecision], Optional[ReviewerDecision], Optional[ReviewerDecision]]:
        """
        Execute all three reviewers in parallel using asyncio.gather.
        
        If a reviewer fails, it returns None and the council continues with the others.
        
        Args:
            proposal: The improvement proposal to review
            
        Returns:
            Tuple of (security_decision, performance_decision, qa_decision)
        """
        logger.info("Executing parallel reviews (Security, Performance, QA)")
        
        # Create review tasks
        tasks = [
            self._safe_review(self.security_reviewer, proposal, "Security"),
            self._safe_review(self.performance_reviewer, proposal, "Performance"),
            self._safe_review(self.qa_reviewer, proposal, "QA")
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        security_decision, performance_decision, qa_decision = results
        
        # Log which reviewers completed successfully
        completed = sum(1 for d in results if d is not None)
        logger.info(f"Parallel reviews completed: {completed}/3 reviewers succeeded")
        
        return security_decision, performance_decision, qa_decision
    
    async def _safe_review(
        self,
        reviewer,
        proposal: ImprovementProposal,
        reviewer_name: str
    ) -> Optional[ReviewerDecision]:
        """
        Execute a single reviewer with error handling.
        
        Args:
            reviewer: The reviewer service instance
            proposal: The improvement proposal
            reviewer_name: Name of the reviewer (for logging)
            
        Returns:
            ReviewerDecision or None if reviewer failed
        """
        try:
            decision = await reviewer.review_proposal(proposal)
            logger.info(f"{reviewer_name} reviewer: {decision.decision}")
            return decision
        except Exception as e:
            logger.error(f"{reviewer_name} reviewer failed: {e}")
            return None
    
    def _aggregate_decisions(
        self,
        security: Optional[ReviewerDecision],
        performance: Optional[ReviewerDecision],
        qa: Optional[ReviewerDecision]
    ) -> tuple[str, dict]:
        """
        Aggregate reviewer decisions through voting logic.
        
        Voting rules:
        - 2+ reject → reject
        - 1+ revise and 0 reject → revise
        - All approve → approve
        - If all reviewers failed → reject (safety)
        
        Args:
            security: Security reviewer decision
            performance: Performance reviewer decision
            qa: QA reviewer decision
            
        Returns:
            Tuple of (final_decision, voting_breakdown)
        """
        # Filter out None decisions
        decisions = [d for d in [security, performance, qa] if d is not None]
        
        # Safety: if all reviewers failed, reject
        if not decisions:
            logger.warning("All reviewers failed - defaulting to reject for safety")
            return "reject", {
                "approve": 0,
                "revise": 0,
                "reject": 0,
                "failed": 3,
                "reason": "All reviewers failed"
            }
        
        # Count votes
        votes = {
            "approve": sum(1 for d in decisions if d.decision == "approve"),
            "revise": sum(1 for d in decisions if d.decision == "revise"),
            "reject": sum(1 for d in decisions if d.decision == "reject"),
            "failed": 3 - len(decisions)
        }
        
        # Apply voting logic
        if votes["reject"] >= 2:
            final_decision = "reject"
            votes["reason"] = "2+ reviewers rejected"
        elif votes["reject"] >= 1:
            final_decision = "reject"
            votes["reason"] = "1+ reviewer rejected"
        elif votes["revise"] >= 1:
            final_decision = "revise"
            votes["reason"] = "1+ reviewer requested revisions"
        elif votes["approve"] == len(decisions):
            final_decision = "approve"
            votes["reason"] = "All reviewers approved"
        else:
            # Fallback (shouldn't happen)
            final_decision = "revise"
            votes["reason"] = "Mixed decisions"
        
        return final_decision, votes
    
    def _calculate_overall_risk(
        self,
        security: Optional[ReviewerDecision],
        performance: Optional[ReviewerDecision],
        qa: Optional[ReviewerDecision]
    ) -> str:
        """
        Calculate overall risk level as the maximum of all reviewers.
        
        Risk hierarchy: high > medium > low
        
        Args:
            security: Security reviewer decision
            performance: Performance reviewer decision
            qa: QA reviewer decision
            
        Returns:
            Overall risk level ("low", "medium", or "high")
        """
        risk_levels = []
        
        if security:
            risk_levels.append(security.risk_level)
        if performance:
            risk_levels.append(performance.risk_level)
        if qa:
            risk_levels.append(qa.risk_level)
        
        if not risk_levels:
            return "high"  # Default to high if no data
        
        # Return maximum risk
        if "high" in risk_levels:
            return "high"
        elif "medium" in risk_levels:
            return "medium"
        else:
            return "low"
    
    def _calculate_overall_confidence(
        self,
        security: Optional[ReviewerDecision],
        performance: Optional[ReviewerDecision],
        qa: Optional[ReviewerDecision]
    ) -> float:
        """
        Calculate overall confidence as the average of all reviewers.
        
        Args:
            security: Security reviewer decision
            performance: Performance reviewer decision
            qa: QA reviewer decision
            
        Returns:
            Overall confidence (0.0 to 1.0)
        """
        confidences = []
        
        if security:
            confidences.append(security.confidence)
        if performance:
            confidences.append(performance.confidence)
        if qa:
            confidences.append(qa.confidence)
        
        if not confidences:
            return 0.0  # Default to 0 if no data
        
        return sum(confidences) / len(confidences)
    
    def _generate_summary(
        self,
        final_decision: str,
        security: Optional[ReviewerDecision],
        performance: Optional[ReviewerDecision],
        qa: Optional[ReviewerDecision],
        voting_breakdown: dict
    ) -> str:
        """
        Generate human-readable summary of council decision.
        
        Args:
            final_decision: The final aggregated decision
            security: Security reviewer decision
            performance: Performance reviewer decision
            qa: QA reviewer decision
            voting_breakdown: Voting statistics
            
        Returns:
            Summary text
        """
        summary_parts = []
        
        # Add voting summary
        summary_parts.append(
            f"Review Council Decision: {final_decision.upper()} "
            f"({voting_breakdown.get('reason', 'Unknown reason')})"
        )
        
        # Add individual reviewer summaries
        if security:
            summary_parts.append(
                f"Security: {security.decision} "
                f"({len(security.concerns)} concerns, "
                f"{len(security.recommendations)} recommendations)"
            )
        
        if performance:
            summary_parts.append(
                f"Performance: {performance.decision} "
                f"({len(performance.concerns)} concerns, "
                f"{len(performance.recommendations)} recommendations)"
            )
        
        if qa:
            summary_parts.append(
                f"QA: {qa.decision} "
                f"({len(qa.concerns)} concerns, "
                f"{len(qa.recommendations)} recommendations)"
            )
        
        return " | ".join(summary_parts)
