# Quick Setup Guide - Axon Agency

**Complete setup instructions for Development, Staging, and Production environments**

**Last Updated:** November 18, 2025

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Staging Setup](#staging-setup)
4. [Production Setup](#production-setup)
5. [Verification Steps](#verification-steps)
6. [Common Issues](#common-issues)
7. [Key Endpoints](#key-endpoints)
8. [Workflows & Commands](#workflows--commands)

---

## Prerequisites

### Required Software

| Software | Version | Purpose | Installation |
|----------|---------|---------|-------------|
| **Python** | 3.11+ | Backend API | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 20+ | Frontend web app | [nodejs.org](https://nodejs.org/) |
| **npm** | 10+ | Frontend package manager | Included with Node.js |
| **Git** | Latest | Version control | [git-scm.com](https://git-scm.com/) |

### Optional (Recommended for Production)

| Software | Version | Purpose |
|----------|---------|---------|
| **PostgreSQL** | 14+ | Production database (instead of SQLite) |
| **MongoDB** | 6.0+ | WhatsApp Sales Agent persistence |
| **Redis** | 7+ | Jobs queue and caching |

### API Keys & Services

**Minimum viable (Development):**
- OpenAI API key ([platform.openai.com](https://platform.openai.com/api-keys))

**Optional (Production/Staging):**
- Google Gemini API key ([ai.google.dev](https://ai.google.dev/))
- MongoDB Atlas cluster ([mongodb.com](https://www.mongodb.com/cloud/atlas))
- Stripe account ([stripe.com](https://stripe.com/))
- Ayrshare API key ([ayrshare.com](https://www.ayrshare.com/))
- Telegram Bot token (from [@BotFather](https://t.me/botfather))

---

## Development Setup

**Goal:** Get Axon Agency running locally with minimal configuration for development.

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/axon-agency.git
cd axon-agency
```

### Step 2: Install Backend Dependencies

```bash
cd apps/api
pip install -r requirements.txt
```

**Expected packages installed:**
- FastAPI
- uvicorn
- SQLModel
- OpenAI SDK
- Motor (MongoDB async)
- Stripe SDK
- And more...

### Step 3: Install Frontend Dependencies

```bash
cd apps/web
npm install
```

**Expected packages installed:**
- Next.js 15
- React 19
- Tailwind CSS
- shadcn/ui components
- And more...

### Step 4: Configure Backend Environment

**Create `.env` file:**

```bash
cd apps/api
cp .env.example .env
```

**Edit `apps/api/.env` with minimum configuration:**

```env
# Server
BIND=0.0.0.0
PORT=8080

# Database (SQLite for development)
DATABASE_URL=sqlite:///./axon.db

# Auth (development mode)
JWT_SECRET=dev-secret-change-in-production
DEV_MODE=true

# CORS (allow frontend)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000,http://localhost:5001

# OpenAI (REQUIRED - get from platform.openai.com)
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Optional: Google Gemini (fallback LLM)
GEMINI_API_KEY=
```

**⚠️ Important Notes:**
- `DEV_MODE=true` disables authentication for easier development
- `JWT_SECRET` should use a secure random value in production
- `DATABASE_URL` uses SQLite (no PostgreSQL required for dev)
- `OPENAI_API_KEY` is the only **required** external service

### Step 5: Configure Frontend Environment

**Create `.env.local` file:**

```bash
cd apps/web
cp .env.example .env.local
```

**Edit `apps/web/.env.local`:**

```env
# Backend API URL (must match backend port)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

### Step 6: Initialize Database

**SQLite database is auto-created on first run.** No manual migrations needed for development.

**To verify database creation:**

```bash
cd apps/api
ls -lh axon.db
# Should see: axon.db file created after first API start
```

### Step 7: Start Backend Server

**Terminal 1 - Backend:**

```bash
cd axon-agency/apps/api
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080
```

**Expected output:**

```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
⚠️  WARNING: DEV_MODE is enabled - authentication bypass active
⚠️  WARNING: Using default JWT_SECRET - change in production
INFO:     Application startup complete.
```

**Verify backend is running:**

```bash
curl http://localhost:8080/api/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

### Step 8: Start Frontend Server

**Terminal 2 - Frontend:**

```bash
cd axon-agency/apps/web
npm run dev
```

**Expected output:**

```
▲ Next.js 15.0.x
- Local:        http://localhost:5000
- Network:      http://192.168.x.x:5000

✓ Ready in 3.2s
```

**Open browser:**

```
http://localhost:5000
```

You should see the Axon Agency dashboard.

### Step 9: Verify Development Setup

**Run health checks:**

```bash
# 1. Backend API health
curl http://localhost:8080/api/health

# 2. Integrations health
curl http://localhost:8080/api/integrations/health

# 3. Get dev token (DEV_MODE only)
curl -X POST http://localhost:8080/api/auth/dev/token

# 4. Test agent chat
curl -X POST http://localhost:8080/api/agent/chat \
  -H "Authorization: Bearer <dev-token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "session_id": "test-123"}'
```

### Development Workflow

**Auto-reload is enabled:**
- Backend: Uvicorn with `--reload` watches Python files
- Frontend: Next.js with hot module replacement (HMR)

**Making changes:**
1. Edit files in `apps/api/app/` or `apps/web/`
2. Servers automatically reload
3. Refresh browser to see changes

**Stopping servers:**
- Press `CTRL+C` in each terminal

---

## Staging Setup

**Goal:** Deploy Axon Agency to a staging environment with partial production features enabled.

Staging mimics production but uses test/sandbox credentials and allows debugging.

### Step 1: Prerequisites

**Infrastructure:**
- Cloud server (AWS EC2, DigitalOcean, Replit, etc.)
- Domain/subdomain for staging (e.g., `staging.axon.agency`)
- SSL certificate (Let's Encrypt recommended)

**Services:**
- OpenAI API key (production key or separate staging key)
- Google Gemini API key (optional fallback)
- MongoDB Atlas cluster (optional for WhatsApp Sales Agent)

### Step 2: Clone & Install

Same as development setup:

```bash
git clone https://github.com/your-org/axon-agency.git
cd axon-agency
cd apps/api && pip install -r requirements.txt
cd ../web && npm install
```

### Step 3: Configure Staging Environment

**Backend `.env` (staging):**

```env
# Server
BIND=0.0.0.0
PORT=8080

# Database - Use PostgreSQL or MongoDB Atlas
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/axon_staging

# Auth - Generate secure JWT secret
JWT_SECRET=<generate-random-secret-here>
PRODUCTION_MODE=false  # Keep false for staging debugging
DEV_MODE=false  # Disable auth bypass

# CORS - Allow staging domain
ALLOWED_ORIGINS=https://staging.axon.agency,http://localhost:3000

# LLM Providers
OPENAI_API_KEY=sk-proj-staging-key-here
OPENAI_MODEL=gpt-4o-mini

# Gemini fallback (recommended)
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.0-flash-exp

# MongoDB (optional - for WhatsApp Sales Agent)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=whatsapp_sales_agent_staging

# Redis (optional - for jobs)
REDIS_URL=redis://localhost:6379/0

# Social Deploy (optional - use Ayrshare test account)
ENABLE_AYRSHARE_SOCIAL=true
AYRSHARE_API_KEY=ayr_staging_key

# Telegram Deploy (optional - use test bot)
ENABLE_TELEGRAM_DEPLOY=true
TELEGRAM_BOT_TOKEN=123456:ABC-DEF-staging-bot

# Stripe (use test mode keys)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID=price_test_...

# WhatsApp Deploy (n8n webhook)
N8N_WHATSAPP_DEPLOY_WEBHOOK_URL=https://n8n.staging.example.com/webhook/whatsapp
```

**Frontend `.env.local` (staging):**

```env
NEXT_PUBLIC_BACKEND_URL=https://api.staging.axon.agency
```

### Step 4: Generate JWT Secret

**Generate secure random secret:**

```bash
# macOS/Linux:
openssl rand -hex 32

# Output example:
# a3f2b8c9e1d4f7a6b2c8e9f1d3a7b5c2e8f9a1b4c6d7e2f3a5b8c9d1e4f7a6b2

# Set in .env:
JWT_SECRET=a3f2b8c9e1d4f7a6b2c8e9f1d3a7b5c2e8f9a1b4c6d7e2f3a5b8c9d1e4f7a6b2
```

### Step 5: Setup PostgreSQL Database

**Option A: Cloud PostgreSQL (Recommended)**

Use managed PostgreSQL from:
- **Neon** ([neon.tech](https://neon.tech/)) - Free tier available
- **Supabase** ([supabase.com](https://supabase.com/))
- **AWS RDS** ([aws.amazon.com/rds](https://aws.amazon.com/rds/))

**Get connection string:**
```
postgresql+psycopg://user:password@host:5432/database
```

**Option B: Self-hosted PostgreSQL**

```bash
# Install PostgreSQL
sudo apt install postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE axon_staging;
CREATE USER axon_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE axon_staging TO axon_user;
\q

# Connection string:
DATABASE_URL=postgresql+psycopg://axon_user:secure_password@localhost:5432/axon_staging
```

### Step 6: Run Database Migrations

**SQLModel auto-creates tables on startup.** No manual migrations needed unless using Alembic.

**Verify tables created:**

```bash
# Connect to PostgreSQL
psql postgresql+psycopg://user:pass@host:5432/axon_staging

# List tables
\dt

# Expected tables:
# - users
# - tenants
# - orders
# - ... (all SQLModel models)
```

### Step 7: Start Services with Process Manager

**Use systemd or PM2 to keep services running:**

**Option A: systemd (Linux)**

Create `/etc/systemd/system/axon-api.service`:

```ini
[Unit]
Description=Axon Agency API
After=network.target

[Service]
Type=simple
User=axon
WorkingDirectory=/home/axon/axon-agency/apps/api
Environment="PATH=/home/axon/.local/bin:/usr/bin"
ExecStart=/home/axon/.local/bin/uvicorn app.main:socket_app --host 0.0.0.0 --port 8080
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/axon-web.service`:

```ini
[Unit]
Description=Axon Agency Web
After=network.target

[Service]
Type=simple
User=axon
WorkingDirectory=/home/axon/axon-agency/apps/web
Environment="PATH=/home/axon/.nvm/versions/node/v20.x.x/bin:/usr/bin"
ExecStart=/home/axon/.nvm/versions/node/v20.x.x/bin/npm run start
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl enable axon-api axon-web
sudo systemctl start axon-api axon-web
sudo systemctl status axon-api axon-web
```

**Option B: PM2 (Node.js process manager)**

```bash
# Install PM2
npm install -g pm2

# Start backend
cd axon-agency/apps/api
pm2 start "uvicorn app.main:socket_app --host 0.0.0.0 --port 8080" --name axon-api

# Start frontend (build first)
cd axon-agency/apps/web
npm run build
pm2 start "npm run start" --name axon-web

# Save PM2 state
pm2 save
pm2 startup
```

### Step 8: Setup Reverse Proxy (Nginx)

**Install Nginx:**

```bash
sudo apt install nginx
```

**Configure Nginx (`/etc/nginx/sites-available/axon-staging`):**

```nginx
# API (api.staging.axon.agency)
server {
    listen 80;
    server_name api.staging.axon.agency;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend (staging.axon.agency)
server {
    listen 80;
    server_name staging.axon.agency;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Enable and reload:**

```bash
sudo ln -s /etc/nginx/sites-available/axon-staging /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 9: Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d api.staging.axon.agency -d staging.axon.agency

# Auto-renewal is configured by default
```

### Step 10: Verify Staging Deployment

```bash
# 1. Check HTTPS endpoints
curl https://api.staging.axon.agency/api/health
curl https://staging.axon.agency

# 2. Check integrations health
curl https://api.staging.axon.agency/api/integrations/health

# 3. Test authentication (no DEV_MODE)
curl -X POST https://api.staging.axon.agency/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "Test123!", "full_name": "Test User"}'
```

---

## Production Setup

**Goal:** Deploy Axon Agency to production with all integrations enabled and security hardened.

### Security Checklist (Before Production)

**Before deploying to production, complete ALL items in [`SECRETS_MATRIX.md`](./SECRETS_MATRIX.md):**

- [ ] `JWT_SECRET` changed to secure random value (NOT default)
- [ ] `DEV_MODE=false` (auth bypass disabled)
- [ ] `PRODUCTION_MODE=true`
- [ ] `DATABASE_URL` using PostgreSQL (NOT SQLite)
- [ ] `ALLOWED_ORIGINS` set to production domain only
- [ ] All API keys use **production** credentials (not test/sandbox)
- [ ] SSL/HTTPS enabled with valid certificate
- [ ] Firewall rules configured (only ports 80/443 exposed)
- [ ] Database backups automated
- [ ] Monitoring/logging configured
- [ ] Rate limiting enabled
- [ ] CORS properly restricted

### Step 1: Production Environment Variables

**Backend `.env` (production):**

```env
# Server
BIND=0.0.0.0
PORT=8080

# Database - PostgreSQL production
DATABASE_URL=postgresql+psycopg://user:pass@prod-db-host:5432/axon_production

# Auth - MUST use secure random secret
JWT_SECRET=<secure-random-secret-from-openssl-rand>
PRODUCTION_MODE=true
DEV_MODE=false

# CORS - Only production domain
ALLOWED_ORIGINS=https://app.axon.agency

# LLM Providers (production keys)
OPENAI_API_KEY=sk-proj-production-key
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=AIzaSy-production-key

# MongoDB (production cluster)
MONGODB_URI=mongodb+srv://prod-user:pass@prod-cluster.mongodb.net/
MONGODB_DB_NAME=whatsapp_sales_agent_production

# Redis (production instance)
REDIS_URL=redis://prod-redis-host:6379/0

# Social Deploy (production Ayrshare account)
ENABLE_AYRSHARE_SOCIAL=true
AYRSHARE_API_KEY=<production-key>

# Telegram Deploy (production bot)
ENABLE_TELEGRAM_DEPLOY=true
TELEGRAM_BOT_TOKEN=<production-bot-token>
DEFAULT_TELEGRAM_CHAT_ID=<fallback-channel-id>

# Stripe (LIVE mode keys)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PRICE_ID=price_live_...
STRIPE_SUCCESS_URL=https://app.axon.agency/payment/success
STRIPE_CANCEL_URL=https://app.axon.agency/payment/cancel

# WhatsApp Sales Agent - All integrations
MELVIS_API_URL=https://melvis.production.example.com/api
MELVIS_API_KEY=<production-melvis-key>
TAVILY_API_KEY=<production-tavily-key>
LINKEDIN_API_KEY=<production-linkedin-key>
CALCOM_BOOKING_LINK=https://cal.com/your-agency/consultation

# n8n Production
N8N_WHATSAPP_DEPLOY_WEBHOOK_URL=https://n8n.production.example.com/webhook/whatsapp
N8N_API_KEY=<production-n8n-key>

# Autonomous Agents
AUTONOMOUS_AGENT_ARCHITECT_ENABLED=true
AUTONOMOUS_AGENT_REVIEW_COUNCIL_ENABLED=true

# LLM Router
LLM_ROUTER_ENABLED=true
```

**⚠️ Critical Production Settings:**

1. **JWT_SECRET MUST be changed:**
   ```bash
   # Generate new secret:
   openssl rand -hex 32
   ```

2. **Database MUST be PostgreSQL** (SQLite not suitable for production)

3. **All integrations use LIVE credentials:**
   - Stripe: `sk_live_...` (NOT `sk_test_...`)
   - Telegram: Production bot token
   - MongoDB: Production cluster with backups enabled

### Step 2: Production Database Setup

**Use managed PostgreSQL service:**

- **Neon** (recommended for auto-scaling)
- **Supabase** (includes auth + storage)
- **AWS RDS** (enterprise-grade)
- **Google Cloud SQL**

**Enable automated backups:**
- Daily backups with 30-day retention
- Point-in-time recovery enabled
- Read replicas for high availability

### Step 3: MongoDB Production Setup

**Use MongoDB Atlas production cluster:**

1. **Create M10+ cluster** (M0 free tier not suitable for production)
2. **Enable backups** (continuous backup with point-in-time recovery)
3. **Setup IP whitelist** (application server IPs only, NOT 0.0.0.0/0)
4. **Enable authentication** (strong password, rotate keys regularly)
5. **Setup monitoring** (Atlas alerts for high CPU/memory usage)

### Step 4: Production Deployment

**Deploy using one of these methods:**

**Option A: Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./apps/api
    ports:
      - "8080:8080"
    env_file:
      - ./apps/api/.env.production
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    build: ./apps/web
    ports:
      - "5000:5000"
    env_file:
      - ./apps/web/.env.production
    restart: always
    depends_on:
      - api
```

**Deploy:**
```bash
docker-compose up -d
docker-compose logs -f
```

**Option B: Kubernetes**

See [deployment docs](./DEPLOYMENT.md) for Kubernetes manifests.

**Option C: Replit Deployments**

If hosted on Replit, use Replit Deployments feature:
- Set all production ENV vars in Replit Secrets
- Configure autoscaling
- Enable always-on

### Step 5: Setup Monitoring & Logging

**Backend logging (production):**

```python
# app/main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/axon-api.log', maxBytes=10485760, backupCount=10),
        logging.StreamHandler()
    ]
)
```

**Recommended monitoring tools:**
- **Sentry** - Error tracking ([sentry.io](https://sentry.io/))
- **LogTail** - Log aggregation ([logtail.com](https://logtail.com/))
- **Uptime Robot** - Uptime monitoring ([uptimerobot.com](https://uptimerobot.com/))
- **New Relic** - APM ([newrelic.com](https://newrelic.com/))

### Step 6: Setup Backups

**Database backups:**
- Automated daily backups (managed by PostgreSQL/MongoDB service)
- Test restore process monthly
- Store backups in separate region/cloud provider

**Code backups:**
- Git repository with protected main branch
- Tagged releases for rollback capability
- Deployment artifacts stored in S3/GCS

**Environment secrets:**
- Store `.env.production` securely (1Password, Vault, AWS Secrets Manager)
- Never commit to Git
- Rotate keys quarterly

### Step 7: Performance Optimization

**Backend optimizations:**

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Axon Agency API",
    docs_url=None if settings.production_mode else "/docs",  # Disable Swagger in prod
    redoc_url=None if settings.production_mode else "/redoc",
)

# Enable gzip compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Connection pooling
from sqlmodel import create_engine
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

**Frontend optimizations:**

```bash
# Build with production optimizations
cd apps/web
npm run build

# Start production server
npm run start
```

**CDN for static assets:**
- Use Cloudflare, AWS CloudFront, or Vercel CDN
- Cache static assets (images, JS, CSS)
- Enable HTTP/2

### Step 8: Security Hardening

**Enable rate limiting:**

```python
# app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes
@router.post("/api/orders", dependencies=[Depends(limiter.limit("10/minute"))])
async def create_order(...):
    ...
```

**Firewall rules:**
```bash
# Only allow ports 80/443
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

**HTTPS only:**
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name app.axon.agency api.axon.agency;
    return 301 https://$server_name$request_uri;
}
```

**Content Security Policy:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Only production domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Step 9: Deploy Channels Configuration

**WhatsApp Deploy (n8n):**
1. Setup n8n workflow for WhatsApp Business API
2. Configure webhook URL in `N8N_WHATSAPP_DEPLOY_WEBHOOK_URL`
3. Test with sample order deploy

**Telegram Deploy:**
1. Create production bot with @BotFather
2. Set webhook: `https://api.axon.agency/api/integrations/telegram/webhook`
3. Configure `TELEGRAM_BOT_TOKEN` + `DEFAULT_TELEGRAM_CHAT_ID`
4. Test with `/api/orders/{id}/deploy/telegram`

**Social Deploy (Ayrshare):**
1. Connect social media accounts in Ayrshare dashboard
2. Enable platforms: Twitter, Facebook, Instagram
3. Set `AYRSHARE_API_KEY` + `ENABLE_AYRSHARE_SOCIAL=true`
4. Test with `/api/orders/{id}/deploy/social`

### Step 10: Production Verification

**Run comprehensive health checks:**

```bash
# 1. API health
curl https://api.axon.agency/api/health

# 2. All integrations health
curl https://api.axon.agency/api/integrations/health

# 3. Database connectivity
# Should return 200 OK with all statuses = "healthy"

# 4. Test authentication flow
curl -X POST https://api.axon.agency/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@axon.agency", "username": "admin", "password": "SecurePass123!", "full_name": "Admin User"}'

# 5. Test order creation
curl -X POST https://api.axon.agency/api/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"tipo_producto": "autopilot_whatsapp", "nombre_producto": "Test Autopilot", "datos_cliente": {"company": "Test Corp"}}'

# 6. Test WhatsApp Sales Agent (if MongoDB configured)
curl https://api.axon.agency/api/leads/list \
  -H "Authorization: Bearer <admin-token>"
```

**Verify all integrations:**

```bash
# Get unified health status
curl https://api.axon.agency/api/integrations/health | jq

# Expected response with ALL integrations = "healthy":
{
  "overall_status": "healthy",
  "timestamp": "2025-11-18T...",
  "integrations": [
    {"name": "mongodb", "status": "healthy"},
    {"name": "whatsapp_core", "status": "healthy"},
    {"name": "whatsapp_sales_agent", "status": "healthy"},
    {"name": "social", "status": "healthy"},
    {"name": "telegram", "status": "healthy"}
  ]
}
```

**Production Readiness Checklist:**

- [ ] All health checks return `"healthy"`
- [ ] Can create user and authenticate
- [ ] Can create orders
- [ ] Can deploy to WhatsApp/Telegram/Social
- [ ] MongoDB leads endpoint returns data
- [ ] HTTPS certificate valid
- [ ] Monitoring/alerting configured
- [ ] Backups verified
- [ ] Rate limiting active
- [ ] DEV_MODE disabled
- [ ] Default JWT_SECRET changed
- [ ] All production API keys configured

---

## Verification Steps

### Backend Verification

```bash
# 1. Health check
curl http://localhost:8080/api/health
# Expected: {"status": "healthy", "timestamp": "..."}

# 2. Integrations health
curl http://localhost:8080/api/integrations/health | jq
# Expected: List of all integrations with status

# 3. Product catalog
curl http://localhost:8080/api/products/catalog
# Expected: Array of autopilot products

# 4. Get dev token (DEV_MODE only)
TOKEN=$(curl -X POST http://localhost:8080/api/auth/dev/token | jq -r '.access_token')
echo $TOKEN

# 5. Test authenticated endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/orders
# Expected: Empty array [] or list of orders

# 6. Test agent chat
curl -X POST http://localhost:8080/api/agent/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola", "session_id": "verify-123"}'
# Expected: AI response
```

### Frontend Verification

1. Open `http://localhost:5000` in browser
2. Should see Axon Agency dashboard
3. Navigate through pages:
   - `/agent` - Super Axon Agent chat
   - `/agent/orders` - Orders list
   - `/agent/factory` - Agent Factory dashboard
   - `/agent/catalog` - Product catalog
   - `/agent/tenants` - Tenants management
   - `/agent/leads` - WhatsApp Sales Agent leads

4. Check browser console for errors (should be none)

### Integration Tests

```bash
# WhatsApp Sales Agent (if MongoDB configured)
curl http://localhost:8080/api/leads/list
# Expected: {"leads": [], "total": 0} or list of leads

# Social health (if Ayrshare configured)
curl http://localhost:8080/api/integrations/social/health
# Expected: {"status": "healthy" or "disabled", ...}

# Telegram status
curl http://localhost:8080/api/integrations/telegram/status
# Expected: {"enabled": true/false, ...}
```

---

## Common Issues

### Issue 1: Backend Won't Start

**Symptoms:**
```
ERROR:    Error loading ASGI app. Import string "app.main:socket_app" doesn't exist.
```

**Solutions:**

```bash
# 1. Check you're in correct directory
cd axon-agency/apps/api
pwd  # Should end with /apps/api

# 2. Verify Python version
python --version  # Should be 3.11+

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. Check PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

---

### Issue 2: Frontend Can't Reach Backend

**Symptoms:**
- Frontend shows "API connection failed"
- Browser console: `ERR_CONNECTION_REFUSED`

**Solutions:**

```bash
# 1. Verify backend is running
curl http://localhost:8080/api/health

# 2. Check NEXT_PUBLIC_BACKEND_URL
cat apps/web/.env.local
# Should match backend URL exactly

# 3. Check CORS settings
# In apps/api/.env, ensure:
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000

# 4. Restart both servers
# Kill processes and start fresh
```

---

### Issue 3: MongoDB Connection Failed

**Error:**
```
ERROR: MongoDB connection failed: ServerSelectionTimeoutError
```

**Solutions:**

```bash
# 1. Verify MongoDB URI format
echo $MONGODB_URI
# Should be: mongodb+srv://user:pass@cluster.mongodb.net/

# 2. Test connection with mongosh
mongosh "$MONGODB_URI"

# 3. Check MongoDB Atlas firewall
# Login to Atlas → Network Access
# Add IP: 0.0.0.0/0 (for testing) or your server IP

# 4. Verify credentials
# Check username/password in connection string

# 5. Test with Python
python3 -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
async def test():
    client = AsyncIOMotorClient('$MONGODB_URI')
    await client.admin.command('ping')
    print('✅ MongoDB connection successful')
asyncio.run(test())
"
```

---

### Issue 4: OpenAI API Key Invalid

**Error:**
```
ERROR: OpenAI API error: Incorrect API key provided
```

**Solutions:**

```bash
# 1. Verify API key format
echo $OPENAI_API_KEY
# Should start with sk-proj- or sk-

# 2. Test API key with curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
# Should return list of models

# 3. Check usage limits
# Visit: https://platform.openai.com/usage

# 4. Regenerate key
# Visit: https://platform.openai.com/api-keys
```

---

### Issue 5: CORS Errors in Browser

**Error in browser console:**
```
Access to fetch at 'http://localhost:8080/api/...' from origin 'http://localhost:5000' has been blocked by CORS policy
```

**Solutions:**

```bash
# 1. Check ALLOWED_ORIGINS in backend .env
cat apps/api/.env | grep ALLOWED_ORIGINS
# Should include frontend URL

# 2. Update ALLOWED_ORIGINS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000,http://localhost:5001

# 3. Restart backend server
# CORS middleware loads on startup

# 4. Verify in browser Network tab
# Response headers should include:
# Access-Control-Allow-Origin: http://localhost:5000
```

---

### Issue 6: Database Tables Not Created

**Symptoms:**
- Orders API returns `"table orders does not exist"`
- SQLite file exists but empty

**Solutions:**

```bash
# 1. Check database file
ls -lh apps/api/axon.db

# 2. SQLModel auto-creates tables on startup
# Just restart the API server

# 3. Manually inspect database
sqlite3 apps/api/axon.db
.tables
# Should show: users, tenants, orders, etc.

# 4. For PostgreSQL, check connection
psql $DATABASE_URL -c "\dt"
```

---

### Issue 7: WhatsApp Sales Agent Not Working

**Symptoms:**
- `/api/leads/list` returns 503 "MongoDB not configured"
- Health check shows MongoDB status = "disabled"

**Solutions:**

```bash
# 1. Check MongoDB ENV vars
env | grep MONGODB
# Should show MONGODB_URI and MONGODB_DB_NAME

# 2. Verify in .env file
cat apps/api/.env | grep MONGODB

# 3. Test MongoDB connection
curl http://localhost:8080/api/integrations/health | jq '.integrations[] | select(.name=="mongodb")'
# Should show status: "healthy"

# 4. Check logs
# Look for: "MongoDB connected successfully"
```

---

### Issue 8: Stripe Checkout Not Generating

**Symptoms:**
- Qualified lead but no checkout URL
- Logs show: "Stripe client not configured"

**Solutions:**

```bash
# 1. Check Stripe ENV vars
env | grep STRIPE
# Need: STRIPE_SECRET_KEY, STRIPE_PRICE_ID

# 2. Verify Stripe key format
echo $STRIPE_SECRET_KEY
# Should start with sk_live_ or sk_test_

# 3. Test Stripe API
curl https://api.stripe.com/v1/prices/$STRIPE_PRICE_ID \
  -u "$STRIPE_SECRET_KEY:"
# Should return price details

# 4. Check Stripe dashboard
# Verify price ID exists and is active
```

---

## Key Endpoints

### Health & System

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health` | GET | No | API health check |
| `/api/integrations/health` | GET | Yes | All integrations status |
| `/api/products/catalog` | GET | Optional | Available autopilot products |

### Authentication

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/register` | POST | No | Register new user |
| `/api/auth/login` | POST | No | Login with credentials |
| `/api/auth/dev/token` | POST | No | Get dev token (DEV_MODE only) |

### Orders

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/orders` | GET | Yes | List orders (tenant-scoped) |
| `/api/orders` | POST | Yes | Create new order |
| `/api/orders/{id}` | GET | Yes | Get order details |
| `/api/orders/{id}/deploy/whatsapp` | POST | Yes | Deploy to WhatsApp |
| `/api/orders/{id}/deploy/social` | POST | Yes | Deploy to social media |
| `/api/orders/{id}/deploy/telegram` | POST | Yes | Deploy to Telegram |

### Leads (WhatsApp Sales Agent)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/leads/list` | GET | Admin | List all WhatsApp leads |

### Tenants (Multi-tenant)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/tenants` | GET | Admin | List all tenants |
| `/api/tenants` | POST | Admin | Create tenant |
| `/api/tenants/{id}` | GET | Yes | Get tenant details |

### Agent (LLM Chat)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/agent/chat` | POST | Yes | Chat with AI agent |

---

## Workflows & Commands

### Development Workflows

**Setup (Replit-style):**

Two workflows are configured in `.replit`:

1. **axon-agency-api** (Backend)
   ```bash
   cd axon-agency/apps/api && uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080
   ```

2. **axon-web** (Frontend)
   ```bash
   cd axon-agency/apps/web && npm run dev
   ```

**To start both workflows:**
- Click "Run" in Replit
- Or manually start each in separate terminals

### Useful Commands

**Backend:**

```bash
# Start API server (development)
cd apps/api
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080

# Start API server (production)
uvicorn app.main:socket_app --host 0.0.0.0 --port 8080 --workers 4

# Check Python dependencies
pip list

# Install new package
pip install <package-name>
pip freeze > requirements.txt
```

**Frontend:**

```bash
# Start dev server
cd apps/web
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Check dependencies
npm list

# Install new package
npm install <package-name>
```

**Database:**

```bash
# SQLite: Inspect database
sqlite3 apps/api/axon.db
.tables
SELECT * FROM users;

# PostgreSQL: Inspect database
psql $DATABASE_URL
\dt
SELECT * FROM users;
```

**MongoDB:**

```bash
# Connect with mongosh
mongosh "$MONGODB_URI"

# Switch to database
use whatsapp_sales_agent

# Query collections
db.users.find()
db.leads.find()
db.sessions.find()
```

**Docker (if using):**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Restart services
docker-compose restart api web

# Stop all
docker-compose down
```

---

## Next Steps After Setup

1. **Configure Tenants:**
   - Create your first tenant via `/api/tenants` (POST)
   - Associate users with tenants

2. **Test Order Flow:**
   - Create test order via `/api/orders` (POST)
   - Deploy to available channels
   - Verify deliverables

3. **Enable WhatsApp Sales Agent:**
   - Configure MongoDB Atlas
   - Set all 7 integration API keys
   - Test webhook with simulated messages

4. **Setup Monitoring:**
   - Add Sentry for error tracking
   - Configure uptime monitoring
   - Setup log aggregation

5. **Review Documentation:**
   - [`SECRETS_MATRIX.md`](./SECRETS_MATRIX.md) - ENV vars reference
   - [`WHATSAPP_SALES_AGENT_PLAN.md`](./WHATSAPP_SALES_AGENT_PLAN.md) - WhatsApp Sales Agent architecture
   - [`README.md`](../README.md) - Project overview

---

## Related Documentation

- **[SECRETS_MATRIX.md](./SECRETS_MATRIX.md)** - Complete environment variables reference
- **[WHATSAPP_SALES_AGENT_PLAN.md](./WHATSAPP_SALES_AGENT_PLAN.md)** - WhatsApp Sales Agent technical documentation
- **[PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)** - Production deployment checklist
- **[README.md](../README.md)** - Project overview and features

---

**Last Updated:** November 18, 2025  
**Version:** 1.0  
**Maintained by:** Axon Agency Team

Need help? Check the [Common Issues](#common-issues) section or review the full documentation.
