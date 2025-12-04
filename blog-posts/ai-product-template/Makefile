.PHONY: run-dev run-test-api run-test-ui backend frontend docker-up docker-down docker-build

backend:
	@echo "Starting backend on http://localhost:8000..."
	cd api && PYTHONPATH=src uv run uvicorn api.main:app --reload --port 8000

frontend:
	@echo "Starting frontend on http://localhost:5173..."
	cd app && npm run dev

run-dev:
	@echo "Starting both backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo ""
	@$(MAKE) -j 2 backend frontend

run-test-api:
	cd api && PYTHONPATH=src uv run pytest

run-test-ui:
	cd app && npm run test

docker-build:
	docker compose build

docker-up:
	docker compose up -d
	@echo "API: http://localhost:8000"
	@echo "App: http://localhost:3000"

docker-down:
	docker compose down
