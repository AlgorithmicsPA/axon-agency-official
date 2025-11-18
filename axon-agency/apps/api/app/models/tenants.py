"""Tenant models for multi-tenant support."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON
from pydantic import BaseModel
import uuid


class Tenant(SQLModel, table=True):
    """
    Representa un cliente/workspace en Axon Agency.
    
    Cada tenant es una organización que usa nuestros servicios.
    Ejemplos: escuelas, notarías, negocios de delivery, clínicas, etc.
    """
    __tablename__ = "tenants"
    
    # IDENTIFICACIÓN
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="UUID único del tenant"
    )
    
    slug: str = Field(
        unique=True,
        index=True,
        description="Slug único para URLs (ej: colegio-pedregal)"
    )
    
    # INFORMACIÓN BÁSICA
    name: str = Field(
        description="Nombre de la organización (ej: Colegio Pedregal)"
    )
    
    business_type: str = Field(
        default="general",
        description="Tipo de negocio: school, notary, delivery, health, retail, general"
    )
    
    # CONTACTO
    contact_email: str = Field(
        description="Email principal del tenant"
    )
    
    contact_phone: Optional[str] = Field(
        default=None,
        description="Teléfono de contacto"
    )
    
    contact_name: Optional[str] = Field(
        default=None,
        description="Nombre del contacto principal"
    )
    
    # BRANDING
    branding: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Configuración de branding: logo_url, primary_color, secondary_color, etc."
    )
    
    # CONFIGURACIÓN
    settings: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Configuración específica del tenant: max_orders, allowed_agents, etc."
    )
    
    # ESTADO
    active: bool = Field(
        default=True,
        description="True si el tenant está activo"
    )
    
    # TIMESTAMPS
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del tenant"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )
    
    # METADATA
    notes: str = Field(
        default="",
        description="Notas internas del equipo sobre este tenant"
    )


class TenantCreate(BaseModel):
    """Schema para crear nuevo tenant."""
    slug: str
    name: str
    business_type: str = "general"
    contact_email: str
    contact_phone: Optional[str] = None
    contact_name: Optional[str] = None
    branding: Optional[dict] = None
    settings: dict = {}
    notes: str = ""


class TenantUpdate(BaseModel):
    """Schema para actualizar tenant."""
    name: Optional[str] = None
    business_type: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_name: Optional[str] = None
    branding: Optional[dict] = None
    settings: Optional[dict] = None
    active: Optional[bool] = None
    notes: Optional[str] = None


class TenantResponse(BaseModel):
    """Schema para respuesta de tenant."""
    id: str
    slug: str
    name: str
    business_type: str
    contact_email: str
    contact_phone: Optional[str] = None
    contact_name: Optional[str] = None
    branding: Optional[dict] = None
    settings: dict
    active: bool
    created_at: datetime
    updated_at: datetime
    notes: str
    
    class Config:
        from_attributes = True
