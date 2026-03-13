.PHONY: install dev lint format test build publish clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

lint:
	ruff check watcherr/ tests/

format:
	ruff format watcherr/ tests/
	ruff check --fix watcherr/ tests/

test:
	pytest tests/ -v

build:
	python -m build

publish:
	twine upload dist/*

clean:
	rm -rf dist/ build/ *.egg-info
