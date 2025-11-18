# 📋 REPLIT INVENTARIO - Estado Actual AXON Agency
**Fecha:** 14 Noviembre 2025  
**Propósito:** Documentación completa del proyecto antes de integración con Axon 88 (Jetson Orin)

---

## 🏗️ 1. ESTRUCTURA DEL PROYECTO

### Arquitectura General
```
axon-agency/
├── apps/
│   ├── api/                    # Backend FastAPI (Python 3.11)
│   │   ├── app/
│   │   │   ├── routers/        # 27 routers con ~88 endpoints
│   │   │   ├── services/       # 16 servicios core
│   │   │   ├── providers/      # LLM providers (OpenAI, Gemini, Ollama)
│   │   │   ├── models/         # SQLModel schemas
│   │   │   └── core/           # Config, security, database
│   │   └── requirements.txt    # 26 dependencias principales
│   │
│   └── web/                    # Frontend Next.js 15 (TypeScript)
│       ├── app/                # 20 páginas/rutas
│       ├── components/         # UI components (shadcn/ui)
│       ├── lib/                # API client, hooks, utils
│       └── package.json        # React 19, TanStack Query, Socket.IO
│
├── docs/                       # Documentación
│   └── night-shift-report.md  # Últimas 6 features implementadas
│
└── replit.md                   # Arquitectura y memoria del proyecto
```

### Lenguajes y Frameworks
- **Backend:** Python 3.11 + FastAPI + Uvicorn + SQLModel
- **Frontend:** TypeScript + Next.js 15 + React 19 + Tailwind CSS
- **Database:** SQLite (desarrollo) → PostgreSQL (producción)
- **Real-time:** Socket.IO (bidireccional)
- **AI/ML:** OpenAI SDK, Google Gemini, sentence-transformers, faiss-cpu

---

## 🔌 2. BACKEND - API ENDPOINTS

### Total: ~88 endpoints distribuidos en 27 routers

#### A) AI & Agent Orchestration (Core del sistema)
**Router: `/api/agent/*`** (agent.py)
- `POST /chat` - Super Axon Agent (orquestador principal)
- `POST /stt` - Speech-to-text con OpenAI Whisper (autenticado)

**Router: `/api/prompt/*`** (prompt.py)  
- `POST /improve` - Prompt Refiner PRO con multi-LLM fallback
- `GET /status` - Estado del servicio

**Router: `/api/llm/*`** (llm.py)
- `POST /chat` - Chat directo multi-LLM
- `POST /chat/stream` - Streaming SSE token-by-token
- `GET /languages` - Lenguajes soportados
- `GET /health` - Health check

**Router: `/api/agent/meta/*`** (meta_agent.py)
- `POST /agents` - Crear agente especializado (SECURITY, PERFORMANCE, QA, BUILDER, etc.)
- `GET /agents` - Listar agentes
- `GET /agents/{id}` - Info de agente
- `DELETE /agents/{id}` - Eliminar agente
- `POST /agents/{id}/assign` - Asignar tarea
- `POST /agents/{id}/complete` - Marcar completado
- `GET /agents/{id}/metrics` - Métricas del agente
- `GET /agents/{id}/status` - Estado actual
- `GET /catalog` - Catálogo de tipos de agentes

**Router: `/api/agent/autonomous/*`** (autonomous.py)
- `POST /sessions` - Crear sesión autónoma de self-improvement
- `GET /sessions` - Listar sesiones
- `GET /sessions/{id}` - Detalle de sesión
- `POST /sessions/{id}/cancel` - Cancelar sesión
- `GET /sessions/{id}/status` - Estado
- `GET /sessions/{id}/diff` - Ver diff de cambios
- `POST /sessions/{id}/apply` - Aplicar cambios
- `POST /sessions/{id}/reject` - Rechazar cambios
- `GET /metrics` - Métricas globales

#### B) RAG & Knowledge Management
**Router: `/api/rag/*`** (rag.py)
- `POST /create` - Crear corpus
- `POST /upload` - Subir documentos
- `POST /query` - Query semántico
- `GET /corpus/{id}/stats` - Estadísticas

