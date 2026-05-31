.PHONY: install run train test lint clean pre-commit

install:
	pip install -e .[dev]

run:
	python -m flywire_lsm.server

train:
	python scripts/train.py

test:
	python -m pytest tests/ -v --cov=flywire_lsm --cov-report=term-missing

lint:
	ruff check flywire_lsm/ scripts/ tests/ --fix

pre-commit:
	pre-commit run --all-files

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .coverage htmlcov dist build
