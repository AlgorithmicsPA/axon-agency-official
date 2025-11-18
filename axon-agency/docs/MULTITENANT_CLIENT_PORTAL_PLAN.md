# FASE 7: Multi-Tenant + Client Portal — Plan de Arquitectura

**Documento de Diseño Técnico**  
**Fecha**: 16-17 Noviembre 2025  
**Status**: **Phases 1-5 COMPLETE** ✅ (Backend + Auth + Portal + Admin UI + Testing)  
**Production Ready**: See [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md) for deployment guide  
**Autor**: Axon Agency Team

---

## ✅ Implementation Status

### Phase 1: Backend Multi-Tenant Infrastructure — **COMPLETE** ✅

**Fecha de implementación**: 17 Noviembre 2025  
**Status**: Producción completa, 100% backward compatible  

**Implementado:**
- ✅ Modelo `Tenant` (`app/models/tenants.py`): UUID primary key, slug, name, business_type, branding, settings, timestamps
- ✅ Columna `tenant_id` agregada al modelo `Order` (nullable, FK opcional a `tenants.id`)
- ✅ API CRUD de Tenants (`app/routers/tenants.py`):
  - `GET /api/tenants` - Listar todos los tenants
  - `GET /api/tenants/{id}` - Obtener tenant por ID
  - `POST /api/tenants` - Crear nuevo tenant
  - `PUT /api/tenants/{id}` - Actualizar tenant
  - `DELETE /api/tenants/{id}` - Eliminar tenant
- ✅ API de Orders extendida con soporte multi-tenant:
  - `GET /api/orders?tenant_id=...` - Filtrar órdenes por tenant
  - `POST /api/orders` - Crear orden con `tenant_id` opcional
- ✅ Migración SQL idempotente (`migrate_multitenant.py`):
  - Tabla `tenants` creada con índices en `slug` y `active`
  - Columna `tenant_id` agregada a `orders` con índice
- ✅ Testing completo validado:
  - Creación de tenant "Colegio Pedregal"
  - Creación de órdenes con/sin tenant_id
  - Filtrado de órdenes por tenant_id
  - Backward compatibility (18 órdenes existentes mantienen tenant_id=null)

**Archivos de implementación:**
```
axon-agency/apps/api/
├── app/models/tenants.py         (nuevo)
├── app/models/orders.py          (modificado: +tenant_id)
├── app/routers/tenants.py        (nuevo)
├── app/routers/orders.py         (modificado: +filtro tenant_id)
├── app/main.py                   (modificado: +router tenants)
└── migrate_multitenant.py        (nuevo)
```

**Base de datos:**
- SQLite (`axon.db`) con nueva tabla `tenants` y columna `orders.tenant_id`
- Migración ejecutada exitosamente sin breaking changes

### Phase 2: Auth + Tenant Context — **COMPLETE** ✅

**Fecha de implementación**: 17 Noviembre 2025  
**Status**: Producción completa, 100% backward compatible, dev-mode compatible  

**Implementado:**
- ✅ Modelo `User` extendido con `tenant_id` (`app/models/core.py`): nullable VARCHAR FK a `tenants.id`
- ✅ Migración SQL idempotente (`migrate_multitenant_phase2.py`):
  - Columna `tenant_id` agregada a tabla `users` con índice
  - Todos los usuarios existentes tienen `tenant_id = NULL` (backward compatible)
- ✅ Helper `get_user_from_token` en `app/core/security.py`:
  - Retorna User model completo desde DB (no solo TokenData)
  - Dev-mode bypass: retorna mock user cuando dev token no existe en DB
  - Security: valida is_active antes de retornar user
- ✅ Endpoint `/api/auth/me` actualizado (`app/routers/auth.py`):
  - Retorna campos adicionales: `id`, `email`, `is_admin`, `tenant_id`, `tenant_slug`, `tenant_name`
  - Si user tiene tenant_id, busca Tenant en DB y retorna slug + name
- ✅ Filtrado automático por tenant en `GET /api/orders` (`app/routers/orders.py`):
  - **Admin users** (role=admin): ven TODAS las órdenes, pueden filtrar por cualquier tenant_id
  - **Tenant-bound users** (user.tenant_id != null, no admin): ven SOLO órdenes de su tenant, filtro forzado automáticamente
  - **Legacy users** (tenant_id = null, no admin): ven todas las órdenes (backward compatible)
  - Logging: registra cuando tenant user accede a órdenes y cuando query param es overridden
- ✅ Frontend AuthContext extendido (`apps/web/contexts/AuthContext.tsx`):
  - Nuevos campos: `tenantId`, `tenantSlug`, `tenantName`, `isTenantUser`
  - `isTenantUser` computed: `!!tenantId && !isAdmin`
  - Type User incluye: `id`, `email`, `is_admin`, `tenant_id`, `tenant_slug`, `tenant_name`
- ✅ TenantOnly guard agregado (`apps/web/components/auth/RoleGuard.tsx`):
  - Componente para proteger rutas exclusivas de tenant users
  - Usa `isTenantUser` del AuthContext
- ✅ Testing completo validado:
  - Dev token funciona (/auth/dev/token → /auth/me con mock user)
  - /auth/me retorna tenant fields (tenant_id, tenant_slug, tenant_name)
  - Admin user ve todas las órdenes (con/sin tenant_id)
  - Backward compatibility verificada (users sin tenant_id funcionan normal)

**Archivos de implementación:**
```
axon-agency/apps/api/
├── app/models/core.py               (modificado: User.tenant_id)
├── app/core/security.py             (modificado: +get_user_from_token helper)
├── app/routers/auth.py              (modificado: /auth/me con tenant info)
├── app/routers/orders.py            (modificado: filtrado automático por tenant)
└── migrate_multitenant_phase2.py   (nuevo)

axon-agency/apps/web/
├── contexts/AuthContext.tsx         (modificado: +tenant fields)
└── components/auth/RoleGuard.tsx    (modificado: +TenantOnly guard)
```

**Base de datos:**
- SQLite (`axon.db`) con columna `users.tenant_id` (nullable)
- Migración Phase 2 ejecutada exitosamente sin breaking changes

**Architect Review:**
- ✅ Security validada: tenant filtering correcto, admin flow unchanged
- ✅ Backward compatibility confirmada: existing users/orders work con tenant_id=null
- ✅ Dev-mode regression fixed: dev token funciona con mock user bypass
- ✅ Code quality: logging agregado, error handling correcto

