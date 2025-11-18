"""OpenAI Sales Client with Structured Output for WhatsApp Sales Agent."""

import httpx
from openai import AsyncOpenAI
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from loguru import logger


# ========================================
# PYDANTIC SCHEMAS FOR STRUCTURED OUTPUT
# ========================================

class LeadData(BaseModel):
    """Lead qualification data collected during conversation."""
    nombre: Optional[str] = None
    email: Optional[str] = None
    empresa: Optional[str] = None
    sector: Optional[str] = None
    tamano_empresa: Optional[str] = None
    presupuesto_aprox: Optional[str] = None


class LeadInfo(BaseModel):
    """Lead information with completion status."""
    completed: bool = False
    data: LeadData = Field(default_factory=LeadData)


class ContextNeeded(BaseModel):
    """Flags to trigger external context services."""
    use_melvis: bool = False  # Flag to trigger RAG/knowledge base search
    use_tavily: bool = False  # Flag to trigger web search


class SalesAgentResponse(BaseModel):
    """Structured response from OpenAI sales agent."""
    reply: str  # Message to send to WhatsApp user
    next_step: str  # Next conversation step identifier
    lead: LeadInfo = Field(default_factory=LeadInfo)
    actions: List[Literal["NONE", "CREATE_OR_UPDATE_LEAD", "SUGGEST_CAL_LINK", "CREATE_STRIPE_CHECKOUT"]]
    context_needed: ContextNeeded = Field(default_factory=ContextNeeded)


# ========================================
# OPENAI SALES CLIENT
# ========================================

class OpenAISalesClient:
    """OpenAI client for WhatsApp Sales Agent with structured JSON output."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1"
    ):
        """
        Initialize OpenAI Sales Client.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o-mini)
            base_url: OpenAI API base URL
        """
        # Store full key for client, truncated for logs
        self._api_key_full = api_key
        self._api_key_display = api_key[:15] + "..." if len(api_key) > 15 else "***"
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        
        logger.info(
            f"OpenAI Sales Client initialized. "
            f"Model: {model}, "
            f"Key: {self._api_key_display}"
        )
    
    async def generate_sales_response(
        self,
        user_message: str,
        session_step: str,
        session_answers: dict,
        message_history: List[Dict[str, str]],
        rag_context: Optional[str] = None,
        web_context: Optional[str] = None
    ) -> SalesAgentResponse:
        """
        Generate structured sales agent response using OpenAI with JSON mode.
        
        Args:
            user_message: Latest message from WhatsApp user
            session_step: Current conversation step from session
            session_answers: Collected answers from session
            message_history: Recent conversation history for context
            rag_context: Optional RAG/Melvis knowledge base chunks
            web_context: Optional Tavily web search results
        
        Returns:
            SalesAgentResponse with reply, next_step, lead, actions, context_needed
        """
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt()
            
            # Build user prompt with context
            user_prompt = self._build_user_prompt(
                user_message=user_message,
                session_step=session_step,
                session_answers=session_answers,
                message_history=message_history,
                rag_context=rag_context,
                web_context=web_context
            )
            
            # Call OpenAI with structured output
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=SalesAgentResponse,
                temperature=0.7
            )
            
            parsed_response = response.choices[0].message.parsed
            
            # Handle case where parsing failed
            if parsed_response is None:
                logger.error("OpenAI returned None for parsed response")
                raise ValueError("Failed to parse OpenAI response")
            
            logger.info(
                f"OpenAI sales response generated. "
                f"Step: {session_step} → {parsed_response.next_step}, "
                f"Lead completed: {parsed_response.lead.completed}, "
                f"Actions: {parsed_response.actions}"
            )
            
            return parsed_response
            
        except Exception as e:
            error_msg = str(e)[:200]
            logger.error(f"OpenAI sales call failed: {error_msg}")
            
            # Fallback response on error
            return SalesAgentResponse(
                reply="Disculpa, tuve un problema técnico. ¿Puedes repetir tu mensaje?",
                next_step=session_step,  # Stay on same step
                actions=["NONE"]
            )
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with sales agent instructions."""
        return """Eres el Agente de Ventas de WhatsApp de DANIA Agency.

Tu misión es cualificar leads paso a paso, siguiendo este flujo:

1. **Saludo inicial** (step: greet) → Preguntar nombre
2. **Obtener nombre** (step: get_name) → Preguntar email
3. **Obtener email** (step: get_email) → Preguntar empresa
4. **Obtener empresa** (step: get_empresa) → Preguntar sector
5. **Obtener sector** (step: get_sector) → Preguntar tamaño empresa
6. **Obtener tamaño** (step: get_tamano) → Preguntar presupuesto aproximado
7. **Obtener presupuesto** (step: get_presupuesto) → Lead completo
8. **Lead completo** (step: qualified) → Ofrecer Cal.com link + Stripe checkout

**REGLAS IMPORTANTES**:
- Sé amable y profesional en español
- Si el usuario no responde bien, reformula con paciencia
- NO inventes datos del usuario
- Marca lead.completed = true SOLO cuando tengas todos los datos
- Usa context_needed.use_melvis = true si el usuario hace preguntas sobre servicios/productos
- Usa context_needed.use_tavily = true si el usuario pregunta info externa en tiempo real
- Cuando lead.completed = true, activa acciones: CREATE_OR_UPDATE_LEAD + SUGGEST_CAL_LINK + CREATE_STRIPE_CHECKOUT

**FORMATO DE RESPUESTA**:
Devuelve SIEMPRE un JSON con esta estructura exacta:
{
  "reply": "tu mensaje para WhatsApp",
  "next_step": "siguiente_paso",
  "lead": {
    "completed": true/false,
    "data": {
      "nombre": "",
      "email": "",
      "empresa": "",
      "sector": "",
      "tamano_empresa": "",
      "presupuesto_aprox": ""
    }
  },
  "actions": ["NONE" o "CREATE_OR_UPDATE_LEAD" o "SUGGEST_CAL_LINK" o "CREATE_STRIPE_CHECKOUT"],
  "context_needed": {
    "use_melvis": false,
    "use_tavily": false
  }
}"""
    
    def _build_user_prompt(
        self,
        user_message: str,
        session_step: str,
        session_answers: dict,
        message_history: List[Dict[str, str]],
        rag_context: Optional[str] = None,
        web_context: Optional[str] = None
    ) -> str:
        """Build user prompt with all context."""
        prompt_parts = [
            f"**Mensaje del usuario**: {user_message}",
            f"**Paso actual**: {session_step}",
            f"**Respuestas guardadas**: {session_answers}",
        ]
        
        # Add message history
        if message_history:
            history_str = "\n".join([
                f"- {msg['direction']}: {msg['text']}" 
                for msg in message_history[-5:]  # Last 5 messages
            ])
            prompt_parts.append(f"**Historial reciente**:\n{history_str}")
        
        # Add RAG context if provided
        if rag_context:
            prompt_parts.append(f"**Base de conocimiento (Melvis)**:\n{rag_context}")
        
        # Add web context if provided
        if web_context:
            prompt_parts.append(f"**Información web (Tavily)**:\n{web_context}")
        
        prompt_parts.append(
            "\nGenera la respuesta JSON estructurada siguiendo el flujo de cualificación de leads."
        )
        
        return "\n\n".join(prompt_parts)
