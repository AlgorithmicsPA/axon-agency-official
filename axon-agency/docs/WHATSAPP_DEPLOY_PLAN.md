# FASE 9.1 - WhatsApp Autopilot Deploy Layer

## Objetivo

Agregar una capa de despliegue para órdenes de tipo `whatsapp_autopilot` que permite a los administradores enviar automáticamente las configuraciones completadas a n8n mediante webhook para activación en WhatsApp.

## Arquitectura

### 1. Modelo de Datos

#### Deploy Event Schema

Cada evento de deploy se almacena como un objeto JSON en el campo `deploy_history` del modelo Order:

```python
{
    "id": "uuid-v4",                      # Identificador único del evento
    "order_id": "uuid-orden",             # FK a la orden
    "channel": "whatsapp",                # Canal de deploy
    "status": "pending|success|failed",   # Estado del deploy
    "target_system": "n8n",               # Sistema destino
    "requested_at": "2025-11-17T12:00:00Z",  # Timestamp de solicitud
    "completed_at": "2025-11-17T12:00:05Z",  # Timestamp de completado (opcional)
    "error_message": "string|null",       # Mensaje de error si failed
    "webhook_url": "https://...",         # URL del webhook (sanitizado)
    "response_status": 200                # HTTP status del webhook (opcional)
}
```

#### Order Model Extension

```python
deploy_history: Optional[list[dict]] = Field(
    default=None,
    sa_column=Column(JSON),
    description="Historial de eventos de deploy a canales externos (WhatsApp, Telegram, etc.)"
)
```

**Importante:** Este campo es nullable para backward compatibility. No requiere migración de base de datos.

### 2. Payload a n8n

#### Estructura Estándar

```json
{
  "tenant": {
    "id": "uuid-tenant",
    "slug": "algorithmics-academy",
    "nombre": "Algorithmics Academy"
  },
  "order": {
    "id": "uuid-orden",
    "order_number": "ORD-2025-001",
    "tipo_producto": "whatsapp_autopilot",
    "nombre_producto": "WhatsApp Soporte Clientes",
    "estado": "listo",
    "datos_cliente": {
      "empresa": "Mi Empresa",
      "contacto": "cliente@example.com",
      "descripcion": "Bot de soporte"
    }
  },
  "agent_blueprint": {
    "version": "1.0",
    "agent_type": "conversational",
    "product_type": "whatsapp_autopilot",
    "sources": [
      {"type": "website_url", "value": "https://example.com", "notes": null}
    ],
    "channels": ["whatsapp"],
    "capabilities": ["responder_preguntas", "derivar_humano"],
    "automation_level": "semi",
    "client_profile": {...},
    "notes": "Agente para soporte 24/7"
  },
  "deliverable": {
    "metadata": {
      "order_number": "ORD-2025-001",
      "tipo_producto": "whatsapp_autopilot",
      "qa_status": "ok",
      "construido_en": "2025-11-17T10:00:00Z",
      "archivos": [
        "flows/whatsapp_flow.json",
        "config/agent_config.yaml",
        "prompts/system_prompt.txt"
      ]
    },
    "artifacts": [
      {
        "path": "flows/whatsapp_flow.json",
        "type": "n8n_workflow",
        "description": "Flujo principal de conversación WhatsApp"
      },
      {
        "path": "config/agent_config.yaml",
        "type": "configuration",
        "description": "Configuración del agente"
      },
      {
        "path": "prompts/system_prompt.txt",
        "type": "prompt",
        "description": "Prompt del sistema"
      }
    ]
  }
}
```

#### Casos Especiales

**Tenant NULL (Órdenes Legacy):**
```json
{
  "tenant": null,
  "order": {...},
  ...
}
```

**Sin Deliverable Generado:**
```json
{
  "deliverable": {
    "metadata": null,
    "artifacts": []
  }
}
```

### 3. Validaciones

#### Pre-Deploy Checks

