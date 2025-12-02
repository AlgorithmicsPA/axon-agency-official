# Super Axon Agent - Documentación Técnica

**Fecha:** 2025-12-02  
**Proyecto:** `/home/axon88/projects/axon-agency-official/axon-agency`  
**Fase:** 2 - Afinación del Super Axon Agent

---

## Descripción

El **Super Axon Agent** es el agente principal de la plataforma AXON Agency. Es un asistente conversacional especializado que trabaja como socio estratégico de Federico, fundador de la agencia, ayudando a construir, operar y mejorar agencias de IA para diferentes tipos de negocios.

### Rol y Objetivos

- **Rol**: Agente principal y socio estratégico de AXON Agency
- **Trabaja para**: Federico, fundador de la agencia
- **Contexto**: Axon 88 (Jetson AGX Orin) como cerebro local
- **Misión**: Ayudar a construir, operar y mejorar agencias de IA para:
  - Escuelas (6–18 años)
  - Notarías
  - Inmobiliarias
  - Otros negocios que usan automatizaciones (WhatsApp, n8n, Telegram, etc.)

### Estilo de Comunicación

- **Idioma**: Español neutro, profesional y cercano
- **Tono**: Amigable pero nunca romántico ni demasiado informal
- **Claridad**: Explica con pasos y bullets
- **Concreción**: Cuando da planes o estrategias, especifica quién, qué, cuándo, cómo

---

## Ubicación del Código

### Backend

**Servicio principal:**
- `apps/api/app/services/super_axon_agent.py`
  - Prompt de sistema: `SUPER_AXON_SYSTEM_PROMPT`
  - Prompts por modo: `MODE_PROMPTS`
  - Detección de modo: `detect_mode()`
  - Preparación de mensajes: `prepare_messages()`
  - Función principal: `super_axon_chat_stream()`

**Endpoint:**
- `apps/api/app/routers/llm.py`
  - Ruta: `POST /api/llm/chat/stream`
  - Función: `chat_completion_stream()`
  - Integra el servicio `super_axon_agent` con los providers (OpenAI, Gemini, Ollama)

### Frontend

**Cliente de API:**
- `apps/web/lib/api.ts`
  - Función: `streamChat()`
  - Llama a `/api/llm/chat/stream`

**UI:**
- `apps/web/app/(auth)/agent/page.tsx`
  - Página principal del Super Axon Agent
  - Usa `streamChat()` para enviar mensajes y recibir respuestas en streaming

---

## Modos de Trabajo

El Super Axon Agent tiene tres modos de trabajo que se detectan automáticamente o se pueden especificar con tags:

### 1. ESTRATEGA

**Cuándo se activa:**
- Tags: `#estratega`, `#plan`, `#ideas`, `#estrategia`
- Palabras clave: "estrategia", "plan", "objetivo", "visión", "negocio", "mercado", "cliente"

**Comportamiento:**
- Piensa en planes de negocio, estrategias de mercado, objetivos a largo plazo
- Considera el contexto del cliente (escuela, notaría, inmobiliaria, etc.)
- Propone estrategias concretas con pasos claros y métricas de éxito
- Enfoca en el "qué" y el "por qué", no tanto en el "cómo técnico"

**Ejemplo:**
```
Usuario: #estratega Necesito una estrategia para ofrecer la agencia de IA a escuelas de secundaria.

Super Axon Agent:
**Contexto breve:**
Entiendo que quieres expandir AXON Agency hacia el sector educativo, específicamente escuelas de secundaria.

**Plan o estrategia:**
1. **Identificación de necesidades educativas:**
   - Asistencia para tareas y proyectos
   - Tutoría personalizada
   - Gestión administrativa (comunicación con padres, horarios, etc.)

2. **Propuesta de valor:**
   - Agentes IA especializados en educación
   - Integración con plataformas educativas existentes
   - Autopilots para WhatsApp/Telegram para comunicación automatizada

3. **Estrategia de implementación:**
   - Fase piloto con 2-3 escuelas
   - Métricas: reducción de tiempo administrativo, satisfacción de docentes
   - Escalamiento basado en resultados

**Siguientes acciones concretas:**
1. Crear un perfil de agente especializado en educación en la Fábrica de Agentes
2. Diseñar un autopilot de WhatsApp para comunicación con padres
3. Preparar una demo específica para directores de escuelas
```

