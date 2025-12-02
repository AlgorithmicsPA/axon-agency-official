# Configuración del Backend - AXON Agency

**Fecha:** 2025-12-02  
**Proyecto:** `/home/axon88/projects/axon-agency-official/axon-agency/apps/api`

---

## Variables de Entorno

### Archivo: `apps/api/.env`

El backend usa variables de entorno definidas en `apps/api/.env` y cargadas mediante Pydantic Settings en `app/core/config.py`.

### Variables Esenciales

#### CORS y Red

```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5100,http://localhost:5200,http://127.0.0.1:5200,http://192.168.200.32:5200
API_PORT=8090
SOCKET_PORT=9001
```

- **ALLOWED_ORIGINS**: Lista separada por comas de orígenes permitidos para CORS
- **API_PORT**: Puerto donde corre el servidor FastAPI (por defecto 8090)
- **SOCKET_PORT**: Puerto para WebSocket/Socket.IO (por defecto 9001)

#### Base de Datos

```bash
DATABASE_URL=sqlite:///./storage/axon_agency.db
```

- **DATABASE_URL**: URL de conexión a la base de datos (SQLite por defecto)

#### LLM Providers

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Google Gemini
GEMINI_API_KEY=...

# Ollama (local)
OLLAMA_ENABLED=false
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

- **OPENAI_API_KEY**: Clave de API de OpenAI (requerida para OpenAI provider)
- **GEMINI_API_KEY**: Clave de API de Google Gemini (requerida para Gemini provider)
- **OLLAMA_ENABLED**: Habilitar/deshabilitar Ollama (local)
- **OLLAMA_BASE_URL**: URL base de Ollama (por defecto localhost:11434)
- **OLLAMA_MODEL**: Modelo de Ollama a usar (por defecto llama2)

#### Seguridad

```bash
SECRET_KEY=your-secret-key-here
DEV_MODE=false
```

- **SECRET_KEY**: Clave secreta para JWT y encriptación (NUNCA commitear)
- **DEV_MODE**: Modo desarrollo (bypass de autenticación si es `true`)

#### Storage

```bash
STORAGE_ROOT=./storage
```

- **STORAGE_ROOT**: Directorio raíz para almacenamiento de archivos, vectores, etc.

---

## Servicios Externos

### OpenAI

- **Uso**: Chat completions, embeddings, speech-to-text (Whisper)
- **Endpoints**: `/api/llm/chat`, `/api/llm/chat/stream`, `/api/agent/stt`
- **Requerido**: `OPENAI_API_KEY`

### Google Gemini

- **Uso**: Chat completions (multimodal), embeddings
- **Endpoints**: `/api/llm/chat`, `/api/llm/chat/stream`
- **Requerido**: `GEMINI_API_KEY`

### Ollama (Local)

- **Uso**: Chat completions locales (sin API key)
- **Endpoints**: `/api/llm/chat`, `/api/llm/chat/stream`
- **Requerido**: Ollama corriendo localmente, `OLLAMA_ENABLED=true`

---

## Arranque del Backend en Axon 88

### Método 1: Uvicorn Directo

```bash
cd /home/axon88/projects/axon-agency-official/axon-agency/apps/api
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8090
```

### Método 2: Con Reload (Desarrollo)

```bash
cd /home/axon88/projects/axon-agency-official/axon-agency/apps/api
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
```

### Verificación

```bash
# Health check
curl http://localhost:8090/api/health

# Verificar CORS
curl -H "Origin: http://localhost:5200" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8090/api/metrics
```

---

## Estructura de Routers

Todos los routers se registran en `app/main.py` con prefijos `/api/...`:

- `/api/health` - Health checks
- `/api/metrics` - Métricas del sistema
- `/api/auth/*` - Autenticación
- `/api/llm/*` - LLM completions y streaming
- `/api/agent/*` - Super Axon Agent
- `/api/campaigns/*` - Campañas
- `/api/conversations/*` - Conversaciones
- `/api/rag/*` - RAG (Retrieval Augmented Generation)
- `/api/media/*` - Gestión de medios
- `/api/posts/*` - Publicaciones
- `/api/integrations/*` - Integraciones (WhatsApp, Telegram)
- `/api/autopilots/*` - Autopilots
- `/api/tenants/*` - Multi-tenant
- `/api/orders/*` - Órdenes
- `/api/leads/*` - Leads
- `/api/factory/*` - Fábrica de agentes
- `/api/admin/*` - Administración

---

## Configuración de CORS

CORS se configura en `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Lista parseada desde ALLOWED_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Importante**: Después de cambiar `ALLOWED_ORIGINS` en `.env`, reiniciar el backend para aplicar los cambios.

---

## Base de Datos

### SQLite (Por Defecto)

- **Ubicación**: `apps/api/storage/axon_agency.db`
- **Migraciones**: Automáticas al arrancar (SQLModel)
- **Modelos**: Definidos en `app/models.py`

### Cambiar a PostgreSQL

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/axon_agency
```

---

## Logs

Los logs se configuran en `app/main.py`:

```python
logging.basicConfig(level=logging.INFO)
```

Para cambiar el nivel de logs, modificar `level=logging.INFO` a `logging.DEBUG` o `logging.WARNING`.

---

## Troubleshooting

### CORS Errors

1. Verificar que `ALLOWED_ORIGINS` en `.env` incluya el origen del frontend
2. Reiniciar el backend después de cambiar `.env`
3. Verificar que el middleware CORS esté antes de `include_router(...)`

### LLM Provider Errors

1. Verificar que las API keys estén configuradas en `.env`
2. Verificar conectividad a los servicios externos
3. Revisar logs del backend para errores específicos

### Database Errors

1. Verificar permisos de escritura en `storage/`
2. Verificar que `DATABASE_URL` sea correcta
3. Eliminar `storage/axon_agency.db` para recrear la base de datos (pierde datos)

---

**Fin del documento**

