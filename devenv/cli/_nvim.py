"""Neovim installer.

Lays out the team's Neovim environment on a Linux server:

* Clones Vundle into ``~/.vim/bundle/Vundle.vim`` (the bundled ``init.vim``
  still drives plugins through Vundle, sharing the bundle directory with
  any legacy vim install).
* Deploys ``init.vim`` and ``coc-settings.json`` into ``~/.config/nvim/``.
* Installs ``coc.nvim`` as a native neovim pack under
  ``~/.local/share/nvim/site/pack/coc/start/coc.nvim`` (release branch).
* Runs ``:PluginInstall`` headlessly to fetch Vundle plugins.
* Runs ``:CocInstall`` headlessly to fetch coc extensions
  (``coc-pyright``, ``coc-clangd``). Requires ``node`` on PATH.
"""

from __future__ import annotations

from devenv.cli._installer import (
    InstallContext,
    InstallError,
    deploy_dotfile,
    ensure_command,
    ensure_dir,
    git_clone_idempotent,
    package_file,
    run,
)

VUNDLE_REPO = "https://github.com/VundleVim/Vundle.vim.git"
COC_REPO = "https://github.com/neoclide/coc.nvim.git"
COC_BRANCH = "release"
COC_EXTENSIONS = ("coc-pyright", "coc-clangd")


def install(ctx: InstallContext) -> None:
    """Deploy nvim dotfiles, Vundle, coc.nvim, and coc extensions."""
    ensure_command("nvim")
    ensure_command("git")

    nvim_config = ctx.home / ".config" / "nvim"
    ensure_dir(nvim_config, ctx)

    deploy_dotfile(package_file("nvim", "init.vim"), nvim_config / "init.vim", ctx)
    deploy_dotfile(
        package_file("nvim", "coc-settings.json"),
        nvim_config / "coc-settings.json",
        ctx,
    )

    vim_bundle = ctx.home / ".vim" / "bundle" / "Vundle.vim"
    git_clone_idempotent(VUNDLE_REPO, vim_bundle, ctx, depth=1)

    coc_dest = ctx.home / ".local" / "share" / "nvim" / "site" / "pack" / "coc" / "start" / "coc.nvim"
    _git_clone_branch(COC_REPO, coc_dest, COC_BRANCH, ctx)

    init_vim = nvim_config / "init.vim"
    run(
        [
            "nvim",
            "--headless",
            "-u",
            str(init_vim),
            "-c",
            "PluginInstall",
            "-c",
            "qa",
        ],
        ctx,
        check=False,
    )

    _install_coc_extensions(init_vim, ctx)


def _git_clone_branch(url: str, dest, branch: str, ctx: InstallContext) -> None:
    """Idempotently clone ``url`` at ``branch`` into ``dest``."""
    from devenv.cli._installer import _log  # noqa: PLC0415 — internal helper.

    if dest.exists():
        _log(f"already present: {dest} (skip clone)")
        return
    ensure_dir(dest.parent, ctx)
    run(
        ["git", "clone", "--depth", "1", "--branch", branch, url, str(dest)],
        ctx,
    )


def _install_coc_extensions(init_vim, ctx: InstallContext) -> None:
    """Run ``:CocInstall`` headlessly for the team's coc extension set."""
    from devenv.cli._installer import _log  # noqa: PLC0415 — internal helper.

    try:
        ensure_command("node")
    except InstallError:
        _log(
            "node not found on PATH — skipping :CocInstall."
            " Install Node.js and run `:CocInstall coc-pyright coc-clangd` manually.",
            color="yellow",
        )
        return

    coc_cmd = f":CocInstall -sync {' '.join(COC_EXTENSIONS)}|qa"
    run(
        [
            "nvim",
            "--headless",
            "-u",
            str(init_vim),
            "-c",
            coc_cmd,
        ],
        ctx,
        check=False,
    )
