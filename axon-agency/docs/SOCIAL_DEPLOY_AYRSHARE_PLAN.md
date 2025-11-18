# FASE 9.S - Social Autopilot Deploy via Ayrshare

## Objetivo

Agregar una capa de despliegue para órdenes de tipo `social_autopilot` que permite a los administradores publicar automáticamente contenido en múltiples redes sociales (Twitter, Facebook, Instagram) mediante la API de Ayrshare.

## Arquitectura

### 1. Modelo de Datos

#### Deploy Event Schema

Cada evento de deploy se almacena como un objeto JSON en el campo `deploy_history` del modelo Order (reutilizando estructura de FASE 9.1):

```python
{
    "id": "uuid-v4",                      # Identificador único del evento
    "order_id": "uuid-orden",             # FK a la orden
    "channel": "social",                  # Canal de deploy
    "status": "pending|success|failed",   # Estado del deploy
    "target_system": "ayrshare",          # Sistema destino
    "requested_at": "2025-11-17T12:00:00Z",  # Timestamp de solicitud
    "completed_at": "2025-11-17T12:00:05Z",  # Timestamp de completado (opcional)
    "error_message": "string|null",       # Mensaje de error si failed
    "platforms": ["twitter", "facebook", "instagram"],  # Plataformas publicadas
    "response_status": 200,               # HTTP status de Ayrshare (opcional)
    "ayrshare_post_id": "string|null"     # ID del post en Ayrshare (si success)
}
```

#### Order Model Extension

**NOTA:** Reutilizamos el campo existente `deploy_history` del modelo Order. No se requiere migración de base de datos.

```python
deploy_history: Optional[list[dict]] = Field(
    default=None,
    sa_column=Column(JSON),
    description="Historial de eventos de deploy a canales externos (WhatsApp, Telegram, Social, etc.)"
)
```

### 2. Payload a Ayrshare

#### Estructura Estándar

```json
{
  "post": "¡Nuevo autopilot disponible! 🤖 Ahora puedes automatizar tus redes sociales con IA. #IA #Automatización #SocialMedia",
  "platforms": ["twitter", "facebook", "instagram"],
  "mediaUrls": [
    "https://example.com/media/screenshot.png"
  ],
  "scheduleDate": null,
  "profileKey": null
}
```

#### Endpoint Ayrshare

```
POST https://app.ayrshare.com/api/post
Headers:
  Authorization: Bearer {AYRSHARE_API_KEY}
  Content-Type: application/json
```

#### Response Exitosa (2xx)

```json
{
  "status": "success",
  "id": "ayr-post-id-12345",
  "postIds": {
    "twitter": "1234567890",
    "facebook": "fb_post_id",
    "instagram": "ig_media_id"
  }
}
```

#### Response Error (4xx/5xx)

```json
{
  "status": "error",
  "message": "API key invalid or expired"
}
```

### 3. Validaciones

#### Pre-Deploy Checks

1. **Autenticación:** Usuario debe ser admin (`require_admin()`)
2. **Orden existe:** Verificar que `order_id` es válido
3. **Tipo compatible:** `tipo_producto` debe contener "social" (ej: `social_autopilot`, `autopilot_social`)
4. **Estado correcto:** `estado == "listo"`
5. **QA aprobado:** `qa_status == "ok"` (si existe)
6. **API Key configurado:** ENV `AYRSHARE_API_KEY` debe existir y no estar vacío

#### Respuestas de Error

```python
# Admin no autenticado
401: {"detail": "Not authenticated"}
403: {"detail": "Admin access required"}

# Validación de orden
404: {"detail": "Order not found"}
400: {"detail": "Order is not a Social-compatible product"}
400: {"detail": "Order must be in 'listo' state to deploy (current: 'construccion')"}
400: {"detail": "Order must pass QA before deploy (current qa_status: 'warn')"}

# Configuración
500: {"detail": "Deploy unavailable: AYRSHARE_API_KEY not configured"}

# Ayrshare API error
500: {"detail": "Deploy failed: Ayrshare API returned error", "error": "..."}
```

