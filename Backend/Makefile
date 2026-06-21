.PHONY: dev test lint format clean docker-up docker-down

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v --tb=short

test-cov:
	pytest -v --tb=short --cov=app --cov-report=term-missing

lint:
	ruff check .

format:
	ruff check --fix .
	ruff format .

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-rebuild:
	docker compose down -v
	docker compose up -d

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov

env:
	cp -n .env.example .env 2>/dev/null || true
