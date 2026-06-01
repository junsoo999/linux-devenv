"""Workspace directory bootstrap — mirrors the legacy ``install_dir.sh``."""

from __future__ import annotations

from devenv.cli._installer import InstallContext, ensure_dir


def install(ctx: InstallContext) -> None:
    """Create ``$HOME/workspace`` and ``$HOME/worktrees``."""
    ensure_dir(ctx.home / "workspace", ctx)
    ensure_dir(ctx.home / "worktrees", ctx)
