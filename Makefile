.PHONY: dev run test fmt lint docker-up docker-down clean

dev:
	uvicorn app.main:sio_app --host 0.0.0.0 --port 8080 --reload

run:
	python -m uvicorn app.main:sio_app --host 0.0.0.0 --port 8080

test:
	pytest tests/ -v

fmt:
	black app/ tests/
	ruff check --fix app/ tests/

lint:
	ruff check app/ tests/
	black --check app/ tests/

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f axon-core

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf logs/*.log
