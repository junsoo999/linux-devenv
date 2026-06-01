"""Click-based command-line interface for ``linux-devenv``.

Provides ``devenv`` subcommands that bootstrap a Linux server dev
environment (workspace directory, oh-my-zsh + powerlevel10k + zsh
plugins, nvim + Vundle + coc.nvim, tmux + TPM plugins) and lay out the
managed dotfiles into the user's home directory.

Each tool installer is idempotent; running ``devenv install`` more than
once is safe. Existing dotfiles are backed up to ``<file>.bak.<ts>``
before they are replaced unless ``--force`` is passed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from devenv import __version__
from devenv.cli import _dir, _nvim, _tmux, _zsh
from devenv.cli._installer import (
    CommandMissingError,
    InstallContext,
    InstallError,
    packages_root,
)
from devenv.cli._platform import ensure_linux, is_linux

# Order matters: workspace dir → shell → editor → multiplexer.
_TOOL_REGISTRY: dict[str, "_ToolEntry"] = {}


class _ToolEntry:
    """Static metadata about an installable tool."""

    def __init__(self, name: str, description: str, install_fn) -> None:
        self.name = name
        self.description = description
        self.install_fn = install_fn


def _register(name: str, description: str, install_fn) -> None:
    _TOOL_REGISTRY[name] = _ToolEntry(name, description, install_fn)


_register("dir", "$HOME/workspace, $HOME/worktrees 디렉토리 생성", _dir.install)
_register("zsh", "Z-Shell + oh-my-zsh + powerlevel10k + 플러그인 + dotfile", _zsh.install)
_register("nvim", "Neovim + Vundle + coc.nvim + 플러그인 + init.vim", _nvim.install)
_register("tmux", "Tmux + TPM + 플러그인 + tmux.conf", _tmux.install)


_HOME_OPTION = click.option(
    "--home",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="설치 대상 HOME 디렉토리 (기본: 현재 사용자의 $HOME). 테스트 / 격리 환경용.",
)


def _resolve_home(home: Path | None) -> Path:
    """Resolve ``--home`` at command-execution time."""
    return home if home is not None else Path.home()


def _parse_csv(value: str | None) -> list[str]:
    """Split a comma-separated option value into a clean list."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _select_tools(only: str | None, skip: str | None) -> list[_ToolEntry]:
    """Resolve --only / --skip into an ordered tool list."""
    only_names = _parse_csv(only)
    skip_names = _parse_csv(skip)
    unknown = [n for n in (*only_names, *skip_names) if n not in _TOOL_REGISTRY]
    if unknown:
        raise click.BadParameter(f"알 수 없는 도구: {', '.join(unknown)}")
    if only_names and skip_names:
        raise click.BadParameter("`--only`와 `--skip`은 함께 쓸 수 없습니다.")
    if only_names:
        return [_TOOL_REGISTRY[n] for n in only_names]
    selected = [t for n, t in _TOOL_REGISTRY.items() if n not in skip_names]
    return selected


@click.group(help="Linux 서버용 개발 환경(Z-Shell, Neovim, Tmux) 자동 설치 도구.")
@click.version_option(__version__, prog_name="devenv")
def cli() -> None:
    """Top-level command group: install / setup / list / where / doctor / clean."""


@cli.command(help="전체 또는 선택한 도구를 설치합니다.")
@click.option("--only", type=str, default=None, help="설치할 도구만 콤마로 지정 (예: zsh,tmux).")
@click.option("--skip", type=str, default=None, help="제외할 도구를 콤마로 지정.")
@click.option("--force", "-f", is_flag=True, help="기존 dotfile을 백업 없이 덮어씁니다.")
@click.option("--dry-run", is_flag=True, help="실제 실행 없이 수행할 명령만 출력합니다.")
@click.option("--yes", "-y", "assume_yes", is_flag=True, help="대화형 프롬프트를 자동 승인합니다.")
@_HOME_OPTION
def install(
    only: str | None,
    skip: str | None,
    force: bool,
    dry_run: bool,
    assume_yes: bool,
    home: Path | None,
) -> None:
    """Install one or more managed tools into the target HOME."""
    if not dry_run:
        ensure_linux()
    tools = _select_tools(only, skip)
    ctx = InstallContext(
        home=_resolve_home(home),
        force=force,
        dry_run=dry_run,
        assume_yes=assume_yes,
    )
    click.secho(f"==> target HOME : {ctx.home}", fg="cyan")
    if ctx.dry_run:
        click.secho("==> dry-run 모드: 실제 변경은 일어나지 않습니다.", fg="yellow")

    for tool in tools:
        click.secho(f"==> [{tool.name}] {tool.description}", fg="cyan", bold=True)
        try:
            tool.install_fn(ctx)
        except CommandMissingError as exc:
            click.secho(f"  ! 선행 명령 누락: {exc}", fg="red", err=True)
            sys.exit(1)
        except InstallError as exc:
            click.secho(f"  ! 설치 실패 ({tool.name}): {exc}", fg="red", err=True)
            sys.exit(2)
        click.secho(f"  ✓ {tool.name} 완료", fg="green")


