.PHONY: backend-install backend-run backend-test backend-lint \
        frontend-install frontend-run frontend-test frontend-lint

backend-install:
	cd backend && pip install -r requirements-dev.txt

backend-run:
	cd backend && uvicorn app.main:app --reload --port 8000

backend-test:
	cd backend && pytest -v

backend-lint:
	cd backend && black --check app tests && ruff check app tests && mypy app

frontend-install:
	cd frontend && npm install

frontend-run:
	cd frontend && npm run dev

frontend-test:
	cd frontend && npm run test

frontend-lint:
	cd frontend && npm run lint && npm run typecheck

# Docker Compose targets land in Phase 17.
