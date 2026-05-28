#!/bin/bash

##########################################################################
##  Bootstrap dev environment for linux-devenv
##
##  - sets up uv-managed virtualenv (.venv)
##  - syncs dev dependencies
##  - installs pre-commit hooks
##
##  This is NOT the end-user environment install. End users run:
##      uv pip install -e . && devenv install
##
##########################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_PATH="$(dirname "$SCRIPT_DIR")"
pushd "$WORKSPACE_PATH" >/dev/null || exit 1

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Bootstrap dev environment for linux-devenv"
    echo
    echo "Options:"
    echo "  -p, --python_ver PYTHON_VERSION   Python version (default: 3.10)"
    echo "  -h, --help                        Show this help message"
}

PYTHON_VERSION="3.10"

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--python_ver)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

if [[ "$PYTHON_VERSION" != "3.10" && "$PYTHON_VERSION" != "3.11" \
    && "$PYTHON_VERSION" != "3.12" && "$PYTHON_VERSION" != "3.13" ]]; then
    echo "Error: Python version must be one of 3.10 / 3.11 / 3.12 / 3.13"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "[ERROR] uv is not installed. Install with:"
    echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "[INFO] uv sync (python ${PYTHON_VERSION})"
uv sync --python "${PYTHON_VERSION}"

echo "[INFO] uv pip install -e . (editable install for devenv CLI)"
uv pip install -e .

echo "[INFO] pre-commit install"
uv run pre-commit install

popd >/dev/null || exit 1

echo "[INFO] done. Try: uv run devenv --help"
