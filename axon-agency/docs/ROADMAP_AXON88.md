# ROADMAP - AXON Agency en Axon 88

**Fecha:** Noviembre 28, 2025  
**Versión:** 1.0  
**Propósito:** Plan de fases para activar y estabilizar AXON Agency en máquina Axon 88  

---

## 🗺️ Mapa de Componentes

### AXON Agency API (apps/api)
- **¿Dónde corre?** Axon 88 (tu máquina)
- **Puerto:** 8080
- **BD:** PostgreSQL local
- **Responsabilidades:** 
  - Orquestación de órdenes
  - Auth multi-tenant
  - Integración con Axon Core
  - Deploy a WhatsApp, Social, Telegram

### AXON Agency Web (apps/web)
- **¿Dónde corre?** Axon 88 (tu máquina)
- **Puerto:** 5000
- **Responsabilidades:**
  - UI Dashboard
  - Tenant management
  - Order management
  - Integrations health

### Axon Core (EXTERNO - OTRO REPO)
- **¿Dónde corre?** Jetson o servidor remoto
- **Responsabilidades:**
  - Infraestructura de servicios
  - Commands
  - Workflows n8n
  - LLM remoto (opcional)
- **Cómo se integra:** `AXON_CORE_API_BASE` + `AXON_CORE_API_TOKEN`

### PostgreSQL Local
- **¿Dónde?** En Axon 88
- **Puerto:** 5432
- **Base:** `axon_agency`
- **Usuario:** `axon`

---

## 📊 Estado Actual (Según Este Repo)

### ✅ MVP - Funcionalidades Congeladas

**En el Sidebar (13 items visibles):**
1. Dashboard
2. Super Axon Agent
3. Catalog
4. Factory
5. Tenants
6. Integrations Health
7. WhatsApp Config
8. Telegram Config
9. RAG Knowledge
10. Code Playground
11. Analytics
12. Settings
13. Profile

**Completitud:**
- ✅ Auth (JWT)
- ✅ Multi-tenancy
- ✅ Orders + Deploy
- ✅ RAG + Document processing
- ✅ Code Playground

### 🟡 Experimental - Ocultos en MVP

**42+ páginas accesibles pero no visibles en menú:**
- Autonomous Agent (self-improvement)
- Meta-Agent Factory
- **Architect Agent** (`/agent/improve` - 498 líneas, UI completa)
- Client Portal por tenant
- Project Generator
- Sales Leads Agent
- +30 más

**Completitud:**
- 🟡 Autonomous Agent (70%)
- 🟡 Learning System (60%)
- 🟡 Review Council (60%)

### ❌ No Implementado (Este Repo)

- WhatsApp Sales Agent webhook (código listo, endpoint falta)
- Advanced analytics UI
- Telegram deploy frontend button (backend completo)

---

## 🚀 Roadmap por Fases

### **FASE 0 - Auditoría ✅ (COMPLETADA)**

**Objetivo:** Mapear el repositorio, identificar componentes

**Completado:**
- ✅ `docs/AXON_AGENCY_MAP.md` - Mapa interno
- ✅ `docs/ROADMAP_AXON88.md` - Este archivo
- ✅ Variables de entorno documentadas

**Checklist:**
- [x] Repos identificados (AXON Agency vs Axon Core)
- [x] Routers catalogados (33 API endpoints)
- [x] Servicios catalogados (20 services)
- [x] Rutas frontend mapeadas (42+ páginas)
- [x] Dependencias documentadas

---

### **FASE 1 - Encender API + Web con PostgreSQL Real**

**Objetivo:** AXON Agency corriendo en Axon 88 con BD real, sin DEV_MODE

**Módulos involucrados:**
- Backend: `apps/api/app/main.py`, `app/core/config.py`
- Frontend: `apps/web/` (Next.js build)
- BD: PostgreSQL local

**Variables de entorno clave:**
```bash
# API
PRODUCTION_MODE=true
DEV_MODE=false
DATABASE_URL=postgresql+psycopg://axon:PASSWORD@localhost:5432/axon_agency
JWT_SECRET=<generate-32-random-chars>
ALLOWED_ORIGINS=https://your-axon88.com
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://IP_DE_AXON88:8080
```

**Pasos:**
1. PostgreSQL corriendo en Axon 88
2. Base de datos `axon_agency` creada
3. Usuario `axon` con permisos
4. `.env` en `apps/api/` con valores reales
5. API inicia en puerto 8080
6. Frontend inicia en puerto 5000

**Checks de completitud:**
```bash
✓ curl http://localhost:8080/api/health → {"status":"ok"}
✓ JWT_SECRET ≠ "change-me-in-production"
✓ DEV_MODE=false en logs
✓ Frontend carga en http://localhost:5000
✓ Puedo hacer login
```

---

### **FASE 2 - Alineación con Axon Core**

**Objetivo:** Validar comunicación AXON Agency ↔ Axon Core

**Módulos involucrados:**
- `app/adapters/axon_core.py`
- `app/routers/axon_core.py`
- `/api/axon-core/*` endpoints

