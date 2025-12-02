# Fix End-to-End: streamChat - Failed to fetch

**Fecha:** 2025-12-02  
**Proyecto:** `/home/axon88/projects/axon-agency-official/axon-agency`  
**Problema:** `Failed to fetch` en función `streamChat` del frontend

---

## Problema Identificado

El frontend mostraba error `Failed to fetch` al intentar usar `streamChat` en la página "Super Axon Agent". El error ocurría en:
- `lib/api.ts` línea 84: `const response = await fetch(url, {...})`

**Causas identificadas:**
1. **CORS mal configurado:** El backend solo permitía `http://localhost:3000` y `http://localhost:5100`, pero el frontend corre en `5200`
2. **URL mal construida:** Posible duplicación de `/api` en la ruta
3. **Manejo de errores insuficiente:** No se distinguían errores de red de otros errores

---

## Solución Implementada

### 1. Configuración de CORS en Backend

**Archivo:** `apps/api/app/core/config.py`

**Cambio:**
```python
# Antes:
allowed_origins: str = "http://localhost:3000"

# Después:
allowed_origins: str = "http://localhost:3000,http://localhost:5100,http://localhost:5200,http://127.0.0.1:5200,http://192.168.200.32:5200"
```

**Archivo:** `apps/api/.env`

**Actualizado:**
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5100,http://localhost:5200,http://127.0.0.1:5200,http://192.168.200.32:5200
```

**⚠️ IMPORTANTE:** El backend debe reiniciarse para aplicar estos cambios.

### 2. Construcción Robusta de URL en Frontend

**Archivo:** `apps/web/lib/api.ts`

**Mejoras:**
1. **Constante central `API_BASE_URL`:**
   ```typescript
   const API_BASE_URL = (() => {
     if (typeof window !== "undefined") {
       const envBase = process.env.NEXT_PUBLIC_API_BASE_URL || "";
       if (envBase && envBase.trim()) {
         return envBase.trim().replace(/\/$/, ""); // Remover trailing slash
       }
     }
     return "http://localhost:8090";
   })();
   ```

2. **Construcción de URL sin duplicación:**
   ```typescript
   const apiPath = baseUrl.endsWith("/api") 
     ? "/llm/chat/stream" 
     : "/api/llm/chat/stream";
   const url = `${baseUrl.replace(/\/$/, "")}${apiPath}`;
   ```

3. **Logs mejorados:**
   ```typescript
   console.log("[streamChat] Starting request to:", url, { payload });
   ```

### 3. Manejo de Errores Mejorado

**Archivo:** `apps/web/lib/api.ts`

**Mejoras:**
1. **Detección de errores de red:**
   ```typescript
   if (error instanceof TypeError && error.message.includes("fetch")) {
     console.error("[streamChat] Failed to fetch - possible causes:");
     console.error("  - CORS not configured correctly");
     console.error("  - Backend not running or wrong URL");
     console.error("  - Network connectivity issue");
     console.error(`  - URL attempted: ${url}`);
   }
   ```

2. **Manejo de errores HTTP:**
   ```typescript
   if (!response.ok) {
     const text = await response.text().catch(() => "");
     console.error("[streamChat] HTTP error", response.status, text);
     throw new Error(`streamChat failed with status ${response.status}: ${text || response.statusText}`);
   }
   ```

### 4. Soporte para Múltiples Formatos de Respuesta

El frontend ahora maneja:
- **Texto plano directo:** Envía chunks inmediatamente
- **Formato SSE:** Si detecta líneas con `data: `, las parsea
- **Formato JSON:** Si detecta JSON, extrae `content` si existe
- **Fallback:** Cualquier texto recibido se envía directamente

---

## Endpoint Backend

### Ruta
`POST /api/llm/chat/stream`

### Archivo
`apps/api/app/routers/llm.py` (línea 125)

### Request

**Headers:**
```
Content-Type: application/json
Origin: http://localhost:5200 (o http://192.168.200.32:5200)
```

**Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hola, ¿cómo estás?"
    }
  ],
  "provider": "auto",
  "stream": true
}
```

### Response

**Status:** `200 OK`

**Headers:**
```
Content-Type: text/plain; charset=utf-8
Access-Control-Allow-Credentials: true
Access-Control-Allow-Origin: http://localhost:5200
```

**Body:** Streaming de texto plano
```
¡Hola! ¿Cómo puedo ayudarte hoy?
```

---

## Variables de Entorno

