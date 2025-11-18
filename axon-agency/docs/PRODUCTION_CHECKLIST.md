# AXON Agency - Production Deployment Checklist

**Multi-Tenant System - Production Readiness Guide**  
**Version:** 1.0  
**Last Updated:** November 17, 2025  
**Status:** Ready for Production Deployment

---

## 📋 Overview

This document provides a comprehensive checklist for deploying the AXON Agency multi-tenant system to production. The system has been hardened with tenant isolation, admin-only controls, and secure authentication flows.

**CRITICAL:** Read this entire document before initiating production deployment.

---

## 🔐 Phase 1: DEV_MODE → PROD_MODE Migration

### 1.1 Disable Development Mode

Development mode enables authentication bypasses and should NEVER be active in production.

**Backend Configuration (`axon-agency/apps/api/.env`):**

```bash
# CRITICAL: Set these values for production
DEV_MODE=false
PRODUCTION_MODE=true

# Verify dev mode is disabled
# The API will show critical warnings on startup if dev_mode is still enabled
```

**What DEV_MODE controls:**
- ✅ Development token endpoint (`POST /api/auth/dev/token`)
- ✅ Mock user bypass in `get_user_from_token()`
- ✅ WebSocket authentication bypass
- ✅ Security validation warnings at startup

**Verification:**

```bash
# Start the API and check logs
cd axon-agency/apps/api
uvicorn app.main:socket_app --host 0.0.0.0 --port 8080

# You should NOT see this warning:
# ⚠️  SECURITY WARNING: DEV_MODE IS ENABLED  ⚠️
```

**Test dev token is disabled:**

```bash
# This should return 404 in production
curl -X POST http://localhost:8080/api/auth/dev/token

# Expected response (production):
# {"detail": "Not available in production mode"}
```

---

### 1.2 Configure Production Authentication

Replace development tokens with real JWT-based authentication.

**Environment Variables (`axon-agency/apps/api/.env`):**

```bash
# JWT Configuration
JWT_SECRET="your-super-secret-production-key-min-32-chars"
JWT_ISS="axon"
JWT_AUD="control"
JWT_EXPIRATION_MINUTES=1440

# CRITICAL: Never use the default value in production!
# The API will refuse to start if JWT_SECRET="change-me-in-production" and PRODUCTION_MODE=true
```

**Generate a secure JWT secret:**

```bash
# Option 1: OpenSSL
openssl rand -base64 48

# Option 2: Python
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Set environment variable:**

```bash
# In Replit Secrets or .env file
export JWT_SECRET="<generated-secret-here>"
```

---

### 1.3 Configure Required API Keys

Validate all required secrets are configured before deployment.

**Required Secrets (`axon-agency/apps/api/.env`):**

```bash
# OpenAI API (for GPT models)
OPENAI_API_KEY="sk-proj-..."
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_MODEL="gpt-4o-mini"

# Google Gemini API (for Gemini models)
GEMINI_API_KEY="AIza..."
GEMINI_MODEL="gemini-2.0-flash-exp"

# Database
DATABASE_URL="sqlite:///./axon.db"  # or PostgreSQL for production

# Optional: Other services
N8N_API_KEY="..."  # if using n8n workflows
AXON_CORE_API_TOKEN="..."  # if using Axon Core integration
```

**Verification Script:**

```bash
# Check secrets are configured
cd axon-agency/apps/api
python3 << 'EOF'
from app.core.config import settings

print("🔍 Checking production secrets...")
print(f"✓ JWT_SECRET: {'✅ SET' if settings.jwt_secret != 'change-me-in-production' else '❌ DEFAULT'}")
print(f"✓ OPENAI_API_KEY: {'✅ SET' if settings.openai_api_key else '❌ MISSING'}")
print(f"✓ GEMINI_API_KEY: {'✅ SET' if settings.gemini_api_key else '❌ MISSING'}")
print(f"✓ DEV_MODE: {'❌ ENABLED' if settings.dev_mode else '✅ DISABLED'}")
print(f"✓ PRODUCTION_MODE: {'✅ ENABLED' if settings.production_mode else '❌ DISABLED'}")
EOF
```

---

### 1.4 Configure CORS for Production Domain

Update CORS settings to allow your production frontend domain.

**Backend Configuration (`axon-agency/apps/api/.env`):**

```bash
# Development (default)
ALLOWED_ORIGINS="http://localhost:3000"

# Production (update with your domain)
ALLOWED_ORIGINS="https://your-production-domain.com,https://www.your-production-domain.com"

# Multiple domains (comma-separated)
ALLOWED_ORIGINS="https://app.example.com,https://portal.example.com"
```

**Code Reference:** `axon-agency/apps/api/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Parsed from ALLOWED_ORIGINS env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Verification:**

