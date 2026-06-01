"""OS detection helpers — gate ``devenv install`` to Linux only."""

from __future__ import annotations

import platform
import sys


def is_linux() -> bool:
    """Return True when running on Linux."""
    return platform.system() == "Linux"


def ensure_linux() -> None:
    """Exit with code 1 when not running on Linux.

    Mirrors the ``check_linux`` Make target in the legacy Bash setup.
    """
    if is_linux():
        return
    import click

    click.secho(
        f"[ERROR] devenv install must be run on Linux (detected: {platform.system()}).",
        fg="red",
        err=True,
    )
    sys.exit(1)
