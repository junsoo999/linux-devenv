"""Neovim installer.

Lays out the team's Neovim environment on a Linux server:

* If ``nvim`` is missing from PATH, downloads the official prebuilt
  release tarball into ``~/.local/opt/nvim/`` and symlinks the binary
  to ``~/.local/bin/nvim``.
* Clones Vundle into ``~/.vim/bundle/Vundle.vim`` (the bundled
  ``init.vim`` still drives plugins through Vundle, sharing the bundle
  directory with any legacy vim install).
* Deploys ``init.vim`` and ``coc-settings.json`` into ``~/.config/nvim/``.
* Installs ``coc.nvim`` as a native neovim pack under
  ``~/.local/share/nvim/site/pack/coc/start/coc.nvim`` (release branch).
* Runs ``:PluginInstall`` headlessly to fetch Vundle plugins.
* Runs ``:CocInstall`` headlessly to fetch coc extensions
  (``coc-pyright``, ``coc-clangd``). Requires ``node`` on PATH.
"""

from __future__ import annotations

import platform
import shutil
from pathlib import Path

from devenv.cli._installer import (
    InstallContext,
    InstallError,
    _log,
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

# Use the ``stable`` release tag so we follow whatever Neovim's current
# stable build is without pinning to a single point version.
NVIM_RELEASE_TAG = "stable"
NVIM_RELEASE_BASE = "https://github.com/neovim/neovim/releases/download"


def install(ctx: InstallContext) -> None:
    """Deploy nvim binary (if needed), dotfiles, Vundle, coc.nvim, and coc extensions."""
    ensure_command("git")
    nvim_bin = _ensure_nvim_binary(ctx)

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
            nvim_bin,
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

    _install_coc_extensions(nvim_bin, init_vim, ctx)


def _ensure_nvim_binary(ctx: InstallContext) -> str:
    """Ensure ``nvim`` is available; install to ``~/.local`` when missing.

    Returns the absolute path to the ``nvim`` binary that subsequent
    commands should invoke. When ``nvim`` was already on ``PATH`` this
    is whatever ``shutil.which`` returned; otherwise it is the symlink
    deployed under ``~/.local/bin/nvim``.
    """
    found = shutil.which("nvim")
    if found:
        _log(f"nvim already present: {found}")
        return found

    asset = _nvim_release_asset()
    if asset is None:
        raise InstallError(
            "no Neovim prebuilt release for this CPU architecture"
            f" ({platform.machine()}); install nvim manually and rerun.",
        )

    ensure_command("curl")
    ensure_command("tar")

    local_root = ctx.home / ".local"
    opt_dir = local_root / "opt" / "nvim"
    bin_dir = local_root / "bin"
    ensure_dir(opt_dir.parent, ctx)
    ensure_dir(bin_dir, ctx)

    url = f"{NVIM_RELEASE_BASE}/{NVIM_RELEASE_TAG}/{asset}"
    tarball = opt_dir.parent / asset

    if not opt_dir.exists():
        run(["curl", "-fsSL", "-o", str(tarball), url], ctx)
        # Extract under a temp name first, then move into opt/nvim so
        # the final layout is independent of the tarball's top-level dir.
        staging = opt_dir.parent / f"nvim-staging-{NVIM_RELEASE_TAG}"
        if ctx.dry_run:
            _log(f"[dry-run] mkdir -p {staging}")
            _log(f"[dry-run] tar -xzf {tarball} -C {staging} --strip-components=1")
            _log(f"[dry-run] mv {staging} {opt_dir}")
            _log(f"[dry-run] rm {tarball}")
        else:
            if staging.exists():
                shutil.rmtree(staging)
            staging.mkdir(parents=True)
            run(
                ["tar", "-xzf", str(tarball), "-C", str(staging), "--strip-components=1"],
                ctx,
            )
            staging.rename(opt_dir)
            tarball.unlink(missing_ok=True)
            # macOS quarantines binaries downloaded via curl; strip the
            # attribute so the nvim binary is not blocked by Gatekeeper.
            if platform.system() == "Darwin" and shutil.which("xattr"):
                run(["xattr", "-dr", "com.apple.quarantine", str(opt_dir)], ctx, check=False)
    else:
        _log(f"already present: {opt_dir} (skip download)")

    nvim_target = opt_dir / "bin" / "nvim"
    nvim_link = bin_dir / "nvim"
    if ctx.dry_run:
        _log(f"[dry-run] ln -sf {nvim_target} {nvim_link}")
        return str(nvim_link)

    if nvim_link.is_symlink() or nvim_link.exists():
        nvim_link.unlink()
    nvim_link.symlink_to(nvim_target)
    _log(f"linked {nvim_link} → {nvim_target}", color="green")

    if not shutil.which("nvim"):
        _log(
            f'{bin_dir} is not on your PATH yet — add `export PATH="{bin_dir}:$PATH"` to your shell rc.',
            color="yellow",
        )
    return str(nvim_link)


def _nvim_release_asset() -> str | None:
    """Map the current OS + CPU architecture to a Neovim release asset name."""
    machine = platform.machine().lower()
    system = platform.system()
    if system == "Darwin":
        if machine in ("x86_64", "amd64"):
            return "nvim-macos-x86_64.tar.gz"
        if machine in ("aarch64", "arm64"):
            return "nvim-macos-arm64.tar.gz"
        return None
    if machine in ("x86_64", "amd64"):
        return "nvim-linux-x86_64.tar.gz"
    if machine in ("aarch64", "arm64"):
        return "nvim-linux-arm64.tar.gz"
    return None


def _git_clone_branch(url: str, dest: Path, branch: str, ctx: InstallContext) -> None:
    """Idempotently clone ``url`` at ``branch`` into ``dest``."""
    if dest.exists():
        _log(f"already present: {dest} (skip clone)")
        return
    ensure_dir(dest.parent, ctx)
    run(
        ["git", "clone", "--depth", "1", "--branch", branch, url, str(dest)],
        ctx,
    )


def _install_coc_extensions(nvim_bin: str, init_vim: Path, ctx: InstallContext) -> None:
    """Run ``:CocInstall`` headlessly for the team's coc extension set."""
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
            nvim_bin,
            "--headless",
            "-u",
            str(init_vim),
            "-c",
            coc_cmd,
        ],
        ctx,
        check=False,
    )
