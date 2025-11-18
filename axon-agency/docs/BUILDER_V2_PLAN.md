# Builder v2 Integration Plan - QA + Deliverable

**Estado:** 📋 Diseño aprobado - Pendiente implementación  
**Fecha:** Noviembre 15, 2025  
**Autor:** Federico @ AXON Agency  
**Versión:** 1.0.0

---

## 1. Resumen Ejecutivo

### ¿Qué es Builder v2?

**Builder v2** es la segunda generación del sistema de construcción de productos en Axon 88 (Jetson Orin Nano). Mientras que **Builder v1** construye el producto físico en `/home/axon88/factory/products/`, **Builder v2** añade dos capacidades críticas:

1. **QA Automático (Quality Assurance)**
   - Validación estructural de productos construidos
   - Checks de archivos requeridos (order.json, plan.json, spec.md)
   - Verificación de integridad antes de entregar al cliente
   - Generación de reportes con status (ok/warn/fail)

2. **Deliverable Packaging**
   - Empaquetado profesional del producto terminado
   - Generación de SUMMARY.md con detalles completos
   - Archivo meta.json con metadata estructurada
   - ZIP del producto listo para entrega
   - Almacenamiento en `/home/axon88/factory/deliverables/`

### ¿Por qué Replit debe conocer QA + Deliverable?

Replit es el **cerebro de la fábrica** - el portal donde Federico y operadores:
- Monitorean el estado completo de órdenes
- Verifican que productos pasen QA antes de entrega
- Acceden a metadata y paquetes finales
- Toman decisiones sobre aprobar/rechazar entregas

**Actualmente (Builder v1):**
- Replit solo sabe si Axon 88 construyó el producto (`product_path`)
- No puede verificar si pasó QA
- No puede acceder a metadata del deliverable
- No puede descargar paquetes finales

**Con Builder v2 integrado:**
- Replit conocerá el estado de QA por orden
- Expondrá metadata del deliverable (sin rutas sensibles)
- Permitirá visualizar y eventualmente descargar ZIPs
- Dashboard completo del ciclo de vida: Order → Plan → Build → **QA → Deliverable** → Entrega

---

## 2. Modelo Mental del Flujo Actualizado

### Flujo Completo: Order → Entrega

```
┌─────────────────────────────────────────────────────────────────────┐
│ REPLIT (Cerebro - Cloud)                                            │
│                                                                      │
│  1. Order creada (estado: nuevo)                                    │
│     POST /api/orders                                                │
│                                                                      │
│  2. Plan generado (estado: planificacion)                           │
│     POST /api/factory/process-orders                                │
│     → LLM genera plan JSON estructurado                             │
│                                                                      │
│  3. Build delegado a Axon 88 (estado: construccion)                 │
│     POST https://api-axon88.algorithmicsai.com/factory/build-local  │
│     → Replit envía: {order_number, plan, tipo_producto}            │
│                                                                      │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ Cloudflare Tunnel (HTTPS)
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ AXON 88 (Fábrica - Local Jetson)                                    │
│                                                                      │
│  4. Builder v1 construye producto                                   │
│     /home/axon88/factory/products/ORD-2025-NNN_tipo_producto/       │
│     → FastAPI backend, Next.js frontend, DB schemas, etc.           │
│                                                                      │
│  5. Builder v2 ejecuta QA                                           │
│     qa_runner.py → run_qa_and_package()                             │
│     → Valida archivos requeridos: order.json, plan.json, spec.md   │
│     → Genera reporte QA: {status: ok/warn/fail, messages: [...]}   │
│                                                                      │
│  6. Builder v2 genera Deliverable                                   │
│     /home/axon88/factory/deliverables/ORD-2025-NNN_tipo/            │
│     → SUMMARY.md (reporte legible)                                  │
│     → meta.json (metadata estructurada)                             │
│     → ORD-2025-NNN_tipo.zip (paquete completo)                      │
│                                                                      │
│  7. Axon 88 responde a Replit con resultado completo                │
│     {                                                                │
│       "success": true,                                               │
│       "product_path": "/home/axon88/.../ORD-2025-NNN_tipo/",        │
│       "deliverable_dir": "/home/axon88/.../ORD-2025-NNN_tipo/",     │
│       "zip_path": "/home/axon88/.../ORD-2025-NNN_tipo.zip",         │
│       "qa": {                                                        │
│         "status": "ok",                                              │
│         "messages": ["All required files present"],                 │
│         "checked_files": ["order.json", "plan.json", "spec.md"]     │
│       },                                                             │
│       "construido_en": "2025-11-15T14:30:00"                        │
│     }                                                                │
│                                                                      │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ Response vía Cloudflare Tunnel
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ REPLIT (Cerebro - Cloud)                                            │
│                                                                      │
│  8. Replit actualiza Order con QA + Deliverable                     │
│     PATCH /api/orders/{id}                                          │
│     → product_path, construido_en (como antes)                      │
│     → qa_status: "ok"                                               │
│     → qa_messages: [...]                                            │
│     → deliverable_metadata: {generado_en, archivos}                 │
│     → estado: "listo" (si QA = ok)                                  │
│                                                                      │
│  9. Federico consulta QA y Deliverable                              │
│     GET /api/orders/{id}/qa                                         │
│     GET /api/orders/{id}/deliverable                                │
│                                                                      │
│  10. Dashboard /agent muestra estado completo                       │
│      ✅ QA: ok | ⚠️ warn | ❌ fail                                  │
│      📦 Deliverable: listo para descarga                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### División de Responsabilidades

| Componente | Responsabilidad | Ubicación |
|------------|-----------------|-----------|
| **Replit (cerebro)** | Orchestración, planificación, estado de órdenes, UI para Federico | Cloud (Replit workspace) |
| **Axon 88 Builder v1** | Construcción física del producto (código, DB, configs) | Jetson Orin Nano (`~/factory/products/`) |
| **Axon 88 Builder v2** | QA automático + empaquetado de deliverables | Jetson Orin Nano (`~/factory/deliverables/`) |
| **Cloudflare Tunnel** | Comunicación segura Replit ↔ Axon 88 | `https://api-axon88.algorithmicsai.com` |

