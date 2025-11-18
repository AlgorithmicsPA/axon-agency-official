# AXON Factory Vision - Modelo de Fábrica Privada de Autopilotos SaaS

**Versión:** 1.0.0  
**Fecha:** Noviembre 14, 2025  
**Autor:** Federico @ AXON Agency

---

## 1. Modelo de Negocio - Fábrica Privada

### 1.1 Concepto Fundamental

**AXON Agency NO es un SaaS público donde los clientes entran a configurar.**

AXON Agency es el **cerebro de una fábrica PRIVADA** que produce autopilotos SaaS completos para clientes finales.

**Analogía perfecta:** Como una fábrica de automóviles, pero para software/autopilotos inteligentes.

### 1.2 Flujo del Cliente

```
Cliente → Hace Pedido → Fábrica Construye Automáticamente → Cliente Recibe Producto Terminado
```

**Modelo tradicional (SaaS público como Zapier, Notion):**
- ❌ Cliente entra a plataforma compleja
- ❌ Cliente configura todo manualmente
- ❌ Cliente ve toda la complejidad técnica
- ❌ Modelo self-service (hazlo tú mismo)

**Modelo AXON Factory:**
- ✅ Cliente hace pedido simple (como pedir un auto)
- ✅ Fábrica construye automáticamente con IA
- ✅ Cliente recibe producto TERMINADO y funcionando
- ✅ Cliente solo usa SU producto específico
- ✅ Modelo white-glove / done-for-you

### 1.3 Diferenciación Clave

| Aspecto | SaaS Tradicional | AXON Factory |
|---------|------------------|--------------|
| **Acceso del Cliente** | Entra a plataforma completa | Solo ve SU autopiloto |
| **Configuración** | Cliente configura manualmente | IA construye automáticamente |
| **Complejidad** | Cliente ve toda la complejidad | Cliente ve producto simple |
| **Soporte** | Documentación + tickets | Producto hecho a medida |
| **Modelo** | Self-service | White-glove service |
| **Escalabilidad** | Un producto para todos | Productos únicos por cliente |

---

## 2. Productos que Genera la Fábrica

La fábrica AXON produce **autopilotos SaaS completos** - sistemas de IA autónomos que operan negocios específicos.

### 2.1 Catálogo Inicial de Productos

#### **Autopilot WhatsApp** (`autopilot_whatsapp`)
**Descripción:** Bot inteligente de ventas/soporte por WhatsApp  
**Stack base:** FastAPI, Twilio WhatsApp API, PostgreSQL, Redis  
**Templates:** `autopilot_base`, `whatsapp_bot_base`  
**Integraciones comunes:** WhatsApp Business API, Stripe, Google Sheets  
**Estimación:** 24 horas de construcción  

**Ejemplo de uso:**
- Tienda de ropa que quiere vender por WhatsApp 24/7
- Consultorio médico que agenda citas automáticamente
- Restaurante que toma pedidos vía WhatsApp

#### **Autopilot Ventas** (`autopilot_ventas`)
**Descripción:** Agente de ventas completo con funnel automatizado  
**Stack base:** Next.js, FastAPI, PostgreSQL, n8n  
**Templates:** `autopilot_base`, `sales_funnel_base`  
**Integraciones comunes:** Stripe, HubSpot, WhatsApp, Email  
**Estimación:** 48 horas de construcción  

**Ejemplo de uso:**
- Coach que vende cursos online
- Agencia que ofrece servicios de marketing
- SaaS que necesita pipeline de ventas automatizado

#### **Webhook Service** (`webhook_service`)
**Descripción:** Servicio de webhooks personalizado para integraciones  
**Stack base:** FastAPI, Redis, PostgreSQL  
**Templates:** `webhook_service_base`  
**Integraciones comunes:** Slack, Discord, Email, SMS  
**Estimación:** 16 horas de construcción  

**Ejemplo de uso:**
- Sincronización entre sistemas internos
- Notificaciones automáticas multi-canal
- Automatización de workflows empresariales

### 2.2 Características de los Autopilotos

Todos los autopilotos generados incluyen:

- ✅ **Backend completo** (FastAPI con endpoints REST)
- ✅ **Base de datos** (PostgreSQL con modelos SQLModel)
- ✅ **Autenticación** (JWT tokens + API keys)
- ✅ **Frontend** (Next.js o landing específico)
- ✅ **Integraciones** (APIs externas configuradas)
- ✅ **Documentación** (API docs + guía de uso)
- ✅ **Deploy automático** (listo en producción)
- ✅ **Monitoreo** (logs + métricas)

