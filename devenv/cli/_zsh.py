"""Z-Shell installer — mirrors the legacy ``install_zsh.sh``.

Installs oh-my-zsh non-interactively, powerlevel10k, the standard zsh
plugin set, optional helpers (fzf / thefuck / autojump), and deploys
the bundled zsh dotfiles into the target HOME.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from devenv.cli._installer import (
    InstallContext,
    _log,
    confirm,
    deploy_dotfile,
    ensure_command,
    ensure_dir,
    git_clone_idempotent,
    package_file,
    run,
    run_shell,
)
from devenv.cli._platform import is_macos

OH_MY_ZSH_INSTALL_URL = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
POWERLEVEL10K_REPO = "https://github.com/romkatv/powerlevel10k.git"

_ZSH_PLUGINS: list[tuple[str, str]] = [
    ("https://github.com/zsh-users/zsh-autosuggestions", "zsh-autosuggestions"),
    ("https://github.com/zsh-users/zsh-syntax-highlighting.git", "zsh-syntax-highlighting"),
    ("https://github.com/zsh-users/zsh-history-substring-search", "zsh-history-substring-search"),
    ("https://github.com/MichaelAquilina/zsh-you-should-use", "you-should-use"),
    ("https://github.com/zsh-users/zsh-completions.git", "zsh-completions"),
]


def install(ctx: InstallContext) -> None:
    """Install zsh stack into ``ctx.home``."""
    ensure_command("zsh")
    ensure_command("git")
    ensure_command("curl")

    _install_oh_my_zsh(ctx)
    _install_powerlevel10k(ctx)
    _install_plugins(ctx)
    _install_optional_dependencies(ctx)
    _deploy_dotfiles(ctx)


def _zsh_custom(ctx: InstallContext) -> Path:
    """Return ``$ZSH_CUSTOM`` equivalent (``$HOME/.oh-my-zsh/custom``)."""
    return ctx.home / ".oh-my-zsh" / "custom"


def _install_oh_my_zsh(ctx: InstallContext) -> None:
    oh_my_zsh_dir = ctx.home / ".oh-my-zsh"
    if oh_my_zsh_dir.exists():
        return
    command = (
        f"set -e -o pipefail; "
        f"curl -fsSL {OH_MY_ZSH_INSTALL_URL} | "
        f'RUNZSH=no CHSH=no KEEP_ZSHRC=yes HOME="{ctx.home}" sh'
    )
    run_shell(command, ctx)


def _install_powerlevel10k(ctx: InstallContext) -> None:
    dest = _zsh_custom(ctx) / "themes" / "powerlevel10k"
    git_clone_idempotent(POWERLEVEL10K_REPO, dest, ctx, depth=1)


def _install_plugins(ctx: InstallContext) -> None:
    base = _zsh_custom(ctx) / "plugins"
    ensure_dir(base, ctx)
    for url, name in _ZSH_PLUGINS:
        git_clone_idempotent(url, base / name, ctx)


def _install_optional_dependencies(ctx: InstallContext) -> None:
    """Install fzf / thefuck / autojump if missing.

    fzf is installed via its official ``install`` script under
    ``$HOME/.fzf``. thefuck is tried via pip first, then falls back to
    the system package manager (apt on Linux, brew on macOS). autojump
    is queued for the same package manager. Apt installs require sudo
    and are confirmed once with the user; brew installs do not.
    """
    pending_packages: list[str] = []

    if shutil.which("fzf") is None:
        fzf_dir = ctx.home / ".fzf"
        git_clone_idempotent("https://github.com/junegunn/fzf.git", fzf_dir, ctx, depth=1)
        installer = fzf_dir / "install"
        if installer.exists() or ctx.dry_run:
            run([str(installer), "--all"], ctx, check=False)

    if shutil.which("thefuck") is None:
        # On macOS the pip --user prefix (``~/Library/Python/3.x/bin``)
        # is not on PATH by default, so a successful pip install would
        # still leave ``shutil.which("thefuck")`` returning None and
        # trigger reinstall on every run. Route macOS straight to brew.
        if is_macos():
            pending_packages.append("thefuck")
        else:
            installed = False
            for pip in ("pip3", "pip"):
                if shutil.which(pip) is None:
                    continue
                result = run([pip, "install", "--user", "thefuck"], ctx, check=False)
                if result is None or result.returncode == 0:
                    installed = True
                    break
            if not installed:
                pending_packages.append("thefuck")

    if shutil.which("autojump") is None:
        pending_packages.append("autojump")

    if not pending_packages:
        return

    if is_macos():
        brew = shutil.which("brew")
        if brew is None:
            _log(
                f"brew not found — skipping {', '.join(pending_packages)}."
                " Install Homebrew (https://brew.sh) and rerun, or install manually.",
                color="yellow",
            )
            return
        run([brew, "install", *pending_packages], ctx, check=False)
        return

    apt = shutil.which("apt-get") or shutil.which("apt")
    if apt is None:
        return
    prompt = f"일부 패키지({', '.join(pending_packages)}) 설치에 sudo가 필요합니다. 계속할까요?"
    if not confirm(prompt, ctx):
        return
    if apt.endswith("apt-get"):
        run(["sudo", "apt-get", "update"], ctx, check=False)
        run(["sudo", "apt-get", "install", "-y", *pending_packages], ctx, check=False)
    else:
        run(["sudo", "apt", "update"], ctx, check=False)
        run(["sudo", "apt", "install", "-y", *pending_packages], ctx, check=False)


def _deploy_dotfiles(ctx: InstallContext) -> None:
    deploy_dotfile(package_file("zsh", "zshrc"), ctx.home / ".zshrc", ctx)
    deploy_dotfile(package_file("zsh", "devconfig"), ctx.home / ".devconfig", ctx)
    deploy_dotfile(package_file("zsh", "p10k.zsh"), ctx.home / ".p10k.zsh", ctx)
    custom_dir = _zsh_custom(ctx)
    ensure_dir(custom_dir, ctx)
    deploy_dotfile(
        package_file("zsh", "aliases.zsh"),
        custom_dir / "aliases.zsh",
        ctx,
    )