**Variables de entorno:**
```bash
AXON_CORE_API_BASE=https://api-axon88.algorithmicsai.com
AXON_CORE_API_TOKEN=<token-from-axon-core>
AXON_CORE_ENABLED=true
```

**Pasos:**
1. Verificar `AXON_CORE_API_BASE` es accesible
2. Obtener token de Axon Core (si necesario)
3. Probar endpoints proxy

**Checks de completitud:**
```bash
✓ curl http://localhost:8080/api/axon-core/health
  → {"status": "connected", "remote": "https://..."}

✓ curl http://localhost:8080/api/axon-core/catalog
  → Retorna catálogo de Axon Core

✓ curl http://localhost:8080/api/axon-core/services
  → Retorna lista de servicios

✓ Los logs NO muestran "Axon Core is not reachable"
```

**Notas:**
- Si Axon Core está en otro repo/servidor, estos checks dependen de su disponibilidad
- Sin Axon Core accesible, los endpoints retornarán errores 503 (esperado)

---

### **FASE 3 - Estabilización: Logging, Métricas, Seguridad**

**Objetivo:** Hardening de seguridad y observabilidad

**Módulos involucrados:**
- `app/core/security.py` - JWT validation
- `app/routers/tenants.py` - Admin-only endpoints
- `app/routers/orders.py` - Tenant-scoped access
- Logging en todo el stack

**Pasos:**
1. **Logging centralizado:**
   - Verificar logs en `~/.axon88/logs/` (o donde configures)
   - Rotar logs diarios
   - Nivel: INFO en prod, DEBUG en dev

2. **Admin-only protection:**
   - `/api/tenants/*` → admin only ✓
   - `/api/admin/*` → admin only ✓
   - `/api/orders/{id}/deploy/*` → admin only ✓

3. **Multi-tenant isolation:**
   - Users solo ven sus órdenes (si están en un tenant)
   - Admins ven todo
   - Legacy users (tenant_id=NULL) aislados

4. **JWT validation:**
   - Verificar tokens no expirados
   - Verificar firma
   - Verificar claims (iss, aud)

**Checks de completitud:**
```bash
✓ Logs aparecem sin errores de auth
✓ User regular NO puede listar todos los tenants
✓ User regular NO puede ver órdenes de otro tenant
✓ Admin CAN ver todo
✓ JWT expirado retorna 401
```

---

### **FASE 4 - Activación de Features Avanzadas**

**Objetivo:** Encender experimentales (Architect Agent, Autonomous, Meta-Agent, Orders Deploy)

**Módulos involucrados:**
- `app/services/architect.py` - Revisor de código
- `app/services/autonomous_agent.py` - Self-improvement
- `app/services/specialized_agent.py` - Meta-agent factory
- `app/routers/orders.py` - Deploy channels
- `app/routers/integrations.py` - Health checks

#### **4a - Architect Agent (Self-Improvement)**

**Variables de entorno:**
```bash
AUTONOMOUS_AGENT_ARCHITECT_ENABLED=true
GEMINI_API_KEY=AIzaSy...  # Para el revisor
```

**Pasos:**
1. Acceder a `/agent/improve` (oculto en menú)
2. Click en "Analizar y Sugerir"
3. API escanea el repo, genera propuestas
4. Architec revisa con Gemini
5. Puedes aprobar/rechazar

**Checks:**
```bash
✓ GET /api/self-improve/structure → Retorna análisis del repo
✓ POST /api/improve/jobs/analyze → Crea trabajos de mejora
✓ GET /api/improve/jobs → Lista trabajos
✓ POST /api/improve/jobs/{id}/approve → Arquitecto decide
```

#### **4b - Orders + Deploy Channels**

**Variables de entorno:**
```bash
# WhatsApp via n8n
N8N_WHATSAPP_DEPLOY_WEBHOOK_URL=https://n8n.example.com/webhook/deploy

# Social (Ayrshare)
AYRSHARE_API_KEY=ayr_...
ENABLE_AYRSHARE_SOCIAL=true

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
ENABLE_TELEGRAM_DEPLOY=true
```

**Pasos:**
1. Crear una orden en `/agent/orders`
2. Set estado="listo", qa_status="ok"
3. Click en "Deploy to WhatsApp" / "Deploy to Social" / "Deploy to Telegram"
4. API valida, crea payload, envía a integraciones

**Checks:**
```bash
✓ POST /api/orders/{id}/deploy/whatsapp → Webhook enviado
✓ POST /api/orders/{id}/deploy/social → Ayrshare POST
✓ POST /api/orders/{id}/deploy/telegram → Telegram Bot API
✓ GET /api/integrations/social/health → Status de Ayrshare
```

#### **4c - Autonomous Agent + Review Council**

**Variables de entorno:**
```bash
AUTONOMOUS_AGENT_REVIEW_COUNCIL_ENABLED=true
```