### 4. Flujo End-to-End

```
┌─────────────┐
│   Admin UI  │
│ Order Detail│
└──────┬──────┘
       │ Click "Deploy to Social (Ayrshare)"
       ▼
┌─────────────────────────────────┐
│ POST /api/orders/{id}/deploy/   │
│           social                 │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Validations:                   │
│  - isAdmin?                     │
│  - Order exists?                │
│  - tipo_producto contains "social"? │
│  - estado == "listo"?           │
│  - qa_status == "ok"?           │
│  - AYRSHARE_API_KEY set?        │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Extract Content:               │
│  - text (from deliverable or    │
│    agent_blueprint)             │
│  - platforms (default: all)     │
│  - mediaUrls (from artifacts)   │
│  - scheduleDate (optional)      │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  POST to Ayrshare API           │
│  /api/post endpoint             │
│  Authorization: Bearer {key}    │
└──────┬──────────────────────────┘
       │
       ├─────► Success (2xx)
       │       │
       │       ▼
       │   ┌─────────────────────┐
       │   │ Create deploy_event │
       │   │ status: "success"   │
       │   │ ayrshare_post_id    │
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

#### Datos NO Incluidos en Logs

- API key de Ayrshare (NUNCA loguear)
- Rutas absolutas del filesystem
- Secrets de ENV
- Profile keys sensibles

#### Datos Sanitizados

```python
# ❌ MAL
logger.info(f"Deploying to Ayrshare with API key: {settings.ayrshare_api_key}")

# ✅ BIEN
logger.info(f"Deploying order {order.order_number} to Ayrshare API")

# ❌ MAL (en deploy event)
"ayrshare_api_key": settings.ayrshare_api_key

# ✅ BIEN (en deploy event)
"platforms": ["twitter", "facebook", "instagram"]
```

#### Logging Seguro

```python
# ✅ CORRECTO
logger.info(f"Deploying order {order.order_number} to Ayrshare social platforms")
logger.info(f"Ayrshare deploy successful for order {order.order_number}")

# ❌ INCORRECTO
logger.info(f"API key: {api_key}")
logger.info(f"Deploying to {settings.ayrshare_base_url} with key {api_key[:10]}...")
```

### 6. Extracción de Contenido

#### Texto del Post

**Prioridad de fuentes:**

1. `deliverable_metadata.social_post_text` (si existe)
2. `agent_blueprint.notes` (fallback)
3. `order.nombre_producto` + descripción genérica (último fallback)

```python
# Ejemplo de extracción
if order.deliverable_metadata and order.deliverable_metadata.get("social_post_text"):
    post_text = order.deliverable_metadata["social_post_text"]
elif order.agent_blueprint and order.agent_blueprint.get("notes"):
    post_text = order.agent_blueprint["notes"]
else:
    post_text = f"Nuevo autopilot disponible: {order.nombre_producto}"
```

#### Plataformas

**Default:** `["twitter", "facebook", "instagram"]`

**Customización (futuro):** Leer de `agent_blueprint.channels` o `datos_cliente.platforms`

#### Media URLs

**Fuentes:**

1. Buscar archivos de imagen en `deliverable_metadata.archivos`
2. Convertir a URLs públicas (si están en storage)
3. **Limitación actual:** Solo URLs públicas permitidas

```python
# Ejemplo
media_urls = []
if order.deliverable_metadata and order.deliverable_metadata.get("archivos"):
    for archivo in order.deliverable_metadata["archivos"]:
        if archivo.endswith((".png", ".jpg", ".jpeg", ".gif")):
            # En futuro, convertir a URL pública
            # Por ahora, solo si ya es URL
            if archivo.startswith("http"):
                media_urls.append(archivo)
