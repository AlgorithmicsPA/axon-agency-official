# AXON Factory - Orders API Design

**Versión:** 1.0.0  
**Fecha:** Noviembre 14, 2025  
**Status:** Diseñado (no implementado)  
**Autor:** Federico @ AXON Agency

---

## 1. Overview

La **Orders API** es el sistema central de gestión de órdenes de la fábrica AXON. Permite:

- ✅ Crear órdenes de autopilotos desde ventas
- ✅ Trackear progreso de construcción en tiempo real
- ✅ Gestionar estados del ciclo de vida
- ✅ Consultar productos entregados
- ✅ Logs y auditoría completa

**Arquitectura:**
- REST API con FastAPI
- Base de datos: PostgreSQL (SQLModel)
- Autenticación: JWT + API keys
- Real-time: WebSockets (opcional)

---

## 2. Modelo de Datos

### 2.1 Order Model (SQLModel)

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid


class Order(SQLModel, table=True):
    """
    Modelo de orden de autopilot.
    
    Representa una solicitud de cliente para construir un autopilot específico.
    Trackea todo el ciclo de vida desde venta hasta entrega.
    """
    
    # ===== IDENTIFICACIÓN =====
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="UUID único de la orden"
    )
    
    order_number: str = Field(
        index=True,
        description="Número de orden legible (ej: ORD-2025-001)"
    )
    
    # ===== PRODUCTO =====
    tipo_producto: str = Field(
        index=True,
        description="Tipo de autopilot (autopilot_whatsapp, autopilot_ventas, webhook_service)"
    )
    
    nombre_producto: str = Field(
        description="Nombre descriptivo del producto para el cliente"
    )
    
    # ===== CLIENTE =====
    cliente_id: Optional[str] = Field(
        default=None,
        index=True,
        description="ID del cliente en sistema de usuarios (si existe)"
    )
    
    datos_cliente: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type_": "JSON"},
        description="Información del cliente y configuración del autopilot"
    )
    # Ejemplo de datos_cliente:
    # {
    #   "nombre": "Empresa XYZ S.A.",
    #   "email": "contacto@empresa.com",
    #   "telefono": "+5215512345678",
    #   "industria": "retail",
    #   "pais": "México",
    #   "configuracion": {
    #     "whatsapp_number": "+5215587654321",
    #     "horario_atencion": "9:00-20:00",
    #     "idioma": "es",
    #     "personalidad_bot": "profesional y amigable",
    #     "productos": ["camisetas", "pantalones", "zapatos"],
    #     "integraciones": ["stripe", "google_sheets"]
    #   }
    # }
    
    # ===== ESTADO =====
    estado: str = Field(
        default="nuevo",
        index=True,
        description="Estado actual de la orden en el pipeline"
    )
    # Estados válidos:
    # - nuevo: Orden recién creada, pendiente de planificación
    # - planificacion: Super Axon Agent está generando plan
    # - construccion: Builder/Developer Agents construyendo
    # - qa: Review Council validando calidad
    # - listo: Producto terminado, pendiente de deploy
    # - entregado: Producto desplegado y entregado al cliente
    # - fallido: Error crítico en construcción
    # - cancelado: Orden cancelada por cliente/admin
    
    # ===== PLANIFICACIÓN =====
    plan: Optional[dict] = Field(
        default=None,
        sa_column_kwargs={"type_": "JSON"},
        description="Plan de construcción generado por Super Axon Agent"
    )
    # Ejemplo de plan:
    # {
    #   "stack_tecnologico": ["FastAPI", "Next.js", "PostgreSQL", "Redis"],
    #   "integraciones": ["WhatsApp Business API", "Stripe", "Google Sheets"],
    #   "templates": ["autopilot_base", "whatsapp_bot_base"],
    #   "recursos_requeridos": {
    #     "cpu_cores": 2,
    #     "ram_gb": 4,
    #     "storage_gb": 20
    #   },
    #   "estimacion_horas": 24,
    #   "subagentes_asignados": ["Builder", "Developer", "RAG", "QA", "Security"],
    #   "milestones": [
    #     {"nombre": "Scaffolding", "estimacion_horas": 2},
    #     {"nombre": "Backend API", "estimacion_horas": 8},
    #     {"nombre": "Frontend", "estimacion_horas": 6},
    #     {"nombre": "Integraciones", "estimacion_horas": 4},
    #     {"nombre": "QA", "estimacion_horas": 4}
    #   ]
    # }
    
    # ===== CONSTRUCCIÓN =====
    repo_url: Optional[str] = Field(
        default=None,
        description="URL del repositorio Git del proyecto generado"
    )
    
    deploy_url: Optional[str] = Field(
        default=None,
        description="URL del deployment en producción"
    )
    
    # ===== RESULTADO =====
    resultado: Optional[dict] = Field(
        default=None,
        sa_column_kwargs={"type_": "JSON"},
        description="Información del producto entregado (URLs, credenciales, docs)"
    )
    # Ejemplo de resultado:
    # {
    #   "portal_url": "https://autopilot-xyz.axon88.com",
    #   "admin_url": "https://autopilot-xyz.axon88.com/admin",
    #   "api_url": "https://api.autopilot-xyz.axon88.com",
    #   "credentials": {
    #     "admin_email": "admin@empresa.com",
    #     "admin_password_temporal": "ChangeMe123!",
    #     "api_key": "axon_pk_live_abc123xyz",
    #     "webhook_secret": "whsec_def456uvw"
    #   },
    #   "docs_url": "https://docs.axon88.com/autopilot-xyz",
    #   "support_email": "support@axon88.com",
    #   "webhooks": {
    #     "whatsapp": "https://autopilot-xyz.axon88.com/webhooks/whatsapp",
    #     "stripe": "https://autopilot-xyz.axon88.com/webhooks/stripe"
    #   },
    #   "configuracion_inicial": {
    #     "db_migrated": true,
    #     "seeds_loaded": true,
    #     "integrations_configured": ["whatsapp", "stripe"]
    #   }
    # }
    
    # ===== TRACKING =====
    progreso: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Progreso de construcción (0-100%)"
    )
    
    logs: list[dict] = Field(
        default_factory=list,
        sa_column_kwargs={"type_": "JSON"},
        description="Log de eventos y acciones en la orden"
    )
    # Cada log entry:
    # {
    #   "timestamp": "2025-11-14T10:30:00Z",
    #   "agente": "Builder Agent",
    #   "mensaje": "Proyecto base creado desde template autopilot_base",
    #   "tipo": "info",  # info | warning | error | success
    #   "metadata": {...}  # Datos adicionales
    # }
    
    # ===== ASIGNACIÓN =====
    asignado_a: Optional[str] = Field(
        default=None,
        description="Agente actual responsable de la orden"
    )
    # Ejemplos: "Super Axon Agent", "Builder Agent", "QA Agent", etc.
    
    session_id: Optional[str] = Field(
        default=None,
        description="ID de sesión de Autonomous Agent (si aplica)"
    )
    
    # ===== TIMESTAMPS =====
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
    
    # ===== METADATA =====
    prioridad: str = Field(
        default="normal",
        description="Prioridad de la orden (baja, normal, alta, urgente)"
    )
    
    tags: list[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type_": "JSON"},
        description="Tags para categorización y búsqueda"
    )
    
    notas_internas: str = Field(
        default="",
        description="Notas internas para el equipo (no visibles al cliente)"
    )
    
    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "order_number": "ORD-2025-001",
                "tipo_producto": "autopilot_whatsapp",
                "nombre_producto": "WhatsApp Bot Ventas - Empresa XYZ",
                "datos_cliente": {
                    "nombre": "Empresa XYZ",
                    "email": "contacto@empresa.com",
                    "configuracion": {
                        "whatsapp_number": "+5215512345678",
                        "idioma": "es"
                    }
                },
                "estado": "nuevo",
                "prioridad": "normal"
            }
        }
