"""Shared fixtures for unit tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from devenv.cli._installer import InstallContext


@pytest.fixture
def fake_home(tmp_path: Path) -> Path:
    """A throwaway HOME directory rooted under pytest's tmp_path."""
    home = tmp_path / "home"
    home.mkdir()
    return home


@pytest.fixture
def ctx(fake_home: Path) -> InstallContext:
    """Default InstallContext with a fake HOME and no dry-run."""
    return InstallContext(home=fake_home, force=False, dry_run=False, assume_yes=True)


@pytest.fixture
def dry_ctx(fake_home: Path) -> InstallContext:
    """InstallContext in dry-run mode (no subprocess / filesystem mutations)."""
    return InstallContext(home=fake_home, force=False, dry_run=True, assume_yes=True)