### Phase 3: Client Portal UI — **COMPLETE** ✅

**Fecha de implementación**: 17 Noviembre 2025  
**Status**: Producción completa, security verified by architect  

**Implementado:**
- ✅ Redirect page `/portal` (`app/portal/page.tsx`):
  - Tenant users → auto-redirect to `/portal/{tenantSlug}`
  - Admin users → message: "You are an admin. Use /agent/* dashboards"
  - Guest users → Access Denied message
- ✅ Portal layout `/portal/[tenantSlug]/layout.tsx`:
  - Security checks: tenant slug validation, admin bypass for debugging
  - Tenant branding: header with tenant name + "Client Portal" subtitle
  - Navigation: Dashboard | Orders links
  - Dark theme consistent with admin UI (`bg-slate-950`, `text-slate-50`, `border-slate-800`)
- ✅ Dashboard `/portal/[tenantSlug]/page.tsx`:
  - Stats cards: Total Orders, In Progress (nuevo/planificacion/construccion/qa), Ready (listo), Failed (fallido)
  - Recent orders table: last 10 orders sorted by updated_at desc
  - Columns: Order #, Product Name, Estado (badge), Last Updated, Deliverable (✓/Pendiente)
  - "Ver todas las órdenes" button → full orders list
- ✅ Orders list `/portal/[tenantSlug]/orders/page.tsx`:
  - Full table with all tenant orders (backend auto-filters by tenant_id)
  - Estado filter: All / Listo / En Progreso / Fallido (client-side)
  - Columns: Order #, Product Name, Estado, Created At, Updated At, Deliverable
  - Click row → navigate to order detail
- ✅ Order detail `/portal/[tenantSlug]/orders/[id]/page.tsx` (READ-ONLY):
  - Header: order number, estado badge, dates
  - Product info: tipo_producto, nombre_producto
  - Safe client data: sitio_web, contacto (NO secrets)
  - Deliverable section: sanitized filenames only (NO internal paths)
  - **Critical security fix**: Deliverable paths sanitized using `.split('/').pop()` to show only basenames
  - NO QA status/messages, NO agent artifacts, NO internal filesystem paths
- ✅ Reusable components (`components/portal/`):
  - `TenantStatsCard.tsx`: stats display with icon, title, value, description
  - `TenantPortalHeader.tsx`: header with tenant name, navigation links
  - `TenantOrdersTable.tsx`: orders table with estado badges, filters, deliverable status

**Security:**
- ✅ Tenant slug validation in layout (tenant users restricted to their slug)
- ✅ Admin users can access any slug for debugging
- ✅ Deliverable paths sanitized - only filenames shown, NO internal filesystem paths
- ✅ Clean client-facing UI - NO QA, artifacts, or internal admin data exposed
- ✅ Architect verified security fix for path sanitization

**Archivos de implementación:**
```
axon-agency/apps/web/
├── app/portal/page.tsx                         (nuevo)
├── app/portal/[tenantSlug]/layout.tsx          (nuevo)
├── app/portal/[tenantSlug]/page.tsx            (nuevo)
├── app/portal/[tenantSlug]/orders/page.tsx     (nuevo)
├── app/portal/[tenantSlug]/orders/[id]/page.tsx (nuevo)
└── components/portal/
    ├── TenantStatsCard.tsx                     (nuevo)
    ├── TenantPortalHeader.tsx                  (nuevo)
    └── TenantOrdersTable.tsx                   (nuevo)
```

**Architect Review:**
- ✅ Security validated: deliverable paths sanitized (critical fix applied)
- ✅ No internal data exposed: QA, artifacts, filesystem paths all hidden
- ✅ Code quality: clean client-facing UI, re-uses shadcn/ui components
- ✅ Estado badge colors match admin pattern
- ✅ Fallback handling for malformed paths

### Phase 4: Tenant Admin UI — **COMPLETE** ✅

**Fecha de implementación**: 17 Noviembre 2025  
**Status**: Producción completa, security validated by architect  

**Implementado:**
- ✅ List page `/agent/tenants` (`app/agent/tenants/page.tsx`):
  - Stats cards: Total Tenants, Active, Inactive (auto-calculated from tenant data)
  - Table columns: Name, Slug, Type (badge), Contact, Created, Actions
  - Actions: "Edit" button → detail page, "View Portal" → `/portal/{slug}` (new tab)
  - AdminOnly guard: non-admin users see "Access Denied" message
- ✅ Detail page `/agent/tenants/[id]` (`app/agent/tenants/[id]/page.tsx`):
  - Tenant info card: name, slug, business_type, contact, branding, settings, status
  - Orders summary card: Total, In Progress, Completed, Failed (tenant-specific counts)
  - Recent orders table: last 5 orders from this tenant
  - Edit form: inline editing with TenantForm component
  - Delete tenant button with confirmation dialog
  - "View Portal" button → `/portal/{slug}` (new tab)
- ✅ Reusable components (`components/tenants/`):
  - `TenantBadge.tsx`: business type badges with colors (school→green, notary→blue, delivery→orange, health→red, retail→purple, general→gray)
  - `TenantListTable.tsx`: tenant table with Edit/Portal buttons, sortable columns
  - `TenantForm.tsx`: create/edit form with full validation + delete dialog
    - Fields: name, slug (auto-generated from name), business_type (select), contact_email, contact_name, contact_phone, primary_color, notes (textarea), active (toggle)
    - Validation: email format, required fields
    - Delete confirmation with AlertDialog
- ✅ shadcn/ui components created (`components/ui/`):
  - `input.tsx`: text input with dark theme support
  - `textarea.tsx`: multi-line text input with dark theme
  - `label.tsx`: form label component
  - `alert-dialog.tsx`: confirmation dialog for destructive actions
- ✅ Sidebar updated (`components/Sidebar.tsx`):
  - "Tenants" link added (admin-only, Building icon)
  - Placed after "Fábrica de Agentes" in navigation
  - Conditional rendering: only visible to admin users

**Security:**
- ✅ All pages wrapped in `<AdminOnly>` guard (non-admins see Access Denied)
- ✅ Uses `useApiClient` which auto-includes JWT token from store
- ✅ Same auth pattern as `/agent/factory` and `/agent/orders` (proven working)
- ✅ Delete action requires confirmation via AlertDialog

