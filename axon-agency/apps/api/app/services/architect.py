"""
Architect Agent Service: Reviews and approves/rejects code improvement proposals.

This service acts as a Senior Architect that reviews changes proposed by the
autonomous agent before they are applied, ensuring code quality and safety.
"""

import json
from typing import Optional
from loguru import logger

from app.models import ImprovementProposal, ArchitectDecision, CouncilDecision
from app.providers.gemini import gemini_chat


ARCHITECT_SYSTEM_PROMPT = """Eres el Arquitecto Senior de AXON Agency.

Tu trabajo es revisar cambios de código propuestos por un agente autónomo
y decidir si se deben aprobar, rechazar o pedir revisiones.

Tienes los siguientes principios:
- Prioriza la estabilidad sobre la experimentación.
- Nunca apruebes cambios que puedan romper autenticación, pagos o datos.
- Prefiere refactors pequeños y seguros frente a reescrituras agresivas.
- Usa el historial de outcomes para estimar la probabilidad de éxito.
- Rechaza cambios que modifiquen archivos críticos sin justificación clara.
- Aprueba mejoras de documentación, optimización de imports, y pequeños refactors.

Archivos críticos que requieren revisión estricta:
- app/core/security.py (autenticación)
- app/services/autonomous_agent.py (auto-modificación)
- app/main.py (configuración principal)
- Cualquier archivo que maneje pagos o datos sensibles

Debes devolver SIEMPRE un JSON con este formato EXCLUSIVO:

{
  "decision": "approve" | "revise" | "reject",
  "risk_level": "low" | "medium" | "high",
  "confidence": 0.0-1.0,
  "comments": "explicación breve y clara",
  "required_changes": ["lista de cambios o condiciones"]
}

No agregues texto fuera de este JSON.
"""


