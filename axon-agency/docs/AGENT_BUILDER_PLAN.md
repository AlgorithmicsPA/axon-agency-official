# Agent Builder - Plan de Arquitectura (FASE 4.B)

**Estado:** 📋 Diseño en progreso - NO implementado  
**Fecha:** Noviembre 16, 2025  
**Autor:** AXON Agency Team  
**Versión:** 1.0.0

---

## 1. Resumen Ejecutivo

### ¿Qué es el Agent Builder?

**Agent Builder** es el subsistema inteligente de Axon 88 que transforma un `AgentBlueprint` (el "plano" de un agente/sistema) en una **estructura de proyecto completa y lista para construir**.

Mientras que:
- **Builder v1** construye el código físico del proyecto
- **Builder v2** añade QA y empaquetado de deliverables

**Agent Builder** actúa como la "capa de traducción" que:
1. Lee el `AgentBlueprint` (qué quiere el cliente)
2. Genera la especificación detallada de construcción (`AgentBuildSpec`)
3. Crea los artefactos necesarios: flujos, configuraciones, integraciones, prompts
4. Prepara todo para que Builder v1/v2 lo construya y empaquete

### ¿Por qué necesitamos Agent Builder?

**Problema actual:**
- Builder v1/v2 construyen proyectos genéricos basados en un `plan` de texto libre
- No hay lógica que interprete QUÉ tipo de agente se está construyendo
- Cada agente (WhatsApp, Marketing, etc.) necesita:
  - Flujos específicos de conversación
  - Integraciones con servicios externos (n8n, VAPI, CRMs)
  - Prompts y configuraciones particulares
  - Estructura de proyecto coherente

**Con Agent Builder:**
- Blueprint define CLARAMENTE: tipo de agente, canales, capacidades, fuentes
- Agent Builder genera automáticamente:
  - `/spec/` - Especificación detallada del agente
  - `/flows/` - Flujos de conversación/automatización
  - `/config/` - Configuraciones por capability
  - `/integrations/` - Manifests para n8n, VAPI, webhooks
  - `/prompts/` - Prompts base por módulo

### Filosofía del Negocio

**No vendemos chatbots - Vendemos SISTEMAS completos:**
- Un "WhatsApp Autopilot" no es solo un bot de respuestas
- Es un SISTEMA con:
  - Flujos de ventas automatizados
  - Integración con CRM
  - Recordatorios programados
  - Analytics en tiempo real
  - Dashboard para el cliente

**Agent Builder garantiza coherencia:**
- Cada agente del mismo tipo tiene la misma estructura base
- Capabilities se mapean a módulos concretos (no ambiguos)
- Integraciones quedan documentadas y listas para activar

---

## 2. Ubicación en el Ecosistema Actual

### Dónde Vive el Agent Builder

**Ubicación física:** Axon 88 (Jetson Orin Nano)  
**Archivo principal (propuesto):** `~/factory/agent_builder.py`

### Flujo Completo: Order → Agente Construido

