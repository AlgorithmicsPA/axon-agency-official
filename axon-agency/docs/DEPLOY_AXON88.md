# 🚀 Deployment Guide - Axon Agency on Axon88

Complete guide for deploying Axon Agency using Docker Compose on Axon88.

---

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- At least 2GB RAM available
- Ports 5000, 8080, 5432, 6379 available

---

## 🏗️ Quick Start

### 1. Build the Stack

```bash
# From repository root
docker compose -f docker-compose.axon88.yml build
```

Build times:
- Backend API: ~2-3 minutes
- Frontend Web: ~3-5 minutes

### 2. Start Services

```bash
# Start all services in detached mode
docker compose -f docker-compose.axon88.yml up -d
```

Services will start in order:
1. PostgreSQL (waits for health check)
2. Redis (waits for health check)
3. Backend API (waits for postgres + redis)
4. Frontend Web (waits for backend API)

### 3. Verify Deployment

```bash
# Check all services are running
docker compose -f docker-compose.axon88.yml ps

# Check backend health
curl http://localhost:8080/api/health

# Check frontend (in browser)
# Open: http://localhost:5000
```

Expected output:
```json
{"status": "ok"}
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the repository root with your configuration:

```bash
# .env (DO NOT COMMIT TO GIT)

# ===========================
# PRODUCTION SETTINGS
# ===========================
PRODUCTION_MODE=true
DEV_MODE=false

# ===========================
# SECURITY (REQUIRED)
# ===========================
# Generate with: openssl rand -hex 32
JWT_SECRET=your-32-character-random-secret-here

# PostgreSQL password
POSTGRES_PASSWORD=your-secure-postgres-password

# ===========================
# DATABASE (REQUIRED)
# ===========================
DATABASE_URL=postgresql+psycopg://axon:your-secure-postgres-password@postgres:5432/axon

# ===========================
# CORS (REQUIRED)
# ===========================
ALLOWED_ORIGINS=https://axon88.com,https://app.axon88.com

# ===========================
# FRONTEND (REQUIRED)
# ===========================
# For internal: http://axon-agency-api:8080
# For external: https://api.axon88.com
NEXT_PUBLIC_BACKEND_URL=https://api.axon88.com

# ===========================
# LLM PROVIDERS (OPTIONAL)
# ===========================
OPENAI_API_KEY=sk-proj-your-key
GEMINI_API_KEY=your-gemini-key

# ===========================
# WHATSAPP SALES AGENT (OPTIONAL)
# ===========================
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=whatsapp_sales_prod

# ===========================
# INTEGRATIONS (OPTIONAL)
# ===========================
N8N_WHATSAPP_DEPLOY_WEBHOOK_URL=https://n8n.example.com/webhook/whatsapp
AYRSHARE_API_KEY=your-ayrshare-key
TELEGRAM_BOT_TOKEN=your-telegram-token
STRIPE_SECRET_KEY=sk_live_your-stripe-key
```

Then run:
```bash
docker compose -f docker-compose.axon88.yml --env-file .env up -d
```

### Using External Secrets Management

For production on Axon88, use external secrets:

```bash
# Export secrets from environment
export JWT_SECRET=$(openssl rand -hex 32)
export POSTGRES_PASSWORD=$(openssl rand -hex 16)
export DATABASE_URL="postgresql+psycopg://axon:${POSTGRES_PASSWORD}@postgres:5432/axon"

# Run with env vars
docker compose -f docker-compose.axon88.yml up -d
```

---

## 🔍 Service Details

### Backend API (axon-agency-api)

- **Port:** 8080
- **Health:** `http://localhost:8080/api/health`
- **Database:** PostgreSQL (not SQLite in production)
- **Logs:** `docker logs axon-agency-api -f`

**Connect to container:**
```bash
docker exec -it axon-agency-api bash
```

### Frontend Web (axon-agency-web)

- **Port:** 5000
- **URL:** `http://localhost:5000`
- **Logs:** `docker logs axon-agency-web -f`

**Connect to container:**
```bash
docker exec -it axon-agency-web sh
```

### PostgreSQL

- **Port:** 5432
- **Database:** axon
- **User:** axon
- **Connect:**
```bash
docker exec -it axon-postgres psql -U axon -d axon
```

### Redis

- **Port:** 6379
- **Connect:**
```bash
docker exec -it axon-redis redis-cli
```

---

## 🛠️ Common Operations

### View Logs

