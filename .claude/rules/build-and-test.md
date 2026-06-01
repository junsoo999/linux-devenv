---
description: Reference when changing the CLI, Makefile, or scripts, or when validating changes locally. Covers uv, devenv subcommands, pytest, pre-commit, and Docker smoke tests.
globs:
  - "Makefile"
  - "pyproject.toml"
  - "scripts/**"
  - "devenv/**"
  - "tests/**"
alwaysApply: false
---

# Build and test guide

`linux-devenv`은 **uv-managed Python 패키지 + Click CLI + dotfile 자산**이다. "빌드"는 `uv pip install -e .`, "테스트"는 pytest + 깨끗한 Linux 컨테이너에서의 `devenv install` 스모크.

## Stack

- **Python**: 3.10+
- **Package manager**: [uv](https://github.com/astral-sh/uv)
- **CLI framework**: Click 8.x
- **Linter / formatter**: Ruff
- **Type checker**: ty (Astral)
- **Tests**: pytest (`tests/unit_test/`, `CliRunner` + `fake_home` fixture)
- **Pre-commit**: ruff, ty, bashate, markdownlint
- **대상 OS**: Linux. macOS는 `ensure_linux()`가 차단.

## uv environment rules (required)

### Do not

- `pip install` → use `uv pip install`.
- `source .venv/bin/activate` → uv가 알아서 한다.
- `python <script>` → `uv run --no-sync python <script>`.
- `pytest ...` → `uv run --no-sync pytest ...`.

### Do

- `uv sync` — `pyproject.toml`에서 의존 동기화.
- `uv pip install -e .` — devenv CLI editable install.
- `uv run --no-sync devenv --help` — CLI 실행.
- `uv run --no-sync pytest tests/unit_test` — 테스트.
- `uv run --no-sync pre-commit run --all-files` — 모든 훅.

## Installation flows

두 가지 install 흐름을 **구분**한다.

### A. 개발자 부트스트랩 (uv + pre-commit)

```bash
make install
# 또는
bash scripts/install_packages.sh --python_ver 3.10
```

옵션: `PYTHON_VERSION=3.10|3.11|3.12|3.13` (기본 3.10).

### B. 실제 환경 설치 (zsh / vim / tmux)

```bash
uv run --no-sync devenv doctor     # 선행 조건 점검
uv run --no-sync devenv install    # 전체 설치
```

또는 wheel/editable로 설치 후:

```bash
uv pip install -e .
devenv install
```

## Make targets

```bash
make help        # 사용 가능한 타겟
make install     # 개발자 부트스트랩 (A 흐름)
make lint        # pre-commit run --all-files
make test        # pytest tests/unit_test
make clean       # 캐시 / 빌드 산출물 제거
```

## devenv CLI 표면

```text
devenv install [--only zsh,tmux] [--skip vim] [--force] [--dry-run] [--yes] [--home PATH]
devenv setup [--home PATH]
devenv list [--installed] [--home PATH]
devenv where
devenv doctor
devenv clean [--dry-run] [--home PATH]
```

- `--home PATH` — 테스트 / 격리 환경용. 기본은 `Path.home()`.
- `--dry-run` — 어떤 명령이 실행될지만 출력 (서브프로세스 / FS 변경 없음). 새 기능 추가 시 반드시 dry-run에서도 동작하도록 헬퍼 사용.
- exit code: `0` 성공, `1` 사용자 / 환경 문제 (Linux 아님, 명령 누락, 옵션 충돌), `2` 시스템 / 설치 실패.

## 검증 / 스모크 테스트

### 1. 단위 테스트

```bash
uv run --no-sync pytest tests/unit_test
uv run --no-sync pytest tests/unit_test/test_cli.py -k dry_run
```

테스트는 **항상 `fake_home` fixture를 사용**해 실제 사용자 HOME을 건드리지 않는다.

### 2. 깨끗한 컨테이너에서 통합 검증 (권장)

```bash
docker run --rm -it -v "$PWD":/work -w /work ubuntu:22.04 bash -lc '
  apt-get update && apt-get install -y sudo git curl make zsh vim tmux python3 python3-venv &&
  curl -LsSf https://astral.sh/uv/install.sh | sh &&
  export PATH="$HOME/.local/bin:$PATH" &&
  make install &&
  uv run --no-sync devenv install --yes
'
```

위가 에러 없이 끝나야 한다.

### 3. 멱등성 검증

```bash
uv run --no-sync devenv install --yes
uv run --no-sync devenv install --yes   # 두 번째도 깨지지 않아야
```

깨지면 `_installer.py`의 헬퍼 가드를 보강하라 — `coding-conventions.md`의 idempotency 섹션 참조.

### 4. 빠른 dry-run

```bash
uv run --no-sync devenv install --only zsh --dry-run --home /tmp/devenv-test
```

stdout에 `[dry-run] $ git clone ...` 같은 라인이 찍히고, `/tmp/devenv-test/`는 그대로여야 한다.

## Lint

```bash
uv run --no-sync ruff format .
uv run --no-sync ruff check . --fix
uv run --no-sync ty check devenv
uv run --no-sync pre-commit run --all-files
```

`devenv/packages/`는 ruff exclude (dotfile은 zsh/vim 문법이라 Python lint 대상이 아님).

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `devenv install`이 "must be run on Linux" | macOS/WSL. Linux 컨테이너 또는 Linux 서버에서 실행. |
| `uv: command not found` | `curl -LsSf https://astral.sh/uv/install.sh \| sh`. |
| `command -v zsh` 실패 | OS 패키지 매니저로 zsh/vim/tmux 미리 설치. `devenv doctor`로 점검. |
| 두 번째 `devenv install`에서 git clone 실패 | 멱등성 가드가 깨진 케이스. `git_clone_idempotent` 직접 호출 없이 helper 사용 확인. |
| 사용자 dotfile 손실 | `deploy_dotfile`이 timestamp 백업을 자동 생성한다. `~/.zshrc.bak.<ts>` 확인. |
| `ty check` 실패 | `unresolved-import`, `unused-ignore-comment`는 의도적으로 ignore. 다른 항목은 실제 타입 문제. |
| pytest가 실제 HOME을 건드림 | 새 테스트가 `fake_home` fixture를 안 쓴 것. conftest의 `ctx`/`dry_ctx`를 사용. |
