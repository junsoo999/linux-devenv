#!/bin/bash

##########################################################################
##  Install Tmux
##
##  Authors:  Junsoo    Kim   ( js.kim@hyperaccel.ai        )
##  Version:  0.0.1
##  Date:     2026-05-22      ( v0.0.1, init                )
##
##########################################################################

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo -e "[ERROR\t] Tmux is not installed. Please install tmux first."
    exit 1
fi

# Copy tmux.conf file to home directory
cp packages/tmux/tmux.conf "$HOME/.tmux.conf"

# Install TPM (Tmux Plugin Manager)
mkdir -p "$HOME/.tmux/plugins"
if [[ ! -d "$HOME/.tmux/plugins/tpm" ]]; then
    git clone https://github.com/tmux-plugins/tpm "$HOME/.tmux/plugins/tpm"
fi

# Install plugins defined in tmux.conf
"$HOME/.tmux/plugins/tpm/bin/install_plugins"

##########################################################################