---

## 3. Diseño de API en Replit (Propuesta)

### 3.1 Modelo de Datos: Extensión de Order

Agregar campos nuevos al modelo `Order` (SQLModel) en `app/models/orders.py`:

```python
class Order(SQLModel, table=True):
    # ... campos existentes ...
    
    # Builder v2 - QA fields
    qa_status: Optional[str] = Field(
        default=None, 
        description="QA status: ok | warn | fail | null (no ejecutado)"
    )
    qa_messages: Optional[List[str]] = Field(
        default=None, 
        sa_column=Column(JSON), 
        description="Lista de mensajes del QA check"
    )
    qa_checked_files: Optional[List[str]] = Field(
        default=None, 
        sa_column=Column(JSON),
        description="Archivos validados durante QA"
    )
    qa_ejecutado_en: Optional[datetime] = Field(
        default=None,
        description="Timestamp cuando se ejecutó QA en Axon 88"
    )
    
    # Builder v2 - Deliverable fields
    deliverable_generado: bool = Field(
        default=False, 
        description="True si Axon 88 generó deliverable"
    )
    deliverable_metadata: Optional[Dict[str, Any]] = Field(
        default=None, 
        sa_column=Column(JSON),
        description="Metadata del deliverable (sin rutas sensibles)"
    )
    deliverable_generado_en: Optional[datetime] = Field(
        default=None,
        description="Timestamp cuando se generó deliverable en Axon 88"
    )
```

**Importante:** Estos campos se llenan cuando Axon 88 responde exitosamente con el resultado de Builder v2.

---

### 3.2 Endpoint: GET /api/orders/{order_id}/qa

**Descripción:** Retorna el estado de QA y mensajes de una orden específica.

**Path Parameters:**
- `order_id` (UUID): ID de la orden

**Response (200 OK - QAStatusResponse):**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-013",
  "qa_executed": true,
  "qa_status": "ok",
  "qa_messages": [
    "All required files present",
    "order.json valid",
    "plan.json valid",
    "spec.md exists"
  ],
  "qa_checked_files": [
    "order.json",
    "plan.json",
    "spec.md"
  ],
  "qa_ejecutado_en": "2025-11-15T14:32:15.123456"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Orden 550e8400-e29b-41d4-a716-446655440000 no encontrada"
}
```

**Response (200 OK - QA no ejecutado todavía):**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-014",
  "qa_executed": false,
  "qa_status": null,
  "qa_messages": [],
  "qa_checked_files": [],
  "qa_ejecutado_en": null,
  "mensaje": "QA aún no se ha ejecutado para esta orden"
}
```