```

---

## 3. REST API Endpoints

### 3.1 POST /api/orders - Crear Nueva Orden

**Descripción:** Crear una nueva orden de autopilot (usualmente desde el sistema de ventas).

**Authentication:** Required (JWT o API key)

**Request Body:**
```json
{
  "tipo_producto": "autopilot_whatsapp",
  "nombre_producto": "WhatsApp Bot Ventas - Empresa XYZ",
  "datos_cliente": {
    "nombre": "Empresa XYZ S.A.",
    "email": "contacto@empresa.com",
    "telefono": "+5215512345678",
    "industria": "retail",
    "pais": "México",
    "configuracion": {
      "whatsapp_number": "+5215587654321",
      "horario_atencion": "9:00-20:00",
      "idioma": "es",
      "personalidad_bot": "profesional y amigable",
      "productos": ["camisetas", "pantalones", "zapatos"],
      "integraciones": ["stripe", "google_sheets"]
    }
  },
  "prioridad": "normal",
  "tags": ["retail", "whatsapp", "mexico"]
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-001",
  "tipo_producto": "autopilot_whatsapp",
  "nombre_producto": "WhatsApp Bot Ventas - Empresa XYZ",
  "estado": "nuevo",
  "progreso": 0,
  "created_at": "2025-11-14T10:00:00Z",
  "message": "Orden creada exitosamente. Super Axon Agent la procesará pronto."
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Validation error",
  "details": {
    "tipo_producto": "Tipo de producto no válido. Opciones: autopilot_whatsapp, autopilot_ventas, webhook_service"
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Authentication required",
  "message": "Valid JWT token or API key required"
}
```

---

### 3.2 GET /api/orders/{id} - Consultar Estado de Orden

**Descripción:** Obtener información completa de una orden específica.

**Authentication:** Required

**Path Parameters:**
- `id` (string): UUID de la orden

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-001",
  "tipo_producto": "autopilot_whatsapp",
  "nombre_producto": "WhatsApp Bot Ventas - Empresa XYZ",
  "estado": "construccion",
  "progreso": 45,
  "asignado_a": "Builder Agent",
  "datos_cliente": {
    "nombre": "Empresa XYZ S.A.",
    "email": "contacto@empresa.com",
    "industria": "retail",
    "configuracion": {
      "whatsapp_number": "+5215587654321",
      "horario_atencion": "9:00-20:00",
      "idioma": "es"
    }
  },
  "plan": {
    "stack_tecnologico": ["FastAPI", "Twilio WhatsApp API", "PostgreSQL", "Redis"],
    "integraciones": ["WhatsApp Business API", "Stripe", "Google Sheets"],
    "templates": ["autopilot_base", "whatsapp_bot_base"],
    "estimacion_horas": 24,
    "subagentes_asignados": ["Builder", "Developer", "RAG", "QA", "Security"]
  },
  "logs": [
    {
      "timestamp": "2025-11-14T10:05:00Z",
      "agente": "Super Axon Agent",
      "mensaje": "Orden recibida, iniciando planificación",
      "tipo": "info"
    },
    {
      "timestamp": "2025-11-14T10:15:00Z",
      "agente": "Planner Agent",
      "mensaje": "Plan de construcción generado exitosamente",
      "tipo": "success"
    },
    {
      "timestamp": "2025-11-14T10:30:00Z",
      "agente": "Builder Agent",
      "mensaje": "Proyecto base creado desde template autopilot_base",
      "tipo": "info"
    },
    {
      "timestamp": "2025-11-14T11:00:00Z",
      "agente": "Developer Agent",
      "mensaje": "Integración con WhatsApp API completada",
      "tipo": "success"
    },
    {
      "timestamp": "2025-11-14T11:30:00Z",
      "agente": "Developer Agent",
      "mensaje": "Configurando Stripe webhooks...",
      "tipo": "info"
    }
  ],
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T11:30:00Z",
  "planificado_at": "2025-11-14T10:15:00Z",
  "construccion_iniciada_at": "2025-11-14T10:30:00Z",
  "prioridad": "normal",
  "tags": ["retail", "whatsapp", "mexico"]
}
```

**Response (404 Not Found):**
```json
{
  "error": "Order not found",
  "message": "No order exists with ID: 550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 3.3 GET /api/orders/{id}/result - Obtener Producto Entregado

**Descripción:** Obtener información del producto entregado (URLs, credenciales, documentación).

**IMPORTANTE:** Solo disponible cuando `estado = "listo"` o `estado = "entregado"`

**Authentication:** Required

**Path Parameters:**
- `id` (string): UUID de la orden

**Response (200 OK) - Producto listo:**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-001",
  "tipo_producto": "autopilot_whatsapp",
  "nombre_producto": "WhatsApp Bot Ventas - Empresa XYZ",
  "estado": "listo",
  "resultado": {
    "portal_url": "https://autopilot-xyz.axon88.com",
    "admin_url": "https://autopilot-xyz.axon88.com/admin",
    "api_url": "https://api.autopilot-xyz.axon88.com",
    "credentials": {
      "admin_email": "admin@empresa.com",
      "admin_password_temporal": "ChangeMe123!",
      "api_key": "axon_pk_live_abc123xyz789",
      "webhook_secret": "whsec_def456uvw012"
    },
    "docs_url": "https://docs.axon88.com/autopilot-xyz",
    "support_email": "support@axon88.com",
    "webhooks": {
      "whatsapp": "https://autopilot-xyz.axon88.com/webhooks/whatsapp",
      "stripe": "https://autopilot-xyz.axon88.com/webhooks/stripe"
    },
    "configuracion_inicial": {
      "db_migrated": true,
      "seeds_loaded": true,
      "integrations_configured": ["whatsapp", "stripe", "google_sheets"]
    }
  },
  "repo_url": "https://github.com/axon88-products/autopilot-xyz-001",
  "deploy_url": "https://autopilot-xyz.axon88.com",
  "entregado_at": "2025-11-14T14:00:00Z"
}
```

**Response (400 Bad Request) - Producto no listo:**
```json
{
  "error": "Producto aún no está listo",
  "estado_actual": "construccion",
  "progreso": 45,
  "mensaje": "El autopilot está en construcción. Revisa el estado en /api/orders/550e8400-e29b-41d4-a716-446655440000",
  "estimacion_tiempo_restante": "8-12 horas"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Order not found"
}
```

---

### 3.4 GET /api/orders - Listar Órdenes

**Descripción:** Listar órdenes con filtros y paginación.

**Authentication:** Required

**Query Parameters:**
- `estado` (string, optional): Filtrar por estado (nuevo, planificacion, construccion, qa, listo, entregado)
- `tipo_producto` (string, optional): Filtrar por tipo de producto
- `prioridad` (string, optional): Filtrar por prioridad (baja, normal, alta, urgente)
- `tag` (string, optional): Filtrar por tag
- `limit` (integer, optional): Número de resultados (default: 50, max: 200)
- `offset` (integer, optional): Para paginación (default: 0)
- `sort_by` (string, optional): Campo para ordenar (created_at, updated_at, prioridad)
- `sort_order` (string, optional): Orden (asc, desc) (default: desc)

**Example Request:**
```
GET /api/orders?estado=construccion&limit=20&offset=0&sort_by=created_at&sort_order=desc
```

**Response (200 OK):**
```json
{
  "total": 150,
  "limit": 20,
  "offset": 0,
  "count": 20,
  "orders": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "order_number": "ORD-2025-001",
      "tipo_producto": "autopilot_whatsapp",
      "nombre_producto": "WhatsApp Bot Ventas - Empresa XYZ",
      "estado": "construccion",
      "progreso": 45,
      "asignado_a": "Builder Agent",
      "prioridad": "normal",
      "created_at": "2025-11-14T10:00:00Z",
      "updated_at": "2025-11-14T11:30:00Z"
    },
    {
      "id": "660f9511-f3ac-52e5-b827-557766551111",
      "order_number": "ORD-2025-002",
      "tipo_producto": "autopilot_ventas",
      "nombre_producto": "Funnel Ventas - Coach ABC",
      "estado": "construccion",
      "progreso": 60,
      "asignado_a": "Developer Agent",
      "prioridad": "alta",
      "created_at": "2025-11-14T11:00:00Z",
      "updated_at": "2025-11-14T12:00:00Z"
    }
    // ... más órdenes
  ]
}
```

---

### 3.5 PATCH /api/orders/{id} - Actualizar Estado (Interno)

**Descripción:** Actualizar estado, progreso y logs de una orden.

**IMPORTANTE:** Este endpoint es para uso interno (Super Axon Agent, subagentes). No debe ser expuesto públicamente.

**Authentication:** Required (admin/system role)

**Path Parameters:**
- `id` (string): UUID de la orden

**Request Body:**
```json
{
  "estado": "qa",
  "progreso": 85,
  "asignado_a": "QA Agent",
  "logs": [
    {
      "timestamp": "2025-11-14T13:00:00Z",
      "agente": "QA Agent",
      "mensaje": "Tests automatizados ejecutados: 45/45 pasaron ✅",
      "tipo": "success"
    },
    {
      "timestamp": "2025-11-14T13:15:00Z",
      "agente": "Security Agent",
      "mensaje": "Auditoría de seguridad completada: 0 vulnerabilidades críticas",
      "tipo": "success"
    }
  ],
  "qa_iniciada_at": "2025-11-14T13:00:00Z"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-001",
  "estado": "qa",
  "progreso": 85,
  "asignado_a": "QA Agent",
  "updated_at": "2025-11-14T13:15:00Z",
  "message": "Orden actualizada exitosamente"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "Forbidden",
  "message": "Este endpoint es solo para uso interno del sistema"
}
```

---

### 3.6 DELETE /api/orders/{id} - Cancelar Orden

**Descripción:** Cancelar una orden (solo si está en estado `nuevo` o `planificacion`).

**Authentication:** Required (admin role)

**Path Parameters:**
- `id` (string): UUID de la orden

**Response (200 OK):**
```json
{
  "message": "Orden ORD-2025-001 cancelada exitosamente",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "estado_anterior": "nuevo",
  "estado_nuevo": "cancelado"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "No se puede cancelar la orden",
  "message": "La orden está en estado 'construccion'. Solo se pueden cancelar órdenes en estado 'nuevo' o 'planificacion'",
  "estado_actual": "construccion"
}
```

---

## 4. Tipos de Productos (Catálogo)

### 4.1 PRODUCT_TYPES Configuration

```python
PRODUCT_TYPES = {
    "autopilot_whatsapp": {
        "nombre": "Autopilot WhatsApp",
        "descripcion": "Bot inteligente para ventas/soporte por WhatsApp",
        "stack_base": [
            "FastAPI",
            "Twilio WhatsApp API",
            "PostgreSQL",
            "Redis",
            "Next.js"
        ],
        "templates": [
            "autopilot_base",
            "whatsapp_bot_base"
        ],
        "integraciones_comunes": [
            "WhatsApp Business API",
            "Stripe",
            "Google Sheets",
            "HubSpot"
        ],
        "estimacion_horas": 24,
        "precio_base_usd": 2500,
        "features": [
            "Respuestas automáticas 24/7",
            "Integración con catálogo de productos",
            "Procesamiento de pedidos",
            "Notificaciones automáticas",
            "Dashboard de métricas",
            "Multi-idioma"
        ]
    },
    
    "autopilot_ventas": {
        "nombre": "Autopilot Ventas",
        "descripcion": "Agente de ventas completo con funnel automatizado",
        "stack_base": [
            "Next.js",
            "FastAPI",
            "PostgreSQL",
            "n8n",
            "Redis"
        ],
        "templates": [
            "autopilot_base",
            "sales_funnel_base"
        ],
        "integraciones_comunes": [
            "Stripe",
            "HubSpot",
            "WhatsApp",
            "Email (SendGrid/Resend)",
            "Calendar (Google Calendar)"
        ],
        "estimacion_horas": 48,
        "precio_base_usd": 5000,
        "features": [
            "Landing page optimizada",
            "Chat de ventas con IA",
            "Pipeline automatizado",
            "Email marketing",
            "Agendamiento automático",
            "Dashboard de conversiones",
            "A/B testing",
            "CRM integrado"
        ]
    },
    
    "webhook_service": {
        "nombre": "Webhook Service",
        "descripcion": "Servicio de webhooks personalizado para integraciones",
        "stack_base": [
            "FastAPI",
            "Redis",
            "PostgreSQL"
        ],
        "templates": [
            "webhook_service_base"
        ],
        "integraciones_comunes": [
            "Slack",
            "Discord",
            "Email",
            "SMS (Twilio)",
            "Zapier",
            "Make"
        ],
        "estimacion_horas": 16,
        "precio_base_usd": 1500,
        "features": [
            "Webhooks ilimitados",
            "Event routing",
            "Transformaciones de datos",
            "Retry automático",
            "Logs y auditoría",
            "Rate limiting",
            "Authentication flexible"
        ]
    }
}
```

### 4.2 GET /api/products/types - Listar Tipos de Productos

**Descripción:** Obtener catálogo de productos disponibles.

**Authentication:** Optional (público)

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": "autopilot_whatsapp",
      "nombre": "Autopilot WhatsApp",
      "descripcion": "Bot inteligente para ventas/soporte por WhatsApp",
      "estimacion_horas": 24,
      "precio_base_usd": 2500,
      "features": [
        "Respuestas automáticas 24/7",
        "Integración con catálogo de productos",
        "Procesamiento de pedidos"
      ]
    },
    {
      "id": "autopilot_ventas",
      "nombre": "Autopilot Ventas",
      "descripcion": "Agente de ventas completo con funnel automatizado",
      "estimacion_horas": 48,
      "precio_base_usd": 5000,
      "features": [
        "Landing page optimizada",
        "Chat de ventas con IA",
        "Pipeline automatizado"
      ]
    },
    {
      "id": "webhook_service",
      "nombre": "Webhook Service",
      "descripcion": "Servicio de webhooks personalizado",
      "estimacion_horas": 16,
      "precio_base_usd": 1500,
      "features": [
        "Webhooks ilimitados",
        "Event routing",
        "Transformaciones de datos"
      ]
    }
  ]
}
```

---

## 5. Integración con Super Axon Agent

### 5.1 Flujo de Procesamiento de Órdenes

#### **1. Polling de Órdenes Nuevas**

Super Axon Agent revisa periódicamente órdenes pendientes:

```python
# Ejecutar cada 5 minutos (o en tiempo real con WebSocket)
async def poll_pending_orders():
    """Poll for new orders and process them."""
    pending_orders = await db.query(Order).filter(
        Order.estado == "nuevo"
    ).order_by(
        Order.prioridad.desc(),  # Alta prioridad primero
        Order.created_at.asc()   # FIFO dentro de misma prioridad
    ).limit(10).all()
    
    for order in pending_orders:
        await super_axon_agent.process_order(order)