---

## 3. Qué Ve el Cliente Final

### 3.1 Puntos de Contacto del Cliente

El cliente final interactúa ÚNICAMENTE con:

#### **A) Landing Page del Autopiloto**
- Página de marketing profesional
- Explica qué hace el autopiloto específico
- Call-to-action claro (comprar/contratar)
- Diseño personalizado según marca del cliente

**Ejemplo:** `https://autopilot-ventas-xyz.com`

#### **B) Agente Vendedor (AI)**
- Chat inteligente que cierra la venta
- Responde preguntas sobre el autopiloto
- Procesa pago (Stripe/MercadoPago)
- Genera orden automáticamente

**Ejemplo:** Chat widget en la landing

#### **C) Portal Limitado del Cliente**
- Dashboard simple para usar SU autopiloto
- Ver estadísticas de uso
- Configuraciones básicas
- Acceso a documentación

**Ejemplo:** `https://portal.autopilot-ventas-xyz.com`

### 3.2 Qué el Cliente NUNCA Ve

El cliente NO tiene acceso a:

- ❌ Super Axon Agent (director de producción)
- ❌ Consola de AXON Agency (herramienta interna)
- ❌ Proceso de construcción del autopiloto
- ❌ Código fuente interno
- ❌ Infraestructura de la fábrica
- ❌ Otros clientes o sus productos
- ❌ Panel de administración de la fábrica

**Analogía:** Como comprar un iPhone:
- ✅ Cliente ve: tienda Apple, sitio web, producto terminado
- ❌ Cliente NO ve: fábrica en China, proceso de manufactura, cadena de suministro

---

## 4. Arquitectura de Dos Mundos

La fábrica AXON opera en **dos mundos complementarios** que se comunican entre sí.

### 4.1 Mundo 1: REPLIT (Cerebro - Orquestación)

**Ubicación:** Replit Workspaces (cloud)  
**Rol:** Cerebro central, orquestación, interfaz para Federico

**Componentes principales:**

#### **Super Axon Agent**
- Director de producción principal
- Lee órdenes de clientes
- Planifica construcción de autopilotos
- Delega a subagentes especializados
- Monitorea progreso
- Reporta status a Federico

#### **ChatOrchestrationService**
- Interfaz de chat inteligente
- Clasifica intents (INFO vs BUILD)
- Rutas entre LLM directo y Autonomous Agent
- Mantiene contexto de conversaciones

#### **API de Órdenes** (diseñada, no implementada)
- Lectura/escritura de Orders (órdenes de clientes)
- Estados: nuevo → planificación → construcción → qa → listo → entregado
- Tracking de progreso
- Logs de construcción

#### **LLM Routing**
- Multi-provider: Gemini, OpenAI, Ollama
- Selección inteligente según tarea
- Fallback automático

#### **UI /agent**
- Dashboard para Federico y operadores
- Monitoreo de construcciones activas
- Chat con Super Axon Agent
- Vista de autonomous sessions

**Tecnologías:**
- FastAPI (backend)
- Next.js (frontend)
- SQLite/PostgreSQL (database)
- Socket.io (WebSockets)
- Python 3.11+

---

### 4.2 Mundo 2: AXON 88 (Producción - Ejecución)

**Ubicación:** Jetson AGX Orin (hardware físico en oficina de Federico)  
**Rol:** Planta de producción, ejecución, servicios locales

**Hardware:**
- **Jetson AGX Orin Developer Kit**
- 64GB RAM
- GPU integrada (IA local)
- 2TB NVMe SSD
- Red 1Gbps+

**Servicios instalados:**

#### **PostgreSQL**
- Base de datos producción
- Multi-tenant (RLS por cliente)
- Backups automáticos

#### **Redis**
- Cache
- Pub/Sub para eventos
- Session storage

#### **n8n**
- Workflows de automatización
- Integraciones con APIs externas (WhatsApp, Stripe, etc.)
- Triggers y acciones automatizadas

#### **Docker**
- Containers para proyectos aislados
- Sandboxing de código

#### **LLMs locales (Ollama)**
- DeepSeek-R1 (razonamiento)
- Mistral (general purpose)
- Llama 3.1 (conversación)
- Sin costo de API, privacidad total

#### **control-api (puerto 8088)**
- API de control de servicios locales
- Gestión de Docker containers
- Logs y métricas
- Health checks

#### **portal-agents (puerto 3080)**
- Consola interna para Federico/operadores
- Vista de órdenes activas
- Status de la fábrica
- Logs en tiempo real
- Métricas de producción
- **NO es el portal público de clientes**