**Casos de uso:**
- Dashboard de Federico: mostrar badge de QA status (✅ ok, ⚠️ warn, ❌ fail)
- Review Council: verificar que producto pasó QA antes de aprobar
- Debugging: ver qué archivos faltaron si QA falló

---

### 3.3 Endpoint: GET /api/orders/{order_id}/deliverable

**Descripción:** Retorna metadata del deliverable empaquetado (sin exponer rutas internas de Axon 88).

**Path Parameters:**
- `order_id` (UUID): ID de la orden

**Response (200 OK - DeliverableResponse):**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-013",
  "has_deliverable": true,
  "qa_status": "ok",
  "generated_at": "2025-11-15T14:32:20.456789",
  "files": [
    {
      "name": "SUMMARY.md",
      "type": "markdown",
      "description": "Reporte completo del producto construido"
    },
    {
      "name": "meta.json",
      "type": "json",
      "description": "Metadata estructurada del deliverable"
    },
    {
      "name": "ORD-2025-013_autopilot_whatsapp.zip",
      "type": "zip",
      "description": "Paquete completo del producto"
    }
  ],
  "metadata": {
    "order_number": "ORD-2025-013",
    "tipo_producto": "autopilot_whatsapp",
    "qa_status": "ok",
    "construido_en": "2025-11-15T14:30:00",
    "total_archivos": 3
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Orden 550e8400-e29b-41d4-a716-446655440000 no encontrada"
}
```

**Response (200 OK - Deliverable no generado):**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-014",
  "has_deliverable": false,
  "qa_status": null,
  "generated_at": null,
  "files": [],
  "metadata": {},
  "mensaje": "Deliverable aún no generado para esta orden"
}
```

**Nota de seguridad:**
- Este endpoint **NO expone rutas absolutas** de Axon 88 (`/home/axon88/factory/...`)
- Solo devuelve metadata pública segura
- En futuras versiones, se puede añadir endpoint de descarga con signed URLs

---

### 3.4 Actualización de AxonFactoryClient

Modificar `app/services/axon_factory_client.py` para parsear respuesta extendida de Axon 88:

**Response actual de Axon 88 (Builder v1):**
```json
{
  "success": true,
  "product_path": "/home/axon88/factory/products/ORD-2025-012_autopilot_whatsapp",
  "log_path": "/home/axon88/factory/logs/orders.log",
  "construido_en": "2025-11-15T02:14:34.084390"
}
```

**Response futura de Axon 88 (Builder v2):**
```json
{
  "success": true,
  "product_path": "/home/axon88/factory/products/ORD-2025-013_autopilot_whatsapp",
  "log_path": "/home/axon88/factory/logs/orders.log",
  "construido_en": "2025-11-15T14:30:00.123456",
  "deliverable_dir": "/home/axon88/factory/deliverables/ORD-2025-013_autopilot_whatsapp",
  "zip_path": "/home/axon88/factory/deliverables/ORD-2025-013_autopilot_whatsapp/ORD-2025-013_autopilot_whatsapp.zip",
  "qa": {
    "status": "ok",
    "messages": [
      "All required files present",
      "order.json valid",
      "plan.json valid",
      "spec.md exists"
    ],
    "checked_files": ["order.json", "plan.json", "spec.md"]
  }
}
```

**Cambios necesarios en AxonFactoryClient:**
1. Parsear campos `qa` y `deliverable_dir` si están presentes
2. Manejar backward compatibility (si Axon 88 aún no tiene Builder v2, campos serán null)
3. Retornar todos los datos al orchestrator para actualizar la Order

**Pseudo-código:**
```python
class AxonFactoryClient:
    async def build_product(self, order_number: str, plan: dict, tipo_producto: str):
        response = await self.http_client.post(
            f"{self.base_url}/factory/build-local",
            json={
                "order_number": order_number,
                "plan": plan,
                "tipo_producto": tipo_producto
            }
        )
        
        data = response.json()
        
        return {
            "success": data["success"],
            "product_path": data.get("product_path"),
            "log_path": data.get("log_path"),
            "construido_en": data.get("construido_en"),
            # Builder v2 fields (pueden ser None si Axon 88 no tiene v2 todavía)
            "deliverable_dir": data.get("deliverable_dir"),
            "zip_path": data.get("zip_path"),
            "qa": data.get("qa")  # {status, messages, checked_files}
        }
```