```

#### **2. Clasificación y Planificación**

```python
async def process_order(order: Order):
    """Process a new order: classify and plan."""
    
    # 1. Obtener tipo de producto del catálogo
    product_type = PRODUCT_TYPES.get(order.tipo_producto)
    if not product_type:
        await mark_order_failed(order, "Tipo de producto no válido")
        return
    
    # 2. Usar LLM para generar plan personalizado
    planning_prompt = f"""
    Genera un plan de construcción detallado para:
    
    Producto: {product_type['nombre']}
    Cliente: {order.datos_cliente['nombre']}
    Industria: {order.datos_cliente.get('industria', 'general')}
    Configuración: {json.dumps(order.datos_cliente.get('configuracion', {}), indent=2)}
    
    Stack base: {', '.join(product_type['stack_base'])}
    Templates: {', '.join(product_type['templates'])}
    
    Proporciona:
    1. Stack tecnológico completo (incluyendo versiones)
    2. Integraciones necesarias
    3. Milestones con estimaciones
    4. Subagentes asignados
    5. Recursos requeridos (CPU, RAM, storage)
    """
    
    plan = await llm_router.chat(planning_prompt, mode="code")
    
    # 3. Actualizar orden con plan
    order.plan = parse_plan(plan)
    order.estado = "planificacion"
    order.planificado_at = datetime.utcnow()
    order.asignado_a = "Super Axon Agent"
    order.logs.append({
        "timestamp": datetime.utcnow().isoformat(),
        "agente": "Super Axon Agent",
        "mensaje": "Plan de construcción generado",
        "tipo": "success"
    })
    
    await db.commit()
    
    # 4. Notificar a Federico para aprobación
    await notify_federico(order, "plan_ready")
