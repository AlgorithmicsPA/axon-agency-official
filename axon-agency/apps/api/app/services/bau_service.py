"""BAU v1 (Build Automation Unit) - Automated order processing."""

import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import Session, select, or_
from sqlalchemy.orm import attributes
from loguru import logger

from app.models.orders import Order, OrderStatus
from app.services.orders_orchestrator import get_orchestrator_service
from app.services.axon_factory_client import get_axon_factory_client


def sanitize_bau_error(message: Optional[str]) -> Optional[str]:
    """
    Sanitize BAU error messages to prevent exposure of internal filesystem paths.
    
    Replaces absolute paths like /home/axon88/factory/products/... with generic
    high-level messages while maintaining functional context.
    
    Args:
        message: Original error message that may contain internal paths (can be None)
        
    Returns:
        Sanitized error message without filesystem paths (or None if input was None)
        
    Examples:
        >>> sanitize_bau_error("El producto ya existe en: /home/axon88/factory/products/ORD-2025-012")
        "El producto ya existe para esta orden"
        
        >>> sanitize_bau_error("Cannot retry build - no plan available")
        "Cannot retry build - no plan available"
    """
    if not message:
        return message
    
    # Pattern 1: "El producto ya existe en: /home/axon88/..." → generic message
    if "producto ya existe" in message.lower():
        return "El producto ya existe para esta orden"
    
    # Pattern 2: Generic path removal - replace /home/axon88/... with contextual text
    # Matches: /home/axon88/factory/products/ORD-YYYY-NNN_tipo or similar patterns
    path_pattern = r'/home/axon88/[^\s]+'
    if re.search(path_pattern, message):
        # Try to preserve context while removing path
        if "producto" in message.lower():
            sanitized = re.sub(path_pattern, "el directorio de productos", message)
        elif "log" in message.lower():
            sanitized = re.sub(path_pattern, "el log del sistema", message)
        else:
            sanitized = re.sub(path_pattern, "el directorio interno", message)
        return sanitized
    
    # Pattern 3: Remove other absolute paths (generic /home/*, /var/*, etc.)
    generic_path_pattern = r'/[a-zA-Z0-9_/.-]+'
    if re.search(generic_path_pattern, message):
        # Only sanitize if it looks like a filesystem path (contains multiple /)
        matches = re.findall(generic_path_pattern, message)
        sanitized = message
        for match in matches:
            if match.count('/') >= 2:  # At least /something/else
                sanitized = sanitized.replace(match, "[ruta interna]")
        # Return sanitized version if any paths were replaced
        if sanitized != message:
            return sanitized
    
    # No paths found - return original message
    return message


class BAUResult(BaseModel):
    """Result of BAU tick operation."""
    processed_total: int
    advanced_to_planificacion: int
    advanced_to_construccion: int
    errors: List[str]


