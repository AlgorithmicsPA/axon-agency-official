"""Orders Orchestrator Service - Production director for AXON Factory orders."""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.orm import attributes
from loguru import logger

from app.models.orders import Order, OrderStatus
from app.services.llm_router import get_llm_router
from app.services.axon_factory_client import get_axon_factory_client
from app.core.database import get_session


class OrderProcessingResult(BaseModel):
    """Result of processing a single order."""
    order_id: str
    order_number: str
    tipo_producto: str
    nombre_producto: str
    old_status: str
    new_status: str
    plan_summary: str
    error: Optional[str] = None


class OrdersOrchestratorService:
    """
    Orders Orchestrator - Production director for AXON Factory.
    
    Responsibilities:
    - Monitor pending orders (estado='nuevo')
    - Generate production plans using LLM
    - Update order status and metadata
    - Coordinate with subagents (future: Builder, QA, etc.)
    """
    
    def __init__(self):
        """Initialize the orchestrator service."""
        self.llm_router = None
        self.axon_factory_client = get_axon_factory_client()
        
    async def initialize(self):
        """Initialize LLM router."""
        if self.llm_router is None:
            self.llm_router = get_llm_router()
            await self.llm_router.initialize()
    
    def _generate_plan_prompt(self, order: Order) -> str:
        """
        Generate LLM prompt for creating production plan.
        
        Args:
            order: Order instance with tipo_producto, datos_cliente, etc.
            
        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""Eres el PLANNER AGENT de AXON Factory. Tu misión es generar un PLAN DE PRODUCCIÓN para construir un autopilot.

**ORDEN RECIBIDA:**
- Order Number: {order.order_number}
- Tipo de Producto: {order.tipo_producto}
- Nombre: {order.nombre_producto}
- Prioridad: {order.prioridad}
- Tags: {', '.join(order.tags) if order.tags else 'ninguno'}

**DATOS DEL CLIENTE:**
```json
{json.dumps(order.datos_cliente, indent=2, ensure_ascii=False)}
```

**TU TAREA:**
Genera un plan de producción detallado en formato JSON con esta estructura:

```json
{{
  "tipo_autopilot": "{order.tipo_producto}",
  "resumen": "Descripción breve del autopilot a construir (2-3 líneas)",
  "fases": [
    {{
      "nombre": "Setup Inicial",
      "descripcion": "Configurar proyecto base, DB, estructura",
      "estimacion_horas": 2,
      "dependencias": [],
      "tareas": [
        "Crear estructura de proyecto",
        "Configurar base de datos",
        "Setup de autenticación"
      ]
    }},
    {{
      "nombre": "Integración Principal",
      "descripcion": "Integrar API principal (WhatsApp/Stripe/etc)",
      "estimacion_horas": 4,
      "dependencias": ["Setup Inicial"],
      "tareas": [
        "Configurar API client",
        "Implementar webhooks",
        "Testing de integración"
      ]
    }},
    {{
      "nombre": "Lógica de Negocio",
      "descripcion": "Implementar flujos específicos del cliente",
      "estimacion_horas": 6,
      "dependencias": ["Integración Principal"],
      "tareas": [
        "Flujo de conversación",
        "Reglas de negocio",
        "Persistencia de datos"
      ]
    }},
    {{
      "nombre": "QA y Deploy",
      "descripcion": "Testing completo y deployment",
      "estimacion_horas": 3,
      "dependencias": ["Lógica de Negocio"],
      "tareas": [
        "Tests automatizados",
        "Review Council (Security, Performance, QA)",
        "Deploy a producción"
      ]
    }}
  ],
  "stack_tecnologico": {{
    "backend": "FastAPI",
    "frontend": "Next.js",
    "database": "PostgreSQL",
    "integraciones": ["WhatsApp Business API", "Stripe", "etc"]
  }},
  "estimacion_total_horas": 15,
  "notas_especiales": "Consideraciones específicas basadas en datos del cliente"
}}
```

**REGLAS:**
1. Adapta las fases al tipo de producto ({order.tipo_producto})
2. Si datos_cliente incluye configuraciones específicas, refléjalas en el plan
3. Prioridad {order.prioridad} → ajusta estimaciones (urgente=más recursos, baja=menos presión)
4. Incluye SIEMPRE fase de QA y Deploy al final
5. Las tareas deben ser ESPECÍFICAS y ACCIONABLES
6. Estima realísticamente según complejidad

**OUTPUT:**
Devuelve SOLO el JSON del plan, sin markdown, sin explicaciones adicionales."""

        return prompt
    
    async def _generate_plan(self, order: Order) -> Dict[str, Any]:
        """
        Generate production plan for an order using LLM.
        
        Args:
            order: Order instance
            
        Returns:
            Generated plan as dictionary
        """
        if not self.llm_router:
            await self.initialize()
        
        prompt = self._generate_plan_prompt(order)
        
        try:
            # Use LLM router with fallback chain (Gemini → OpenAI → Ollama)
            # TaskType.CODE_GENERATION for structured output (JSON)
            response = await self.llm_router.route_and_execute(
                prompt=prompt,
                task_type=None,  # Let router auto-classify
                context={
                    "task_type": "code_generation",  # Hint for structured JSON output
                    "temperature": 0.3  # Low temperature for consistency
                }
            )
            
            # Extract JSON from response
            content = response.content.strip()
            
            # Try to find JSON in response (handle markdown code blocks)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            plan = json.loads(content)
            
            logger.info(f"✅ Plan generado para orden {order.order_number}")
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing JSON del plan para {order.order_number}: {e}")
            # Fallback: crear plan básico
            return {
                "tipo_autopilot": order.tipo_producto,
                "resumen": f"Plan básico para {order.nombre_producto}",
                "fases": [
                    {
                        "nombre": "Planificación",
                        "descripcion": "Diseño inicial",
                        "estimacion_horas": 2,
                        "dependencias": [],
                        "tareas": ["Analizar requerimientos", "Diseñar arquitectura"]
                    },
                    {
                        "nombre": "Construcción",
                        "descripcion": "Desarrollo del autopilot",
                        "estimacion_horas": 8,
                        "dependencias": ["Planificación"],
                        "tareas": ["Implementar backend", "Implementar frontend", "Integraciones"]
                    },
                    {
                        "nombre": "QA y Deploy",
                        "descripcion": "Testing y deployment",
                        "estimacion_horas": 3,
                        "dependencias": ["Construcción"],
                        "tareas": ["Tests", "Review Council", "Deploy"]
                    }
                ],
                "estimacion_total_horas": 13,
                "notas_especiales": "Plan generado automáticamente (LLM parsing failed)"
            }
        except Exception as e:
            logger.error(f"❌ Error generando plan para {order.order_number}: {e}")
            raise
    
    async def _process_single_order(self, session: Session, order: Order) -> OrderProcessingResult:
        """
        Process a single order: generate plan, call Axon 88, update state.
        
        This method can be reused by BAUService and other components.
        
        Args:
            session: Database session
            order: Order instance to process
            
        Returns:
            OrderProcessingResult with processing outcome
        """
        await self.initialize()
        
        logger.info(f"⚙️  Processing {order.order_number}: {order.nombre_producto}")
        
        old_status = order.estado
        
        try:
            # Generate production plan
            plan = await self._generate_plan(order)
            
            # Update order
            order.plan = plan
            order.estado = OrderStatus.PLANIFICACION.value
            order.planificado_at = datetime.utcnow()
            order.updated_at = datetime.utcnow()
            order.asignado_a = "Orders Orchestrator"
            
            # Add log entry
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "agente": "Orders Orchestrator",
                "mensaje": f"Plan de producción generado. Estimación: {plan.get('estimacion_total_horas', 'N/A')} horas",
                "tipo": "success"
            }
            
            if order.logs is None:
                order.logs = []
            order.logs.append(log_entry)
            attributes.flag_modified(order, "logs")
            
            # Commit changes (save plan to DB)
            session.add(order)
            session.commit()
            session.refresh(order)
            
            # AXON 88 FACTORY INTEGRATION - Delegate construction to local factory
            logger.info(f"🏭 Requesting build in Axon 88 for {order.order_number}")
            # FASE 3.B: Pass agent_blueprint to Axon 88 (optional, backward compatible)
            build_result = await self.axon_factory_client.build_product(
                order, 
                plan,
                agent_blueprint=order.agent_blueprint
            )
            
            if build_result.success:
                # Update order with Axon 88 factory info
                order.product_path = build_result.product_path
                order.log_path = build_result.log_path
                
                # Parse construido_en from Axon 88 (ISO string) or use current time as fallback
                if build_result.construido_en:
                    try:
                        order.construido_en = datetime.fromisoformat(build_result.construido_en.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        logger.warning(f"Invalid construido_en format from Axon 88: {build_result.construido_en}")
                        order.construido_en = datetime.utcnow()
                else:
                    order.construido_en = datetime.utcnow()
                
                order.estado = OrderStatus.CONSTRUCCION.value
                order.construccion_iniciada_at = datetime.utcnow()
                order.updated_at = datetime.utcnow()
                order.asignado_a = "Axon 88 Builder"
                
                # BUILDER V2 - Persist QA + Deliverable if present
                if build_result.qa:
                    order.qa_status = build_result.qa.get("status")
                    order.qa_messages = build_result.qa.get("messages", [])
                    order.qa_checked_files = build_result.qa.get("checked_files", [])
                    order.qa_ejecutado_en = datetime.utcnow()
                    
                    # Logic de estados basada en QA status:
                    # - ok → listo (skip manual QA)
                    # - warn/fail → qa (requires manual review)
                    if build_result.qa.get("status") == "ok":
                        order.estado = OrderStatus.LISTO.value
                        order.progreso = 100
                        logger.info(f"✅ {order.order_number} → QA passed, marked as 'listo'")
                    elif build_result.qa.get("status") in ["warn", "fail"]:
                        order.estado = OrderStatus.QA.value
                        order.qa_iniciada_at = datetime.utcnow()
                        logger.warning(f"⚠️ {order.order_number} → QA {build_result.qa.get('status')}, requires review")

                if build_result.deliverable_dir:
                    order.deliverable_generado = True
                    order.deliverable_metadata = {
                        "order_number": order.order_number,
                        "tipo_producto": order.tipo_producto,
                        "qa_status": order.qa_status,
                        "construido_en": build_result.construido_en,
                        "archivos": ["SUMMARY.md", "meta.json", f"{order.order_number}_{order.tipo_producto}.zip"]
                    }
                    order.deliverable_generado_en = datetime.utcnow()
                    logger.info(f"📦 {order.order_number} → Deliverable generated")
                
                # Add success log with Builder v2 info (NO internal paths)
                mensaje_base = "Construcción delegada exitosamente en Axon 88 Builder"
                if build_result.qa:
                    mensaje_base += f" | QA: {build_result.qa.get('status')}"
                if build_result.deliverable_dir:
                    mensaje_base += f" | Deliverable: ✓"
                
                build_log = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "agente": "Axon 88 Builder",
                    "mensaje": mensaje_base,
                    "tipo": "success"
                }
                order.logs.append(build_log)
                attributes.flag_modified(order, "logs")
                
                # Commit Axon 88 updates
                session.add(order)
                session.commit()
                session.refresh(order)
                
                logger.success(f"✅ {order.order_number} → construccion en Axon 88")
                
            else:
                # Log failure but don't break the flow
                error_log = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "agente": "Axon 88 Builder",
                    "mensaje": f"Fallo al delegar construcción: {build_result.error_message}",
                    "tipo": "error"
                }
                order.logs.append(error_log)
                attributes.flag_modified(order, "logs")
                
                # Revert state to original when Axon 88 fails
                order.estado = old_status
                order.asignado_a = None
                session.add(order)
                session.commit()
                session.refresh(order)
                
                logger.warning(
                    f"⚠️  {order.order_number} - Axon 88 build failed: {build_result.error_message}. "
                    f"Order reverted to '{old_status}' state."
                )
            
            # Create result summary
            plan_summary = f"{plan.get('resumen', 'Plan generado')} | Fases: {len(plan.get('fases', []))} | Est: {plan.get('estimacion_total_horas', 'N/A')}h"
            
            result = OrderProcessingResult(
                order_id=order.id,
                order_number=order.order_number,
                tipo_producto=order.tipo_producto,
                nombre_producto=order.nombre_producto,
                old_status=old_status,
                new_status=order.estado,
                plan_summary=plan_summary
            )
            
            logger.info(f"✅ {order.order_number} → {order.estado}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing {order.order_number}: {e}")
            
            # Rollback session to restore clean state
            session.rollback()
            
            # Return error result
            return OrderProcessingResult(
                order_id=order.id,
                order_number=order.order_number,
                tipo_producto=order.tipo_producto,
                nombre_producto=order.nombre_producto,
                old_status=old_status,
                new_status=old_status,
                plan_summary="",
                error=str(e)
            )
    
    async def process_pending_orders(self, session: Session) -> List[OrderProcessingResult]:
        """
        Process all pending orders (estado='nuevo').
        
        For each order:
        1. Generate production plan using LLM
        2. Update order: plan, estado='planificacion', planificado_at
        3. Call Axon 88 to build product
        4. Update order with product_path, log_path, construido_en
        
        Args:
            session: Database session
            
        Returns:
            List of processing results
        """
        await self.initialize()
        
        logger.info("🏭 Orders Orchestrator: Starting order processing cycle...")
        
        # Query orders with estado='nuevo'
        query = select(Order).where(Order.estado == OrderStatus.NUEVO.value)
        pending_orders = session.exec(query).all()
        
        if not pending_orders:
            logger.info("📭 No pending orders found (estado='nuevo')")
            return []
        
        logger.info(f"📦 Found {len(pending_orders)} pending order(s)")
        
        results: List[OrderProcessingResult] = []
        
        for order in pending_orders:
            result = await self._process_single_order(session, order)
            results.append(result)
        
        logger.info(f"🏁 Order processing complete: {len(results)} order(s) processed")
        return results


# Singleton instance
_orchestrator_service: Optional[OrdersOrchestratorService] = None


def get_orchestrator_service() -> OrdersOrchestratorService:
    """Get singleton instance of OrdersOrchestratorService."""
    global _orchestrator_service
    if _orchestrator_service is None:
        _orchestrator_service = OrdersOrchestratorService()
    return _orchestrator_service
