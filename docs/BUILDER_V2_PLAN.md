# Builder v2 Integration Plan - AXON Agency

**Status:** ✅ Implemented  
**Last Updated:** 2025-11-16

---

## Overview

Builder v2 extends the original Axon 88 Builder with automated QA validation and deliverable generation, creating a complete end-to-end construction pipeline with quality assurance.

---

## Architecture

### Integration Points

**Replit (AXON Agency):**
- Orders API - Manages order lifecycle
- Orders Orchestrator - Generates production plans via LLM
- Axon Factory Client - HTTP client to Axon 88
- BAU Service - Build Automation Unit for automatic processing

**Axon 88 (Local Factory - Jetson Orin Nano):**
- Builder v1 - Product construction
- Builder v2 - QA validation + deliverable packaging
- Cloudflare Tunnel - Secure HTTP access from Replit

---

## Request/Response Contract

### POST `/factory/build-local`

**Request Payload:**
```json
{
  "order": {
    "order_id": "uuid",
    "order_number": "ORD-2025-001",
    "tipo_producto": "autopilot_whatsapp",
    "nombre_producto": "WhatsApp Sales Bot",
    "datos_cliente": {...},
    "prioridad": "alta"
  },
  "plan": {
    "tipo_autopilot": "autopilot_whatsapp",
    "resumen": "...",
    "fases": [...],
    "stack_tecnologico": {...},
    "estimacion_total_horas": 15
  },
  "agent_blueprint": {  // OPTIONAL (FASE 3.B) - only if exists in Order
    "version": "1.0",
    "agent_type": "whatsapp_sales",
    "product_type": "whatsapp_autopilot",
    "sources": [
      {"type": "website", "value": "https://client.com", "notes": "Product catalog"},
      {"type": "instagram", "value": "@client", "notes": "Social media"}
    ],
    "channels": ["whatsapp"],
    "capabilities": ["ventas", "soporte", "consultas", "faq"],
    "automation_level": "semi",
    "client_profile": {
      "empresa": "Client Corp",
      "industria": "ecommerce"
    },
    "notes": "Custom configuration notes"
  }
}
```

**Response (Builder v2):**
```json
{
  "success": true,
  "error": null,
  "product_path": "/home/axon88/factory/products/ORD-2025-001_autopilot_whatsapp",
  "log_path": "/home/axon88/factory/logs/orders.log",
  "construido_en": "2025-11-15T01:56:31.106933",
  "deliverable_dir": "/home/axon88/factory/deliverables/ORD-2025-001_autopilot_whatsapp",
  "zip_path": "/home/axon88/factory/deliverables/ORD-2025-001_autopilot_whatsapp/ORD-2025-001_autopilot_whatsapp.zip",
  "qa": {
    "status": "ok",  // ok | warn | fail
    "messages": [
      "✓ All required files present",
      "✓ No security issues detected",
      "✓ Dependencies validated"
    ],
    "checked_files": [
      "main.py",
      "requirements.txt",
      "Dockerfile"
    ]
  }
}
```

---

## AgentBlueprint Integration (FASE 3.B)

**Implemented:** 2025-11-16  
**Status:** ✅ Active

### Purpose

Replit now sends an optional `agent_blueprint` field in build requests to Axon 88. This blueprint contains complete agent specifications (sources, channels, capabilities) to eliminate ambiguities during construction.

### Payload Extension

The `agent_blueprint` field is:
- **Optional** - Only included when present in Order (generated from catalog)
- **Backward Compatible** - Orders without blueprint (null) don't include the field
- **Ignored by Axon 88** (initially) - Field is prepared for future builder enhancements

### Implementation Details

**Client Side (Replit):**
```python
# axon_factory_client.py
async def build_product(
    order: Order, 
    plan: dict,
    agent_blueprint: Optional[dict] = None  # ← NEW
):
    payload = {"order": {...}, "plan": {...}}
    
    if agent_blueprint:
        payload["agent_blueprint"] = agent_blueprint
        logger.info(f"📋 AgentBlueprint included - type={agent_blueprint['agent_type']}")
```

**Orchestrator Integration:**
```python
# orders_orchestrator.py
build_result = await self.axon_factory_client.build_product(
    order, 
    plan,
    agent_blueprint=order.agent_blueprint  # ← Pass if exists
)
```

### Backward Compatibility Guarantees

1. **Old Orders** - Orders created before FASE 3.A have `agent_blueprint=null`, field not sent
2. **Axon 88 Tolerance** - Builder can ignore extra field without errors
3. **Response Contract** - No changes to expected response format
4. **State Flow** - Order states (nuevo → planificacion → construccion) unchanged

### Future Usage (Cursor/Axon 88)

The blueprint will enable:
- Automated source scraping (website, social media)
- Pre-configured channel integrations (WhatsApp API, webhooks)
- Capability-driven code generation
- Client-specific customizations

---

## QA Status Flow

The `qa.status` field determines automatic order progression:

- **`ok`** → Order automatically marked as `listo` (ready for delivery)
- **`warn`** → Order marked as `qa` (requires manual review)
- **`fail`** → Order marked as `qa` (critical issues, manual review required)
- **`null`** → Builder v1 only (no QA executed)

---

## Deliverable Package Structure

Builder v2 generates a complete deliverable package:

```
/deliverables/ORD-2025-001_autopilot_whatsapp/
├── SUMMARY.md           # Human-readable summary
├── meta.json            # Machine-readable metadata
└── ORD-2025-001_autopilot_whatsapp.zip  # Complete product archive
```

**Metadata Example (`meta.json`):**
```json
{
  "order_number": "ORD-2025-001",
  "tipo_producto": "autopilot_whatsapp",
  "qa_status": "ok",
  "construido_en": "2025-11-15T01:56:31.106933",
  "archivos": ["SUMMARY.md", "meta.json", "ORD-2025-001_autopilot_whatsapp.zip"]
}
```

---

## Database Schema Changes

### New Fields (Order Model)

**QA Fields:**
- `qa_status: Optional[str]` - ok, warn, fail
- `qa_messages: Optional[List[str]]` - QA check messages
- `qa_checked_files: Optional[List[str]]` - Validated files
- `qa_ejecutado_en: Optional[datetime]` - QA execution timestamp
- `qa_iniciada_at: Optional[datetime]` - QA start timestamp

**Deliverable Fields:**
- `deliverable_generado: bool = False` - Deliverable package created
- `deliverable_metadata: Optional[dict]` - Package metadata (paths, files)
- `deliverable_generado_en: Optional[datetime]` - Generation timestamp

**AgentBlueprint Field (FASE 3.A):**
- `agent_blueprint: Optional[dict]` - Complete agent specification

---

## API Endpoints

### GET `/api/factory/orders/{order_id}/qa`

Returns QA status for an order.

**Response:**
```json
{
  "order_id": "uuid",
  "order_number": "ORD-2025-001",
  "qa_executed": true,
  "qa_status": "ok",
  "qa_messages": ["✓ All checks passed"],
  "qa_checked_files": ["main.py", "requirements.txt"],
  "qa_ejecutado_en": "2025-11-15T01:56:31.106933"
}
```

### GET `/api/factory/orders/{order_id}/deliverable`

Returns deliverable information.

**Response:**
```json
{
  "order_id": "uuid",
  "order_number": "ORD-2025-001",
  "deliverable_generado": true,
  "deliverable_metadata": {
    "order_number": "ORD-2025-001",
    "tipo_producto": "autopilot_whatsapp",
    "qa_status": "ok",
    "archivos": ["SUMMARY.md", "meta.json", "ORD-2025-001.zip"]
  },
  "deliverable_generado_en": "2025-11-15T01:56:31.106933"
}
```

**Note:** Internal Axon 88 paths are NOT exposed to prevent security issues.

---

## Security Hardening (BAU v1)

**Issue:** Error messages exposed internal Axon 88 paths  
**Fix:** Sanitize all error messages before persisting to Order.logs

**Before:**
```
"Fallo al delegar construcción: HTTP 400: /home/axon88/factory/products/..."
```

**After:**
```
"Fallo al delegar construcción: HTTP 400: [sanitized error]"
```

---

## Testing

### Manual Test Flow

1. Create order from catalog (generates AgentBlueprint automatically)
2. Execute BAU tick: `POST /api/factory/bau-tick`
3. Verify order progression: `nuevo` → `planificacion` → `construccion` → `listo`
4. Check QA: `GET /api/factory/orders/{id}/qa`
5. Check Deliverable: `GET /api/factory/orders/{id}/deliverable`
6. Verify logs show AgentBlueprint included (if present)

### Backward Compatibility Test

1. Create order directly: `POST /api/orders` (no blueprint)
2. Execute BAU tick
3. Verify order processes normally without blueprint field
4. Confirm no errors in Axon 88 logs

---

## Configuration

**Environment Variables (Replit):**
```bash
AXON_CORE_ENABLED=true
AXON_CORE_API_BASE=https://api-axon88.algorithmicsai.com
AXON_CORE_API_TOKEN=<cloudflare-tunnel-token>
```

**Cloudflare Tunnel (Axon 88):**
```bash
cloudflared tunnel run axon88-factory
```

---

## Monitoring

**Successful Build Logs (Replit):**
```
INFO: Requesting build in Axon 88 - order=ORD-2025-001
INFO: 📋 AgentBlueprint included - type=whatsapp_sales, version=1.0
INFO: Axon 88 build response - status=200, order=ORD-2025-001
INFO: ✅ ORD-2025-001 → QA passed, marked as 'listo'
INFO: 📦 ORD-2025-001 → Deliverable generated
```

**Axon 88 Build Logs:**
```
INFO: POST /factory/build-local - order=ORD-2025-001
INFO: Builder v2 - QA execution started
INFO: Builder v2 - QA status: ok
INFO: Builder v2 - Deliverable packaging complete
```

---

## Future Enhancements

- [ ] Implement blueprint scraping in Axon 88 (FASE 3.C+)
- [ ] Automated source ingestion (website, social media)
- [ ] RAG integration for client-specific context
- [ ] Real-time build progress streaming via WebSocket
- [ ] Automated deployment post-QA
- [ ] Client notification system (email, Slack)

---

## References

- Order Model: `axon-agency/apps/api/app/models/orders.py`
- Axon Factory Client: `axon-agency/apps/api/app/services/axon_factory_client.py`
- Orders Orchestrator: `axon-agency/apps/api/app/services/orders_orchestrator.py`
- BAU Service: `axon-agency/apps/api/app/services/bau_service.py`
- AgentBlueprint Service: `axon-agency/apps/api/app/services/agent_blueprint_service.py`
