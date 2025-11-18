# AXON Agency - Guía Rápida de Integración

## ✅ Estado Actual

**Tests de Integración:** 3/6 PASSING (configuración correcta)

- ✅ Local Health - Backend Replit funcionando  
- ✅ Dev Token - Autenticación JWT OK
- ✅ Local Catalog - Endpoints locales OK
- ⏳ Axon Core Direct - Esperando túnel Cloudflare
- ⏳ Axon Core Proxy - Esperando túnel Cloudflare  
- ⏳ Axon Core Catalog - Esperando túnel Cloudflare

## 🚀 Activar Integración Completa

### 1️⃣ En Axon 88 (tu máquina local)

```bash
# Inicia el túnel de Cloudflare
cloudflared tunnel --url localhost:8080
```

Esto expondrá tu Axon Core API a través de un túnel seguro.

### 2️⃣ En Replit (automático)

```bash
cd axon-agency
make setup-axon-core
```

Este comando:
- Verifica conectividad con Axon Core
- Obtiene el token JWT automáticamente  
- Actualiza las variables de entorno
- Te confirma que todo está listo

### 3️⃣ Verificar Integración

```bash
make integration
```

**Resultado esperado:** 6/6 PASSING ✅

### 4️⃣ Prueba Manual

```bash
# Health check de Axon Core
curl -s https://api-axon88.algorithmicsai.com/api/health

# Chat con IA (requiere token)
export AXON_TOKEN=$(curl -s -X POST https://api-axon88.algorithmicsai.com/api/auth/dev/token | jq -r .access_token)

curl -s -X POST https://api-axon88.algorithmicsai.com/api/agent/chat \
  -H "Authorization: Bearer $AXON_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hola, ¿me escuchas?", "session_id":"smoke"}'
```

## 📡 Arquitectura

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Usuario Web    │         │  Axon Agency    │         │   Axon Core     │
│  (Browser)      │◄───────►│   (Replit)      │◄───────►│  (Axon 88)      │
│                 │         │                 │         │                 │
│  Port 5000      │         │  Backend: 8080  │  Túnel  │  Port 8080      │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                     │                           │
                                     │                           ▼
                                     │                  ┌─────────────────┐
                                     │                  │     OpenAI      │
                                     │                  │   API (Cloud)   │
                                     │                  └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  PostgreSQL     │
                            │  (SQLite local) │
                            └─────────────────┘
```

## 🔗 Endpoints Disponibles

### Backend Local (Replit)

```bash
GET  /api/health          # Health check
GET  /api/catalog         # Capacidades del sistema
POST /api/auth/dev/token  # Obtener token JWT
POST /api/agent/chat      # Chat con IA
GET  /api/metrics         # Métricas del sistema
```

### Proxy Axon Core (vía Replit)

```bash
GET  /api/axon-core/health      # Verificar conectividad con Axon Core
GET  /api/axon-core/catalog     # Obtener catálogo de Axon Core
POST /api/axon-core/chat        # Chat con LLM vía Axon Core
POST /api/axon-core/command     # Ejecutar comando en Axon 88
GET  /api/axon-core/services    # Listar servicios (systemd/Docker)
GET  /api/axon-core/metrics     # Métricas de Axon 88
POST /api/axon-core/workflow    # Disparar workflow n8n
```

## 🤖 Funcionalidades

Cuando el túnel esté activo:

- **Chat AI con OpenAI** - Tu frontend → Replit → Axon Core → OpenAI
- **Control Remoto** - Gestiona servicios de Axon 88 desde la UI
- **Comandos Seguros** - Terminal remoto con whitelist
- **Métricas en Vivo** - CPU, RAM, GPU de Axon 88 en tiempo real
- **Workflows n8n** - Dispara automatizaciones desde la interfaz
- **Autopilots** - Agentes IA con acceso a tu infraestructura

## 📝 Comandos Útiles

```bash
# Ver estado
make integration

# Configurar Axon Core (cuando túnel esté activo)
make setup-axon-core

# Ver logs
tail -f logs/integration.log

# Reiniciar servicios
make backend
make frontend

# Limpiar
make clean
```

## 🐛 Troubleshooting

### "Cannot connect to Axon Core"

**Causa:** Túnel de Cloudflare no activo

**Solución:**
```bash
# En Axon 88
cloudflared tunnel --url localhost:8080
```

### "503 Service Unavailable"

**Causa:** Axon Core API no está corriendo

**Solución:**
```bash
# En Axon 88
cd /path/to/axon-core
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080
```

### "401 Unauthorized"

**Causa:** Token expirado o inválido

**Solución:**
```bash
# En Replit
make setup-axon-core
```

## 📚 Documentación Completa

- `README.md` (9.3K) - Guía general del proyecto
- `INTEGRATION.md` (8.7K) - Detalles técnicos de integración
- `INTEGRATION_STATUS.txt` - Estado actual del sistema
- `Makefile` - Comandos de desarrollo

## 🎯 Siguiente Paso

**Activa el túnel de Cloudflare en Axon 88 y ejecuta `make setup-axon-core` en Replit.**

Todo funcionará automáticamente. 🚀
