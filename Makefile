.PHONY: install lint test clean help

# Default python version
PYTHON_VERSION ?= 3.10
TEST_MODE ?= unit_test
TEST_WORKERS ?= 0

# Validate TEST_MODE value
ifeq ($(filter $(TEST_MODE),unit_test),)
$(error TEST_MODE must be 'unit_test')
endif

# Developer bootstrap (uv sync + pre-commit install).
# NOTE: this is NOT the end-user environment install — for that, run
# `devenv install` after `uv pip install -e .`.
install:
	@echo "Installing dev environment (Python $(PYTHON_VERSION))..."
	@bash scripts/install_packages.sh --python_ver $(PYTHON_VERSION)

# Run pre-commit on all files
lint:
	@echo "Running pre-commit on all files..."
	@uv run pre-commit run --all-files

# Run pytest
test:
	@echo "Running $(TEST_MODE) tests..."
	@uv run pytest tests/$(TEST_MODE) -n $(TEST_WORKERS)

# Clean caches and build artifacts
clean:
	@echo "Cleaning caches and build artifacts..."
	@rm -rf build/ dist/ ./*.egg-info/
	@rm -rf .ruff_cache/ .pytest_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	@echo "Clean done."

help:
	@echo "Available targets:"
	@echo "  install   - Bootstrap dev environment (uv sync + pre-commit install)"
	@echo "              Usage: make install [PYTHON_VERSION=3.10|3.11|3.12|3.13]"
	@echo "              For end-user setup, run: uv pip install -e . && devenv install"
	@echo "  lint      - Run pre-commit hooks on all files"
	@echo "  test      - Run pytest unit tests [TEST_WORKERS=N]"
	@echo "  clean     - Remove caches and build artifacts"
	@echo "  help      - Show this help message"