```

### 7. UI/UX

#### Botón "Deploy to Social (Ayrshare)"

**Condiciones de Visibilidad:**
- Usuario es admin
- `tipo_producto` contiene "social"
- `estado === "listo"`
- `qa_status === "ok"` (si existe)

**Estados:**
- **Default:** Botón con icono Share2 (de lucide-react)
- **Loading:** Spinner + texto "Deploying to Social..." + botón deshabilitado
- **Success:** Toast "🚀 Social deploy enviado a Ayrshare correctamente"
- **Error:** Toast rojo con mensaje de error del backend

**Ubicación:** Junto al botón "Deploy to WhatsApp" (si existe)

#### Deploy History Card (Unified)

**Opción A: Card Unificada (RECOMENDADA)**

Mostrar todos los deploy events (WhatsApp + Social + futuros canales) en una sola card:

```
┌─────────────────────────────────────────┐
│ Deploy History                          │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📲 whatsapp • success               │ │
│ │ Requested: 17 Nov 2025, 12:00       │ │
│ │ Completed: 17 Nov 2025, 12:00 (5s)  │ │
│ │ Target: n8n                         │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 🚀 social • success                 │ │
│ │ Requested: 17 Nov 2025, 13:00       │ │
│ │ Completed: 17 Nov 2025, 13:00 (3s)  │ │
│ │ Target: ayrshare                    │ │
│ │ Platforms: Twitter, Facebook        │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Empty state:                            │
│ "No se han realizado deploys aún"      │
└─────────────────────────────────────────┘
```

**Iconos por canal:**
- `whatsapp`: `<MessageCircle />` (📲)
- `social`: `<Share2 />` (🚀)
- `telegram`: `<Send />` (futuro)
- `email`: `<Mail />` (futuro)

**Visibilidad:** Solo admin (wrapeado en `<AdminOnly>`)

### 8. Variables de Entorno

```bash
# .env o axon-agency/apps/api/.env
AYRSHARE_API_KEY=your-ayrshare-api-key-here
AYRSHARE_BASE_URL=https://app.ayrshare.com/api
ENABLE_AYRSHARE_SOCIAL=true
```

**Configuración en Ayrshare:**
1. Registrarse en https://www.ayrshare.com/
2. Conectar redes sociales (Twitter, Facebook, Instagram)
3. Obtener API key desde dashboard
4. Agregar API key a ENV de Axon Agency API
5. Activar `ENABLE_AYRSHARE_SOCIAL=true`

**Opt-in:** Si `AYRSHARE_API_KEY` está vacío, la feature está deshabilitada (botón no visible).

### 9. Casos Edge

#### Orden sin Deliverable Text

Si no hay `social_post_text` en deliverable:

```python
post_text = f"Nuevo autopilot disponible: {order.nombre_producto}"
```

#### Orden sin Media

Ayrshare permite posts sin media:

```json
{
  "post": "Texto del post",
  "platforms": ["twitter"],
  "mediaUrls": []  # Vacío OK
}
```

#### Múltiples Deploys

El sistema permite múltiples deploys de la misma orden:
- Caso de uso: re-publicar contenido actualizado
- Cada deploy crea un nuevo evento en `deploy_history`
- No hay límite de cantidad

#### API Timeout

Si Ayrshare no responde en 30 segundos:
- httpx timeout exception
- Registrar como `status: "failed"`
- `error_message: "Ayrshare API request timeout"`

#### API Returns Non-2xx

```python
if response.status_code >= 400:
    status = "failed"
    error_message = f"Ayrshare API returned {response.status_code}: {response.text[:200]}"
