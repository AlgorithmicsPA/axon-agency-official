#!/usr/bin/env bash
# ===================================================
# AXON AGENCY - QUICK START FRONTEND SCRIPT
# ===================================================
# Uso: ./scripts/start_frontend.sh
# Inicia Next.js en modo desarrollo en puerto 5000
# ===================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/apps/web"

echo "🚀 Starting AXON Agency Frontend..."
echo "📁 Working directory: $FRONTEND_DIR"

# Navegar al directorio del frontend
cd "$FRONTEND_DIR"

# Verificar que .env.local existe
if [ ! -f ".env.local" ]; then
    echo "⚠️  .env.local not found. Copying from .env.local.example..."
    cp .env.local.example .env.local
    echo "✅ Created .env.local - please edit with your API URL"
fi

# Verificar que node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Iniciar frontend en dev
echo "🌐 Starting Next.js server on http://localhost:5000"
echo "📝 To stop: press Ctrl+C"
echo ""

npm run dev -- -p 5000

# Al terminar
echo ""
echo "✅ Frontend stopped"
