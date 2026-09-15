"""Unit tests for the herdr installer."""

from __future__ import annotations

from pathlib import Path

import pytest

from devenv.cli import _herdr
from devenv.cli._installer import InstallContext


def test_dry_run_deploys_config_without_touching_fs(
    dry_ctx: InstallContext, capsys: pytest.CaptureFixture[str]
) -> None:
    _herdr.install(dry_ctx)
    out = capsys.readouterr().out
    assert "config.toml" in out
    assert not (dry_ctx.home / ".config" / "herdr").exists()


def test_install_skips_binary_when_present(ctx: InstallContext, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_herdr.shutil, "which", lambda name: "/usr/local/bin/herdr" if name == "herdr" else None)
    called: list[object] = []
    monkeypatch.setattr(_herdr, "run", lambda *a, **k: called.append(a))
    monkeypatch.setattr(_herdr, "run_shell", lambda *a, **k: called.append(a))

    _herdr.install(ctx)

    assert called == []
    dest = ctx.home / ".config" / "herdr" / "config.toml"
    assert dest.is_file()
    assert "[terminal]" in dest.read_text()


def test_install_uses_brew_on_macos(dry_ctx: InstallContext, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_herdr, "is_macos", lambda: True)
    monkeypatch.setattr(_herdr.shutil, "which", lambda name: "/opt/homebrew/bin/brew" if name == "brew" else None)
    cmds: list[list[str]] = []
    monkeypatch.setattr(_herdr, "run", lambda cmd, ctx, **k: cmds.append(list(cmd)))

    _herdr.install(dry_ctx)

    assert cmds == [["brew", "install", "herdr"]]


def test_install_uses_script_on_linux(dry_ctx: InstallContext, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_herdr, "is_macos", lambda: False)
    monkeypatch.setattr(_herdr.shutil, "which", lambda name: "/usr/bin/curl" if name == "curl" else None)
    shells: list[str] = []
    monkeypatch.setattr(_herdr, "run_shell", lambda command, ctx, **k: shells.append(command))

    _herdr.install(dry_ctx)

    assert shells == [f"curl -fsSL {_herdr.HERDR_INSTALL_SCRIPT_URL} | sh"]


def test_second_install_backs_up_existing_config(ctx: InstallContext, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_herdr.shutil, "which", lambda name: "/usr/local/bin/herdr")
    _herdr.install(ctx)
    _herdr.install(ctx)
    cfg_dir: Path = ctx.home / ".config" / "herdr"
    assert (cfg_dir / "config.toml").is_file()
    assert list(cfg_dir.glob("config.toml.bak.*"))