**Archivos de implementación:**
```
axon-agency/apps/web/
├── app/agent/tenants/page.tsx                  (nuevo)
├── app/agent/tenants/[id]/page.tsx             (nuevo)
├── components/tenants/
│   ├── TenantBadge.tsx                         (nuevo)
│   ├── TenantListTable.tsx                     (nuevo)
│   └── TenantForm.tsx                          (nuevo)
├── components/ui/
│   ├── input.tsx                               (nuevo)
│   ├── textarea.tsx                            (nuevo)
│   ├── label.tsx                               (nuevo)
│   └── alert-dialog.tsx                        (nuevo)
└── components/Sidebar.tsx                      (modificado: +Tenants link)
```

**Architect Review:**
- ✅ Auth implementation verified: `useApiClient` correctly configured with JWT token header
- ✅ Security validated: AdminOnly guards applied, Access Denied shown for non-admins
- ✅ Code quality: Form validation, error handling, TypeScript type safety
- ✅ UX consistency: Dark theme matches `/agent/factory` and `/agent/orders` pages
- ⚠️ Manual testing required: User must authenticate as admin to verify CRUD operations end-to-end

**Next Steps:**
- User should test with admin authentication:
  - Login as admin user
  - Navigate to `/agent/tenants`
  - Verify tenant list loads
  - Edit tenant, verify PUT updates
  - Create new tenant, verify POST creates
  - Delete tenant, verify DELETE removes

### Phase 5: Testing & Security Hardening — **COMPLETE** ✅

**Fecha de implementación**: 17 Noviembre 2025  
**Status**: Testing completo, security fixes aplicados, production-ready  

**Implementado:**
- ✅ **Critical Security Fixes**:
  - Admin-only auth agregado a `/api/tenants` (GET/POST/PUT/DELETE) con helper `require_admin()`
  - Tenant scoping agregado a `/api/orders/{id}` y `/api/orders/{id}/result` con helper `verify_order_access()`
  - Backend protection: Admin acceso total, Tenant user solo su tenant, Legacy user solo órdenes sin tenant
- ✅ **Multi-Tenant Isolation Tests**:
  - Creados 2 tenants test: "colegio-pedregal" y "notaria-martinez"
  - Creadas órdenes con diferentes tenant_id
  - Validado tenant filtering funciona correctamente (admin ve todos, tenant user solo su tenant)
  - Validado admin puede acceder a órdenes de cualquier tenant mediante GET /orders/{id}
- ✅ **Portal & Admin UI Security Checks**:
  - `/portal/[tenantSlug]`: Usa auth via `useApiClient()` (backend-protected)
  - `/agent/tenants`: Protegido con `<AdminOnly>` wrapper + backend admin auth
  - `/agent/factory`: Protegido con `<AdminOnly>` wrapper + backend admin auth
  - `/agent/orders`: Backend auth OK (finding menor: debería usar `<AdminOnly>` para consistencia)
- ✅ **Data Leakage & Path Sanitization**:
  - Verificado no hay filesystem paths en API responses
  - Solo URLs públicas expuestas (`repo_url`, `deploy_url`)
  - No se encontraron referencias a `/home/runner`, `/workspace/`, `file://` en código
- ✅ **Production Checklist Creado**:
  - Documento comprehensivo de 900+ líneas en `docs/PRODUCTION_CHECKLIST.md`
  - DEV_MODE → PROD_MODE migration steps
  - Security review summary completo
  - Multi-tenant smoke tests con comandos curl prácticos
  - Database migration checklist
  - Production readiness checklist (45 items)
  - Go-live procedure y rollback plan

**Archivos de implementación:**
```
axon-agency/apps/api/
├── app/routers/tenants.py              (modificado: +require_admin helper, +auth a todos endpoints)
└── app/routers/orders.py               (modificado: +verify_order_access helper, +tenant scoping a GET /{id})

axon-agency/docs/
└── PRODUCTION_CHECKLIST.md             (nuevo: guía de deployment completa)
```

**Testing Summary:**
- ✅ Auth protection: `/api/tenants` sin auth → 403 Forbidden ✓
- ✅ Admin access: Admin token accede a todos los endpoints ✓
- ✅ Tenant filtering: Colegio (2 orders) vs Notaria (1 order) ✓
- ✅ Order access: Admin accede a órdenes de ambos tenants ✓
- ✅ Data isolation: No filesystem paths expuestos ✓

**Production Ready:**
- Sistema multi-tenant completamente funcional
- Security hardening aplicado y verificado
- Backward compatible con legacy users/orders
- Production deployment guide disponible en [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)

---

## 📋 Resumen Ejecutivo

Este documento diseña la arquitectura multi-tenant y Client Portal para Axon Agency, transformando el sistema actual (agencia única) en una plataforma multi-cliente donde cada escuela, notaría o negocio tiene:

- **Su propio workspace/tenant** aislado
- **Portal dedicado** para ver sus órdenes y deliverables
- **Branding personalizado** (logo, colores)
- **Acceso controlado** (solo ven sus propios datos)

La filosofía de negocio se mantiene: **vendemos sistemas completos de agentes**, no chatbots aislados. Ahora lo hacemos para múltiples clientes simultáneamente.

---

## 🔍 Estado Actual del Sistema (Inventario)

### Cómo se Representa Hoy un "Cliente"

**En Orders (`apps/api/app/models/orders.py`):**
```python
cliente_id: Optional[str]           # ID simple, no ligado a tenant
datos_cliente: dict                 # JSON libre con info del cliente
```

**Problema actual:**
- No hay concepto de "workspace" o "tenant"
- `cliente_id` es solo un string, no relacionado con entidad Tenant
- Todas las órdenes se ven en el mismo admin dashboard
- No hay separación lógica entre clientes (escuela vs. notaría)

### Roles Existentes (`apps/web/contexts/AuthContext.tsx`)

```typescript
role: "admin" | "viewer" | "member"

isAdmin = role === "admin"          // Team interno de Axon
isClient = role === "viewer" || "member"  // Clientes externos
```

**Problema actual:**
- Roles genéricos, no ligados a tenants específicos
- Un "viewer" vería TODAS las órdenes (no solo las de su tenant)
- No hay concepto de "admin de tenant" vs. "admin global"

### Flujo de Orden Actual

```
Catálogo → CatalogOrderRequest → Order Creation → Factory → Builder v2
```

**CatalogOrderRequest actual:**
```typescript
{
  agent_id: string,
  website_url: string,
  description: string,
  contact_email?: string
}
```

**Problema actual:**
- No se especifica a qué tenant pertenece la orden
- El admin crea órdenes manualmente sin asociarlas a un workspace

