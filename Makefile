.PHONY: help test lint format check install clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install              - Install dependencies with uv"
	@echo "  test                 - Run all tests (unit + integration)"
	@echo "  test-unit            - Run unit tests only"
	@echo "  test-integration     - Run integration tests only"
	@echo "  test-cov             - Run all tests with coverage"
	@echo "  test-unit-cov        - Run unit tests with coverage"
	@echo "  test-integration-cov - Run integration tests with coverage"
	@echo "  lint                 - Run all linting checks (includes mypy)"
	@echo "  lint-quick           - Run linting checks (skip mypy type checking)"
	@echo "  format               - Auto-fix formatting issues"
	@echo "  check                - Run both linting and tests"
	@echo "  clean                - Clean up cache and temp files"

# Development setup
install:
	uv sync --dev

# Testing targets
test: test-unit test-integration
	@echo "All tests completed!"

test-unit:
	@echo "Running unit tests..."
	uv run pytest tests/unit_tests/ -v

test-integration:
	@echo "Running integration tests..."
	uv run pytest tests/integration_tests/ -v

test-cov:
	uv run pytest --cov=connectchain --cov-report=term-missing

test-unit-cov:
	uv run pytest tests/unit_tests/ --cov=connectchain --cov-report=term-missing

test-integration-cov:
	uv run pytest tests/integration_tests/ --cov=connectchain --cov-report=term-missing

test-verbose:
	uv run pytest -v

# Linting targets
lint: lint-black lint-isort lint-pylint lint-mypy
	@echo ""
	@echo "All linting checks completed!"

lint-black:
	@echo "Running Black formatting check..."
	@uv run black --check --diff connectchain/ || (echo "Black formatting check failed. Run 'make format' to fix." && exit 1)
	@echo "Black formatting check passed"

lint-isort:
	@echo "Running isort import sorting check..."
	@uv run isort --check-only --diff connectchain/ || (echo "Import sorting check failed. Run 'make format' to fix." && exit 1)
	@echo "Import sorting check passed"

lint-pylint:
	@echo "Running Pylint code analysis..."
	@uv run pylint --fail-under=9.0 connectchain/ || (echo "Pylint analysis failed" && exit 1)
	@echo "Pylint analysis passed"

lint-mypy:
	@echo "Running MyPy type checking..."
	@uv run mypy connectchain/ || (echo "MyPy type checking failed" && exit 1)
	@echo "MyPy type checking passed"

# Auto-formatting
format:
	@echo "Auto-formatting code..."
	@echo "  Running Black formatter..."
	@uv run black connectchain/
	@echo "  Running isort import sorter..."
	@uv run isort connectchain/
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