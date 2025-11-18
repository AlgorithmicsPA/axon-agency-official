"""
Security Reviewer Service: Reviews code for security vulnerabilities.

This specialized reviewer focuses on identifying security risks in code changes,
including authentication issues, injection vulnerabilities, and secrets handling.
"""

import json
from typing import Optional
from loguru import logger

from app.models import ImprovementProposal, ReviewerDecision
from app.providers.gemini import gemini_chat


SECURITY_SYSTEM_PROMPT = """Eres el Revisor de Seguridad del Review Council de AXON Agency.

Tu especialidad es identificar vulnerabilidades de seguridad en cambios de código.

ÁREAS DE ENFOQUE:
- Autenticación y control de acceso
- Validación de entrada de usuario
- Manejo de secretos y credenciales
- Inyección SQL y NoSQL
- Vulnerabilidades XSS y CSRF
- Uso de criptografía
- Exposición de datos sensibles

REGLAS ESTRICTAS:
- NUNCA apruebes cambios a archivos de autenticación sin justificación clara
- RECHAZA cualquier cambio que exponga secretos o credenciales
- RECHAZA cambios que eliminen validación de entrada
- Sé especialmente crítico con archivos en app/core/security.py, app/routers/auth.py
- Requiere revisión para cualquier uso de exec(), eval(), o comandos shell

Debes devolver SIEMPRE un JSON con este formato EXCLUSIVO:

{
  "reviewer_name": "security",
  "decision": "approve" | "revise" | "reject",
  "risk_level": "low" | "medium" | "high",
  "confidence": 0.0-1.0,
  "comments": "explicación de tu análisis de seguridad",
  "concerns": ["lista de problemas de seguridad específicos encontrados"],
  "recommendations": ["lista de mejoras de seguridad sugeridas"]
}

No agregues texto fuera de este JSON.
"""


class SecurityReviewerService:
    """
    Reviews code for security vulnerabilities and best practices.
    
    Focus areas:
    - Auth/access control changes
    - Input validation
    - Secrets handling
    - SQL injection risks
    - XSS vulnerabilities
    - Cryptography usage
    """
    
    SECURITY_KEYWORDS = [
        "password", "auth", "token", "secret", "key",
        "sql", "query", "exec", "eval", "shell",
        "crypto", "hash", "encrypt", "decrypt",
        "api_key", "credential", "session", "cookie"
    ]
    
    CRITICAL_FILES = [
        "app/core/security.py",
        "app/routers/auth.py",
        "app/services/autonomous_agent.py",
        "app/core/config.py"
    ]
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize Security Reviewer."""
        self.config = config or {}
        logger.info("Security Reviewer Service initialized")
    
    async def review_proposal(
        self,
        proposal: ImprovementProposal
    ) -> ReviewerDecision:
        """
        Review proposal for security vulnerabilities.
        
        Args:
            proposal: The improvement proposal to review
            
        Returns:
            ReviewerDecision with security analysis
        """
        logger.info(f"Security review for session {proposal.session_id}, files: {proposal.files}")
        
        review_prompt = self._build_review_prompt(proposal)
        
        try:
            messages = [
                {"role": "system", "content": SECURITY_SYSTEM_PROMPT},
                {"role": "user", "content": review_prompt}
            ]
            
            response = await gemini_chat(messages=messages)
            decision = self._parse_decision(response)
            
            logger.info(
                f"Security decision: {decision.decision} "
                f"(risk: {decision.risk_level}, concerns: {len(decision.concerns)})"
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Error in security review: {e}")
            return ReviewerDecision(
                reviewer_name="security",
                decision="reject",
                risk_level="high",
                confidence=0.0,
                comments=f"Security review failed: {str(e)}. Rejecting for safety.",
                concerns=["Review system error"],
                recommendations=["Manual security review required"]
            )
    
    def _build_review_prompt(self, proposal: ImprovementProposal) -> str:
        """Build security review prompt."""
        
        critical_files = [f for f in proposal.files if any(cf in f for cf in self.CRITICAL_FILES)]
        has_security_keywords = any(
            keyword in proposal.diff.lower() 
            for keyword in self.SECURITY_KEYWORDS
        )
        
        prompt = f"""Revisa este cambio de código desde una perspectiva de SEGURIDAD:

**Sesión:** {proposal.session_id}
**Archivos afectados:** {', '.join(proposal.files)}
"""
        
        if critical_files:
            prompt += f"\n⚠️ ARCHIVOS CRÍTICOS: {', '.join(critical_files)}\n"
        
        if has_security_keywords:
            prompt += "\n⚠️ Contiene palabras clave de seguridad\n"
        
        prompt += f"""
**Resumen:** {proposal.summary}

**Razón:** {proposal.reason}

**Diff:**
```
{proposal.diff[:3000]}{'...(truncated)' if len(proposal.diff) > 3000 else ''}
```

ANALIZA:
1. ¿Se modifican archivos de autenticación o seguridad?
2. ¿Hay cambios en validación de entrada?
3. ¿Se exponen secretos o credenciales?
4. ¿Existe riesgo de inyección SQL o XSS?
5. ¿Se usa exec(), eval() o comandos shell?
6. ¿Los cambios criptográficos son seguros?

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
                reviewer_name=data.get("reviewer_name", "security"),
                decision=data["decision"],
                risk_level=data["risk_level"],
                confidence=float(data["confidence"]),
                comments=data["comments"],
                concerns=data.get("concerns", []),
                recommendations=data.get("recommendations", [])
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse security decision: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid security reviewer response format: {e}")