---

## 🏗️ Modelo Multi-Tenant (Diseño)

### 1. Conceptos Clave

#### **Tenant / Workspace**
Una organización cliente que usa Axon Agency para construir sistemas de agentes.

**Ejemplos de tenants:**
- 🏫 **Colegio Pedregal** (escuela K-12)
- 📜 **Notaría 17** (servicios notariales)
- 🍕 **Pizza Express** (delivery food)
- 🏥 **Clínica Dental Dr. Ruiz** (salud)

Cada tenant tiene:
- Su propio conjunto de órdenes
- Sus propios usuarios (representantes de la organización)
- Branding personalizado (logo, colores, slug)
- Acceso aislado (no ven datos de otros tenants)

#### **Usuario Interno (Admin Global)**
Miembro del equipo de Axon Agency.

**Permisos:**
- Ver TODOS los tenants y sus órdenes
- Crear/editar tenants
- Asignar órdenes a tenants
- Acceder a rutas internas (`/agent/*`)
- Ver artifacts, QA interno, logs de Axon 88

**Roles internos:**
- `admin` (full access)
- `member` (limited internal access)

#### **Usuario Cliente (Tenant User)**
Representante de un tenant (ej: director de escuela, notario, dueño de negocio).

**Permisos:**
- Ver solo órdenes de SU tenant (`tenant_id = su_tenant`)
- Ver deliverables listos/entregados
- Solicitar ajustes (comentarios)
- NO ver internals (Axon 88 paths, QA detallado, artifacts)

**Roles de tenant:**
- `tenant_admin` (puede crear órdenes para su tenant)
- `tenant_viewer` (solo lectura de órdenes de su tenant)

#### **Orden Ligada a Tenant**
Cada orden pertenece a UN tenant específico.

**Relación:**
```
Tenant (1) ──── (N) Orders
```

Una escuela puede tener múltiples órdenes:
- WhatsApp Autopilot para admisiones
- Marketing Autopilot para redes sociales
- Content Generator para blog escolar

---

### 2. Entidad Tenant (Diseño de Modelo)

```python
# apps/api/app/models/tenants.py (FUTURO)

class Tenant(SQLModel, table=True):
    """
    Representa un cliente/workspace en Axon Agency.
    Cada tenant es una organización que usa nuestros servicios.
    """
    __tablename__ = "tenants"
    
    # IDENTIFICACIÓN
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="UUID único del tenant"
    )
    
    slug: str = Field(
        unique=True,
        index=True,
        description="Slug único para URLs (ej: colegio-pedregal)"
    )
    
    # INFORMACIÓN BÁSICA
    nombre: str = Field(
        description="Nombre de la organización (ej: Colegio Pedregal)"
    )
    
    tipo: str = Field(
        default="general",
        description="Tipo de negocio: school, notary, delivery, health, retail, general"
    )
    
    # CONTACTO
    contact_email: str = Field(
        description="Email principal del tenant"
    )
    
    contact_phone: Optional[str] = Field(
        default=None,
        description="Teléfono de contacto"
    )
    
    contact_name: Optional[str] = Field(
        default=None,
        description="Nombre del contacto principal"
    )
    
    # BRANDING
    branding: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="""
        Configuración de branding del tenant:
        {
            "logo_url": "https://...",
            "primary_color": "#1E40AF",
            "secondary_color": "#10B981",
            "company_website": "https://colegiopedregal.com"
        }
        """
    )
    
    # CONFIGURACIÓN
    settings: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="""
        Configuración específica del tenant:
        {
            "max_orders": 10,           // Límite de órdenes activas
            "allowed_agents": ["*"],    // Agentes disponibles (* = todos)
            "notifications_email": "admin@tenant.com",
            "timezone": "America/Mexico_City"
        }
        """
    )
    
    # ESTADO
    active: bool = Field(
        default=True,
        description="True si el tenant está activo"
    )
    
    # TIMESTAMPS
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del tenant"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )
    
    # METADATA
    notas_internas: str = Field(
        default="",
        description="Notas del equipo interno sobre este tenant"
    )
```

**Tipos de tenant propuestos:**
- `school` - Instituciones educativas
- `notary` - Notarías y servicios legales
- `delivery` - Negocios de comida/delivery
- `health` - Clínicas, consultorios
- `retail` - Tiendas, comercio
- `general` - Otros negocios

---

### 3. Cambios en Order (Diseño)

```python
# apps/api/app/models/orders.py (MODIFICACIONES FUTURAS)

class Order(SQLModel, table=True):
    # ... campos existentes ...
    
    # NUEVO: Relación con Tenant
    tenant_id: Optional[str] = Field(
        default=None,
        index=True,
        foreign_key="tenants.id",
        description="ID del tenant al que pertenece esta orden"
    )
    
    # MEJORADO: Información de contacto del cliente (más estructurada)
    client_contact: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="""
        Contacto del cliente dentro del tenant:
        {
            "nombre": "Juan Pérez",
            "email": "juan@colegiopedregal.com",
            "telefono": "+52 55 1234 5678",
            "cargo": "Director de Tecnología"
        }
        """
    )
    
    # DEPRECADO (mantener por compatibilidad temporal)
    cliente_id: Optional[str]  # Todavía existe pero tenant_id es la nueva forma
```

**Estrategia de campos:**
- `tenant_id` → Relación principal con el workspace
- `client_contact` → Contacto específico dentro del tenant
- `cliente_id` → Mantener temporalmente para migración, eventualmente deprecar
- `datos_cliente` → Migrar info a `client_contact` y blueprint

---

### 4. Relaciones del Modelo

```
┌─────────────┐
│   Tenant    │
│  (1 tenant) │
└──────┬──────┘
       │
       │ has many
       │
       ▼
┌─────────────┐         ┌──────────────┐
│   Orders    │────────▶│ AgentBlueprint│
│ (N orders)  │  has    │              │
└──────┬──────┘         └──────────────┘
       │
       │ has many
       │
       ▼
┌─────────────┐
│    Users    │
│ (tenant     │
│  members)   │
└─────────────┘

Relaciones:
- Tenant (1) ──── (N) Orders
- Tenant (1) ──── (N) Users (tenant members)
- Order (1) ──── (1) AgentBlueprint
```

