"""
Chat Orchestration Service: Routes chat requests to LLM or Autonomous Agent.

This service transforms the Super Axon Agent into an intelligent orchestrator that:
- Responds to simple questions with direct LLM calls
- Delegates complex builds to the Autonomous Agent Service
- Maintains clear separation between chat and autonomous flows
"""

import json
from typing import Any, Dict, Optional
from pydantic import BaseModel
from loguru import logger

from app.services.llm_router import get_llm_router
from app.services.orders_orchestrator import get_orchestrator_service
from app.providers.gemini import gemini_chat
from app.providers.openai import openai_chat
from app.providers.ollama import ollama_chat
from app.core.config import settings
from app.core.database import get_session


# ============================================================================
# SUPER AXON AGENT SYSTEM PROMPT v1.0
# ============================================================================
SUPER_AXON_SYSTEM_PROMPT = """🌐 SUPER AXON AGENT — Control Plane de AXON Agency

🧠 IDENTIDAD
Eres SUPER AXON AGENT, el cerebro orquestador central de AXON Agency, ejecutado en:
• Jetson AGX Orin (Axon88) — 64GB RAM, GPU, 2TB SSD
• Replit Workspaces — Desarrollo colaborativo
• n8n Workflows — Automatización inteligente
• Axon Core API — Infraestructura base
• MetaFederico Framework — Arquitectura empresarial

Sistema de IA autónomo, multi-agente, multi-LLM, multi-tenant y auto-mejorable para:
✔️ Construir, optimizar y gobernar todos los proyectos de la agencia
✔️ Orquestar subagentes especializados
✔️ Integrar LLMs locales + cloud
✔️ Ejecutar procesos inteligentes
✔️ Mantener memoria estructurada
✔️ Asegurar calidad, seguridad y coherencia

Tu rol: Arquitecto, director técnico, estratega, supervisor y cerebro operativo.

🏭 MODELO DE FÁBRICA PRIVADA
Eres el CEREBRO de la fábrica privada de Federico, NO un chatbot público.
• Los clientes finales NUNCA te ven - solo ven sus productos terminados
• Tu misión: ayudar a Federico a diseñar, construir y mejorar autopilotos SaaS
• Productos que construyes: autopilotos completos (whatsapp bots, sales agents, webhooks)
• Cuando Federico menciona "orden" o "autopilot", estás hablando de producción de software
• Orquestas subagentes para construir productos reales que se entregan a clientes

🧱 GOVERNING CORE (12 reglas fundamentales)
1. AXON supervisa y dirige a todos los subagentes
2. No mezclas contextos entre tenants ni proyectos
3. Proteges información sensible
4. Nunca ejecutas acciones de sistema sin confirmación
5. Orquestas subagentes cuando la tarea lo requiera
6. Usas la memoria ejecutiva para continuidad
7. No inventas datos no verificados
8. Analizas antes de responder; siempre entregas claridad
9. Explicas como consultor senior, no como asistente básico
10. Sugieres mejoras siempre que existan
11. Cumples estándares de calidad, seguridad y estructura
12. Operas con precisión, elegancia y visión estratégica

🤖 SUBAGENTES BAJO TU DIRECCIÓN
1) Marketing Agent — Campañas, funnels, contenido, WhatsApp, leads
2) Installer Agent — APIs, claves, webhooks, n8n, Replit
3) Developer Agent — Backend, frontend, RAG, arquitectura, debugging
4) Planner Agent — Roadmaps, fases, estructuras, specs
5) Ops Agent — Diagnósticos, logs, backups, servicios
6) QA Agent — Pruebas, coherencia, correcciones
7) Security Agent — Revisión de riesgos, permisos, datos sensibles
8) Performance Agent — Optimización, microservicios, cargas, memory awareness
9) RAG Agent — Indexación, embeddings, Brand Brain, Knowledge Spaces
10) Autopilot Agent — Automatizaciones, procesos, acciones multi-step

🔄 MULTI-LLM ROUTING
Local (Ollama/Jetson): DeepSeek-R1, Mistral, Llama 3.1
Cloud (API): GPT-5.1, GPT-4o, Gemini 2.0 Flash, Gemini Pro, Claude
Routing automático según tarea (código, arquitectura, contenido, razonamiento)

🏢 MULTI-TENANT (RLS completo)
Cada tenant aislado con Brand Brain, RAG, memoria y pipelines propios.
Nunca mezclas info entre: escuelas, notarías, hospitales, tiendas, condominios, delivery, clientes externos.

📚 CAPACIDADES PRINCIPALES
✅ RAG & Knowledge Layer — Ingesta docs, vector stores, embeddings, Brand Brains
✅ Auto-Builder — Proyectos completos, APIs, BD, UI, n8n, Docker, systemd
✅ Review Council — Security, Performance, QA (cada entrega validada)
✅ Self-Improvement — Aprende del output, mejora prompts, refina procesos
✅ Code Playground — Editor Monaco, ejecución Docker sandbox
✅ Autonomous Agent — Construcción autónoma con Architect Supervisor
✅ Meta-Agent System — Agentes especializados (SECURITY, PERFORMANCE, QA, BUILDER, PLANNER, TESTER)
✅ Learning Layer — Adaptive learning, historical outcomes

🧾 FORMATO DE RESPUESTA
Responde SIEMPRE con estructura profesional clara:
1) Respuesta para el usuario — Clara, estratégica, humana
2) Análisis — Qué se pidió, qué implica, qué módulos intervienen
3) Subagentes — Qué agentes deben actuar y por qué
4) Plan — Pasos claros con dependencias y lógica
5) Ejecución — Creación, código, propuesta (si aplica)
6) Review Council — Observaciones de seguridad, performance, QA
7) Memory Update — Qué debe guardarse
8) Next Steps — Recomendación estratégica

❤️ OBJETIVO FINAL
Construir junto a Federico una agencia total, autónoma, escalable y profesional:
Multi-agente | Multi-LLM | Multi-tenant | RAG avanzado | Auto-mejora | Pipelines inteligentes
Sistema replicable en escuelas, notarías, hospitales, comercios, condominios, empresas globales.

AXON es el cerebro que lo hará posible. Vamos a cambiar el mundo juntos.
"""


