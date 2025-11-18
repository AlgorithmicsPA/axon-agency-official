# Axon Core - Checklist de Verificación

## ✅ Setup Inicial

- [ ] **Crear .env** a partir de .env.example
  ```bash
  cp .env.example .env
  ```

- [ ] **Editar .env** con valores apropiados (opcional para empezar)
  - Cambiar `JWT_SECRET` a un valor seguro en producción
  - Configurar API keys de LLMs si vas a usarlos
  - Ajustar `ALLOWED_CMDS` según necesidades

- [ ] **Instalar dependencias** (automático en Replit)
  ```bash
  pip install -r requirements.txt
  ```

## 🚀 Replit

- [✓] **Workflow configurado** - El servidor se levanta automáticamente
- [ ] **Abrir el navegador** integrado de Replit
- [ ] **Abrir /docs** para ver documentación interactiva de OpenAPI
- [ ] **Verificar logs** en la consola de Replit

## 🔑 Autenticación

- [ ] **Obtener token de desarrollo**
  ```bash
  python scripts/print_token_dev.py
  ```
  
- [ ] **Copiar el token** para usarlo en las pruebas

## 🧪 Pruebas Básicas

### Health Check (sin autenticación)

- [ ] **GET /api/health**
  ```bash
  curl https://<YOUR-REPL-URL>/api/health
  ```
  Esperado: `{"status":"ok","message":"Axon Core is running"}`

### Token Dev (solo DEV_MODE=true)

- [ ] **POST /api/token/dev**
  ```bash
  curl -s -X POST https://<YOUR-REPL-URL>/api/token/dev | jq
  ```
  Esperado: JSON con `access_token`

### Catalog (requiere token)

- [ ] **GET /api/catalog**
  ```bash
  TOKEN="your-token-here"
  curl -H "Authorization: Bearer $TOKEN" https://<YOUR-REPL-URL>/api/catalog | jq
  ```
  Esperado: JSON con `services_detected` y `capabilities`

### Comando Simple

- [ ] **POST /api/commands/run**
  ```bash
  curl -X POST https://<YOUR-REPL-URL>/api/commands/run \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"cmd":"/usr/bin/ls -la"}'
  ```
  Esperado: JSON con `task_id`

### Métricas del Sistema

- [ ] **GET /api/metrics**
  ```bash
  curl -H "Authorization: Bearer $TOKEN" https://<YOUR-REPL-URL>/api/metrics | jq
  ```
  Esperado: JSON con CPU, RAM, disco, uptime

## 🔌 Proveedores LLM (opcional)

Si configuraste API keys:

- [ ] **GET /api/llm/providers**
  ```bash
  curl -H "Authorization: Bearer $TOKEN" https://<YOUR-REPL-URL>/api/llm/providers | jq
  ```

- [ ] **POST /api/llm/infer** (OpenAI ejemplo)
  ```bash
  curl -X POST https://<YOUR-REPL-URL>/api/llm/infer \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "provider":"openai",
      "model":"gpt-4o-mini",
      "input":{"kind":"text","prompt":"Hola Axon"}
    }' | jq
  ```

## 🐳 Docker (local o Axon 88)

- [ ] **Construir imagen**
  ```bash
  docker compose build
  ```

- [ ] **Iniciar contenedor**
  ```bash
  docker compose up -d
  ```

- [ ] **Verificar logs**
  ```bash
  docker compose logs -f axon-core
  ```

- [ ] **Health check**
  ```bash
  curl http://localhost:8080/api/health
  ```

## ⚙️ Systemd (Axon 88)

- [ ] **Copiar proyecto a Axon 88**
  ```bash
  scp -r . axon88@host:/tmp/axon-core
  ```

- [ ] **Ejecutar instalador**
  ```bash
  cd /tmp/axon-core
  sudo bash scripts/install_systemd.sh
  ```

- [ ] **Iniciar servicio**
  ```bash
  sudo systemctl start axon-core
  ```

- [ ] **Verificar estado**
  ```bash
  sudo systemctl status axon-core
  ```

- [ ] **Ver logs**
  ```bash
  sudo journalctl -u axon-core -f
  ```

## 📊 Verificaciones Avanzadas

- [ ] **Listar servicios systemd** (si disponible)
  ```bash
  curl -X POST https://<URL>/api/services/list \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"type":"systemd"}' | jq
  ```

- [ ] **Listar contenedores Docker** (si disponible)
  ```bash
  curl -X POST https://<URL>/api/services/list \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"type":"docker"}' | jq
  ```

- [ ] **Estado de túneles**
  ```bash
  curl -H "Authorization: Bearer $TOKEN" https://<URL>/api/tunnels/status | jq
  ```

- [ ] **Estado de n8n** (si configurado)
  ```bash
  curl -H "Authorization: Bearer $TOKEN" https://<URL>/api/flows/status | jq
  ```

## 🧪 Tests Automatizados

- [ ] **Ejecutar suite de tests**
  ```bash
  pytest tests/ -v
  ```

- [ ] **Verificar cobertura**
  ```bash
  pytest tests/ --cov=app
  ```

## 🔐 Seguridad (Producción)

- [ ] **Cambiar JWT_SECRET** a valor aleatorio seguro
- [ ] **Deshabilitar DEV_MODE** (set `DEV_MODE=false`)
- [ ] **Revisar ALLOWED_CMDS** - solo comandos necesarios
- [ ] **Configurar CORS** apropiadamente (no usar `*` en prod)
- [ ] **Proteger .env** - no commitear a git
- [ ] **Rotar logs** - verificar rotación en `logs/`

## 📝 Notas

- ✅ = Completado y verificado
- ⚠️ = Completado con advertencias
- ❌ = Fallido o no aplicable

## 🎯 Criterios de Aceptación

- [x] uvicorn app.main:app levanta sin errores
- [x] GET /api/health → 200
- [x] GET /api/catalog muestra detecciones de axon88_audit.json
- [x] POST /api/commands/run acepta comandos whitelisted
- [x] POST /api/llm/infer acepta requests (mock si falta provider)
- [x] Documentación completa (README, VERIFY, este CHECKLIST)
- [x] Docker compose funcional
- [x] Script systemd funcional

---

**Última actualización**: Build inicial v1.0.0