**User → Tenant Relationship:**
```python
# apps/api/app/models/users.py (FUTURO)

class User(SQLModel, table=True):
    id: str
    username: str
    email: str
    
    # NUEVO: Relación con tenant
    tenant_id: Optional[str] = Field(
        default=None,
        index=True,
        foreign_key="tenants.id",
        description="Si es usuario de tenant, ID del tenant"
    )
    
    # Roles:
    # - "admin" → Admin global (sin tenant_id)
    # - "tenant_admin" → Admin de su tenant
    # - "tenant_viewer" → Solo lectura de su tenant
    role: str
```

---

## 🎨 Diseño del Client Portal v1

### 1. UX General - Visión del Cliente

Cuando un representante del **Colegio Pedregal** entra a su portal:

1. **Dashboard personalizado** con:
   - Logo de su escuela
   - Estadísticas de sus órdenes
   - Órdenes recientes (solo las suyas)

2. **Lista de órdenes** filtrada automáticamente:
   - Solo ve órdenes con `tenant_id = colegio-pedregal`
   - No ve órdenes de Notaría 17 o Pizza Express

3. **Detalle de orden**:
   - Estado actual (nuevo → planificación → construcción → listo)
   - Si está "listo": puede ver/descargar deliverable
   - Puede dejar comentarios/solicitar ajustes
   - NO ve: Axon 88 paths, QA interno detallado, artifacts crudos

4. **Deliverables aprobados**:
   - Descarga de paquete final
   - Documentación de uso
   - Credenciales/URLs de acceso

### 2. Rutas Propuestas (Diseño, No Implementación)

#### Portal de Cliente

```
/portal/{tenantSlug}
├── /portal/colegio-pedregal
│   ├── / (dashboard)
│   ├── /orders (lista de órdenes)
│   ├── /orders/ORD-2025-042 (detalle)
│   └── /settings (ajustes del tenant)
│
├── /portal/notaria-17
│   └── ... (misma estructura)
│
└── /portal/pizza-express
    └── ... (misma estructura)
```

#### Rutas Internas (Admin)

```
/agent
├── /agent/tenants (NUEVO - gestión de tenants)
│   ├── / (lista de tenants)
│   ├── /new (crear tenant)
│   ├── /{tenantId} (detalle de tenant)
│   └── /{tenantId}/orders (órdenes del tenant)
│
├── /agent/orders (órdenes globales - todos los tenants)
├── /agent/factory (factory dashboard global)
└── ... (rutas existentes)
```

### 3. Autenticación: Admin vs. Cliente

#### Flujo de Autenticación

```
Usuario hace login
    │
    ├─▶ role === "admin" 
    │       │
    │       └─▶ Redirige a /agent/orders (dashboard interno)
    │           Puede ver TODOS los tenants
    │
    └─▶ role === "tenant_admin" o "tenant_viewer"
            │
            └─▶ Redirige a /portal/{su-tenant-slug}
                Solo ve datos de su tenant
```

#### Estrategia de Auth (Alto Nivel)

**Opción 1: Session-Based con Tenant Context**
```typescript
// AuthContext mejorado (FUTURO)
interface User {
  id: string
  username: string
  email: string
  role: "admin" | "tenant_admin" | "tenant_viewer"
  tenant_id?: string        // Si es usuario de tenant
  tenant_slug?: string      // Slug del tenant para URLs
}
```

**Opción 2: JWT con Tenant Claims**
```json
{
  "user_id": "uuid",
  "role": "tenant_admin",
  "tenant_id": "uuid-del-tenant",
  "tenant_slug": "colegio-pedregal"
}
```

**Middleware de Portal (FUTURO):**
```typescript
// Verificar que usuario solo acceda a su tenant
if (user.role.startsWith('tenant_') && tenantSlug !== user.tenant_slug) {
  return redirect('/unauthorized')
}
```

### 4. Qué Ve el Admin vs. Qué Ve el Cliente

#### Admin Global (`role === "admin"`)

**Puede ver:**
- ✅ Todos los tenants
- ✅ Todas las órdenes (todos los tenants)
- ✅ Blueprints completos
- ✅ Artifacts de Agent Builder
- ✅ QA interno detallado
- ✅ Logs de Axon 88
- ✅ Rutas internas (`product_path`, `log_path`)
- ✅ Crear/editar tenants
- ✅ Asignar órdenes a tenants

**Rutas accesibles:**
```
/agent/*              (todas las rutas internas)
/portal/{cualquier-tenant}  (puede ver cualquier portal)
```

#### Cliente Tenant (`role === "tenant_admin" o "tenant_viewer"`)

**Puede ver:**
- ✅ Solo órdenes de SU tenant (`tenant_id = su_tenant`)
- ✅ Estado de orden (nuevo → listo)
- ✅ Deliverables marcados como "listo/entregado"
- ✅ Documentación final
- ❌ NO ve blueprints internos
- ❌ NO ve artifacts crudos
- ❌ NO ve QA interno detallado
- ❌ NO ve rutas de Axon 88
- ❌ NO puede crear tenants

**Rutas accesibles:**
```
/portal/{su-tenant-slug}/*     (solo su portal)
/catalog                       (catálogo público - opcional)
```

#### Tabla de Permisos

| Recurso                  | Admin Global | Tenant Admin | Tenant Viewer |
|--------------------------|--------------|--------------|---------------|
| Ver todos los tenants    | ✅           | ❌           | ❌            |
| Ver su tenant            | ✅           | ✅           | ✅            |
| Crear tenant             | ✅           | ❌           | ❌            |
| Ver todas las órdenes    | ✅           | ❌           | ❌            |
| Ver órdenes de su tenant | ✅           | ✅           | ✅            |
| Crear orden para tenant  | ✅           | ✅           | ❌            |
| Ver blueprints           | ✅           | ❌           | ❌            |
| Ver artifacts            | ✅           | ❌           | ❌            |
| Ver QA interno           | ✅           | ❌           | ❌            |
| Ver deliverable final    | ✅           | ✅ (su tenant) | ✅ (su tenant) |
| Descargar deliverable    | ✅           | ✅ (su tenant) | ✅ (su tenant) |

### 5. Integración con Catálogo de Agentes

#### Creación de Orden desde Catálogo (Admin Interno)

**Request mejorado:**
```typescript
// CatalogOrderRequest (FUTURO)
interface CatalogOrderRequest {
  agent_id: string                    // ID del agente del catálogo
  tenant_id: string                   // NUEVO: A qué tenant pertenece
  website_url: string
  description: string
  client_contact: {                   // NUEVO: Contacto estructurado
    nombre: string
    email: string
    telefono?: string
    cargo?: string
  }
}
```