```

#### **3. Delegación a Subagentes**

```python
async def start_construction(order: Order):
    """Start construction phase by delegating to Autonomous Agent."""
    
    # 1. Crear sesión de Autonomous Agent
    from app.routers.autonomous import get_autonomous_agent
    agent = await get_autonomous_agent()
    
    goal = f"""
    Construir {order.tipo_producto} para {order.datos_cliente['nombre']}.
    
    Plan:
    {json.dumps(order.plan, indent=2)}
    
    Configuración del cliente:
    {json.dumps(order.datos_cliente['configuracion'], indent=2)}
    
    Deliverables:
    - Código completo (backend + frontend)
    - Base de datos configurada
    - Integraciones funcionando
    - Tests pasando
    - Documentación
    """
    
    session = await agent.start_external_goal_session(
        goal=goal,
        mode="balanced",
        tenant_id="default",
        metadata={
            "order_id": order.id,
            "order_number": order.order_number,
            "tipo_producto": order.tipo_producto
        },
        origin="orders_system"
    )
    
    # 2. Vincular sesión con orden
    order.session_id = session["session_id"]
    order.estado = "construccion"
    order.construccion_iniciada_at = datetime.utcnow()
    order.asignado_a = "Autonomous Agent"
    order.logs.append({
        "timestamp": datetime.utcnow().isoformat(),
        "agente": "Super Axon Agent",
        "mensaje": f"Construcción iniciada (session: {session['session_id']})",
        "tipo": "info"
    })
    
    await db.commit()
