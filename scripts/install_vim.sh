#!/bin/bash

##########################################################################
##  Install Vim
##
##  Authors:  Junsoo    Kim   ( js.kim@hyperaccel.ai        )
##  Version:  0.0.1
##  Date:     2025-07-05      ( v0.0.1, init                )
##
##########################################################################

# Check if vim is installed
if ! command -v vim &> /dev/null; then
    echo -e "[ERROR\t] Vim is not installed. Please install vim first."
    exit 1
fi

# Copy vimrc file to home directory
mkdir -p $HOME/.vim
cp packages/vim/vimrc $HOME/.vim/vimrc

# Install vim bundle by git
mkdir -p $HOME/.vim/bundle
git clone https://github.com/VundleVim/Vundle.vim.git $HOME/.vim/bundle/Vundle.vim

# Install plugins using vim
vim -E -s -c "source $HOME/.vim/vimrc" -c "PluginInstall" -c "qa"

##########################################################################