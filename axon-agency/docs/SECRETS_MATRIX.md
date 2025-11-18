# 🔐 SECRETS MATRIX - Axon Agency

Inventario completo de todas las variables de entorno y credenciales del sistema Axon Agency.

**Última actualización:** 18 de noviembre de 2025

---

## 📚 Related Documentation

**Before configuring secrets, review these guides:**

- **[QUICK_SETUP_GUIDE.md](./QUICK_SETUP_GUIDE.md)** - Step-by-step setup for development, staging, and production environments
- **[WHATSAPP_SALES_AGENT_PLAN.md](./WHATSAPP_SALES_AGENT_PLAN.md)** - Complete WhatsApp Sales Agent architecture and integration guide
- **[PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)** - Security checklist before production deployment

This document provides the **complete reference** for all environment variables. Use the guides above for **setup workflows** and **architectural details**.

---

## 📋 Índice

1. [🔹 Core / Infraestructura](#-core--infraestructura)
2. [🔹 Base de Datos y Almacenamiento](#-base-de-datos-y-almacenamiento)
3. [🔹 LLM Providers](#-llm-providers)
4. [🔹 WhatsApp Clásico (Deploy)](#-whatsapp-clásico-deploy)
5. [🔹 WhatsApp Sales Agent (Template Full IntegraIA)](#-whatsapp-sales-agent-template-full-integraia)
6. [🔹 Social Autopilots / Ayrshare](#-social-autopilots--ayrshare)
7. [🔹 Telegram Deploy](#-telegram-deploy)
8. [🔹 Servicios Externos](#-servicios-externos)
9. [🔹 Frontend (Next.js)](#-frontend-nextjs)
10. [🔹 Autonomous Agent System](#-autonomous-agent-system)

---

## 🔹 Core / Infraestructura

Variables básicas de configuración del servidor y aplicación.

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `BIND` | API Server | Opcional | dev, staging, prod | config | Dirección IP donde escucha el servidor | `0.0.0.0` |
| `PORT` | API Server | Opcional | dev, staging, prod | config | Puerto donde escucha el servidor | `8080` |
| `PRODUCTION_MODE` | API Server | Opcional | prod | config | Activa modo producción (desactiva debugging) | `true` |
| `DEV_MODE` | API Server | Opcional | dev | config | Activa bypass de autenticación (SOLO desarrollo) | `true` |
| `ALLOWED_ORIGINS` | CORS | Obligatoria | dev, staging, prod | config | Orígenes permitidos para CORS (separados por coma) | `http://localhost:3000,https://axon.agency` |

**⚠️ IMPORTANTE:** `DEV_MODE=true` desactiva autenticación - **NUNCA** usar en producción.

---

## 🔹 Base de Datos y Almacenamiento

### PostgreSQL (Base de datos principal)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `DATABASE_URL` | Core DB | Obligatoria | dev, staging, prod | secret | Connection string de PostgreSQL | `postgresql+psycopg://user:pass@host:5432/axon` |

### MongoDB (WhatsApp Sales Agent)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `MONGODB_URI` | WhatsApp Sales Agent | Obligatoria* | dev, staging, prod | secret | MongoDB connection URI (Atlas o self-hosted) | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGODB_DB_NAME` | WhatsApp Sales Agent | Opcional | dev, staging, prod | config | Nombre de la base de datos MongoDB | `whatsapp_sales_agent` |

*Obligatoria solo si se usa WhatsApp Sales Agent.

### Redis (Jobs & Cache)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `REDIS_URL` | Jobs, Cache | Opcional | dev, staging, prod | secret | Redis connection URL | `redis://localhost:6379/0` |

### Storage

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `STORAGE_ROOT` | File Storage | Opcional | dev, staging, prod | config | Directorio raíz para almacenamiento de archivos | `./storage` |

---

## 🔹 LLM Providers

### OpenAI

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `OPENAI_API_KEY` | LLM Core, Sales Agent | Obligatoria | dev, staging, prod | secret | OpenAI API key | `sk-proj-abc123...` |
| `OPENAI_BASE_URL` | LLM Core | Opcional | dev, staging, prod | config | OpenAI API base URL (para proxies) | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | LLM Core | Opcional | dev, staging, prod | config | Modelo por defecto para tareas simples | `gpt-4o-mini` |
| `OPENAI_VISION_MODEL` | LLM Core | Opcional | dev, staging, prod | config | Modelo para tareas multimodales | `gpt-4o` |

### Google Gemini

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `GEMINI_API_KEY` | LLM Core | Opcional | dev, staging, prod | secret | Google Gemini API key | `AIzaSy...` |
| `GEMINI_MODEL` | LLM Core | Opcional | dev, staging, prod | config | Modelo Gemini por defecto | `gemini-2.0-flash-exp` |
| `GEMINI_FLASH_MODEL` | LLM Core | Opcional | dev, staging, prod | config | Modelo Gemini Flash | `gemini-2.0-flash-exp` |

### Ollama (Local LLM)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `OLLAMA_ENABLED` | LLM Router | Opcional | dev, staging | config | Habilita uso de Ollama local | `false` |
| `OLLAMA_BASE_URL` | LLM Router | Opcional | dev, staging | config | URL del servidor Ollama | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | LLM Router | Opcional | dev, staging | config | Modelo Ollama por defecto | `llama3.1` |

### LLM Router

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `LLM_ROUTER_ENABLED` | LLM Router | Opcional | dev, staging, prod | config | Habilita routing inteligente entre LLMs | `true` |

### Embeddings

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `EMBEDDING_MODEL` | Vector Embeddings | Opcional | dev, staging, prod | config | Modelo OpenAI para embeddings (RAG/vectorización) | `text-embedding-3-large` |

---

## 🔹 WhatsApp Clásico (Deploy)

Deploy de autopilots a WhatsApp vía webhook n8n.

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `N8N_WHATSAPP_DEPLOY_WEBHOOK_URL` | WhatsApp Deploy | Obligatoria* | staging, prod | secret | Webhook URL de n8n para deploy WhatsApp | `https://n8n.example.com/webhook/whatsapp-deploy` |

*Obligatoria solo para deploy de autopilots WhatsApp.

---

## 🔹 WhatsApp Sales Agent (Template Full IntegraIA)

Sistema completo de sales qualification con 7 integraciones externas.

### Melvis (RAG / Vector Store)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `MELVIS_API_URL` | Sales Agent RAG | Opcional | dev, staging, prod | config | Melvis API base URL para búsqueda semántica | `https://melvis.example.com/api` |
| `MELVIS_API_KEY` | Sales Agent RAG | Opcional | dev, staging, prod | secret | Melvis API key para autenticación | `mlv_abc123...` |
| `MELVIS_COLLECTION` | Sales Agent RAG | Opcional | dev, staging, prod | config | Nombre de la colección de conocimiento | `kb_sales` |

### Tavily (Web Search)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `TAVILY_API_KEY` | Sales Agent Search | Opcional | dev, staging, prod | secret | Tavily API key para búsqueda web | `tvly-abc123...` |

### LinkedIn (Lead Enrichment)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `LINKEDIN_API_KEY` | Sales Agent Enrichment | Opcional | dev, staging, prod | secret | LinkedIn API key (o servicio alternativo) | `lin_abc123...` |
| `LINKEDIN_BASE_URL` | Sales Agent Enrichment | Opcional | dev, staging, prod | config | LinkedIn API base URL | `https://api.linkedin.com/v2` |

### Stripe (Payment Checkout)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `STRIPE_SECRET_KEY` | Sales Agent Payments | Opcional | dev, staging, prod | secret | Stripe secret key (sk_live o sk_test) | `sk_live_abc123...` |
| `STRIPE_PRICE_ID` | Sales Agent Payments | Opcional | dev, staging, prod | config | Stripe Price ID para checkout sessions | `price_1ABC123...` |
| `STRIPE_SUCCESS_URL` | Sales Agent Payments | Opcional | dev, staging, prod | config | URL de redirección tras pago exitoso | `https://dania.agency/gracias` |
| `STRIPE_CANCEL_URL` | Sales Agent Payments | Opcional | dev, staging, prod | config | URL de redirección si se cancela el pago | `https://dania.agency/cancelado` |

### Cal.com (Booking/Scheduling)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `CALCOM_BOOKING_LINK` | Sales Agent Booking | Opcional | dev, staging, prod | config | Cal.com booking link para leads cualificados | `https://cal.com/dania-agency/consulta-gratuita` |

---

## 🔹 Social Autopilots / Ayrshare

Deploy de contenido a redes sociales (Twitter, Facebook, Instagram) vía Ayrshare.

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `AYRSHARE_API_KEY` | Social Deploy | Obligatoria* | staging, prod | secret | Ayrshare API key | `ayr_abc123...` |
| `AYRSHARE_BASE_URL` | Social Deploy | Opcional | staging, prod | config | Ayrshare API base URL | `https://app.ayrshare.com/api` |
| `ENABLE_AYRSHARE_SOCIAL` | Social Deploy | Opcional | staging, prod | config | Feature flag para habilitar deploy social | `true` |

*Obligatoria solo si se habilita deploy social (`ENABLE_AYRSHARE_SOCIAL=true`).

---

## 🔹 Telegram Deploy

Deploy de autopilots a Telegram Bot API.

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram Deploy | Obligatoria* | staging, prod | secret | Telegram Bot API token (obtener de @BotFather) | `123456:ABC-DEF1234gh...` |
| `TELEGRAM_BASE_URL` | Telegram Deploy | Opcional | staging, prod | config | Telegram Bot API base URL | `https://api.telegram.org` |
| `DEFAULT_TELEGRAM_CHAT_ID` | Telegram Deploy | Opcional | staging, prod | config | Chat ID por defecto (fallback global) | `123456789` o `@channel_username` |
| `ENABLE_TELEGRAM_DEPLOY` | Telegram Deploy | Opcional | staging, prod | config | Feature flag para habilitar deploy Telegram | `true` |

*Obligatoria solo si se habilita deploy Telegram (`ENABLE_TELEGRAM_DEPLOY=true`).

**Multi-tenant chat_id fallback:**
1. `deliverable_metadata.telegram_chat_id` (per-order)
2. `tenant.settings.telegram_chat_id` (per-tenant)
3. `DEFAULT_TELEGRAM_CHAT_ID` (global fallback)

---

## 🔹 Servicios Externos

### Axon Core Integration

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `AXON_CORE_API_BASE` | Axon Core | Opcional | dev, staging, prod | config | URL base del API de Axon Core | `https://axon-core.example.com` |
| `AXON_CORE_API_TOKEN` | Axon Core | Opcional | dev, staging, prod | secret | Token de autenticación para Axon Core | `axc_abc123...` |
| `AXON_CORE_ENABLED` | Axon Core | Opcional | dev, staging, prod | config | Habilita integración con Axon Core | `true` |

### n8n (Workflow Automation)

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `N8N_BASE_URL` | n8n Integration | Opcional | dev, staging, prod | config | URL base del servidor n8n | `http://127.0.0.1:5679` |
| `N8N_API_KEY` | n8n Integration | Opcional | dev, staging, prod | secret | n8n API key para autenticación | `n8n_abc123...` |

---

## 🔹 Frontend (Next.js)

Variables de entorno del frontend web (Next.js).

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | API Proxy | Obligatoria | dev, staging, prod | config | URL del backend API (accesible desde navegador) | `http://localhost:8080` (dev), `https://api.axon.agency` (prod) |
| `NEXT_PUBLIC_REPLIT_STUDIO_URL` | Replit Studio Embed | Opcional | staging, prod | config | URL del Replit Studio embebido | `https://replit.com/@user/project` |

---

## 🔹 Autonomous Agent System

Sistema de agentes autónomos para mejora de código.

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `AUTONOMOUS_AGENT_ARCHITECT_ENABLED` | Architect Agent | Opcional | dev, staging, prod | config | Habilita Architect Supervisor agent | `true` |
| `AUTONOMOUS_AGENT_REVIEW_COUNCIL_ENABLED` | Review Council | Opcional | dev, staging, prod | config | Habilita Review Council multi-agent | `true` |

---

## 🔹 JWT Authentication

Configuración de autenticación JWT.

| Nombre | Módulo/Feature | Obligatoria | Entornos | Tipo | Descripción | Ejemplo |
|--------|---------------|-------------|----------|------|-------------|---------|
| `JWT_SECRET` | Auth | Obligatoria | dev, staging, prod | secret | Secret para firmar tokens JWT (CAMBIAR en producción) | `change-me-in-production` |
| `JWT_ISS` | Auth | Opcional | dev, staging, prod | config | Issuer del token JWT | `axon` |
| `JWT_AUD` | Auth | Opcional | dev, staging, prod | config | Audience del token JWT | `control` |
| `JWT_EXPIRATION_MINUTES` | Auth | Opcional | dev, staging, prod | config | Tiempo de expiración del token en minutos | `1440` (24 horas) |

---

## 📊 Resumen por Criticidad

### 🔴 CRÍTICAS (Sistema no funciona sin estas)

**Producción:**
- `OPENAI_API_KEY` - LLM core functionality
- `DATABASE_URL` - Persistencia de datos
- `JWT_SECRET` - Autenticación (cambiar default en prod)
- `NEXT_PUBLIC_BACKEND_URL` - Comunicación frontend-backend

**Por Feature (cuando se activa):**
- `MONGODB_URI` - Si se usa WhatsApp Sales Agent
- `N8N_WHATSAPP_DEPLOY_WEBHOOK_URL` - Si se usa deploy WhatsApp clásico
- `AYRSHARE_API_KEY` - Si se usa deploy social
- `TELEGRAM_BOT_TOKEN` - Si se usa deploy Telegram

### 🟡 IMPORTANTES (Funcionalidad reducida sin estas)

- `GEMINI_API_KEY` - Fallback LLM provider
- `REDIS_URL` - Jobs y cache (degrada a in-memory)
- `N8N_API_KEY` - Integración workflows

### 🟢 OPCIONALES (Mejoran experiencia)

- `MELVIS_API_KEY` - RAG para Sales Agent
- `TAVILY_API_KEY` - Web search para Sales Agent
- `LINKEDIN_API_KEY` - Lead enrichment
- `STRIPE_SECRET_KEY` - Payments
- `CALCOM_BOOKING_LINK` - Booking
- `OLLAMA_ENABLED` - LLM local (dev)
- `AXON_CORE_*` - Integración Axon Core
- `EMBEDDING_MODEL` - Modelo de embeddings (usa default si no se configura)

---

## 🎯 Variables Mínimas por Escenario

Esta sección define las **configuraciones mínimas** necesarias para probar funcionalidades específicas sin configurar todo el sistema.

### ✅ Escenario 1: Login Real (Auth + Cookies)

**Objetivo:** Probar autenticación JWT sin base de datos real ni integraciones.

**Variables requeridas:**
```bash
# Backend
JWT_SECRET=dev-secret-key-change-me-in-production
DEV_MODE=true
ALLOWED_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

**Qué funciona:**
- ✅ Login/logout con JWT tokens
- ✅ Cookies y sesiones
- ✅ Bypass de autenticación en endpoints protegidos (DEV_MODE)

**Qué NO funciona:**
- ❌ Persistencia de usuarios en DB (DEV_MODE usa usuarios mock)
- ❌ Integraciones externas (LLM, WhatsApp, etc.)

**Prueba rápida:**
```bash
# Test manual
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Debe retornar: {"access_token": "eyJ..."}
```

---

### ✅ Escenario 2: WhatsApp Sales Agent (datos reales en MongoDB)

**Objetivo:** Probar el template Full IntegraIA con 7 integraciones externas.

**Variables OBLIGATORIAS:**
```bash
# Core
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE  # ⚠️ API key REAL requerida
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=whatsapp_sales_dev
DEV_MODE=false  # Desactivar para usar MongoDB real
DATABASE_URL=postgresql+psycopg://axon:axon@localhost:5432/axon
JWT_SECRET=dev-secret-123
ALLOWED_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

**Variables OPCIONALES (mejoran funcionalidad):**
```bash
# RAG / Knowledge Base
MELVIS_API_URL=https://melvis.example.com/api
MELVIS_API_KEY=mlv-your-key
MELVIS_COLLECTION=kb_sales

# Web Search
TAVILY_API_KEY=tvly-your-key

# Lead Enrichment
LINKEDIN_API_KEY=lin-your-key
LINKEDIN_BASE_URL=https://api.linkedin.com/v2

# Payments
STRIPE_SECRET_KEY=sk_test_your-key
STRIPE_PRICE_ID=price_1ABC123
STRIPE_SUCCESS_URL=https://example.com/success
STRIPE_CANCEL_URL=https://example.com/cancel

# Scheduling
CALCOM_BOOKING_LINK=https://cal.com/your-link/meeting
```

**Qué funciona con SOLO las obligatorias:**
- ✅ Webhook WhatsApp recibe mensajes
- ✅ MongoDB persiste users, messages, leads, sessions
- ✅ OpenAI clasifica intent y genera respuestas
- ✅ Conversación multiturno con estado (session tracking)
- ⚠️ RAG/search/enrichment/payments/booking NO funcionan (se omiten gracefully)

**Qué funciona con TODAS (obligatorias + opcionales):**
- ✅ Todo lo anterior +
- ✅ RAG semántico con Melvis (conocimiento empresarial)
- ✅ Web search con Tavily (contexto real-time)
- ✅ Enriquecimiento LinkedIn (datos profesionales)
- ✅ Checkout Stripe (pagos)
- ✅ Booking Cal.com (agendamiento)

**Prueba rápida (webhook simulation):**
```bash
# Simular webhook WhatsApp entrante
curl -X POST http://localhost:8080/api/whatsapp/webhook/sales-agent \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+5491112345678",
    "message": "Hola, quiero información sobre automatización con IA"
  }'

# Verificar en MongoDB:
# - Colección users: debe tener nuevo usuario con phone
# - Colección messages: debe tener mensaje "in" y respuesta "out"
# - Colección sessions: debe tener sesión con current_step
```

---

### ✅ Escenario 3: Health Dashboard (sin romper nada)

**Objetivo:** Ver dashboard de integraciones sin configurar API keys reales.

**Variables requeridas:**
```bash
# Backend
DEV_MODE=true  # Bypass autenticación
DATABASE_URL=sqlite:///./axon.db  # DB local simple
ALLOWED_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

**Qué funciona:**
- ✅ GET /api/integrations/health → retorna status de todas las integraciones
- ✅ Dashboard UI muestra tabla de integraciones con badges (enabled/disabled)
- ✅ Integraciones sin API key aparecen como "disabled" (graceful degradation)

**Qué se ve en el dashboard:**
- 🟢 OpenAI: disabled (OPENAI_API_KEY no configurada)
- 🟢 Gemini: disabled (GEMINI_API_KEY no configurada)
- 🟢 Ayrshare: disabled (AYRSHARE_API_KEY no configurada)
- 🟢 Telegram: disabled (TELEGRAM_BOT_TOKEN no configurada)
- 🟢 MongoDB: disabled (MONGODB_URI no configurada)
- 🟢 Stripe: disabled (STRIPE_SECRET_KEY no configurada)
- etc.

**Prueba rápida:**
```bash
curl http://localhost:8080/api/integrations/health

# Debe retornar:
# {
#   "overall_status": "degraded",
#   "integrations": [
#     {"name": "openai", "enabled": false, "reason": "API key not configured"},
#     {"name": "gemini", "enabled": false, "reason": "API key not configured"},
#     ...
#   ]
# }
```

---

### ✅ Escenario 4: Deploy Social Autopilot (Ayrshare)

**Objetivo:** Publicar contenido en redes sociales (Twitter, Facebook, Instagram).

**Variables OBLIGATORIAS:**
```bash
# Core
OPENAI_API_KEY=sk-proj-YOUR-KEY  # Para generar contenido IA
DATABASE_URL=postgresql+psycopg://axon:axon@localhost:5432/axon
JWT_SECRET=dev-secret-123
DEV_MODE=false
ALLOWED_ORIGINS=http://localhost:3000

# Social Deploy
AYRSHARE_API_KEY=ayr-YOUR-KEY-HERE  # ⚠️ Ayrshare API key REAL
AYRSHARE_BASE_URL=https://app.ayrshare.com/api
ENABLE_AYRSHARE_SOCIAL=true  # ⚠️ Feature flag ON

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

**Qué funciona:**
- ✅ POST /api/autopilots/deploy → opción "social" disponible
- ✅ Deploy a Twitter, Facebook, Instagram simultáneamente
- ✅ Scheduling de posts (fecha/hora programada)
- ✅ Multi-imagen support (hasta 10 imágenes por post)
- ✅ Rate limit tracking (Ayrshare 300 req/5min)

**Prueba rápida:**
```bash
curl -X POST http://localhost:8080/api/autopilots/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "autopilot_id": 123,
    "channel": "social",
    "platforms": ["twitter", "facebook"],
    "media_urls": ["https://example.com/image.jpg"]
  }'

# Debe retornar:
# {
#   "status": "success",
#   "ayrshare_post_id": "ayr-abc123",
#   "platform_ids": {"twitter": "123", "facebook": "456"}
# }
```

---

### ✅ Escenario 5: Deploy Telegram Autopilot

**Objetivo:** Enviar autopilots a chat/canal de Telegram.

**Variables OBLIGATORIAS:**
```bash
# Core
DATABASE_URL=postgresql+psycopg://axon:axon@localhost:5432/axon
JWT_SECRET=dev-secret-123
DEV_MODE=false
ALLOWED_ORIGINS=http://localhost:3000

# Telegram Deploy
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIJKL  # ⚠️ Bot token REAL de @BotFather
TELEGRAM_BASE_URL=https://api.telegram.org
ENABLE_TELEGRAM_DEPLOY=true  # ⚠️ Feature flag ON

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

**Variables OPCIONALES:**
```bash
# Fallback global (si order no tiene telegram_chat_id)
DEFAULT_TELEGRAM_CHAT_ID=123456789  # o @channel_username
```

**Qué funciona:**
- ✅ POST /api/autopilots/deploy → opción "telegram" disponible
- ✅ Envío a user, group o channel
- ✅ Texto + foto (sendPhoto)
- ✅ Texto + múltiples fotos (sendMediaGroup)
- ✅ Fallback multi-tenant: order.telegram_chat_id → tenant.telegram_chat_id → DEFAULT_TELEGRAM_CHAT_ID

**Prueba rápida:**
```bash
# Obtener tu chat_id: envia /start a tu bot y mira updates
curl https://api.telegram.org/bot<TOKEN>/getUpdates

# Deploy autopilot
curl -X POST http://localhost:8080/api/autopilots/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "autopilot_id": 123,
    "channel": "telegram",
    "deliverable_metadata": {
      "telegram_chat_id": "123456789"
    }
  }'

# Debe retornar:
# {
#   "status": "success",
#   "telegram_message_id": 789,
#   "chat_id": "123456789"
# }
```

---

## 🚀 Setup Rápido por Entorno

### Desarrollo Local (Mínimo)

```bash
# Core
DATABASE_URL=postgresql+psycopg://axon:axon@localhost:5432/axon
OPENAI_API_KEY=sk-proj-...
DEV_MODE=true
ALLOWED_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

### Staging (Recomendado)

Agregar a desarrollo local:
```bash
# Producción mode
PRODUCTION_MODE=false
DEV_MODE=false
JWT_SECRET=<generar-nuevo-secret>

# MongoDB (si usas Sales Agent)
MONGODB_URI=mongodb+srv://...
MONGODB_DB_NAME=whatsapp_sales_staging

# Gemini fallback
GEMINI_API_KEY=AIzaSy...

# Redis
REDIS_URL=redis://...
```

### Producción (Completo)

Staging + todas las integraciones que necesites activar:
```bash
# Deploy channels
N8N_WHATSAPP_DEPLOY_WEBHOOK_URL=https://...
AYRSHARE_API_KEY=ayr_...
ENABLE_AYRSHARE_SOCIAL=true
TELEGRAM_BOT_TOKEN=123456:ABC...
ENABLE_TELEGRAM_DEPLOY=true

# Sales Agent integraciones
MELVIS_API_KEY=mlv_...
TAVILY_API_KEY=tvly_...
LINKEDIN_API_KEY=lin_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PRICE_ID=price_...
CALCOM_BOOKING_LINK=https://cal.com/...

# Frontend
NEXT_PUBLIC_BACKEND_URL=https://api.axon.agency
NEXT_PUBLIC_REPLIT_STUDIO_URL=https://replit.com/...
```

---

## ⚠️ Notas de Seguridad

1. **NUNCA** commitear valores reales de secrets al repositorio
2. Usar `.env` local para desarrollo (git-ignored)
3. Usar secrets management de Replit/hosting para staging/prod
4. Rotar `JWT_SECRET` en producción (nunca usar el default)
5. `DEV_MODE=true` desactiva autenticación - **SOLO** desarrollo
6. API keys truncadas en logs (primeros 15 chars + "...")
7. MongoDB URI truncada en logs (primeros 20 chars + "...")

---

## 📝 Checklist de Configuración

Antes de deploy a producción, verificar:

- [ ] `JWT_SECRET` cambiado del default
- [ ] `DEV_MODE=false` (CRÍTICO - desactiva auth bypass)
- [ ] `PRODUCTION_MODE=true`
- [ ] `DATABASE_URL` apunta a PostgreSQL de producción
- [ ] `OPENAI_API_KEY` configurada (obligatoria)
- [ ] `ALLOWED_ORIGINS` lista correcta de dominios frontend
- [ ] `NEXT_PUBLIC_BACKEND_URL` apunta a URL pública del API
- [ ] MongoDB configurado si se usa Sales Agent
- [ ] Webhooks n8n configurados si se usa deploy WhatsApp
- [ ] Ayrshare key si se usa deploy social
- [ ] Telegram bot token si se usa deploy Telegram
- [ ] Stripe keys en modo live (no test)
- [ ] Todos los secrets en secrets manager (NO en .env)

---

**Generado:** 17 de noviembre de 2025  
**Versión:** 1.0.0  
**Contacto:** Federico (Axon Agency)
