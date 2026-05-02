.PHONY: run test format lint seed

run:
	set PYTHONPATH=. && uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

test:
	set PYTHONPATH=. && python -m pytest -q backend/tests

format:
	black .
	ruff check . --fix

lint:
	ruff check .

seed:
	set PYTHONPATH=. && python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"