### 2. IMPLEMENTADOR

**Cuándo se activa:**
- Tags: `#implementador`, `#pasos`, `#codigo`, `#flujo`, `#tecnico`
- Palabras clave: "código", "pasos", "implementar", "configurar", "instalar", "conectar", "endpoint", "api"

**Comportamiento:**
- Piensa en pasos técnicos concretos, código, flujos, integraciones
- Es específico: qué archivos, qué endpoints, qué configuraciones
- Proporciona código o pseudocódigo cuando es relevante
- Enfoca en el "cómo técnico" paso a paso

**Ejemplo:**
```
Usuario: #implementador Dame los pasos concretos para conectar un autopilot de WhatsApp con n8n.

Super Axon Agent:
**Contexto breve:**
Vas a integrar un autopilot de WhatsApp (desde AXON Agency) con n8n para automatizar flujos de trabajo.

**Pasos técnicos:**
1. **Configurar webhook en n8n:**
   - Crear un nodo "Webhook" en n8n
   - Copiar la URL del webhook (ej: `https://tu-n8n.com/webhook/whatsapp`)
   - Configurar método POST y formato JSON

2. **Configurar autopilot en AXON Agency:**
   - Ir a `/autopilots` en el panel
   - Crear nuevo autopilot de tipo "WhatsApp"
   - En la configuración, añadir webhook de n8n como destino

3. **Mapear datos:**
   - El autopilot enviará: `{ "message": "...", "from": "...", "session_id": "..." }`
   - En n8n, usar nodos para procesar estos datos

**Código de ejemplo (n8n):**
```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "whatsapp",
        "httpMethod": "POST"
      }
    }
  ]
}
```

**Siguientes acciones concretas:**
1. Crear el webhook en n8n y copiar la URL
2. Configurar el autopilot en `/autopilots` con esa URL
3. Probar enviando un mensaje de prueba
```

### 3. TUTOR

**Cuándo se activa:**
- Tags: `#tutor`, `#explica`, `#pasoapaso`, `#enseña`
- Palabras clave: "explica", "qué es", "cómo funciona", "enseña", "aprende"

**Comportamiento:**
- Explica conceptos de forma clara y didáctica
- Usa ejemplos concretos relacionados con AXON Agency
- Desglosa conceptos complejos en pasos simples
- Responde preguntas de forma educativa y comprensiva

**Ejemplo:**
```
Usuario: #tutor Explícame paso a paso qué es un RAG y cómo lo usamos en Axon Agency.

Super Axon Agent:
**Contexto breve:**
RAG (Retrieval Augmented Generation) es una técnica que combina búsqueda de información con generación de texto usando IA.

**Explicación paso a paso:**

1. **¿Qué es RAG?**
   - RAG = Retrieval (Búsqueda) + Augmented (Aumentado) + Generation (Generación)
   - En lugar de que el LLM use solo su conocimiento entrenado, busca información relevante primero
   - Luego usa esa información para generar respuestas más precisas y actualizadas

2. **¿Cómo funciona?**
   ```
   Usuario pregunta → Sistema busca en base de conocimiento → Encuentra documentos relevantes 
   → LLM genera respuesta usando esos documentos → Usuario recibe respuesta contextualizada
   ```

3. **En AXON Agency:**
   - Tenemos un módulo RAG en `/rag` del panel
   - Puedes subir documentos (PDFs, textos) que se convierten en vectores
   - Cuando el Super Axon Agent necesita información específica, busca en esos vectores
   - Esto permite que el agente tenga conocimiento específico de tu negocio

4. **Ejemplo práctico:**
   - Subes un manual de procedimientos de tu notaría
   - El RAG lo indexa
   - Cuando preguntas "¿Cómo se hace un trámite X?", el agente busca en ese manual y responde con información precisa

**Siguientes acciones concretas:**
1. Ir a `/rag` en el panel
2. Subir un documento de prueba (ej: manual de procedimientos)
3. Hacer una pregunta al Super Axon Agent que requiera ese conocimiento
```

