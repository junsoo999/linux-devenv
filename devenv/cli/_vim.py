"""Vim installer — mirrors the legacy ``install_vim.sh``."""

from __future__ import annotations

from devenv.cli._installer import (
    InstallContext,
    deploy_dotfile,
    ensure_command,
    ensure_dir,
    git_clone_idempotent,
    package_file,
    run,
)

VUNDLE_REPO = "https://github.com/VundleVim/Vundle.vim.git"


def install(ctx: InstallContext) -> None:
    """Install Vundle, deploy ``vimrc``, and run ``:PluginInstall``."""
    ensure_command("vim")
    ensure_command("git")

    vim_dir = ctx.home / ".vim"
    ensure_dir(vim_dir, ctx)

    deploy_dotfile(package_file("vim", "vimrc"), vim_dir / "vimrc", ctx)

    git_clone_idempotent(VUNDLE_REPO, vim_dir / "bundle" / "Vundle.vim", ctx)

    run(
        [
            "vim",
            "-E",
            "-s",
            "-c",
            f"source {vim_dir / 'vimrc'}",
            "-c",
            "PluginInstall",
            "-c",
            "qa",
        ],
        ctx,
        check=False,
    )
