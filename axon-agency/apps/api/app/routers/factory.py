"""Factory info endpoint - expone modo y capacidades de la fábrica."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List

from app.core.config import settings
from app.core.database import get_session
from app.models.orders import Order
from app.services.orders_orchestrator import get_orchestrator_service, OrderProcessingResult
from app.services.bau_service import get_bau_service, BAUResult

router = APIRouter()


class FactoryInfo(BaseModel):
    """Información de la fábrica AXON."""
    mode: str
    version: str
    features: dict
    axon88_connection: dict
    products_available: list[str]


@router.get("/info")
async def get_factory_info() -> FactoryInfo:
    """
    Obtener información sobre el modo y capacidades de la fábrica.
    
    Este endpoint expone:
    - Modo de operación (factory_private)
    - Features habilitadas
    - Estado de conexión con Axon 88
    - Tipos de productos disponibles para construcción
    
    Returns:
        FactoryInfo: Información completa de la fábrica
    """
    return FactoryInfo(
        mode="factory_private",
        version="1.0.0",
        features={
            "chat": True,
            "autonomous_agent": True,
            "rag": True,
            "code_playground": True,
            "self_improvement": True,
            "review_council": True,
            "multi_llm_routing": True,
            "builder_agent": False,  # Planeado, no implementado
            "orders_api": True,  # ✅ Implementado
        },
        axon88_connection={
            "enabled": settings.axon_core_enabled,
            "url": settings.axon_core_api_base,
            "status": "configured" if settings.axon_core_api_token else "no_token",
        },
        products_available=[
            "autopilot_whatsapp",
            "autopilot_ventas",
            "webhook_service",
        ]
    )


class ProcessOrdersResponse(BaseModel):
    """Respuesta del procesamiento de órdenes."""
    processed_count: int
    orders: List[OrderProcessingResult]
    message: str


@router.post("/process-orders", response_model=ProcessOrdersResponse)
async def process_pending_orders(
    session: Session = Depends(get_session)
):
    """
    Procesar órdenes pendientes (estado='nuevo').
    
    Este endpoint:
    - Lee todas las órdenes con estado='nuevo'
    - Genera plan de producción con LLM para cada orden
    - Actualiza estado a 'planificacion' y setea planificado_at
    - Agrega log entry con detalles del plan
    
    Uso interno: Para disparar manualmente el ciclo de producción o desde
    automatizaciones (n8n, cron, etc.).
    
    Returns:
        ProcessOrdersResponse: Resumen del procesamiento con lista de órdenes procesadas
    """
    orchestrator = get_orchestrator_service()
    results = await orchestrator.process_pending_orders(session)
    
    return ProcessOrdersResponse(
        processed_count=len(results),
        orders=results,
        message=f"Procesadas {len(results)} orden(es). Ver detalles en 'orders'."
    )


class BAUTickResponse(BaseModel):
    """Respuesta del tick de BAU (Build Automation Unit)."""
    status: str
    processed_total: int
    advanced_to_planificacion: int
    advanced_to_construccion: int
    errors: List[str]


@router.post("/bau-tick", response_model=BAUTickResponse)
async def bau_automation_tick(
    session: Session = Depends(get_session)
):
    """
    BAU v1 - Build Automation Unit tick.
    
    Procesa automáticamente órdenes que necesitan atención:
    - Estado 'nuevo' → genera plan + llama Axon 88
    - Estado 'planificacion' sin product_path → reintenta construcción en Axon 88
    
    Este endpoint es una capa delgada encima de OrdersOrchestratorService
    y AxonFactoryClient. Diseñado para ser llamado manualmente o por
    automatizaciones (n8n, cron).
    
    Returns:
        BAUTickResponse: Métricas del tick (órdenes procesadas, transiciones, errores)
    """
    bau = get_bau_service()
    result = await bau.tick(session)
    
    return BAUTickResponse(
        status="ok",
        processed_total=result.processed_total,
        advanced_to_planificacion=result.advanced_to_planificacion,
        advanced_to_construccion=result.advanced_to_construccion,
        errors=result.errors
    )


class QAStatusResponse(BaseModel):
    """Respuesta del endpoint de QA status."""
    order_id: str
    order_number: str
    qa_executed: bool
    qa_status: str | None = None
    qa_messages: list[str] | None = None
    qa_checked_files: list[str] | None = None
    qa_ejecutado_en: str | None = None


@router.get("/orders/{order_id}/qa", response_model=QAStatusResponse)
async def get_order_qa_status(
    order_id: str,
    session: Session = Depends(get_session)
):
    """
    Obtener estado del QA check de una orden.
    
    Retorna información sobre la validación de calidad ejecutada por Axon 88 Builder v2:
    - qa_status: ok (passed), warn (warnings), fail (failed), null (no ejecutado)
    - qa_messages: Mensajes descriptivos del QA
    - qa_checked_files: Lista de archivos validados
    - qa_ejecutado_en: Timestamp de ejecución
    
    Args:
        order_id: ID de la orden
        
    Returns:
        QAStatusResponse: Estado del QA check
        
    Raises:
        HTTPException 404: Si la orden no existe
    """
    statement = select(Order).where(Order.id == order_id)
    order = session.exec(statement).first()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    qa_executed = order.qa_status is not None
    
    return QAStatusResponse(
        order_id=order.id,
        order_number=order.order_number,
        qa_executed=qa_executed,
        qa_status=order.qa_status,
        qa_messages=order.qa_messages,
        qa_checked_files=order.qa_checked_files,
        qa_ejecutado_en=order.qa_ejecutado_en.isoformat() if order.qa_ejecutado_en else None
    )


class DeliverableResponse(BaseModel):
    """Respuesta del endpoint de deliverable."""
    order_id: str
    order_number: str
    deliverable_generado: bool
    deliverable_metadata: dict | None = None
    deliverable_generado_en: str | None = None


@router.get("/orders/{order_id}/deliverable", response_model=DeliverableResponse)
async def get_order_deliverable(
    order_id: str,
    session: Session = Depends(get_session)
):
    """
    Obtener información del deliverable de una orden.
    
    Retorna metadata del paquete de entrega generado por Axon 88 Builder v2:
    - archivos: Lista de archivos incluidos (SUMMARY.md, meta.json, ZIP)
    - qa_status: Estado del QA asociado
    - construido_en: Timestamp de construcción
    
    IMPORTANTE: Este endpoint NO expone rutas internas de Axon 88 (/home/axon88/...),
    solo metadata pública para el cliente.
    
    Args:
        order_id: ID de la orden
        
    Returns:
        DeliverableResponse: Información del deliverable
        
    Raises:
        HTTPException 404: Si la orden no existe
    """
    statement = select(Order).where(Order.id == order_id)
    order = session.exec(statement).first()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    return DeliverableResponse(
        order_id=order.id,
        order_number=order.order_number,
        deliverable_generado=order.deliverable_generado,
        deliverable_metadata=order.deliverable_metadata,
        deliverable_generado_en=order.deliverable_generado_en.isoformat() if order.deliverable_generado_en else None
    )