```

#### **4. Tracking de Progreso**

```python
async def monitor_construction_progress(order: Order):
    """Monitor progress of autonomous agent session."""
    
    from app.routers.autonomous import get_autonomous_agent
    agent = await get_autonomous_agent()
    
    # Obtener progreso de la sesión
    session = await agent.get_session(order.session_id)
    
    # Estimar progreso basado en milestones completados
    completed_milestones = session.get("completed_actions", 0)
    total_milestones = len(order.plan.get("milestones", []))
    progress = int((completed_milestones / total_milestones) * 100) if total_milestones > 0 else 0
    
    # Actualizar orden
    order.progreso = min(progress, 95)  # Máximo 95% hasta QA
    order.updated_at = datetime.utcnow()
    
    await db.commit()
```

#### **5. Review y QA**

```python
async def start_qa_review(order: Order):
    """Start QA review process with Review Council."""
    
    order.estado = "qa"
    order.qa_iniciada_at = datetime.utcnow()
    order.progreso = 95
    order.asignado_a = "Review Council"
    
    # Ejecutar Review Council
    from app.services.review_council import get_review_council
    council = get_review_council()
    
    review_result = await council.review_product(
        product_path=f"~/factory/products/{order.order_number.lower()}",
        order_metadata=order.dict()
    )
    
    if review_result["approved"]:
        # Aprobado → listo para deploy
        order.estado = "listo"
        order.progreso = 100
        order.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agente": "Review Council",
            "mensaje": "✅ Producto aprobado por Review Council",
            "tipo": "success",
            "metadata": review_result
        })
    else:
        # Rechazado → regresa a construcción
        order.estado = "construccion"
        order.progreso = 70
        order.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agente": "Review Council",
            "mensaje": f"❌ Producto rechazado. Razón: {review_result['reason']}",
            "tipo": "error",
            "metadata": review_result
        })
    
    await db.commit()
