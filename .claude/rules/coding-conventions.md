---
description: Reference when writing or editing Python (devenv/) or dotfiles (devenv/packages/). Covers Python style, Click conventions, idempotency rules, and dotfile conventions.
globs:
  - "devenv/**/*.py"
  - "devenv/packages/**"
  - "tests/**/*.py"
  - "scripts/**/*.sh"
  - "Makefile"
alwaysApply: false
---

# Coding conventions

`devenv/**/*.py` (Click CLI + installer 로직), `devenv/packages/**` (정적 dotfile), `scripts/*.sh` (uv 부트스트랩), `tests/**` 작성 규칙.

## Python style

### General

- **PEP 8** + 프로젝트 오버라이드.
- **Google-style docstrings** 필수.
- **Ruff**가 포맷 + 린트 (Black/isort/flake8 대체). pre-commit이 권장 호출 경로.
- **ty** (Astral)로 타입 체크. `unresolved-import`, `unused-ignore-comment`는 의도적 ignore.
- Python **3.10+**.
- 모든 public 함수 / 클래스에 **type hints**.
- **uv only** — `pip install`, `python` 직접, `source .venv/bin/activate` 금지.

### Line length, indentation, quotes

- 최대 줄 길이: **119**
- 들여쓰기: **4 spaces** (탭 금지)
- 문자열 인용부호: **double quotes**

### Naming

- 함수 / 변수: `snake_case` (`install_tool()`, `target_home`)
- 클래스: `CapWords` (`InstallContext`, `CommandMissingError`)
- 모듈: `snake_case` (`_installer`, `_platform`); 내부 모듈은 leading `_`
- 상수: `UPPER_SNAKE_CASE` (`POWERLEVEL10K_REPO`, `_ZSH_PLUGINS`)
- private: leading underscore (`_zsh_custom`, `_deploy_dotfiles`)

### Docstrings

- 큰따옴표 3개.
- 첫 줄: 짧은 명령형 요약, 마침표로 종료 (Ruff D415).
- 비자명한 함수 / 클래스: Args / Returns / Raises 섹션.
- Google 스타일; 타입은 type hint에 두고 docstring에는 반복 금지.

```python
def deploy_dotfile(src: Path, dest: Path, ctx: InstallContext) -> None:
    """Copy ``src`` to ``dest``, backing up any existing file first.

    Args:
        src: Bundled dotfile under ``devenv/packages/<tool>/``.
        dest: Final destination under ``ctx.home``.
        ctx: InstallContext (controls dry-run / force / backup).
    """
```

### Imports

- isort: stdlib → third-party → local, 공백줄로 구분.
- `from __future__ import annotations`를 모든 새 모듈 상단에.
- 미사용 import는 `__init__.py`에서만 허용 (per-file-ignore F401).

### `print` 금지

- Ruff `T20`이 `print()`를 차단. CLI 출력은 `click.echo()` / `click.secho()`.

## Click / CLI conventions (`devenv/cli/`)

- 모든 subcommand는 `@cli.command()`로 등록. 새 도구 추가 시 `_TOOL_REGISTRY`에 `_register("<name>", "<desc>", <install_fn>)`도 함께.
- CLI는 **얇게** 유지 — 로직은 `_installer.py` 또는 `_<tool>.py`로. CLI 함수는 인자 파싱 + 컨텍스트 구성 + 헬퍼 호출만.
- **`--help` 텍스트는 한국어 (팀 UX)**, 단 함수/모듈/클래스 docstring은 영어. Click이 docstring을 자동으로 help로 쓰지 않도록 `@cli.command(help="...")` kwarg를 명시.
- 타입 있는 예외(`InstallError`, `CommandMissingError`)를 헬퍼/로직 모듈에 정의하고, CLI boundary에서 `click.secho(..., err=True)` + `sys.exit(<code>)`로 변환.
- 모든 long option에 가능하면 short alias: `-f/--force`, `-y/--yes`.
- Exit code: `0` 성공, `1` 사용자 / 환경 문제, `2` 시스템 / 설치 실패.
- 사용자 메시지는 **한국어** (사내 도구), 코드 / docstring / 주석 / 예외 메시지는 **영어**.

