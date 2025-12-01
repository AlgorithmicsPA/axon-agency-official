# AXON Agency - Mapa Interno del Repositorio

**Fecha:** Noviembre 28, 2025  
**Versión:** 1.0  
**Propósito:** Auditoría y mapeo preciso de qué es AXON Agency vs Axon Core en este repositorio  

---

## 🎯 Definiciones Clave

### AXON Agency (ESTE REPO)
- **¿Qué es?** Plataforma IA full-stack / panel de control / agencia autónoma
- **Rol en Axon88:** Interfaz de usuario + orquestador de agentes + gestor de órdenes
- **Componentes:**
  - `apps/api/` - FastAPI backend con 33 routers
  - `apps/web/` - Next.js 15 frontend con 42+ páginas
  - `docs/` - Documentación técnica
  
### Axon Core (REPO EXTERNO - NO ESTÁ AQUÍ)
- **¿Qué es?** Backend de infraestructura / gestor de servicios y comandos
- **Rol en Axon88:** Capa de infraestructura subyacente
- **Ubicación:** Otro repositorio (no incluido en axon-agency/)
- **Cómo se integra:** Via API HTTP + WebSocket

---

## 📍 Cómo se Comunican en Axon 88

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIO EN NAVEGADOR                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  AXON Agency Frontend  │
                    │   (Next.js - 5000)     │
                    │  apps/web/            │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ AXON Agency API       │
                    │  (FastAPI - 8080)     │
                    │ apps/api/             │
                    └───┬─────────────────┬─┘
                        │                 │
            ┌───────────▼──────┐   ┌──────▼─────────────┐
            │                  │   │                    │
            │ PostgreSQL DB    │   │ Axon Core (externo)│
            │ (Local)          │   │ /api/axon-core/... │
            │                  │   │ (Jetson/Remote)    │
            └──────────────────┘   └────────────────────┘
```

**Comunicación:**
1. **Frontend → API (AXON Agency):** HTTP/WebSocket en puerto 5000 → 8080
2. **API (AXON Agency) → Axon Core:** HTTP via `AXON_CORE_API_BASE` (env var)
3. **Autenticación interna:** JWT local en AXON Agency
4. **Autenticación a Axon Core:** Opcional `AXON_CORE_API_TOKEN`

---

## 🏗️ Estructura Backend (apps/api)

### Routers (API Endpoints) - 33 archivos

| Categoría | Routers | Propósito |
|-----------|---------|----------|
| **Core** | health, auth, metrics | Health check, JWT auth, métricas |
| **Agentes** | agent, autonomous, meta_agent | Super Axon Agent, self-improvement, specialized agents |
| **Mejoras** | self_improve, improvement_jobs, learning | Code analysis, improvement proposals, learning system |
| **Órdenes** | orders, products, catalog, factory | Order orchestration, product catalog, agent factory |
| **Deploy** | integrations | WhatsApp, Social (Ayrshare), Telegram deploy |
| **Tenants** | tenants, admin | Multi-tenancy, admin operations |
| **Content** | media, posts, conversations, campaigns | Media upload, posts, chat history |
| **RAG** | rag, training, evaluation | Document ingestion, vector search, training |
| **Dev** | playground, projects, llm, prompt | Code editor, project generation, LLM routing |
| **External** | axon_core | Proxy a Axon Core backend externo |

### Services (Lógica de Negocio) - 20 archivos

| Servicio | Propósito | Estado |
|----------|----------|--------|
| `architect.py` | Revisor Senior (Gemini) de código | ✅ Completo |
| `autonomous_agent.py` | Orquestador autónomo | ✅ Completo |
| `review_council.py` | Multi-expert review | ✅ Completo |
| `orders_orchestrator.py` | 10-step order processing | ✅ Completo |
| `chat_orchestration.py` | Super Axon Agent | ✅ Completo |
| `llm_router.py` | Multi-provider LLM | ✅ Completo |
| `agent_blueprint_service.py` | AgentBlueprint transformation | ✅ Completo |
| `axon_factory_client.py` | Client a Axon 88 Factory | ✅ Completo |
| `vector_store.py` | FAISS embeddings | ✅ Completo |
| `document_processor.py` | PDF/HTML ingestion | ✅ Completo |
| Otros (learning, introspection, etc.) | Supporting services | 🟡 Varias medias |

### Models (Data Schemas) - 7 archivos

- `core.py` - User, Post, Media, Conversation
- `orders.py` - Order, Deliverable, DeployHistory
- `tenants.py` - Tenant, TenantUser (multi-tenancy)
- `self_improve.py` - ImprovementJob, ArchitectDecision
- `rag.py` - Document, Embedding, TrainingJob
- `llm.py` - LLMProvider, LLMCall
- `meta_agent.py` - MetaAgent, AgentInstance

### Providers (LLM APIs) - 3 archivos

- `openai.py` - OpenAI (gpt-4o, gpt-4o-mini)
- `gemini.py` - Google Gemini (2.0 Flash)
- `ollama.py` - Ollama local (optional)

### Integración con Axon Core

**Archivo clave:** `app/adapters/axon_core.py` (118 líneas)

```python
class AxonCoreClient:
    # Métodos disponibles:
    - health_check() → Conectividad a Axon Core
    - get_catalog() → Catálogo de servicios
    - chat() → LLM remoto
    - execute_command() → Comandos en Axon Core
    - list_services() → Servicios disponibles
    - get_metrics() → Métricas del sistema
    - trigger_workflow() → n8n workflows
