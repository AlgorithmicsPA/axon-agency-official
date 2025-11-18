# Orders API - Resumen Ejecutivo

**Estado:** ✅ Production-ready para factory privada  
**Última actualización:** 2025-11-15 (Integración Replit → Axon 88 end-to-end OPERATIVA)  
**Base URL:** `http://localhost:8080/api/orders` (dev)

---

## 📋 Endpoints Implementados

### 1. POST /api/orders - Crear nueva orden
**Descripción:** Crea una nueva orden de autopilot con order_number único generado automáticamente.

**Request Body (OrderCreate):**
```json
{
  "tipo_producto": "autopilot_whatsapp",  // Enum: autopilot_whatsapp | autopilot_ventas | webhook_service
  "nombre_producto": "WhatsApp Bot Ventas XYZ",
  "datos_cliente": {
    "nombre": "Empresa XYZ",
    "email": "contacto@xyz.com",
    "config": {
      // Configuración específica del autopilot
    }
  },
  "prioridad": "normal",  // normal | baja | alta | urgente
  "tags": ["retail", "whatsapp", "mexico"]
}
```

**Response (201 Created - OrderResponse):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-001",
  "tipo_producto": "autopilot_whatsapp",
  "nombre_producto": "WhatsApp Bot Ventas XYZ",
  "estado": "nuevo",
  "progreso": 0,
  "prioridad": "normal",
  "tags": ["retail", "whatsapp", "mexico"],
  "asignado_a": null,
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T10:00:00Z"
}
```

**Validaciones:**
- ✅ `tipo_producto` debe ser enum válido (rechaza valores inválidos con 400)
- ✅ `order_number` generado automáticamente con formato ORD-YYYY-NNN
- ✅ Protección contra race conditions (retry logic + unique constraint)

---

### 2. GET /api/orders - Listar órdenes

**Query Parameters:**
- `estado` (opcional): Filtrar por estado (nuevo, planificacion, construccion, qa, listo, entregado, fallido, cancelado)
- `tipo_producto` (opcional): Filtrar por tipo
- `limit` (default: 50): Número máximo de resultados
- `offset` (default: 0): Para paginación

**Ejemplos:**
```bash
# Todas las órdenes
GET /api/orders

# Solo órdenes nuevas
GET /api/orders?estado=nuevo

# Autopilots de WhatsApp, paginado
GET /api/orders?tipo_producto=autopilot_whatsapp&limit=20&offset=0
```

**Response (200 OK - Array de OrderResponse):**
```json
[
  {
    "id": "...",
    "order_number": "ORD-2025-001",
    "tipo_producto": "autopilot_whatsapp",
    "estado": "construccion",
    "progreso": 45,
    "prioridad": "alta",
    "tags": ["retail"],
    "asignado_a": "Builder Agent",
    "created_at": "...",
    "updated_at": "..."
  }
]
```

---

### 3. GET /api/orders/{order_id} - Obtener detalle completo

**Path Parameters:**
- `order_id`: UUID de la orden

**Response (200 OK - OrderDetailResponse):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-001",
  "tipo_producto": "autopilot_whatsapp",
  "nombre_producto": "WhatsApp Bot Ventas XYZ",
  "estado": "construccion",
  "progreso": 45,
  "prioridad": "alta",
  "tags": ["retail", "whatsapp"],
  "asignado_a": "Builder Agent",
  "session_id": "session_abc123",
  "cliente_id": null,
  "datos_cliente": {
    "nombre": "Empresa XYZ",
    "email": "contacto@xyz.com"
  },
  "plan": {
    "tipo_autopilot": "whatsapp",
    "fases": [
      {"fase": "setup", "completado": true},
      {"fase": "integracion", "completado": false}
    ]
  },
  "logs": [
    {
      "timestamp": "2025-11-14T10:00:00Z",
      "agente": "Super Axon Agent",
      "mensaje": "Orden recibida, iniciando planificación",
      "tipo": "info"
    }
  ],
  "repo_url": null,
  "deploy_url": null,
  "resultado": null,
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T11:30:00Z",
  "planificado_at": "2025-11-14T10:15:00Z",
  "construccion_iniciada_at": "2025-11-14T10:30:00Z",
  "qa_iniciada_at": null,
  "entregado_at": null,
  "notas_internas": ""
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Orden 550e8400-e29b-41d4-a716-446655440000 no encontrada"
}
```

---

### 4. GET /api/orders/{order_id}/result - Obtener producto entregado

**Descripción:** Solo disponible cuando `estado = "listo"` o `estado = "entregado"`

