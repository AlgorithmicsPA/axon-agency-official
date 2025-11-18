"""
Performance Reviewer Service: Reviews code for performance impact.

This specialized reviewer focuses on identifying performance bottlenecks,
inefficient database queries, and resource usage issues.
"""

import json
from typing import Optional
from loguru import logger

from app.models import ImprovementProposal, ReviewerDecision
from app.providers.gemini import gemini_chat


PERFORMANCE_SYSTEM_PROMPT = """Eres el Revisor de Rendimiento del Review Council de AXON Agency.

Tu especialidad es identificar problemas de rendimiento en cambios de código.

ÁREAS DE ENFOQUE:
- Eficiencia de queries a base de datos
- Complejidad de loops (n² o superior)
- Uso de memoria y estructuras de datos
- Uso correcto de async/await
- Operaciones de archivos grandes
- Patrones N+1 en queries
- Operaciones bloqueantes

REGLAS:
- RECHAZA loops anidados sobre colecciones grandes sin justificación
- RECHAZA queries en loops (patrón N+1)
- Marca operaciones bloqueantes en código async
- Requiere revisión para operaciones de archivos >10MB
- Sé crítico con uso de .all() en queries de tablas grandes

Debes devolver SIEMPRE un JSON con este formato EXCLUSIVO:

{
  "reviewer_name": "performance",
  "decision": "approve" | "revise" | "reject",
  "risk_level": "low" | "medium" | "high",
  "confidence": 0.0-1.0,
  "comments": "explicación de tu análisis de rendimiento",
  "concerns": ["lista de problemas de rendimiento específicos"],
  "recommendations": ["lista de optimizaciones sugeridas"]
}

No agregues texto fuera de este JSON.
"""


class PerformanceReviewerService:
    """
    Reviews code for performance impact.
    
    Focus areas:
    - Database query efficiency
    - Loop complexity
    - Memory usage
    - Async/await usage
    - Large file operations
    - N+1 query patterns
    """
    
    PERFORMANCE_KEYWORDS = [
        "for", "while", "query", "db", "database",
        "sleep", "await", "async", "thread",
        "cache", "memory", "list", "dict",
        ".all()", "join", "filter", "select"
    ]
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize Performance Reviewer."""
        self.config = config or {}
        logger.info("Performance Reviewer Service initialized")
    
    async def review_proposal(
        self,
        proposal: ImprovementProposal
    ) -> ReviewerDecision:
        """
        Review proposal for performance impact.
        
        Args:
            proposal: The improvement proposal to review
            
        Returns:
            ReviewerDecision with performance analysis
        """
        logger.info(f"Performance review for session {proposal.session_id}, files: {proposal.files}")
        
        review_prompt = self._build_review_prompt(proposal)
        
        try:
            messages = [
                {"role": "system", "content": PERFORMANCE_SYSTEM_PROMPT},
                {"role": "user", "content": review_prompt}
            ]
            
            response = await gemini_chat(messages=messages)
            decision = self._parse_decision(response)
            
            logger.info(
                f"Performance decision: {decision.decision} "
                f"(risk: {decision.risk_level}, concerns: {len(decision.concerns)})"
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Error in performance review: {e}")
            return ReviewerDecision(
                reviewer_name="performance",
                decision="revise",
                risk_level="medium",
                confidence=0.0,
                comments=f"Performance review failed: {str(e)}. Requesting manual review.",
                concerns=["Review system error"],
                recommendations=["Manual performance review required"]
            )
    
    def _build_review_prompt(self, proposal: ImprovementProposal) -> str:
        """Build performance review prompt."""
        
        has_performance_keywords = any(
            keyword in proposal.diff.lower() 
            for keyword in self.PERFORMANCE_KEYWORDS
        )
        
        prompt = f"""Revisa este cambio de código desde una perspectiva de RENDIMIENTO:

**Sesión:** {proposal.session_id}
**Archivos afectados:** {', '.join(proposal.files)}
"""
        
        if has_performance_keywords:
            prompt += "\n⚠️ Contiene operaciones que afectan rendimiento\n"
        
        prompt += f"""
**Resumen:** {proposal.summary}

**Razón:** {proposal.reason}

**Diff:**
```
{proposal.diff[:3000]}{'...(truncated)' if len(proposal.diff) > 3000 else ''}
```

ANALIZA:
1. ¿Hay queries en loops (N+1)?
2. ¿Los loops están bien optimizados?
3. ¿Se usa async/await correctamente?
4. ¿Hay operaciones bloqueantes en código async?
5. ¿El uso de memoria es razonable?
6. ¿Las estructuras de datos son eficientes?

Devuelve tu decisión en JSON exclusivamente.
"""
        
        return prompt
    
    def _parse_decision(self, response: str) -> ReviewerDecision:
        """Parse LLM response into ReviewerDecision."""
        try:
            response = response.strip()
            
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1]) if len(lines) > 2 else response
                response = response.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(response)
            
            return ReviewerDecision(
                reviewer_name=data.get("reviewer_name", "performance"),
                decision=data["decision"],
                risk_level=data["risk_level"],
                confidence=float(data["confidence"]),
                comments=data["comments"],
                concerns=data.get("concerns", []),
                recommendations=data.get("recommendations", [])
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse performance decision: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid performance reviewer response format: {e}")
