# Net alias
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias tt='tmux attach -t'
alias tnew='tmux new -s '
alias tkill='tmux kill-sessing -t'
alias vi='vim -X'
alias vc='vi ~/.zshrc'
alias va='vi ~/.oh-my-zsh/custom/aliases.zsh'
alias sc='source ~/.zshrc'

function cd
{
  builtin cd "$@" && pwd;
}