#### **~/factory/ estructura**
```
~/factory/
├── products/          # Autopilotos generados
│   ├── autopilot-xyz-001/
│   ├── autopilot-abc-002/
│   └── ...
├── templates/         # Templates base
│   ├── autopilot_base/
│   ├── whatsapp_bot_base/
│   ├── sales_funnel_base/
│   └── webhook_service_base/
└── config/            # Configuraciones
    ├── product_types.json
    └── integrations.json
```

#### **MetaFederico Framework**
- Antes: meta-agente principal
- Ahora: módulo/toolbox integrado
- Super Axon Agent lo usa como herramienta
- Conserva funcionalidades específicas de arquitectura empresarial

---

### 4.3 Comunicación entre Mundos

```
┌─────────────────────────────────────┐
│  REPLIT (Cerebro - Orquestación)    │
│                                     │
│  • Super Axon Agent                 │
│  • ChatOrchestrationService         │
│  • API de Órdenes                   │
│  • LLM Routing (Gemini/OpenAI)      │
│  • UI /agent                        │
└──────────────┬──────────────────────┘
               │
               │ Cloudflare Tunnel
               │ https://api-axon88.algorithmicsai.com
               ↓
┌─────────────────────────────────────┐
│  AXON 88 (Producción - Ejecución)   │
│                                     │
│  • control-api (8088)               │
│  • portal-agents (3080)             │
│  • PostgreSQL, Redis, n8n, Docker   │
│  • Ollama (LLMs locales)            │
│  • ~/factory/ (products + templates)│
│  • MetaFederico toolbox             │
└─────────────────────────────────────┘
```

**Protocolo de comunicación:**
- **Túnel seguro:** Cloudflare Tunnel (sin exponer puertos directamente)
- **Autenticación:** API tokens
- **Formato:** REST JSON + WebSockets
- **Latencia:** <100ms (óptimo para operaciones en tiempo real)

**Opciones de deployment de frontend:**
- Vercel/Netlify (cloud) → habla con Axon 88 via tunnel
- Replit (cloud) → habla con Axon 88 via tunnel
- Axon 88 local (servido directamente desde Jetson)

---

## 5. Flujo Completo de una Orden

### 5.1 Paso 1: VENTA

**Actor:** Cliente final  
**Duración:** 5-15 minutos

1. Cliente llega a **landing page** del autopiloto
   - Ejemplo: `https://autopilot-whatsapp.axon88.com`
   - Lee sobre el producto
   - Ve demo/video explicativo

2. Cliente habla con **Agente Vendedor (AI)**
   - Chat inteligente responde preguntas
   - Explica características y precio
   - Ofrece onboarding personalizado
   - Cierra la venta conversacionalmente

3. Cliente hace **pago**
   - Stripe o MercadoPago
   - Proceso seguro y simple
   - Confirmación inmediata

4. Sistema crea **Order automáticamente**
   - Order.tipo_producto = "autopilot_whatsapp"
   - Order.datos_cliente = {info del cliente}
   - Order.estado = "nuevo"
   - Se envía notificación a Federico

**Salida:** Orden creada, cliente recibe email de confirmación

---

### 5.2 Paso 2: PLANIFICACIÓN

**Actor:** Super Axon Agent  
**Duración:** 10-30 minutos

1. **Super Axon Agent lee orden pendiente**
   - Query DB: `SELECT * FROM orders WHERE estado='nuevo' ORDER BY prioridad DESC`
   - Prioriza según urgencia y complejidad

2. **Clasifica tipo de producto**
   - Lee Order.tipo_producto
   - Consulta catálogo de productos (PRODUCT_TYPES)
   - Identifica stack base y templates

3. **Propone plan de construcción detallado:**
   - **Stack tecnológico:** FastAPI, Next.js, PostgreSQL, Redis
   - **Integraciones necesarias:** WhatsApp Business API, Stripe
   - **Templates a usar:** autopilot_base + whatsapp_bot_base
   - **Recursos requeridos:** 2 CPU cores, 4GB RAM, 20GB storage
   - **Estimación de tiempo:** 24 horas
   - **Subagentes asignados:** Builder, Developer, QA, Security

4. **Usa LLM para refinar plan**
   - Gemini/OpenAI analiza datos del cliente
   - Personaliza configuración según industria
   - Identifica requisitos especiales

5. **Actualiza orden:**
   - Order.plan = {plan completo}
   - Order.estado = "planificación"
   - Order.planificado_at = timestamp actual