class ArchitectAgentService:
    """
    Architect Agent that reviews improvement proposals before they are applied.
    """
    
    def __init__(self, learning_service=None, config: Optional[dict] = None):
        """
        Initialize Architect Agent.
        
        Args:
            learning_service: Learning service for historical context (optional)
            config: Configuration dict (optional)
        """
        self.learning_service = learning_service
        self.config = config or {}
        logger.info("Architect Agent Service initialized")
    
    async def review_proposal(
        self,
        proposal: ImprovementProposal,
        council_decision: Optional[CouncilDecision] = None,
    ) -> ArchitectDecision:
        """
        Review an improvement proposal and make a decision.
        
        Args:
            proposal: The improvement proposal to review
            council_decision: Optional council decision from multi-expert review
            
        Returns:
            ArchitectDecision with approve/revise/reject decision
        """
        logger.info(
            f"Reviewing proposal for session {proposal.session_id}, "
            f"iteration {proposal.iteration}, files: {proposal.files}"
        )
        
        # Collect historical context from Learning Layer if available
        historical_context = await self._get_historical_context(proposal)
        
        # Build review prompt (including council decision if available)
        review_prompt = self._build_review_prompt(proposal, historical_context, council_decision)
        
        try:
            # Call LLM for review
            messages = [
                {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
                {"role": "user", "content": review_prompt}
            ]
            
            response = await gemini_chat(messages=messages)
            
            # Parse JSON response
            decision = self._parse_decision(response)
            
            logger.info(
                f"Architect decision for {proposal.files}: {decision.decision} "
                f"(risk: {decision.risk_level}, confidence: {decision.confidence:.2f})"
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Error reviewing proposal: {e}")
            # Fail-safe: reject on error
            return ArchitectDecision(
                decision="reject",
                risk_level="high",
                confidence=0.0,
                comments=f"Error during review: {str(e)}. Rejecting for safety.",
                required_changes=[]
            )
    
    async def _get_historical_context(
        self,
        proposal: ImprovementProposal
    ) -> str:
        """
        Get historical context from Learning Layer.
        
        Args:
            proposal: The improvement proposal
            
        Returns:
            String with historical context summary
        """
        if not self.learning_service:
            return "No historical data available."
        
        try:
            # Get success rate for this improvement type
            stats = await self.learning_service.get_success_stats()
            
            # Build context summary
            context_parts = []
            
            if proposal.predicted_success is not None:
                context_parts.append(
                    f"Predicted success probability: {proposal.predicted_success:.1%}"
                )
            
            # Overall success rate
            overall_rate = stats.get("overall_success_rate", 0)
            context_parts.append(f"Overall improvement success rate: {overall_rate:.1%}")
            
            # Type-specific success rate if available
            type_stats = stats.get("by_type", {})
            if type_stats:
                context_parts.append("\nSuccess rates by improvement type:")
                for imp_type, rate in type_stats.items():
                    context_parts.append(f"  - {imp_type}: {rate:.1%}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"Could not get historical context: {e}")
            return "Historical context unavailable."
    
    def _build_review_prompt(
        self,
        proposal: ImprovementProposal,
        historical_context: str,
        council_decision: Optional[CouncilDecision] = None
    ) -> str:
        """
        Build prompt for architect review.
        
        Args:
            proposal: The improvement proposal
            historical_context: Historical context from Learning Layer
            council_decision: Optional council decision from expert reviewers
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Revisa la siguiente propuesta de mejora de código:

**Sesión:** {proposal.session_id}
**Iteración:** {proposal.iteration}

**Resumen:** {proposal.summary}

**Razón:** {proposal.reason}

**Archivos afectados:**
{chr(10).join(f'  - {f}' for f in proposal.files)}

**Diff/Cambios:**
```
{proposal.diff[:2000]}{'...(truncated)' if len(proposal.diff) > 2000 else ''}
```
"""
        
        if proposal.before_metrics:
            prompt += f"\n**Métricas antes:**\n{json.dumps(proposal.before_metrics, indent=2)}\n"
        
        if historical_context:
            prompt += f"\n**Contexto histórico:**\n{historical_context}\n"
        
        # Include Review Council decision if available
        if council_decision:
            prompt += f"\n\n**🔍 REVIEW COUNCIL (Expertos Especializados):**\n"
            prompt += f"Decisión final del Council: **{council_decision.final_decision.upper()}**\n"
            prompt += f"Riesgo agregado: {council_decision.overall_risk_level}\n"
            prompt += f"Confianza promedio: {council_decision.overall_confidence:.2f}\n"
            prompt += f"Votación: {council_decision.voting_breakdown}\n\n"
            
            # Security reviewer
            if council_decision.security_decision:
                sec = council_decision.security_decision
                prompt += f"**Security Reviewer:** {sec.decision} (risk: {sec.risk_level})\n"
                if sec.concerns:
                    prompt += f"  Preocupaciones: {', '.join(sec.concerns[:3])}\n"
            
            # Performance reviewer
            if council_decision.performance_decision:
                perf = council_decision.performance_decision
                prompt += f"**Performance Reviewer:** {perf.decision} (risk: {perf.risk_level})\n"
                if perf.concerns:
                    prompt += f"  Preocupaciones: {', '.join(perf.concerns[:3])}\n"
            
            # QA reviewer
            if council_decision.qa_decision:
                qa = council_decision.qa_decision
                prompt += f"**QA Reviewer:** {qa.decision} (risk: {qa.risk_level})\n"
                if qa.concerns:
                    prompt += f"  Preocupaciones: {', '.join(qa.concerns[:3])}\n"
            
            prompt += f"\nResumen del Council: {council_decision.summary}\n"
        
        prompt += """
Analiza:
1. ¿Los cambios son seguros?
2. ¿Afectan código crítico?
3. ¿El diff muestra cambios razonables?
4. ¿La justificación es clara?
5. ¿El riesgo está justificado por el beneficio?
"""
        
        if council_decision:
            prompt += f"""6. ¿Estás de acuerdo con la evaluación del Review Council?
7. Si el Council encontró riesgos "{council_decision.overall_risk_level}", ¿son aceptables?
"""
        
        prompt += "\nDevuelve tu decisión en JSON exclusivamente.\n"
        
        return prompt
    
    def _parse_decision(self, response: str) -> ArchitectDecision:
        """
        Parse LLM response into ArchitectDecision.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed ArchitectDecision
            
        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Try to find JSON in response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1]) if len(lines) > 2 else response
                response = response.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            data = json.loads(response)
            
            # Validate and create decision
            return ArchitectDecision(
                decision=data["decision"],
                risk_level=data["risk_level"],
                confidence=float(data["confidence"]),
                comments=data["comments"],
                required_changes=data.get("required_changes", [])
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse architect decision: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid architect response format: {e}")
