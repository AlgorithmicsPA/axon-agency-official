# AXON Agency - Plataforma IA Full-Stack

Monorepo completo de una Agencia IA capaz de CREAR y OPERAR activos de inteligencia artificial: páginas, agentes, autopilotos, campañas, publicaciones, medios, RAG, analíticas, y conexiones (WhatsApp/Telegram).

## 📋 Estructura del Proyecto

```
axon-agency/
├── apps/
│   ├── api/          # Backend FastAPI + Python 3.11
│   └── web/          # Frontend Next.js 15
├── packages/
│   └── shared/       # Tipos y esquemas compartidos
├── Makefile          # Scripts de desarrollo
└── README.md         # Este archivo
```

## 🚀 Inicio Rápido

### Requisitos
- Python 3.11+
- Node.js 18+
- SQLite (incluido por defecto)

### Instalación

```bash
# Instalar dependencias del backend
cd apps/api && pip install -r requirements.txt

# Instalar dependencias del frontend
cd apps/web && npm install
```

### Configuración

#### Backend (`apps/api/.env`)
```env
BIND=0.0.0.0
PORT=8080
DATABASE_URL=sqlite:///./axon.db
JWT_SECRET=changeme-dev-only
DEV_MODE=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5001

# OpenAI (opcional)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

#### Frontend (`apps/web/.env.local`)
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

### Ejecución

```bash
# Backend (puerto 8080)
cd apps/api
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080

# Frontend (puerto 5001)
cd apps/web
npm run dev
```

O usar el Makefile:
```bash
make dev
```

## ✅ Estado del Sistema

### Backend API ✅
- **Puerto:** 8080
- **WebSocket:** Soportado
- **Base de Datos:** SQLite (axon.db)
- **Auth:** JWT con modo desarrollo
- **Estado:** RUNNING

### Frontend Web ✅
- **Puerto:** 5001
- **Framework:** Next.js 15 + TypeScript
- **UI:** Tailwind CSS + shadcn/ui
- **Estado:** RUNNING

## 📡 API Endpoints

### Health & System
```bash
# Health check
curl http://localhost:8080/api/health

# System catalog
curl http://localhost:8080/api/catalog

# System metrics (requiere auth)
curl -H "Authorization: Bearer <token>" http://localhost:8080/api/metrics
```

### Authentication
```bash
# Obtener token de desarrollo
curl -X POST http://localhost:8080/api/auth/dev/token

# Registrar usuario
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "usuario",
    "password": "password123",
    "full_name": "Usuario Ejemplo"
  }'

# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "password123"
  }'
```

### Agent Chat
```bash
# Chat con IA (requiere OPENAI_API_KEY)
curl -X POST http://localhost:8080/api/agent/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hola, ¿cómo estás?",
    "session_id": "session-123"
  }'
```

### Posts & Content
```bash
# Crear borrador
curl -X POST http://localhost:8080/api/posts/draft \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Mi Primera Landing",
    "brief": "Una página sobre IA"
  }'

# Listar posts
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/posts/list

# Publicar post
curl -X POST http://localhost:8080/api/posts/publish/mi-primera-landing \
  -H "Authorization: Bearer <token>"
```

### Media Upload
```bash
# Subir archivo
curl -X POST http://localhost:8080/api/media/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/image.jpg"

# Listar media
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/media/list

# Eliminar media
curl -X DELETE http://localhost:8080/api/media/1 \
  -H "Authorization: Bearer <token>"
```

### Campaigns
```bash
# Crear campaña
curl -X POST http://localhost:8080/api/campaigns/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Campaña de Navidad",
    "goal": "Aumentar ventas 30%",
    "config": {"channels": ["email", "whatsapp"]}
  }'

# Listar campañas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/campaigns/list

# Ver estado de campaña
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/campaigns/1/status
```

### Autopilots
```bash
# Listar autopilots
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/autopilots/list

# Disparar autopilot
curl -X POST http://localhost:8080/api/autopilots/trigger \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "content-generator",
    "payload": {"topic": "IA en 2025"}
  }'
```

### RAG (Conocimiento)
```bash
# Subir documento
curl -X POST http://localhost:8080/api/rag/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf"

# Listar fuentes
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/rag/list

# Consultar RAG
curl -X POST http://localhost:8080/api/rag/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué dice el documento sobre IA?",
    "top_k": 5
  }'
```

### Integrations
```bash
# WhatsApp status
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/integrations/whatsapp/status

# Telegram status
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/integrations/telegram/status
```

### Conversations
```bash
# Listar conversaciones
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/conversations/list