---

### 3.5 Actualización de OrdersOrchestratorService

Modificar `_process_single_order()` para guardar datos de QA + Deliverable cuando Axon 88 responde:

**Pseudo-código:**
```python
async def _process_single_order(self, order: Order, session: Session):
    # ... código existente para generar plan ...
    
    # Llamar a Axon 88
    build_result = await self.axon_factory_client.build_product(
        order_number=order.order_number,
        plan=plan,
        tipo_producto=order.tipo_producto
    )
    
    if build_result["success"]:
        # Actualizar campos existentes
        order.product_path = build_result["product_path"]
        order.construido_en = datetime.fromisoformat(build_result["construido_en"])
        order.estado = "construccion"  # o "listo" si QA = ok
        order.asignado_a = "Axon 88 Builder"
        
        # ✨ NUEVO: Guardar QA + Deliverable si están presentes
        if build_result.get("qa"):
            qa_data = build_result["qa"]
            order.qa_status = qa_data.get("status")
            order.qa_messages = qa_data.get("messages", [])
            order.qa_checked_files = qa_data.get("checked_files", [])
            order.qa_ejecutado_en = datetime.utcnow()
            
            # Si QA pasó, marcar orden como "listo"
            if qa_data.get("status") == "ok":
                order.estado = "listo"
        
        if build_result.get("deliverable_dir"):
            order.deliverable_generado = True
            order.deliverable_metadata = {
                "order_number": order.order_number,
                "tipo_producto": order.tipo_producto,
                "qa_status": order.qa_status,
                "construido_en": build_result["construido_en"],
                "archivos": ["SUMMARY.md", "meta.json", f"{order.order_number}_{order.tipo_producto}.zip"]
            }
            order.deliverable_generado_en = datetime.utcnow()
        
        session.add(order)
        session.commit()
```

**Lógica de estados actualizada:**
- Si Axon 88 responde sin QA → estado = `"construccion"` (como antes)
- Si Axon 88 responde con QA = `ok` → estado = `"listo"` (saltar estado QA manual)
- Si Axon 88 responde con QA = `warn` o `fail` → estado = `"qa"` (requiere revisión manual)

---

## 4. Contrato Oficial: meta.json de Axon 88

### 4.1 Formato Estándar

Archivo generado por Builder v2 en `/home/axon88/factory/deliverables/{order_number}_{tipo}/meta.json`:

```json
{
  "version": "1.0.0",
  "generated_at": "2025-11-15T14:32:20.456789",
  "order_number": "ORD-2025-013",
  "tipo_producto": "autopilot_whatsapp",
  "nombre_producto": "WhatsApp Bot Ventas XYZ",
  "qa": {
    "executed": true,
    "status": "ok",
    "messages": [
      "All required files present",
      "order.json valid",
      "plan.json valid",
      "spec.md exists"
    ],
    "checked_files": [
      "order.json",
      "plan.json",
      "spec.md"
    ],
    "executed_at": "2025-11-15T14:32:15.123456"
  },
  "deliverable": {
    "deliverable_dir": "/home/axon88/factory/deliverables/ORD-2025-013_autopilot_whatsapp",
    "zip_path": "/home/axon88/factory/deliverables/ORD-2025-013_autopilot_whatsapp/ORD-2025-013_autopilot_whatsapp.zip",
    "summary_path": "/home/axon88/factory/deliverables/ORD-2025-013_autopilot_whatsapp/SUMMARY.md",
    "files": [
      {
        "name": "SUMMARY.md",
        "type": "markdown",
        "size_bytes": 2048
      },
      {
        "name": "meta.json",
        "type": "json",
        "size_bytes": 512
      },
      {
        "name": "ORD-2025-013_autopilot_whatsapp.zip",
        "type": "zip",
        "size_bytes": 1048576
      }
    ]
  },
  "product": {
    "product_path": "/home/axon88/factory/products/ORD-2025-013_autopilot_whatsapp",
    "construido_en": "2025-11-15T14:30:00.123456",
    "builder_version": "v1"
  }
}
```

### 4.2 Campos que Replit Usará