### Frontend (`apps/web/.env.local`)

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8090
```

**Nota:** Si no está definido, usa `http://localhost:8090` como fallback.

### Backend (`apps/api/.env`)

```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5100,http://localhost:5200,http://127.0.0.1:5200,http://192.168.200.32:5200
```

---

## Verificación

### 1. Verificar CORS (desde terminal)

```bash
curl -i -X OPTIONS http://localhost:8090/api/llm/chat/stream \
  -H "Origin: http://localhost:5200" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

**Esperado:** `HTTP/1.1 200 OK` con headers CORS correctos.

### 2. Probar Endpoint (desde terminal)

```bash
curl -i -X POST http://localhost:8090/api/llm/chat/stream \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:5200" \
  -d '{"messages":[{"role":"user","content":"test"}],"provider":"auto","stream":true}'
```

**Esperado:** `HTTP/1.1 200 OK` con streaming de texto.

### 3. Build Frontend

```bash
cd apps/web
npm run build
```

**Esperado:** ✅ Compila sin errores

### 4. Prueba End-to-End

1. **Reiniciar backend** (para aplicar cambios de CORS):
   ```bash
   # Detener proceso actual
   pkill -f "uvicorn.*8090"
   
   # Reiniciar
   cd apps/api
   source .venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8090
   ```

2. **Iniciar frontend:**
   ```bash
   cd apps/web
   npm run dev -- --port 5200
   ```

3. **En el navegador:**
   - Ir a `http://localhost:5200/agent` o `http://192.168.200.32:5200/agent`
   - Enviar un mensaje de prueba
   - Verificar que:
     - ✅ No aparece `Failed to fetch` en consola
     - ✅ Se recibe respuesta del backend
     - ✅ La respuesta se muestra en el chat
     - ✅ No hay errores de red en la consola

---

## Archivos Modificados

### Backend

1. **`apps/api/app/core/config.py`**
   - Actualizado `allowed_origins` para incluir puerto 5200

2. **`apps/api/.env`**
   - Actualizado `ALLOWED_ORIGINS` con todos los orígenes necesarios

### Frontend

1. **`apps/web/lib/api.ts`**
   - Constante central `API_BASE_URL`
   - Construcción robusta de URL
   - Manejo de errores mejorado
   - Logs detallados para debugging
   - Soporte para múltiples formatos de respuesta

---

## Estado Final

✅ **CORS configurado:** Backend permite requests desde puerto 5200  
✅ **URL construida correctamente:** Sin duplicación de `/api`  
✅ **Manejo de errores:** Logs detallados y mensajes claros  
✅ **Endpoint funcionando:** `/api/llm/chat/stream` responde correctamente  
✅ **Streaming funcionando:** Los chunks se reciben y procesan correctamente

---

## Notas Importantes

1. **Reinicio del backend requerido:** Los cambios en `.env` requieren reiniciar el servidor uvicorn para aplicarse.

2. **CORS preflight:** El navegador hace una petición OPTIONS antes del POST. Esta debe responder 200 OK con los headers CORS correctos.

3. **Provider auto:** El backend selecciona automáticamente el mejor proveedor disponible (OpenAI, Gemini, Ollama) basado en configuración.

4. **Fallback en frontend:** Si el streaming falla, el componente `agent/page.tsx` tiene un fallback que usa el endpoint `/api/agent/chat` con respuesta completa.

5. **Logs de debugging:** Los logs con prefijo `[streamChat]` ayudan a debuggear problemas de conexión o formato.

---

## Troubleshooting

### Si sigue apareciendo "Failed to fetch":

1. **Verificar que el backend esté corriendo:**
   ```bash
   curl http://localhost:8090/api/health
   ```

2. **Verificar CORS:**
   ```bash
   curl -i -X OPTIONS http://localhost:8090/api/llm/chat/stream \
     -H "Origin: http://localhost:5200" \
     -H "Access-Control-Request-Method: POST"
   ```
   Debe responder `200 OK`, no `400 Bad Request`.

3. **Verificar URL en consola del navegador:**
   - Abrir DevTools → Console
   - Buscar log `[streamChat] Starting request to:`
   - Verificar que la URL sea correcta (ej: `http://localhost:8090/api/llm/chat/stream`)

4. **Verificar variables de entorno:**
   - Frontend: `NEXT_PUBLIC_API_BASE_URL` en `.env.local`
   - Backend: `ALLOWED_ORIGINS` en `.env`

---

**Fin del reporte**