class ChatIntent(BaseModel):
    """Classified intent from user message."""
    kind: str  # "INFO", "SMALL_HELP", "AUTONOMOUS_BUILD"
    goal: str
    mode: Optional[str] = "balanced"
    tenant_id: str = "default"
    metadata: Dict[str, Any] = {}


class AutonomousSessionInfo(BaseModel):
    """Information about an autonomous session."""
    session_id: str
    mode: str
    url: str
    started_at: str
    goal: str


class ChatResponse(BaseModel):
    """Response from chat orchestration."""
    type: str  # "direct" or "autonomous_session"
    message: str
    provider: Optional[str] = None
    session: Optional[AutonomousSessionInfo] = None


class ChatOrchestrationService:
    """
    Orchestrates chat requests between direct LLM responses and autonomous agent delegation.
    
    This service classifies user intents and routes them appropriately:
    - INFO/SMALL_HELP → Direct LLM response
    - AUTONOMOUS_BUILD → Delegate to AutonomousAgentService
    """
    
    def __init__(self):
        """Initialize the chat orchestration service."""
        self.llm_router = get_llm_router()
        logger.info("ChatOrchestrationService initialized")
    
    async def handle_message(self, text: str, current_user: Any) -> ChatResponse:
        """
        Handle incoming chat message by classifying intent and routing appropriately.
        
        Args:
            text: User message text
            current_user: Current authenticated user (or None in dev mode)
            
        Returns:
            ChatResponse with either direct answer or autonomous session info
        """
        logger.info(f"Handling message: {text[:100]}...")
        
        # Early detection: Orders processing command
        if self._is_orders_processing_command(text):
            logger.info("🏭 Detected orders processing command")
            return await self._handle_process_orders()
        
        # Step 1: Classify intent
        intent = await self.classify_intent(text)
        logger.info(f"Classified intent: {intent.kind} - {intent.goal[:80]}")
        
        # Step 2: Route based on intent
        if intent.kind in ["INFO", "SMALL_HELP"]:
            # Direct LLM response
            return await self._handle_direct_response(text, intent)
        else:  # AUTONOMOUS_BUILD
            # Delegate to autonomous agent
            return await self._start_autonomous_session(intent, current_user)
    
    async def classify_intent(self, text: str) -> ChatIntent:
        """
        Classify user intent using LLM.
        
        Args:
            text: User message
            
        Returns:
            ChatIntent with classification results
        """
        classification_prompt = f"""Analiza esta solicitud del usuario y clasifícala:

"{text}"

Responde SOLO con JSON válido en este formato exacto:
{{
  "kind": "INFO" | "SMALL_HELP" | "AUTONOMOUS_BUILD",
  "goal": "descripción clara del objetivo del usuario",
  "mode": "balanced"
}}

Guía de clasificación:
- INFO: Preguntas generales, explicaciones, conceptos teóricos, definiciones
  Ejemplos: "¿Qué es Python?", "Explica qué es una API", "¿Cómo funciona FastAPI?"
  
- SMALL_HELP: Tareas pequeñas puntuales, consultas específicas, ayuda rápida
  Ejemplos: "Dame un ejemplo de código", "¿Cómo se declara una variable?", "Muestra cómo usar asyncio"
  
- AUTONOMOUS_BUILD: Crear agentes, landing pages, proyectos completos, sistemas complejos, flujos de trabajo
  Ejemplos: "Crea un agente de seguridad", "Construye una landing page", "Desarrolla un sistema de chat"

IMPORTANTE: Responde SOLO con el JSON, sin texto adicional."""

        try:
            # Use Gemini preferentially for classification (best JSON support)
            messages = [{"role": "user", "content": classification_prompt}]
            
            response_text = None
            provider_used = None
            
            # Try providers in order: Gemini → OpenAI → Ollama
            if settings.gemini_api_key:
                try:
                    response_text = await gemini_chat(messages)
                    provider_used = "gemini"
                except Exception as e:
                    logger.warning(f"Gemini classification failed: {e}")
            
            if not response_text and settings.openai_api_key:
                try:
                    response_text = await openai_chat(messages)
                    provider_used = "openai"
                except Exception as e:
                    logger.warning(f"OpenAI classification failed: {e}")
            
            if not response_text and settings.ollama_available:
                try:
                    response_text = await ollama_chat(messages)
                    provider_used = "ollama"
                except Exception as e:
                    logger.warning(f"Ollama classification failed: {e}")
            
            if not response_text:
                raise ValueError("No LLM provider available for classification")
            
            logger.info(f"Classification done with {provider_used}")
            
            # Parse JSON response
            # Clean markdown code blocks if present
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            parsed = json.loads(clean_text)
            
            return ChatIntent(
                kind=parsed.get("kind", "INFO"),
                goal=parsed.get("goal", text),
                mode=parsed.get("mode", "balanced"),
                tenant_id="default",
                metadata={"classifier": provider_used}
            )
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse classification JSON: {e}, response: {response_text}")
            # Fallback: keyword-based classification
            return self._fallback_classification(text)
        except Exception as e:
            logger.error(f"Classification error: {e}")
            # Fallback classification
            return self._fallback_classification(text)
    
    def _fallback_classification(self, text: str) -> ChatIntent:
        """
        Fallback classification using keyword matching.
        
        Args:
            text: User message
            
        Returns:
            ChatIntent based on keyword analysis
        """
        text_lower = text.lower()
        
        # Keywords for AUTONOMOUS_BUILD
        build_keywords = [
            "crea", "crear", "construye", "construir", "desarrolla", "desarrollar",
            "implementa", "implementar", "genera", "generar", "agente", "landing",
            "página", "sistema", "aplicación", "proyecto", "flujo", "bot"
        ]
        
        # Keywords for INFO
        info_keywords = [
            "qué es", "que es", "explica", "explicar", "cómo funciona", "como funciona",
            "definición", "definicion", "concepto"
        ]
        
        # Check for build intent
        if any(keyword in text_lower for keyword in build_keywords):
            return ChatIntent(
                kind="AUTONOMOUS_BUILD",
                goal=text,
                mode="balanced",
                metadata={"classifier": "fallback"}
            )
        
        # Check for info intent
        if any(keyword in text_lower for keyword in info_keywords):
            return ChatIntent(
                kind="INFO",
                goal=text,
                mode="balanced",
                metadata={"classifier": "fallback"}
            )
        
        # Default to SMALL_HELP for ambiguous cases
        return ChatIntent(
            kind="SMALL_HELP",
            goal=text,
            mode="balanced",
            metadata={"classifier": "fallback"}
        )
    
    async def _handle_direct_response(self, text: str, intent: ChatIntent) -> ChatResponse:
        """
        Handle direct LLM response for INFO and SMALL_HELP intents.
        
        Args:
            text: User message
            intent: Classified intent
            
        Returns:
            ChatResponse with direct LLM answer
        """
        logger.info(f"Handling direct response for: {intent.kind}")
        
        # Include SUPER AXON SYSTEM PROMPT to give agent full context and identity
        messages = [
            {"role": "system", "content": SUPER_AXON_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
        
        # Try providers with fallback
        response_text = None
        provider_used = None
        last_error = None
        
        providers = []
        if settings.gemini_api_key:
            providers.append(("gemini", gemini_chat))
        if settings.openai_api_key:
            providers.append(("openai", openai_chat))
        if settings.ollama_available:
            providers.append(("ollama", ollama_chat))
        
        if not providers:
            raise ValueError("No LLM provider configured")
        
        for provider_name, provider_func in providers:
            try:
                response_text = await provider_func(messages)
                provider_used = provider_name
                logger.info(f"✅ Direct response from {provider_name}")
                break
            except Exception as e:
                last_error = e
                logger.warning(f"{provider_name} failed: {e}, trying next...")
                continue
        
        if response_text is None:
            raise Exception(f"All providers failed. Last error: {last_error}")
        
        return ChatResponse(
            type="direct",
            message=response_text,
            provider=provider_used
        )
    
    async def _start_autonomous_session(
        self,
        intent: ChatIntent,
        current_user: Any
    ) -> ChatResponse:
        """
        Start an autonomous agent session for complex builds.
        
        Args:
            intent: Classified intent with goal
            current_user: Current user
            
        Returns:
            ChatResponse with autonomous session info
        """
        logger.info(f"Starting autonomous session for goal: {intent.goal[:80]}")
        
        # Import here to avoid circular dependency
        from app.routers.autonomous import get_autonomous_agent
        
        # Get autonomous agent service
        agent = await get_autonomous_agent()
        
        # Start external goal session
        session_data = await agent.start_external_goal_session(
            goal=intent.goal,
            mode=intent.mode,
            tenant_id=intent.tenant_id,
            metadata=intent.metadata,
            origin="chat"
        )
        
        # Build session info
        session_info = AutonomousSessionInfo(
            session_id=session_data["session_id"],
            mode=session_data["mode"],
            url=f"/agent/autonomous/{session_data['session_id']}",
            started_at=session_data["started_at"],
            goal=session_data["goal"]
        )
        
        # Build response message
        message = f"""🤖 He iniciado una sesión autónoma para trabajar en tu objetivo:

**Goal:** {intent.goal}

**Session ID:** {session_data['session_id']}
**Mode:** {session_data['mode']}
**Status:** {session_data['status']}

Puedes monitorear el progreso en: {session_info.url}

El agente autónomo está trabajando de manera independiente para completar tu solicitud."""
        
        return ChatResponse(
            type="autonomous_session",
            message=message,
            provider="autonomous_agent",
            session=session_info
        )
    
    def _is_orders_processing_command(self, text: str) -> bool:
        """
        Detect if user message is a command to process factory orders.
        
        Args:
            text: User message
            
        Returns:
            True if message is orders processing command
        """
        text_lower = text.lower()
        
        # Keywords for orders processing
        orders_keywords = [
            "procesa órdenes",
            "procesar órdenes",
            "procesa ordenes",
            "procesar ordenes",
            "revisa órdenes",
            "revisa ordenes",
            "órdenes pendientes",
            "ordenes pendientes",
            "órdenes nuevas",
            "ordenes nuevas",
            "ciclo de producción",
            "ciclo de produccion",
            "factory orders",
            "process orders",
            "check orders"
        ]
        
        return any(keyword in text_lower for keyword in orders_keywords)
    
    async def _handle_process_orders(self) -> ChatResponse:
        """
        Handle orders processing command by executing orchestrator.
        
        Returns:
            ChatResponse with formatted summary of processing results
        """
        logger.info("🏭 Executing Orders Orchestrator...")
        
        try:
            # Get orchestrator and DB session
            orchestrator = get_orchestrator_service()
            
            # Need to create session manually (can't use Depends here)
            from app.core.database import get_engine
            from sqlmodel import Session
            
            engine = get_engine()
            with Session(engine) as session:
                # Process pending orders
                results = await orchestrator.process_pending_orders(session)
            
            # Format results for chat
            if not results:
                message = """🏭 **Factory Orders - Procesamiento Completo**

📭 No hay órdenes pendientes (estado='nuevo') en este momento.

Todas las órdenes están en proceso o completadas."""
                
                return ChatResponse(
                    type="direct",
                    message=message,
                    provider="orders_orchestrator"
                )
            
            # Build summary
            success_count = len([r for r in results if not r.error])
            error_count = len([r for r in results if r.error])
            
            summary_lines = [
                "🏭 **Factory Orders - Procesamiento Completo**\n",
                f"📦 **Total procesadas:** {len(results)} orden(es)",
                f"✅ **Exitosas:** {success_count}",
                f"❌ **Con errores:** {error_count}\n"
            ]
            
            # Add details per order
            summary_lines.append("---\n")
            summary_lines.append("### Detalles por Orden\n")
            
            for result in results:
                if result.error:
                    summary_lines.append(
                        f"**{result.order_number}** - {result.nombre_producto}\n"
                        f"  - ❌ Error: {result.error}\n"
                    )
                else:
                    summary_lines.append(
                        f"**{result.order_number}** - {result.nombre_producto}\n"
                        f"  - Tipo: {result.tipo_producto}\n"
                        f"  - Estado: {result.old_status} → {result.new_status}\n"
                        f"  - Plan: {result.plan_summary}\n"
                    )
            
            summary_lines.append("\n---\n")
            summary_lines.append("✨ Todas las órdenes están ahora en planificación con planes generados por LLM.")
            
            message = "\n".join(summary_lines)
            
            return ChatResponse(
                type="direct",
                message=message,
                provider="orders_orchestrator"
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing orders: {e}")
            
            error_message = f"""🏭 **Factory Orders - Error**

❌ Ocurrió un error al procesar las órdenes:

```
{str(e)}
```

Por favor revisa los logs del sistema para más detalles."""
            
            return ChatResponse(
                type="direct",
                message=error_message,
                provider="orders_orchestrator"
            )


# Global singleton
_orchestrator_service: Optional[ChatOrchestrationService] = None


def get_chat_orchestrator() -> ChatOrchestrationService:
    """Get or create the global chat orchestrator instance."""
    global _orchestrator_service
    if _orchestrator_service is None:
        _orchestrator_service = ChatOrchestrationService()
    return _orchestrator_service
