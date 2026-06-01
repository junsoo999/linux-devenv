"""Unit tests for devenv.cli._installer helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from devenv.cli._installer import (
    CommandMissingError,
    InstallContext,
    deploy_dotfile,
    ensure_command,
    ensure_dir,
    git_clone_idempotent,
    package_file,
    packages_root,
)


def test_packages_root_resolves_to_existing_dir() -> None:
    root = packages_root()
    assert root.is_dir()
    assert (root / "zsh" / "zshrc").is_file()
    assert (root / "vim" / "vimrc").is_file()
    assert (root / "tmux" / "tmux.conf").is_file()


def test_package_file_returns_existing_asset() -> None:
    assert package_file("zsh", "zshrc").is_file()


def test_ensure_command_returns_path_for_existing_command() -> None:
    assert ensure_command("sh").endswith("sh")


def test_ensure_command_raises_for_missing() -> None:
    with pytest.raises(CommandMissingError):
        ensure_command("definitely-not-a-real-command-xyz")


def test_ensure_dir_idempotent(ctx: InstallContext) -> None:
    target = ctx.home / "a" / "b" / "c"
    ensure_dir(target, ctx)
    ensure_dir(target, ctx)
    assert target.is_dir()


def test_deploy_dotfile_creates_and_backs_up(ctx: InstallContext, tmp_path: Path) -> None:
    src = tmp_path / "src.txt"
    src.write_text("new\n")
    dest = ctx.home / ".rc"

    deploy_dotfile(src, dest, ctx)
    assert dest.read_text() == "new\n"

    src.write_text("newer\n")
    deploy_dotfile(src, dest, ctx)
    backups = list(ctx.home.glob(".rc.bak.*"))
    assert len(backups) == 1
    assert backups[0].read_text() == "new\n"
    assert dest.read_text() == "newer\n"


def test_deploy_dotfile_force_skips_backup(ctx: InstallContext, tmp_path: Path) -> None:
    src = tmp_path / "src.txt"
    src.write_text("v1\n")
    dest = ctx.home / ".rc"
    deploy_dotfile(src, dest, ctx)

    ctx_force = InstallContext(home=ctx.home, force=True, dry_run=False, assume_yes=True)
    src.write_text("v2\n")
    deploy_dotfile(src, dest, ctx_force)

    assert dest.read_text() == "v2\n"
    assert not list(ctx.home.glob(".rc.bak.*"))


def test_git_clone_idempotent_skips_when_exists(ctx: InstallContext) -> None:
    dest = ctx.home / "already" / "there"
    dest.mkdir(parents=True)
    cloned = git_clone_idempotent("https://example.invalid/repo.git", dest, ctx)
    assert cloned is False


def test_dry_run_does_not_touch_filesystem(dry_ctx: InstallContext, tmp_path: Path) -> None:
    target = dry_ctx.home / "should-not-exist"
    ensure_dir(target, dry_ctx)
    assert not target.exists()

    src = tmp_path / "src.txt"
    src.write_text("x")
    dest = dry_ctx.home / ".rc"
    deploy_dotfile(src, dest, dry_ctx)
    assert not dest.exists()