**Router: `/api/memory/*`** (memory.py)
- `POST /store` - Guardar memoria
- `POST /recall` - Recuperar memoria
- `POST /search` - Búsqueda semántica
- `GET /stats` - Estadísticas de memoria

**Router: `/api/training/*`** (training.py)
- `POST /datasets/create` - Crear dataset
- `GET /datasets/list` - Listar datasets
- `POST /jobs` - Crear job de entrenamiento

**Router: `/api/evaluation/*`** (evaluation.py)
- `POST /create` - Crear evaluación
- `GET /jobs` - Listar evaluaciones
- `POST /jobs/{id}` - Detalle
- `GET /jobs/{id}` - Estado

#### C) Self-Improvement System
**Router: `/api/self-improve/*`** (self_improve.py)
- `POST /analyze` - Analizar código para mejoras
- `POST /execute` - Ejecutar mejora
- `GET /jobs` - Listar trabajos de mejora

**Router: `/api/learning/*`** (learning.py)
- `POST /record-outcome` - Registrar resultado de mejora
- `POST /get-suggestions` - Obtener sugerencias basadas en histórico
- `GET /outcomes` - Listar outcomes
- `DELETE /outcomes/{id}` - Eliminar outcome
- `POST /search-similar` - Búsqueda semántica de casos similares
- `GET /stats` - Estadísticas del learning layer
- `POST /retrain` - Re-entrenar vector store

**Router: `/api/improvement-jobs/*`** (improvement_jobs.py)
- `POST /jobs` - Crear job
- `GET /jobs` - Listar jobs
- `GET /jobs/{id}` - Detalle
- `PUT /jobs/{id}` - Actualizar
- `DELETE /jobs/{id}` - Eliminar
- `POST /jobs/{id}/execute` - Ejecutar
- `POST /jobs/{id}/approve` - Aprobar
- `POST /jobs/{id}/reject` - Rechazar
- `POST /jobs/{id}/cleanup` - Limpiar
- `POST /jobs/{id}/apply` - Aplicar cambios

#### D) Code Playground
**Router: `/api/playground/*`** (playground.py)
- `POST /execute` - Ejecutar código en Docker sandbox
- `POST /chat` - Chat con AI assistant

#### E) Projects & Auto-Builder
**Router: `/api/projects/*`** (projects.py)
- `POST /draft` - Crear borrador de proyecto
- `POST /generate` - Generar proyecto completo (Auto-Builder MVP)
- `GET /generate/{id}/download` - Descargar proyecto generado

#### F) Infrastructure & Integration
**Router: `/api/health`** (health.py)
- `GET /health` - Health check general

**Router: `/api/metrics`** (metrics.py)
- `GET /api/metrics` - Métricas del sistema

**Router: `/api/auth/*`** (auth.py)
- `POST /dev/token` - Generar token de desarrollo
- Otros endpoints de autenticación (login, register)

**Router: `/api/axon-core/*`** (axon_core.py)
- `GET /health` - Health check de Axon Core
- `POST /command` - Ejecutar comando en Axon Core
- `GET /file/{path}` - Obtener archivo
- Otros endpoints para comunicación con Axon 88

**Router: `/api/integrations/*`** (integrations.py)
- CRUD para integraciones (WhatsApp, Telegram, n8n, etc.)

#### G) Social Media & Campaigns (UI preparada, backend parcial)
**Router: `/api/campaigns/*`** (campaigns.py)
- CRUD básico de campañas

**Router: `/api/posts/*`** (posts.py)  
- CRUD básico de posts

**Router: `/api/conversations/*`** (conversations.py)
- `GET /list` - Listar conversaciones del chat
- `POST /create` - Crear conversación
- CRUD básico

**Router: `/api/media/*`** (media.py)
- Upload y gestión de media

**Router: `/api/autopilots/*`** (autopilots.py)
- CRUD de autopilots (automatizaciones)

**Router: `/api/services/*`** (services.py)
- Gestión de servicios externos

---

## 🎯 3. SERVICIOS CORE (Backend)

### ChatOrchestrationService (449 líneas)
**Archivo:** `app/services/chat_orchestration.py`

