""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"" Neovim Configurations
""
"" Authors: Junsoo  Kim     ( js.kim@hyperaccel.ai                )
"" Version: 1.0.0
"" Date:    2024.01.24      ( v1.0.0                              )
""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"" Common Settings
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" Initial settings
set nocompatible
filetype off
syntax on

" General settings
set nu
set hlsearch
set autoindent
set autowrite
set autoread
set scrolloff=6
set cindent
set history=256
set laststatus=2
set shiftwidth=2
set showmatch
set smartcase
set smarttab
set smartindent
set softtabstop=2
set tabstop=2
set expandtab
set incsearch
set backspace=indent,eol,start
" set clipboard=unnamedplus
" Remember cursor location
au BufReadPost *
 \ if line("'\"") > 0 && line("'\"") <= line("$") |
 \ exe "norm g`\"" |
 \ endif

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"" VIM Bundle Pulgins
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" Vundle manager
Plugin 'VundleVim/Vundle.vim'
" VScode theme
Plugin 'tomasiser/vim-code-dark'
" File tree
Plugin 'scrooloose/nerdtree'
Plugin 'Xuyuanp/nerdtree-git-plugin'
Plugin 'michaeljsmith/vim-indent-object'
Plugin 'tiagofumo/vim-nerdtree-syntax-highlight'
Plugin 'ryanoasis/vim-devicons'
" Status bar
Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'
Plugin 'tpope/vim-fugitive'
Plugin 'ctrlpvim/ctrlp.vim'
Plugin 'edkolev/tmuxline.vim'
" Neat vundles
Plugin 'scrooloose/syntastic'
Plugin 'Raimondi/delimitMate'
Plugin 'airblade/vim-gitgutter'
Plugin 'jiangmiao/auto-pairs'
Plugin 'preservim/nerdcommenter'
Plugin 'ojroques/vim-oscyank'
call vundle#end()
filetype plugin indent on

" Vundle configuration
language en_US.UTF-8
set encoding=utf-8
set fileencodings=utf-8,cp949

" VisualStudioCode theme
color codedark

" Settings for vim-airline
let g:airline#extensions#tabline#enabled = 1
let g:airline_powerline_fonts = 1
let g:airline_theme= 'tomorrow'
let g:Powerline_symbols = 'fancy'

" Settings for vim-ctrlp
let g:ctrlp_custom_ignore = {
  \ 'dir':  '\.git$\|public$\|log$\|tmp$\|vendor$',
  \ 'file': '\v\.(exe|so|dll)$'
\ }

" Default settings for vim-gitgutter
let g:gitgutter_max_signs = 500

" OSC52: yank → local system clipboard (over SSH)
let s:VimOSCYankPostRegisters = ['', '+', '*']
function! s:VimOSCYankPostCallback(event)
    if exists('*OSCYankRegister') && a:event.operator == 'y' && index(s:VimOSCYankPostRegisters, a:event.regname) != -1
        call OSCYankRegister(a:event.regname)
    endif
endfunction
augroup VimOSCYankPost
    autocmd!
    autocmd TextYankPost * call s:VimOSCYankPostCallback(v:event)
augroup END

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"" Key Mappings
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

nnoremap <C-B>        <Esc>:NERDTreeToggle<CR>
inoremap <C-B>        <Esc>:NERDTreeToggle<CR>
nnoremap <C-F>        <ESC>:NERDTreeFocus<CR>
inoremap <C-F>        <ESC>:NERDTreeFocus<CR>
nnoremap <C-L>        <ESC>:bnext!<CR>
inoremap <C-L>        <ESC>:bnext!<CR>
nnoremap <C-H>        <ESC>:bprevious!<CR>
inoremap <C-H>        <ESC>:bprevious!<CR>
nmap <silent> gd      <Plug>(coc-definition)
nmap <silent> gy      <Plug>(coc-type-definition)
nmap <silent> gi      <Plug>(coc-implementation)
nmap <silent> gr      <Plug>(coc-references)
nnoremap <silent> K :call CocActionAsync('doHover')<CR>

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"" Nerd-Tree Enviornmentss
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

let g:NERDTreeGitStatusIndicatorMapCustom = {
  \ 'Modified'  :'✹',
  \ 'Staged'    :'✚',
  \ 'Untracked' :'✭',
  \ 'Renamed'   :'➜',
  \ 'Unmerged'  :'═',
  \ 'Deleted'   :'✖',
  \ 'Dirty'     :'✗',
  \ 'Ignored'   :'☒',
  \ 'Clean'     :'✔︎',
  \ 'Unknown'   :'?',
\ }
let g:NERDTreeShowHidden = 1
let g:NERDTreeMapActivateNode = 'l'
let g:NERDTreeMapCloseDir = 'h'
let g:NERDTreeMapJumpParent = 'H'

" If another buffer tries to replace NERDTree, put it in the other window, and bring back NERDTree.
autocmd BufEnter * if bufname('#') =~ 'NERD_tree_\d\+' && bufname('%') !~ 'NERD_tree_\d\+' && winnr('$') > 1 |
  \ let buf=bufnr() | buffer# | execute "normal! \<C-W>w" | execute 'buffer'.buf | endif
