.PHONY: dev test lint clean build install restart integration

dev:
	@echo "🚀 Starting development servers..."
	@echo "   Backend:  http://localhost:8080"
	@echo "   Frontend: http://localhost:5001"
	@echo ""
	@echo "Run in separate terminals:"
	@echo "   make backend"
	@echo "   make frontend"

backend:
	cd apps/api && uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080

frontend:
	cd apps/web && npm run dev

install:
	@echo "📦 Installing dependencies..."
	cd apps/api && pip install -r requirements.txt
	cd apps/web && npm install

restart:
	@echo "♻️  Restarting workflows..."
	@echo "   Use Replit's workflow restart or rerun make backend/frontend"

test:
	@echo "🧪 Running tests..."
	cd apps/api && pytest

integration:
	@echo "🔗 Running integration tests..."
	python scripts/test_integration.py

lint:
	@echo "🔍 Linting code..."
	cd apps/api && ruff check .
	cd apps/web && npm run lint

build:
	@echo "🏗️  Building frontend..."
	cd apps/web && npm run build

clean:
	@echo "🧹 Cleaning..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf logs/*.log

setup-axon-core:
	@echo "🔗 Setting up Axon Core integration..."
	./scripts/setup_axon_core.sh

help:
	@echo "Available commands:"
	@echo "  make dev              - Show development instructions"
	@echo "  make backend          - Start backend server"
	@echo "  make frontend         - Start frontend server"
	@echo "  make install          - Install all dependencies"
	@echo "  make integration      - Run integration tests"
	@echo "  make setup-axon-core  - Configure Axon Core connection"
	@echo "  make test             - Run unit tests"
	@echo "  make lint             - Lint code"
	@echo "  make build            - Build frontend"
	@echo "  make clean            - Clean build artifacts"
