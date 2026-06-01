"""Shared installation primitives.

The CLI surface in :mod:`devenv.cli` is intentionally thin; all
reusable logic for ensuring directories, idempotent ``git clone``,
backing up + deploying dotfiles, and shelling out to external
installers lives here. Per-tool modules (:mod:`devenv.cli._zsh`,
``_vim``, ``_tmux``) compose these helpers.
"""

from __future__ import annotations

import contextlib
import datetime as _dt
import shutil
import subprocess
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Sequence

import click


class InstallError(RuntimeError):
    """Raised when an installation step fails in a way the CLI should surface."""


class CommandMissingError(InstallError):
    """A required executable was not found on PATH."""


@dataclass
class InstallContext:
    """Runtime context threaded through every installer step.

    Attributes:
        home: Target HOME directory. ``Path.home()`` in normal use,
            redirected in tests.
        force: When True, overwrite existing dotfiles without backing
            them up.
        dry_run: When True, log every command but execute nothing.
        assume_yes: When True, treat interactive prompts as accepted.
    """

    home: Path
    force: bool = False
    dry_run: bool = False
    assume_yes: bool = False


def packages_root() -> Path:
    """Return the on-disk path to the bundled dotfile assets.

    Resolves ``devenv/packages/`` whether the package is installed as a
    wheel, an editable install, or used from the source checkout.
    """
    return Path(str(resources.files("devenv").joinpath("packages")))


def package_file(*parts: str) -> Path:
    """Return the path to a specific bundled asset.

    Example:
        ``package_file("zsh", "zshrc")`` → ``.../devenv/packages/zsh/zshrc``.
    """
    return packages_root().joinpath(*parts)


def _log(message: str, *, color: str | None = None) -> None:
    """Emit a single user-facing log line via Click."""
    click.secho(f"    {message}", fg=color)


def ensure_command(name: str) -> str:
    """Verify ``name`` is on PATH; return its absolute path.

    Raises:
        CommandMissingError: If the command is not installed.
    """
    found = shutil.which(name)
    if not found:
        raise CommandMissingError(name)
    return found


def ensure_dir(path: Path, ctx: InstallContext) -> None:
    """Create ``path`` (and parents) idempotently."""
    if ctx.dry_run:
        _log(f"[dry-run] mkdir -p {path}")
        return
    path.mkdir(parents=True, exist_ok=True)


def run(
    cmd: Sequence[str],
    ctx: InstallContext,
    *,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str] | None:
    """Run a subprocess, respecting ``ctx.dry_run``.

    Args:
        cmd: Argv list.
        ctx: InstallContext.
        check: Raise InstallError on non-zero exit.
        env: Extra environment variables merged on top of ``os.environ``.

    Returns:
        ``CompletedProcess`` when executed, ``None`` in dry-run mode.

    Raises:
        InstallError: When ``check`` is True and the command fails.
    """
    rendered = " ".join(cmd)
    if ctx.dry_run:
        _log(f"[dry-run] {rendered}")
        return None
    import os as _os

    merged_env = None
    if env:
        merged_env = {**_os.environ, **env}
    _log(f"$ {rendered}", color="bright_black")
    result = subprocess.run(  # noqa: S603 — arguments are explicit, not shell-interpolated
        list(cmd),
        check=False,
        text=True,
        env=merged_env,
    )
    if check and result.returncode != 0:
        raise InstallError(f"command failed ({result.returncode}): {rendered}")
    return result


def run_shell(command: str, ctx: InstallContext, *, check: bool = True) -> None:
    """Run a string command through ``/bin/bash -lc``.

    Reserved for cases where we *must* invoke a remote installer that
    expects a shell (e.g. ``sh -c "$(curl ... install.sh)"``). Prefer
    :func:`run` for argv-style commands.
    """
    if ctx.dry_run:
        _log(f"[dry-run] bash -lc '{command}'")
        return
    _log(f"$ bash -lc '{command}'", color="bright_black")
    result = subprocess.run(  # noqa: S602 — user-controlled command intended.
        ["/bin/bash", "-lc", command],
        check=False,
        text=True,
    )
    if check and result.returncode != 0:
        raise InstallError(f"shell command failed ({result.returncode}): {command}")


def git_clone_idempotent(
    url: str,
    dest: Path,
    ctx: InstallContext,
    *,
    depth: int | None = None,
) -> bool:
    """Clone ``url`` into ``dest`` if absent.

    Returns:
        True when a clone happened, False when ``dest`` already existed.
    """
    if dest.exists():
        _log(f"already present: {dest} (skip clone)")
        return False
    ensure_dir(dest.parent, ctx)
    cmd = ["git", "clone"]
    if depth is not None:
        cmd += ["--depth", str(depth)]
    cmd += [url, str(dest)]
    run(cmd, ctx)
    return True


def deploy_dotfile(src: Path, dest: Path, ctx: InstallContext) -> None:
    """Copy ``src`` to ``dest``, backing up any existing file first.

    Behaviour:
    - Missing parent directory is created.
    - Existing ``dest`` is renamed to ``dest.bak.<UTC-timestamp>`` unless
      ``ctx.force`` is True (then the existing file is removed).
    - Symlinks at ``dest`` are removed (we replace with a regular file).
    """
    ensure_dir(dest.parent, ctx)
    if ctx.dry_run:
        if dest.exists() or dest.is_symlink():
            action = "rm" if ctx.force else "backup"
            _log(f"[dry-run] {action} existing {dest}")
        _log(f"[dry-run] cp {src} → {dest}")
        return

    if dest.is_symlink() or dest.exists():
        if ctx.force:
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            else:
                shutil.rmtree(dest)
            _log(f"removed existing {dest} (--force)", color="yellow")
        else:
            ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%d%H%M%S")
            backup = dest.with_name(dest.name + f".bak.{ts}")
            dest.rename(backup)
            _log(f"backed up {dest} → {backup}", color="yellow")

    shutil.copy2(src, dest)
    with contextlib.suppress(OSError):
        dest.chmod(dest.stat().st_mode | 0o200)
    _log(f"deployed {src.name} → {dest}", color="green")


def confirm(prompt: str, ctx: InstallContext, *, default: bool = False) -> bool:
    """Ask a yes/no question, auto-accepting under ``--yes`` / ``--dry-run``."""
    if ctx.assume_yes or ctx.dry_run:
        _log(f"{prompt} → auto-yes", color="yellow")
        return True
    return click.confirm(prompt, default=default)
