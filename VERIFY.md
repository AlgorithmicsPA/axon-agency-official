# Axon Core - Verificación con curl

Ejemplos funcionales para probar todos los endpoints.

## 🔧 Setup

```bash
# Reemplaza con tu URL de Replit o localhost
export REPL_HOST="your-repl-url.replit.dev"

# O para local:
# export REPL_HOST="localhost:8080"

# Obtener token de desarrollo
export TOKEN=$(curl -s -X POST https://$REPL_HOST/api/token/dev | jq -r .access_token)

# Verificar token
echo $TOKEN
```

## 📡 Endpoints

### 1. Health Check (sin auth)

```bash
curl -s https://$REPL_HOST/api/health | jq
```

**Esperado:**
```json
{
  "status": "ok",
  "message": "Axon Core is running"
}
```

### 2. Get Dev Token

```bash
curl -s -X POST "https://$REPL_HOST/api/token/dev?username=test-admin" | jq
```

**Esperado:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "admin",
  "username": "test-admin"
}
```

### 3. Catalog - Detección de Sistema

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  https://$REPL_HOST/api/catalog | jq
```

**Esperado:**
```json
{
  "version": "1.0.0",
  "dev_mode": true,
  "audit_loaded": true,
  "services_detected": {
    "ollama": 11434,
    "n8n": 5679,
    "nginx": 80,
    "postgres": 5432,
    "fastapi": [8091, 8089],
    "docker": true,
    "cloudflared": 20241,
    "xrdp": 3389,
    "ssh": 22,
    "systemd": true,
    "cuda": true
  },
  "capabilities": {
    "llm_local": true,
    "llm_cloud": true,
    "workflows": true,
    "containers": true,
    "systemd": true,
    "gpu": true,
    "tunnels": true,
    "database": true,
    "web_server": true
  }
}
```

### 4. Ejecutar Comando

```bash
curl -s -X POST https://$REPL_HOST/api/commands/run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"/usr/bin/ls -la"}' | jq
```

**Esperado:**
```json
{
  "task_id": "uuid-here",
  "status": "pending",
  "message": "Command queued for execution"
}
```

**Obtener estado del comando:**
```bash
TASK_ID="uuid-from-above"
curl -s -H "Authorization: Bearer $TOKEN" \
  https://$REPL_HOST/api/commands/$TASK_ID | jq
```

### 5. Listar Archivos

```bash
curl -s -X POST https://$REPL_HOST/api/files/list \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path":""}' | jq
```

### 6. Listar Servicios (systemd)

```bash
curl -s -X POST https://$REPL_HOST/api/services/list \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"systemd"}' | jq
```

### 7. Listar Contenedores (Docker)

```bash
curl -s -X POST https://$REPL_HOST/api/services/list \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"docker"}' | jq
```

### 8. Listar Todos los Servicios

```bash
curl -s -X POST https://$REPL_HOST/api/services/list \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq
```

### 9. Métricas del Sistema

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  https://$REPL_HOST/api/metrics | jq
```

**Esperado:**
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "cpu_percent": 25.5,
  "memory_percent": 45.2,
  "memory_available_mb": 2048.5,
  "disk_percent": 60.1,
  "disk_free_gb": 15.3,
  "uptime_seconds": 86400.0,
  "gpu_utilization": 30.0,
  "gpu_temp": 45.0,
  "load_average": [1.5, 1.2, 1.0]
}
```

### 10. Proveedores LLM Disponibles

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  https://$REPL_HOST/api/llm/providers | jq
```

### 11. Inferencia LLM - OpenAI

```bash
curl -s -X POST https://$REPL_HOST/api/llm/infer \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model": "gpt-4o-mini",
    "input": {
      "kind": "text",
      "prompt": "Hola Axon, explica qué es FastAPI en 2 líneas"
    },
    "temperature": 0.7,
    "max_tokens": 200
  }' | jq
```

### 12. Inferencia LLM - Ollama (local)

```bash
curl -s -X POST https://$REPL_HOST/api/llm/infer \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "ollama",
    "model": "llama2",
    "input": {
      "kind": "text",
      "prompt": "¿Qué es Python?"
    }
  }' | jq
```

### 13. Estado de n8n

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  https://$REPL_HOST/api/flows/status | jq
```

### 14. Disparar Workflow n8n

```bash
curl -s -X POST https://$REPL_HOST/api/flows/trigger \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "your-workflow-id",
    "payload": {
      "message": "Test from Axon Core"
    }
  }' | jq
```

### 15. Estado de Túneles

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  https://$REPL_HOST/api/tunnels/status | jq
```

### 16. Reiniciar Túnel

```bash
curl -s -X POST https://$REPL_HOST/api/tunnels/action \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tunnel": "cloudflared",
    "action": "restart"
  }' | jq
```

## 🔐 Ejemplos con Roles

### Viewer (solo lectura)

```bash
# Obtener token con rol viewer
VIEWER_TOKEN=$(curl -s -X POST "https://$REPL_HOST/api/token/dev?username=viewer" | jq -r .access_token)

# Puede ver catalog
curl -H "Authorization: Bearer $VIEWER_TOKEN" \
  https://$REPL_HOST/api/catalog | jq

# NO puede ejecutar comandos (debe retornar 403)
curl -X POST https://$REPL_HOST/api/commands/run \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"/usr/bin/ls"}' | jq
```

### Admin (control total)

```bash
# El token por defecto tiene rol admin
curl -X POST https://$REPL_HOST/api/commands/run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"/usr/bin/uptime"}' | jq
```

## 🧪 Test Completo

Script para probar todo:

```bash
#!/bin/bash
set -e

REPL_HOST="your-repl-url.replit.dev"

echo "=== Axon Core Verification ==="
echo ""

echo "1. Health check..."
curl -sf https://$REPL_HOST/api/health > /dev/null && echo "✓ Health OK"

echo "2. Get token..."
TOKEN=$(curl -sf -X POST https://$REPL_HOST/api/token/dev | jq -r .access_token)
[ -n "$TOKEN" ] && echo "✓ Token OK"

echo "3. Catalog..."
curl -sf -H "Authorization: Bearer $TOKEN" https://$REPL_HOST/api/catalog > /dev/null && echo "✓ Catalog OK"

echo "4. Metrics..."
curl -sf -H "Authorization: Bearer $TOKEN" https://$REPL_HOST/api/metrics > /dev/null && echo "✓ Metrics OK"

echo "5. LLM Providers..."
curl -sf -H "Authorization: Bearer $TOKEN" https://$REPL_HOST/api/llm/providers > /dev/null && echo "✓ LLM OK"

echo ""
echo "=== All tests passed! ==="
```

## 📝 Notas

- Reemplaza `$REPL_HOST` con tu URL real
- En producción, no uses `/api/token/dev` (deshabilita DEV_MODE)
- Los comandos deben estar en la whitelist `ALLOWED_CMDS`
- Algunos endpoints pueden retornar vacío si servicios no disponibles (ej: Docker en Replit)

---

**Última actualización**: Build inicial v1.0.0