**Sistema Prompt Épico (106 líneas):**
- Define SUPER AXON AGENT como orquestador central
- 12 reglas de gobierno
- **10 subagentes declarados:**
  1. Marketing Agent
  2. Installer Agent
  3. Developer Agent
  4. Planner Agent
  5. Ops Agent
  6. QA Agent
  7. Security Agent
  8. Performance Agent
  9. RAG Agent
  10. Autopilot Agent
- **8-Step Response Format** (Respuesta → Análisis → Subagentes → Plan → Ejecución → Review → Memory → Next Steps)
- Multi-LLM routing: Ollama local + GPT/Gemini cloud
- Integración con n8n, Replit, Axon Core, MetaFederico

**Funcionalidades:**
- Intent classification (INFO, SMALL_HELP, AUTONOMOUS_BUILD)
- Respuestas directas para preguntas simples
- Delegación a Autonomous Agent para builds complejos
- Tracking de sesiones
- Multi-LLM fallback chain

### AutonomousAgentService (1,130 líneas)
**Archivo:** `app/services/autonomous_agent.py`

**Capacidades:**
- Self-improvement de código existente
- Análisis estático con introspection
- Generación de mejoras
- **Review Council** (Security, Performance, QA reviewers)
- **Architect Supervisor** (revisión obligatoria antes de aplicar cambios)
- Workspace temporal (Git-free)
- Async offloading
- Cooperative cancellation

**LIMITACIÓN CRÍTICA IDENTIFICADA:**
❌ **NO puede construir proyectos nuevos desde cero** - solo mejora código existente
✅ Perfecto para self-improvement
❌ No reemplaza al Builder Agent que necesitamos

### LLMRouter (407 líneas)
**Archivo:** `app/services/llm_router.py`

**Providers configurados:**
- **Gemini:** gemini-2.0-flash-exp (preferido) ✅ FUNCIONAL
- **OpenAI:** gpt-4o-mini (fallback) ✅ FUNCIONAL
- **Ollama:** llama3.1 (local) ⚠️ DISPONIBLE pero no en Replit

**Routing inteligente:**
- Auto-clasificación de tareas
- Fallback chain automático
- Métricas por provider
- Streaming support

### Review Council Services
**Archivos:**
- `security_reviewer.py` - Analiza vulnerabilidades
- `performance_reviewer.py` - Optimizaciones
- `qa_reviewer.py` - Calidad de código
- `review_council.py` - Orquestador de revisiones

**Estado:** ✅ Implementado y funcional

### Architect Service
**Archivo:** `architect.py`

**Funcionalidades:**
- Revisión arquitectónica obligatoria
- Análisis de cambios
- Recomendaciones estratégicas

**Estado:** ✅ Implementado

### Learning Service
**Archivo:** `learning.py`

**Funcionalidades:**
- Almacena outcomes de mejoras
- Vector store con embeddings (22 outcomes históricos)
- Búsqueda semántica de casos similares
- Sugerencias basadas en aprendizaje

**Estado:** ✅ Implementado con OpenAI embeddings

### Otros Servicios
- `vector_store.py` - Almacenamiento vectorial (FAISS fallback a numpy)
- `document_processor.py` - Procesamiento de documentos PDF
- `embeddings.py` - OpenAI text-embedding-3-large
- `introspection.py` - Análisis de código
- `self_modification.py` - Modificación segura de código
- `specialized_agent.py` - Factory de agentes especializados
- `governance.py` - Límites y governance multi-tenant

---

## 🤖 4. LLMs Y MODELOS

### Configuración Actual (.env)
```bash
# Cloud LLMs (FUNCIONALES)
OPENAI_API_KEY=<desde Replit Secrets>
OPENAI_MODEL=gpt-4o-mini
GEMINI_MODEL=gemini-2.0-flash-exp

# Local LLMs (CONFIGURADO pero NO activo en Replit)
OLLAMA_ENABLED=false
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1
```

### Routing Multi-LLM Actual
**Preferencia:** Gemini 2.0 Flash → OpenAI gpt-4o-mini → Ollama (si está disponible)