```

#### **6. Entrega**

```python
async def deploy_and_deliver(order: Order):
    """Deploy product and mark as delivered."""
    
    # 1. Deploy (manual o automatizado según configuración)
    deploy_result = await deploy_product(order)
    
    # 2. Generar credenciales
    credentials = await generate_client_credentials(order)
    
    # 3. Crear portal del cliente
    portal_url = await create_client_portal(order)
    
    # 4. Actualizar orden con resultado
    order.resultado = {
        "portal_url": portal_url,
        "admin_url": f"{deploy_result['url']}/admin",
        "api_url": deploy_result["api_url"],
        "credentials": credentials,
        "docs_url": f"https://docs.axon88.com/{order.order_number.lower()}",
        "support_email": "support@axon88.com",
        "webhooks": deploy_result.get("webhooks", {}),
        "configuracion_inicial": deploy_result.get("config", {})
    }
    
    order.deploy_url = deploy_result["url"]
    order.repo_url = deploy_result.get("repo_url")
    order.estado = "entregado"
    order.entregado_at = datetime.utcnow()
    order.logs.append({
        "timestamp": datetime.utcnow().isoformat(),
        "agente": "Ops Agent",
        "mensaje": "🎉 Producto desplegado y entregado al cliente",
        "tipo": "success"
    })
    
    await db.commit()
    
    # 5. Notificar al cliente
    await send_delivery_email(order)
