#!/bin/bash

##########################################################################
##  Install Z-Shell
##
##  Authors:  Junsoo    Kim   ( js.kim@hyperaccel.ai        )
##  Version:  0.0.1
##  Date:     2025-07-05      ( v0.0.1, init                )
##
##########################################################################

# Check if zsh is installed
if ! command -v zsh &> /dev/null; then
    echo -e "[ERROR\t] Z-Shell is not installed. Please install Z-Shell first."
    exit 1
fi

# Install oh-my-zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Install powerlevel10k
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k

# Powerlevel10k configuration
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-history-substring-search ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-history-substring-search
git clone https://github.com/MichaelAquilina/zsh-you-should-use ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/you-should-use

# Setup zsh script files
cp packages/zsh/zshrc $HOME/.zshrc
cp packages/zsh/zsh_aliases $HOME/.zsh_aliases
cp packages/zsh/zsh_ohmyzsh $HOME/.zsh_ohmyzsh
cp packages/zsh/p10k.zsh $HOME/.p10k.zsh

##########################################################################