"""Tenants API router for multi-tenant support."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import get_session
from app.core.security import get_current_user, get_user_from_token, TokenData
from app.models.tenants import (
    Tenant, TenantCreate, TenantUpdate, TenantResponse
)
from datetime import datetime

router = APIRouter()


def require_admin(current_user: TokenData, session: Session) -> None:
    """
    Helper function to verify user is admin.
    Raises HTTPException if user is not admin.
    """
    user = get_user_from_token(current_user, session)
    
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    active_only: bool = True,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Listar todos los tenants (admin-only).
    
    Parámetros:
    - active_only: solo mostrar tenants activos (default: True)
    
    Requires: Admin role
    """
    require_admin(current_user, session)
    
    query = select(Tenant)
    
    if active_only:
        query = query.where(Tenant.active == True)
    
    query = query.order_by(Tenant.created_at.desc())
    
    tenants = session.exec(query).all()
    return tenants


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Obtener información de un tenant específico (admin-only).
    
    Requires: Admin role
    """
    require_admin(current_user, session)
    
    tenant = session.get(Tenant, tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} no encontrado")
    
    return tenant


@router.post("", response_model=TenantResponse, status_code=201)
async def create_tenant(
    tenant_data: TenantCreate,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Crear nuevo tenant (admin-only).
    
    El slug debe ser único y URL-friendly (ej: colegio-pedregal).
    
    Requires: Admin role
    """
    require_admin(current_user, session)
    
    # Verificar que el slug no exista
    existing_tenant = session.exec(
        select(Tenant).where(Tenant.slug == tenant_data.slug)
    ).first()
    
    if existing_tenant:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un tenant con slug '{tenant_data.slug}'"
        )
    
    try:
        tenant = Tenant(
            slug=tenant_data.slug,
            name=tenant_data.name,
            business_type=tenant_data.business_type,
            contact_email=tenant_data.contact_email,
            contact_phone=tenant_data.contact_phone,
            contact_name=tenant_data.contact_name,
            branding=tenant_data.branding,
            settings=tenant_data.settings,
            notes=tenant_data.notes
        )
        
        session.add(tenant)
        session.commit()
        session.refresh(tenant)
        
        return tenant
        
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creando tenant: {str(e)}"
        )


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    update_data: TenantUpdate,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Actualizar información de tenant (admin-only).
    
    Permite actualizar: name, business_type, contacto, branding, settings, active, notes.
    
    Requires: Admin role
    """
    require_admin(current_user, session)
    
    tenant = session.get(Tenant, tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} no encontrado")
    
    # Actualizar campos
    update_dict = update_data.dict(exclude_unset=True)
    
    for key, value in update_dict.items():
        setattr(tenant, key, value)
    
    # Actualizar timestamp
    tenant.updated_at = datetime.utcnow()
    
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    
    return tenant


@router.delete("/{tenant_id}", status_code=204)
async def delete_tenant(
    tenant_id: str,
    hard_delete: bool = False,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Eliminar (soft delete) o desactivar tenant (admin-only).
    
    Por defecto hace soft delete (active = False).
    Si hard_delete=True, elimina el registro permanentemente.
    
    Requires: Admin role
    IMPORTANTE: Hard delete puede afectar órdenes asociadas.
    """
    require_admin(current_user, session)
    
    tenant = session.get(Tenant, tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} no encontrado")
    
    if hard_delete:
        # Hard delete (eliminar permanentemente)
        session.delete(tenant)
    else:
        # Soft delete (desactivar)
        tenant.active = False
        tenant.updated_at = datetime.utcnow()
        session.add(tenant)
    
    session.commit()
    
    return None