```bash
# Test CORS headers from production domain
curl -H "Origin: https://your-production-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8080/api/health

# Should return Access-Control-Allow-Origin header
```

---

## 🛡️ Phase 2: Security Review Summary

### 2.1 Security Fixes Applied (Phase 5)

The following security hardening was implemented in the multi-tenant system:

#### ✅ Backend Security Implementations

**1. Admin-Only Tenant Management (`/api/tenants`)**
- **File:** `axon-agency/apps/api/app/routers/tenants.py`
- **Implementation:** `require_admin()` helper function
- **Protected Endpoints:**
  - `GET /api/tenants` - List all tenants (admin only)
  - `GET /api/tenants/{id}` - Get tenant details (admin only)
  - `POST /api/tenants` - Create tenant (admin only)
  - `PUT /api/tenants/{id}` - Update tenant (admin only)
  - `DELETE /api/tenants/{id}` - Delete tenant (admin only)

**Code snippet:**
```python
def require_admin(current_user: TokenData, session: Session) -> None:
    """Verify user is admin. Raises HTTPException if not."""
    user = get_user_from_token(current_user, session)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
```

**2. Tenant-Scoped Order Access (`/api/orders/{id}`)**
- **File:** `axon-agency/apps/api/app/routers/orders.py`
- **Implementation:** `verify_order_access()` function with multi-level access control
- **Access Rules:**
  - **Admin users:** Can access ANY order (all tenants)
  - **Tenant-bound users:** Can ONLY access orders from their tenant (`order.tenant_id == user.tenant_id`)
  - **Legacy users:** Can only access orders without tenant_id (backward compatible)

**Code snippet:**
```python
def verify_order_access(order: Order, current_user: TokenData, session: Session) -> None:
    """Verify user has access to this order."""
    user = get_user_from_token(current_user, session)
    
    if user.role == "admin":
        return  # Admin can access all orders
    
    if user.tenant_id:
        if order.tenant_id != user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
```

**3. Automatic Tenant Filtering (`GET /api/orders`)**
- **Implementation:** Automatic query filter injection based on user role
- **Behavior:**
  - **Admin:** Can see all orders, optional `?tenant_id=X` filter
  - **Tenant user:** Automatically filtered to `WHERE tenant_id = user.tenant_id` (cannot override)
  - **Legacy user:** Sees all orders (backward compatible)

**4. Deliverable Path Sanitization (Client Portal)**
- **File:** `axon-agency/apps/web/app/portal/[tenantSlug]/orders/[id]/page.tsx`
- **Security Fix:** Deliverable paths sanitized to show only filenames
- **Implementation:** `.split('/').pop()` to extract basename only
- **Prevents:** Exposure of internal filesystem paths to clients

#### ✅ Frontend Security Implementations

**1. Admin-Only UI Components (`<AdminOnly>` wrapper)**
- **File:** `axon-agency/apps/web/components/auth/RoleGuard.tsx`
- **Protected Pages:**
  - `/agent/tenants` - Tenant management dashboard
  - `/agent/tenants/[id]` - Tenant detail/edit page
  - `/agent/factory` - Agent Factory dashboard

**Code snippet:**
```tsx
export function AdminOnly({ children, fallback = null }: RoleGuardProps) {
  const { isAdmin, isLoading } = useAuth();
  
  if (isLoading) return null;
  if (!isAdmin) return <>{fallback}</>;
  
  return <>{children}</>;
}
```

**2. Tenant-Only UI Components (`<TenantOnly>` wrapper)**
- **Protected Routes:** `/portal/[tenantSlug]/*` (client portal)
- **Validation:** Tenant users can only access their own slug

**3. Client Portal Data Sanitization**
- **Hidden from clients:** QA status, agent artifacts, internal filesystem paths
- **Shown to clients:** Order status, product info, sanitized deliverable filenames only

---

### 2.2 Verified Security Posture

#### ✅ Multi-Tenant Data Isolation

**Tenant Isolation Matrix:**

| User Role | Can Access | Cannot Access |
|-----------|-----------|---------------|
| **Admin** | All tenants, all orders | N/A |
| **Tenant User** | Own tenant orders only | Other tenants' data |
| **Legacy User** | Legacy orders (no tenant_id) | Tenant-scoped orders |

**Database-Level Isolation:**
- Tenants table: UUID primary key, unique slug constraint
- Orders table: `tenant_id` foreign key (nullable for backward compatibility)
- Users table: `tenant_id` foreign key (nullable)
- Indexes: `idx_orders_tenant_id`, `idx_users_tenant_id`, `idx_tenants_slug`