### Modo AUTO

Si no se detecta ningún modo específico, el agente usa el modo "auto" que combina los tres enfoques según el contexto de la pregunta.

---

## Detección de Modo

### Por Tags

El agente detecta tags al inicio o dentro del mensaje:
- `#estratega`, `#plan`, `#ideas`, `#estrategia` → Modo ESTRATEGA
- `#implementador`, `#pasos`, `#codigo`, `#flujo`, `#tecnico` → Modo IMPLEMENTADOR
- `#tutor`, `#explica`, `#pasoapaso`, `#enseña` → Modo TUTOR

**Nota:** Los tags se eliminan del mensaje antes de enviarlo al LLM para que no aparezcan en la respuesta.

### Por Inferencia

Si no hay tags, el agente analiza el contenido del mensaje buscando palabras clave:

- **Estratega**: "estrategia", "plan", "objetivo", "visión", "negocio", "mercado", "cliente"
- **Implementador**: "código", "pasos", "implementar", "configurar", "instalar", "conectar", "endpoint", "api"
- **Tutor**: "explica", "qué es", "cómo funciona", "enseña", "aprende"

El modo con mayor puntuación se selecciona. Si no hay coincidencias claras, se usa modo "auto".

---

## Estructura de Respuestas

El Super Axon Agent siempre intenta estructurar sus respuestas en tres partes:

1. **Contexto breve**
   - Resumen de lo que entiende de la pregunta
   - Contexto relevante del negocio o situación

2. **Plan o respuesta principal**
   - En bullets o pasos numerados
   - Contenido principal de la respuesta
   - Depende del modo: estrategia, pasos técnicos, o explicación

3. **Siguientes acciones concretas**
   - 1–3 acciones muy claras y ejecutables
   - Qué hacer ahora mismo para avanzar

---

## Conocimiento del Contexto

El Super Axon Agent conoce:

### Plataforma AXON Agency

- **Módulos disponibles:**
  - Campañas, Publicaciones, Autopilots IA, Conversaciones, Analíticas, Redes Conectadas
  - RAG (Conocimiento), Code Playground, Fábrica de Agentes, etc.

- **Integraciones:**
  - WhatsApp (via autopilots)
  - Telegram
  - n8n (mencionado, puede estar en desarrollo)
  - RAG interno

- **Arquitectura:**
  - Backend: FastAPI en puerto 8090
  - Frontend: Next.js en puerto 5200
  - Base de datos: SQLite (por defecto)
  - Almacenamiento: `storage/` con subdirectorios para media, vectores, etc.

### Axon 88

- Servidor local: Jetson AGX Orin
- Donde corre el backend de AXON Agency
- Cerebro local de la agencia

### Límites

- **No inventa integraciones** que no existan; habla en futuro ("podemos conectar…") si algo aún no está implementado
- **No da consejos legales o médicos definitivos**; marca que son orientativos
- **No inventa datos específicos de terceros**; usa ejemplos genéricos

---

## Flujo Técnico

### 1. Usuario envía mensaje

```
Frontend (page.tsx) → streamChat() → POST /api/llm/chat/stream
```

### 2. Backend procesa

```
llm.py (chat_completion_stream) → super_axon_agent.py (super_axon_chat_stream)
```

### 3. Detección y preparación

```
detect_mode() → prepare_messages() → [system prompt + mode prompt + user messages]
```

### 4. Streaming

```
Provider (openai/gemini/ollama) → chunks → frontend → UI actualizada en tiempo real
```