```

#### Plataforma No Conectada

Si el usuario no conectó Instagram en Ayrshare:

```json
{
  "status": "error",
  "message": "Instagram profile not connected to Ayrshare account"
}
```

**Manejo:** Registrar error en deploy_history y mostrar mensaje claro al admin.

### 10. Testing

#### Test Cases

1. **Happy Path - Admin + Social Ready**
   - Precondiciones: admin logged in, orden social_autopilot, estado=listo, qa_status=ok, AYRSHARE_API_KEY configurado
   - Acción: Click "Deploy to Social"
   - Esperado: 
     - Request POST a Ayrshare API
     - deploy_history actualizado con evento success
     - Toast success "🚀 Social deploy enviado..."
     - Card Deploy History muestra nuevo evento con icono Share2

2. **Validación - Orden No Social**
   - Precondiciones: admin logged in, orden whatsapp_autopilot
   - Esperado: Botón "Deploy to Social" NO visible

3. **Validación - Orden No Lista**
   - Precondiciones: admin, orden social pero estado=construccion
   - Esperado: Botón NO visible o deshabilitado

4. **Validación - QA Failed**
   - Precondiciones: admin, orden social, estado=listo, qa_status=fail
   - Esperado: Botón NO visible

5. **Seguridad - No Admin**
   - Precondiciones: user no admin, orden social lista
   - Esperado: 
     - Botón NO visible
     - Si intenta POST directo: 403 Forbidden

6. **Config - Sin API Key**
   - Precondiciones: AYRSHARE_API_KEY no definida
   - Acción: Click deploy
   - Esperado: Error 500 "Deploy no disponible: AYRSHARE_API_KEY not configured"

7. **Multi-Channel Deploy History**
   - Precondiciones: orden con deploys a whatsapp Y social
   - Acción: Ver order detail page
   - Esperado: Deploy History Card muestra ambos eventos con iconos diferentes

8. **Error Handling - API Timeout**
   - Precondiciones: Ayrshare API no responde
   - Esperado: 
     - deploy_history con status="failed"
     - error_message="Ayrshare API request timeout"
     - Toast error al usuario

9. **Error Handling - API Error Response**
    - Precondiciones: Ayrshare API responde 401 (invalid key)
    - Esperado:
      - deploy_history con status="failed"
      - error_message con status code y mensaje
      - Toast error al usuario

10. **No Conflict with WhatsApp Deploy**
    - Precondiciones: código WhatsApp deploy ya implementado
    - Acción: Implementar social deploy
    - Esperado: WhatsApp deploy sigue funcionando sin cambios

### 11. Ayrshare Client Implementation

#### Archivo: `apps/api/app/integrations/ayrshare_client.py`

```python
"""Ayrshare API client for social media publishing."""

import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)


class AyrshareError(Exception):
    """Custom exception for Ayrshare API errors."""
    pass


async def post_to_social(
    api_key: str,
    base_url: str,
    text: str,
    platforms: list[str],
    media_urls: Optional[list[str]] = None,
    schedule_iso: Optional[str] = None,
    profile_key: Optional[str] = None,
) -> dict:
    """
    Publicar contenido en redes sociales vía Ayrshare API.
    
    Args:
        api_key: Ayrshare API key (Bearer token)
        base_url: Base URL de Ayrshare API (ej: https://app.ayrshare.com/api)
        text: Texto del post
        platforms: Lista de plataformas ['twitter', 'facebook', 'instagram']
        media_urls: URLs de imágenes/videos a incluir (opcional)
        schedule_iso: Fecha/hora de publicación programada en ISO 8601 (opcional)
        profile_key: Profile key para multi-perfil (opcional)
    
    Returns:
        dict: Response de Ayrshare API
        {
            "status": "success",
            "id": "ayr-post-id",
            "postIds": {"twitter": "123", "facebook": "456"}
        }
    
    Raises:
        AyrshareError: Si la API retorna error o falla la request
    """
    # NUNCA loguear API key completo
    logger.info(f"Posting to Ayrshare social platforms: {', '.join(platforms)}")
    
    # Construir payload
    payload = {
        "post": text,
        "platforms": platforms
    }
    
    if media_urls:
        payload["mediaUrls"] = media_urls
    
    if schedule_iso:
        payload["scheduleDate"] = schedule_iso
    
    if profile_key:
        payload["profileKey"] = profile_key
    
    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # POST request
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/post",
                json=payload,
                headers=headers
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"Ayrshare post successful: {data.get('id', 'unknown')}")
            
            return data
    
    except httpx.HTTPStatusError as e:
        error_msg = f"Ayrshare API returned {e.response.status_code}"
        
        try:
            error_data = e.response.json()
            error_msg += f": {error_data.get('message', 'Unknown error')}"
        except:
            error_msg += f": {e.response.text[:200]}"
        
        logger.error(f"Ayrshare API error: {error_msg}")
        raise AyrshareError(error_msg)
    
    except httpx.TimeoutException:
        error_msg = "Ayrshare API request timeout (30s)"
        logger.error(error_msg)
        raise AyrshareError(error_msg)
    
    except Exception as e:
        error_msg = f"Ayrshare API exception: {str(e)[:200]}"
        logger.error(error_msg)
        raise AyrshareError(error_msg)
