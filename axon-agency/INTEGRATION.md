# Integración Axon Agency ↔ Axon Core ↔ OpenAI

Este documento describe la arquitectura de integración completa entre Axon Agency (Replit), Axon Core (Axon 88 local), y OpenAI.

## 🏗️ Arquitectura

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Axon Agency    │         │   Axon Core     │         │     OpenAI      │
│   (Replit)      │◄───────►│  (Axon 88)      │◄───────►│  API (Cloud)    │
│                 │         │                 │         │                 │
│  - Frontend     │         │  - LLM Provider │         │  - GPT Models   │
│  - Backend API  │         │  - n8n Flows    │         │  - Vision API   │
│  - SQLite DB    │         │  - PostgreSQL   │         │                 │
│  - WebSocket    │         │  - Services     │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │                           │
        │     Cloudflare Tunnel     │
        └───────────────────────────┘
```

## 🔌 Componentes de Integración

### 1. Adaptador Axon Core (`apps/api/app/adapters/axon_core.py`)

Cliente HTTP asíncrono que se comunica con Axon Core:

**Métodos disponibles:**
- `health_check()` - Verifica conectividad
- `get_catalog()` - Obtiene capacidades del sistema
- `chat(text, session_id)` - Chat con LLM
- `execute_command(cmd, args)` - Ejecuta comandos
- `list_services()` - Lista servicios systemd/Docker
- `get_metrics()` - Obtiene métricas del sistema
- `trigger_workflow(id, payload)` - Dispara workflows n8n

### 2. Router Proxy (`apps/api/app/routers/axon_core.py`)

Endpoints API que reenvían peticiones a Axon Core:

```bash
GET  /api/axon-core/health      # Verificar conectividad
GET  /api/axon-core/catalog     # Obtener catalog
POST /api/axon-core/chat        # Chat con LLM
POST /api/axon-core/command     # Ejecutar comando (admin)
GET  /api/axon-core/services    # Listar servicios
GET  /api/axon-core/metrics     # Métricas del sistema
POST /api/axon-core/workflow    # Disparar workflow
```

### 3. Cloudflare Tunnel

Túnel seguro que expone Axon Core (local) a Internet:

```bash
# En Axon 88
cloudflared tunnel --url localhost:8080
```

URL actual: `https://api-axon88.algorithmicsai.com`

## 🚀 Setup de Integración

### Paso 1: Iniciar Túnel (en Axon 88)

```bash
# Opción A: Túnel temporal
cloudflared tunnel --url localhost:8080

# Opción B: Túnel permanente (recomendado para producción)
cloudflared tunnel create axon-core
cloudflared tunnel route dns axon-core axon.tu-dominio.com
cloudflared tunnel run axon-core
```

### Paso 2: Configurar Variables de Entorno

#### En Replit (`apps/api/.env`)

```env
AXON_CORE_API_BASE=https://api-axon88.algorithmicsai.com
AXON_CORE_API_TOKEN=<obtener-del-script>
AXON_CORE_ENABLED=true
```

