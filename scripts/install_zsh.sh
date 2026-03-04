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

# Install optional dependencies (fzf, thefuck, autojump)
export PATH="$HOME/.local/bin:$HOME/bin:$PATH"
NEED_SUDO=0
APT_PACKAGES=()

if ! command -v fzf &> /dev/null; then
    if [[ ! -d "$HOME/.fzf" ]]; then
        git clone --depth 1 https://github.com/junegunn/fzf.git "$HOME/.fzf"
    fi
    if [[ -x "$HOME/.fzf/install" ]]; then
        "$HOME/.fzf/install" --all
    fi
fi

if ! command -v thefuck &> /dev/null; then
    if command -v pip3 &> /dev/null; then
        pip3 install --user thefuck 2>/dev/null || true
    fi
    if command -v pip &> /dev/null && ! command -v thefuck &> /dev/null; then
        pip install --user thefuck 2>/dev/null || true
    fi
    if ! command -v thefuck &> /dev/null; then
        APT_PACKAGES+=(thefuck)
        NEED_SUDO=1
    fi
fi

if ! command -v autojump &> /dev/null; then
    APT_PACKAGES+=(autojump)
    NEED_SUDO=1
fi

if [[ $NEED_SUDO -eq 1 && ${#APT_PACKAGES[@]} -gt 0 ]]; then
    if command -v apt-get &> /dev/null || command -v apt &> /dev/null; then
        read -p "일부 패키지 설치에 sudo가 필요합니다. 계속할까요? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y "${APT_PACKAGES[@]}"
            else
                sudo apt update
                sudo apt install -y "${APT_PACKAGES[@]}"
            fi
        fi
    fi
fi

# Setup zsh config files
cp packages/zsh/zshrc "$HOME/.zshrc"
cp packages/zsh/devconfig "$HOME/.devconfig"
cp packages/zsh/p10k.zsh "$HOME/.p10k.zsh"
mkdir -p "$HOME/.oh-my-zsh/custom"
cp packages/zsh/aliases.zsh "$HOME/.oh-my-zsh/custom/aliases.zsh"

##########################################################################