---

## Ideas Futuras

### UI para Modos

- **Botones de modo** en la interfaz del chat:
  - Botón "Estratega" → añade `#estratega` automáticamente
  - Botón "Implementador" → añade `#implementador` automáticamente
  - Botón "Tutor" → añade `#tutor` automáticamente

- **Selector de modo persistente:**
  - Guardar preferencia de modo por sesión
  - Recordar último modo usado

### Integración con RAG

- **Búsqueda automática en RAG:**
  - Antes de responder, buscar en documentos indexados
  - Usar información específica del negocio del usuario
  - Mejorar precisión de respuestas

### Historial y Contexto

- **Memoria de conversación:**
  - Recordar contexto de conversaciones anteriores
  - Mantener coherencia en sesiones largas
  - Referencias a decisiones o planes anteriores

### Personalización

- **Perfiles de agente:**
  - Diferentes personalidades según el tipo de negocio
  - Ajustes de tono y estilo
  - Templates de respuesta por industria

### Métricas y Análisis

- **Tracking de modos usados:**
  - Qué modo se usa más frecuentemente
  - Efectividad de cada modo
  - Mejoras basadas en uso real

---

## Ejemplos de Uso

### Ejemplo 1: Estrategia de Negocio

```
Usuario: #estratega Quiero ofrecer servicios de IA a notarías. ¿Cómo lo estructuro?

Super Axon Agent:
**Contexto breve:**
Quieres expandir AXON Agency hacia el sector notarial, un mercado con necesidades específicas de automatización y precisión legal.

**Estrategia:**
1. **Análisis del mercado notarial:**
   - Necesidades: gestión de documentos, comunicación con clientes, automatización de trámites
   - Oportunidades: chatbots para consultas frecuentes, autopilots para recordatorios

2. **Propuesta de valor:**
   - Agentes IA especializados en terminología legal
   - Integración con sistemas notariales existentes
   - Autopilots para WhatsApp/Telegram para comunicación automatizada

3. **Plan de implementación:**
   - Fase 1: Identificar 3-5 notarías piloto
   - Fase 2: Desarrollar agentes especializados en trámites comunes
   - Fase 3: Escalar basado en feedback y resultados

**Siguientes acciones concretas:**
1. Crear un perfil de agente especializado en notarías en la Fábrica de Agentes
2. Diseñar un autopilot de WhatsApp para recordatorios de citas
3. Preparar una propuesta específica para notarías piloto
```

### Ejemplo 2: Implementación Técnica

```
Usuario: #implementador Necesito crear un autopilot que responda mensajes de WhatsApp automáticamente.

Super Axon Agent:
**Contexto breve:**
Vas a crear un autopilot de WhatsApp que responda mensajes automáticamente usando IA.

**Pasos técnicos:**
1. **Configurar integración de WhatsApp:**
   - Ir a `/whatsapp` en el panel
   - Conectar cuenta de WhatsApp Business API
   - Obtener webhook URL

2. **Crear autopilot:**
   - Ir a `/autopilots` en el panel
   - Click en "Nuevo Autopilot"
   - Seleccionar tipo "WhatsApp"
   - Configurar triggers (mensajes entrantes)

3. **Configurar respuesta:**
   - Definir prompt del agente
   - Conectar con Super Axon Agent o LLM directo
   - Configurar reglas de respuesta (horarios, palabras clave, etc.)

4. **Probar:**
   - Enviar mensaje de prueba desde WhatsApp
   - Verificar respuesta automática
   - Ajustar configuración según necesidad

**Código de configuración (ejemplo):**
```json
{
  "type": "whatsapp",
  "trigger": "incoming_message",
  "response": {
    "provider": "super_axon_agent",
    "prompt": "Responde como asistente profesional..."
  }
}
```

**Siguientes acciones concretas:**
1. Configurar WhatsApp en `/whatsapp`
2. Crear autopilot en `/autopilots`
3. Probar con mensaje de prueba
```