#### En Replit (`apps/web/.env.local`)

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
NEXT_PUBLIC_AXON_CORE_URL=https://api-axon88.algorithmicsai.com
```

### Paso 3: Obtener Token de Axon Core

**Opción A: Automático**
```bash
cd axon-agency
chmod +x scripts/setup_axon_core.sh
./scripts/setup_axon_core.sh
```

**Opción B: Manual**
```bash
# Obtener token
TOKEN=$(curl -s -X POST https://api-axon88.algorithmicsai.com/api/auth/dev/token | jq -r .access_token)

# Actualizar .env
echo "AXON_CORE_API_TOKEN=$TOKEN" >> apps/api/.env
```

### Paso 4: Reiniciar Servicios

```bash
# En Replit
make restart

# O manualmente
cd apps/api && uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080
```

### Paso 5: Verificar Integración

```bash
# Ejecutar pruebas de integración
python scripts/test_integration.py
```

Resultado esperado:
```
✅ Integración completa Axon Core ↔ Replit ↔ OpenAI
🌐 Axon Core URL: https://api-axon88.algorithmicsai.com
🤖 Chat AI funcionando
📡 Comunicación WebSocket activa
📦 Autopilots y landings listos
```

## 📊 Tests de Integración

El script `test_integration.py` ejecuta 6 pruebas:

1. **Local Health** - Backend de Replit funcional
2. **Dev Token** - Autenticación funcionando
3. **Local Catalog** - Endpoints locales OK
4. **Axon Core Direct** - Conectividad directa con Axon Core
5. **Axon Core Proxy** - Proxy a través del backend
6. **Axon Core Catalog** - Obtener capacidades de Axon Core

### Estado Actual

```
✅ PASS: Local Health
✅ PASS: Dev Token
✅ PASS: Local Catalog
❌ FAIL: Axon Core Direct     (esperando túnel activo)
❌ FAIL: Axon Core Proxy      (esperando túnel activo)
❌ FAIL: Axon Core Catalog    (esperando túnel activo)
```

Los 3 tests locales pasan correctamente. Los tests de Axon Core pasarán automáticamente cuando el túnel esté activo.

## 🔄 Flujo de Datos

### Chat con IA

```
Usuario (Frontend)
    ↓ WebSocket
Backend (Replit)
    ↓ HTTP POST /api/axon-core/chat
Axon Core (Axon 88)
    ↓ HTTP POST /api/llm/openai
OpenAI API
    ↓ Streaming response
Axon Core
    ↓ JSON response
Backend (Replit)
    ↓ WebSocket emit
Usuario (Frontend)
```

### Ejecución de Comandos

```
Usuario (Frontend, Admin)
    ↓ HTTP POST /api/axon-core/command
Backend (Replit)
    ↓ Valida role = admin
    ↓ HTTP POST con JWT token
Axon Core
    ↓ Verifica comando en whitelist
    ↓ Ejecuta via subprocess
    ↓ Retorna stdout/stderr
Backend
    ↓ JSON response
Usuario
```

### Workflows n8n

```
Usuario (Frontend)
    ↓ POST /api/axon-core/workflow
Backend (Replit)
    ↓ POST /api/flows/trigger/{id}
Axon Core
    ↓ POST webhook a n8n
n8n
    ↓ Ejecuta workflow
    ↓ Retorna resultado
Usuario
```

## 🔒 Seguridad

### Autenticación

1. **Replit → Usuario**: JWT tokens propios
2. **Replit → Axon Core**: JWT token de Axon Core
3. **Axon Core → OpenAI**: API Key en .env

### Consideraciones

- **Dev Mode**: Habilitado en desarrollo, endpoints `/dev/token`
- **Production Mode**: Requiere JWT_SECRET seguro, deshabilita dev endpoints
- **CORS**: Configurado para localhost y dominios de producción
- **Rate Limiting**: TODO - implementar para producción

## 🐛 Troubleshooting

### Error: "Cannot connect to Axon Core"

**Causa**: Túnel de Cloudflare no está activo

**Solución**:
```bash
# En Axon 88
cloudflared tunnel --url localhost:8080
```

### Error: "503 Service Unavailable"

**Causa**: Axon Core API no está corriendo

**Solución**:
```bash
# En Axon 88
cd /path/to/axon-core
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080
```

### Error: "401 Unauthorized"

**Causa**: Token expirado o inválido

**Solución**:
```bash
# Regenerar token
./scripts/setup_axon_core.sh
```

### Error: "Name or service not known"

**Causa**: URL del túnel incorrecta o DNS no resuelve

**Solución**:
1. Verificar URL del túnel en cloudflared logs
2. Actualizar `AXON_CORE_API_BASE` en .env
3. Verificar conectividad: `curl https://tu-url.trycloudflare.com/api/health`

## 📝 Logs

Los logs de integración se guardan en:

```bash
axon-agency/logs/integration.log
```

Para ver logs en tiempo real:

```bash
tail -f logs/integration.log
```

## 🎯 Próximos Pasos

1. ✅ Adaptador Axon Core implementado
2. ✅ Router proxy implementado
3. ✅ Tests de integración implementados
4. ⏳ Activar túnel Cloudflare en Axon 88
5. ⏳ Configurar token de Axon Core
6. ⏳ Ejecutar tests completos (6/6 passing)
7. ⏳ Integrar frontend con proxy endpoints
8. ⏳ Implementar módulo de entrenamiento de agentes

## 📞 Endpoints de Ejemplo

### Verificar Conectividad

```bash
# Con autenticación
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/dev/token | jq -r .access_token)

# Verificar Axon Core
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/axon-core/health
```

### Chat con IA vía Axon Core

```bash
curl -X POST http://localhost:8080/api/axon-core/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "¿Estás conectado con Axon Agency?",
    "session_id": "test-123",
    "model": "gpt-4o-mini"
  }'
```

### Listar Servicios de Axon 88

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/axon-core/services
```

### Métricas del Sistema

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/axon-core/metrics
```

---

**Estado de Integración**: ✅ Configurado, ⏳ Esperando túnel activo