**Pasos:**
1. Acceder a `/agent/autonomous`
2. Iniciar sesión autónoma (CONSERVATIVE / BALANCED / AGGRESSIVE mode)
3. Agent ejecuta loop: analyze → propose → review → decide → execute

**Checks:**
```bash
✓ POST /api/autonomous/sessions → Crea sesión
✓ GET /api/autonomous/sessions/{id} → Detalle sesión
✓ WebSocket updates en tiempo real
✓ Review council genera opiniones (SECURITY, QA, PERFORMANCE)
```

**Completitud esperada:**
- Fase 4a: ✅ Completo
- Fase 4b: ✅ Completo (depende de integraciones)
- Fase 4c: 🟡 Experimental (funciona pero a medias)

---

## 📋 Checklist de Validación por Fase

### FASE 1 - Encender

```bash
# Pre-requisitos
[ ] PostgreSQL 13+ instalado en Axon 88
[ ] Python 3.9+ disponible
[ ] Node.js 18+ + npm disponible
[ ] Git disponible

# Setup API
[ ] Clonar repo: git clone ...
[ ] Crear DB: createdb axon_agency -O axon
[ ] Copiar .env.example a .env
[ ] Editar .env con valores reales
[ ] pip install -r requirements.txt
[ ] uvicorn app.main:socket_app corriendo en 8080

# Setup Frontend
[ ] cd apps/web
[ ] Copiar .env.local.example a .env.local
[ ] Editar .env.local con URL API correcta
[ ] npm install
[ ] npm run build
[ ] npm start corriendo en 5000

# Validación
[ ] curl http://localhost:8080/api/health → 200 OK
[ ] curl http://localhost:5000 → HTML del sitio
[ ] Puedo hacer login en UI
[ ] DEV_MODE=false en logs API
```

### FASE 2 - Axon Core

```bash
[ ] AXON_CORE_API_BASE configurado
[ ] AXON_CORE_ENABLED=true
[ ] curl /api/axon-core/health → 200 OK (o 503 si Axon Core offline)
[ ] curl /api/axon-core/catalog → JSON response
[ ] curl /api/axon-core/services → JSON response
```

### FASE 3 - Seguridad

```bash
[ ] Admin user creado en UI
[ ] Non-admin user creado en UI
[ ] Non-admin NO puede listar tenants
[ ] Non-admin NO puede ver órdenes de otro tenant
[ ] Admin CAN ver todo
[ ] JWT token expira correctamente
[ ] Token inválido retorna 401
```

### FASE 4 - Features

```bash
# Architect
[ ] GET /api/self-improve/structure retorna análisis
[ ] POST /api/improve/jobs/analyze crea trabajos
[ ] Gemini review funciona

# Orders + Deploy
[ ] POST /api/orders crea orden
[ ] POST /api/orders/{id}/deploy/whatsapp valida
[ ] POST /api/orders/{id}/deploy/social valida
[ ] POST /api/orders/{id}/deploy/telegram valida

# Autonomous
[ ] POST /api/autonomous/sessions crea sesión
[ ] Loop autónomo ejecuta sin errors
[ ] Review council genera opiniones
```

---

## ⚠️ TODOs y Limitaciones

### En ESTE Repo (AXON Agency)

- [ ] **TODO:** Conectar WhatsApp Sales Agent webhook a `/api/webhooks/whatsapp`
  - Código: `app/templates/whatsapp_template_full_integraia.py` ✅ Listo
  - Falta: Endpoint HTTP
  
- [ ] **TODO:** Frontend button para Telegram deploy (backend ✅)

- [ ] **TODO:** Advanced analytics dashboard UI

- [ ] **TODO:** Full test coverage (20% actual)

### Dependencias Externas (Fuera de Alcance)

- **Axon Core:** Deployado en repo separado
  - Responsabilidad: Team Axon Core
  - Integración en este repo: Solo vía HTTP + Bearer auth

- **n8n Workflows:** Configurados en Axon Core
  - AXON Agency solo envía HTTP POST a webhook

- **Ayrshare, Telegram, etc.:** APIs externas
  - AXON Agency solo cliente

---

## 🎯 Métricas de Éxito

**Fase 1:** ✅ Ambas apps corriendo, auth funcional, BD conectada
**Fase 2:** ✅ Comunicación bidireccional con Axon Core
**Fase 3:** ✅ Multi-tenant aislamiento, logging centralizado
**Fase 4:** ✅ Deploys funcionando, self-improvement activado

---

## 📞 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| Port 8080/5000 en uso | `lsof -i :8080` y mata proceso |
| DB connection error | Verifica PostgreSQL: `sudo systemctl status postgresql` |
| CORS errors en UI | Checkea `ALLOWED_ORIGINS` y `NEXT_PUBLIC_API_BASE_URL` |
| JWT errors | Verifica `JWT_SECRET` no es default |
| Axon Core offline | Normal, endpoints retornarán 503 (expected) |
| Node modules error | `npm install --force` |
| Python deps error | `pip install -r requirements.txt --force-reinstall` |

---

**Última actualización:** Noviembre 28, 2025  
**Mantenido por:** AXON Agency Team
