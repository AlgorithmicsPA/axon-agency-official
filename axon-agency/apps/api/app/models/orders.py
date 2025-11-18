"""Orders API models for AXON Factory."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON
from pydantic import BaseModel
from enum import Enum
import uuid


class SourceConfig(BaseModel):
    """
    Configuración de una fuente de información para el AgentBlueprint.
    
    Ejemplos:
    - {"type": "website_url", "value": "https://ejemplo.com", "notes": "Sitio principal"}
    - {"type": "manual_input", "value": "Productos: X, Y, Z", "notes": null}
    - {"type": "faq_file", "value": "faqs.pdf", "notes": "FAQ subido por cliente"}
    """
    type: str
    value: str
    notes: Optional[str] = None


class AgentBlueprint(BaseModel):
    """
    Blueprint (plano) de un agente/sistema completo.
    
    Define QUÉ se va a construir: tipo de agente, fuentes de información,
    canales, capacidades, nivel de automatización, etc.
    
    Este blueprint sirve como contrato para Axon 88 Builder, especificando
    exactamente qué sistema construir sin ambigüedades.
    """
    version: str = "1.0"
    agent_type: str
    product_type: str
    sources: list[SourceConfig] = []
    channels: list[str] = []
    capabilities: list[str] = []
    automation_level: str = "semi"
    client_profile: Optional[dict] = None
    notes: Optional[str] = None


class OrderStatus(str, Enum):
    """Estados válidos de una orden."""
    NUEVO = "nuevo"
    PLANIFICACION = "planificacion"
    CONSTRUCCION = "construccion"
    QA = "qa"
    LISTO = "listo"
    ENTREGADO = "entregado"
    FALLIDO = "fallido"
    CANCELADO = "cancelado"


class ProductType(str, Enum):
    """Tipos de productos disponibles."""
    AUTOPILOT_WHATSAPP = "autopilot_whatsapp"
    AUTOPILOT_VENTAS = "autopilot_ventas"
    WEBHOOK_SERVICE = "webhook_service"


class Order(SQLModel, table=True):
    """
    Modelo de orden de autopilot.
    
    Representa una solicitud de cliente para construir un autopilot específico.
    Trackea todo el ciclo de vida desde venta hasta entrega.
    """
    __tablename__ = "orders"
    
    # IDENTIFICACIÓN
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="UUID único de la orden"
    )
    
    order_number: str = Field(
        unique=True,
        index=True,
        description="Número de orden legible único (ej: ORD-2025-001)"
    )
    
    # PRODUCTO
    tipo_producto: str = Field(
        index=True,
        description="Tipo de autopilot (autopilot_whatsapp, autopilot_ventas, webhook_service)"
    )
    
    nombre_producto: str = Field(
        description="Nombre descriptivo del producto para el cliente"
    )
    
    # CLIENTE
    cliente_id: Optional[str] = Field(
        default=None,
        index=True,
        description="ID del cliente en sistema de usuarios (si existe)"
    )
    
    datos_cliente: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Información del cliente y configuración del autopilot"
    )
    
    # MULTI-TENANT (FASE 7)
    tenant_id: Optional[str] = Field(
        default=None,
        index=True,
        foreign_key="tenants.id",
        description="ID del tenant al que pertenece esta orden (nullable para backward compatibility)"
    )
    
    # ESTADO
    estado: str = Field(
        default="nuevo",
        index=True,
        description="Estado actual de la orden en el pipeline"
    )
    
    # PLANIFICACIÓN
    plan: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Plan de construcción generado por Super Axon Agent"
    )
    
    # CONSTRUCCIÓN
    repo_url: Optional[str] = Field(
        default=None,
        description="URL del repositorio Git del proyecto generado"
    )
    
    deploy_url: Optional[str] = Field(
        default=None,
        description="URL del deployment en producción"
    )
    
    # AXON 88 FACTORY INTEGRATION
    product_path: Optional[str] = Field(
        default=None,
        description="Ruta del producto en Axon 88 (ej: ~/factory/products/ORD-2025-001_autopilot_whatsapp/)"
    )
    
    log_path: Optional[str] = Field(
        default=None,
        description="Ruta del log de construcción en Axon 88"
    )
    
    construido_en: Optional[datetime] = Field(
        default=None,
        description="Timestamp de cuando se completó la construcción en Axon 88"
    )
    
    # BUILDER V2 - QA FIELDS
    qa_status: Optional[str] = Field(
        default=None,
        description="QA status: ok | warn | fail | null (no ejecutado)"
    )
    
    qa_messages: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Lista de mensajes del QA check"
    )
    
    qa_checked_files: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Archivos validados durante QA"
    )
    
    qa_ejecutado_en: Optional[datetime] = Field(
        default=None,
        description="Timestamp cuando se ejecutó QA en Axon 88"
    )
    
    # BUILDER V2 - DELIVERABLE FIELDS
    deliverable_generado: bool = Field(
        default=False,
        description="True si Axon 88 generó deliverable"
    )
    
    deliverable_metadata: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Metadata del deliverable (sin rutas sensibles)"
    )
    
    deliverable_generado_en: Optional[datetime] = Field(
        default=None,
        description="Timestamp cuando se generó deliverable en Axon 88"
    )
    
    # AGENT BLUEPRINT (FASE 3.A)
    agent_blueprint: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Blueprint del agente/sistema a construir (especificación completa)"
    )
    
    # DEPLOY HISTORY (FASE 9.1)
    deploy_history: Optional[list[dict]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Historial de eventos de deploy a canales externos (WhatsApp, Telegram, etc.)"
    )
    
    # RESULTADO
    resultado: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Información del producto entregado (URLs, credenciales, docs)"
    )
    
    # TRACKING
    progreso: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Progreso de construcción (0-100%)"
    )
    
    logs: list[dict] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Log de eventos y acciones en la orden"
    )
    
    # ASIGNACIÓN
    asignado_a: Optional[str] = Field(
        default=None,
        description="Agente actual responsable de la orden"
    )
    
    session_id: Optional[str] = Field(
        default=None,
        description="ID de sesión de Autonomous Agent (si aplica)"
    )
    
    # TIMESTAMPS
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación de la orden"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )
    
    planificado_at: Optional[datetime] = Field(
        default=None,
        description="Fecha cuando se completó la planificación"
    )
    
    construccion_iniciada_at: Optional[datetime] = Field(
        default=None,
        description="Fecha cuando inició la construcción"
    )
    
    qa_iniciada_at: Optional[datetime] = Field(
        default=None,
        description="Fecha cuando inició QA"
    )
    
    entregado_at: Optional[datetime] = Field(
        default=None,
        description="Fecha cuando se entregó al cliente"
    )
    
    # METADATA
    prioridad: str = Field(
        default="normal",
        description="Prioridad de la orden (baja, normal, alta, urgente)"
    )
    
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Tags para categorización y búsqueda"
    )
    
    notas_internas: str = Field(
        default="",
        description="Notas internas para el equipo (no visibles al cliente)"
    )


class OrderCreate(BaseModel):
    """Schema para crear nueva orden."""
    tipo_producto: str
    nombre_producto: str
    datos_cliente: dict
    tenant_id: Optional[str] = None
    prioridad: str = "normal"
    tags: list[str] = []


class OrderUpdate(BaseModel):
    """Schema para actualizar orden (uso interno)."""
    estado: Optional[OrderStatus] = None
    progreso: Optional[int] = None
    logs: Optional[list[dict]] = None
    plan: Optional[dict] = None
    asignado_a: Optional[str] = None
    session_id: Optional[str] = None
    resultado: Optional[dict] = None
    repo_url: Optional[str] = None
    deploy_url: Optional[str] = None


class DeployEvent(BaseModel):
    """Schema para un evento de deploy."""
    id: str
    order_id: str
    channel: str
    status: str
    target_system: str
    requested_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    webhook_url: Optional[str] = None
    response_status: Optional[int] = None


class DeployEventCreate(BaseModel):
    """Schema para crear un evento de deploy."""
    channel: str
    target_system: str
    status: str = "pending"
    error_message: Optional[str] = None
    webhook_url: Optional[str] = None
    response_status: Optional[int] = None


class OrderResponse(BaseModel):
    """Schema para respuesta de orden (listado)."""
    id: str
    order_number: str
    tipo_producto: str
    nombre_producto: str
    estado: str
    progreso: int
    prioridad: str
    tags: list[str]
    asignado_a: Optional[str] = None
    tenant_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
    """Schema para respuesta completa de orden (detalle)."""
    id: str
    order_number: str
    tipo_producto: str
    nombre_producto: str
    estado: str
    progreso: int
    prioridad: str
    tags: list[str]
    asignado_a: Optional[str] = None
    session_id: Optional[str] = None
    cliente_id: Optional[str] = None
    tenant_id: Optional[str] = None
    datos_cliente: dict
    plan: Optional[dict] = None
    logs: list[dict]
    repo_url: Optional[str] = None
    deploy_url: Optional[str] = None
    construido_en: Optional[datetime] = None
    qa_status: Optional[str] = None
    qa_messages: Optional[list[str]] = None
    qa_checked_files: Optional[list[str]] = None
    qa_ejecutado_en: Optional[datetime] = None
    deliverable_generado: bool = False
    deliverable_metadata: Optional[dict] = None
    deliverable_generado_en: Optional[datetime] = None
    agent_blueprint: Optional[dict] = None
    deploy_history: Optional[list[dict]] = None
    resultado: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    planificado_at: Optional[datetime] = None
    construccion_iniciada_at: Optional[datetime] = None
    qa_iniciada_at: Optional[datetime] = None
    entregado_at: Optional[datetime] = None
    notas_internas: str
    ayrshare_enabled: bool = False
    
    class Config:
        from_attributes = True
