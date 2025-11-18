"""Orders API router for AXON Factory."""

import logging
import uuid
import httpx
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select, func
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timezone
import asyncio

from app.core.database import get_session
from app.core.security import get_current_user, get_user_from_token, TokenData, require_admin
from app.core.config import settings
from app.models.orders import (
    Order, OrderCreate, OrderUpdate, OrderResponse, OrderDetailResponse,
    OrderStatus, ProductType, DeployEvent, DeployEventCreate
)
from app.models.tenants import Tenant
from app.integrations.ayrshare_client import post_to_social, AyrshareError
from app.integrations.telegram_client import send_to_telegram, TelegramError

router = APIRouter()
logger = logging.getLogger(__name__)


def generate_order_number(session: Session) -> str:
    """
    Generar order_number único con protección contra race conditions.
    
    Usa MAX(order_number) + 1 con retry logic para evitar duplicados.
    """
    year = datetime.utcnow().year
    prefix = f"ORD-{year}-"
    
    # Obtener el máximo número de orden del año actual
    max_order_query = select(
        func.max(Order.order_number)
    ).where(
        Order.order_number.like(f"{prefix}%")
    )
    max_order = session.exec(max_order_query).one()
    
    if max_order:
        # Extraer el número del formato ORD-YYYY-NNN
        last_num = int(max_order.split('-')[-1])
        next_num = last_num + 1
    else:
        next_num = 1
    
    return f"{prefix}{next_num:03d}"


