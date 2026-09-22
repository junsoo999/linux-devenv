"""Claude Code installer.

`Claude Code <https://claude.com/claude-code>`_ is Anthropic's agentic
coding CLI. This installer runs the official native installer
(``curl -fsSL https://claude.ai/install.sh | bash``) when ``claude`` is
missing from PATH. The native build has no Node.js dependency and lands
in ``~/.local/bin/claude``; when the binary is already present the step
is skipped, so re-running ``devenv install`` is safe.

User-level settings (``~/.claude/settings.json``) are personal and are
intentionally not managed here.
"""

from __future__ import annotations

import shutil

from devenv.cli._installer import (
    InstallContext,
    _log,
    ensure_command,
    run_shell,
)

CLAUDE_INSTALL_SCRIPT_URL = "https://claude.ai/install.sh"


def install(ctx: InstallContext) -> None:
    """Install the ``claude`` binary when it is not already on PATH."""
    found = shutil.which("claude")
    if found:
        _log(f"claude already present: {found}")
        return

    ensure_command("curl")
    run_shell(f"curl -fsSL {CLAUDE_INSTALL_SCRIPT_URL} | bash", ctx)

    if not ctx.dry_run and not shutil.which("claude"):
        bin_dir = ctx.home / ".local" / "bin"
        _log(
            f'claude is not on your PATH yet — add `export PATH="{bin_dir}:$PATH"` to your shell rc.',
            color="yellow",
        )
