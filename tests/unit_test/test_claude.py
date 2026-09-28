"""Unit tests for the Claude Code installer."""

from __future__ import annotations

import pytest

from devenv.cli import _claude
from devenv.cli._installer import InstallContext


def test_dry_run_prints_install_script(
    dry_ctx: InstallContext, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_claude.shutil, "which", lambda name: "/usr/bin/curl" if name == "curl" else None)
    _claude.install(dry_ctx)
    out = capsys.readouterr().out
    assert _claude.CLAUDE_INSTALL_SCRIPT_URL in out
    assert "[dry-run]" in out


def test_install_skips_when_present(ctx: InstallContext, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_claude.shutil, "which", lambda name: "/usr/local/bin/claude" if name == "claude" else None)
    shells: list[str] = []
    monkeypatch.setattr(_claude, "run_shell", lambda command, ctx, **k: shells.append(command))

    _claude.install(ctx)

    assert shells == []


def test_install_runs_script_when_missing(dry_ctx: InstallContext, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_claude.shutil, "which", lambda name: "/usr/bin/curl" if name == "curl" else None)
    shells: list[str] = []
    monkeypatch.setattr(_claude, "run_shell", lambda command, ctx, **k: shells.append(command))

    _claude.install(dry_ctx)

    assert shells == [f"curl -fsSL {_claude.CLAUDE_INSTALL_SCRIPT_URL} | bash"]