```

---

## 6. Estados y Transiciones

### 6.1 Diagrama de Estados

```
        nuevo
          ↓ (Super Axon planifica)
    planificacion
          ↓ (Plan aprobado)
    construccion
          ↓ (Código completo)
         qa
         ↙ ↘
   (rechazado)  (aprobado)
        ↓           ↓
   construccion   listo
                    ↓ (Deploy)
               entregado
    
    (En cualquier punto)
          ↓
    fallido / cancelado
```

### 6.2 Transiciones Válidas

| Desde | Hacia | Condición | Actor |
|-------|-------|-----------|-------|
| nuevo | planificacion | Automático | Super Axon Agent |
| planificacion | construccion | Plan aprobado | Super Axon Agent |
| planificacion | cancelado | Cancelación manual | Admin/Federico |
| construccion | qa | Código completo | Builder/Developer Agents |
| construccion | fallido | Error crítico | System |
| qa | listo | Review aprobado | Review Council |
| qa | construccion | Review rechazado | Review Council |
| listo | entregado | Deploy exitoso | Ops Agent |
| listo | fallido | Deploy fallido | Ops Agent |
| * | cancelado | Cancelación manual | Admin |

---

## 7. WebSocket API (Opcional)

Para updates en tiempo real del progreso de órdenes:

### 7.1 Conexión

```javascript
const ws = new WebSocket('wss://api.axon88.com/ws/orders');

ws.on('open', () => {
  // Autenticar
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'JWT_TOKEN'
  }));
  
  // Subscribirse a orden específica
  ws.send(JSON.stringify({
    type: 'subscribe',
    order_id: '550e8400-e29b-41d4-a716-446655440000'
  }));
});