**Application-Level Isolation:**
- Automatic query filtering in `GET /api/orders`
- Access validation in `GET /api/orders/{id}`
- Frontend route guards (`<AdminOnly>`, `<TenantOnly>`)

#### ✅ Backend Admin-Only Endpoints

**Protected API Routes:**

| Endpoint | Method | Auth Required | Role Required |
|----------|--------|---------------|---------------|
| `/api/tenants` | GET | ✅ JWT | Admin |
| `/api/tenants` | POST | ✅ JWT | Admin |
| `/api/tenants/{id}` | GET | ✅ JWT | Admin |
| `/api/tenants/{id}` | PUT | ✅ JWT | Admin |
| `/api/tenants/{id}` | DELETE | ✅ JWT | Admin |
| `/api/orders` | GET | ✅ JWT | Any (auto-filtered) |
| `/api/orders/{id}` | GET | ✅ JWT | Owner or Admin |
| `/api/orders` | POST | ✅ JWT | Any |
| `/api/orders/{id}` | PATCH | ✅ JWT | Internal use |

#### ✅ Frontend Admin UI Protection

**Protected Pages:**

| Page | Route | Guard | Fallback |
|------|-------|-------|----------|
| Tenant List | `/agent/tenants` | `<AdminOnly>` | "Access Denied" |
| Tenant Detail | `/agent/tenants/[id]` | `<AdminOnly>` | "Access Denied" |
| Factory Dashboard | `/agent/factory` | `<AdminOnly>` | "Access Denied" |
| Orders Dashboard | `/agent/orders` | ⚠️ No Guard | Recommended to add |

**Status:** All critical admin UIs are protected. `/agent/orders` should ideally have `<AdminOnly>` wrapper for consistency (non-critical finding).

---

### 2.3 Minor Findings (Non-Critical)

#### ⚠️ Finding 1: `/agent/orders` Missing AdminOnly Guard

**Severity:** Low  
**Status:** Non-blocking for production  

**Description:**  
The orders dashboard at `/agent/orders` page does not have an `<AdminOnly>` wrapper, unlike `/agent/tenants` and `/agent/factory`. While the backend correctly enforces tenant scoping via `verify_order_access()`, the frontend could show "Access Denied" earlier for non-admin users.

**Recommendation:**
```tsx
// axon-agency/apps/web/app/agent/orders/page.tsx
import { AdminOnly } from '@/components/auth/RoleGuard';

export default function OrdersPage() {
  return (
    <AdminOnly fallback={<div>Access Denied</div>}>
      {/* existing page content */}
    </AdminOnly>
  );
}
```

**Mitigation:** Backend API correctly enforces access control, so this is a UX improvement rather than a security vulnerability.

---

## 🧪 Phase 3: Multi-Tenant Smoke Tests

### 3.1 Authentication Flow Tests

#### Test 1: Admin Login

```bash
# 1. Register admin user (first-time setup)
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@axon.agency",
    "password": "SecureAdminPass123!",
    "full_name": "Admin User"
  }'

# 2. Update user role to admin (via database or admin endpoint)
# NOTE: You'll need to manually update the role in the database for the first admin user

# 3. Login as admin
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "SecureAdminPass123!"
  }'

# Expected response:
# {
#   "access_token": "eyJ...",
#   "token_type": "bearer",
#   "user": {
#     "id": 1,
#     "username": "admin",
#     "email": "admin@axon.agency",
#     "role": "admin"
#   }
# }

# Save the access_token for subsequent requests
export ADMIN_TOKEN="<access_token_here>"

# 4. Verify admin user info
curl -X GET http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected response:
# {
#   "id": 1,
#   "username": "admin",
#   "email": "admin@axon.agency",
#   "role": "admin",
#   "is_admin": true,
#   "tenant_id": null,
#   "tenant_slug": null,
#   "tenant_name": null
# }
```

#### Test 2: Tenant User Login

```bash
# 1. Create a tenant (as admin)
curl -X POST http://localhost:8080/api/tenants \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "test-school",
    "name": "Test School",
    "business_type": "school",
    "contact_email": "contact@testschool.com",
    "contact_name": "School Admin",
    "contact_phone": "+1234567890"
  }'

# Save tenant_id from response
export TENANT_ID="<tenant_id_here>"

# 2. Register tenant user
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "school_user",
    "email": "user@testschool.com",
    "password": "SchoolUserPass123!",
    "full_name": "School User"
  }'

# 3. Assign user to tenant (manual DB update for now)
# UPDATE users SET tenant_id = '<tenant_id>' WHERE username = 'school_user';

# 4. Login as tenant user
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "school_user",
    "password": "SchoolUserPass123!"
  }'

# Save tenant user token
export TENANT_TOKEN="<access_token_here>"

# 5. Verify tenant user info
curl -X GET http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer $TENANT_TOKEN"

# Expected response:
# {
#   "id": 2,
#   "username": "school_user",
#   "email": "user@testschool.com",
#   "role": "viewer",
#   "is_admin": false,
#   "tenant_id": "<tenant_id>",
#   "tenant_slug": "test-school",
#   "tenant_name": "Test School"
# }
```

