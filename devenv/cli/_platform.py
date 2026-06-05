"""OS detection helpers — gate ``devenv install`` to supported OSes."""

from __future__ import annotations

import platform
import sys

_SUPPORTED = ("Linux", "Darwin")


def is_linux() -> bool:
    """Return True when running on Linux."""
    return platform.system() == "Linux"


def is_macos() -> bool:
    """Return True when running on macOS (Darwin)."""
    return platform.system() == "Darwin"


def is_supported() -> bool:
    """Return True when running on a supported OS (Linux or macOS)."""
    return platform.system() in _SUPPORTED


def ensure_supported() -> None:
    """Exit with code 1 when the current OS is unsupported.

    ``devenv install`` targets Linux servers and macOS workstations; other
    platforms (e.g. Windows) are rejected up front so individual installers
    do not have to defend against them.
    """
    if is_supported():
        return
    import click

    click.secho(
        f"[ERROR] devenv install requires Linux or macOS (detected: {platform.system()}).",
        fg="red",
        err=True,
    )
    sys.exit(1)


def ensure_linux() -> None:
    """Backward-compatible alias for :func:`ensure_supported`."""
    ensure_supported()