```
┌─────────────────────────────────────────────────────────────────────────┐
│ REPLIT (Cerebro - Cloud)                                                │
│                                                                          │
│  1. Cliente solicita agente desde /catalog                              │
│     POST /api/catalog/orders                                            │
│     → Se genera Order + AgentBlueprint automáticamente                 │
│                                                                          │
│  2. Orchestrator genera plan de construcción                            │
│     POST /api/factory/process-orders                                    │
│     → LLM genera plan JSON estructurado                                 │
│                                                                          │
│  3. Orchestrator envía a Axon 88                                        │
│     POST https://api-axon88.../factory/build-local                      │
│     Payload: { order, plan, agent_blueprint }                           │
│                                                                          │
└──────────────────────┬──────────────────────────────────────────────────┘
                       │
                       │ HTTPS vía Cloudflare Tunnel
                       ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ AXON 88 (Fábrica - Local Jetson)                                        │
│                                                                          │
│  4. ✨ NUEVO: Agent Builder procesa blueprint                           │
│     ~/factory/agent_builder.py                                          │
│     Input:  { order, plan, agent_blueprint }                            │
│     Output: AgentBuildSpec + Artefactos preparados                      │
│                                                                          │
│     Pasos internos del Agent Builder:                                   │
│     ┌────────────────────────────────────────────────────────┐          │
│     │ a) BlueprintParser                                     │          │
│     │    - Parsea agent_blueprint                            │          │
│     │    - Normaliza sources, channels, capabilities         │          │
│     │                                                         │          │
│     │ b) TemplateSelector                                    │          │
│     │    - Selecciona template base según agent_type         │          │
│     │    - Ej: whatsapp_autopilot → template_whatsapp/      │          │
│     │                                                         │          │
│     │ c) CapabilityMapper                                    │          │
│     │    - Mapea capabilities → módulos concretos            │          │
│     │    - Ej: "ventas" → sales_flow.json + sales_intents   │          │
│     │                                                         │          │
│     │ d) ArtifactGenerator                                   │          │
│     │    - Genera /spec/, /flows/, /config/, /prompts/      │          │
│     │    - Crea AgentBuildSpec unificado                    │          │
│     │                                                         │          │
│     │ e) IntegrationMapper                                   │          │
│     │    - Prepara manifests de integraciones                │          │
│     │    - n8n, VAPI, webhooks, CRMs                        │          │
│     └────────────────────────────────────────────────────────┘          │
│                                                                          │
│  5. Builder v1 construye proyecto usando AgentBuildSpec                 │
│     → Crea backend, frontend, DB schemas                                │
│     → Incluye artefactos de Agent Builder                               │
│                                                                          │
│  6. Builder v2 ejecuta QA + genera deliverable                          │
│     → QA valida artefactos generados por Agent Builder                  │
│     → Empaqueta todo (código + flows + config + integrations)          │
│                                                                          │
│  7. Respuesta a Replit con resultado completo                           │
│     { success, product_path, qa, deliverable_metadata }                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Integración con Builder v2

**Agent Builder NO reemplaza Builder v1/v2 - Los complementa:**

| Componente | Responsabilidad | Cuándo se ejecuta |
|------------|-----------------|-------------------|
| **Agent Builder** | Interpreta blueprint → genera artefactos específicos del agente | ANTES de Builder v1 |
| **Builder v1** | Construye código físico del proyecto (backend, frontend, DB) | DESPUÉS de Agent Builder |
| **Builder v2** | QA + empaquetado de deliverables | DESPUÉS de Builder v1 |

**Flujo de ejecución propuesto:**
```
/factory/build-local recibe (order, plan, agent_blueprint)
    ↓
Agent Builder genera artefactos → AgentBuildSpec
    ↓
Builder v1 construye proyecto usando AgentBuildSpec
    ↓
Builder v2 ejecuta QA + genera deliverable
    ↓
