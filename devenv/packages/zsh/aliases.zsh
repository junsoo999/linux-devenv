# Net alias
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias vi='nvim'
alias vc='vi ~/.zshrc'
alias va='vi ~/.oh-my-zsh/custom/aliases.zsh'
alias sc='source ~/.zshrc'

function cd
{
  builtin cd "$@" && pwd;
}

function clean-up-branch {
  git fetch --prune

  # Strip the 2-char status prefix ("  ", "* ", "+ ") before extracting the name
  local gone_branches
  gone_branches=$(git branch -vv | grep ': gone\]' | sed -E 's/^..//' | awk '{print $1}')

  if [[ -z "$gone_branches" ]]; then
    echo "No branches to clean up"
    return 0
  fi

  # Remove worktrees that have any of these branches checked out
  echo "$gone_branches" | while read -r branch; do
    local wt
    wt=$(git worktree list --porcelain | awk -v b="refs/heads/$branch" '
      /^worktree / { path=$2 }
      $0 == "branch " b { print path; exit }
    ')
    if [[ -n "$wt" ]]; then
      echo "Removing worktree: $wt"
      git worktree remove --force "$wt"
    fi
  done

  # Delete the branches
  echo "$gone_branches" | xargs git branch -D

  # Prune stale worktree admin records
  git worktree prune
}

# Project shortcuts
[[ ! -f $HOME/workspace/.shortcuts.zsh ]] || source $HOME/workspace/.shortcuts.zsh
[[ ! -f $HOME/worktrees/.shortcuts.zsh ]] || source $HOME/worktrees/.shortcuts.zsh
