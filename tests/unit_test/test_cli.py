"""CLI-level smoke tests using Click's CliRunner."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from devenv import __version__
from devenv.cli import cli


def test_help_lists_all_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for name in ("install", "setup", "list", "where", "doctor", "clean"):
        assert name in result.output


def test_version_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_where_outputs_packages_and_home() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["where"])
    assert result.exit_code == 0
    assert "source" in result.output
    assert "home" in result.output


def test_setup_creates_workspace_dirs(tmp_path: Path) -> None:
    runner = CliRunner()
    home = tmp_path / "h"
    home.mkdir()
    result = runner.invoke(cli, ["setup", "--home", str(home)])
    assert result.exit_code == 0, result.output
    assert (home / "workspace").is_dir()
    assert (home / "worktrees").is_dir()


def test_list_shows_all_tools_with_status(tmp_path: Path) -> None:
    runner = CliRunner()
    home = tmp_path / "h"
    home.mkdir()
    result = runner.invoke(cli, ["list", "--home", str(home)])
    assert result.exit_code == 0
    for name in ("dir", "zsh", "vim", "tmux"):
        assert name in result.output
    assert "missing" in result.output


def test_install_dry_run_only_dir(tmp_path: Path) -> None:
    runner = CliRunner()
    home = tmp_path / "h"
    home.mkdir()
    result = runner.invoke(
        cli,
        ["install", "--only", "dir", "--dry-run", "--home", str(home)],
    )
    assert result.exit_code == 0, result.output
    assert "[dir]" in result.output
    assert "[dry-run]" in result.output
    # dry-run must not actually create the dirs
    assert not (home / "workspace").exists()


def test_install_only_and_skip_mutually_exclusive(tmp_path: Path) -> None:
    runner = CliRunner()
    home = tmp_path / "h"
    home.mkdir()
    result = runner.invoke(
        cli,
        ["install", "--only", "zsh", "--skip", "vim", "--dry-run", "--home", str(home)],
    )
    assert result.exit_code != 0
    assert "함께 쓸 수 없습니다" in result.output


def test_install_rejects_unknown_tool(tmp_path: Path) -> None:
    runner = CliRunner()
    home = tmp_path / "h"
    home.mkdir()
    result = runner.invoke(
        cli,
        ["install", "--only", "emacs", "--dry-run", "--home", str(home)],
    )
    assert result.exit_code != 0
    assert "알 수 없는 도구" in result.output
