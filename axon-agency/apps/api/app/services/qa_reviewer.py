"""
QA Reviewer Service: Reviews code for quality, testing, and maintainability.

This specialized reviewer focuses on identifying quality issues, missing tests,
documentation gaps, and maintainability concerns in code changes.
"""

import json
from typing import Optional
from loguru import logger

from app.models import ImprovementProposal, ReviewerDecision
from app.providers.gemini import gemini_chat


QA_SYSTEM_PROMPT = """Eres el Revisor de Calidad (QA) del Review Council de AXON Agency.

Tu especialidad es identificar problemas de calidad, testing y mantenibilidad en cambios de código.

ÁREAS DE ENFOQUE:
- Cobertura de tests (unit tests, integration tests)
- Calidad del código y legibilidad
- Documentación (docstrings, comments, README)
- Complejidad de código (cyclomatic complexity)
- Mantenibilidad y deuda técnica
- Nombres de variables y funciones descriptivos
- Separación de responsabilidades (SRP)
- Patrones de diseño apropiados

REGLAS:
- RECHAZA cambios complejos sin tests asociados
- RECHAZA código con complejidad ciclomática >10 sin justificación
- Marca falta de docstrings en funciones públicas
- Requiere revisión para código duplicado
- Sé crítico con nombres de variables poco descriptivos (x, tmp, data)
- RECHAZA funciones >50 líneas sin clara separación de responsabilidades

Debes devolver SIEMPRE un JSON con este formato EXCLUSIVO:

{
  "reviewer_name": "qa",
  "decision": "approve" | "revise" | "reject",
  "risk_level": "low" | "medium" | "high",
  "confidence": 0.0-1.0,
  "comments": "explicación de tu análisis de calidad",
  "concerns": ["lista de problemas de calidad específicos"],
  "recommendations": ["lista de mejoras de calidad sugeridas"]
}

No agregues texto fuera de este JSON.
"""


class QAReviewerService:
    """
    Reviews code for quality, testing, and maintainability.
    
    Focus areas:
    - Test coverage and quality
    - Code complexity
    - Documentation completeness
    - Code maintainability
    - Design patterns
    - Naming conventions
    """
    
    QA_KEYWORDS = [
        "test", "assert", "mock", "fixture",
        "def ", "class ", "async def",
        "import", "from", "return",
        "if", "for", "while", "try"
    ]
    
    CRITICAL_FILES = [
        "app/services/",
        "app/models/",
        "app/core/",
        "app/routers/"
    ]
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize QA Reviewer."""
        self.config = config or {}
        logger.info("QA Reviewer Service initialized")
    
    async def review_proposal(
        self,
        proposal: ImprovementProposal
    ) -> ReviewerDecision:
        """
        Review proposal for quality, testing, and maintainability.
        
        Args:
            proposal: The improvement proposal to review
            
        Returns:
            ReviewerDecision with QA analysis
        """
        logger.info(f"QA review for session {proposal.session_id}, files: {proposal.files}")
        
        review_prompt = self._build_review_prompt(proposal)
        
        try:
            messages = [
                {"role": "system", "content": QA_SYSTEM_PROMPT},
                {"role": "user", "content": review_prompt}
            ]
            
            response = await gemini_chat(messages=messages)
            decision = self._parse_decision(response)
            
            logger.info(
                f"QA decision: {decision.decision} "
                f"(risk: {decision.risk_level}, concerns: {len(decision.concerns)})"
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Error in QA review: {e}")
            return ReviewerDecision(
                reviewer_name="qa",
                decision="revise",
                risk_level="medium",
                confidence=0.0,
                comments=f"QA review failed: {str(e)}. Requesting manual review.",
                concerns=["Review system error"],
                recommendations=["Manual QA review required"]
            )
    
    def _build_review_prompt(self, proposal: ImprovementProposal) -> str:
        """Build QA review prompt."""
        
        critical_files = [
            f for f in proposal.files 
            if any(cf in f for cf in self.CRITICAL_FILES)
        ]
        
        has_test_changes = any("test" in f.lower() for f in proposal.files)
        
        prompt = f"""Revisa este cambio de código desde una perspectiva de CALIDAD y TESTING:

**Sesión:** {proposal.session_id}
**Archivos afectados:** {', '.join(proposal.files)}
"""
        
        if critical_files:
            prompt += f"\n⚠️ ARCHIVOS CRÍTICOS: {', '.join(critical_files)}\n"
        
        if has_test_changes:
            prompt += "\n✅ Incluye cambios en tests\n"
        else:
            prompt += "\n⚠️ NO incluye cambios en tests\n"
        
        prompt += f"""
**Resumen:** {proposal.summary}

**Razón:** {proposal.reason}

**Diff:**
```
{proposal.diff[:3000]}{'...(truncated)' if len(proposal.diff) > 3000 else ''}
```

ANALIZA:
1. ¿Hay tests para los cambios introducidos?
2. ¿La complejidad del código es razonable?
3. ¿Existe documentación adecuada (docstrings)?
4. ¿Los nombres de variables/funciones son descriptivos?
5. ¿El código es mantenible y legible?
6. ¿Se siguen buenas prácticas de diseño?
7. ¿Hay código duplicado o violaciones del DRY?

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
                reviewer_name=data.get("reviewer_name", "qa"),
                decision=data["decision"],
                risk_level=data["risk_level"],
                confidence=float(data["confidence"]),
                comments=data["comments"],
                concerns=data.get("concerns", []),
                recommendations=data.get("recommendations", [])
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse QA decision: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid QA reviewer response format: {e}")