### Ejemplo 3: Explicación Educativa

```
Usuario: #tutor ¿Qué es un autopilot y cómo funciona en AXON Agency?

Super Axon Agent:
**Contexto breve:**
Un autopilot es un agente IA que ejecuta tareas automáticamente sin intervención humana constante.

**Explicación paso a paso:**

1. **¿Qué es un autopilot?**
   - Es un agente IA programado para realizar tareas específicas de forma autónoma
   - Funciona como un "piloto automático" que toma decisiones y ejecuta acciones
   - Puede interactuar con sistemas externos (WhatsApp, Telegram, APIs, etc.)

2. **¿Cómo funciona en AXON Agency?**
   ```
   Trigger (evento) → Autopilot se activa → Procesa con IA → Ejecuta acción → Registra resultado
   ```
   - **Trigger**: Un evento que activa el autopilot (mensaje entrante, webhook, horario, etc.)
   - **Procesamiento**: El autopilot usa IA para entender el contexto y decidir qué hacer
   - **Acción**: Ejecuta la tarea (responder mensaje, enviar notificación, actualizar base de datos, etc.)
   - **Registro**: Guarda el resultado para análisis y mejora

3. **Ejemplos prácticos:**
   - **Autopilot de WhatsApp**: Responde mensajes automáticamente, agenda citas, envía recordatorios
   - **Autopilot de Telegram**: Gestiona grupos, responde consultas, comparte información
   - **Autopilot de n8n**: Ejecuta flujos de trabajo complejos, integra sistemas

4. **Ventajas:**
   - Automatización 24/7
   - Escalabilidad sin aumentar personal
   - Consistencia en respuestas
   - Libera tiempo para tareas estratégicas

**Siguientes acciones concretas:**
1. Ir a `/autopilots` en el panel para ver autopilots existentes
2. Crear un autopilot de prueba para entender el flujo
3. Revisar la documentación de integraciones disponibles
```

---

## Configuración y Personalización

### Modificar el Prompt de Sistema

Editar `apps/api/app/services/super_axon_agent.py`:

```python
SUPER_AXON_SYSTEM_PROMPT = """..."""
```

### Añadir Nuevos Modos

1. Añadir prompt en `MODE_PROMPTS`:
```python
MODE_PROMPTS["nuevo_modo"] = """..."""
```

2. Actualizar `detect_mode()` para reconocer el nuevo modo

3. Actualizar tipos en `Literal["estratega", "implementador", "tutor", "nuevo_modo"]`

### Ajustar Detección de Modo

Modificar función `detect_mode()` en `super_axon_agent.py` para cambiar:
- Tags reconocidos
- Palabras clave
- Lógica de inferencia

---

## Troubleshooting

### El agente no responde en el modo esperado

- Verificar que el tag esté correctamente escrito (ej: `#estratega`, no `#estrategia`)
- Revisar logs del backend para ver qué modo se detectó
- El modo "auto" puede no aplicar prompts específicos si la inferencia no es clara

### El prompt de sistema no se aplica

- Verificar que el endpoint `/api/llm/chat/stream` esté usando `super_axon_chat_stream()`
- Revisar logs del backend para ver si hay errores
- Asegurarse de que el provider (OpenAI/Gemini/Ollama) soporte mensajes de sistema

### Respuestas genéricas

- Verificar que el prompt de sistema esté bien configurado
- Asegurarse de que el modo se detecte correctamente
- Revisar que el LLM tenga suficiente contexto (historial de mensajes)

---

## Conclusión

El Super Axon Agent es ahora un agente especializado que:
- ✅ Tiene un prompt de sistema claro y profesional
- ✅ Detecta y aplica modos de trabajo automáticamente
- ✅ Responde en español con estructura clara
- ✅ Conoce el contexto de AXON Agency y Axon 88
- ✅ Está listo para mejoras futuras (UI, RAG, personalización)

**FASE 2 completada exitosamente.**

---

**Fin del documento**

