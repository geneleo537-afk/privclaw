.PHONY: dev down logs migrate migration seed test prod build shell-be shell-fe init

init:
	@cp .env.example .env
	@echo "✓ 环境配置模板已复制到 .env，请编辑填写实际配置后执行 make dev"

dev:
	docker compose up -d
	@echo "前端: http://localhost:3000"
	@echo "后端 API: http://localhost:8000/docs"
	@echo "MinIO: http://localhost:9001"

down:
	docker compose down

logs:
	docker compose logs -f backend frontend

migrate:
	docker compose exec backend alembic upgrade head

migration:
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

seed:
	docker compose exec backend python -m app.scripts.seed_demo

test:
	docker compose exec backend pytest -v --cov=app --cov-report=term-missing

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

build:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml build

shell-be:
	docker compose exec backend bash

shell-fe:
	docker compose exec frontend sh