1. **Autenticación:** Usuario debe ser admin (`require_admin()`)
2. **Orden existe:** Verificar que `order_id` es válido
3. **Tipo compatible:** `tipo_producto` debe contener "whatsapp" (ej: `whatsapp_autopilot`, `autopilot_whatsapp`)
4. **Estado correcto:** `estado == "listo"`
5. **QA aprobado:** `qa_status == "ok"` (si existe)
6. **Webhook configurado:** ENV `N8N_WHATSAPP_DEPLOY_WEBHOOK_URL` debe existir

#### Respuestas de Error

```python
# Admin no autenticado
401: {"detail": "Not authenticated"}
403: {"detail": "Admin access required"}

# Validación de orden
404: {"detail": "Order not found"}
400: {"detail": "Order is not a WhatsApp-compatible product"}
400: {"detail": "Order must be in 'listo' state to deploy (current: 'construccion')"}
400: {"detail": "Order must pass QA before deploy (current qa_status: 'warn')"}

# Configuración
500: {"detail": "Deploy unavailable: N8N_WHATSAPP_DEPLOY_WEBHOOK_URL not configured"}

# Webhook error
500: {"detail": "Deploy failed: n8n webhook returned error", "error": "..."}
```

### 4. Flujo End-to-End

```
┌─────────────┐
│   Admin UI  │
│ Order Detail│
└──────┬──────┘
       │ Click "Deploy to WhatsApp"
       ▼
┌─────────────────────────────────┐
│ POST /api/orders/{id}/deploy/   │
│           whatsapp               │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Validations:                   │
│  - isAdmin?                     │
│  - Order exists?                │
│  - tipo_producto compatible?    │
│  - estado == "listo"?           │
│  - qa_status == "ok"?           │
│  - N8N_WEBHOOK_URL set?         │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Build Payload:                 │
│  - tenant (if exists)           │
│  - order data                   │
│  - agent_blueprint              │
│  - deliverable artifacts        │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  HTTP POST to n8n webhook       │
│  Content-Type: application/json │
└──────┬──────────────────────────┘
       │
       ├─────► Success (2xx)
       │       │
       │       ▼
       │   ┌─────────────────────┐
       │   │ Create deploy_event │
       │   │ status: "success"   │
       │   │ completed_at: now   │
       │   └─────────────────────┘
       │
       └─────► Error (non-2xx)
               │
               ▼
           ┌─────────────────────┐
           │ Create deploy_event │
           │ status: "failed"    │
           │ error_message: ...  │
           │ completed_at: now   │
           └─────────────────────┘
               │
               ▼
       ┌─────────────────────────────────┐
       │  Append event to                │
       │  order.deploy_history           │
       │  session.commit()               │
       └──────┬──────────────────────────┘
              │
              ▼
       ┌─────────────────────────────────┐
       │  Return response to UI:         │
       │  {                              │
       │    "status": "ok",              │
       │    "message": "Deploy sent...", │
       │    "deploy_event": {...}        │
       │  }                              │
       └─────────────────────────────────┘
```

### 5. Seguridad y Sanitización

#### Datos NO Incluidos en Payload

- Rutas absolutas del filesystem de Axon 88 Builder
- Secrets de ENV (API keys, tokens)
- Contraseñas o credenciales
- IDs internos de sesiones de Builder

#### Datos Sanitizados

```python
# ❌ MAL
"repo_path": "/home/axon88/builds/ORD-2025-001"

# ✅ BIEN
"order_number": "ORD-2025-001"
"artifacts": ["flows/whatsapp_flow.json"]  # rutas relativas
```

#### Logging Seguro

```python
# ❌ NO loguear
logger.info(f"Deploying to {N8N_WHATSAPP_DEPLOY_WEBHOOK_URL}")

# ✅ Loguear sin secrets
logger.info(f"Deploying order {order.order_number} to n8n WhatsApp webhook")
```

### 6. UI/UX

#### Botón "Deploy to WhatsApp"

