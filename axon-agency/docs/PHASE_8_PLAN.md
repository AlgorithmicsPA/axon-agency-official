# PHASE 8: Demo Tenants + Portal Polish

**Status:** IMPLEMENTATION IN PROGRESS  
**Start Date:** Nov 17, 2025  
**Objective:** Create realistic demo data and polish client portal UX without breaking changes

---

## 1. Demo Tenants

### 1.1 Tenant Profiles

#### Tenant 1: Algorithmics AI Academy
- **Name:** Algorithmics AI Academy
- **Slug:** `algorithmics-academy`
- **Type:** `school`
- **Industry:** Education Technology
- **Description:** Academia de programación e IA para niños y jóvenes
- **Contact:** academy@algorithmics.ai
- **Use Case:** Necesitan automatización de marketing educativo y contenido SEO para atraer nuevos estudiantes

#### Tenant 2: Notaría 17
- **Name:** Notaría 17
- **Slug:** `notaria-17`
- **Type:** `notary`
- **Industry:** Legal Services
- **Description:** Notaría pública especializada en trámites digitales
- **Contact:** contacto@notaria17.mx
- **Use Case:** Requieren automatización de WhatsApp para consultas legales y landing pages para servicios notariales

#### Tenant 3: BeeSmart Delivery
- **Name:** BeeSmart Delivery
- **Slug:** `beesmart-delivery`
- **Type:** `delivery`
- **Industry:** Logistics & E-commerce
- **Description:** Servicio de mensajería urbana rápida
- **Contact:** soporte@beesmart.delivery
- **Use Case:** Necesitan sistema de atención al cliente via WhatsApp y herramientas de QA para su app móvil

---

## 2. Demo Orders per Tenant

### 2.1 Algorithmics AI Academy Orders

| Agent | Product Name | Estado | Prioridad | Razón de Negocio |
|-------|-------------|--------|-----------|------------------|
| `content-generator` | Generador de Artículos SEO | `listo` | `alta` | Blog educativo con contenido optimizado para keywords como "cursos programación niños", "IA educativa" |
| `marketing-autopilot` | Autopilot Redes Sociales | `construccion` | `alta` | Automatizar posts en Instagram/Facebook con contenido de clases y testimonios |
| `landing-builder` | Landing Page Inscripciones | `nuevo` | `media` | Landing page para campaña de verano 2025 con formulario de registro |

### 2.2 Notaría 17 Orders

| Agent | Product Name | Estado | Prioridad | Razón de Negocio |
|-------|-------------|--------|-----------|------------------|
| `whatsapp-autopilot` | WhatsApp Consultas Legales | `listo` | `alta` | Automatizar respuestas a consultas frecuentes (costos, requisitos, horarios) |
| `landing-builder` | Landing Testamentos Digitales | `construccion` | `alta` | Landing page especializada en testamentos online con CTA conversión |
| `web-cloner` | Renovación Portal Notarial | `planificacion` | `media` | Clonar y mejorar sitio actual con mejor UX y trámites digitales |

### 2.3 BeeSmart Delivery Orders

| Agent | Product Name | Estado | Prioridad | Razón de Negocio |
|-------|-------------|--------|-----------|------------------|
| `whatsapp-autopilot` | WhatsApp Soporte Clientes | `listo` | `alta` | Bot para rastreo de paquetes, consultas de tarifas, soporte 24/7 |
| `qa-automator` | QA App Móvil Delivery | `construccion` | `alta` | Testing automatizado de flujos críticos (pedido, pago, tracking) |
| `marketing-autopilot` | Marketing Digital Promociones | `nuevo` | `media` | Campañas automatizadas para promociones flash y descuentos por zona |

---

## 3. Portal UX Improvements

### 3.1 Welcome Header
**Location:** `/portal/[tenantSlug]` main page

**Current:** Generic dashboard  
**New:** Personalized welcome
```
Bienvenido al Portal de [TenantName]
Aquí puedes ver tus agentes configurados, órdenes en proceso y entregables listos.
```

### 3.2 Empty States

#### No Orders Yet
```
🤖 Todavía no hay órdenes

Cuando creemos tu primer agente, aparecerá aquí con su progreso en tiempo real.
```

#### Order in Progress
```
🚧 Construcción en Proceso

Tu agente está siendo construido por nuestro equipo. Recibirás notificaciones cuando esté listo para pruebas.
```

#### Order Ready
```
✅ Entregable Disponible

Tu agente está listo. Puedes descargarlo y comenzar a usarlo de inmediato.
```

### 3.3 Text Improvements

**Avoid Technical Jargon:**
- ❌ "Order ID: ORD-12345"
- ✅ "Orden #12345"

- ❌ "Estado: PLANIFICACION"
- ✅ "En planificación"

- ❌ "Progreso: 45%"
- ✅ "Avance: 45% completado"

**Non-Technical Language:**
- ❌ "AgentBlueprint generated successfully"
- ✅ "Especificaciones técnicas generadas"

- ❌ "Build artifacts available at /deliverables/..."
- ✅ "Tu agente está listo para descargar"

### 3.4 Security & Privacy

**NO EXPONER:**
- ❌ Internal IDs (tenant_id, user_id)
- ❌ Filesystem paths (/home/axon/deliverables/...)
- ❌ Raw JSON objects
- ❌ Internal status codes

**SÍ MOSTRAR:**
- ✅ Order number (ORD-12345)
- ✅ Human-readable status ("En construcción")
- ✅ Public download URLs
- ✅ Formatted JSON cuando sea necesario

---

## 4. Implementation Plan

### 4.1 Backend: Seed Endpoint