```

### 12. Próximos Pasos (Roadmap Futuro)

Esta implementación sienta las bases para:

1. **Analytics Integration:**
   - Webhook de Ayrshare para recibir analytics (likes, shares, comments)
   - Dashboard de performance de posts
   - Métricas de engagement por plataforma

2. **Scheduled Publishing:**
   - UI para seleccionar fecha/hora de publicación
   - Calendar view de posts programados
   - Editar/cancelar scheduled posts

3. **Multi-Profile Support:**
   - Seleccionar perfiles específicos de Ayrshare
   - Deploy a diferentes cuentas de cliente
   - Gestión de profile keys

4. **Media Upload:**
   - Subir imágenes desde Axon Agency
   - Conversión de storage local a URLs públicas
   - Optimización de media para cada plataforma

5. **Content Variations:**
   - Diferentes textos por plataforma (Twitter 280 chars, FB más largo)
   - Hashtags personalizados por red social
   - Adaptación automática de contenido

6. **Ayrshare Webhooks:**
   - Recibir callbacks de publish success/failure
   - Actualizar deploy_history con post IDs reales
   - Notificaciones de moderación o errores

## Archivos Modificados/Creados

### Backend
- `apps/api/app/core/config.py` - ✅ Agregar ENV vars Ayrshare
- `apps/api/app/integrations/__init__.py` - ✅ Crear si no existe
- `apps/api/app/integrations/ayrshare_client.py` - ✅ Nuevo archivo
- `apps/api/app/routers/orders.py` - ✅ Agregar endpoint `/deploy/social`

### Frontend
- `apps/web/app/agent/orders/[id]/page.tsx` - ✅ Agregar botón + unified Deploy History Card

### Docs
- `docs/SOCIAL_DEPLOY_AYRSHARE_PLAN.md` - ✅ Este documento
- `replit.md` - Actualizar con FASE 9.S status

## Ejemplo de Uso

### 1. Configurar Ayrshare API Key

```bash
# En .env de Axon Agency API
echo "AYRSHARE_API_KEY=YOUR_AYRSHARE_API_KEY_HERE" >> axon-agency/apps/api/.env
echo "ENABLE_AYRSHARE_SOCIAL=true" >> axon-agency/apps/api/.env
```

### 2. Crear Orden Social Autopilot

```bash
# Via UI o API
POST /api/orders
{
  "tipo_producto": "social_autopilot",
  "nombre_producto": "Social Media Manager Bot",
  "datos_cliente": {
    "empresa": "Mi Startup",
    "industria": "Tech",
    "target_platforms": ["twitter", "linkedin"]
  },
  "tenant_id": "uuid-tenant"
}
```

### 3. Completar Pipeline

- Estado: nuevo → planificacion → construccion → qa → listo
- QA status: ok
- Deliverable generado con `social_post_text`

### 4. Deploy

- Admin accede a `/agent/orders/{id}`
- Ve botón "Deploy to Social (Ayrshare)"
- Click → POST a Ayrshare API
- Deploy history actualizado con channel='social'
- Post publicado en Twitter, Facebook, Instagram simultáneamente

## Conclusión

FASE 9.S implementa social media deploy siguiendo el mismo patrón modular y extensible de FASE 9.1:

✅ Backward compatible (reutiliza deploy_history)
✅ Multi-channel ready (unified Deploy History Card)
✅ Seguro (API key sanitizado, validaciones completas)
✅ Extensible (fácil agregar más features de Ayrshare)
✅ Auditable (deploy_history completo con timestamps)
✅ No interfiere con WhatsApp Deploy (código totalmente separado)

Ready para extender con analytics, scheduled posts, multi-profile y más features de Ayrshare API.