| Campo | Uso en Replit | Exponer al Cliente Final |
|-------|---------------|---------------------------|
| `order_number` | Identificación única | No |
| `tipo_producto` | Clasificación | Sí (en resultado final) |
| `qa.status` | Badge en dashboard | No (interno) |
| `qa.messages` | Debugging, logs internos | No |
| `qa.checked_files` | Verificación de completitud | No |
| `deliverable.files` | Lista de archivos disponibles | Sí (metadata segura) |
| `product_path` | **NO EXPONER** (ruta interna Axon 88) | ❌ NUNCA |
| `deliverable_dir` | **NO EXPONER** (ruta interna Axon 88) | ❌ NUNCA |
| `zip_path` | **NO EXPONER** (ruta interna Axon 88) | ❌ NUNCA |

**Regla crítica de seguridad:**
- Las rutas absolutas de Axon 88 son **internas y privadas**
- Replit las guarda en DB para operaciones internas
- **NUNCA** las expone en respuestas de API públicas
- En futuras versiones, se usarán signed URLs para descargas seguras

### 4.3 TODO: Capa de Descarga Segura

**Problema:** Cliente final necesitará descargar el ZIP del producto.

**Soluciones futuras:**
1. **Signed URLs (preferido):**
   - Axon 88 genera URL temporal con token (válida 1 hora)
   - Replit devuelve esa URL al cliente
   - Cliente descarga directamente desde Axon 88 (sin pasar por Replit)

2. **Proxy en Replit:**
   - Endpoint `GET /api/orders/{id}/deliverable/download`
   - Replit pide ZIP a Axon 88 internamente
   - Replit hace streaming del ZIP al cliente
   - Más lento pero más controlable (puede añadir logs, rate limiting)

3. **Object Storage externo:**
   - Axon 88 sube ZIP a S3/R2/DigitalOcean Spaces
   - Replit genera signed URL desde el storage
   - Más escalable para múltiples clientes concurrentes

**Decisión:** Postponer para fase 2 de implementación. Por ahora, solo exponer metadata.

---

## 5. Impacto en UI Interna (Portal /agent)

### 5.1 Vista de Detalle de Orden

En la página `/agent/orders/{order_id}`, añadir sección nueva después de "Estado de Construcción":

```
┌──────────────────────────────────────────────────────────┐
│ 📦 QA y Deliverable                                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ Estado QA:  ✅ ok | ⚠️ warn | ❌ fail | ⏳ pendiente     │
│                                                           │
│ Fecha de ejecución: 15 nov 2025, 14:32                  │
│                                                           │
│ Archivos validados:                                      │
│   • order.json                                           │
│   • plan.json                                            │
│   • spec.md                                              │
│                                                           │
│ Mensajes:                                                │
│   ✓ All required files present                          │
│   ✓ order.json valid                                    │
│   ✓ plan.json valid                                     │
│   ✓ spec.md exists                                      │
│                                                           │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                           │
│ Deliverable generado: ✅ Sí                              │
│                                                           │
│ Archivos disponibles:                                    │
│   📄 SUMMARY.md (reporte completo)                       │
│   📊 meta.json (metadata estructurada)                   │
│   📦 ORD-2025-013_autopilot_whatsapp.zip (producto)      │
│                                                           │
│ [🔒 Descargar Paquete] ← Solo administradores (futuro)  │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### 5.2 Elementos UI Mínimos Necesarios

**Componente 1: QA Status Badge**
```tsx
// Ejemplo React component
<QAStatusBadge status={order.qa_status} />

// Renderiza:
✅ QA: ok      → Badge verde
⚠️ QA: warn    → Badge amarillo
❌ QA: fail    → Badge rojo
⏳ QA: pending → Badge gris
```

**Componente 2: Deliverable Files List**
```tsx
<DeliverableFilesList 
  files={order.deliverable_metadata?.archivos || []}
  orderNumber={order.order_number}
/>

// Renderiza:
📄 SUMMARY.md
📊 meta.json
📦 ORD-2025-013_autopilot_whatsapp.zip
```

**Componente 3: Download Button (futuro - fase 2)**
```tsx
<Button 
  onClick={() => downloadDeliverable(order.id)}
  disabled={!order.deliverable_generado || !isAdmin}
>
  🔒 Descargar Paquete
