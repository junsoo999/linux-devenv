.PHONY: help install setup clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install all development tools (zsh, vim)"
	@echo "  setup       - Setup directory structure"
	@echo "  clean       - Clean up temporary files"

# Check if the script is running on a Linux server
# If not, exit with error
check_linux:
	@if [ "$(shell uname -s)" != "Linux" ]; then \
		echo "This script must be run on a Linux server"; \
		exit 1; \
	fi

# Setup directory structure
setup: check_linux
	@echo "Setting up directory structure..."
	@./scripts/install_dir.sh

# Install all development tools
install: setup
	@echo "Installing zsh..."
	@./scripts/install_zsh.sh
	@echo "Installing vim..."
	@./scripts/install_vim.sh