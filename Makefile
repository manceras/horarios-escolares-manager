.DEFAULT_GOAL := help
.PHONY: help setup dev dev-api dev-web check check-api check-web fix gen-api migrate migration seed create-user build clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Install every dependency and the git hooks
	cd backend && uv sync
	cd frontend && pnpm install
	uv tool run pre-commit install || pre-commit install

dev: ## Run the API and the web app together
	$(MAKE) -j2 dev-api dev-web

dev-api: ## Run the API on :8000
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-web: ## Run the web app on :5173
	cd frontend && pnpm dev

gen-api: ## Regenerate the frontend API client from the backend OpenAPI document
	cd backend && uv run python scripts/export_openapi.py ../openapi.json
	cd frontend && pnpm gen:api

check: check-api check-web ## Lint, type-check and test everything -- the gate

check-api: ## Backend lint, types and tests
	cd backend && uv run ruff check .
	cd backend && uv run ruff format --check .
	cd backend && uv run mypy app
	cd backend && uv run pytest

check-web: gen-api ## Frontend lint, types and build
	cd frontend && pnpm lint
	cd frontend && pnpm format:check
	cd frontend && pnpm typecheck

fix: ## Auto-fix what can be auto-fixed
	cd backend && uv run ruff check . --fix && uv run ruff format .
	cd frontend && pnpm lint --fix && pnpm format

migrate: ## Apply pending database migrations
	cd backend && uv run alembic upgrade head

migration: ## Create a migration: make migration name=add_rooms
	@test -n "$(name)" || (echo "Usage: make migration name=add_rooms" && exit 1)
	cd backend && uv run alembic revision --autogenerate -m "$(name)"

create-user: ## Create a user account, prompting for the password (use this in production)
	cd backend && uv run python scripts/create_user.py

seed: ## Load development data
	cd backend && uv run python scripts/seed.py

build: ## Build the production images
	docker compose build

clean: ## Remove build output and caches
	rm -rf frontend/dist openapi.json
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