</Button>
```

### 5.3 Dashboard General (/agent)

En la tabla de órdenes, añadir columna "QA":

```
| Order Number | Producto          | Estado       | QA  | Progreso |
|--------------|-------------------|--------------|-----|----------|
| ORD-2025-013 | Autopilot WA      | listo        | ✅  | 100%     |
| ORD-2025-014 | Funnel Ventas     | construccion | ⏳  | 75%      |
| ORD-2025-015 | Webhook Service   | listo        | ⚠️  | 100%     |
```

**Filtros adicionales:**
- Filtrar por QA status (ok, warn, fail, pending)
- Filtrar por "tiene deliverable" (sí/no)

---

## 6. Roadmap de Implementación

### Fase 1: Backend - Modelos y Endpoints (Estimación: 4-6 horas)

- [ ] **Tarea 1.1:** Extender modelo `Order` en `app/models/orders.py`
  - Añadir campos: `qa_status`, `qa_messages`, `qa_checked_files`, `qa_ejecutado_en`
  - Añadir campos: `deliverable_generado`, `deliverable_metadata`, `deliverable_generado_en`
  - Ejecutar migración de DB (Alembic o SQLModel auto-create)

- [ ] **Tarea 1.2:** Actualizar `AxonFactoryClient` en `app/services/axon_factory_client.py`
  - Parsear campos `qa` y `deliverable_dir` de la respuesta de Axon 88
  - Mantener backward compatibility (campos opcionales)
  - Añadir tests unitarios para parseo

- [ ] **Tarea 1.3:** Actualizar `OrdersOrchestratorService` en `app/services/orders_orchestrator.py`
  - Modificar `_process_single_order()` para guardar QA + Deliverable
  - Lógica de estados: construccion → listo si QA = ok
  - Añadir logs para debugging

- [ ] **Tarea 1.4:** Crear endpoint `GET /api/orders/{id}/qa` en `app/routers/orders.py`
  - Schema de respuesta: `QAStatusResponse`
  - Manejo de casos: QA ejecutado vs no ejecutado
  - Tests de integración

- [ ] **Tarea 1.5:** Crear endpoint `GET /api/orders/{id}/deliverable` en `app/routers/orders.py`
  - Schema de respuesta: `DeliverableResponse`
  - Filtrar rutas sensibles de Axon 88
  - Tests de integración

### Fase 2: Integración con Axon 88 (Estimación: 2-4 horas)

- [ ] **Tarea 2.1:** Coordinar con Axon 88 para confirmar formato de respuesta Builder v2
  - Verificar que `qa` y `deliverable_dir` están en la respuesta
  - Confirmar estructura de meta.json
  - Hacer test end-to-end con orden real

- [ ] **Tarea 2.2:** Testing de integración Replit ↔ Axon 88
  - Crear orden de test
  - Verificar que QA se guarda correctamente en Replit DB
  - Verificar que deliverable metadata se expone sin rutas sensibles

### Fase 3: Frontend - UI en Portal /agent (Estimación: 6-8 horas)

- [ ] **Tarea 3.1:** Crear componente `QAStatusBadge.tsx`
  - Visual design según estado (ok/warn/fail/pending)
  - Tooltip con mensajes de QA

- [ ] **Tarea 3.2:** Crear componente `DeliverableCard.tsx`
  - Mostrar archivos disponibles
  - Botón de descarga (disabled por ahora)
  - Metadata del deliverable

- [ ] **Tarea 3.3:** Actualizar página de detalle `/agent/orders/[id]`
  - Integrar `QAStatusBadge` y `DeliverableCard`
  - Fetch de datos desde `/api/orders/{id}/qa` y `/deliverable`
  - Loading states y error handling

- [ ] **Tarea 3.4:** Actualizar tabla de órdenes en dashboard `/agent`
  - Añadir columna "QA" con badge
  - Añadir filtros por QA status
  - Añadir indicador de deliverable generado

### Fase 4: Descarga Segura de Deliverables (Estimación: 8-12 horas - FUTURO)

**Nota:** Esta fase se postpone para después de validar que la integración básica funciona.

- [ ] **Tarea 4.1:** Diseñar sistema de signed URLs
  - Axon 88 genera token temporal (JWT)
  - Endpoint en Axon 88: `GET /factory/deliverables/download?token=...`
  - Expiración de 1 hora

- [ ] **Tarea 4.2:** Implementar endpoint en Replit `POST /api/orders/{id}/deliverable/request-download`
  - Replit pide signed URL a Axon 88
  - Retorna URL temporal al cliente
  - Solo administradores autorizados

- [ ] **Tarea 4.3:** Implementar descarga en UI
  - Botón "Descargar Paquete" funcional
  - Progress indicator durante descarga
  - Manejo de errores (token expirado, archivo no disponible)

- [ ] **Tarea 4.4:** Testing de seguridad
  - Verificar que URLs expiran correctamente
  - Verificar que solo administradores pueden descargar
  - Añadir audit logs de descargas

### Fase 5: Testing y Documentación (Estimación: 4-6 horas)

- [ ] **Tarea 5.1:** Tests automatizados
  - Unit tests para parseo de QA y deliverable
  - Integration tests para endpoints nuevos
  - End-to-end test de flujo completo

- [ ] **Tarea 5.2:** Actualizar documentación
  - Actualizar `ORDERS_API_SUMMARY.md` con endpoints nuevos
  - Actualizar `FACTORY_VISION.md` con sección Builder v2
  - Crear ejemplos de uso en `README.md`

- [ ] **Tarea 5.3:** Validación con Federico
  - Demo de funcionalidad completa
  - Recolectar feedback
  - Ajustes finales

---

## 7. Métricas de Éxito

### Indicadores de que Builder v2 Integration está funcionando:

1. **Backend:**
   - ✅ Campo `qa_status` se guarda correctamente en DB después de construir
   - ✅ Campo `deliverable_metadata` se guarda correctamente en DB
   - ✅ Endpoints `/qa` y `/deliverable` retornan datos correctos
   - ✅ No se exponen rutas internas de Axon 88 en respuestas de API

2. **Integración Axon 88:**
   - ✅ Response de Axon 88 incluye `qa` y `deliverable_dir`
   - ✅ Estado de orden cambia a "listo" automáticamente si QA = ok
   - ✅ Backward compatibility: órdenes antiguas sin QA siguen funcionando

3. **Frontend:**
   - ✅ Badge de QA visible en dashboard y detalle de orden
   - ✅ Lista de archivos del deliverable se muestra correctamente
   - ✅ UI refleja estado real de QA y deliverable en tiempo real

4. **Experiencia de Federico:**
   - ✅ Federico puede ver de un vistazo qué órdenes pasaron QA
   - ✅ Federico puede verificar qué archivos están en el deliverable
   - ✅ Federico tiene visibilidad completa del estado de productos sin acceder a Axon 88 directamente

---

## 8. Riesgos y Mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación |
|--------|---------|--------------|------------|
| **Axon 88 no envía campos `qa` o `deliverable_dir`** | Alto | Baja | Backward compatibility en AxonFactoryClient - campos opcionales |
| **Rutas sensibles de Axon 88 se exponen accidentalmente** | Crítico | Media | Code review obligatorio antes de merge, tests de seguridad |
| **meta.json con formato incorrecto** | Medio | Media | Validación con Pydantic schema, manejo de errores robusto |
| **Cliente final accede a rutas internas** | Crítico | Baja | Nunca exponer product_path/deliverable_dir en APIs públicas |
| **Signed URLs expiran antes de descarga completa** | Bajo | Media | Implementar refresh de token durante descarga (fase 4) |

---

## 9. Preguntas Abiertas (Para Resolver en Implementación)

1. **¿Axon 88 ya está enviando los campos `qa` y `deliverable_dir` en la respuesta?**
   - **Acción:** Coordinar con Axon (Cursor) para confirmar
   - **Timeline:** Antes de iniciar Tarea 2.1

2. **¿Qué hacer si QA = "warn"? ¿Requiere revisión manual?**
   - **Opción A:** Estado = "qa" (requiere revisión de Federico)
   - **Opción B:** Estado = "listo" pero con flag de advertencia
   - **Decisión:** Postponer para fase de implementación basado en casos reales

3. **¿Debemos validar el contenido de meta.json en Replit?**
   - **Opción A:** Confiar en Axon 88 (más rápido)
   - **Opción B:** Validar con Pydantic schema (más robusto)
   - **Decisión:** Validar con Pydantic - costo mínimo, beneficio alto

4. **¿Cómo manejar órdenes antiguas (pre-Builder v2)?**
   - **Respuesta:** Campos nuevos son nullable - órdenes antiguas tendrán `qa_status=null`
   - **UI:** Mostrar "QA: no disponible" para órdenes antiguas

---

## 10. Integración con Agent Builder (FASE 4.B)

### ¿Qué es Agent Builder y cómo se relaciona con Builder v2?

**Agent Builder** es un nuevo subsistema diseñado en FASE 4.B que actúa como capa de traducción entre el `AgentBlueprint` y la construcción física del proyecto.

**Relación con Builder v2:**

```
Agent Builder (FASE 4.B - DISEÑO)
    ↓ genera artefactos específicos del agente
