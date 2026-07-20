.PHONY: backend-install backend-run backend-test backend-lint

backend-install:
	cd backend && pip install -r requirements-dev.txt

backend-run:
	cd backend && uvicorn app.main:app --reload --port 8000

backend-test:
	cd backend && pytest -v

backend-lint:
	cd backend && black --check app tests && ruff check app tests && mypy app

# Frontend targets land in Phase 3.
# Docker Compose targets land in Phase 17.