class BAUService:
    """
    Build Automation Unit (BAU) v1.
    
    Automatically processes orders that need attention:
    - Orders in 'nuevo' state → generate plan + call Axon 88
    - Orders in 'planificacion' without product → retry Axon 88 build
    
    This is a thin layer on top of existing OrdersOrchestratorService
    and AxonFactoryClient.
    """
    
    def __init__(self):
        """Initialize BAU service."""
        self.orchestrator = get_orchestrator_service()
        self.axon_factory_client = get_axon_factory_client()
    
    async def tick(self, session: Session) -> BAUResult:
        """
        Execute one BAU tick: process all candidate orders.
        
        Candidate orders:
        1. estado='nuevo' → needs planning + building
        2. estado='planificacion' AND product_path=None → needs retry build
        
        Args:
            session: Database session
            
        Returns:
            BAUResult with processing metrics
        """
        logger.info("🤖 BAU v1: Starting automation tick...")
        
        # Find candidate orders
        candidates = session.exec(
            select(Order).where(
                or_(
                    Order.estado == OrderStatus.NUEVO.value,
                    (Order.estado == OrderStatus.PLANIFICACION.value) & (Order.product_path == None)
                )
            )
        ).all()
        
        if not candidates:
            logger.info("📭 BAU: No candidate orders found")
            return BAUResult(
                processed_total=0,
                advanced_to_planificacion=0,
                advanced_to_construccion=0,
                errors=[]
            )
        
        logger.info(f"📦 BAU: Found {len(candidates)} candidate order(s)")
        
        processed_total = 0
        advanced_to_planificacion = 0
        advanced_to_construccion = 0
        errors: List[str] = []
        
        for order in candidates:
            try:
                old_estado = order.estado
                
                if order.estado == OrderStatus.NUEVO.value:
                    # Process new order: generate plan + call Axon 88
                    logger.info(f"🆕 BAU: Processing new order {order.order_number}")
                    
                    # Reuse OrdersOrchestratorService logic
                    result = await self.orchestrator._process_single_order(session, order)
                    
                    if result.error:
                        sanitized_error = sanitize_bau_error(result.error)
                        errors.append(f"{order.order_number}: {sanitized_error}")
                    else:
                        processed_total += 1
                        if result.new_status == OrderStatus.PLANIFICACION.value:
                            advanced_to_planificacion += 1
                        elif result.new_status == OrderStatus.CONSTRUCCION.value:
                            advanced_to_construccion += 1
                    
                elif order.estado == OrderStatus.PLANIFICACION.value and order.product_path is None:
                    # Retry build for order with plan but no product
                    logger.info(f"🔄 BAU: Retrying build for {order.order_number} (planificacion without product)")
                    
                    if not order.plan:
                        error_msg = f"{order.order_number}: Cannot retry build - no plan available"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        continue
                    
                    # Call Axon 88 directly
                    build_result = await self.axon_factory_client.build_product(order, order.plan)
                    
                    if build_result.success:
                        # Update order with Axon 88 info
                        order.product_path = build_result.product_path
                        order.log_path = build_result.log_path
                        
                        # Parse construido_en timestamp
                        if build_result.construido_en:
                            try:
                                order.construido_en = datetime.fromisoformat(
                                    build_result.construido_en.replace('Z', '+00:00')
                                )
                            except (ValueError, AttributeError):
                                logger.warning(
                                    f"Invalid construido_en format from Axon 88: {build_result.construido_en}"
                                )
                                order.construido_en = datetime.utcnow()
                        else:
                            order.construido_en = datetime.utcnow()
                        
                        order.estado = OrderStatus.CONSTRUCCION.value
                        order.construccion_iniciada_at = datetime.utcnow()
                        order.updated_at = datetime.utcnow()
                        order.asignado_a = "Axon 88 Builder"
                        
                        # Add success log
                        build_log = {
                            "timestamp": datetime.utcnow().isoformat(),
                            "agente": "BAUService",
                            "mensaje": f"Construcción delegada a Axon 88 completada. Product path: {build_result.product_path}",
                            "tipo": "success"
                        }
                        
                        if order.logs is None:
                            order.logs = []
                        order.logs.append(build_log)
                        attributes.flag_modified(order, "logs")
                        
                        # Commit updates
                        session.add(order)
                        session.commit()
                        session.refresh(order)
                        
                        logger.success(f"✅ BAU: {order.order_number} → construccion")
                        processed_total += 1
                        advanced_to_construccion += 1
                        
                    else:
                        # Log error and leave order in planificacion
                        sanitized_log_message = sanitize_bau_error(build_result.error_message)
                        error_log = {
                            "timestamp": datetime.utcnow().isoformat(),
                            "agente": "BAUService",
                            "mensaje": f"Reintento de construcción falló: {sanitized_log_message}",
                            "tipo": "error"
                        }
                        
                        if order.logs is None:
                            order.logs = []
                        order.logs.append(error_log)
                        attributes.flag_modified(order, "logs")
                        
                        # Commit error log
                        session.add(order)
                        session.commit()
                        session.refresh(order)
                        
                        sanitized_error = sanitize_bau_error(build_result.error_message)
                        error_msg = f"{order.order_number}: Build retry failed - {sanitized_error}"
                        logger.warning(f"⚠️  {error_msg}")
                        errors.append(error_msg)
                        processed_total += 1
                
            except Exception as e:
                logger.error(f"❌ BAU: Error processing {order.order_number}: {e}")
                session.rollback()
                sanitized_error = sanitize_bau_error(str(e))
                errors.append(f"{order.order_number}: {sanitized_error}")
        
        logger.info(
            f"🏁 BAU tick complete: {processed_total} processed, "
            f"{advanced_to_planificacion} → planificacion, "
            f"{advanced_to_construccion} → construccion, "
            f"{len(errors)} errors"
        )
        
        return BAUResult(
            processed_total=processed_total,
            advanced_to_planificacion=advanced_to_planificacion,
            advanced_to_construccion=advanced_to_construccion,
            errors=errors
        )


# Singleton instance
_bau_service: Optional[BAUService] = None


def get_bau_service() -> BAUService:
    """Get singleton instance of BAUService."""
    global _bau_service
    if _bau_service is None:
        _bau_service = BAUService()
    return _bau_service