**Condiciones de Visibilidad:**
- Usuario es admin
- `tipo_producto` contiene "whatsapp"
- `estado === "listo"`
- `qa_status === "ok"` (si existe)

**Estados:**
- **Default:** Botón azul con icono MessageCircle
- **Loading:** Spinner + texto "Deploying..." + botón deshabilitado
- **Success:** Toast verde "📲 Deploy enviado a n8n correctamente"
- **Error:** Toast rojo con mensaje de error del backend

#### Deploy History Card

**Ubicación:** Debajo de AgentBlueprintCard en order detail page

**Contenido:**
```
┌─────────────────────────────────────────┐
│ Deploy History (WhatsApp)               │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ whatsapp • success                  │ │
│ │ Requested: 17 Nov 2025, 12:00       │ │
│ │ Completed: 17 Nov 2025, 12:00 (5s)  │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ whatsapp • failed                   │ │
│ │ Requested: 17 Nov 2025, 11:00       │ │
│ │ Error: Webhook timeout              │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Empty state:                            │
│ "No se han realizado deploys aún"      │
└─────────────────────────────────────────┘
```

**Visibilidad:** Solo admin (wrapeado en `<AdminOnly>`)

### 7. Variables de Entorno

```bash
# .env o .env.local
N8N_WHATSAPP_DEPLOY_WEBHOOK_URL=https://n8n.example.com/webhook/whatsapp-deploy
```

**Configuración en n8n:**
1. Crear webhook node en n8n
2. Configurar como POST endpoint
3. Copiar URL del webhook
4. Agregar a ENV de Axon Agency API

### 8. Casos Edge

#### Orden sin Tenant (Legacy)

```json
{
  "tenant": null,
  "order": {...}
}
```

n8n debe manejar este caso gracefully.

#### Orden sin Deliverable

```json
{
  "deliverable": {
    "metadata": null,
    "artifacts": []
  }
}
```

n8n puede decidir rechazar o proceder con configuración mínima.

#### Múltiples Deploys

El sistema permite múltiples deploys de la misma orden:
- Caso de uso: re-deploy después de correcciones
- Cada deploy crea un nuevo evento en `deploy_history`
- No hay límite de cantidad

#### Webhook Timeout

Si n8n no responde en 30 segundos:
- httpx timeout exception
- Registrar como `status: "failed"`
- `error_message: "Webhook request timeout"`

#### Webhook Returns Non-2xx

```python
if response.status_code >= 400:
    status = "failed"
    error_message = f"Webhook returned {response.status_code}: {response.text[:200]}"
```

### 9. Testing

#### Test Cases

1. **Happy Path - Admin + WhatsApp Ready**
   - Precondiciones: admin logged in, orden whatsapp_autopilot, estado=listo, qa_status=ok
   - Acción: Click "Deploy to WhatsApp"
   - Esperado: 
     - Request POST a n8n webhook
     - deploy_history actualizado con evento success
     - Toast success "📲 Deploy enviado..."
     - Card Deploy History muestra nuevo evento

2. **Validación - Orden No WhatsApp**
   - Precondiciones: admin logged in, orden landing-builder
   - Esperado: Botón "Deploy to WhatsApp" NO visible

3. **Validación - Orden No Lista**
   - Precondiciones: admin, orden whatsapp pero estado=construccion
   - Esperado: Botón NO visible o deshabilitado

4. **Validación - QA Failed**
   - Precondiciones: admin, orden whatsapp, estado=listo, qa_status=fail
   - Esperado: Botón NO visible

5. **Seguridad - No Admin**
   - Precondiciones: user no admin, orden whatsapp lista
   - Esperado: 
     - Botón NO visible
     - Si intenta POST directo: 403 Forbidden

6. **Config - Sin Webhook URL**
   - Precondiciones: N8N_WHATSAPP_DEPLOY_WEBHOOK_URL no definida
   - Acción: Click deploy
   - Esperado: Error 500 "Deploy no disponible: falta N8N_WHATSAPP_DEPLOY_WEBHOOK_URL"