```

**Router:** `app/routers/axon_core.py` (150 líneas)

```
GET  /api/axon-core/health     → Verifica Axon Core
GET  /api/axon-core/catalog    → Catálogo remoto
POST /api/axon-core/chat       → Chat con LLM remoto
POST /api/axon-core/command    → Ejecutar comando
GET  /api/axon-core/services   → Listar servicios
GET  /api/axon-core/metrics    → Métricas del sistema
POST /api/axon-core/workflow   → Trigger n8n workflow
```

**Variables de Entorno (en apps/api/.env):**

```bash
AXON_CORE_API_BASE=https://api-axon88.algorithmicsai.com
AXON_CORE_API_TOKEN=<token-opcional>
AXON_CORE_ENABLED=true
```

---

## 🌐 Estructura Frontend (apps/web)

### Rutas Principales

**Route Groups (Next.js 15):**

- **`(public)/`** - SIN autenticación
  - `/` - Landing page
  - `/privacy-policy`, `/terms-of-service`, `/data-deletion`

- **`(auth)/`** - CON autenticación
  - Dashboard, Agent, Catalog, Factory, etc. (13 items en MVP)
  - 42+ páginas experimentales (ocultas en menú)

### MVP Sidebar (13 items visibles)

1. `/` → Dashboard
2. `/agent` → Super Axon Agent Chat
3. `/catalog` → Catálogo de agentes
4. `/agent/factory` → Agent Factory (admin)
5. `/agent/tenants` → Tenant management (admin)
6. `/agent/integrations` → Health checks (admin)
7. `/whatsapp` → Config WhatsApp
8. `/telegram` → Config Telegram
9. `/rag` → Gestión de documentos
10. `/playground` → Code Editor
11. `/analytics` → Analytics
12. `/settings` → User settings
13. `/profile` → Mi perfil

### Páginas Experimentales (ocultas pero accesibles)

- `/agent/improve` - **Architect Agent** (498 líneas) ← UI para mejoras autónomas
- `/agent/autonomous` - Sesiones autónomas
- `/agent/meta` - Meta-agent factory
- `/portal/[tenantSlug]` - Client portal
- `/projects/new` - Project generator
- +30 más (ver `docs/PRODUCTION_CHECKLIST.md` para lista completa)

### Tecnología Frontend

- Next.js 15.5.6 + React 19
- TypeScript + Tailwind CSS
- Radix UI + shadcn/ui
- Monaco Editor (code playground)
- Recharts (analytics)
- Socket.IO (WebSocket)

---

## 🔄 Flujo de Integración Axon 88

### Escenario: Deploy de una Orden a WhatsApp

1. **Usuario en UI** hace clic en "Deploy to WhatsApp"
   - Frontend (`/agent/orders/[id]/page.tsx`)
   
2. **API recibe**: `POST /api/orders/{id}/deploy/whatsapp`
   - Router: `apps/api/app/routers/orders.py`
   
3. **Validación**:
   - ¿Admin? ✓
   - ¿Order listo (estado=listo, qa_status=ok)? ✓
   
4. **Deploy**:
   - n8n webhook (via `N8N_WHATSAPP_DEPLOY_WEBHOOK_URL`)
   - Payload incluye: tenant, order, agent_blueprint, deliverable
   
5. **Registro**:
   - Deploy history guardado en `Order.deploy_history` (JSON)
   - Status: success/failed
   
6. **Response** al frontend:
   - Confirmación + timestamp

**Nota:** El webhook n8n está en Axon Core (externo). AXON Agency solo orquesta.

---

## 📊 Dependencias Externas

### Backend (Python)

**LLM APIs:**
- OpenAI (gpt-4o, gpt-4o-mini)
- Google Gemini (2.0 Flash)

**Bases de Datos:**
- PostgreSQL (prod)
- MongoDB (WhatsApp Sales Agent)
- Redis (jobs/cache)

**Integrations:**
- n8n (workflow automation)
- Ayrshare (social media posting)
- Telegram Bot API
- Stripe (payments)
- Cal.com (scheduling)
- LinkedIn API (lead enrichment)

**Frameworks:**
- FastAPI 0.115.0
- Uvicorn + Socket.IO
- SQLAlchemy + Alembic

### Frontend (JavaScript)

**Frameworks:**
- Next.js 15.5.6
- React 19
- TailwindCSS 3.4.18

**Libraries:**
- TanStack React Query
- Zustand (state management)
- Monaco Editor
- Recharts

---

## ✅ Estado de Completitud (Este Repo)

### Completo (MVP)

| Componente | % | Notas |
|-----------|---|-------|
| Auth (JWT) | 100% | Production-ready |
| Multi-tenancy | 100% | Fases 1-8 completas |
| Orders | 100% | 10-step orchestration |
| Deploy (WhatsApp, Social, Telegram) | 100% | Production-ready |
| Architect Agent | 100% | Backend + UI básica |
| RAG | 100% | Document ingestion + search |
| Code Playground | 100% | Monaco Editor ready |
| Landing Page | 100% | Legal pages included |

### Experimental (Visible pero oculto en MVP)

| Componente | % | Estado |
|-----------|---|--------|
| Autonomous Agent | 70% | Self-improvement sistema |
| Learning System | 60% | Predicción de éxito |
| Review Council | 60% | Multi-expert review |
| Meta-Agent Factory | 60% | Specialization de agentes |

### No Implementado

| Componente | Notas |
|-----------|-------|
| WhatsApp Sales Agent Webhook | Código listo, endpoint falta conectar |
| Advanced Analytics Dashboard | Framework existe, UI media |
| Frontend Telegram Deploy Button | Backend complete, UI pending |

---

## 🔐 Variables de Entorno Críticas para Axon 88

### Backend (apps/api/.env)

```bash
# OBLIGATORIO
DEV_MODE=false
PRODUCTION_MODE=true
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/axon_agency
JWT_SECRET=<generate-32-random-chars>
ALLOWED_ORIGINS=https://your-domain.com