**Implementado:**
- ✅ Multi-provider fallback chain
- ✅ Auto-detection de providers disponibles
- ✅ Streaming SSE para todos los providers
- ✅ Métricas por provider
- ✅ Task classification automática

**Planeado pero NO implementado:**
- ❌ Routing por tipo de tarea (código vs contenido vs razonamiento)
- ❌ Cost optimization
- ❌ Rate limiting por provider

### Embeddings
**Actual:** OpenAI text-embedding-3-large (dimension 3072)
**Alternativa planeada:** Local embeddings en Axon 88

---

## 🔗 5. CONEXIÓN CON AXON 88

### Variables de Entorno
```bash
AXON_CORE_API_BASE=https://api-axon88.algorithmicsai.com
AXON_CORE_API_TOKEN=                    # ⚠️ VACÍO
AXON_CORE_ENABLED=true
```

### Endpoints que llaman a Axon 88
**Router:** `axon_core.py`

**Funcionalidades declaradas:**
- Health check de Axon Core
- Ejecución de comandos remotos
- Acceso a archivos
- Gestión de servicios

### Estado Actual de la Integración
🟡 **PARCIALMENTE CONFIGURADO**
- ✅ URL configurada (https://api-axon88.algorithmicsai.com)
- ❌ Token de autenticación vacío
- ❌ No se puede verificar conectividad real
- ⚠️ Router existe pero no sabemos si funciona sin token

**Necesitamos de Cursor (agente en Axon 88):**
1. ¿Qué servicios están corriendo en Axon 88?
2. ¿Qué LLMs locales están disponibles? (DeepSeek-R1, Mistral, Llama, etc.)
3. ¿Está MetaFederico activo? ¿Qué hace?
4. ¿Cómo generar/obtener AXON_CORE_API_TOKEN?
5. ¿Qué endpoints expone la API de Axon 88?

---

## 🎨 6. UI / FRONTEND

### Páginas Existentes (20 rutas en Next.js)
```
/                      # Dashboard/Home
/agent                 # ✅ Super Axon Agent Chat (PRODUCTION-READY)
/analytics             # Analytics dashboard (UI preparada)
/api                   # API playground/docs
/autopilots            # Autopilots management
/campaigns             # Campaigns CRUD
/comments              # Comments system
/conversations         # Conversations list
/media                 # Media library
/memberships           # Memberships
/networks              # Social networks
/partners              # Partners
/playground            # ✅ Code Playground (Monaco + Docker)
/posts                 # Posts CRUD
/profile               # User profile
/projects              # ✅ Projects + Auto-Builder MVP
/rag                   # RAG/Knowledge management
/settings              # Settings
/team                  # Team management
/telegram              # Telegram integration
/whatsapp              # WhatsApp integration
```

### /agent (Super Axon Agent Chat) - ESTADO COMPLETO

#### ✅ LO QUE FUNCIONA (Production-Ready)
1. **Streaming SSE:**
   - Parser SSE correcto (data:, [DONE], JSON extraction)
   - Progressive rendering token-by-token
   - Fallback automático a /api/agent/chat
   - Timeout 30s con error handling

2. **Chat Persistence (Offline-First):**
   - ConversationsSidebar con búsqueda y filtros
   - useChatSessions hook (localStorage + DB sync)
   - NO orphaned messages (guardado después de respuesta exitosa)
   - Dynamic titles generados por LLM
   - Relative timestamps con date-fns

3. **Prompt Refiner PRO:**
   - Botón "Mejorar" con IA
   - Multi-LLM fallback (Gemini → OpenAI → Ollama)
   - Undo stack completo (múltiples mejoras)
   - JSON error handling robusto
   - Muestra cambios, reasoning, provider usado

4. **Voice Input (Hybrid):**
   - Web Speech API (primario)
   - Backend STT con OpenAI Whisper (fallback) ✅ AUTENTICADO
   - MediaRecorder para captura
   - Timeout 30s
   - Mensajes diferenciados por modo

5. **Markdown Rendering (ChatGPT-style):**
   - MessageBubble component
   - react-markdown + remark-gfm
   - Syntax highlighting (react-syntax-highlighter, atomDark theme)
   - Tables, lists, links, blockquotes, inline code
   - Dark theme profesional

6. **Arquitectura:**
   - Single orchestrator (ChatOrchestrationService)
   - Reusa Autonomous Agent para delegación
   - Intent classification (INFO, SMALL_HELP, AUTONOMOUS_BUILD)
   - Session tracking con session_url

#### ❌ LO QUE FALTA EN /agent
- No hay visualización de "subagentes trabajando" (aunque el prompt los menciona)
- No muestra métricas en tiempo real
- No hay modo "builder" visual (para AUTONOMOUS_BUILD)
- Sidebar de conversaciones no muestra metadatos (provider usado, tipo de respuesta)

### Otras Páginas - Estado Incompleto
La mayoría tienen:
- ✅ UI básica montada (componentes shadcn/ui)
- ⚠️ Conectadas a endpoints que existen pero con datos mock/limitados
- ❌ No tienen funcionalidad real end-to-end

**Prioridades para completar:**
1. `/projects` - Auto-Builder necesita UI de progreso
2. `/rag` - RAG management necesita upload de documentos funcional
3. `/playground` - Code execution está, falta AI assistant integrado
4. `/campaigns` - Social media posting no está conectado
5. `/analytics` - Dashboard vacío, necesita métricas reales

---

## 📊 7. ESTADO vs. SYSTEM PROMPT ÉPICO

### Comparación: Promesa vs. Realidad

| Capacidad Prometida | Estado | Notas |
|---------------------|--------|-------|
| **10 Subagentes** | 🟡 PARCIAL | Declarados en prompt, NO implementados como servicios reales |
| Marketing Agent | ❌ NO | Solo descripción en prompt |
| Installer Agent | ❌ NO | Solo descripción en prompt |
| Developer Agent | 🟡 PARCIAL | Autonomous Agent hace esto parcialmente |
| Planner Agent | ❌ NO | Solo descripción en prompt |
| Ops Agent | ❌ NO | Solo descripción en prompt |
| QA Agent | ✅ SÍ | QA Reviewer en Review Council |
| Security Agent | ✅ SÍ | Security Reviewer en Review Council |
| Performance Agent | ✅ SÍ | Performance Reviewer en Review Council |
| RAG Agent | 🟡 PARCIAL | RAG service existe, no como "agente" autónomo |
| Autopilot Agent | ❌ NO | Solo descripción en prompt |
| **Builder Capabilities** | ❌ NO | Auto-Builder MVP existe pero limitado |
| Construir proyectos desde cero | ❌ NO | Autonomous Agent solo mejora existente |
| Auto-Builder MVP | 🟡 PROTOTIPO | `/projects/generate` existe, necesita testing |
| **Multi-Tenant** | ❌ NO | No hay separación de datos por tenant |
| Tenant isolation | ❌ NO | No implementado |
| Billing/quotas | ❌ NO | No implementado |
| **RAG & Knowledge** | ✅ SÍ | Implementado completamente |
| Document upload | ✅ SÍ | PDF, HTML, text processing |
| Vector store | ✅ SÍ | OpenAI embeddings + FAISS/numpy |
| Semantic search | ✅ SÍ | Query endpoint funcional |
| **Self-Improvement** | ✅ SÍ | Completamente implementado |
| Code analysis | ✅ SÍ | Introspection service |
| Autonomous improvements | ✅ SÍ | Autonomous Agent |
| Review Council | ✅ SÍ | Security, Performance, QA |
| Architect Supervisor | ✅ SÍ | Mandatory review |
| Learning Layer | ✅ SÍ | 22 historical outcomes |
| **Code Playground** | ✅ SÍ | Monaco + Docker sandbox |
| Code execution | ✅ SÍ | Múltiples lenguajes |
| AI assistance | 🟡 PARCIAL | Chat endpoint existe, no integrado en UI |
| **Multi-LLM Orchestration** | ✅ SÍ | Gemini + OpenAI + Ollama routing |
| Provider fallback | ✅ SÍ | Automático |
| Streaming | ✅ SÍ | SSE implementation |
| **Chat Interface** | ✅ SÍ | Production-ready |
| Streaming responses | ✅ SÍ | SSE con parser correcto |
| Voice input | ✅ SÍ | Web Speech + Whisper fallback |
| Prompt refinement | ✅ SÍ | AI-powered con undo |
| Persistence | ✅ SÍ | Offline-first + DB sync |
| Markdown rendering | ✅ SÍ | ChatGPT-style |
| **Integration con Axon 88** | 🟡 CONFIGURADO | Token vacío, no verificado |
| API connection | 🟡 PARCIAL | URL configurada, sin token |
| MetaFederico integration | ❓ DESCONOCIDO | Mencionado en prompt, estado real desconocido |

### Resumen de Gaps Críticos
1. **Builder Agent real** - NO existe (bloqueador para AUTONOMOUS_BUILD)
2. **Subagentes especializados** - Solo 3/10 implementados (Security, Performance, QA)
3. **Multi-tenancy** - NO implementado (bloqueador para SaaS)
4. **Integración Axon 88** - Configurada pero sin token/verificación
5. **Social Media posting** - UI lista, sin integración real

---

## 📝 8. RESUMEN EJECUTIVO

### ¿Qué hace HOY este proyecto?

**AXON Agency en Replit** es una **plataforma AI Agency híbrida** con dos componentes principales:

1. **Super Axon Agent (Chat Orchestrator)** - Interfaz conversacional producción-ready que:
   - Responde preguntas con multi-LLM routing (Gemini/OpenAI)
   - Delega builds complejos al Autonomous Agent
   - Tiene streaming SSE, voice input, prompt refinement, markdown rendering
   - Persiste conversaciones offline-first
   - Define 10 subagentes en prompt (pero solo 3 implementados)

2. **Autonomous Agent System** - Sistema de self-improvement que:
   - Analiza código existente
   - Genera mejoras
   - Pasa por Review Council (Security, Performance, QA)
   - Requiere Architect approval
   - Aprende de outcomes históricos
   - **LIMITACIÓN:** Solo mejora código existente, NO construye proyectos nuevos

### ✅ Lo que funciona BIEN
- Chat interface profesional con todas las features modernas
- Multi-LLM orchestration con fallback robusto
- Self-improvement loop completo (analyze → improve → review → apply)
- RAG/Knowledge management funcional
- Code playground con Docker sandbox
- Review Council con 3 specialized reviewers
- Learning layer adaptativo

### ❌ Lo que está ROTO o INCOMPLETO
1. **Builder Agent no existe** - Autonomous Agent solo mejora, no construye
2. **Subagentes son promesas** - 7/10 declarados en prompt pero NO implementados como servicios
3. **Multi-tenancy CERO** - No hay separación de datos, billing, quotas
4. **Integración Axon 88 parcial** - URL configurada, token vacío, sin verificación
5. **Auto-Builder MVP sin testing** - Existe endpoint pero no sabemos si funciona
6. **Social media** - UI preparada, integraciones NO conectadas
7. **Analytics dashboard vacío** - No hay métricas reales

### 🏗️ Qué debería MOVERSE a Axon 88 (cuando migremos backend)

#### Backend Completo (API FastAPI)
**Razones:**
- Jetson tiene GPU → puede correr modelos locales (DeepSeek-R1, Mistral, Llama)
- 64GB RAM + 2TB SSD → perfecto para RAG, embeddings, vector stores
- Permite integración directa con MetaFederico
- Reduce latencia (LLMs locales vs cloud API calls)
- Control total del stack

**Servicios a migrar:**
- ChatOrchestrationService
- AutonomousAgentService
- LLMRouter (con Ollama local como preferido)
- RAG services (vector store, embeddings)
- Review Council
- Architect Supervisor
- Learning Layer
- Meta-Agent factory

#### Database
- SQLite → PostgreSQL en Axon 88
- Vector store (FAISS completo, no numpy fallback)

#### Docker Services
- Code playground execution
- Auto-builder sandboxes

### ☁️ Qué puede quedar como UI en CLOUD (Replit/Vercel)

#### Frontend Next.js Completo
**Razones:**
- UI necesita baja latencia para usuarios
- Deploy en edge (Vercel) → worldwide performance
- Fácil escalado horizontal
- No necesita GPU ni recursos pesados

**Lo que queda:**
- Toda la carpeta `apps/web/`
- Comunicación con Axon 88 via API REST + WebSocket
- Autenticación JWT (token generado por Axon 88)
- Cache de conversaciones en localStorage

#### Assets Estáticos
- Media files (inicialmente)
- Frontend build artifacts

### 🔄 Arquitectura Objetivo POST-MIGRACIÓN

```
┌─────────────────────────────────────────────────┐
│          USERS (Worldwide)                      │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│     CLOUD (Vercel/Replit)                       │
│  ┌─────────────────────────────────────────┐   │
│  │  Next.js Frontend (UI only)             │   │
│  │  - Chat interface                       │   │
│  │  - Dashboard                            │   │
│  │  - Analytics                            │   │
│  │  - Settings                             │   │
│  └────────────┬────────────────────────────┘   │
└───────────────┼────────────────────────────────┘
                │ HTTPS/WSS
                │ (Cloudflare Tunnel)
                ▼
┌─────────────────────────────────────────────────┐
│   AXON 88 (Jetson AGX Orin - Federico's Home)  │
│  ┌─────────────────────────────────────────┐   │
│  │  FastAPI Backend (COMPLETE)             │   │
│  │  - Super Axon Agent Orchestrator        │   │
│  │  - Autonomous Agent System              │   │
│  │  - Multi-LLM Router (Local + Cloud)     │   │
│  │  - RAG/Knowledge System                 │   │
│  │  - Review Council                       │   │
│  │  - Builder Agent (TO BUILD)             │   │
│  │  - 10 Specialized Subagents (TO BUILD)  │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │  Local LLMs (Ollama)                    │   │
│  │  - DeepSeek-R1                          │   │
│  │  - Mistral                              │   │
│  │  - Llama 3.1                            │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │  MetaFederico Framework                 │   │
│  │  - (Integrated as toolbox/module)       │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │  PostgreSQL + Vector Store (FAISS)      │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │  Docker Engine (Code execution)         │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │  n8n Workflows                          │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 🎯 Dependencias CRÍTICAS para el Plan Maestro

Para crear el roadmap definitivo, **NECESITAMOS de Cursor** (agente en Axon 88):

1. **Inventario completo de Axon 88:**
   - Servicios corriendo (n8n, Ollama, MetaFederico, otros)
   - LLMs locales disponibles y sus capacidades
   - Estado actual de MetaFederico (¿qué hace? ¿APIs?)
   - Hardware real disponible (confirmar specs)

2. **Conectividad:**
   - Cómo generar AXON_CORE_API_TOKEN
   - Endpoints expuestos por Axon Core API
   - Status de Cloudflare Tunnel (https://api-axon88.algorithmicsai.com)

3. **Capacidades actuales:**
   - ¿Puede Axon 88 correr FastAPI + PostgreSQL + Docker?
   - ¿Networking configurado para recibir requests del frontend cloud?
   - ¿Existe sistema de backups/recovery?

### 📋 Próximos Pasos Inmediatos

1. **Federico:** Pedir a Cursor que genere **AXON88_INVENTARIO.md** con:
   - Servicios instalados
   - LLMs locales disponibles
   - MetaFederico capabilities
   - API endpoints expuestos
   - Hardware specs confirmadas

2. **Combinar inventarios:** REPLIT_INVENTARIO.md + AXON88_INVENTARIO.md

3. **Diseñar plan maestro** en 4 fases:
   - Fase 1: Completar gaps críticos aquí (Builder Agent, subagentes)
   - Fase 2: Migración backend a Axon 88
   - Fase 3: Multi-tenancy + billing
   - Fase 4: Ecosystem & growth

---

**Documento generado:** 14 Nov 2025  
**Próxima acción:** Obtener AXON88_INVENTARIO.md de Cursor  
**Objetivo:** Plan maestro integrado para "cambiar el mundo" 🌍