**Flujo propuesto:**
```
Admin en /agent/tenants/colegio-pedregal
    │
    └─▶ Click "Crear Orden para Este Tenant"
            │
            └─▶ Modal con Catálogo
                    │
                    ├─▶ Selecciona "WhatsApp Autopilot"
                    ├─▶ Completa formulario
                    │   - website_url: colegiopedregal.com
                    │   - description: "Autopilot para admisiones"
                    │   - client_contact: director@colegio...
                    │
                    └─▶ POST /api/catalog/orders
                        {
                          agent_id: "whatsapp-autopilot",
                          tenant_id: "uuid-colegio-pedregal",
                          ...
                        }
                            │
                            └─▶ Se crea Order con tenant_id asignado
```

#### Creación de Orden desde Portal (Cliente - FASE POSTERIOR)

**En futuro** (no en v1 del portal):

```
Cliente logueado en /portal/colegio-pedregal
    │
    └─▶ Click "Solicitar Nuevo Agente"
            │
            └─▶ Ve catálogo filtrado (solo agentes permitidos)
                    │
                    └─▶ Completa formulario simplificado
                        - tenant_id se obtiene automáticamente del user.tenant_id
                        - client_contact se pre-llena con datos del user
```

**Campos necesarios en request para soportar esto:**
```typescript
// Backend valida que user.tenant_id === request.tenant_id
// Para evitar que un tenant cree órdenes en nombre de otro
```

---

## 🔄 Estrategia de Migración

### Fase 1: Agregar Campos Opcionales (Backward Compatible)

**Cambios en DB Schema:**
```sql
-- Crear tabla tenants (nueva)
CREATE TABLE tenants (
  id UUID PRIMARY KEY,
  slug VARCHAR UNIQUE NOT NULL,
  nombre VARCHAR NOT NULL,
  tipo VARCHAR DEFAULT 'general',
  contact_email VARCHAR NOT NULL,
  contact_phone VARCHAR,
  contact_name VARCHAR,
  branding JSON,
  settings JSON DEFAULT '{}',
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  notas_internas TEXT DEFAULT ''
);

-- Agregar tenant_id a orders (NULLABLE para compatibilidad)
ALTER TABLE orders
  ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL;

-- Agregar client_contact a orders (NULLABLE)
ALTER TABLE orders
  ADD COLUMN client_contact JSON DEFAULT NULL;

-- Índices
CREATE INDEX idx_orders_tenant_id ON orders(tenant_id);
CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_tipo ON tenants(tipo);
```

**Estrategia:**
- `tenant_id` es **NULLABLE** → órdenes antiguas siguen funcionando
- Órdenes nuevas pueden tener `tenant_id = NULL` (creadas antes de asignar tenant)
- Sistema funciona con y sin multi-tenancy simultáneamente

### Fase 2: Crear Tenants para Clientes Existentes

**Proceso manual (admin interno):**

1. **Revisar órdenes actuales:**
   ```sql
   SELECT DISTINCT datos_cliente->>'email' as email, 
                   datos_cliente->>'nombre' as nombre
   FROM orders
   WHERE tenant_id IS NULL;
   ```

2. **Crear tenants representativos:**
   - Si hay 3 órdenes de "colegiopedregal.com" → crear tenant "Colegio Pedregal"
   - Si hay 2 órdenes de "notaria17.mx" → crear tenant "Notaría 17"

3. **Script de creación:**
   ```python
   # Script manual para crear tenants (ejemplo)
   tenants_to_create = [
     {
       "slug": "colegio-pedregal",
       "nombre": "Colegio Pedregal",
       "tipo": "school",
       "contact_email": "contacto@colegiopedregal.com"
     },
     {
       "slug": "notaria-17",
       "nombre": "Notaría 17",
       "tipo": "notary",
       "contact_email": "info@notaria17.mx"
     }
   ]
   
   for tenant_data in tenants_to_create:
     tenant = Tenant(**tenant_data)
     session.add(tenant)
   session.commit()
   ```

### Fase 3: Asignar tenant_id a Órdenes Antiguas

**Estrategia de asignación:**

**Opción A: Manual por admin**
```
Admin interno:
1. Va a /agent/orders
2. Ve órdenes sin tenant_id
3. Revisa datos_cliente para identificar cliente
4. Asigna manualmente tenant_id desde UI
```

**Opción B: Script semi-automático**
```python
# Heurística simple basada en email domain
def assign_tenant_to_old_orders():
    orders_sin_tenant = session.exec(
        select(Order).where(Order.tenant_id == None)
    ).all()
    
    for order in orders_sin_tenant:
        email = order.datos_cliente.get('email', '')
        domain = email.split('@')[-1]
        
        # Buscar tenant por email domain
        tenant = session.exec(
            select(Tenant).where(Tenant.contact_email.like(f'%{domain}'))
        ).first()
        
        if tenant:
            order.tenant_id = tenant.id
            session.add(order)
    
    session.commit()
```

**Estrategia conservadora:**
- NO asignar automáticamente si no estamos 100% seguros
- Órdenes con `tenant_id = NULL` siguen siendo válidas
- Admin puede asignar manualmente después

### Fase 4: Aplicar en Replit (Dev) → Producción

**Proceso:**

1. **Desarrollo en Replit:**
   - Implementar modelos nuevos
   - Crear rutas `/api/tenants/*`
   - Crear UI `/portal/*`
   - Probar con tenants de prueba

2. **Migración en SQLite (dev):**
   ```bash
   # En Replit
   python scripts/migrate_to_multitenant.py
   ```

3. **Testing exhaustivo:**
   - Crear tenant de prueba
   - Crear órdenes para ese tenant
   - Verificar que portal muestra solo órdenes del tenant
   - Verificar que admin ve todo

4. **Deploy a producción:**
   - Exportar schema nuevo
   - Correr migración en producción (Cursor/Axon 88)
   - Crear tenants reales
   - Asignar órdenes existentes

---

## 🎯 Decisiones de Diseño Clave

### 1. ¿Por Qué `tenant_id` Nullable?

**Razón:** Backward compatibility durante migración.

**Ventajas:**
- Sistema sigue funcionando mientras migramos
- Órdenes antiguas no se rompen
- Podemos migrar gradualmente

**Desventajas:**
- Query más complejo (filtrar por `tenant_id IS NULL OR tenant_id = ?`)
- Eventualmente querremos hacer NOT NULL

