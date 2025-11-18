#!/bin/bash
set -e

echo "=== Axon Core - Development Bootstrap ==="

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env created"
else
    echo "✓ .env already exists"
fi

echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Bootstrap Complete ==="
echo ""
echo "Start development server:"
echo "  uvicorn app.main:sio_app --host 0.0.0.0 --port 8080 --reload"
echo ""
echo "Or use:"
echo "  make dev"
echo ""
echo "Get a development token:"
echo "  python scripts/print_token_dev.py"
echo ""