@cli.command(help="$HOME/workspace, $HOME/worktrees 디렉토리만 생성합니다.")
@click.option("--dry-run", is_flag=True, help="실행 없이 명령만 출력.")
@_HOME_OPTION
def setup(dry_run: bool, home: Path | None) -> None:
    """Create the baseline workspace directories under HOME."""
    ctx = InstallContext(
        home=_resolve_home(home),
        force=False,
        dry_run=dry_run,
        assume_yes=False,
    )
    _dir.install(ctx)
    click.secho(f"  ✓ workspace ready at {ctx.home}", fg="green")


@cli.command(name="list", help="설치 가능한 도구와 현재 설치 상태를 표시합니다.")
@click.option("--installed", is_flag=True, help="시스템에 실제 설치된 도구만 표시.")
@_HOME_OPTION
def list_cmd(installed: bool, home: Path | None) -> None:
    """List managed tools and (optionally) their installation state."""
    target_home = _resolve_home(home)
    name_width = max(len(name) for name in _TOOL_REGISTRY)
    for tool in _TOOL_REGISTRY.values():
        status = _tool_status(tool.name, target_home)
        if installed and status != "installed":
            continue
        click.echo(f"  {tool.name.ljust(name_width)}  [{status}]  {tool.description}")


def _tool_status(name: str, home: Path) -> str:
    """Best-effort detection of whether a tool's dotfiles are present."""
    markers = {
        "dir": home / "workspace",
        "zsh": home / ".zshrc",
        "nvim": home / ".config" / "nvim" / "init.vim",
        "tmux": home / ".tmux.conf",
    }
    marker = markers.get(name)
    if marker is None:
        return "unknown"
    return "installed" if marker.exists() else "missing"


@cli.command(help="관리되는 dotfile 자산 경로와 기본 HOME을 출력합니다.")
def where() -> None:
    """Print the source dotfile package directory and the default HOME."""
    click.echo(f"source  : {packages_root()}")
    click.echo(f"home    : {Path.home()}")
    click.echo("tools   : " + ", ".join(_TOOL_REGISTRY))


@cli.command(help="선행 조건(zsh / nvim / tmux / git / curl / Linux 여부)을 점검합니다.")
def doctor() -> None:
    """Probe the host for required commands and OS."""
    ok = True
    if is_linux():
        click.secho("  ✓ Linux", fg="green")
    else:
        click.secho("  ✗ non-Linux: `devenv install` is blocked", fg="red")
        ok = False

    import shutil

    for cmd in ("zsh", "nvim", "tmux", "git", "curl"):
        path = shutil.which(cmd)
        if path:
            click.secho(f"  ✓ {cmd:<5} → {path}", fg="green")
        else:
            click.secho(f"  ✗ {cmd:<5} 누락", fg="red")
            ok = False
    sys.exit(0 if ok else 1)


@cli.command(help="devenv가 만든 백업 파일(*.bak.<ts>)을 정리합니다.")
@click.option("--dry-run", is_flag=True, help="삭제 대상만 표시.")
@_HOME_OPTION
def clean(dry_run: bool, home: Path | None) -> None:
    """Remove timestamped backup files created by previous installs."""
    target_home = _resolve_home(home)
    candidates = list(target_home.glob(".*.bak.*"))
    candidates += list((target_home / ".oh-my-zsh" / "custom").glob("*.bak.*"))
    if not candidates:
        click.echo("정리할 백업 파일이 없습니다.")
        return
    for path in candidates:
        if dry_run:
            click.echo(f"  [dry-run] would remove {path}")
            continue
        path.unlink()
        click.echo(f"  removed {path}")