7. **Multi-tenant - Tenant Asociado**
   - Precondiciones: orden con tenant_id válido
   - Acción: Deploy
   - Esperado: Payload incluye tenant data completo

8. **Multi-tenant - Orden Legacy**
   - Precondiciones: orden con tenant_id = null
   - Acción: Deploy
   - Esperado: Payload incluye "tenant": null

9. **Error Handling - Webhook Timeout**
   - Precondiciones: n8n webhook no responde
   - Esperado: 
     - deploy_history con status="failed"
     - error_message="Webhook request timeout"
     - Toast error al usuario

10. **Error Handling - Webhook Error Response**
    - Precondiciones: n8n webhook responde 500
    - Esperado:
      - deploy_history con status="failed"
      - error_message con status code y mensaje
      - Toast error al usuario

### 10. Próximos Pasos (FASE 9.2+)

Esta implementación sienta las bases para:

1. **FASE 9.2 - Multi-Channel Deploy:**
   - Telegram: `/deploy/telegram`
   - Email: `/deploy/email`
   - Slack: `/deploy/slack`
   - Mismo patrón, diferentes webhooks

2. **FASE 9.3 - Deploy Status Tracking:**
   - Webhook de n8n de vuelta a Axon Agency
   - Actualizar status de "pending" a "deployed" o "active"
   - Mostrar si el agente está corriendo en WhatsApp

3. **FASE 9.4 - Deploy Rollback:**
   - Botón "Rollback Deploy"
   - Enviar señal a n8n para desactivar
   - Registrar evento de rollback en history

4. **FASE 9.5 - Deploy Metrics:**
   - Contadores de mensajes procesados
   - Uptime del agente
   - Errores reportados

## Archivos Modificados

### Backend
- `apps/api/app/models/orders.py` - Agregar campo `deploy_history`
- `apps/api/app/routers/orders.py` - Agregar endpoint `/deploy/whatsapp`
- `apps/api/app/core/config.py` - Agregar ENV var `N8N_WHATSAPP_DEPLOY_WEBHOOK_URL`

### Frontend
- `apps/web/app/agent/orders/[id]/page.tsx` - Agregar botón deploy + history card
- `apps/web/components/orders/DeployHistoryCard.tsx` - Nuevo componente (opcional)

### Docs
- `docs/WHATSAPP_DEPLOY_PLAN.md` - Este documento
- `replit.md` - Actualizar con FASE 9.1 status

## Ejemplo de Uso

### 1. Configurar Webhook n8n

```bash
# En n8n, crear workflow con webhook node
# Copiar URL: https://n8n.example.com/webhook/abc123

# Agregar a .env de Axon Agency API
echo "N8N_WHATSAPP_DEPLOY_WEBHOOK_URL=https://n8n.example.com/webhook/abc123" >> .env
```

### 2. Crear Orden WhatsApp

```bash
# Via UI o API
POST /api/orders
{
  "tipo_producto": "whatsapp_autopilot",
  "nombre_producto": "Bot Soporte Clientes",
  "datos_cliente": {...},
  "tenant_id": "uuid-tenant"
}
```

### 3. Completar Pipeline

- Estado: nuevo → planificacion → construccion → qa → listo
- QA status: ok

### 4. Deploy

- Admin accede a `/agent/orders/{id}`
- Ve botón "Deploy to WhatsApp"
- Click → POST a n8n
- Deploy history actualizado
- n8n recibe payload completo y activa agente

## Conclusión

FASE 9.1 implementa la base de un sistema de deploy modular y extensible que:

✅ Mantiene backward compatibility (campo nullable)
✅ Respeta multi-tenancy (incluye tenant en payload)
✅ Es seguro (validaciones + sanitización)
✅ Es extensible (fácil agregar más canales)
✅ Es auditable (deploy_history completo)
✅ No toca Axon 88 (solo API + UI de Axon Agency)

Ready para FASE 9.2 - más canales de deploy.