---

### 3.2 Tenant Isolation Tests

#### Test 3: Verify Tenant User Cannot Access Other Tenant's Data

```bash
# Setup: Create two tenants and orders
# Tenant 1: test-school
# Tenant 2: other-school

# 1. Create order for Tenant 1 (as admin)
curl -X POST http://localhost:8080/api/orders \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "autopilot_blog_seo",
    "nombre_producto": "School Blog",
    "tenant_id": "<tenant_1_id>",
    "datos_cliente": {
      "sitio_web": "https://testschool.com"
    }
  }'

# Save order_id
export ORDER_1_ID="<order_id_here>"

# 2. Create order for Tenant 2 (as admin)
curl -X POST http://localhost:8080/api/orders \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "autopilot_blog_seo",
    "nombre_producto": "Other School Blog",
    "tenant_id": "<tenant_2_id>",
    "datos_cliente": {
      "sitio_web": "https://otherschool.com"
    }
  }'

export ORDER_2_ID="<order_id_here>"

# 3. Tenant 1 user tries to list orders
curl -X GET http://localhost:8080/api/orders \
  -H "Authorization: Bearer $TENANT_TOKEN"

# Expected: Should ONLY see orders with tenant_id = tenant_1_id
# Should NOT see orders from tenant_2_id

# 4. Tenant 1 user tries to access Tenant 2's order directly
curl -X GET http://localhost:8080/api/orders/$ORDER_2_ID \
  -H "Authorization: Bearer $TENANT_TOKEN"

# Expected response (403 Forbidden):
# {
#   "detail": "You don't have access to this order"
# }

# 5. Tenant 1 user accesses own order
curl -X GET http://localhost:8080/api/orders/$ORDER_1_ID \
  -H "Authorization: Bearer $TENANT_TOKEN"

# Expected: Success (200 OK) with full order details
```

---

### 3.3 Admin Access Tests

#### Test 4: Verify Admin Can Access All Tenants

```bash
# 1. Admin lists all tenants
curl -X GET http://localhost:8080/api/tenants \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: Array of all tenants (both tenant_1 and tenant_2)

# 2. Admin lists all orders
curl -X GET http://localhost:8080/api/orders \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: Array of ALL orders (from all tenants + legacy orders)

# 3. Admin filters orders by specific tenant
curl -X GET "http://localhost:8080/api/orders?tenant_id=<tenant_1_id>" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: Only orders from tenant_1

# 4. Admin accesses any order directly
curl -X GET http://localhost:8080/api/orders/$ORDER_2_ID \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: Success (200 OK) - admin can access any order

# 5. Non-admin tries to access tenant management
curl -X GET http://localhost:8080/api/tenants \
  -H "Authorization: Bearer $TENANT_TOKEN"

# Expected response (403 Forbidden):
# {
#   "detail": "Admin access required"
# }
```

---

### 3.4 Client Portal Tests

#### Test 5: Portal Functionality

**Frontend Tests (manual in browser):**