# Filtrar por sesión
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/conversations/list?session_id=session-123"
```

## 🎨 Frontend Pages

El frontend incluye 18 páginas principales:

1. **/** - Dashboard con métricas del sistema
2. **/agent** - Super Axon Agent (chat + micrófono + TTS)
3. **/campaigns** - Gestión de campañas
4. **/posts** - Publicaciones y landing pages
5. **/media** - Galería de medios
6. **/conversations** - Historial de conversaciones
7. **/whatsapp** - Configuración WhatsApp
8. **/telegram** - Configuración Telegram
9. **/comments** - Comentarios y feedback
10. **/autopilots** - Autopilots IA
11. **/memberships** - Gestión de membresías
12. **/partners** - Asociados
13. **/team** - Mi equipo
14. **/rag** - Conocimiento RAG
15. **/networks** - Redes conectadas
16. **/settings** - Configuración
17. **/analytics** - Analíticas
18. **/profile** - Mi perfil

## 🔒 Seguridad

### Modo Desarrollo
- `DEV_MODE=true` habilita endpoint `/api/auth/dev/token`
- JWT_SECRET usa valor por defecto
- Warnings visibles en logs

### Modo Producción
```env
PRODUCTION_MODE=true
DEV_MODE=false
JWT_SECRET=<secreto-seguro-aleatorio>
```

⚠️ El sistema **NO ARRANCARÁ** en producción si:
- JWT_SECRET es el valor por defecto
- DEV_MODE está habilitado

## 🗄️ Base de Datos

### Modelos
- **User** - Usuarios del sistema
- **Team** - Equipos/organizaciones
- **Partner** - Socios comerciales
- **Membership** - Suscripciones
- **Campaign** - Campañas de marketing
- **Post** - Contenido/landing pages
- **Media** - Archivos multimedia
- **Conversation** - Historial de chat
- **Autopilot** - Agentes automatizados
- **RagSource** - Fuentes de conocimiento
- **AnalyticsEvent** - Eventos de analítica
- **Comment** - Comentarios de usuarios

### SQLite
La base de datos se crea automáticamente en `apps/api/axon.db`

## 🌐 WebSocket

Conectar al WebSocket para chat en tiempo real:

```javascript
import { io } from "socket.io-client";

const socket = io("http://localhost:8080", {
  auth: { token: "your-jwt-token" }
});

// Enviar mensaje
socket.emit("chat:user", {
  text: "Hola",
  session_id: "session-123"
});

// Recibir respuesta
socket.on("chat:assistant", (data) => {
  console.log("Assistant:", data.text);
});
```

## 📊 Características

### ✅ Implementado
- [x] API REST completa con FastAPI
- [x] WebSocket para chat en tiempo real
- [x] Autenticación JWT con roles
- [x] CRUD de posts, media, campaigns
- [x] OpenAI integration
- [x] Frontend Next.js 15 con 18 páginas
- [x] UI Dark theme con Tailwind + shadcn/ui
- [x] SQLite database
- [x] CORS configurado
- [x] Modo desarrollo y producción
- [x] Webhooks WhatsApp/Telegram (stubs)
- [x] RAG básico
- [x] Autopilots registry
- [x] Analytics events
- [x] Static file serving

### 🚧 Pendiente (extensiones futuras)
- [ ] Redis para colas y jobs
- [ ] n8n workflows activos
- [ ] Embeddings para RAG
- [ ] Tool calling en agente IA
- [ ] Tests automatizados
- [ ] Docker compose
- [ ] Alembic migrations
- [ ] Producción deployment

## 🛠️ Desarrollo

```bash
# Linter
make lint

# Tests
make test

# Build frontend
make build

# Limpiar
make clean
```

## 📝 Notas

- El frontend conecta al backend en `http://localhost:8080`
- Puerto 5001 para web (configurable en package.json)
- CORS permite localhost:3000 y localhost:5001
- OpenAI API key es opcional (fallback a stub)
- Redis es opcional (sin jobs background por ahora)

## 🎯 Próximos Pasos

1. Configurar OPENAI_API_KEY para habilitar chat real
2. Implementar jobs con Redis/RQ
3. Conectar n8n workflows
4. Agregar embeddings para RAG
5. Implementar tool calling
6. Dockerizar aplicación
7. Configurar CI/CD

## 📄 Licencia

Proyecto interno - Todos los derechos reservados

---

**AXON Agency** - Plataforma IA completa para crear y operar activos de inteligencia artificial.
