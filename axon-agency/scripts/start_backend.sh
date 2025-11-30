#!/usr/bin/env bash
# ===================================================
# AXON AGENCY - QUICK START BACKEND SCRIPT
# ===================================================
# Uso: ./scripts/start_backend.sh
# Inicia la API de FastAPI en puerto 8080
# ===================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/apps/api"

echo "🚀 Starting AXON Agency Backend..."
echo "📁 Working directory: $BACKEND_DIR"

# Navegar al directorio del backend
cd "$BACKEND_DIR"

# Activar venv si existe
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || true
fi

# Verificar que .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  .env not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env - please edit with real values"
fi

# Iniciar API
echo "🌐 Starting FastAPI server on 0.0.0.0:8080..."
echo "📝 To stop: press Ctrl+C"
echo ""

uvicorn app.main:socket_app --host 0.0.0.0 --port 8080 --reload

# Al terminar
echo ""
echo "✅ Backend stopped"
