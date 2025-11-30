# Guía Rápida: Deploy de Axon Agency en Axon 88

## 📋 Resumen

Este documento es una guía **práctica y rápida** para desplegar Axon Agency en un servidor Axon 88 (Jetson Orin u otro).

**Tiempo estimado:** 30-45 minutos (asumiendo que ya tienes PostgreSQL instalado)

---

## 🎯 Pre-requisitos

- ✅ PostgreSQL 13+ instalado y corriendo
- ✅ Python 3.9+ 
- ✅ Node.js 18+ + npm
- ✅ Git
- ✅ Acceso de root/sudo en el servidor

---

## 1️⃣ Clonar el repositorio

```bash
# En tu servidor (ej. /home/axon88/projects/)
cd /home/axon88/projects
git clone https://github.com/tu-org/axon-agency.git
cd axon-agency
```

---

## 2️⃣ Setup de Base de Datos PostgreSQL

```bash
# 1. Crear usuario 'axon' con contraseña
sudo -u postgres createuser axon -P
# (Te pedirá que ingreses contraseña - **GUÁRDALA**)

# 2. Crear base de datos
sudo -u postgres createdb axon_agency -O axon

# 3. Verificar conexión
psql -U axon -d axon_agency -h localhost -c "SELECT 1;"
# Deberías ver: (1 row) con el número 1
```

---

## 3️⃣ Configurar y levantar Backend (FastAPI)

```bash
# 1. Entrar al directorio del backend
cd apps/api

# 2. Copiar archivo de entorno
cp .env.example .env

# 3. EDITAR .env con tus valores
nano .env  # (o tu editor favorito)

# Cambios CRÍTICOS en .env:
#   DATABASE_URL = postgresql+psycopg://axon:TU_CONTRASEÑA@localhost:5432/axon_agency
#   JWT_SECRET = (generar una cadena segura, ej: $(openssl rand -hex 32))
#   OPENAI_API_KEY = sk-proj-... (si tienes una clave)
#   DEV_MODE = false  (IMPORTANTE en producción)
#   PRODUCTION_MODE = true  (IMPORTANTE en producción)

# 4. Instalar dependencias
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Ejecutar migraciones (si aplica)
alembic upgrade head  # Si usa Alembic

# 6. Iniciar API
uvicorn app.main:socket_app --host 0.0.0.0 --port 8080

# ESPERA: Deberías ver:
# ✅ INFO:     Uvicorn running on http://0.0.0.0:8080
# ✅ Application startup complete
```

**Prueba de salud:**
```bash
# En otra terminal:
curl http://localhost:8080/api/health
# Esperado: {"status":"ok", ...}
```

---

## 4️⃣ Configurar y levantar Frontend (Next.js)

```bash
# 1. Entrar al directorio del frontend
cd ../web  # (asumiendo que estabas en apps/api)

# 2. Copiar archivo de entorno
cp .env.local.example .env.local

# 3. EDITAR .env.local
nano .env.local

# Cambios IMPORTANTES en .env.local:
#   NEXT_PUBLIC_API_BASE_URL = http://IP_DE_AXON88:8080
#     (ej: http://192.168.1.100:8080)
#   NEXT_PUBLIC_AXON_CORE_URL = https://api-axon88.algorithmicsai.com
#   NEXT_PUBLIC_WHATSAPP_PHONE_NUMBER = 52xxxxxxxxxx (si aplica)

# 4. Instalar dependencias
npm install

# 5. Build para producción (RECOMENDADO)
npm run build

# 6. Iniciar servidor
npm run start -- -p 5000

# ESPERA: Deberías ver:
# ✅ Ready in X.XXs
# ✅ Listening on http://0.0.0.0:5000
```

**Prueba en navegador:**
```
http://IP_DE_AXON88:5000
```

---

## 5️⃣ Configurar Reverse Proxy (Nginx) – RECOMENDADO

Si quieres acceder a todo a través de un solo dominio:

```nginx
# /etc/nginx/sites-available/axon-agency
upstream backend {
    server localhost:8080;
}

upstream frontend {
    server localhost:5000;
}

server {
    listen 80;
    server_name tu.dominio.com;

    # API (rutas /api/*)
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Frontend (todo lo demás)
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

Habilitar:
```bash
sudo ln -s /etc/nginx/sites-available/axon-agency /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 6️⃣ Crear Systemd Services (Opcional pero recomendado)

Para que los servicios se reinicien automáticamente:

### Backend service: `/etc/systemd/system/axon-agency-api.service`

```ini
[Unit]
Description=AXON Agency API
After=network.target postgresql.service

[Service]
Type=simple
User=axon88
WorkingDirectory=/home/axon88/projects/axon-agency/apps/api
Environment="PATH=/home/axon88/projects/axon-agency/apps/api/.venv/bin"
ExecStart=/home/axon88/projects/axon-agency/apps/api/.venv/bin/uvicorn app.main:socket_app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Frontend service: `/etc/systemd/system/axon-agency-web.service`

```ini
[Unit]
Description=AXON Agency Web
After=network.target axon-agency-api.service

[Service]
Type=simple
User=axon88
WorkingDirectory=/home/axon88/projects/axon-agency/apps/web
ExecStart=/usr/bin/npm run start -- -p 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Habilitar y iniciar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable axon-agency-api
sudo systemctl enable axon-agency-web
sudo systemctl start axon-agency-api
sudo systemctl start axon-agency-web
sudo systemctl status axon-agency-api
sudo systemctl status axon-agency-web
```

---

## 7️⃣ Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| **Port 8080 en uso** | `lsof -i :8080` y mata el proceso, o cambia PORT en .env |
| **Database connection error** | Verifica que PostgreSQL está corriendo: `sudo systemctl status postgresql` |
| **CORS errors en frontend** | Asegúrate que `NEXT_PUBLIC_API_BASE_URL` es correcto y alcanzable |
| **Módulos Python faltando** | Reinstala: `pip install -r requirements.txt --force-reinstall` |
| **npm start lento** | Primero corre `npm run build`, luego `npm start` |

---

## 8️⃣ Health Checks

Una vez todo esté corriendo:

```bash
# Backend
curl -s http://localhost:8080/api/health | jq .

# Frontend
curl -s http://localhost:5000 | grep -q "AXON" && echo "Frontend OK" || echo "Frontend Error"

# Nginx (si la usas)
curl -s http://tu.dominio.com/api/health | jq .
```

---

## 📝 Checklist Pre-Deploy Final

- [ ] PostgreSQL está corriendo y accesible
- [ ] Base de datos `axon_agency` creada
- [ ] `.env` en `apps/api/` con valores reales
- [ ] DEV_MODE=false en producción
- [ ] JWT_SECRET es seguro (32+ caracteres)
- [ ] OPENAI_API_KEY (si usas OpenAI)
- [ ] `.env.local` en `apps/web/` con URLs correctas
- [ ] Backend inicia sin errores en puerto 8080
- [ ] Frontend inicia sin errores en puerto 5000
- [ ] `curl http://localhost:8080/api/health` retorna 200 OK
- [ ] Puedes acceder a `http://localhost:5000` en navegador
- [ ] Nginx configurado (si lo usas)
- [ ] Systemd services habilitados (si los usas)

---

## 🎉 ¡Listo!

Tu instancia de Axon Agency debería estar funcionando. Ahora puedes:

1. Acceder en `http://IP_DE_AXON88:5000` (o tu dominio)
2. Crear un usuario admin
3. Crear tenants y órdenes
4. Probar flujos de deploy (WhatsApp, Social, Telegram)

Para más detalles, consulta `docs/PRODUCTION_CHECKLIST.md`.

---

**Última actualización:** Noviembre 28, 2025  
**Mantenido por:** AXON Agency Team