Respuesta a Replit con todo completo
```

---

## 3. Arquitectura Interna del Agent Builder

### 3.1 Módulos Principales

```
agent_builder.py
│
├── BlueprintParser
│   ├── parse_blueprint(agent_blueprint: dict) → ParsedBlueprint
│   ├── normalize_sources() → list[SourceSpec]
│   ├── normalize_channels() → list[ChannelSpec]
│   └── normalize_capabilities() → list[str]
│
├── TemplateSelector
│   ├── select_template(agent_type: str) → TemplatePath
│   └── load_template_config(template_path: str) → TemplateConfig
│
├── CapabilityMapper
│   ├── map_capabilities(capabilities: list[str]) → list[CapabilityModule]
│   ├── get_flow_definitions(capability: str) → FlowDefinition
│   └── get_intent_mappings(capability: str) → dict[str, list[str]]
│
├── ArtifactGenerator
│   ├── generate_spec(parsed_blueprint, template_config) → spec.md
│   ├── generate_flows(capability_modules) → flows/*.json
│   ├── generate_config(parsed_blueprint) → config/*.yaml
│   ├── generate_prompts(capability_modules) → prompts/*.txt
│   └── generate_build_spec() → AgentBuildSpec
│
├── IntegrationMapper
│   ├── map_integrations(channels, capabilities) → list[Integration]
│   ├── generate_n8n_manifest() → integrations/n8n_manifest.json
│   ├── generate_vapi_manifest() → integrations/vapi_manifest.json
│   └── generate_webhook_specs() → integrations/webhooks.json
│
└── AgentBuilderOrchestrator (punto de entrada principal)
    └── build_agent(order, plan, agent_blueprint) → AgentBuildSpec
```

### 3.2 Responsabilidades Detalladas

#### BlueprintParser
**Qué hace:** Toma el `AgentBlueprint` (JSON) y lo normaliza a una estructura interna consistente.

**Input:**
```json
{
  "version": "1.0",
  "agent_type": "whatsapp_autopilot",
  "product_type": "autopilot_whatsapp",
  "sources": [
    {"type": "website_url", "value": "https://cliente.com", "notes": null},
    {"type": "manual_input", "value": "Productos: X, Y, Z", "notes": "FAQ"}
  ],
  "channels": ["whatsapp", "webchat"],
  "capabilities": ["respuesta_inteligente", "ventas", "recordatorios"],
  "automation_level": "full",
  "client_profile": {"empresa": "ABC Corp", "industria": "retail"}
}
```

**Output (ParsedBlueprint):**
```python
ParsedBlueprint(
    agent_type="whatsapp_autopilot",
    product_type="autopilot_whatsapp",
    sources=[
        SourceSpec(type="website_url", url="https://cliente.com", notes=None),
        SourceSpec(type="manual_input", content="Productos: X, Y, Z", notes="FAQ")
    ],
    channels=[ChannelSpec(name="whatsapp"), ChannelSpec(name="webchat")],
    capabilities=["respuesta_inteligente", "ventas", "recordatorios"],
    automation_level=AutomationLevel.FULL,
    client_profile={"empresa": "ABC Corp", "industria": "retail"}
)
```

#### TemplateSelector
**Qué hace:** Selecciona la plantilla base según `agent_type`.

**Templates disponibles (propuestos):**
```
~/factory/templates/
├── whatsapp_autopilot/
│   ├── template_config.yaml
│   ├── base_structure/
│   └── default_flows/
├── marketing_autopilot/
│   ├── template_config.yaml
│   ├── base_structure/
│   └── default_flows/
└── webhook_service/
    ├── template_config.yaml
    └── base_structure/
```

**TemplateConfig ejemplo (whatsapp_autopilot):**
```yaml
template_name: whatsapp_autopilot
version: "1.0"
required_capabilities:
  - respuesta_inteligente
optional_capabilities:
  - ventas
  - recordatorios
  - soporte_tecnico
default_channels:
  - whatsapp
supported_integrations:
  - n8n
  - vapi
  - twilio_api
project_structure:
  - backend/
  - frontend/
  - flows/
  - config/
  - integrations/
```

#### CapabilityMapper
**Qué hace:** Traduce capabilities abstractas → módulos concretos con flujos e intents.

**Mapping propuesto:**

| Capability | Flow Definition | Intents | Config File |
|------------|----------------|---------|-------------|
| `respuesta_inteligente` | `flows/base_conversation.json` | `greeting`, `help`, `goodbye` | `config/base.yaml` |
| `ventas` | `flows/sales.json` | `product_inquiry`, `pricing`, `close_deal` | `config/sales.yaml` |
| `recordatorios` | `flows/reminders.json` | `set_reminder`, `list_reminders`, `cancel_reminder` | `config/reminders.yaml` |
| `soporte_tecnico` | `flows/support.json` | `technical_issue`, `escalate`, `faq` | `config/support.yaml` |

**FlowDefinition ejemplo (ventas):**
```json
{
  "flow_name": "sales",
  "description": "Flujo de ventas automatizado con IA",
  "intents": [
    {
      "name": "product_inquiry",
      "examples": ["¿Qué productos tienen?", "Quiero ver el catálogo"],
      "response_template": "prompts/sales_product_inquiry.txt"
    },
    {
      "name": "pricing",
      "examples": ["¿Cuánto cuesta?", "Precio de X producto"],
      "response_template": "prompts/sales_pricing.txt"
    }
  ],
  "nodes": [
    {"type": "entry", "id": "start"},
    {"type": "intent_classifier", "id": "classify"},
    {"type": "response_generator", "id": "respond"},
    {"type": "crm_integration", "id": "save_lead"}
  ]
}
```

#### ArtifactGenerator
**Qué hace:** Genera archivos concretos en el proyecto.

**Artefactos generados:**

1. **`/spec/agent_spec.md`** - Especificación completa del agente
```markdown
# Especificación del Agente: WhatsApp Autopilot

## Tipo de Agente
whatsapp_autopilot

## Canales Activos
- WhatsApp Business API
- WebChat (opcional)

## Capabilities Implementadas
### 1. Respuesta Inteligente
- Contexto: Información de https://cliente.com
- Modelo: GPT-4 (via VAPI)
- Fallback: Operador humano si confianza < 0.7

### 2. Ventas
- Flujo: Consulta → Oferta → Cierre
- Integración CRM: HubSpot API
- Recordatorios automáticos de seguimiento

### 3. Recordatorios
- Sistema: n8n workflow scheduler
- Persistencia: PostgreSQL
- Notificaciones: WhatsApp + Email
```

2. **`/flows/*.json`** - Flujos de conversación
```
flows/
├── base_conversation.json
├── sales.json
└── reminders.json
```

3. **`/config/*.yaml`** - Configuraciones por módulo
```
config/
├── base.yaml
├── sales.yaml
├── reminders.yaml
└── integrations.yaml
```

4. **`/prompts/*.txt`** - Prompts base
```
prompts/
├── system_prompt.txt
├── sales_product_inquiry.txt
├── sales_pricing.txt
└── reminder_confirmation.txt
```

5. **`/integrations/*.json`** - Manifests de integraciones
```
integrations/
├── n8n_manifest.json
├── vapi_manifest.json
└── webhooks.json
```

#### IntegrationMapper
**Qué hace:** Prepara los manifests de integraciones externas.

**n8n_manifest.json ejemplo:**
```json
{
  "workflows": [
    {
      "name": "whatsapp_reminder_scheduler",
      "description": "Programa recordatorios vía WhatsApp",
      "trigger": {
        "type": "webhook",
        "endpoint": "/api/reminders/schedule"
      },
      "nodes": [
        {
          "type": "schedule",
          "cron": "user_defined"
        },
        {
          "type": "whatsapp_send",
          "api": "twilio"
        }
      ]
    },
    {
      "name": "crm_lead_sync",
      "description": "Sincroniza leads con HubSpot",
      "trigger": {
        "type": "webhook",
        "endpoint": "/api/leads/new"
      },
      "nodes": [
        {
          "type": "hubspot_create_contact"
        }
      ]
    }
  ]
}
```

**vapi_manifest.json ejemplo:**
```json
{
  "assistant_config": {
    "name": "WhatsApp Sales Bot",
    "voice_model": "eleven_labs_es",
    "llm_model": "gpt-4",
    "system_prompt_path": "prompts/system_prompt.txt"
  },
  "phone_numbers": [
    {
      "provider": "twilio",
      "number": "+52XXXXXXXXXX",
      "capabilities": ["sms", "voice", "whatsapp"]
    }
  ],
  "webhooks": [
    {
      "event": "call_started",
      "url": "https://cliente.com/api/webhooks/vapi/call-started"
    },
    {
      "event": "call_ended",
      "url": "https://cliente.com/api/webhooks/vapi/call-ended"
    }
  ]
}
```

---

## 4. Contratos de Datos Propuestos

### 4.1 AgentBuildSpec

**Descripción:** Estructura intermedia que unifica toda la información necesaria para construir el agente.

**Pseudo-Pydantic:**
```python
class AgentBuildSpec(BaseModel):
    """
    Especificación completa de construcción de un agente.
    Se deriva de: AgentBlueprint + Plan + Template seleccionado.
    """
    
    # Identificación
    order_number: str
    agent_type: str  # whatsapp_autopilot, marketing_autopilot, etc.
    product_type: str
    
    # Template seleccionado
    template_name: str
    template_version: str
    
    # Fuentes de información
    sources: list[SourceSpec]
    
    # Canales activos
    channels: list[ChannelSpec]
    
    # Capabilities con sus módulos
    capability_modules: list[CapabilityModule]
    
    # Integraciones a configurar
    integrations: list[IntegrationSpec]
    
    # Artefactos generados
    artifacts: ArtifactBundle
    
    # Metadata
    automation_level: AutomationLevel  # manual, semi, full
    client_profile: dict
    generated_at: datetime
    agent_builder_version: str = "1.0.0"
```

### 4.2 CapabilityModule

**Descripción:** Representa un módulo funcional del agente (ventas, recordatorios, etc.).

```python
class CapabilityModule(BaseModel):
    """
    Módulo funcional de una capability (ej: ventas, recordatorios).
    """
    name: str  # "ventas", "recordatorios", etc.
    flow_definition: FlowDefinition
    intents: list[Intent]
    prompts: list[PromptFile]
    config: dict  # config específica del módulo
    dependencies: list[str]  # ["database", "crm_integration"]
```

### 4.3 FlowDefinition

**Descripción:** Define un flujo de conversación/automatización.

```python
class FlowDefinition(BaseModel):
    """
    Definición de un flujo de conversación o automatización.
    """
    flow_name: str
    description: str
    intents: list[Intent]
    nodes: list[FlowNode]
    transitions: list[Transition]
    fallback_behavior: FallbackConfig
```

### 4.4 IntegrationSpec

**Descripción:** Especificación de una integración externa.

```python
class IntegrationSpec(BaseModel):
    """
    Especificación de integración con servicio externo.
    """
    integration_type: str  # "n8n", "vapi", "hubspot", "twilio"
    provider: str  # "n8n", "vapi", "hubspot_api"
    required_credentials: list[str]  # ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"]
    manifest_path: str  # "integrations/n8n_manifest.json"
    webhook_endpoints: list[WebhookEndpoint]
    status: str  # "configured", "pending_activation"
```

### 4.5 ArtifactBundle

**Descripción:** Todos los artefactos generados por Agent Builder.

```python
class ArtifactBundle(BaseModel):
    """
    Bundle de todos los artefactos generados.
    """
    spec_file: str  # "spec/agent_spec.md"
    flow_files: list[str]  # ["flows/sales.json", "flows/reminders.json"]
    config_files: list[str]  # ["config/base.yaml", "config/sales.yaml"]
    prompt_files: list[str]  # ["prompts/system_prompt.txt", ...]
    integration_manifests: list[str]  # ["integrations/n8n_manifest.json"]
    total_artifacts: int
    generated_at: datetime
```

---

## 5. Flujo Detallado: whatsapp_autopilot

### Caso de Uso: Cliente solicita WhatsApp Autopilot con ventas y recordatorios

**Input recibido en Axon 88:**
```json
{
  "order": {
    "order_number": "ORD-2025-020",
    "tipo_producto": "autopilot_whatsapp",
    "nombre_producto": "WhatsApp Bot Tienda ABC",
    "datos_cliente": {
      "empresa": "Tienda ABC",
      "industria": "retail",
      "whatsapp_number": "+52XXXXXXXXXX"
    }
  },
  "plan": {
    "descripcion": "WhatsApp autopilot con ventas y recordatorios",
    "modulos": ["backend_fastapi", "frontend_nextjs", "db_postgresql"]
  },
  "agent_blueprint": {
    "version": "1.0",
    "agent_type": "whatsapp_autopilot",
    "product_type": "autopilot_whatsapp",
    "sources": [
      {"type": "website_url", "value": "https://tiendaabc.com", "notes": "Catálogo"},
      {"type": "manual_input", "value": "FAQ: Horarios, envíos, devoluciones", "notes": null}
    ],
    "channels": ["whatsapp"],
    "capabilities": ["respuesta_inteligente", "ventas", "recordatorios"],
    "automation_level": "full",
    "client_profile": {"empresa": "Tienda ABC", "industria": "retail"}
  }
}
```

### Paso a Paso: Agent Builder Execution

#### PASO 1: BlueprintParser.parse_blueprint()
```
Input: agent_blueprint (JSON)

Acciones:
1. Validar estructura del blueprint
2. Normalizar sources:
   - website_url → SourceSpec(type="web", url="https://tiendaabc.com")
   - manual_input → SourceSpec(type="manual", content="FAQ: Horarios...")
3. Normalizar channels:
   - "whatsapp" → ChannelSpec(name="whatsapp", provider="twilio")
4. Normalizar capabilities:
   - ["respuesta_inteligente", "ventas", "recordatorios"] → list[str]

Output: ParsedBlueprint
```

#### PASO 2: TemplateSelector.select_template("whatsapp_autopilot")
```
Input: agent_type = "whatsapp_autopilot"

Acciones:
1. Buscar template en ~/factory/templates/whatsapp_autopilot/
2. Cargar template_config.yaml
3. Verificar required_capabilities vs capabilities del blueprint
4. Retornar TemplateConfig

Output: TemplateConfig(
    template_name="whatsapp_autopilot",
    version="1.0",
    required_capabilities=["respuesta_inteligente"],
    optional_capabilities=["ventas", "recordatorios", "soporte_tecnico"],
    default_integrations=["n8n", "vapi", "twilio_api"]
)
```

#### PASO 3: CapabilityMapper.map_capabilities()
```
Input: capabilities = ["respuesta_inteligente", "ventas", "recordatorios"]

Acciones:
Para cada capability, generar CapabilityModule:

1. respuesta_inteligente:
   - Flow: flows/base_conversation.json
   - Intents: greeting, help, goodbye, general_inquiry
   - Prompts: system_prompt.txt, general_response.txt
   - Config: config/base.yaml

2. ventas:
   - Flow: flows/sales.json
   - Intents: product_inquiry, pricing, close_deal, check_availability
   - Prompts: sales_product_inquiry.txt, sales_pricing.txt, sales_close.txt
   - Config: config/sales.yaml
   - Dependencies: ["crm_integration"]

3. recordatorios:
   - Flow: flows/reminders.json
   - Intents: set_reminder, list_reminders, cancel_reminder
   - Prompts: reminder_confirmation.txt, reminder_list.txt
   - Config: config/reminders.yaml
   - Dependencies: ["n8n_integration", "database"]

Output: list[CapabilityModule] con 3 módulos
```

#### PASO 4: ArtifactGenerator.generate_all()
```
Input: ParsedBlueprint, TemplateConfig, list[CapabilityModule]

Acciones:
1. Generar /spec/agent_spec.md:
   - Descripción completa del agente
   - Capabilities implementadas
   - Fuentes de información
   - Canales activos
   - Integraciones requeridas

2. Generar /flows/*.json:
   - flows/base_conversation.json (from capability respuesta_inteligente)
   - flows/sales.json (from capability ventas)
   - flows/reminders.json (from capability recordatorios)

3. Generar /config/*.yaml:
   - config/base.yaml (configuración global)
   - config/sales.yaml (config de ventas)
   - config/reminders.yaml (config de recordatorios)

4. Generar /prompts/*.txt:
   - prompts/system_prompt.txt (prompt base del agente)
   - prompts/sales_product_inquiry.txt
   - prompts/sales_pricing.txt
   - prompts/reminder_confirmation.txt

Output: ArtifactBundle con todos los paths
```

#### PASO 5: IntegrationMapper.map_integrations()
```
Input: channels=["whatsapp"], capabilities=["ventas", "recordatorios"]

Acciones:
1. Identificar integraciones necesarias:
   - whatsapp → Twilio API
   - ventas → HubSpot CRM (opcional), VAPI (LLM)
   - recordatorios → n8n (scheduler)

2. Generar integrations/n8n_manifest.json:
   {
     "workflows": [
       {
         "name": "whatsapp_reminder_scheduler",
         "trigger": {"type": "webhook"},
         "nodes": [{"type": "schedule"}, {"type": "whatsapp_send"}]
       }
     ]
   }

3. Generar integrations/vapi_manifest.json:
   {
     "assistant_config": {
       "name": "Tienda ABC WhatsApp Bot",
       "llm_model": "gpt-4",
       "system_prompt_path": "prompts/system_prompt.txt"
     },
     "phone_numbers": [{
       "provider": "twilio",
       "number": "+52XXXXXXXXXX"
     }]
   }

4. Generar integrations/webhooks.json:
   [
     {"path": "/api/webhooks/whatsapp/message", "method": "POST"},
     {"path": "/api/webhooks/vapi/call-ended", "method": "POST"}
   ]

Output: list[IntegrationSpec]
```

#### PASO 6: AgentBuilderOrchestrator.generate_build_spec()
```
Input: Todos los outputs anteriores

Acciones:
1. Unificar todo en AgentBuildSpec
2. Escribir archivo intermedio: /tmp/build_spec_ORD-2025-020.json
3. Retornar AgentBuildSpec completo

Output: AgentBuildSpec
{
  "order_number": "ORD-2025-020",
  "agent_type": "whatsapp_autopilot",
  "product_type": "autopilot_whatsapp",
  "template_name": "whatsapp_autopilot",
  "sources": [...],
  "channels": [...],
  "capability_modules": [
    { "name": "respuesta_inteligente", "flow_definition": {...} },
    { "name": "ventas", "flow_definition": {...} },
    { "name": "recordatorios", "flow_definition": {...} }
  ],
  "integrations": [
    { "integration_type": "twilio", ... },
    { "integration_type": "n8n", ... },
    { "integration_type": "vapi", ... }
  ],
  "artifacts": {
    "spec_file": "spec/agent_spec.md",
    "flow_files": ["flows/base_conversation.json", "flows/sales.json", ...],
    "config_files": [...],
    "prompt_files": [...],
    "integration_manifests": [...]
  },
  "generated_at": "2025-11-16T20:30:00",
  "agent_builder_version": "1.0.0"
}
```

### PASO 7: Entrega a Builder v1

Agent Builder genera artefactos en directorio temporal:
```
/tmp/agent_build_ORD-2025-020/
├── spec/
│   └── agent_spec.md
├── flows/
│   ├── base_conversation.json
│   ├── sales.json
│   └── reminders.json
├── config/
│   ├── base.yaml
│   ├── sales.yaml
│   └── reminders.yaml
├── prompts/
│   ├── system_prompt.txt
│   ├── sales_product_inquiry.txt
│   └── reminder_confirmation.txt
└── integrations/
    ├── n8n_manifest.json
    ├── vapi_manifest.json
    └── webhooks.json
```

**Builder v1 recibe:**
- `order` (original)
- `plan` (original)
- `agent_build_spec` (generado por Agent Builder)
- `artifacts_path` = `/tmp/agent_build_ORD-2025-020/`

**Builder v1 construye:**
```
~/factory/products/ORD-2025-020_autopilot_whatsapp/
├── backend/
│   ├── app/
│   │   ├── flows/         # ← Copiado de artifacts_path/flows/
│   │   ├── config/        # ← Copiado de artifacts_path/config/
│   │   ├── prompts/       # ← Copiado de artifacts_path/prompts/
│   │   ├── integrations/  # ← Copiado de artifacts_path/integrations/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── ... (Next.js app con dashboard)
├── spec/
│   └── agent_spec.md      # ← Copiado de artifacts_path/spec/
└── order.json
```

---

## 6. Conexión con Pipeline Actual

### ¿Cuándo se ejecuta Agent Builder?

**Opción A (Propuesta): Dentro de /factory/build-local**
```python
# En axon88/factory/builder.py

async def build_local(order, plan, agent_blueprint=None):
    """
    Endpoint principal de construcción.
    """
    
    # ✨ NUEVO: Si hay agent_blueprint, ejecutar Agent Builder primero
    agent_build_spec = None
    artifacts_path = None
    
    if agent_blueprint:
        print("[Agent Builder] Procesando blueprint...")
        from agent_builder import AgentBuilderOrchestrator
        
        orchestrator = AgentBuilderOrchestrator()
        agent_build_spec = orchestrator.build_agent(
            order=order,
            plan=plan,
            agent_blueprint=agent_blueprint
        )
        
        artifacts_path = agent_build_spec.artifacts.base_path
        print(f"[Agent Builder] Artefactos generados en: {artifacts_path}")
    
    # Builder v1 (con o sin agent_build_spec)
    product_path = builder_v1.build(
        order=order,
        plan=plan,
        agent_build_spec=agent_build_spec,  # None si no hay blueprint
        artifacts_path=artifacts_path
    )
    
    # Builder v2 (QA + Deliverable)
    qa_result = builder_v2.run_qa_and_package(product_path)
    
    return {
        "success": True,
        "product_path": product_path,
        "qa": qa_result.qa,
        "deliverable_metadata": qa_result.deliverable_metadata
    }
```

**Opción B (Alternativa): Pipeline separado**
```
Agent Builder → genera artefactos
    ↓
Builder v1 → construye proyecto usando artefactos
    ↓
Builder v2 → QA + deliverable
```

**Decisión recomendada:** Opción A (integrado en /factory/build-local) para mantener compatibilidad backward.

### Impacto en deliverable_metadata

**Campos nuevos en deliverable_metadata (propuesto):**
```json
{
  "order_number": "ORD-2025-020",
  "tipo_producto": "autopilot_whatsapp",
  "qa_status": "ok",
  "construido_en": "2025-11-16T20:35:00",
  
  "agent_builder": {
    "executed": true,
    "version": "1.0.0",
    "agent_type": "whatsapp_autopilot",
    "capabilities": ["respuesta_inteligente", "ventas", "recordatorios"],
    "channels": ["whatsapp"],
    "integrations": [
      {"type": "twilio", "status": "configured"},
      {"type": "n8n", "status": "pending_activation"},
      {"type": "vapi", "status": "configured"}
    ],
    "artifacts": {
      "flows": 3,
      "prompts": 5,
      "config_files": 3,
      "integration_manifests": 3
    }
  }
}
```

**Beneficio para Replit:**
- Dashboard puede mostrar: "Este agente tiene 3 flujos activos, 3 integraciones configuradas"
- Cliente ve: "Tu WhatsApp Bot incluye: Ventas automatizadas + Recordatorios programados"

---

## 7. Riesgos y Límites

### Riesgos Identificados

1. **Complejidad de Mantenimiento**
   - Cada nuevo `agent_type` requiere template completo
   - Mapeo de capabilities puede volverse inconsistente
   - **Mitigación:** Documentar templates claramente, versionarlos

2. **Dependencia de Templates**
   - Si template no existe para un agent_type, Agent Builder falla
   - **Mitigación:** Template genérico de fallback

3. **Drift entre Blueprint y Artefactos Generados**
   - Blueprint dice "ventas" pero artefactos no coinciden
   - **Mitigación:** QA valida presencia de artefactos declarados

4. **Integraciones Externas No Disponibles**
   - Blueprint requiere HubSpot pero cliente no tiene cuenta
   - **Mitigación:** Marcar integraciones como "pending_activation", no fallar

### Límites del Diseño Actual

**Lo que Agent Builder SÍ hace:**
- Genera estructura de proyecto coherente
- Mapea capabilities → módulos concretos
- Prepara manifests de integraciones
- Garantiza consistencia entre agentes del mismo tipo

**Lo que Agent Builder NO hace (todavía):**
- NO ejecuta integraciones (n8n workflows, VAPI setup)
- NO scrappea websites automáticamente
- NO entrena modelos custom
- NO valida que cliente tenga credenciales de APIs

**Por implementar en futuras fases:**
- Auto-activation de integraciones (n8n workflows via API)
- Web scraping automático de `sources.website_url`
- Training de knowledge base con `sources.manual_input`
- Validación de credenciales antes de build

---

## 8. Preguntas Abiertas

1. **¿Cómo versionar templates?**
   - Propuesta: `whatsapp_autopilot_v1.0/`, `whatsapp_autopilot_v1.1/`
   - Permitir que orden especifique versión de template

2. **¿Cómo manejar capabilities custom no mapeadas?**
   - Opción A: Fallar y pedir que se agregue mapping
   - Opción B: Generar módulo genérico con prompt base
   - **Decisión pendiente**

3. **¿Agent Builder debe validar viabilidad técnica?**
   - Ej: Cliente pide "ventas" pero no proporciona catálogo de productos
   - Opción A: Validar y fallar temprano
   - Opción B: Generar placeholder y marcar como "requiere configuración"
   - **Decisión pendiente**

4. **¿Cómo integrar conocimiento de `sources`?**
   - Website scraping: ¿Agent Builder o proceso separado?
   - RAG ingestion: ¿Builder o post-deployment?
   - **Decisión pendiente**

---

## 9. Próximos Pasos (Para Fase de BUILD)

### Fase de Implementación (FASE 4.C - futuro)

1. **Implementar BlueprintParser**
   - Archivo: `~/factory/agent_builder/blueprint_parser.py`
   - Tests: Validar normalización de sources, channels, capabilities

2. **Crear Templates Base**
   - Template: `whatsapp_autopilot_v1.0/`
   - Template: `marketing_autopilot_v1.0/`

3. **Implementar CapabilityMapper**
   - Archivo: `~/factory/agent_builder/capability_mapper.py`
   - Mapping: capabilities → FlowDefinition + Intents

4. **Implementar ArtifactGenerator**
   - Generar archivos reales en /tmp/
   - Validar estructura de artefactos

5. **Integrar con Builder v1**
   - Modificar `/factory/build-local` para invocar Agent Builder
   - Pasar `agent_build_spec` a Builder v1

6. **Testing End-to-End**
   - Orden completa: Replit → Agent Builder → Builder v1 → Builder v2
   - Validar QA incluye validación de artefactos generados

7. **Actualizar Replit**
   - Mostrar metadata de Agent Builder en dashboard
   - Campos: capabilities activas, integraciones configuradas

---

## 10. Conclusión

**Agent Builder** es la clave para pasar de una fábrica genérica a una **fábrica de agentes inteligentes**.

Con este diseño:
- ✅ Blueprint define CLARAMENTE qué construir
- ✅ Agent Builder traduce blueprint → artefactos concretos
- ✅ Builder v1/v2 siguen funcionando sin cambios
- ✅ Cada agente del mismo tipo es consistente
- ✅ Integraciones quedan documentadas y listas para activar

**Filosofía cumplida:**
- No vendemos chatbots - Vendemos SISTEMAS completos
- Cada agente tiene flujos, integraciones, configs bien definidos
- Escalable: agregar nuevo `agent_type` = crear template + mappings

**Estado actual:** 📋 Diseño completo - Listo para implementación en BUILD

---

**Autor:** AXON Agency Team  
**Versión:** 1.0.0  
**Fecha:** Noviembre 16, 2025
