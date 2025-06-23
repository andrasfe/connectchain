.PHONY: help test lint format check install clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install    - Install dependencies with uv"
	@echo "  test       - Run all tests"
	@echo "  test-cov   - Run tests with coverage"
	@echo "  lint       - Run all linting checks (includes mypy)"
	@echo "  lint-quick - Run linting checks (skip mypy type checking)"
	@echo "  format     - Auto-fix formatting issues"
	@echo "  check      - Run both linting and tests"
	@echo "  clean      - Clean up cache and temp files"

# Development setup
install:
	uv sync --dev

# Testing targets
test:
	python -m pytest

test-cov:
	python -m pytest --cov=connectchain --cov-report=term-missing

test-verbose:
	python -m pytest -v

# Linting targets
lint: lint-black lint-isort lint-pylint lint-mypy
	@echo ""
	@echo "All linting checks completed!"

lint-black:
	@echo "Running Black formatting check..."
	@python -m black --check --diff connectchain/ || (echo "Black formatting check failed. Run 'make format' to fix." && exit 1)
	@echo "Black formatting check passed"

lint-isort:
	@echo "Running isort import sorting check..."
	@python -m isort --check-only --diff connectchain/ || (echo "Import sorting check failed. Run 'make format' to fix." && exit 1)
	@echo "Import sorting check passed"

lint-pylint:
	@echo "Running Pylint code analysis..."
	@python -m pylint --fail-under=9.0 connectchain/ || (echo "Pylint analysis failed" && exit 1)
	@echo "Pylint analysis passed"

lint-mypy:
	@echo "Running MyPy type checking..."
	@python -m mypy connectchain/ || (echo "MyPy type checking failed" && exit 1)
	@echo "MyPy type checking passed"

# Auto-formatting
format:
	@echo "Auto-formatting code..."
	@echo "  Running Black formatter..."
	@python -m black connectchain/
	@echo "  Running isort import sorter..."
	@python -m isort connectchain/
	@echo "Code formatting completed!"

# Combined checks
check: lint test

# Less strict linting (skip mypy for now)
lint-quick: lint-black lint-isort lint-pylint
	@echo ""
	@echo "Quick linting checks completed! (MyPy skipped)"

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/ 