**Endpoint:** `POST /api/admin/seed-demo`

**Features:**
- ✅ Admin-only (uses `require_admin()` helper)
- ✅ Idempotent (check if tenant exists by slug before creating)
- ✅ Creates tenants with realistic data
- ✅ Creates orders using existing catalog agents
- ✅ Reuses `create_order()` logic from `/api/catalog/orders`
- ✅ Sets correct `tenant_id` in all orders
- ✅ Generates `agent_blueprint` for catalog orders

**Response:**
```json
{
  "success": true,
  "message": "Demo data created successfully",
  "tenants_created": 3,
  "orders_created": 9,
  "tenants": [
    {"slug": "algorithmics-academy", "orders": 3},
    {"slug": "notaria-17", "orders": 3},
    {"slug": "beesmart-delivery", "orders": 3}
  ]
}
```

### 4.2 Frontend: Admin Button

**Location:** `/agent/factory` (admin dashboard)

**UI Component:**
```tsx
<Card className="border-yellow-500/50">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      🎭 Demo Data Seeder
    </CardTitle>
    <CardDescription>
      Solo uso interno. Crea tenants y órdenes de demostración.
    </CardDescription>
  </CardHeader>
  <CardContent>
    <Button onClick={handleSeedDemo} disabled={loading}>
      {loading ? "Creando..." : "Crear Datos Demo"}
    </Button>
  </CardContent>
</Card>
```

**Guards:**
- Only visible if `user.role === "admin"`
- Shows toast on success/error
- Non-destructive (can run multiple times)

### 4.3 Portal Polish

**Files to Update:**
- `/portal/[tenantSlug]/page.tsx` - Welcome header
- `/portal/[tenantSlug]/orders/page.tsx` - Empty states
- Portal components - Text improvements

**Changes:**
- Add tenant name to header
- Add descriptive subtitles
- Improve empty state messaging
- Remove technical jargon
- Ensure no internal paths exposed

---

## 5. Safety & Rollback

### 5.1 Safety Guarantees

✅ **NO Schema Changes**
- Uses existing `tenants` and `orders` tables
- No new columns or migrations required

✅ **NO Security Relaxation**
- All existing guards remain in place
- `require_admin()` on seed endpoint
- Tenant isolation unchanged

✅ **Idempotent Operations**
- Check tenant existence before creation
- No duplicate orders
- Can safely re-run seed

✅ **DEV_MODE Aware**
- Respects existing `DEV_MODE` behavior
- No changes to production security model

### 5.2 Rollback Strategy

If anything breaks:

1. **Remove seed endpoint**: Delete `/api/admin/seed-demo` route
2. **Remove admin button**: Hide demo seeder card in `/agent/factory`
3. **Revert portal text changes**: Git revert to previous copy
4. **Delete demo tenants** (if needed): Use `/agent/tenants` admin UI

**Database Safety:**
- Demo tenants can be deleted via admin UI
- Demo orders can be deleted individually
- No destructive migrations required

---

## 6. Testing Checklist

### 6.1 Backend Testing

- [ ] `POST /api/admin/seed-demo` returns 403 without admin token
- [ ] `POST /api/admin/seed-demo` creates 3 tenants
- [ ] All created orders have correct `tenant_id`
- [ ] Orders have realistic `datos_cliente` and `agent_blueprint`
- [ ] Idempotency: calling twice doesn't duplicate data

### 6.2 Frontend Testing

- [ ] Admin sees "Crear Datos Demo" button in `/agent/factory`
- [ ] Non-admin users don't see demo seeder
- [ ] Button triggers seed and shows success toast
- [ ] `/agent/tenants` shows new demo tenants
- [ ] "Ver Portal" links work for each tenant

### 6.3 Portal Testing

- [ ] `/portal/algorithmics-academy` shows 3 orders
- [ ] `/portal/notaria-17` shows 3 orders
- [ ] `/portal/beesmart-delivery` shows 3 orders
- [ ] Welcome header shows tenant name
- [ ] Empty states are user-friendly
- [ ] No internal paths or IDs exposed

### 6.4 Isolation Testing

- [ ] Admin can see all demo tenant orders
- [ ] Demo tenant user only sees their own orders
- [ ] Legacy users don't see demo tenant orders
- [ ] Multi-tenant filtering still works correctly

---

## 7. Success Criteria

✅ Phase 8 is complete when:

1. **Demo Data Exists**
   - 3 realistic demo tenants created
   - 9 demo orders distributed across tenants
   - Orders use actual catalog agents

2. **Admin Controls Work**
   - Seed endpoint functional and safe
   - Admin UI button triggers seed
   - Idempotent operation confirmed

3. **Portal UX Improved**
   - Welcome headers personalized
   - Empty states user-friendly
   - No technical jargon
   - No internal data exposed

4. **Documentation Complete**
   - `replit.md` updated with Phase 8 status
   - Seed mechanism documented
   - Portal access instructions clear

5. **Zero Breaking Changes**
   - No schema modifications
   - No security regressions
   - Existing functionality intact
   - All tests passing

---

## 8. Next Steps (Post-Phase 8)

Once Phase 8 is complete:

1. **User Acceptance Testing**
   - Show demo portals to stakeholders
   - Get feedback on UX improvements
   - Iterate based on feedback

2. **Production Preparation**
   - Review `docs/PRODUCTION_CHECKLIST.md`
   - Plan production tenant onboarding
   - Set up monitoring and alerts

3. **Future Enhancements**
   - Real-time order progress notifications
   - Client portal analytics
   - Tenant-specific branding/themes
   - Email notifications for order updates

---

**End of PHASE_8_PLAN.md**
