"""Herdr installer.

`Herdr <https://herdr.dev>`_ is a terminal multiplexer / agent workspace
manager. This installer:

* Installs the ``herdr`` binary when it is missing from PATH. On macOS
  with Homebrew available it uses ``brew install herdr``; everywhere else
  it runs the official install script (``curl -fsSL
  https://herdr.dev/install.sh | sh``), which drops the release binary
  onto PATH (typically ``~/.local/bin``).
* Deploys the team ``config.toml`` into ``~/.config/herdr/config.toml``
  with the usual timestamped backup.
"""

from __future__ import annotations

import shutil

from devenv.cli._installer import (
    InstallContext,
    _log,
    deploy_dotfile,
    ensure_command,
    package_file,
    run,
    run_shell,
)
from devenv.cli._platform import is_macos

HERDR_INSTALL_SCRIPT_URL = "https://herdr.dev/install.sh"


def install(ctx: InstallContext) -> None:
    """Install the ``herdr`` binary (if needed) and deploy ``config.toml``."""
    _ensure_herdr_binary(ctx)

    # deploy_dotfile creates the parent directory itself.
    deploy_dotfile(package_file("herdr", "config.toml"), ctx.home / ".config" / "herdr" / "config.toml", ctx)


def _ensure_herdr_binary(ctx: InstallContext) -> None:
    """Install ``herdr`` when it is not already on PATH."""
    found = shutil.which("herdr")
    if found:
        _log(f"herdr already present: {found}")
        return

    if is_macos() and shutil.which("brew"):
        run(["brew", "install", "herdr"], ctx)
        return

    ensure_command("curl")
    run_shell(f"curl -fsSL {HERDR_INSTALL_SCRIPT_URL} | sh", ctx)

    if not ctx.dry_run and not shutil.which("herdr"):
        bin_dir = ctx.home / ".local" / "bin"
        _log(
            f'herdr is not on your PATH yet — add `export PATH="{bin_dir}:$PATH"` to your shell rc.',
            color="yellow",
        )