def verify_order_access(order: Order, current_user: TokenData, session: Session) -> None:
    """
    Verificar que el usuario tiene acceso a esta orden.
    
    Reglas de acceso:
    - Admin: puede acceder a cualquier orden
    - Tenant user: solo puede acceder a órdenes de su tenant
    - Legacy user (sin tenant): solo puede acceder a órdenes sin tenant
    
    Raises HTTPException si no tiene acceso.
    """
    user = get_user_from_token(current_user, session)
    
    # Admin tiene acceso a todo
    if user.role == "admin":
        return
    
    # Tenant user: solo puede acceder a órdenes de su tenant
    if user.tenant_id:
        if order.tenant_id != user.tenant_id:
            logger.warning(f"User {user.username} (tenant {user.tenant_id}) attempted to access order {order.id} from tenant {order.tenant_id}")
            raise HTTPException(
                status_code=403,
                detail="You don't have access to this order"
            )
        return
    
    # Legacy user (sin tenant): solo puede acceder a órdenes sin tenant
    if order.tenant_id is not None:
        logger.warning(f"Legacy user {user.username} attempted to access tenant order {order.id}")
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this order"
        )
    
    # Legacy user accediendo a orden legacy - permitido
    return


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session)
):
    """
    Crear nueva orden de autopilot.
    
    Genera un order_number único (ORD-YYYY-NNN) y crea la orden con estado 'nuevo'.
    """
    # Validar tipo_producto usando enum
    try:
        ProductType(order_data.tipo_producto)
    except ValueError:
        valid_products = [p.value for p in ProductType]
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de producto no válido. Opciones: {', '.join(valid_products)}"
        )
    
    # Generar order_number con retry logic para evitar race conditions
    max_retries = 3
    for attempt in range(max_retries):
        try:
            order_number = generate_order_number(session)
            
            order = Order(
                order_number=order_number,
                tipo_producto=order_data.tipo_producto,
                nombre_producto=order_data.nombre_producto,
                datos_cliente=order_data.datos_cliente,
                tenant_id=order_data.tenant_id,
                prioridad=order_data.prioridad,
                tags=order_data.tags,
                estado=OrderStatus.NUEVO.value,
                progreso=0
            )
            
            session.add(order)
            session.commit()
            session.refresh(order)
            
            return order
            
        except IntegrityError:
            session.rollback()
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=500,
                    detail="Error generando número de orden único. Intente nuevamente."
                )
            await asyncio.sleep(0.1)  # Pequeño delay async antes de reintentar


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    estado: Optional[str] = None,
    tipo_producto: Optional[str] = None,
    tenant_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Listar órdenes con filtros opcionales.
    
    Aplica filtrado automático por tenant según el rol del usuario:
    - Admin: puede ver todas las órdenes o filtrar por tenant_id
    - Tenant-bound user: solo ve órdenes de su propio tenant
    - Legacy user (sin tenant): solo ve órdenes sin tenant (tenant_id IS NULL)
    
    Parámetros:
    - estado: filtrar por estado (nuevo, planificacion, construccion, qa, listo, entregado)
    - tipo_producto: filtrar por tipo
    - tenant_id: filtrar por tenant (solo aplica para admins)
    - limit: número máximo de resultados
    - offset: para paginación
    """
    user = get_user_from_token(current_user, session)
    
    statement = select(Order)
    
    if estado:
        statement = statement.where(Order.estado == estado)
    if tipo_producto:
        statement = statement.where(Order.tipo_producto == tipo_producto)
    
    if user.role == "admin":
        if tenant_id is not None:
            statement = statement.where(Order.tenant_id == tenant_id)
    else:
        if user.tenant_id:
            effective_tenant_id = user.tenant_id
            
            if tenant_id is not None and tenant_id != effective_tenant_id:
                logger.info(f"User {user.username} attempted to access tenant {tenant_id}, overriding to {effective_tenant_id}")
                tenant_id = effective_tenant_id
            
            logger.info(f"User {user.username} (tenant {effective_tenant_id}) filtering orders")
            statement = statement.where(Order.tenant_id == effective_tenant_id)
        else:
            # Legacy user (sin tenant): solo puede acceder a órdenes sin tenant
            logger.info(f"Legacy user {user.username} filtering orders (tenant_id IS NULL)")
            statement = statement.where(Order.tenant_id == None)
    
    statement = statement.order_by(Order.created_at.desc()).offset(offset).limit(limit)
    
    orders = session.exec(statement).all()
    return orders


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: str,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Obtener información completa de una orden.
    
    Incluye: datos_cliente, plan, logs, progreso, timestamps, etc.
    
    Tenant scoping:
    - Admin: puede ver cualquier orden
    - Tenant user: solo puede ver órdenes de su tenant
    - Legacy user: solo puede ver órdenes sin tenant
    """
    order = session.get(Order, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Orden {order_id} no encontrada")
    
    # Verificar acceso según tenant
    verify_order_access(order, current_user, session)
    
    # Check if Ayrshare integration is enabled (both API key AND feature flag must be enabled)
    ayrshare_enabled = (
        settings.enable_ayrshare_social and
        bool(settings.ayrshare_api_key and settings.ayrshare_api_key.strip())
    )
    
    # Convert Order model to OrderDetailResponse with ayrshare_enabled flag
    order_dict = order.dict()
    order_dict['ayrshare_enabled'] = ayrshare_enabled
    
    return OrderDetailResponse(**order_dict)


@router.get("/{order_id}/result")
async def get_order_result(
    order_id: str,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Obtener producto entregado (solo si estado = 'listo' o 'entregado').
    
    Devuelve URLs, credenciales, documentación del autopilot.
    
    Tenant scoping:
    - Admin: puede ver cualquier orden
    - Tenant user: solo puede ver órdenes de su tenant
    - Legacy user: solo puede ver órdenes sin tenant
    """
    order = session.get(Order, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Orden {order_id} no encontrada")
    
    # Verificar acceso según tenant
    verify_order_access(order, current_user, session)
    
    if order.estado not in ["listo", "entregado"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Producto aún no está listo",
                "estado_actual": order.estado,
                "progreso": order.progreso,
                "mensaje": f"El autopilot está en {order.estado}. Revisa el estado en /api/orders/{order_id}"
            }
        )
    
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "estado": order.estado,
        "resultado": order.resultado,
        "repo_url": order.repo_url,
        "deploy_url": order.deploy_url,
        "entregado_at": order.entregado_at
    }


@router.patch("/{order_id}", response_model=OrderDetailResponse)
async def update_order(
    order_id: str,
    update_data: OrderUpdate,
    session: Session = Depends(get_session)
):
    """
    Actualizar estado/progreso de orden (uso interno para agentes).
    
    Permite actualizar: estado, progreso, logs, plan, asignado_a, resultado, etc.
    Estados válidos y timestamps automáticos:
    - planificacion → planificado_at
    - construccion → construccion_iniciada_at
    - qa → qa_iniciada_at
    - entregado → entregado_at
    """
    order = session.get(Order, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Orden {order_id} no encontrada")
    
    # Actualizar campos (el estado ya viene validado por el enum OrderStatus en OrderUpdate)
    update_dict = update_data.dict(exclude_unset=True)
    
    for key, value in update_dict.items():
        # Convertir enum a string para estado
        if key == 'estado' and value is not None:
            setattr(order, key, value.value if isinstance(value, OrderStatus) else value)
        else:
            setattr(order, key, value)
    
    # Actualizar timestamp general
    order.updated_at = datetime.utcnow()
    
    # Actualizar timestamps específicos según estado
    if update_data.estado:
        estado_value = update_data.estado.value if isinstance(update_data.estado, OrderStatus) else update_data.estado
        
        if estado_value == OrderStatus.PLANIFICACION.value and not order.planificado_at:
            order.planificado_at = datetime.utcnow()
        elif estado_value == OrderStatus.CONSTRUCCION.value and not order.construccion_iniciada_at:
            order.construccion_iniciada_at = datetime.utcnow()
        elif estado_value == OrderStatus.QA.value and not order.qa_iniciada_at:
            order.qa_iniciada_at = datetime.utcnow()
        elif estado_value == OrderStatus.ENTREGADO.value and not order.entregado_at:
            order.entregado_at = datetime.utcnow()
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order


@router.post("/{order_id}/deploy/whatsapp")
async def deploy_to_whatsapp(
    order_id: str,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(require_admin)
):
    """
    Deploy orden WhatsApp Autopilot a n8n para activación.
    
    FASE 9.1 - WhatsApp Autopilot Deploy Layer
    
    Validaciones:
    - Usuario debe ser admin
    - Orden debe existir
    - tipo_producto debe ser compatible con WhatsApp
    - estado debe ser "listo"
    - qa_status debe ser "ok" (si existe)
    - N8N_WHATSAPP_DEPLOY_WEBHOOK_URL debe estar configurado
    
    Proceso:
    1. Validar pre-condiciones
    2. Construir payload con tenant, order, agent_blueprint, deliverable
    3. POST HTTP a webhook n8n
    4. Registrar evento en deploy_history
    5. Retornar respuesta
    
    Returns:
        {
            "status": "ok",
            "message": "Deploy request sent to n8n",
            "deploy_event": {...}
        }
    """
    # Validar que la orden existe
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validar que es una orden compatible con WhatsApp
    if "whatsapp" not in order.tipo_producto.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order is not a WhatsApp-compatible product (tipo_producto: {order.tipo_producto})"
        )
    
    # Validar que está en estado listo
    if order.estado != "listo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order must be in 'listo' state to deploy (current: '{order.estado}')"
        )
    
    # Validar QA status si existe
    if order.qa_status and order.qa_status != "ok":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order must pass QA before deploy (current qa_status: '{order.qa_status}')"
        )
    
    # Verificar que el webhook está configurado
    if not settings.n8n_whatsapp_deploy_webhook_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deploy unavailable: N8N_WHATSAPP_DEPLOY_WEBHOOK_URL not configured"
        )
    
    # Obtener datos del tenant si existe
    tenant_data = None
    if order.tenant_id:
        tenant = session.get(Tenant, order.tenant_id)
        if tenant:
            tenant_data = {
                "id": tenant.id,
                "slug": tenant.slug,
                "nombre": tenant.name
            }
    
    # Construir artifacts del deliverable
    deliverable_artifacts = []
    if order.deliverable_metadata and order.deliverable_metadata.get("archivos"):
        for archivo in order.deliverable_metadata["archivos"]:
            # Solo rutas relativas, sin rutas absolutas del filesystem
            artifact = {
                "path": archivo,
                "type": "unknown"
            }
            
            # Inferir tipo del archivo
            if "flow" in archivo.lower() or archivo.endswith(".json"):
                artifact["type"] = "n8n_workflow"
            elif "config" in archivo.lower() or archivo.endswith((".yaml", ".yml")):
                artifact["type"] = "configuration"
            elif "prompt" in archivo.lower() or archivo.endswith(".txt"):
                artifact["type"] = "prompt"
            
            deliverable_artifacts.append(artifact)
    
    # Construir payload para n8n
    payload = {
        "tenant": tenant_data,
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "tipo_producto": order.tipo_producto,
            "nombre_producto": order.nombre_producto,
            "estado": order.estado,
            "datos_cliente": order.datos_cliente
        },
        "agent_blueprint": order.agent_blueprint,
        "deliverable": {
            "metadata": order.deliverable_metadata,
            "artifacts": deliverable_artifacts
        }
    }
    
    # Crear evento de deploy
    deploy_event_data = {
        "id": str(uuid.uuid4()),
        "order_id": order.id,
        "channel": "whatsapp",
        "target_system": "n8n",
        "status": "pending",
        "requested_at": datetime.utcnow(),
        "webhook_url": settings.n8n_whatsapp_deploy_webhook_url[:50] + "..."  # Sanitizado
    }
    
    # Intentar enviar a n8n
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"Deploying order {order.order_number} to n8n WhatsApp webhook")
            
            response = await client.post(
                settings.n8n_whatsapp_deploy_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            deploy_event_data["response_status"] = response.status_code
            
            if response.status_code >= 400:
                # Webhook retornó error
                deploy_event_data["status"] = "failed"
                error_text = response.text[:200] if response.text else "No response body"
                deploy_event_data["error_message"] = f"Webhook returned {response.status_code}: {error_text}"
                deploy_event_data["completed_at"] = datetime.utcnow()
                
                logger.error(f"n8n webhook error: {deploy_event_data['error_message']}")
            else:
                # Deploy exitoso
                deploy_event_data["status"] = "success"
                deploy_event_data["completed_at"] = datetime.utcnow()
                
                logger.info(f"Order {order.order_number} deployed successfully to n8n")
    
    except httpx.TimeoutException:
        deploy_event_data["status"] = "failed"
        deploy_event_data["error_message"] = "Webhook request timeout (30s)"
        deploy_event_data["completed_at"] = datetime.utcnow()
        
        logger.error(f"n8n webhook timeout for order {order.order_number}")
    
    except Exception as e:
        deploy_event_data["status"] = "failed"
        deploy_event_data["error_message"] = f"Webhook error: {str(e)[:200]}"
        deploy_event_data["completed_at"] = datetime.utcnow()
        
        logger.error(f"n8n webhook exception for order {order.order_number}: {str(e)}")
    
    # Registrar evento en deploy_history
    if order.deploy_history is None:
        order.deploy_history = []
    
    order.deploy_history.append(deploy_event_data)
    order.updated_at = datetime.utcnow()
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Determinar respuesta según status
    if deploy_event_data["status"] == "success":
        return {
            "status": "ok",
            "message": "Deploy request sent to n8n successfully",
            "deploy_event": deploy_event_data
        }
    else:
        # Deploy falló pero fue registrado
        return {
            "status": "error",
            "message": f"Deploy failed: {deploy_event_data.get('error_message', 'Unknown error')}",
            "deploy_event": deploy_event_data
        }


@router.post("/{order_id}/deploy/social")
async def deploy_to_social(
    order_id: str,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(require_admin)
):
    """
    Deploy orden Social Autopilot a Ayrshare para publicación en redes sociales.
    
    FASE 9.S - Social Autopilot Deploy via Ayrshare
    
    Validaciones:
    - Usuario debe ser admin
    - Orden debe existir
    - tipo_producto debe contener "social"
    - estado debe ser "listo"
    - qa_status debe ser "ok" (si existe)
    - AYRSHARE_API_KEY debe estar configurado
    
    Proceso:
    1. Validar pre-condiciones
    2. Extraer contenido (texto, plataformas, media)
    3. POST HTTP a Ayrshare API
    4. Registrar evento en deploy_history
    5. Retornar respuesta
    
    Returns:
        {
            "status": "ok",
            "message": "Social deploy sent to Ayrshare successfully",
            "deploy_event": {...}
        }
    """
    # Validar que la orden existe
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validar que es una orden compatible con Social
    if "social" not in order.tipo_producto.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order is not a Social-compatible product (tipo_producto: {order.tipo_producto})"
        )
    
    # Validar que está en estado listo
    if order.estado != "listo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order must be in 'listo' state to deploy (current: '{order.estado}')"
        )
    
    # Validar QA status si existe
    if order.qa_status and order.qa_status != "ok":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order must pass QA before deploy (current qa_status: '{order.qa_status}')"
        )
    
    # Verificar que el API key está configurado
    if not settings.ayrshare_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deploy unavailable: AYRSHARE_API_KEY not configured"
        )
    
    # Extraer texto del post (prioridad: deliverable_metadata > agent_blueprint > fallback)
    post_text = None
    if order.deliverable_metadata and order.deliverable_metadata.get("social_post_text"):
        post_text = order.deliverable_metadata["social_post_text"]
    elif order.agent_blueprint and order.agent_blueprint.get("notes"):
        post_text = order.agent_blueprint["notes"]
    else:
        post_text = f"Nuevo autopilot disponible: {order.nombre_producto}"
    
    # Plataformas default
    platforms = ["twitter", "facebook", "instagram"]
    
    # Extraer media URLs si existen
    media_urls = []
    if order.deliverable_metadata and order.deliverable_metadata.get("archivos"):
        for archivo in order.deliverable_metadata["archivos"]:
            # Solo URLs públicas permitidas
            if archivo.startswith("http") and any(archivo.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif"]):
                media_urls.append(archivo)
    
    # Crear evento de deploy
    deploy_event_data = {
        "id": str(uuid.uuid4()),
        "order_id": order.id,
        "channel": "social",
        "target_system": "ayrshare",
        "status": "pending",
        "requested_at": datetime.utcnow(),
        "platforms": platforms
    }
    
    # Intentar enviar a Ayrshare
    try:
        logger.info(f"Deploying order {order.order_number} to Ayrshare social platforms")
        
        ayrshare_response = await post_to_social(
            api_key=settings.ayrshare_api_key,
            base_url=settings.ayrshare_base_url,
            text=post_text,
            platforms=platforms,
            media_urls=media_urls if media_urls else None,
            schedule_iso=None,
            profile_key=None
        )
        
        # Parse platform-specific results from Ayrshare response
        platform_results = {}
        
        # Mark successful platforms from postIds array
        if ayrshare_response.get("postIds"):
            for post_id in ayrshare_response["postIds"]:
                # Extract platform from postId prefix (e.g., "twitter-123" → "twitter")
                platform = post_id.split("-")[0].lower() if "-" in post_id else None
                if platform in platforms:
                    platform_results[platform] = "success"
        
        # Mark failed platforms from errors array
        error_messages = []
        if ayrshare_response.get("errors"):
            for error in ayrshare_response["errors"]:
                platform = error.get("platform", "").lower()
                if platform:
                    platform_results[platform] = "failed"
                    # Collect error messages for summary
                    message = error.get("message", "Unknown error")
                    error_messages.append(f"{platform.capitalize()}: {message}")
        
        # Any platform not in postIds or errors should be marked as 'unknown'
        for platform in platforms:
            if platform not in platform_results:
                platform_results[platform] = "unknown"
        
        # Determine overall status (failed if Ayrshare returned error status or ANY platform failed)
        overall_status = "success" if ayrshare_response.get("status") == "success" else "failed"
        
        # Update deploy_event_data with platform-specific results
        deploy_event_data["status"] = overall_status
        deploy_event_data["completed_at"] = datetime.utcnow()
        deploy_event_data["ayrshare_post_id"] = ayrshare_response.get("id")
        deploy_event_data["platform_results"] = platform_results
        deploy_event_data["response_status"] = 200
        
        # Add error message summary if there are partial failures
        if error_messages:
            deploy_event_data["error_message"] = "; ".join(error_messages)
        
        logger.info(f"Order {order.order_number} deployed to Ayrshare with platform results: {platform_results}")
    
    except AyrshareError as e:
        # Error de Ayrshare API (429, 5xx, etc.)
        # Mark all platforms as 'unknown' since we couldn't reach the API
        platform_results = {platform: "unknown" for platform in platforms}
        
        deploy_event_data["status"] = "failed"
        deploy_event_data["error_message"] = str(e)
        deploy_event_data["completed_at"] = datetime.utcnow()
        deploy_event_data["platform_results"] = platform_results
        
        logger.error(f"Ayrshare API error for order {order.order_number}: {str(e)}")
    
    except Exception as e:
        # Error inesperado
        # Mark all platforms as 'unknown' since we couldn't complete the request
        platform_results = {platform: "unknown" for platform in platforms}
        
        deploy_event_data["status"] = "failed"
        deploy_event_data["error_message"] = f"Unexpected error: {str(e)[:200]}"
        deploy_event_data["completed_at"] = datetime.utcnow()
        deploy_event_data["platform_results"] = platform_results
        
        logger.error(f"Unexpected error during Ayrshare deploy for order {order.order_number}: {str(e)}")
    
    # Registrar evento en deploy_history
    if order.deploy_history is None:
        order.deploy_history = []
    
    order.deploy_history.append(deploy_event_data)
    order.updated_at = datetime.utcnow()
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Determinar respuesta según status
    if deploy_event_data["status"] == "success":
        return {
            "status": "ok",
            "message": "Social deploy sent to Ayrshare successfully",
            "deploy_event": deploy_event_data
        }
    else:
        # Deploy falló pero fue registrado
        return {
            "status": "error",
            "message": f"Deploy failed: {deploy_event_data.get('error_message', 'Unknown error')}",
            "deploy_event": deploy_event_data
        }


@router.post("/{order_id}/deploy/telegram")
async def deploy_order_to_telegram(
    order_id: str,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(require_admin)
):
    """
    Deploy orden Telegram Bot Autopilot a Telegram Bot API.
    
    FASE 10.B - Telegram Bot Deploy via Bot API
    
    Validaciones:
    - Usuario debe ser admin
    - Orden debe existir
    - tipo_producto debe contener "telegram" OR "bot" OR "messaging"
    - estado debe ser "listo"
    - qa_status debe ser "ok" (si existe)
    - TELEGRAM_BOT_TOKEN debe estar configurado y enable_telegram_deploy=True
    
    Proceso:
    1. Validar pre-condiciones
    2. Extraer contenido (texto, chat_id)
    3. POST HTTP a Telegram Bot API
    4. Registrar evento en deploy_history
    5. Retornar respuesta
    
    Returns:
        {
            "status": "ok",
            "message": "Telegram deploy request sent successfully",
            "deploy_event": {...},
            "provider": "telegram_bot_api",
            "chat_id": chat_id,
            "message_id": message_id
        }
    """
    # Validar que la orden existe
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validar que es una orden compatible con Telegram (flexible validation)
    tipo_lower = order.tipo_producto.lower()
    if not any(keyword in tipo_lower for keyword in ["telegram", "bot", "messaging"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order is not a Telegram-compatible product (tipo_producto: {order.tipo_producto})"
        )
    
    # Validar que está en estado listo
    if order.estado != "listo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order must be in 'listo' state to deploy (current: '{order.estado}')"
        )
    
    # Validar QA status si existe
    if order.qa_status and order.qa_status != "ok":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order must pass QA before deploy (current qa_status: '{order.qa_status}')"
        )
    
    # Verificar que Telegram está configurado (dual flag gating)
    if not settings.enable_telegram_deploy or not settings.telegram_bot_token or not settings.telegram_bot_token.strip():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deploy unavailable: Telegram deploy not configured (check ENABLE_TELEGRAM_DEPLOY and TELEGRAM_BOT_TOKEN)"
        )
    
    # Extraer texto del mensaje (prioridad: deliverable_metadata.descripcion > agent_blueprint.objective > fallback)
    text = None
    if order.deliverable_metadata and order.deliverable_metadata.get("descripcion"):
        text = order.deliverable_metadata["descripcion"]
    elif order.agent_blueprint and order.agent_blueprint.get("objective"):
        text = order.agent_blueprint["objective"]
    else:
        text = f"Autopilot deployed: {order.nombre_producto}"
    
    # Extraer chat_id con fallback chain (order → tenant → global)
    chat_id = None
    
    # Priority 1: Order-specific chat_id from deliverable_metadata
    if order.deliverable_metadata and order.deliverable_metadata.get("telegram_chat_id"):
        chat_id = order.deliverable_metadata["telegram_chat_id"]
        logger.info(f"Using order-specific telegram_chat_id: {chat_id}")
    
    # Priority 2: Tenant-specific chat_id from tenant.settings
    elif order.tenant_id:
        tenant = session.get(Tenant, order.tenant_id)
        if tenant and tenant.settings and tenant.settings.get("telegram_chat_id"):
            chat_id = tenant.settings["telegram_chat_id"]
            logger.info(f"Using tenant-specific telegram_chat_id for tenant {tenant.slug}: {chat_id}")
    
    # Priority 3: Global default chat_id from settings
    if not chat_id and settings.default_telegram_chat_id and settings.default_telegram_chat_id.strip():
        chat_id = settings.default_telegram_chat_id.strip()
        logger.info(f"Using global default telegram_chat_id from settings: {chat_id}")
    
    # No chat_id available → Error
    if not chat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Telegram chat_id not configured. Options: "
                "1) Set deliverable_metadata.telegram_chat_id in the order, "
                "2) Set settings.telegram_chat_id in the tenant configuration, "
                "or 3) Configure DEFAULT_TELEGRAM_CHAT_ID environment variable."
            )
        )
    
    # Crear evento de deploy
    deploy_event_data = {
        "id": str(uuid.uuid4()),
        "order_id": order.id,
        "channel": "telegram",
        "target_system": "telegram_bot_api",
        "status": "pending",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "chat_id": chat_id
    }
    
    # Intentar enviar a Telegram
    try:
        logger.info(f"Deploying order {order.order_number} to Telegram chat {chat_id}")
        
        telegram_response = await send_to_telegram(
            bot_token=settings.telegram_bot_token,
            base_url=settings.telegram_base_url,
            chat_id=chat_id,
            text=text,
            photo_urls=None,
            parse_mode="HTML"
        )
        
        # Deploy exitoso
        deploy_event_data["status"] = "success"
        deploy_event_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        deploy_event_data["telegram_message_id"] = telegram_response.get("result", {}).get("message_id")
        deploy_event_data["response_status"] = 200
        
        logger.info(f"Order {order.order_number} deployed successfully to Telegram. Message ID: {deploy_event_data.get('telegram_message_id')}")
    
    except TelegramError as e:
        # Error de Telegram API
        deploy_event_data["status"] = "failed"
        deploy_event_data["error_message"] = str(e)[:200]
        deploy_event_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        logger.error(f"Telegram API error for order {order.order_number}: {str(e)}")
    
    except Exception as e:
        # Error inesperado
        deploy_event_data["status"] = "failed"
        deploy_event_data["error_message"] = f"Unexpected error: {str(e)[:200]}"
        deploy_event_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        logger.error(f"Unexpected error during Telegram deploy for order {order.order_number}: {str(e)}")
    
    # Registrar evento en deploy_history
    if order.deploy_history is None:
        order.deploy_history = []
    
    order.deploy_history.append(deploy_event_data)
    order.updated_at = datetime.utcnow()
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Determinar respuesta según status
    if deploy_event_data["status"] == "success":
        return {
            "status": "ok",
            "message": "Telegram deploy request sent successfully",
            "deploy_event": deploy_event_data,
            "provider": "telegram_bot_api",
            "chat_id": chat_id,
            "message_id": deploy_event_data.get("telegram_message_id")
        }
    else:
        # Deploy falló pero fue registrado
        return {
            "status": "error",
            "message": f"Deploy failed: {deploy_event_data.get('error_message', 'Unknown error')}",
            "deploy_event": deploy_event_data
        }
