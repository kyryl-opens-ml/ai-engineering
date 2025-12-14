.PHONY: run-dev run-test-api run-test-ui backend frontend db-migrate db-upgrade db-downgrade db-current db-history lint-api format-api lint-app format-app lint format

backend:
	@echo "Starting backend on http://localhost:8000..."
	cd api && PYTHONPATH=src uv run uvicorn api.main:app --reload --port 8000

frontend:
	@echo "Starting frontend on http://localhost:5173..."
	cd app && npm run dev

dev:
	@echo "Starting both backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo ""
	@$(MAKE) -j 2 backend frontend

run-test-api:
	cd api && PYTHONPATH=src uv run pytest

run-test-ui:
	cd app && npm run test

db-migrate:
	@read -p "Migration message: " msg; \
	cd api && PYTHONPATH=src uv run alembic revision --autogenerate -m "$$msg"

db-upgrade:
	cd api && PYTHONPATH=src uv run alembic upgrade head

db-downgrade:
	cd api && PYTHONPATH=src uv run alembic downgrade -1

db-current:
	cd api && PYTHONPATH=src uv run alembic current

db-history:
	cd api && PYTHONPATH=src uv run alembic history

lint-api:
	cd api && uv run ruff check src tests

format-api:
	cd api && uv run ruff format src tests && uv run ruff check --fix src tests

lint-app:
	cd app && npm run lint

format-app:
	cd app && npm run lint -- --fix

lint: lint-api lint-app

format: format-api format-app