**Response (200 OK):**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-2025-001",
  "estado": "listo",
  "resultado": {
    "portal_url": "https://autopilot-xyz.axon88.com",
    "admin_url": "https://autopilot-xyz.axon88.com/admin",
    "api_url": "https://api.autopilot-xyz.axon88.com",
    "credentials": {
      "admin_email": "admin@empresa.com",
      "admin_password_temporal": "ChangeMe123!",
      "api_key": "axon_pk_live_abc123xyz789"
    },
    "docs_url": "https://docs.axon88.com/autopilot-xyz",
    "support_email": "support@axon88.com"
  },
  "repo_url": "https://github.com/axon88-products/autopilot-xyz-001",
  "deploy_url": "https://autopilot-xyz.axon88.com",
  "entregado_at": "2025-11-14T14:00:00Z"
}
```

**Error (400 Bad Request - Producto no listo):**
```json
{
  "detail": {
    "error": "Producto aún no está listo",
    "estado_actual": "construccion",
    "progreso": 45,
    "mensaje": "El autopilot está en construccion. Revisa el estado en /api/orders/550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

### 5. PATCH /api/orders/{order_id} - Actualizar orden (uso interno)

**Descripción:** Endpoint para que los agentes actualicen estado, progreso, logs, plan, etc.

**Request Body (OrderUpdate - todos los campos opcionales):**
```json
{
  "estado": "planificacion",  // Enum validado
  "progreso": 15,
  "logs": [
    {
      "timestamp": "2025-11-14T10:15:00Z",
      "agente": "Planner Agent",
      "mensaje": "Plan generado exitosamente",
      "tipo": "success"
    }
  ],
  "plan": {
    "tipo_autopilot": "whatsapp",
    "fases": [...]
  },
  "asignado_a": "Builder Agent",
  "session_id": "session_xyz789",
  "resultado": null,
  "repo_url": null,
  "deploy_url": null
}
```

**Response (200 OK - OrderDetailResponse):**
Devuelve la orden completa actualizada con timestamps automáticos.

**Validaciones:**
- ✅ `estado` debe ser enum válido (rechaza estados inválidos automáticamente)
- ✅ Timestamps automáticos:
  - `planificacion` → setea `planificado_at`
  - `construccion` → setea `construccion_iniciada_at`
  - `qa` → setea `qa_iniciada_at`
  - `entregado` → setea `entregado_at`

---

## 🔐 Enums y Validaciones

### OrderStatus (estados válidos)
```python
"nuevo"        # Orden recibida, esperando planificación
"planificacion" # Super Axon Agent planificando construcción
"construccion" # Builder Agent construyendo autopilot
"qa"           # Review Council haciendo QA
"listo"        # Producto terminado, listo para entregar
"entregado"    # Entregado al cliente
"fallido"      # Falló construcción o QA
"cancelado"    # Cancelado manualmente
```

### ProductType (tipos de productos)
```python
"autopilot_whatsapp"  # WhatsApp chatbot con Twilio/WA Business API
"autopilot_ventas"    # Sales automation autopilot
"webhook_service"     # Custom webhook processor service
```

---

## 📊 Modelos (Schemas)

### OrderCreate (POST request)
```typescript
{
  tipo_producto: string;      // Enum: ProductType
  nombre_producto: string;
  datos_cliente: object;      // JSON libre
  prioridad?: string;         // Default: "normal"
  tags?: string[];            // Default: []
}
```

### OrderUpdate (PATCH request)
```typescript
{
  estado?: OrderStatus;       // Enum validado
  progreso?: number;          // 0-100
  logs?: Array<{
    timestamp: string;
    agente: string;
    mensaje: string;
    tipo: string;
  }>;
  plan?: object;
  asignado_a?: string;
  session_id?: string;
  resultado?: object;
  repo_url?: string;
  deploy_url?: string;
}
```

### OrderResponse (GET listing)
```typescript
{
  id: string;
  order_number: string;
  tipo_producto: string;
  nombre_producto: string;
  estado: string;
  progreso: number;
  prioridad: string;
  tags: string[];
  asignado_a: string | null;
  created_at: string;
  updated_at: string;
}
```

### OrderDetailResponse (GET detail, PATCH response)
```typescript
{
  // Todos los campos de OrderResponse +
  session_id: string | null;
  cliente_id: string | null;
  datos_cliente: object;
  plan: object | null;
  logs: Array<object>;
  repo_url: string | null;
  deploy_url: string | null;
  resultado: object | null;
  planificado_at: string | null;
  construccion_iniciada_at: string | null;
  qa_iniciada_at: string | null;
  entregado_at: string | null;
  notas_internas: string;
}
```

---

## 🔄 Integración con Super Axon Agent

### 1. Polling de órdenes nuevas
```typescript
// Obtener órdenes nuevas cada 30 segundos
const nuevasOrdenes = await fetch('/api/orders?estado=nuevo&limit=10');

// Para cada orden nueva:
// 1. Cambiar estado a "planificacion"
await fetch(`/api/orders/${orderId}`, {
  method: 'PATCH',
  body: JSON.stringify({
    estado: 'planificacion',
    asignado_a: 'Super Axon Agent'
  })
});

// 2. Generar plan con LLM
const plan = await generatePlan(orden.datos_cliente);

// 3. Guardar plan
await fetch(`/api/orders/${orderId}`, {
  method: 'PATCH',
  body: JSON.stringify({
    plan: plan,
    progreso: 20,
    logs: [{
      timestamp: new Date().toISOString(),
      agente: 'Super Axon Agent',
      mensaje: 'Plan generado exitosamente',
      tipo: 'success'
    }]
  })
});
```

### 2. Delegación a Autonomous Agent
```typescript
// Cambiar a construcción
await fetch(`/api/orders/${orderId}`, {
  method: 'PATCH',
  body: JSON.stringify({
    estado: 'construccion',
    asignado_a: 'Builder Agent'
  })
});

// Crear sesión autónoma
const session = await fetch('/api/agent/autonomous/start', {
  method: 'POST',
  body: JSON.stringify({
    task: `Build ${orden.tipo_producto}: ${orden.nombre_producto}`,
    plan: orden.plan
  })
});

// Guardar session_id
await fetch(`/api/orders/${orderId}`, {
  method: 'PATCH',
  body: JSON.stringify({
    session_id: session.id
  })
});
```

### 3. Tracking de progreso
```typescript
// Actualizar progreso periódicamente
await fetch(`/api/orders/${orderId}`, {
  method: 'PATCH',
  body: JSON.stringify({
    progreso: 65,
    logs: [{
      timestamp: new Date().toISOString(),
      agente: 'Builder Agent',
      mensaje: 'Integración con WhatsApp API completada',
      tipo: 'success'
    }]
  })
});
```

### 4. Completar orden
```typescript
// Cambiar a QA
await fetch(`/api/orders/${orderId}`, {
  method: 'PATCH',
  body: JSON.stringify({
    estado: 'qa',
    progreso: 90,
    asignado_a: 'Review Council'
  })
});

// Después de QA exitoso, marcar listo
await fetch(`/api/orders/${orderId}`, {
  method: 'PATCH',
  body: JSON.stringify({
    estado: 'listo',
    progreso: 100,
    repo_url: 'https://github.com/axon88-products/autopilot-xyz-001',
    deploy_url: 'https://autopilot-xyz.axon88.com',
    resultado: {
      portal_url: '...',
      credentials: {...},
      // ... más detalles
    }
  })
});
```

---

## 🏭 Integración con /api/factory/info

La Orders API está registrada en el endpoint de factory info:

```bash
GET /api/factory/info
```

**Response:**
```json
{
  "factory_name": "AXON Agency - Private AI Factory",
  "version": "1.0.0",
  "status": "operational",
  "capabilities": {
    "orders_api": true,  // ✅ Orders API disponible
    "autonomous_agent": true,
    "review_council": true,
    "self_improvement": true,
    "multi_llm": true
  },
  "products": [
    {
      "id": "autopilot_whatsapp",
      "nombre": "WhatsApp Autopilot",
      "descripcion": "Chatbot WhatsApp con Twilio/WA Business API"
    },
    {
      "id": "autopilot_ventas",
      "nombre": "Sales Autopilot",
      "descripcion": "Sistema de automatización de ventas"
    },
    {
      "id": "webhook_service",
      "nombre": "Webhook Service",
      "descripcion": "Procesador de webhooks personalizado"
    }
  ]
}
```

---

## ⚠️ Tech Debt Conocido

Ver sección completa en `ORDERS_API_DESIGN.md` sección 11.

**Resumen:**
- ✅ **Funcional para factory privada** (volumen moderado de órdenes)
- ⚠️ **Async/Sync DB**: Endpoints async con SQLModel síncrono (optimizar si alta concurrencia)
- ⚠️ **Race conditions**: Protección básica suficiente, pero puede mejorar con SELECT FOR UPDATE
- ⚠️ **Testing**: Validación manual, agregar tests automatizados cuando escale

**Decisión:** Implementar ahora, monitorear métricas, optimizar solo si necesario.

---

## 🎯 Próximos Pasos para Integración

1. **Super Axon Agent** (ChatOrchestrationService):
   - Implementar polling de órdenes nuevas
   - Integrar LLM para generación de planes
   - Delegar construcción a Autonomous Agent
   - Trackear progreso en tiempo real

2. **Conexión con Axon 88**:
   - Configurar control-api:8088 en Jetson
   - Delegar construcciones pesadas al Jetson
   - Sincronizar estado entre Replit (cerebro) y Axon 88 (planta)

3. **Review Council Integration**:
   - Integrar revisiones de Security, Performance, QA
   - Actualizar estado a QA cuando construcción termine
   - Aprobar/rechazar órdenes basado en reviews

4. **Delivery Pipeline**:
   - Deploy automation
   - Generación de credenciales
   - Actualizar `resultado` con info de entrega

---

## 🤖 Orders Orchestrator v1 (Auto-Planificación)

**Estado:** ✅ Production-ready  
**Implementación:** `app/services/orders_orchestrator.py`  
**Endpoint:** `POST /api/factory/process-orders`

### Descripción

El Orders Orchestrator es el motor de auto-planificación que procesa órdenes pendientes (estado='nuevo') y genera planes de producción estructurados usando LLM multi-provider. Utiliza el LLMRouter para garantizar alta disponibilidad con fallback automático (Gemini → OpenAI → Ollama).

### Endpoint: POST /api/factory/process-orders

**Descripción:** Procesa todas las órdenes con estado='nuevo', genera planes con LLM, y actualiza estado a 'planificacion'.

**Request:**
```bash
curl -X POST http://localhost:8080/api/factory/process-orders
```
Sin body necesario - procesa automáticamente todas las órdenes pendientes.

**Response (ProcessOrdersResponse):**
```json
{
  "processed_count": 3,
  "orders": [
    {
      "order_id": "a5ffd0f2-1070-4588-a79a-b521d764264e",
      "order_number": "ORD-2025-002",
      "tipo_producto": "autopilot_ventas",
      "nombre_producto": "Funnel de Ventas - Coach ABC",
      "old_status": "nuevo",
      "new_status": "planificacion",
      "plan_summary": "Autopilot para automatizar el funnel de ventas de coaching. Incluye captación, cualificación, seguimiento y cierre de ventas. Adaptado a la configuración específica del Coach ABC (idioma español, funnel de ventas coaching). | Fases: 5 | Est: 25h",
      "error": null
    },
    {
      "order_id": "c27ef782-628d-49eb-9e70-a9395c2773e9",
      "order_number": "ORD-2025-005",
      "tipo_producto": "autopilot_ventas",
      "nombre_producto": "Test Async Final",
      "old_status": "nuevo",
      "new_status": "planificacion",
      "plan_summary": "Plan de producción para construir un autopilot de ventas para Test Async. Este autopilot automatizará la captación de leads, la cualificación y el seguimiento de oportunidades de venta. Se integrará con las herramientas de comunicación y pago necesarias. | Fases: 5 | Est: 21h",
      "error": null
    },
    {
      "order_id": "7beae2f5-4d9f-486b-a593-5c5a65ad8d4b",
      "order_number": "ORD-2025-006",
      "tipo_producto": "autopilot_whatsapp",
      "nombre_producto": "WhatsApp Bot Test Orchestrator",
      "old_status": "nuevo",
      "new_status": "planificacion",
      "plan_summary": "Plan de producción para construir un bot de WhatsApp para Test Cliente. El bot actuará como un orquestador de pruebas automatizadas para atención al cliente 24/7. Dada la alta prioridad, se asignarán recursos para un desarrollo ágil. | Fases: 4 | Est: 20h",
      "error": null
    }
  ],
  "message": "Procesadas 3 orden(es). Ver detalles en 'orders'."
}
```

**Casos de Error por Orden:**
```json
{
  "processed_count": 1,
  "orders": [
    {
      "order_id": "...",
      "order_number": "ORD-2025-007",
      "tipo_producto": "autopilot_ventas",
      "nombre_producto": "Test Error",
      "old_status": "nuevo",
      "new_status": "nuevo",
      "plan_summary": "",
      "error": "Failed to generate plan: LLM provider timeout"
    }
  ],
  "message": "Procesadas 1 orden(es). Ver detalles en 'orders'."
}
```

### Estructura del Plan JSON Generado

Ejemplo real de plan generado por el orchestrator para `autopilot_whatsapp`:

```json
{
  "tipo_autopilot": "autopilot_whatsapp",
  "resumen": "Plan de producción para construir un bot de WhatsApp para Test Cliente. El bot actuará como un orquestador de pruebas automatizadas para atención al cliente 24/7. Dada la alta prioridad, se asignarán recursos para un desarrollo ágil.",
  "fases": [
    {
      "nombre": "Setup Inicial",
      "descripcion": "Configuración del entorno de desarrollo, base de datos y autenticación para el bot de WhatsApp.",
      "estimacion_horas": 3,
      "dependencias": [],
      "tareas": [
        "Crear repositorio Git y configurar proyecto base con FastAPI",
        "Configurar base de datos PostgreSQL en la nube",
        "Implementar autenticación básica para acceso a la API del bot"
      ]
    },
    {
      "nombre": "Integración WhatsApp Business API",
      "descripcion": "Integración con la API de WhatsApp Business para enviar y recibir mensajes.",
      "estimacion_horas": 5,
      "dependencias": ["Setup Inicial"],
      "tareas": [
        "Configurar WhatsApp Business API client",
        "Implementar webhooks para recepción de mensajes",
        "Gestionar la suscripción a eventos de WhatsApp (envío, recepción, estado)"
      ]
    },
    {
      "nombre": "Orquestación de Tests y Lógica de Negocio",
      "descripcion": "Implementar la lógica para orquestar las pruebas automatizadas y atender las solicitudes del cliente.",
      "estimacion_horas": 8,
      "dependencias": ["Integración WhatsApp Business API"],
      "tareas": [
        "Definir y configurar los flujos de conversación para atención al cliente",
        "Implementar la lógica para ejecutar tests automatizados según la solicitud del cliente",
        "Persistir los resultados de los tests en la base de datos",
        "Implementar la lógica para responder a las consultas del cliente y proporcionar información relevante"
      ]
    },
    {
      "nombre": "QA y Deploy",
      "descripcion": "Realizar pruebas exhaustivas y desplegar el bot en un entorno de producción.",
      "estimacion_horas": 4,
      "dependencias": ["Orquestación de Tests y Lógica de Negocio"],
      "tareas": [
        "Escribir y ejecutar tests automatizados (unitarios e integrales)",
        "Realizar pruebas de carga y rendimiento",
        "Review Council (Security, Performance, QA)",
        "Desplegar el bot en un entorno de producción (e.g., AWS, Google Cloud)",
        "Configurar el monitoreo y alertas"
      ]
    }
  ],
  "stack_tecnologico": {
    "backend": "FastAPI",
    "frontend": "No aplica (bot)",
    "database": "PostgreSQL",
    "integraciones": [
      "WhatsApp Business API",
      "Python Testing Framework (pytest, unittest)"
    ]
  },
  "estimacion_total_horas": 20,
  "notas_especiales": "El cliente requiere atención al cliente 24/7, por lo que es crucial asegurar alta disponibilidad y robustez del bot. Considerar la implementación de un sistema de colas para manejar un gran volumen de solicitudes. La prioridad alta justifica la asignación de un equipo con experiencia en bots de WhatsApp y automatización de tests."
}
```

### OrdersOrchestratorService - API Contract

**Clase:** `OrdersOrchestratorService`  
**Ubicación:** `app/services/orders_orchestrator.py`

#### Métodos Públicos

##### `async def process_pending_orders(session: Session) -> List[OrderProcessingResult]`

Procesa todas las órdenes con estado='nuevo' y genera planes con LLM.

**Parámetros:**
- `session`: SQLModel database session (dependency injection)

**Returns:**
```python
List[OrderProcessingResult]  # Ver modelo abajo
```

**Comportamiento:**
1. Query de órdenes con `estado='nuevo'` (ordenadas por `created_at`)
2. Para cada orden:
   - Genera plan usando `LLMRouter.route_and_execute()` (fallback: Gemini → OpenAI → Ollama)
   - Parsea JSON del plan
   - Actualiza estado a `'planificacion'` con timestamps automáticos
   - Agrega log entry
   - Si falla: `session.rollback()` para aislar error, continúa con siguiente orden
3. Devuelve resultados de todas las órdenes procesadas

**Error Handling:**
- Errores por orden NO abortan el proceso completo
- Session rollback en caso de fallo para evitar `PendingRollbackError`
- Fallback a plan básico si JSON parsing falla

**Ejemplo de Uso:**
```python
from app.services.orders_orchestrator import get_orders_orchestrator
from sqlmodel import Session

@router.post("/factory/process-orders")
async def process_orders_endpoint(
    session: Session = Depends(get_session)
):
    orchestrator = get_orders_orchestrator()
    results = await orchestrator.process_pending_orders(session)
    
    return ProcessOrdersResponse(
        processed_count=len(results),
        orders=[r.dict() for r in results]
    )
```

#### Modelos

##### OrderProcessingResult
```python
class OrderProcessingResult(BaseModel):
    order_id: str
    order_number: str
    tipo_producto: str
    nombre_producto: str
    old_status: str
    new_status: str
    plan_summary: str  # Resumen generado del plan
    error: Optional[str] = None  # Error message si falló
```

##### ProcessOrdersResponse
```python
class ProcessOrdersResponse(BaseModel):
    processed_count: int
    orders: List[OrderProcessingResult]
    message: str
```

### Integración con Chat (/api/agent)

El Chat Orchestrator detecta comandos de procesamiento de órdenes usando keywords y ejecuta el orchestrator directamente.

**Keywords Detectadas:**
```python
# Español
"procesar órdenes", "procesa órdenes", "revisar órdenes", 
"revisa órdenes", "órdenes pendientes", "órdenes nuevas",
"ejecutar orchestrator", "procesa orders"

# Inglés
"process orders", "review orders", "pending orders", 
"new orders", "run orchestrator", "factory orders"
```

**Ejemplo de Interacción:**
```
Usuario: Procesa las órdenes pendientes

Super Axon Agent:
✅ **Órdenes Procesadas: 3**

**ORD-2025-002** (autopilot_ventas - Funnel de Ventas - Coach ABC)
- Estado: nuevo → planificacion
- Plan: Autopilot para automatizar el funnel de ventas de coaching. | Fases: 5 | Est: 25h

**ORD-2025-006** (autopilot_whatsapp - WhatsApp Bot Test Orchestrator)
- Estado: nuevo → planificacion
- Plan: Plan de producción para construir un bot de WhatsApp... | Fases: 4 | Est: 20h

🚀 Todas las órdenes han sido planificadas. Puedes revisarlas en el panel de órdenes.
```

**Implementación:**
```python
# En ChatOrchestrationService.handle_message()
if self._is_orders_processing_command(message):
    return await self._handle_process_orders(session, message)
```

### LLM Prompt Engineering

El orchestrator genera planes usando un prompt estructurado que incluye:

1. **Identidad del Agente:** "Eres PLANNER AGENT de AXON Factory..."
2. **Datos de la Orden:** tipo_producto, nombre_producto, datos_cliente, prioridad
3. **Esquema JSON Requerido:** estructura del plan con ejemplos
4. **Instrucciones:** generar plan accionable, realista, con dependencias

**Temperatura:** 0.3 (baja para output estructurado y consistente)  
**Max Tokens:** 2000 (suficiente para planes complejos)

### Métricas y Observabilidad

- ✅ Logs detallados en cada orden (timestamp, agente, mensaje)
- ✅ LLMRouter tracking: latencia, success rate, provider usado, fallbacks
- ✅ OrderProcessingResult incluye errores para debugging
- ✅ Timestamps automáticos: `planificado_at` cuando estado → 'planificacion'

---

## 🏭 Integración con Axon 88 Builder v1

**Estado:** ✅ Production-ready  
**Implementación:** `app/services/axon_factory_client.py`  
**Integrado en:** `OrdersOrchestratorService`

### Descripción

Después de generar el plan de producción, el Orders Orchestrator delega automáticamente la construcción física del producto a la **fábrica local en Axon 88** (Jetson Orin) vía HTTP.

### Arquitectura

```
REPLIT (Cerebro en la nube)                 AXON 88 (Fábrica local - Jetson)
┌─────────────────────────┐                 ┌──────────────────────────┐
│ Orders Orchestrator     │                 │ Builder v1               │
│ - Recibe orden          │                 │ - Construye producto     │
│ - Genera plan (LLM)     │   HTTP POST     │ - Genera código          │
│ - Delega construcción   ├────────────────>│ - Crea estructura        │
│                         │   /factory/     │ - Ejecuta tests          │
│                         │   build-local   │                          │
└─────────────────────────┘                 └──────────────────────────┘
         │                                            │
         │                                            │
         v                                            v
  Estado: planificacion                   ~/factory/products/{order_number}/
                                          ├── order.json
                                          ├── plan.json
                                          ├── spec.md
                                          └── build.log
```

### Flujo de Integración

**1. Orders Orchestrator genera plan:**
```
Estado: nuevo → planificacion
- Plan JSON guardado en DB
- planificado_at timestamp
```

**2. Llama a Axon 88 Factory Client:**
```python
build_result = await axon_factory_client.build_product(order, plan)
```

**Request a Axon 88:**
```http
POST https://api-axon88.algorithmicsai.com/factory/build-local
Content-Type: application/json

{
  "order": {
    "order_id": "uuid...",
    "order_number": "ORD-2025-001",
    "tipo_producto": "autopilot_whatsapp",
    "nombre_producto": "WhatsApp Bot Ventas XYZ",
    "datos_cliente": {...},
    "prioridad": "alta"
  },
  "plan": {
    "tipo_autopilot": "autopilot_whatsapp",
    "fases": [...],
    "stack_tecnologico": {...},
    ...
  }
}
```

**Response de Axon 88 (Success - Formato Real del Builder v1):**
```json
{
  "success": true,
  "error": null,
  "product_path": "/home/axon88/factory/products/ORD-2025-012_autopilot_whatsapp",
  "log_path": "/home/axon88/factory/logs/orders.log",
  "construido_en": "2025-11-15T02:14:34.084390"
}
```

**Response de Axon 88 (Error):**
```json
{
  "success": false,
  "error": "El producto ya existe en: /home/axon88/factory/products/ORD-2025-012_autopilot_whatsapp. No se sobrescriben productos existentes por seguridad.",
  "product_path": "/home/axon88/factory/products/ORD-2025-012_autopilot_whatsapp",
  "log_path": "/home/axon88/factory/logs/orders.log",
  "construido_en": null
}
```

**3. Actualiza orden con resultado:**

Si `build_result.success = true`:
```
Estado: planificacion → construccion
- product_path: "/home/axon88/factory/products/ORD-2025-012_autopilot_whatsapp"
- log_path: "/home/axon88/factory/logs/orders.log"
- construido_en: "2025-11-15T02:14:34.084390" (parseado de ISO string de Axon 88)
- construccion_iniciada_at: timestamp
- asignado_a: "Axon 88 Builder"
```

Si `build_result.success = false`:
```
Estado: planificacion (sin cambios)
- Log entry con error
- Orden queda en planificacion para retry manual
```

### Campos Nuevos en el Modelo Order

#### `product_path` (Optional[str])
**Descripción:** Ruta del producto generado en Axon 88  
**Ejemplo:** `"~/factory/products/ORD-2025-001_autopilot_whatsapp/"`  
**Uso:** Permite ubicar el código generado en el Jetson para debugging, deployment, etc.

#### `log_path` (Optional[str])
**Descripción:** Ruta del log de construcción en Axon 88  
**Ejemplo:** `"~/factory/products/ORD-2025-001_autopilot_whatsapp/build.log"`  
**Uso:** Debugging de errores durante construcción

#### `construido_en` (Optional[datetime])
**Descripción:** Timestamp de cuando Axon 88 completó la construcción  
**Ejemplo:** `"2025-11-14T15:30:00Z"`  
**Uso:** Métricas de tiempo de construcción

### Configuración (Variables de Entorno)

```bash
# Habilitar integración con Axon 88
AXON_CORE_ENABLED=true

# Base URL del control-api en Axon 88 (vía Cloudflare tunnel)
AXON_CORE_API_BASE=https://api-axon88.algorithmicsai.com

# Token de autenticación (opcional)
AXON_CORE_API_TOKEN=
```

### Error Handling

El AxonFactoryClient implementa error handling robusto:

**Timeout (120s):**
```json
{
  "success": false,
  "error_message": "Request timeout after 120s"
}
```

**Network Error:**
```json
{
  "success": false,
  "error_message": "Network error: Connection refused"
}
```

**HTTP 4xx/5xx:**
```json
{
  "success": false,
  "error_message": "HTTP 500: Internal server error",
  "raw_response": {"status_code": 500, "text": "..."}
}
```

**Deshabilitado (AXON_CORE_ENABLED=false):**
```json
{
  "success": false,
  "error_message": "Axon Factory integration is disabled"
}
```

**Importante:** Los errores NO rompen el flujo del orchestrator. Si Axon 88 falla, la orden queda en estado `planificacion` con el plan ya guardado, permitiendo retry manual o debugging.

### Ejemplo End-to-End

**1. Crear orden:**
```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "autopilot_whatsapp",
    "nombre_producto": "WhatsApp Bot Test",
    "datos_cliente": {"nombre": "Test Cliente"}
  }'
```

**2. Procesar órdenes (trigger orchestrator):**
```bash
curl -X POST http://localhost:8080/api/factory/process-orders
```

**3. Verificar resultado:**
```bash
curl http://localhost:8080/api/orders/{order_id}
```

**Response esperada (si Axon 88 responde exitosamente - TEST REAL ORD-2025-012):**
```json
{
  "id": "b999d34d-8446-498c-95f3-5873966d8be8",
  "order_number": "ORD-2025-012",
  "tipo_producto": "autopilot_whatsapp",
  "nombre_producto": "ChatBot WhatsApp para Tienda Online (TEST END-TO-END)",
  "estado": "construccion",
  "progreso": 0,
  "prioridad": "alta",
  "tags": [],
  "asignado_a": "Axon 88 Builder",
  "session_id": null,
  "cliente_id": null,
  "datos_cliente": {
    "nombre": "E-Commerce Demo",
    "industria": "retail",
    "configuracion": {
      "productos": ["ropa", "accesorios", "calzado"],
      "objetivos": [
        "automatizar atención 24/7",
        "aumentar conversiones",
        "reducir carga de soporte"
      ]
    }
  },
  "plan": {
    "tipo_autopilot": "autopilot_whatsapp",
    "resumen": "Desarrollo de un chatbot de WhatsApp para E-Commerce Demo...",
    "fases": [
      {
        "nombre": "Configuración Inicial y Análisis de Requisitos",
        "descripcion": "...",
        "estimacion_horas": 3,
        "dependencias": [],
        "tareas": [...]
      }
    ],
    "stack_tecnologico": {
      "backend": "FastAPI",
      "frontend": "Next.js",
      "database": "PostgreSQL",
      "integraciones": ["WhatsApp Business API"]
    },
    "estimacion_total_horas": 19,
    "notas_especiales": "..."
  },
  "logs": [
    {
      "timestamp": "2025-11-15T02:14:33.735997",
      "agente": "Orders Orchestrator",
      "mensaje": "Plan de producción generado. Estimación: 19 horas",
      "tipo": "success"
    },
    {
      "timestamp": "2025-11-15T02:14:34.078083",
      "agente": "Axon 88 Builder",
      "mensaje": "Construcción delegada exitosamente. Product path: /home/axon88/factory/products/ORD-2025-012_autopilot_whatsapp",
      "tipo": "success"
    }
  ],
  "repo_url": null,
  "deploy_url": null,
  "product_path": "/home/axon88/factory/products/ORD-2025-012_autopilot_whatsapp",
  "log_path": "/home/axon88/factory/logs/orders.log",
  "construido_en": "2025-11-15T02:14:34.084390",
  "resultado": null,
  "created_at": "2025-11-15T02:14:15.999466",
  "updated_at": "2025-11-15T02:14:34.078122",
  "planificado_at": "2025-11-15T02:14:33.735976",
  "construccion_iniciada_at": "2025-11-15T02:14:34.078066",
  "qa_iniciada_at": null,
  "entregado_at": null,
  "notas_internas": ""
}
```

---

## 🤖 BAU v1 – Build Automation Unit

**Estado:** ✅ Production-ready  
**Implementación:** `app/services/bau_service.py`  
**Endpoint:** `POST /api/factory/bau-tick`

### Descripción

BAU (Build Automation Unit) es una **capa delgada** encima de OrdersOrchestratorService y AxonFactoryClient que automatiza el procesamiento de órdenes pendientes. Es el motor de automatización de la fábrica.

### Funcionalidad

BAU procesa automáticamente dos tipos de órdenes:

1. **Órdenes nuevas** (estado='nuevo'):
   - Genera plan de producción con LLM
   - Llama a Axon 88 para construcción
   - Actualiza estado: nuevo → planificacion → construccion

2. **Órdenes sin producto** (estado='planificacion' AND product_path=NULL):
   - Reintenta construcción en Axon 88 (retry logic)
   - Actualiza estado: planificacion → construccion
   - Útil cuando Axon 88 falló anteriormente o estuvo offline

### Endpoint: POST /api/factory/bau-tick

**Request:**
```bash
curl -X POST http://localhost:8080/api/factory/bau-tick \
  -H "Content-Type: application/json"
```

Sin body necesario - procesa todas las órdenes candidatas automáticamente.

**Response (BAUTickResponse):**
```json
{
  "status": "ok",
  "processed_total": 3,
  "advanced_to_planificacion": 1,
  "advanced_to_construccion": 2,
  "errors": []
}
```

**Campos:**
- `status`: Siempre "ok" (indica que el tick se ejecutó, aunque haya errores individuales)
- `processed_total`: Total de órdenes procesadas (incluyendo fallos)
- `advanced_to_planificacion`: Órdenes que pasaron de 'nuevo' a 'planificacion'
- `advanced_to_construccion`: Órdenes que pasaron de 'planificacion' a 'construccion'
- `errors`: Array de mensajes de error (formato: "ORD-YYYY-NNN: mensaje")

**🔒 Seguridad - Sanitización de Errores (FASE 3 Hardening):**

Los mensajes de error del BAU se sanitizan automáticamente para **no exponer rutas internas** del filesystem de Axon 88. Solo se muestran mensajes de alto nivel:

- ❌ **ANTES:** `"ORD-2025-012: El producto ya existe en: /home/axon88/factory/products/ORD-2025-012_autopilot_whatsapp"`
- ✅ **AHORA:** `"ORD-2025-012: El producto ya existe para esta orden"`

Otros ejemplos sanitizados:
- `"Cannot retry build - no plan available"` (sin cambios - no contiene rutas)
- `"Build retry failed - Connection refused"` (sin cambios - error de red genérico)
- Cualquier ruta `/home/axon88/...` se reemplaza por `"el directorio de productos"` u otra descripción contextual

**Ejemplo con errores:**
```json
{
  "status": "ok",
  "processed_total": 2,
  "advanced_to_planificacion": 0,
  "advanced_to_construccion": 1,
  "errors": [
    "ORD-2025-015: Build retry failed - Connection refused to Axon 88"
  ]
}
```

### Lógica Interna

```
Para cada orden candidata:
  
  SI estado = 'nuevo':
    1. Llamar OrdersOrchestratorService._process_single_order()
    2. Esto genera plan + llama Axon 88
    3. Resultado: nuevo → planificacion → construccion (si Axon 88 responde OK)
  
  SI estado = 'planificacion' Y product_path = NULL:
    1. Llamar AxonFactoryClient.build_product() directamente
    2. Usar order.plan existente
    3. SI success=true:
       - Actualizar product_path, log_path, construido_en
       - Estado: planificacion → construccion
    4. SI success=false:
       - Agregar log de error
       - Dejar en 'planificacion' para retry futuro
```

### Integración con Sistema Existente

BAU **NO duplica código**, solo reutiliza:

- **OrdersOrchestratorService._process_single_order()**: Para órdenes nuevas
- **AxonFactoryClient.build_product()**: Para reintentos de construcción
- **Logging y manejo de errores**: Mismo estilo que OrdersOrchestrator

### Uso Manual (BAU v1)

**Caso de uso típico:**

```bash
# 1. Crear nueva orden
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "autopilot_whatsapp",
    "nombre_producto": "Bot para Retail XYZ",
    "datos_cliente": {"nombre": "Retail XYZ"}
  }'

# 2. Llamar BAU tick (procesa automáticamente)
curl -X POST http://localhost:8080/api/factory/bau-tick

# 3. Verificar resultado
curl http://localhost:8080/api/orders/{order_id}
```

**BAU procesará:**
- La orden nueva: generará plan + llamará Axon 88
- Cualquier orden anterior en 'planificacion' sin producto: reintentará construcción

### Ventajas vs. /api/factory/process-orders

| Feature | process-orders | bau-tick |
|---------|---------------|----------|
| Procesa órdenes nuevas | ✅ Sí | ✅ Sí |
| Reintenta órdenes sin producto | ❌ No | ✅ Sí |
| Scope | Solo estado='nuevo' | 'nuevo' + 'planificacion' sin producto |
| Uso | Procesamiento inicial | Automatización completa |

**Recomendación:** Usar `bau-tick` para automatización completa (n8n, cron). Usar `process-orders` solo si quieres procesar únicamente órdenes nuevas.

### Próximos Pasos (BAU v2)

1. **Automatización con n8n/cron:**
   - Llamar `/api/factory/bau-tick` cada 5 minutos
   - Monitorear `errors` array para alertas
   - Dashboard con métricas de BAU

2. **Reintentos inteligentes:**
   - Backoff exponencial para órdenes con múltiples fallos
   - Marcar como 'fallido' después de N reintentos
   - Notificaciones al equipo cuando una orden falla repetidamente

3. **Priorización:**
   - Procesar primero órdenes con prioridad 'urgente' o 'alta'
   - Límite de órdenes procesadas por tick para evitar saturación

---

### Próximos Pasos

1. **Polling/Webhook de Status:**
   - Actualmente Axon 88 responde inmediatamente con product_path
   - Considerar webhook para status updates durante construcción larga
   - Actualizar progreso en tiempo real (0% → 100%)

2. **Review Council Integration:**
   - Después de construcción en Axon 88, triggerar QA automático
   - Security, Performance, QA reviews
   - Actualizar estado a 'qa' → 'listo'

3. **Deployment Automation:**
   - Deploy automático desde Axon 88 después de QA exitoso
   - Actualizar `deploy_url` y `resultado` con credenciales

4. **Analytics:**
   - Tiempo promedio de construcción por tipo de producto
   - Tasa de éxito Replit → Axon 88
   - Identificar cuellos de botella

---

## 🏗️ Relación con Builder v2 (QA + Deliverable)

**Estado:** 📋 Diseñado - Pendiente implementación  
**Documento de diseño:** `docs/BUILDER_V2_PLAN.md`

### Qué es Builder v2

**Builder v2** es la evolución del sistema de construcción en Axon 88 que añade:

1. **QA Automático:** Validación estructural de productos (archivos requeridos, integridad)
2. **Deliverable Packaging:** Empaquetado profesional con SUMMARY.md, meta.json, y ZIP

### Extensiones Futuras de Orders API

Cuando se implemente la integración con Builder v2, la Orders API se extenderá con:

**Nuevos campos en modelo Order:**
- `qa_status` (ok/warn/fail)
- `qa_messages` (array de mensajes de validación)
- `qa_checked_files` (archivos validados)
- `deliverable_generado` (boolean)
- `deliverable_metadata` (metadata sin rutas sensibles)

**Nuevos endpoints:**
- `GET /api/orders/{id}/qa` - Estado y reportes de QA
- `GET /api/orders/{id}/deliverable` - Metadata del paquete final

**Actualización de flujo:**
```
Order → Plan → Build → QA (automático) → Deliverable → Entrega
```

**Para detalles completos del diseño arquitectónico, ver `docs/BUILDER_V2_PLAN.md`**

---

**✅ Orders API + Orchestrator v1 + Axon 88 Integration + BAU v1 - Production-ready**
