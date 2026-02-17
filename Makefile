# Makefile for ArenaAgent development

.PHONY: help install install-dev test lint format clean build docs

help:
	@echo "ArenaAgent Development Commands"
	@echo "================================"
	@echo "install        Install package"
	@echo "install-dev    Install with dev dependencies"
	@echo "test           Run tests"
	@echo "test-cov       Run tests with coverage"
	@echo "lint           Run linters"
	@echo "format         Format code with black and isort"
	@echo "typecheck      Run mypy type checker"
	@echo "clean          Remove build artifacts"
	@echo "build          Build distribution packages"
	@echo "docs           Build documentation"
	@echo "pre-commit     Run pre-commit hooks"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install
	playwright install chromium

test:
	pytest

test-cov:
	pytest --cov=arenaagent --cov-report=html --cov-report=term-missing

test-watch:
	pytest-watch

lint:
	flake8 arenaagent/
	pylint arenaagent/

format:
	black arenaagent/ tests/
	isort arenaagent/ tests/

typecheck:
	mypy arenaagent/

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish-test: build
	twine upload --repository testpypi dist/*

publish: build
	twine upload dist/*

docs:
	cd docs && make html

init-dev: install-dev
	@echo "Development environment initialized!"
	@echo "Next steps:"
	@echo "  1. Run: arenaagent init"
	@echo "  2. Run: make test"
	@echo "  3. Start coding!"
