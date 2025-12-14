# AGENTS.md

## Run
- Start dev (backend + frontend): `make dev`
- Backend only: `make backend`
- Frontend only: `make frontend`

## Test
- API tests: `make run-test-api`
- UI tests: `make run-test-ui`

## Lint
- Lint all: `make lint`
- Format all: `make format`

## Database
- Run migrations: `make db-upgrade`
- Rollback migration: `make db-downgrade`
- Create migration: `make db-migrate`
- View current: `make db-current`
- View history: `make db-history`

## Deployment
- Each git branch gets its own isolated environment via Railway