# LLM
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...

# Integración Axon Core
AXON_CORE_API_BASE=https://api-axon88.algorithmicsai.com
AXON_CORE_ENABLED=true

# Deploys (opcionales)
N8N_WHATSAPP_DEPLOY_WEBHOOK_URL=https://n8n.example.com/webhook/...
TELEGRAM_BOT_TOKEN=<token-from-botfather>
AYRSHARE_API_KEY=ayr_...
```

### Frontend (apps/web/.env.local)

```bash
NEXT_PUBLIC_API_BASE_URL=http://IP_DE_AXON88:8080
NEXT_PUBLIC_AXON_CORE_URL=https://api-axon88.algorithmicsai.com
NEXT_PUBLIC_WHATSAPP_PHONE_NUMBER=52xxxxxxxxxx
```

---

## 📝 Conclusión

**AXON Agency en Axon 88:**
- ✅ Completo como panel + orquestador
- ✅ Multi-tenant production-ready
- ✅ Integración con Axon Core via routers proxy
- 🟡 42+ páginas experimentales accesibles
- ⚠️ Algunas features avanzadas a medias (Learning, Council)

**Axon Core (Externo):**
- 🔗 Se comunica via `/api/axon-core/` endpoints
- 📡 HTTP + Bearer token auth (opcional)
- 🎯 Proporciona: servicios, commands, workflows, LLM remoto, métricas

---

**Última actualización:** Noviembre 28, 2025  
**Mantenido por:** AXON Agency Audit Team