6. **Notifica a Federico**
   - Email/Slack con resumen del plan
   - Federico puede aprobar o ajustar
   - Si aprobado → continúa a construcción

**Salida:** Plan detallado, orden en estado "planificación"

---

### 5.3 Paso 3: CONSTRUCCIÓN

**Actor:** Builder Agent + Developer Subagent + RAG Agent  
**Duración:** 8-48 horas (según complejidad)

#### **3.1 Builder Agent - Proyecto Base**

1. **Crea proyecto desde template**
   - Clona template: `autopilot_base` + `whatsapp_bot_base`
   - Estructura de carpetas
   - Configuraciones base

2. **Genera código base**
   - Backend FastAPI con endpoints REST
   - Modelos SQLModel para DB
   - Autenticación JWT
   - Middleware y seguridad

3. **Configura database**
   - Schema PostgreSQL
   - Migraciones (Alembic)
   - Seeders con datos iniciales

#### **3.2 Developer Subagent - Lógica Específica**

1. **Implementa lógica del cliente**
   - Lee Order.datos_cliente.configuracion
   - Personaliza según industria
   - Adapta flujos conversacionales

2. **Integra APIs externas**
   - WhatsApp Business API setup
   - Stripe payment webhooks
   - Google Sheets (si aplica)

3. **Frontend personalizado**
   - Landing page con branding del cliente
   - Portal de administración
   - Componentes React/Next.js

4. **Workflows n8n**
   - Automatizaciones específicas
   - Triggers de eventos
   - Acciones multi-step

#### **3.3 RAG Agent - Knowledge Base (si aplica)**

1. **Indexa información del cliente**
   - Documentos, FAQs, catálogo de productos
   - Genera embeddings
   - Almacena en vector store

2. **Configura retrieval**
   - Setup de búsqueda semántica
   - Ranking de resultados
   - Context injection para LLM

#### **3.4 Tracking de progreso**

- Order.estado = "construcción"
- Order.progreso = 0 → 75% (actualizado en tiempo real)
- Order.logs[] = eventos de construcción
- Order.construccion_iniciada_at = timestamp

**Salida:** Código completo, DB configurada, integraciones listas

---

### 5.4 Paso 4: QUALITY ASSURANCE

**Actor:** Review Council (QA + Security + Performance + Architect)  
**Duración:** 2-8 horas

#### **4.1 QA Agent - Tests Automatizados**

1. **Unit tests**
   - Funciones y métodos individuales
   - Edge cases
   - Coverage >80%

2. **Integration tests**
   - Endpoints API
   - Database operations
   - Workflows completos

3. **End-to-end tests**
   - User journeys completos
   - Simulación de casos reales
   - Validación de integraciones

**Criterios de aprobación:**
- ✅ 95%+ tests passing
- ✅ No errores críticos
- ✅ Funcionalidad completa

#### **4.2 Security Agent - Auditoría de Seguridad**

1. **Revisa vulnerabilidades**
   - SQL injection
   - XSS, CSRF
   - Exposición de secrets
   - Rate limiting

2. **Validación de autenticación**
   - JWT implementation correcta
   - API key security
   - Permissions/roles

3. **Compliance checks**
   - GDPR (si aplica)
   - PCI DSS (para pagos)
   - Encriptación de datos sensibles

**Criterios de aprobación:**
- ✅ No vulnerabilidades críticas
- ✅ Secrets bien manejados
- ✅ Auth implementado correctamente

#### **4.3 Performance Agent - Optimización**

1. **Métricas de performance**
   - Response time <200ms (endpoints API)
   - Memory usage <500MB (idle)
   - Database queries optimizadas

2. **Optimizaciones**
   - Indexes en DB
   - Caching con Redis
   - Lazy loading (frontend)

3. **Load testing**
   - Simula 100+ usuarios concurrentes
   - Identifica bottlenecks
   - Ajusta resources

**Criterios de aprobación:**
- ✅ API <300ms p95
- ✅ No memory leaks
- ✅ Soporta carga esperada

#### **4.4 Architect Supervisor - Revisión de Arquitectura**

1. **Code quality**
   - Estructura clara
   - Separación de concerns
   - Patterns bien aplicados

2. **Escalabilidad**
   - Diseño permite crecimiento
   - Microservicios (si aplica)
   - Horizontal scaling ready

3. **Mantenibilidad**
   - Código documentado
   - README completo
   - Deploy automatizable

#### **4.5 Review Council - Decisión Final**

