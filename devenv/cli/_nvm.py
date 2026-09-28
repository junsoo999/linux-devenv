"""nvm (Node Version Manager) installer.

`nvm <https://github.com/nvm-sh/nvm>`_ manages per-user Node.js versions.
This installer:

* Clones the nvm repository into ``~/.nvm`` at a pinned release tag
  (:data:`NVM_VERSION`) so every team member gets the same nvm. The clone
  is skipped when the directory already exists.
* Runs ``nvm install --lts`` (idempotent: nvm itself is a no-op when the
  current LTS is already installed) and points the ``default`` alias at
  ``lts/*`` so new shells pick it up.

Shell integration is handled by the oh-my-zsh ``nvm`` plugin enabled in the
managed ``zshrc`` (``zstyle ':omz:plugins:nvm' autoload yes``), so no extra
dotfile is deployed here.
"""

from __future__ import annotations

from devenv.cli._installer import (
    InstallContext,
    _log,
    ensure_command,
    git_clone_idempotent,
    run_shell,
)

NVM_REPO = "https://github.com/nvm-sh/nvm.git"
NVM_VERSION = "v0.40.7"


def install(ctx: InstallContext) -> None:
    """Clone nvm into ``~/.nvm`` and install the latest Node.js LTS."""
    ensure_command("git")
    nvm_dir = ctx.home / ".nvm"

    if git_clone_idempotent(NVM_REPO, nvm_dir, ctx, depth=1, branch=NVM_VERSION):
        _log(f"nvm {NVM_VERSION} cloned into {nvm_dir}")

    # ``bash -lc`` may source a profile that sets NVM_DIR; pin it to ctx.home
    # so ``--home`` isolation is respected.
    run_shell(
        f'export NVM_DIR="{nvm_dir}" && . "$NVM_DIR/nvm.sh" && nvm install --lts && nvm alias default "lts/*"',
        ctx,
    )
