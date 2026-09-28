"""Unit tests for the nvm installer."""

from __future__ import annotations

import pytest

from devenv.cli import _nvm
from devenv.cli._installer import InstallContext


def test_dry_run_prints_clone_and_lts_install(dry_ctx: InstallContext, capsys: pytest.CaptureFixture[str]) -> None:
    _nvm.install(dry_ctx)
    out = capsys.readouterr().out
    assert f"git clone --depth 1 --branch {_nvm.NVM_VERSION} {_nvm.NVM_REPO}" in out
    assert "nvm install --lts" in out
    assert not (dry_ctx.home / ".nvm").exists()


def test_install_clones_pinned_tag_then_installs_lts(ctx: InstallContext, monkeypatch: pytest.MonkeyPatch) -> None:
    cmds: list[list[str]] = []
    shells: list[str] = []
    monkeypatch.setattr("devenv.cli._installer.run", lambda cmd, ctx, **k: cmds.append(list(cmd)))
    monkeypatch.setattr(_nvm, "run_shell", lambda command, ctx, **k: shells.append(command))

    _nvm.install(ctx)

    nvm_dir = ctx.home / ".nvm"
    assert cmds == [["git", "clone", "--depth", "1", "--branch", _nvm.NVM_VERSION, _nvm.NVM_REPO, str(nvm_dir)]]
    assert len(shells) == 1
    assert f'NVM_DIR="{nvm_dir}"' in shells[0]
    assert "nvm install --lts" in shells[0]
    assert 'nvm alias default "lts/*"' in shells[0]


def test_second_install_skips_clone_but_reruns_lts(ctx: InstallContext, monkeypatch: pytest.MonkeyPatch) -> None:
    (ctx.home / ".nvm").mkdir()
    cmds: list[list[str]] = []
    shells: list[str] = []
    monkeypatch.setattr("devenv.cli._installer.run", lambda cmd, ctx, **k: cmds.append(list(cmd)))
    monkeypatch.setattr(_nvm, "run_shell", lambda command, ctx, **k: shells.append(command))

    _nvm.install(ctx)

    assert cmds == []
    assert len(shells) == 1