// Recibir updates
ws.on('message', (data) => {
  const update = JSON.parse(data);
  console.log('Order update:', update);
  
  // {
  //   type: 'order_update',
  //   order_id: '...',
  //   estado: 'construccion',
  //   progreso: 45,
  //   last_log: {...}
  // }
});
```

---

## 8. Seguridad y Autenticación

### 8.1 Authentication Methods

1. **JWT Tokens** (para usuarios/clientes)
   - Login: POST /api/auth/login
   - Token incluido en header: `Authorization: Bearer <token>`

2. **API Keys** (para sistemas internos)
   - Header: `X-API-Key: <api_key>`
   - Scope limitado (solo lectura, solo escritura, admin)

3. **System Tokens** (para subagentes)
   - Header: `X-System-Token: <system_token>`
   - Solo para endpoints internos (/api/orders/{id} PATCH)

### 8.2 Authorization

**Roles:**
- `admin`: Acceso completo
- `operator`: Lectura + actualizaciones de estado
- `client`: Solo lectura de sus propias órdenes
- `system`: Solo endpoints internos

---

## 9. Monitoreo y Observabilidad

### 9.1 Métricas Clave

- **Order creation rate**: Órdenes/día
- **Average construction time**: Tiempo promedio por tipo de producto
- **Success rate**: % órdenes completadas sin fallos
- **Queue depth**: Órdenes pendientes en cada estado
- **Agent utilization**: % tiempo cada agente ocupado

### 9.2 Logs

Todos los eventos importantes se registran en `Order.logs[]`:
- Cambios de estado
- Acciones de agentes
- Errores y warnings
- Milestones completados

---

## 10. Roadmap de Implementación

### Fase 1: Core API (2 semanas)
- ✅ Modelo Order (SQLModel)
- ✅ Endpoints básicos (POST, GET, PATCH)
- ✅ Integración con DB
- ✅ Authentication

### Fase 2: Super Axon Integration (2 semanas)
- ✅ Polling de órdenes nuevas
- ✅ Planificación con LLM
- ✅ Delegación a Autonomous Agent
- ✅ Tracking de progreso

### Fase 3: Review Council Integration (1 semana)
- ✅ QA automation
- ✅ Security scanning
- ✅ Performance testing
- ✅ Aprobación/rechazo

### Fase 4: Delivery Pipeline (1 semana)
- ✅ Deploy automation
- ✅ Credential generation
- ✅ Client portal creation
- ✅ Email notifications

### Fase 5: Monitoring & Optimization (1 semana)
- ✅ WebSocket API
- ✅ Dashboards
- ✅ Alertas
- ✅ Optimizaciones de performance

---

## 11. Tech Debt Conocido

### 11.1 Async/Sync Database Operations

**Estado actual:**
- Los endpoints de Orders API están declarados como `async def` pero utilizan SQLModel con sesiones síncronas (`Session`)
- Esto funciona correctamente para el caso de uso actual (factory privada, volumen moderado de órdenes)

**Implicaciones:**
- Las operaciones de base de datos bloquean el event loop de FastAPI
- Bajo **alta concurrencia** (miles de órdenes simultáneas), esto podría causar latencia
- Para una factory privada con volumen normal, **es suficiente**

**Optimización futura (si es necesaria):**
```python
# Opción 1: Cambiar a AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Opción 2: Usar run_in_threadpool para operaciones sync
from fastapi.concurrency import run_in_threadpool

# Opción 3: Cambiar a endpoints síncronos (def en lugar de async def)
@router.post("", response_model=OrderResponse)
def create_order(...):  # Sin async
    ...
```

**Decisión:** Postponer optimización hasta que se requiera por métricas reales de carga.

---

### 11.2 Order Number Race Conditions

**Estado actual:**
- `generate_order_number()` usa `func.max(Order.order_number) + 1` con retry logic (3 intentos)
- Unique constraint en `order_number` previene duplicados
- `await asyncio.sleep(0.1)` entre reintentos

**Implicaciones:**
- Con **concurrencia extrema** (múltiples workers simultáneos), es posible que los 3 reintentos se agoten y la request falle con 500
- Para una factory privada con creación secuencial/moderada de órdenes, **es suficiente**

**Optimización futura (si es necesaria):**
```python
# Opción 1: Secuencia dedicada con SELECT FOR UPDATE
SELECT order_seq FROM order_sequences WHERE id = 1 FOR UPDATE;
UPDATE order_sequences SET order_seq = order_seq + 1 WHERE id = 1;

# Opción 2: Database-side auto-increment
# Usar PostgreSQL sequence directamente

# Opción 3: Atomic increment con Redis
INCR order:counter:2025
```

**Decisión:** Implementación actual protege suficientemente contra race conditions para el volumen esperado. Monitorear métricas de `IntegrityError` en producción.

---

### 11.3 Automated Testing Coverage

**Estado actual:**
- Validación manual con `curl` commands
- Sin tests automatizados para concurrency scenarios

**Optimización futura:**
```python
# pytest-asyncio test
async def test_concurrent_order_creation():
    """Simular 10 requests concurrentes creando órdenes"""
    tasks = [create_order(...) for _ in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Verificar que todas las órdenes tienen order_number único
```

**Decisión:** Agregar tests cuando se requiera CI/CD automation o después de escalar volumen.

---

### 11.4 Resumen

✅ **Production-ready para factory privada:**
- Todos los endpoints funcionando
- Validación completa con enums
- Protección básica contra race conditions
- Timestamps automáticos
- OrderResponse y OrderDetailResponse completos

⚠️ **Optimizaciones postponidas (para alta concurrencia):**
- AsyncSession para DB operations
- Atomic order number generation
- Automated concurrency tests

**Estrategia:** Implementar la Orders API ahora, monitorear métricas en producción, optimizar solo si los datos lo justifican.

---

**ORDERS API - Powering the AXON Factory 🏭🤖**