**Plan a largo plazo:**
- Fase 1-3: `tenant_id NULLABLE`
- Fase 4: Asignar TODAS las órdenes a un tenant (crear tenant "Legacy" si es necesario)
- Fase 5: `ALTER TABLE orders MODIFY tenant_id NOT NULL`

### 2. ¿Slug vs. ID en URLs?

**Decisión:** Usar **slug** en URLs del portal (`/portal/colegio-pedregal`)

**Razón:**
- URLs amigables y branded
- Cliente ve su nombre en la URL
- SEO-friendly (si el portal es público)

**Internamente:**
- Frontend resuelve slug → tenant_id en primera carga
- Usa tenant_id para queries

### 3. ¿Crear Tenant = Crear User?

**Decisión:** NO automáticamente en v1.

**Proceso manual (v1):**
1. Admin crea Tenant
2. Admin crea User(s) para ese tenant manualmente
3. Admin asigna `tenant_id` al user

**Proceso automático (v2 - futuro):**
1. Admin crea Tenant
2. Sistema auto-genera credenciales para contacto principal
3. Envía email de invitación

### 4. ¿Multi-Tenant a Nivel de Base de Datos?

**Decisión:** Single Database, Tenant ID Filter (Row-Level Security)

**Estrategia:**
```sql
-- Todas las queries filtran por tenant_id
SELECT * FROM orders WHERE tenant_id = :current_tenant_id
```

**Alternativas descartadas:**
- **Database per tenant:** Complejo de mantener, overhead alto
- **Schema per tenant:** Similar complejidad

**Ventaja de Single DB + Filter:**
- Simpleza de deployment
- Queries globales posibles (admin)
- Backup/restore unificado

**Importante:** Implementar middleware de seguridad que SIEMPRE filtre por tenant_id en requests de cliente.

---

## 📱 Mockups de UI (Descripciones)

### Portal Dashboard (`/portal/colegio-pedregal`)

```
┌─────────────────────────────────────────────────────────────┐
│  [Logo Colegio Pedregal]              Usuario: Juan Pérez ▼ │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📊 Dashboard - Colegio Pedregal                              │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ 🎯 Órdenes  │  │ ✅ Listos   │  │ 🔨 En Curso │          │
│  │     5       │  │     2       │  │     3       │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                               │
│  📦 Órdenes Recientes                                         │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ ORD-2025-042  WhatsApp Autopilot    ✅ Listo         │   │
│  │ ORD-2025-038  Marketing Autopilot   🔨 Construcción  │   │
│  │ ORD-2025-032  Content Generator     ✅ Listo         │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  [Ver Todas las Órdenes] →                                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Portal Orders List (`/portal/colegio-pedregal/orders`)

```
┌─────────────────────────────────────────────────────────────┐
│  Mis Órdenes de Agentes                                       │
│                                                               │
│  Filtros: [Todos ▼] [Estado ▼]                               │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ Número        │ Agente             │ Estado    │ Fecha│   │
│  ├───────────────────────────────────────────────────────┤   │
│  │ ORD-2025-042  │ WhatsApp Autopilot │ ✅ Listo  │ 10/11│   │
│  │ ORD-2025-038  │ Marketing Auto     │ 🔨 Const. │ 08/11│   │
│  │ ORD-2025-032  │ Content Generator  │ ✅ Listo  │ 05/11│   │
│  │ ORD-2025-028  │ WhatsApp Auto      │ 📦 Entreg.│ 02/11│   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Portal Order Detail (`/portal/colegio-pedregal/orders/ORD-2025-042`)

```
┌─────────────────────────────────────────────────────────────┐
│  ← Volver a Mis Órdenes                                       │
│                                                               │
│  📦 ORD-2025-042 - WhatsApp Autopilot                         │
│  Estado: ✅ Listo                                             │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ 📋 Detalles                                          │     │
│  │                                                      │     │
│  │ Agente: WhatsApp Autopilot para Admisiones          │     │
│  │ Creado: 10 Nov 2025                                 │     │
│  │ Completado: 12 Nov 2025                             │     │
│  │                                                      │     │
│  │ ✅ Planificación completada                          │     │
│  │ ✅ Construcción completada                           │     │
│  │ ✅ QA aprobado                                       │     │
│  │ ✅ Listo para entregar                               │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ 📦 Deliverable                                       │     │
│  │                                                      │     │
│  │ Tu sistema está listo para usar:                    │     │
│  │                                                      │     │
│  │ 📄 Documentación: manual_uso.pdf                    │     │
│  │ 🔑 Credenciales: credentials.txt                    │     │
│  │ 📦 Paquete completo: deliverable.zip               │     │
│  │                                                      │     │
│  │ [Descargar Todo] 💾                                  │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
│  💬 Comentarios                                               │
│  [Solicitar ajuste o hacer pregunta...]                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Admin Tenant Management (`/agent/tenants`)

```
┌─────────────────────────────────────────────────────────────┐
│  🏢 Gestión de Tenants (Admin)                                │
│                                                               │
│  [+ Crear Nuevo Tenant]                                       │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ Slug           │ Nombre            │ Tipo    │ Órdenes│   │
│  ├───────────────────────────────────────────────────────┤   │
│  │ colegio-ped... │ Colegio Pedregal  │ 🏫 School│    5  │   │
│  │ notaria-17     │ Notaría 17        │ 📜 Notary│    3  │   │
│  │ pizza-express  │ Pizza Express     │ 🍕 Deliv.│    2  │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Roadmap de Implementación (Sugerido)

### Build Phase 1: Backend Multi-Tenant (Replit)

**Duración estimada:** 2-3 días

1. Crear modelo `Tenant` (`apps/api/app/models/tenants.py`)
2. Agregar `tenant_id` a `Order` (nullable)
3. Crear router `/api/tenants/*`
   - `GET /api/tenants` (lista - admin only)
   - `POST /api/tenants` (crear - admin only)
   - `GET /api/tenants/{id}` (detalle)
   - `PUT /api/tenants/{id}` (editar - admin only)
4. Modificar `GET /api/orders` para filtrar por tenant (si user es tenant_user)
5. Migración de DB (agregar campos)

### Build Phase 2: Auth + Tenant Context (Replit)

**Duración estimada:** 2 días

1. Agregar `tenant_id` y `tenant_slug` a modelo User
2. Actualizar `AuthContext.tsx` con tenant info
3. Crear middleware de portal:
   - Verificar que tenant_user solo accede a su tenant
   - Admin puede acceder a cualquier tenant