Builder v1 (existente)
    ↓ construye código físico usando artefactos
Builder v2 (existente)
    ↓ QA + empaquetado de deliverables
```

### Flujo Completo con Agent Builder

**Antes (Builder v1/v2 actual):**
```
Replit envía: { order, plan, tipo_producto }
    ↓
Axon 88 Builder v1: construye proyecto genérico
    ↓
Axon 88 Builder v2: QA + deliverable
    ↓
Respuesta a Replit
```

**Después (con Agent Builder integrado - futuro):**
```
Replit envía: { order, plan, agent_blueprint }
    ↓
Axon 88 Agent Builder: interpreta blueprint → genera artefactos
  - /spec/agent_spec.md
  - /flows/*.json (flujos de conversación)
  - /config/*.yaml (configuraciones)
  - /prompts/*.txt (prompts base)
  - /integrations/*.json (manifests n8n, VAPI, etc.)
    ↓
Axon 88 Builder v1: construye proyecto usando artefactos
    ↓
Axon 88 Builder v2: QA + deliverable (valida artefactos también)
    ↓
Respuesta a Replit con metadata extendida
```

### Impacto en Builder v2

**QA extendido:**
- Builder v2 validará no solo `order.json`, `plan.json`, `spec.md`
- También validará artefactos generados por Agent Builder:
  - `flows/*.json` existen y son válidos
  - `config/*.yaml` tienen estructura correcta
  - `integrations/*.json` contienen manifests completos

**Deliverable metadata extendida:**
```json
{
  "order_number": "ORD-2025-020",
  "tipo_producto": "autopilot_whatsapp",
  "qa_status": "ok",
  
  "agent_builder": {
    "executed": true,
    "version": "1.0.0",
    "agent_type": "whatsapp_autopilot",
    "capabilities": ["respuesta_inteligente", "ventas", "recordatorios"],
    "channels": ["whatsapp"],
    "integrations": [
      {"type": "twilio", "status": "configured"},
      {"type": "n8n", "status": "pending_activation"}
    ],
    "artifacts": {
      "flows": 3,
      "prompts": 5,
      "config_files": 3
    }
  }
}
```

### Beneficios para Builder v2

1. **QA más inteligente:**
   - Sabe qué capabilities debe tener el agente
   - Valida que existan módulos correspondientes
   - Verifica manifests de integraciones

2. **Deliverables más ricos:**
   - Cliente ve: "Tu WhatsApp Bot incluye 3 flujos activos"
   - Dashboard muestra: "2 integraciones configuradas, 1 pendiente"

3. **Backward compatibility:**
   - Si `agent_blueprint` es `null`, Builder v2 funciona exactamente como antes
   - No rompe construcciones existentes

### Estado Actual (Noviembre 2025)

- ✅ **Builder v2:** Implementado y funcionando (QA + Deliverables)
- 📋 **Agent Builder:** Solo diseño arquitectónico (ver `docs/AGENT_BUILDER_PLAN.md`)
- ⏳ **Integración:** Pendiente para fase BUILD futura

**Documentación completa:** `docs/AGENT_BUILDER_PLAN.md`

---

## 11. Conclusión

Este plan define la arquitectura completa para integrar **Builder v2 (QA + Deliverable)** entre Replit y Axon 88. La implementación se hará en fases incrementales:

1. **Fase 1 (Backend):** Modelos y endpoints básicos
2. **Fase 2 (Integración):** Testing con Axon 88 real
3. **Fase 3 (Frontend):** UI para Federico
4. **Fase 4 (Futuro):** Descarga segura de deliverables

**Próximo paso:** Federico revisa y aprueba este diseño. Si aprobado, procedemos a Fase 1 de implementación.

**Estimación total (Fases 1-3):** 12-18 horas de desarrollo  
**Estimación con Fase 4:** 20-30 horas de desarrollo

---

**Autor:** Cursor AI (Replit Agent) con Federico  
**Fecha:** 15 noviembre 2025  
**Versión:** 1.0.0