**Proceso:**
1. Cada agente genera reporte
2. Council evalúa reportes
3. Voto: APROBADO / RECHAZADO / MEJORAS MENORES

**Si APROBADO:**
- Order.estado = "listo"
- Order.progreso = 100%
- Order.qa_iniciada_at = timestamp

**Si RECHAZADO:**
- Order.estado = "construcción" (regresa)
- Order.logs[] += feedback detallado
- Developer Agent hace correcciones

#### **4.6 Autonomous Agent - Mejoras Finales**

- Aplica mejoras menores sugeridas
- Refinamiento de UX
- Optimizaciones de código
- Documentación final

**Salida:** Producto validado, listo para deploy

---

### 5.5 Paso 5: ENTREGA

**Actor:** Ops Agent  
**Duración:** 1-4 horas

#### **5.1 Deploy a Producción**

**Opción A: Deploy en Axon 88 (local)**
```bash
cd ~/factory/products/autopilot-xyz-001
docker-compose up -d
```

**Opción B: Deploy en Cloud (Vercel/Railway)**
```bash
git push origin main
vercel deploy --prod
```

#### **5.2 Configuración DNS**
- Crear subdominio: `autopilot-xyz.axon88.com`
- SSL/TLS automático (Let's Encrypt)
- CDN setup (Cloudflare)

#### **5.3 Generación de Credenciales**

```json
{
  "admin_email": "admin@empresa-xyz.com",
  "admin_password_temporal": "ChangeMe123!",
  "api_key": "axon_pk_live_abc123xyz789",
  "webhook_secret": "whsec_def456uvw"
}
```

#### **5.4 Creación de Portal Limitado del Cliente**

- URL: `https://portal.autopilot-xyz.axon88.com`
- Dashboard simple con:
  - Estadísticas de uso
  - Configuraciones básicas
  - Documentación
  - Soporte

#### **5.5 Actualización de Order**

```python
Order.estado = "listo"
Order.progreso = 100
Order.resultado = {
    "portal_url": "https://autopilot-xyz.axon88.com",
    "admin_url": "https://autopilot-xyz.axon88.com/admin",
    "credentials": {...},
    "docs_url": "https://docs.axon88.com/autopilot-xyz",
    "support_email": "support@axon88.com",
    "whatsapp_webhook": "https://autopilot-xyz.axon88.com/webhooks/whatsapp"
}
Order.deploy_url = "https://autopilot-xyz.axon88.com"
Order.repo_url = "https://github.com/axon88-products/autopilot-xyz"
```

#### **5.6 Notificación al Cliente**

**Email automático:**
```
¡Tu Autopilot WhatsApp está listo! 🎉

Hola [Nombre],

Tu autopilot está desplegado y funcionando:

🌐 URL: https://autopilot-xyz.axon88.com
🔐 Credenciales: [ver abajo]
📚 Documentación: https://docs.axon88.com/autopilot-xyz

Próximos pasos:
1. Inicia sesión con las credenciales temporales
2. Cambia tu contraseña
3. Configura tu número de WhatsApp
4. ¡Empieza a vender!

Cualquier duda: support@axon88.com

Saludos,
Equipo AXON
```

**Salida:** Producto en producción, cliente notificado

---

### 5.6 Paso 6: POST-ENTREGA

**Actor:** Autonomous Agent + Learning Layer  
**Duración:** Continuo (24/7)

#### **6.1 Cliente Accede a su Autopilot**

- Login en portal
- Configura WhatsApp Business API
- Personaliza mensajes
- Activa autopilot

#### **6.2 Monitoreo Continuo (Autonomous Agent)**

**Métricas monitoreadas:**
- Uptime (99.9% SLA)
- Response time (API)
- Error rate (<0.1%)
- Número de conversaciones
- Tasa de conversión

**Alertas automáticas:**
- Si uptime <99%
- Si error rate >1%
- Si response time >500ms
- Si picos inusuales de tráfico

#### **6.3 Learning Layer - Aprende de Feedback**

**Datos recolectados:**
- Conversaciones exitosas vs fallidas
- Patrones de uso
- Preguntas frecuentes no contestadas
- Feedback del cliente

**Mejoras automáticas:**
- Ajusta prompts de IA
- Añade FAQs nuevas a knowledge base
- Optimiza flujos conversacionales
- Sugiere nuevas features

#### **6.4 Self-Improvement Continuo**

**Background tasks:**
- Re-entrenar modelos RAG con nuevos datos
- Optimizar queries de DB
- Actualizar integraciones (nuevas versiones)
- Aplicar security patches

#### **6.5 Order Final**

```python
Order.estado = "entregado"
Order.entregado_at = timestamp_actual
Order.progreso = 100
```

**Salida:** Cliente usando autopilot, sistema auto-mejorable

---

## 6. Rol del Super Axon Agent

### 6.1 Identidad

**Super Axon Agent = Director de Producción de la Fábrica**

No es un chatbot genérico. Es un **agente autónomo especializado** en:
- Orquestar construcción de autopilotos
- Gestionar subagentes especializados
- Mantener calidad y coherencia
- Reportar a Federico (dueño de la fábrica)

### 6.2 Responsabilidades Principales

#### **A) Gestión de Cola de Órdenes**

```python
# Cada N minutos (o real-time con WebSocket)
pending_orders = db.query(Order).filter(
    Order.estado == "nuevo"
).order_by(
    Order.prioridad.desc(),
    Order.created_at.asc()
).limit(10).all()

for order in pending_orders:
    await super_axon.process_order(order)
```

- Lee órdenes nuevas
- Prioriza según urgencia (alta, normal, baja)
- Balancea carga entre subagentes

#### **B) Planificación Estratégica**

Para cada orden:
1. Analiza Order.tipo_producto
2. Consulta catálogo PRODUCT_TYPES
3. Usa LLM para generar plan personalizado
4. Valida viabilidad técnica
5. Estima recursos y tiempo
6. Asigna subagentes apropiados

#### **C) Delegación a Subagentes**

**10 Subagentes Especializados:**

1. **Marketing Agent**
   - Campañas de lanzamiento
   - Copy para landings
   - Email marketing
   - Contenido para redes sociales

2. **Installer Agent**
   - Setup de APIs externas
   - Configuración de webhooks
   - Gestión de secrets
   - Integraciones con Replit

3. **Developer Agent**
   - Backend (FastAPI)
   - Frontend (Next.js/React)
   - Database (PostgreSQL)
   - Tests automatizados

4. **Planner Agent**
   - Roadmaps de proyectos
   - Arquitectura de soluciones
   - Especificaciones técnicas
   - Diagramas y documentación

5. **Ops Agent**
   - Deployment (Docker, Vercel, etc.)
   - Monitoreo (logs, métricas)
   - Backups y disaster recovery
   - CI/CD pipelines

6. **QA Agent**
   - Tests funcionales
   - Tests de integración
   - Regression testing
   - Quality reports

7. **Security Agent**
   - Auditorías de seguridad
   - Penetration testing
   - Compliance checks
   - Vulnerability scanning

8. **Performance Agent**
   - Optimización de código
   - Database tuning
   - Caching strategies
   - Load testing

9. **RAG Agent**
   - Indexación de knowledge bases
   - Embeddings generation
   - Vector store management
   - Semantic search setup

10. **Autopilot Agent**
    - Automatizaciones n8n
    - Workflows complejos
    - Procesos multi-step
    - Event-driven actions

#### **D) Orquestación de Comunicación**

```
Super Axon Agent
    ├─> Marketing Agent (genera copy landing)
    ├─> Planner Agent (diseña arquitectura)
    ├─> Developer Agent
    │       ├─> Builder subagent (scaffolding)
    │       └─> RAG Agent (si knowledge base)
    ├─> Installer Agent (APIs externas)
    └─> Review Council
            ├─> QA Agent
            ├─> Security Agent
            ├─> Performance Agent
            └─> Architect Supervisor
```

- Coordina dependencies entre agentes
- Pasa contexto relevante entre pasos
- Sincroniza milestones
- Resuelve conflictos

#### **E) Memoria Ejecutiva**

Mantiene contexto completo de cada orden:

```python
order_context = {
    "order_id": "uuid-123",
    "current_stage": "construcción",
    "progress": 45,
    "agents_involved": ["Builder", "Developer", "RAG"],
    "blockers": [],
    "decisions_made": [
        {"timestamp": "...", "agent": "Planner", "decision": "Use FastAPI + Next.js"},
        {"timestamp": "...", "agent": "Security", "decision": "Implement JWT auth"}
    ],
    "pending_tasks": [
        {"agent": "Developer", "task": "Integrate WhatsApp API"},
        {"agent": "QA", "task": "Write e2e tests"}
    ]
}
```

#### **F) Reporte a Federico**

**Updates regulares:**
- Email diario con summary de órdenes activas
- Slack/Discord notifications en tiempo real
- Dashboard en `/agent` con vista completa
- Alertas de blockers o issues críticos

**Formato de reporte:**
```
📊 AXON Factory - Daily Report

Órdenes activas: 5
├─ En planificación: 1
├─ En construcción: 2
├─ En QA: 1
└─ Listas para deploy: 1

Órdenes completadas hoy: 2
Tiempo promedio: 28 horas

Blockers:
⚠️ Order ORD-2025-005: Esperando API key de cliente (WhatsApp)

Next steps:
1. Aprobar plan de Order ORD-2025-006
2. Deploy de Order ORD-2025-003
```

### 6.3 Capacidades Técnicas

**Multi-LLM Routing:**
- Gemini 2.0 Flash (código, arquitectura)
- GPT-4o (razonamiento complejo)
- DeepSeek-R1 (local, razonamiento)
- Mistral/Llama (local, general)

**Autonomous Agent Integration:**
- Crea sesiones autónomas para construcciones complejas
- Monitorea progreso de Architect Supervisor
- Interviene si detecta problemas

**RAG & Knowledge:**
- Acceso a toda la documentación de la fábrica
- Templates y best practices indexados
- Historical data de órdenes pasadas
- Learning from outcomes

### 6.4 Modo de Operación

**Conversacional con Federico:**
```
Federico: "Tenemos una orden nueva de autopilot WhatsApp para una tienda de zapatos"

Super Axon: "Perfecto, he revisado la orden ORD-2025-007. 

Análisis:
• Tipo: autopilot_whatsapp
• Cliente: Tienda Zapatos XYZ
• Industria: Retail
• Configuración: WhatsApp +52..., horario 9-20h, idioma español

Plan propuesto:
1. Stack: FastAPI + Twilio WhatsApp API + PostgreSQL
2. Templates: autopilot_base + whatsapp_bot_base
3. Integraciones: WhatsApp Business API, Stripe (pagos)
4. Knowledge base: Catálogo de 50 productos del cliente
5. Estimación: 24 horas

Subagentes asignados:
• Planner Agent: Arquitectura (2h)
• Builder Agent: Scaffolding (4h)
• Developer Agent: Integración WhatsApp + Stripe (8h)
• RAG Agent: Indexar catálogo (2h)
• Review Council: QA + Security + Performance (8h)

¿Apruebo el plan y empiezo la construcción?"
```

**Autónomo para ejecución:**
- Una vez aprobado, ejecuta sin intervención
- Solo pide ayuda si encuentra blockers
- Actualiza progreso en tiempo real
- Completa construcción hasta QA

---

## 7. Relación con Sistemas Existentes

### 7.1 MetaFederico Framework

**Antes (modelo viejo):**
- MetaFederico = meta-agente principal
- Gestionaba todo directamente
- Monolítico

**Ahora (modelo factory):**
- MetaFederico = módulo/toolbox especializado
- Super Axon Agent lo usa como herramienta
- Conserva funcionalidades de arquitectura empresarial
- Integrado como subagent cuando se necesita

**Relación:**
```python
# Super Axon Agent usa MetaFederico para arquitecturas complejas
if order.tipo_producto == "enterprise_erp":
    # Delega a MetaFederico para arquitecturas enterprise
    meta_federico_result = await meta_federico.design_architecture(
        requirements=order.datos_cliente
    )
    order.plan.update(meta_federico_result)
```

### 7.2 portal-agents (Puerto 3080 en Axon 88)

**¿Qué es?**
- Consola interna para Federico y operadores
- Dashboard de la fábrica
- **NO es el portal público de clientes**

**Funcionalidades:**

1. **Vista de Órdenes Activas**
   - Lista de todas las órdenes
   - Estados en tiempo real
   - Progreso visual (0-100%)

2. **Status de la Fábrica**
   - Servicios running (PostgreSQL, Redis, n8n, etc.)
   - Recursos disponibles (CPU, RAM, Disk)
   - Health checks

3. **Logs Centralizados**
   - Logs de construcciones
   - Logs de subagentes
   - Logs de servicios
   - Búsqueda y filtros

4. **Métricas**
   - Órdenes completadas por día/semana/mes
   - Tiempo promedio de construcción
   - Success rate
   - Recursos consumidos

**Futuro:**
- Puede adaptarse como portal de clientes (con vistas limitadas)
- O crear portal separado para clientes
- Mantener portal-agents solo interno

### 7.3 n8n Workflows

**Rol en la fábrica:**
- Automatización de workflows
- Integraciones con APIs externas
- Orchestration de procesos multi-step

**Quién lo usa:**
- **Installer Agent:** Configura workflows para clientes
- **Ops Agent:** Monitorea y gestiona workflows existentes
- **Autopilot Agent:** Crea automatizaciones complejas

**Ejemplos de workflows:**
1. **Orden Nueva → Notificación**
   - Trigger: Nueva orden en DB
   - Acciones: Email a Federico + Slack notification

2. **WhatsApp Incoming → Autopilot**
   - Trigger: Webhook de WhatsApp
   - Acciones: Process message → LLM → Reply

3. **Deploy Completo → Cliente Notificado**
   - Trigger: Order.estado = "listo"
   - Acciones: Email con credenciales + SMS

### 7.4 Autonomous Agent Service

**Relación con Super Axon Agent:**

Super Axon Agent **orquesta**, Autonomous Agent **ejecuta**.

```python
# Super Axon Agent planifica
plan = await super_axon.create_plan(order)

# Super Axon Agent delega a Autonomous Agent para ejecución
session = await autonomous_agent_service.start_external_goal_session(
    goal=f"Construir {order.tipo_producto} según plan",
    mode="balanced",
    metadata={"order_id": order.id, "plan": plan}
)

# Autonomous Agent ejecuta con Architect Supervisor
# - Builder subagent genera código
# - Developer subagent implementa features
# - RAG Agent indexa knowledge base
# - Review Council valida

# Super Axon Agent monitorea progreso
while session.status != "completed":
    progress = await autonomous_agent_service.get_session_status(session.id)
    order.progreso = progress.percentage
    await asyncio.sleep(60)  # Check cada minuto
```

---

## 8. Visión Futura

### 8.1 Roadmap de Productos

**Fase 1 (Actual):** Productos base
- autopilot_whatsapp
- autopilot_ventas
- webhook_service

**Fase 2 (Q1 2026):** Productos verticales
- autopilot_restaurant (pedidos + delivery)
- autopilot_medical (agendas + recordatorios)
- autopilot_ecommerce (tienda completa + pagos)

**Fase 3 (Q2 2026):** Productos enterprise
- autopilot_erp (ERP completo)
- autopilot_crm (CRM + pipelines)
- autopilot_helpdesk (soporte multi-canal)

### 8.2 Escalabilidad

**Múltiples fábricas:**
```
AXON Factory México (Axon 88)
├─ Productos: WhatsApp, Ventas, Webhooks
└─ Capacidad: 20 órdenes/mes

AXON Factory USA (Axon 89)
├─ Productos: Enterprise, ERP, CRM
└─ Capacidad: 50 órdenes/mes

AXON Factory Global (Cloud)
├─ Productos: Todos
└─ Capacidad: Ilimitada (auto-scaling)
```

### 8.3 Automatización Total

**Visión:** Cliente → Orden → Producto Entregado (sin intervención humana)

**Milestones:**
1. ✅ Chat con cliente (AI)
2. ✅ Procesamiento de pago (automático)
3. ⏳ Planificación (AI con aprobación de Federico)
4. ⏳ Construcción (AI autónomo con Review Council)
5. ⏳ Deploy (automático)
6. ⏳ Notificación cliente (automático)

**Goal:** 80% de órdenes completadas sin intervención humana para 2026.

### 8.4 Aprendizaje Continuo

**Learning Layer mejora cada orden:**
- Templates más eficientes
- Prompts optimizados
- Integraciones más rápidas
- Menos errores en QA

**Meta:** Reducir tiempo promedio de construcción de 24h → 8h para productos estándar.

---

## 9. Conclusión

**AXON Agency NO es un SaaS público.**

**AXON Agency ES:**
- Una fábrica privada de autopilotos inteligentes
- Un sistema multi-agente autónomo de producción de software
- Una plataforma que entrega productos terminados, no herramientas configurables

**Diferencia clave:**
- Cliente SaaS tradicional: "Aquí está la herramienta, configúrala tú"
- Cliente AXON Factory: "Aquí está tu producto terminado, úsalo ya"

**Propuesta de valor:**
- White-glove service (hecho para ti)
- AI que construye AI (meta-automatización)
- Productos únicos por cliente (no one-size-fits-all)
- Escalabilidad mediante automatización (no mediante headcount)

**Visión 2026:**
- 500+ autopilotos entregados
- 80% construcción autónoma (sin intervención humana)
- Tiempo promedio: <8 horas (productos estándar)
- Clientes en 10+ países

---

**AXON Factory - Building the Future, Automatically. 🤖🏭**