```bash
# All services
docker compose -f docker-compose.axon88.yml logs -f

# Specific service
docker logs axon-agency-api -f
docker logs axon-agency-web -f
docker logs axon-postgres -f
docker logs axon-redis -f
```

### Restart Services

```bash
# Restart all
docker compose -f docker-compose.axon88.yml restart

# Restart specific service
docker compose -f docker-compose.axon88.yml restart axon-agency-api
```

### Stop Services

```bash
# Stop all (keep data)
docker compose -f docker-compose.axon88.yml down

# Stop and remove volumes (DESTRUCTIVE)
docker compose -f docker-compose.axon88.yml down -v
```

### Update Code

```bash
# Rebuild after code changes
docker compose -f docker-compose.axon88.yml build axon-agency-api
docker compose -f docker-compose.axon88.yml up -d axon-agency-api

# Or rebuild all
docker compose -f docker-compose.axon88.yml build
docker compose -f docker-compose.axon88.yml up -d
```

### Database Backup

```bash
# Backup PostgreSQL
docker exec axon-postgres pg_dump -U axon axon > backup.sql

# Restore
cat backup.sql | docker exec -i axon-postgres psql -U axon axon
```

---

## 🔐 Production Checklist

Before deploying to Axon88 production:

- [ ] Generate secure JWT_SECRET (32+ random characters)
- [ ] Set strong POSTGRES_PASSWORD
- [ ] Configure DATABASE_URL with PostgreSQL (NOT SQLite)
- [ ] Set PRODUCTION_MODE=true
- [ ] Set DEV_MODE=false (CRITICAL)
- [ ] Configure ALLOWED_ORIGINS with production domains
- [ ] Set NEXT_PUBLIC_BACKEND_URL to public API URL
- [ ] Add all required API keys from `docs/SECRETS_MATRIX.md`
- [ ] Configure backup strategy for postgres_data volume
- [ ] Set up monitoring/alerting
- [ ] Configure reverse proxy (nginx/traefik) if needed
- [ ] Enable HTTPS/TLS certificates
- [ ] Test health endpoints

---

## 📊 Resource Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 2GB
- Disk: 10GB

**Recommended:**
- CPU: 4 cores
- RAM: 4GB
- Disk: 20GB (with space for logs/storage)

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
docker logs axon-agency-api

# Common issues:
# - DATABASE_URL incorrect → verify postgres is running
# - Missing JWT_SECRET → check .env file
# - Port 8080 in use → change port mapping
```

### Frontend can't connect to backend

```bash
# Check NEXT_PUBLIC_BACKEND_URL
docker exec axon-agency-web env | grep NEXT_PUBLIC

# Should point to:
# - Development: http://localhost:8080
# - Production: https://api.axon88.com (public URL)
```

### Database connection fails

```bash
# Check postgres is healthy
docker compose -f docker-compose.axon88.yml ps postgres

# Test connection
docker exec axon-postgres pg_isready -U axon

# Check DATABASE_URL format
# Correct: postgresql+psycopg://axon:password@postgres:5432/axon
```

### Out of memory

```bash
# Check resource usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or add memory limits to docker-compose.yml:
# services:
#   axon-agency-api:
#     mem_limit: 1g
```

---

## 📚 Additional Resources

- **Environment Variables:** See `docs/SECRETS_MATRIX.md` for complete list
- **Development Setup:** See `docs/QUICK_SETUP_GUIDE.md`
- **WhatsApp Integration:** See `docs/WHATSAPP_SALES_AGENT_PLAN.md`
- **Production Security:** See `docs/PRODUCTION_CHECKLIST.md`

---

## 🔄 Differences from Development

| Aspect | Development | Production (Axon88) |
|--------|-------------|---------------------|
| Database | SQLite | PostgreSQL |
| DEV_MODE | true | false (CRITICAL) |
| Secrets | Hardcoded | From environment |
| HTTPS | No | Yes (reverse proxy) |
| Logging | Verbose | Production level |
| Backups | Manual | Automated |
| Monitoring | None | Required |

---

## ✅ Summary

You now have a complete Docker-based deployment for Axon Agency:

1. **Build:** `docker compose -f docker-compose.axon88.yml build`
2. **Configure:** Create `.env` file with secrets
3. **Start:** `docker compose -f docker-compose.axon88.yml up -d`
4. **Verify:** Check health endpoints
5. **Monitor:** Watch logs and metrics

For questions or issues, refer to `docs/SECRETS_MATRIX.md` for configuration details.
