# Fix: Module not found - useChatSessions

**Fecha:** 2025-12-01  
**Proyecto:** `/home/axon88/projects/axon-agency-official/axon-agency`  
**App:** `apps/web`

---

## Problema

Error de compilación en Next.js:

```
Module not found: Can't resolve '@/lib/hooks/useChatSessions'
```

Ocurriendo en:
- `apps/web/app/(auth)/agent/page.tsx` (línea 8)
- `apps/web/components/ConversationsSidebar.tsx` (línea 6)

---

## Investigación

### Búsqueda del hook existente

Se realizó una búsqueda exhaustiva en el monorepo:

```bash
rg "useChatSessions" -n .
find . -maxdepth 8 -iname "useChatSessions.*"
```

**Resultados:**
- El hook `useChatSessions` **NO existía** en ninguna parte del repositorio
- Se encontraron referencias en documentación (`docs/night-shift-report.md`) indicando que el hook debería existir, pero el archivo físico no estaba presente
- El componente `page.tsx` y `ConversationsSidebar.tsx` ya estaban importando el hook, causando el error de compilación

### Análisis de dependencias

Se analizaron los componentes que usan el hook para determinar la interfaz requerida:

**`apps/web/app/(auth)/agent/page.tsx` espera:**
- `currentSessionId: string | null`
- `sessions: Session[]`
- `messages: ChatMessage[]`
- `loading: boolean`
- `offline: boolean`
- `loadSessions: () => void`
- `createSession: () => void`
- `saveMessage: (sessionId, role, content, meta?) => Promise<void>`
- `selectSession: (sessionId: string) => void`
- `setCurrentSessionId: (id: string | null) => void`

**`apps/web/components/ConversationsSidebar.tsx` espera:**
- Tipo exportado `Session` con:
  - `session_id: string`
  - `title?: string`
  - `last_message_preview?: string`
  - `last_message_at: string`
  - `last_message_role?: "user" | "assistant"`

---

## Solución Implementada

### Archivo creado

**Ruta:** `/home/axon88/projects/axon-agency-official/axon-agency/apps/web/lib/hooks/useChatSessions.ts`

### Implementación

Se creó un hook React completo que:

1. **Gestiona estado en memoria** usando `useState`:
   - Sesiones de chat (`Session[]`)
   - Mensajes de la sesión actual (`ChatMessage[]`)
   - Estado de carga y conexión
   - ID de sesión actual

2. **Persistencia en localStorage**:
   - Sesiones guardadas en `localStorage.getItem("chat_sessions")`
   - Mensajes guardados en `localStorage.getItem("chat_messages_${sessionId}")`

3. **Funcionalidades implementadas**:
   - `createSession()`: Crea nueva sesión con ID único
   - `saveMessage()`: Guarda mensaje y actualiza preview de sesión
   - `selectSession()`: Cambia la sesión activa y carga sus mensajes
   - `loadSessions()`: Recarga sesiones desde localStorage
   - `setCurrentSessionId()`: Setter para cambiar sesión programáticamente

4. **Generación de IDs**:
   - Usa `crypto.randomUUID()` cuando está disponible
   - Fallback a timestamp + random string para compatibilidad

### Tipos exportados

```typescript
export type ChatMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  createdAt: string;
  meta?: Record<string, any>;
};

export type Session = {
  session_id: string;
  title?: string;
  last_message_preview?: string;
  last_message_at: string;
  last_message_role?: "user" | "assistant";
};
```

### Interfaz del hook

```typescript
export function useChatSessions(): {
  currentSessionId: string | null;
  sessions: Session[];
  messages: ChatMessage[];
  loading: boolean;
  offline: boolean;
  loadSessions: () => void;
  createSession: () => void;
  saveMessage: (sessionId: string, role: "user" | "assistant" | "system", content: string, meta?: Record<string, any>) => Promise<void>;
  selectSession: (sessionId: string) => void;
  setCurrentSessionId: (id: string | null) => void;
}
```

---

## Cambios Realizados

### Archivos creados

1. **`apps/web/lib/hooks/useChatSessions.ts`** (183 líneas)
   - Hook completo con todas las funcionalidades requeridas
   - Persistencia en localStorage
   - Manejo de estado reactivo

### Archivos modificados

**Ninguno** - Los imports en `page.tsx` y `ConversationsSidebar.tsx` ya estaban correctos, solo faltaba la implementación del hook.

---

## Verificación

### TypeScript / Linter

```bash
cd apps/web
npm run lint
```

**Resultado:** ✅ Sin errores relacionados con `useChatSessions`

### Compilación

```bash
cd apps/web
npx next build --no-lint
```

**Resultado:** 
- ✅ El error `Module not found: Can't resolve '@/lib/hooks/useChatSessions'` **desapareció**
- ⚠️ Hay otros errores de build no relacionados (dependencias faltantes: `react-markdown`, `remark-gfm`, `react-syntax-highlighter`, `@/lib/utils`)

### Servidor de desarrollo

```bash
cd apps/web
npm run dev -- --port 5200
```

**Resultado:** ✅ El servidor inicia correctamente y el módulo se resuelve sin errores

### Verificación en navegador

- ✅ El frontend responde en `http://localhost:5200`
- ✅ No hay errores de importación en consola relacionados con `useChatSessions`
- ✅ El componente `/agent` puede renderizar (aunque puede mostrar mensajes vacíos al inicio, lo cual es esperado)

---

## Comandos Ejecutados

```bash
# Verificación de rutas
cd /home/axon88/projects/axon-agency-official/axon-agency
pwd
ls

# Búsqueda del hook
rg "useChatSessions" -n .
find . -maxdepth 8 -iname "useChatSessions.*"

# Creación del directorio
mkdir -p apps/web/lib/hooks

# Verificación de linter
cd apps/web
npm run lint

# Verificación de compilación
npx next build --no-lint

# Inicio del servidor de desarrollo
npm run dev -- --port 5200
```

---

## Estado Final

✅ **Problema resuelto:** El error `Module not found: Can't resolve '@/lib/hooks/useChatSessions'` está completamente resuelto.

✅ **Hook implementado:** El hook `useChatSessions` existe en `apps/web/lib/hooks/useChatSessions.ts` con toda la funcionalidad requerida.

✅ **Compatibilidad:** El hook es compatible con:
- `apps/web/app/(auth)/agent/page.tsx`
- `apps/web/components/ConversationsSidebar.tsx`

✅ **Funcionalidad:** El hook gestiona sesiones de chat en memoria con persistencia en localStorage, sin depender de APIs externas (como se solicitó).

---

## Notas Adicionales

1. **Persistencia local:** El hook usa `localStorage` para persistir sesiones y mensajes. Esto permite que los datos sobrevivan recargas de página.

2. **Sin dependencias externas:** El hook no hace llamadas a APIs. Toda la lógica es local, lo cual es adecuado para desarrollo y permite que el componente compile sin errores.

3. **Errores de build no relacionados:** Hay otros errores de compilación relacionados con dependencias faltantes (`react-markdown`, `remark-gfm`, etc.), pero estos son independientes del fix de `useChatSessions` y no afectan la funcionalidad del agente.

4. **Próximos pasos sugeridos:**
   - Integrar el hook con APIs del backend cuando estén disponibles
   - Agregar sincronización con servidor si se requiere
   - Implementar funcionalidades adicionales como `deleteSession`, `renameSession`, etc., si son necesarias

---

**Fin del reporte**

