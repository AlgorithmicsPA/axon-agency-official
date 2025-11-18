# Axon Core Backend

Backend productivo para gestión de infraestructura Axon 88. API REST + WebSocket con control de servicios, comandos, archivos, LLMs multiproveedor, métricas y más.

## 🚀 Características

- **API REST** completa con autenticación JWT (roles admin/viewer)
- **WebSocket** para streaming de logs en tiempo real
- **Autodetección** de servicios desde `axon88_audit.json`
- **Control de servicios** systemd y Docker
- **Ejecución de comandos** con whitelist y streaming
- **Gestión de archivos** con jaula de seguridad
- **Integración n8n** para disparar workflows
- **LLMs multiproveedor**: OpenAI, Gemini, DeepSeek, Ollama, SDXL
- **Métricas en tiempo real**: CPU, RAM, disco, GPU (si disponible)
- **Auditoría completa** en `logs/audit.jsonl`
- **Arquitectura modular** extensible por plugins

## 📋 Requisitos

- Python 3.11+
- (Opcional) Docker para deployment en contenedor
- (Opcional) systemd para deployment en Ubuntu/Debian

## ⚡ Quick Start (Replit)

1. **Crear archivo .env:**
```bash
cp .env.example .env
```

2. **El workflow ya está configurado** - el servidor se levantará automáticamente

3. **Obtener token de desarrollo:**
```bash
python scripts/print_token_dev.py
```

4. **Abrir documentación interactiva:**
- Navega a la URL de tu Repl + `/docs`
- Usa el token generado para autenticarte

## 🖥️ Development Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración
cp .env.example .env

# Editar .env con tus valores
nano .env

# Levantar servidor
make dev
# O: uvicorn app.main:sio_app --host 0.0.0.0 --port 8080 --reload
```

## 🐳 Docker

```bash
# Construir e iniciar
make docker-up
# O: docker compose up -d

# Ver logs
make docker-logs
# O: docker compose logs -f axon-core

# Detener
make docker-down
```

## 🔧 Deployment en Axon 88 (systemd)

```bash
# Copiar proyecto a Axon 88
scp -r . axon88@axon-host:/tmp/axon-core

# En Axon 88, instalar como servicio
cd /tmp/axon-core
sudo bash scripts/install_systemd.sh

# Iniciar servicio
sudo systemctl start axon-core
sudo systemctl status axon-core

# Ver logs
sudo journalctl -u axon-core -f
```

## 🔑 Autenticación

### Modo Desarrollo (DEV_MODE=true)

```bash
# Obtener token
curl -X POST http://localhost:8080/api/token/dev?username=admin

# O con script
python scripts/print_token_dev.py
```

### Modo Producción (DEV_MODE=false)

El endpoint `/api/token/dev` **no estará disponible**. Debes implementar tu propio sistema de autenticación o generar tokens manualmente con el script.

## 📡 API Endpoints

### Health & Catalog
- `GET /api/health` - Health check
- `GET /api/catalog` - Sistema detectado y capacidades

### Commands
- `POST /api/commands/run` - Ejecutar comando
- `GET /api/commands/{task_id}` - Estado de tarea

### Services
- `POST /api/services/list` - Listar servicios
- `POST /api/services/action` - Controlar servicio

### Files
- `POST /api/files/list` - Listar archivos
- `POST /api/files/upload` - Subir archivo
- `POST /api/files/download` - Descargar archivo

### Flows (n8n)
- `POST /api/flows/trigger` - Disparar workflow
- `GET /api/flows/status` - Estado de n8n

### LLM
- `POST /api/llm/infer` - Inferencia LLM
- `GET /api/llm/providers` - Proveedores disponibles

### Tunnels
- `GET /api/tunnels/status` - Estado de túneles
- `POST /api/tunnels/action` - Controlar túnel

### Metrics
- `GET /api/metrics` - Métricas del sistema

Ver `/docs` para documentación completa de OpenAPI.

## 🔌 WebSocket

Conectar a `/ws/socket.io` con autenticación:

```javascript
const socket = io('http://localhost:8080/ws', {
  path: '/ws/socket.io',
  auth: {
    token: 'YOUR_JWT_TOKEN'
  }
});

socket.on('command_output', (data) => {
  console.log(data);
});
```

## 🧪 Testing

```bash
# Ejecutar tests
make test
# O: pytest tests/ -v

# Con coverage
pytest tests/ --cov=app --cov-report=html
```

## 🎨 Linting & Formatting

```bash
# Formatear código
make fmt

# Verificar linting
make lint
```

## 📁 Estructura del Proyecto

```
axon-core/
├── app/
│   ├── main.py              # Aplicación principal
│   ├── config.py            # Configuración
│   ├── security.py          # JWT & autenticación
│   ├── ws.py                # WebSocket server
│   ├── deps.py              # Dependencies injection
│   ├── routers/             # Endpoints REST
│   ├── core/                # Lógica central
│   │   ├── detect.py        # Autodetección
│   │   ├── events.py        # Sistema de eventos
│   │   ├── registry.py      # Registry de adapters
│   │   ├── types.py         # Modelos Pydantic
│   │   └── utils.py         # Utilidades
│   └── adapters/            # Adapters modulares
│       ├── services_*.py    # systemd, docker
│       ├── llm_*.py         # OpenAI, Gemini, etc.
│       ├── flows_*.py       # n8n
│       └── tunnels_*.py     # cloudflared, tailscale
├── tests/                   # Tests
├── scripts/                 # Scripts útiles
├── logs/                    # Logs y auditoría
├── .env.example             # Configuración de ejemplo
├── requirements.txt         # Dependencias Python
├── Dockerfile               # Imagen Docker
├── docker-compose.yml       # Orquestación
└── Makefile                 # Comandos útiles
```

## 🔐 Seguridad

- **JWT obligatorio** en todos los endpoints (excepto `/health`)
- **Whitelist de comandos** configurable via `ALLOWED_CMDS`
- **Path traversal protection** en operaciones de archivos
- **Roles** admin/viewer para control de acceso
- **Auditoría completa** de acciones en `logs/audit.jsonl`

## 🌐 Variables de Entorno

Ver `.env.example` para la lista completa. Las principales:

```env
# Server
BIND=0.0.0.0
PORT=8080

# JWT
JWT_SECRET=changeme-use-a-secure-secret
DEV_MODE=true  # Deshabilitar en producción

# Comandos permitidos
ALLOWED_CMDS=/usr/bin/ls,/usr/bin/cat,...

# LLM APIs
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...

# Servicios locales
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

## 🧩 Extensibilidad

Para añadir un nuevo adapter:

1. Crear archivo en `app/adapters/`
2. Implementar interfaz según tipo (service, LLM, tunnel, etc.)
3. Registrar en `app/core/registry.py`
4. Usar en routers correspondientes

## 📊 Monitoreo

Los logs se guardan en:
- `logs/axon-core.log` - Logs de aplicación (rotación 10MB)
- `logs/audit.jsonl` - Auditoría de acciones (JSONL)

## 🚢 Export to GitHub

Para exportar este proyecto:

1. Click en el botón de menú de Replit
2. Selecciona "Export to GitHub"
3. Configura tu repositorio
4. Push automático

## 📝 Licencia

Propiedad de Algorithmics PA / Axon 88.

## 🆘 Soporte

Ver `CHECKLIST.md` para verificación paso a paso.
Ver `VERIFY.md` para ejemplos de pruebas con curl.
Ver `POST_BUILD_REPORT.md` para detalles de detección.