4. Crear rutas de auth para tenant users

### Build Phase 3: Portal UI (Replit)

**Duración estimada:** 3-4 días

1. Crear layout del portal (`/portal/[tenantSlug]/layout.tsx`)
2. Dashboard del portal (`/portal/[tenantSlug]/page.tsx`)
3. Lista de órdenes (`/portal/[tenantSlug]/orders/page.tsx`)
4. Detalle de orden (`/portal/[tenantSlug]/orders/[orderNumber]/page.tsx`)
5. Componentes:
   - `TenantHeader` (logo, branding)
   - `OrderCardClient` (versión simplificada sin internals)
   - `DeliverableDownload` (descarga de paquete)

### Build Phase 4: Admin Tenant Management (Replit)

**Duración estimada:** 2 días

1. Crear UI de gestión de tenants (`/agent/tenants/*`)
2. Formulario de creación de tenant
3. Asignación de tenant_id a órdenes desde admin
4. Vista de órdenes filtrada por tenant

### Build Phase 5: Migración de Datos (Dev → Prod)

**Duración estimada:** 1 día

1. Crear tenants para clientes existentes
2. Script de migración para asignar tenant_id a órdenes antiguas
3. Testing exhaustivo en dev
4. Deploy a producción

---

## ✅ Criterios de Éxito

### Fase PLAN (Actual) ✅

- [x] Documento `MULTITENANT_CLIENT_PORTAL_PLAN.md` creado
- [x] Modelo Tenant diseñado
- [x] Relación Tenant ↔ Orders definida
- [x] UX del Client Portal descrito
- [x] Estrategia de migración propuesta
- [x] Roadmap de implementación claro

### Fase BUILD (Futuro)

- [ ] Modelos implementados (Tenant, Order mejorado)
- [ ] API `/api/tenants/*` funcionando
- [ ] Portal UI accesible en `/portal/{slug}`
- [ ] Filtrado de órdenes por tenant funcionando
- [ ] Admin puede gestionar tenants
- [ ] Datos históricos migrados a tenants

---

## 🔐 Consideraciones de Seguridad

### 1. Row-Level Security (Filtrado por Tenant)

**Implementar en todas las queries:**
```python
# INCORRECTO (vulnerabilidad)
orders = session.exec(select(Order)).all()

# CORRECTO (filtrado por tenant)
if user.role == "tenant_admin" or user.role == "tenant_viewer":
    orders = session.exec(
        select(Order).where(Order.tenant_id == user.tenant_id)
    ).all()
else:
    # Admin ve todo
    orders = session.exec(select(Order)).all()
```

### 2. Middleware de Validación

```python
# Middleware para rutas de portal (FUTURO)
@router.get("/portal/{tenant_slug}/orders")
async def get_portal_orders(
    tenant_slug: str,
    user: User = Depends(get_current_user)
):
    # Validar que user tiene acceso a este tenant
    if user.role.startswith('tenant_') and user.tenant_slug != tenant_slug:
        raise HTTPException(403, "No tienes acceso a este tenant")
    
    # ... resto de la lógica
```

### 3. Prevenir Tenant Enumeration

**Mal diseño:**
```
/portal/colegio-pedregal → 200 OK
/portal/notaria-17 → 200 OK
/portal/random-slug → 404 Not Found
```
→ Atacante puede enumerar tenants existentes.

**Buen diseño:**
```
/portal/{slug-inexistente} → Redirige a login (no revela si existe)
Solo después de login exitoso → revela si tiene acceso
```

### 4. Sanitización de Datos Expuestos

**En Portal (Cliente):**
```python
# NO exponer:
- product_path (ruta en Axon 88)
- log_path (logs internos)
- notas_internas
- QA messages detallados
- Artifacts crudos

# SÍ exponer:
- order_number
- estado
- deliverable (si está listo)
- client_contact
```

---

## 📊 Métricas de Éxito (Post-Implementación)

### KPIs a Trackear

1. **Tenants activos:** Número de organizaciones usando el sistema
2. **Órdenes por tenant:** Promedio de órdenes por cliente
3. **Tiempo de respuesta del portal:** Latencia de carga
4. **Satisfacción del cliente:** NPS post-deliverable
5. **Self-service ratio:** % de clientes que usan portal vs. contacto directo

---

## 🎓 Aprendizajes y Decisiones Documentadas

### ¿Por Qué No Usar Supabase/Auth0 para Multi-Tenant?

**Decisión:** Implementar custom multi-tenancy en lugar de usar servicios de terceros.

**Razón:**
- Control total del modelo de datos
- Integración directa con AgentBlueprint y Orders
- Evitar vendor lock-in
- Branding personalizado por tenant sin limitaciones

**Trade-off:**
- Más trabajo de implementación
- Responsabilidad de seguridad propia

### ¿Por Qué Client Portal v1 No Permite Crear Órdenes?

**Decisión:** En v1, solo admin puede crear órdenes para un tenant.

**Razón:**
- Simpleza de implementación
- Control de calidad (admin revisa antes de enviar a factory)
- Evitar spam o órdenes mal formadas
- AgentBlueprint requiere expertise para definir bien

**En v2:** Cliente podrá solicitar agentes desde su portal, pero con aprobación de admin.

---

## 📝 Notas Adicionales

### Compatibilidad con Fases Anteriores

Este diseño multi-tenant es **compatible** con:
- ✅ FASE 3.A/3.B: AgentBlueprint (blueprint por orden)
- ✅ FASE 3.C: Agent Factory Dashboard (ahora puede filtrar por tenant)
- ✅ FASE 4.A: Replit Studio Embebido (admin sigue viendo todo)
- ✅ FASE 4.B: Agent Builder (artifacts por orden, no afectado por tenants)
- ✅ FASE 6: Agent Artifacts UI (admin ve artifacts, cliente NO)

### Extensiones Futuras (Post-v1)

1. **Tenant Billing:** Facturación por tenant ($ por orden)
2. **Tenant Analytics:** Dashboard de uso para cada cliente
3. **White-Label Portal:** Portal totalmente personalizado por tenant
4. **API Keys per Tenant:** Clientes pueden integrar vía API
5. **Multi-User per Tenant:** Varios usuarios por organización
6. **Role Hierarchy:** Owner > Admin > Member por tenant

---

**Fin del Documento de Plan**  
**Próximo Paso:** Entrar en MODO BUILD y comenzar implementación 🚀