1. **Login as tenant user:**
   - Navigate to frontend (http://localhost:3000)
   - Login with tenant user credentials
   - Should auto-redirect to `/portal/test-school`

2. **Portal Dashboard:**
   - Navigate to `/portal/test-school`
   - Verify stats cards show correct counts (Total, In Progress, Ready, Failed)
   - Verify recent orders table shows only tenant's orders
   - Click "Ver todas las órdenes" → should navigate to orders list

3. **Portal Orders List:**
   - Navigate to `/portal/test-school/orders`
   - Verify table shows only orders from this tenant
   - Test estado filter (All / Listo / En Progreso / Fallido)
   - Click on an order → should navigate to detail page

4. **Portal Order Detail:**
   - Navigate to `/portal/test-school/orders/<order_id>`
   - Verify order info is displayed (number, estado, dates, product)
   - Verify deliverables show ONLY sanitized filenames (no internal paths)
   - Verify NO QA status or agent artifacts are visible

5. **Tenant Slug Validation:**
   - As tenant_1 user, try to access `/portal/other-school`
   - Should redirect or show "Access Denied"
   - Admin user can access any slug for debugging

**API Tests:**

```bash
# Tenant user accesses portal orders via API
curl -X GET http://localhost:8080/api/orders \
  -H "Authorization: Bearer $TENANT_TOKEN"

# Should return filtered orders (tenant's orders only)
```

---

### 3.5 Admin UI Tests

#### Test 6: Admin Dashboard Access

**Frontend Tests (manual in browser):**

1. **Login as admin:**
   - Navigate to http://localhost:3000
   - Login with admin credentials
   - Should see full sidebar with admin options

2. **Tenant Management UI (`/agent/tenants`):**
   - Navigate to `/agent/tenants`
   - Verify stats cards (Total, Active, Inactive)
   - Verify tenant list table
   - Click "Edit" → should navigate to detail page
   - Click "View Portal" → should open `/portal/{slug}` in new tab

3. **Tenant Detail UI (`/agent/tenants/[id]`):**
   - Navigate to `/agent/tenants/<tenant_id>`
   - Verify tenant info card
   - Verify orders summary card (tenant-specific stats)
   - Verify recent orders table
   - Test "Edit" form (update tenant name, save)
   - Test "Delete" button (with confirmation dialog)

4. **Factory Dashboard (`/agent/factory`):**
   - Navigate to `/agent/factory`
   - Verify access (should be admin-only)
   - Non-admin should see "Access Denied"

5. **Orders Dashboard (`/agent/orders`):**
   - Navigate to `/agent/orders`
   - Currently accessible to all users
   - Verify backend enforces tenant filtering for non-admins

**Access Control Tests:**

```bash
# Non-admin tries to access admin UI
# (Frontend should show "Access Denied" before making API call)

# Backend verification:
curl -X GET http://localhost:8080/api/tenants \
  -H "Authorization: Bearer $TENANT_TOKEN"

# Expected: 403 Forbidden
```

---

## 💾 Phase 4: Database Migration Checklist

### 4.1 Pre-Migration Backup

**CRITICAL:** Always backup your database before running migrations.

```bash
# Navigate to API directory
cd axon-agency/apps/api

# Create backup with timestamp
BACKUP_NAME="axon_backup_$(date +%Y%m%d_%H%M%S).db"
cp axon.db backups/$BACKUP_NAME

# Verify backup
ls -lh backups/$BACKUP_NAME

# Create backups directory if it doesn't exist
mkdir -p backups
```

**Backup Strategy:**

- **Development:** Backup before each migration
- **Staging:** Daily backups + pre-migration backup
- **Production:** Automated hourly backups + manual pre-migration backup

---

### 4.2 Migration Execution

#### Phase 1 Migration: Tenants + Orders

**Purpose:** Create `tenants` table and add `tenant_id` to `orders`

```bash
cd axon-agency/apps/api

# Run Phase 1 migration
python3 migrate_multitenant.py

# Expected output:
# Connecting to database: /path/to/axon.db
# Step 1: Creating 'tenants' table...
# ✓ Table 'tenants' created or already exists
# ✓ Indexes on 'tenants' created
# Step 2: Adding 'tenant_id' column to 'orders' table...
# ✓ Column 'tenant_id' added to 'orders'
# ✓ Index on 'orders.tenant_id' created
# ✅ MIGRATION COMPLETED SUCCESSFULLY
```

**Verify Phase 1:**

```bash
# Check tenants table exists
sqlite3 axon.db "SELECT name FROM sqlite_master WHERE type='table' AND name='tenants';"

# Expected: tenants

# Check orders.tenant_id column exists
sqlite3 axon.db "PRAGMA table_info(orders);" | grep tenant_id

# Expected: tenant_id column with type VARCHAR
```

#### Phase 2 Migration: Users + Tenant Context

**Purpose:** Add `tenant_id` to `users` table

```bash
cd axon-agency/apps/api

# Run Phase 2 migration
python3 migrate_multitenant_phase2.py

# Expected output:
# Phase 2: Adding 'tenant_id' column to 'users' table...
# ✓ Column 'tenant_id' added to 'users'
# ✓ Index on 'users.tenant_id' created
# ✅ PHASE 2 MIGRATION COMPLETED SUCCESSFULLY
```

**Verify Phase 2:**

```bash
# Check users.tenant_id column exists
sqlite3 axon.db "PRAGMA table_info(users);" | grep tenant_id

# Expected: tenant_id column with type VARCHAR
```

---

### 4.3 Data Migration (Legacy Orders)

If you have existing orders without `tenant_id`, you may need to assign them to tenants.

**Option 1: Assign All Legacy Orders to a Default Tenant**

```bash
# 1. Create a "Legacy" tenant
sqlite3 axon.db << 'EOF'
INSERT INTO tenants (id, slug, name, business_type, contact_email, active, created_at, updated_at)
VALUES (
  'legacy-tenant-id',
  'legacy',
  'Legacy Orders',
  'general',
  'admin@axon.agency',
  1,
  datetime('now'),
  datetime('now')
);
EOF

# 2. Update all orders with NULL tenant_id
sqlite3 axon.db << 'EOF'
UPDATE orders 
SET tenant_id = 'legacy-tenant-id' 
WHERE tenant_id IS NULL;
EOF

# 3. Verify
sqlite3 axon.db "SELECT COUNT(*) FROM orders WHERE tenant_id = 'legacy-tenant-id';"
```

**Option 2: Manual Assignment (Recommended)**

Review legacy orders manually and assign to appropriate tenants:

```bash
# List all orders without tenant_id
sqlite3 axon.db << 'EOF'
SELECT id, order_number, nombre_producto, datos_cliente 
FROM orders 
WHERE tenant_id IS NULL;
EOF

# Assign specific orders to specific tenants
sqlite3 axon.db << 'EOF'
UPDATE orders 
SET tenant_id = '<specific-tenant-id>' 
WHERE id = '<order-id>';
EOF
```

**Option 3: Leave as NULL (Backward Compatible)**

The system supports `tenant_id = NULL` for legacy orders. Admin users can still access them.

---

### 4.4 Post-Migration Validation

```bash
# Check database schema
sqlite3 axon.db << 'EOF'
.schema tenants
.schema orders
.schema users
EOF

# Verify data integrity
sqlite3 axon.db << 'EOF'
-- Count tenants
SELECT COUNT(*) as total_tenants FROM tenants;

-- Count orders by tenant
SELECT 
  COALESCE(tenant_id, 'NULL') as tenant,
  COUNT(*) as order_count 
FROM orders 
GROUP BY tenant_id;

-- Count users by tenant
SELECT 
  COALESCE(tenant_id, 'NULL') as tenant,
  COUNT(*) as user_count 
FROM users 
GROUP BY tenant_id;
EOF
```

**Expected Results:**
- ✅ `tenants` table exists with data
- ✅ `orders` table has `tenant_id` column
- ✅ `users` table has `tenant_id` column
- ✅ Indexes created on `tenant_id` columns
- ✅ No broken foreign key constraints

---

## ✅ Phase 5: Production Readiness Checklist

### 5.1 Environment Configuration

- [ ] **DEV_MODE disabled** (`DEV_MODE=false` in `.env`)
- [ ] **PRODUCTION_MODE enabled** (`PRODUCTION_MODE=true` in `.env`)
- [ ] **JWT_SECRET configured** (not default value, min 32 chars)
- [ ] **OPENAI_API_KEY configured** (valid API key)
- [ ] **GEMINI_API_KEY configured** (valid API key)
- [ ] **CORS configured** (`ALLOWED_ORIGINS` set to production domain)
- [ ] **DATABASE_URL configured** (PostgreSQL for production recommended)
- [ ] **No dev tokens accessible** (`POST /api/auth/dev/token` returns 404)

**Verification Command:**

```bash
cd axon-agency/apps/api
python3 << 'EOF'
from app.core.config import settings

checks = [
    ("DEV_MODE disabled", not settings.dev_mode),
    ("PRODUCTION_MODE enabled", settings.production_mode),
    ("JWT_SECRET set", settings.jwt_secret != "change-me-in-production"),
    ("OPENAI_API_KEY set", bool(settings.openai_api_key)),
    ("GEMINI_API_KEY set", bool(settings.gemini_api_key)),
    ("CORS configured", "localhost" not in str(settings.allowed_origins)),
]

print("\n🔍 Production Readiness Check:\n")
for check_name, passed in checks:
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")

all_passed = all(passed for _, passed in checks)
print(f"\n{'✅ All checks passed!' if all_passed else '❌ Some checks failed!'}")
EOF
```

---

### 5.2 Database Migration

- [ ] **Database backup created** (timestamped backup in `backups/` directory)
- [ ] **Phase 1 migration executed** (`migrate_multitenant.py` completed)
- [ ] **Phase 2 migration executed** (`migrate_multitenant_phase2.py` completed)
- [ ] **Tenants table verified** (table exists with correct schema)
- [ ] **Orders.tenant_id column verified** (column exists, nullable)
- [ ] **Users.tenant_id column verified** (column exists, nullable)
- [ ] **Legacy data migrated** (NULL tenant_ids assigned if needed)
- [ ] **Indexes verified** (idx_orders_tenant_id, idx_users_tenant_id, idx_tenants_slug)

**Verification Command:**

```bash
cd axon-agency/apps/api
sqlite3 axon.db << 'EOF'
-- Check all required tables exist
SELECT 'tenants' as table_name, COUNT(*) as exists FROM sqlite_master WHERE type='table' AND name='tenants'
UNION ALL
SELECT 'orders', COUNT(*) FROM sqlite_master WHERE type='table' AND name='orders'
UNION ALL
SELECT 'users', COUNT(*) FROM sqlite_master WHERE type='table' AND name='users';

-- Check all required indexes exist
SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%tenant%';
EOF
```

---

### 5.3 Multi-Tenant Security Tests

- [ ] **Admin login test passed** (admin can authenticate and get JWT)
- [ ] **Tenant user login test passed** (tenant user can authenticate)
- [ ] **Tenant isolation test passed** (tenant1 cannot access tenant2 data)
- [ ] **Admin access test passed** (admin can access all tenants)
- [ ] **Order access control test passed** (`verify_order_access()` enforced)
- [ ] **Tenant management auth test passed** (`require_admin()` enforced)
- [ ] **Frontend AdminOnly guard test passed** (non-admins see "Access Denied")
- [ ] **Client portal test passed** (tenant users can access portal)
- [ ] **Deliverable sanitization test passed** (no internal paths exposed)

**Quick Test Script:**

```bash
# Save as test_security.sh
#!/bin/bash

echo "🧪 Running security tests..."

# Test 1: Dev token disabled
echo "Test 1: Dev token disabled"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8080/api/auth/dev/token)
if [ "$RESPONSE" == "404" ]; then
  echo "✅ Dev token disabled"
else
  echo "❌ Dev token still accessible (got $RESPONSE)"
fi

# Test 2: Admin can access tenants
echo "Test 2: Admin access to tenants"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET http://localhost:8080/api/tenants -H "Authorization: Bearer $ADMIN_TOKEN")
if [ "$RESPONSE" == "200" ]; then
  echo "✅ Admin can access tenants"
else
  echo "❌ Admin cannot access tenants (got $RESPONSE)"
fi

# Test 3: Non-admin cannot access tenants
echo "Test 3: Non-admin blocked from tenants"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET http://localhost:8080/api/tenants -H "Authorization: Bearer $TENANT_TOKEN")
if [ "$RESPONSE" == "403" ]; then
  echo "✅ Non-admin blocked from tenants"
else
  echo "❌ Non-admin can access tenants (got $RESPONSE)"
fi

echo ""
echo "🎯 Security tests completed"
```

---

### 5.4 Performance & Monitoring

- [ ] **API response time < 200ms** (for GET requests)
- [ ] **Database query optimization** (indexes on tenant_id)
- [ ] **Logging configured** (info level for production)
- [ ] **Error tracking configured** (Sentry or similar)
- [ ] **Health check endpoint responding** (`GET /health`)
- [ ] **Metrics endpoint accessible** (admin-only)

**Performance Test:**

```bash
# Test API response times
time curl -X GET http://localhost:8080/api/health
time curl -X GET http://localhost:8080/api/orders -H "Authorization: Bearer $ADMIN_TOKEN"
time curl -X GET http://localhost:8080/api/tenants -H "Authorization: Bearer $ADMIN_TOKEN"

# All should be < 200ms
```

---

### 5.5 Error Handling & Edge Cases

- [ ] **Invalid tenant_id handling** (404 error returned)
- [ ] **Expired JWT handling** (401 error returned)
- [ ] **Missing auth header handling** (401 error returned)
- [ ] **Cross-tenant access attempts logged** (security audit trail)
- [ ] **Rate limiting configured** (to prevent abuse)
- [ ] **Input validation working** (SQL injection, XSS prevention)

**Error Handling Tests:**

```bash
# Test 1: Invalid tenant ID
curl -X GET http://localhost:8080/api/tenants/invalid-id \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 404 Not Found

# Test 2: Expired token
curl -X GET http://localhost:8080/api/tenants \
  -H "Authorization: Bearer expired-token-here"

# Expected: 401 Unauthorized

# Test 3: Missing auth header
curl -X GET http://localhost:8080/api/tenants

# Expected: 401 Unauthorized
```

---

### 5.6 Deployment Verification

- [ ] **Backend deployed and running** (API accessible)
- [ ] **Frontend deployed and running** (UI accessible)
- [ ] **Database persistent** (data not lost on restart)
- [ ] **Environment variables loaded** (secrets not hardcoded)
- [ ] **HTTPS enabled** (SSL/TLS configured)
- [ ] **Domain configured** (DNS pointing to deployment)
- [ ] **CORS working** (frontend can call backend)
- [ ] **WebSocket working** (for real-time features)

**Deployment Verification:**

```bash
# Check API is live
curl https://api.your-domain.com/health

# Check frontend is live
curl https://your-domain.com

# Check CORS headers
curl -H "Origin: https://your-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://api.your-domain.com/api/health
```

---

## 🚀 Phase 6: Go-Live Procedure

### 6.1 Pre-Launch Checklist

**24 Hours Before:**
- [ ] Review all checklist items above
- [ ] Create final database backup
- [ ] Test rollback procedure
- [ ] Notify stakeholders of launch window

**1 Hour Before:**
- [ ] Set `DEV_MODE=false` and `PRODUCTION_MODE=true`
- [ ] Deploy backend to production
- [ ] Deploy frontend to production
- [ ] Run smoke tests

**Go-Live:**
- [ ] Monitor logs for errors
- [ ] Test auth flow end-to-end
- [ ] Test tenant isolation
- [ ] Test admin access
- [ ] Verify performance metrics

### 6.2 Post-Launch Monitoring

**First 24 Hours:**
- Monitor error rates (target: < 0.1%)
- Monitor API response times (target: < 200ms p95)
- Monitor database connections
- Monitor user authentication success rate

**First Week:**
- Review security logs for anomalies
- Check for unauthorized access attempts
- Verify tenant isolation is working
- Gather user feedback

### 6.3 Rollback Plan

If critical issues are discovered:

```bash
# 1. Stop services
systemctl stop axon-api
systemctl stop axon-web

# 2. Restore database backup
cd axon-agency/apps/api
cp axon.db axon.db.failed
cp backups/<latest-backup>.db axon.db

# 3. Revert code deployment
git revert <commit-hash>

# 4. Re-deploy
# ... deployment steps ...

# 5. Restart services
systemctl start axon-api
systemctl start axon-web
```

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue 1: "Invalid token" errors**

```bash
# Verify JWT_SECRET is correctly set
cd axon-agency/apps/api
python3 -c "from app.core.config import settings; print(f'JWT_SECRET: {settings.jwt_secret[:10]}...')"

# Re-generate token with correct secret
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "..."}'
```

**Issue 2: CORS errors in browser**

```bash
# Check ALLOWED_ORIGINS includes your frontend domain
cd axon-agency/apps/api
python3 -c "from app.core.config import settings; print(f'ALLOWED_ORIGINS: {settings.allowed_origins}')"

# Update .env if needed
echo "ALLOWED_ORIGINS=https://your-frontend-domain.com" >> .env
```

**Issue 3: Tenant user can't access portal**

- Verify `user.tenant_id` is set correctly
- Verify tenant slug matches URL (`/portal/{slug}`)
- Check browser console for auth errors

**Issue 4: Database migration failed**

```bash
# Restore from backup
cd axon-agency/apps/api
cp axon.db axon.db.failed
cp backups/<latest-backup>.db axon.db

# Re-run migration
python3 migrate_multitenant.py
python3 migrate_multitenant_phase2.py
```

---

## 📝 Production Deployment Summary

**Total Estimated Time:** 4-6 hours

| Phase | Duration | Complexity |
|-------|----------|------------|
| Environment Setup | 1 hour | Low |
| Security Review | 30 min | Low |
| Smoke Tests | 1 hour | Medium |
| Database Migration | 1 hour | Medium |
| Pre-Launch Checks | 1 hour | Medium |
| Deployment | 30 min | Low |
| Post-Launch Monitoring | 1 hour | Low |

**Recommended Team:**
- Backend Engineer (API configuration, database migration)
- Frontend Engineer (UI verification, CORS setup)
- DevOps Engineer (deployment, monitoring)
- QA Engineer (smoke tests, edge cases)

**Success Criteria:**
- ✅ All checklist items completed
- ✅ All smoke tests passed
- ✅ Zero security vulnerabilities
- ✅ API response time < 200ms
- ✅ Error rate < 0.1%

---

## 🎯 Conclusion

This production deployment checklist provides a comprehensive guide for safely deploying the AXON Agency multi-tenant system to production. Follow each section carefully, and don't skip any steps.

**Key Takeaways:**

1. **Always disable DEV_MODE** in production
2. **Always backup database** before migrations
3. **Always test tenant isolation** before go-live
4. **Always monitor logs** after deployment
5. **Always have a rollback plan** ready

**Next Steps After Production:**

1. Set up automated backups (hourly)
2. Configure monitoring/alerting (Sentry, DataDog)
3. Set up staging environment for future changes
4. Document tenant onboarding process
5. Create admin user guide

---

**Document Version:** 1.0  
**Last Updated:** November 17, 2025  
**Maintained By:** AXON Agency Team  
**Contact:** For questions or issues, contact the development team.

---

**Good luck with your deployment! 🚀**