## Idempotency (필수)

설치 로직은 **N번 실행해도 동일한 결과 + 비파괴**. `_installer.py`의 헬퍼를 직접 작성한 로직보다 우선 사용.

### 패턴

```python
ensure_command("zsh")                                 # 누락 시 CommandMissingError
ensure_dir(ctx.home / ".vim", ctx)                    # mkdir -p
git_clone_idempotent(repo, dest, ctx, depth=1)        # 이미 있으면 skip
deploy_dotfile(package_file("zsh", "zshrc"),          # 자동 timestamp 백업
               ctx.home / ".zshrc", ctx)
```

### 금지

- `shutil.rmtree(ctx.home / ".oh-my-zsh")` 같이 사용자 디렉토리를 무조건 비우는 코드 — `--force`에서도 헬퍼를 통해.
- `Path("~/.zshrc")` 같이 사용자 HOME을 하드코딩 — 항상 `ctx.home`을 통해 (테스트 가능성 + `--home` 옵션).
- `subprocess.run`을 직접 호출 — `_installer.run()` 또는 `run_shell()`을 사용 (dry-run, 로깅, 에러 변환을 무료로 얻음).
- `Path(__file__).parent / "packages"` — wheel install 시 깨진다. `package_file(...)` 사용.

## Dotfile conventions (`devenv/packages/**`)

- 평문 텍스트. 실행 권한(`+x`) 부여 금지.
- 사용자 머신에 그대로 들어가므로 **사내 비밀 / 개인 경로 / 토큰** 절대 금지.
- 개인 환경변수는 `packages/zsh/devconfig` (`~/.devconfig`)에 두고, 진짜 비밀은 사용자 로컬에서 추가하도록 README에 안내.
- 외부 플러그인 매니저(Vundle, TPM, oh-my-zsh)가 자동 설치하는 항목은 dotfile에 플러그인 이름만, 실제 fetch는 `_<tool>.py` installer가 담당.
- 새 dotfile 추가 시 `pyproject.toml`의 `[tool.setuptools.package-data]`에 포함되는지 확인 (현재는 `packages/<tool>/*` 와일드카드라 자동 포함).

## Shell scripting (`scripts/*.sh`)

`scripts/`에는 이제 **부트스트랩용 `install_packages.sh` 한 개**만 남는다.

- Shebang: `#!/bin/bash`.
- `set -e`로 시작.
- 들여쓰기 4 spaces.
- 변수 확장은 항상 큰따옴표 — `"$HOME"`, `"${PYTHON_VERSION}"`.
- 새 설치 로직은 **Bash로 추가하지 마라** — Python `devenv/cli/_<tool>.py`에 추가.
- bashate가 pre-commit에서 lint.

## Makefile conventions

- 모든 타겟은 `.PHONY:` 등록.
- Makefile은 **얇은 위임자**: uv / pytest / pre-commit / 부트스트랩 스크립트 호출만. 설치 로직을 Makefile에 다시 넣지 마라 (그건 `devenv` CLI의 일).

## Tests (`tests/unit_test/`)

- 항상 `fake_home` / `ctx` / `dry_ctx` fixture 사용 — 실제 `$HOME`을 절대 건드리지 마라.
- 외부 네트워크(`git clone`, `curl`) 의존 테스트는 `--dry-run` 또는 monkeypatch로 우회.
- pydocstyle은 tests에서 면제 (per-file-ignore `D`).
- CLI 동작 검증은 `click.testing.CliRunner`.
- 새 헬퍼 / subcommand 추가 시 단위 테스트도 함께.

## 한국어 / 영어

- **코드 식별자, 주석, 파일명, docstring, 커밋 메시지, PR 제목**: 영어.
- **CLI 사용자 메시지 / `--help`**: 한국어 (팀 UX).
- **Claude ↔ 사용자 채팅**: 한국어.
