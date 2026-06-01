---
description: Reference when you need the repo's overall purpose and structure. Read this first before adding subcommands, dotfiles, or refactoring.
alwaysApply: false
---

# Project context

## Overview

`linux-devenv`은 HyperAccel Simulator 팀의 **Linux 서버용 개발 환경 부트스트랩** 레포지토리다. 두 가지 역할을 한다.

1. **Click 기반 Python CLI (`devenv`)** — `uv run devenv install`이 zsh / nvim / tmux 및 관련 플러그인을 idempotent하게 설치한다.
2. **Dotfile 자산 (Plain text, package-data)** — `devenv/packages/<tool>/`에 들어 있는 설정 파일을 사용자의 홈 디렉토리(`~/.zshrc`, `~/.tmux.conf` 등)로 배치한다.

목표는 새 서버에서 `git clone && make install && uv run devenv install` 세 단계로 팀 공통 셸/에디터/멀티플렉서 환경을 재현하는 것.

## Dual role of `devenv/cli/` vs `devenv/packages/`

```text
devenv/
├── __init__.py                 # __version__
├── cli/                        # 실행 로직 (Python + Click)
│   ├── __init__.py             # Click group + subcommand 등록 (_TOOL_REGISTRY)
│   ├── _installer.py           # 공통 helper (ensure_dir, git_clone_idempotent, deploy_dotfile, run)
│   ├── _platform.py            # Linux 가드
│   ├── _dir.py                 # $HOME/workspace, $HOME/worktrees 생성
│   ├── _zsh.py                 # zsh + oh-my-zsh + p10k + 플러그인 + dotfile
│   ├── _nvim.py                # nvim + Vundle + coc.nvim + 플러그인 + init.vim
│   └── _tmux.py                # tmux + TPM + tmux.conf
└── packages/                   # 정적 설정 자산 (wheel package-data)
    ├── zsh/
    │   ├── zshrc               # → ~/.zshrc
    │   ├── aliases.zsh         # → ~/.oh-my-zsh/custom/aliases.zsh
    │   ├── devconfig           # → ~/.devconfig
    │   └── p10k.zsh            # → ~/.p10k.zsh
    ├── nvim/
    │   ├── init.vim            # → ~/.config/nvim/init.vim
    │   └── coc-settings.json   # → ~/.config/nvim/coc-settings.json
    └── tmux/tmux.conf          # → ~/.tmux.conf
```

### Core rules

- `devenv/cli/*.py`는 **Click 진입점 + Python 설치 로직**. 로직 변경은 여기서.
- `devenv/packages/<tool>/`은 **사용자 홈으로 그대로 들어가는 dotfile**. 실행 로직을 넣지 마라.
- 새 도구를 추가하려면 (1) `devenv/cli/_<tool>.py` 작성, (2) `devenv/packages/<tool>/`에 dotfile, (3) `devenv/cli/__init__.py`의 `_register(...)`에 한 줄 추가.
- 설치 로직은 **idempotent**해야 한다 — `_installer.py`의 `git_clone_idempotent`, `deploy_dotfile`(자동 백업), `ensure_dir`을 사용하라.
- dotfile 자산 접근은 **반드시 `_installer.package_file("zsh", "zshrc")`**를 통한다. `Path(__file__).parent / ...` 직접 조립은 wheel install 시 깨진다.

## CLI entry point

`pyproject.toml`이 엔트리포인트를 등록한다.

```toml
[project.scripts]
devenv = "devenv.cli:cli"
```

`uv pip install -e .` 후 `devenv` 실행 가능. subcommand:

- `devenv install [--only|--skip ...] [--force] [--dry-run] [--yes] [--home PATH]` — 도구 설치
- `devenv setup [--home PATH]` — workspace 디렉토리만
- `devenv list [--installed]` — 도구 목록 + 설치 상태
- `devenv where` — package-data 경로, 기본 HOME
- `devenv doctor` — 선행 조건 점검 (Linux 여부, zsh/nvim/tmux/git/curl)
- `devenv clean [--dry-run]` — 백업 파일 정리

## Makefile은 개발자 부트스트랩 전용

`make install`은 **uv sync + pre-commit install + `uv pip install -e .`** 만 수행한다. 실제 환경 설치는 **`devenv install`**. 이 분리를 README/CLAUDE에서도 일관되게 유지하라.

```text
make install   → 개발자 부트스트랩 (uv 환경)
devenv install → 실제 zsh/vim/tmux 환경 설치
```

## Repository layout

```text
linux-devenv/
├── pyproject.toml              # devenv 패키지 + 의존 + ruff/ty/pytest 설정
├── uv.lock
├── Makefile                    # 슬림 — uv/pytest/pre-commit 위임만
├── README.md                   # 사용자(휴먼)용 문서
├── CLAUDE.md                   # Claude Code 마스터 진입점
├── .gitmessage.txt
├── .gitignore
├── .pre-commit-config.yaml
├── .markdownlint.yaml
├── scripts/
│   └── install_packages.sh     # uv sync + pre-commit install 부트스트랩
├── .claude/
│   └── rules/                  # 이 디렉토리 — 에이전트 룰
├── devenv/                     # Python 패키지
│   ├── cli/                    # Click 진입점 + installer 모듈들
│   └── packages/               # dotfile 자산 (package-data)
└── tests/
    └── unit_test/              # pytest + CliRunner + fake_home fixture
```

## Typical user scenarios

1. **새 서버를 받았다** — `make install && uv run devenv install`로 한 번에 셋업.
2. **기존 dotfile을 수정한다** — `devenv/packages/<tool>/`의 파일만 수정 → `devenv install --force`로 적용 (또는 백업 후 자동 교체).
3. **새 zsh 플러그인을 추가한다** — `devenv/cli/_zsh.py`의 `_ZSH_PLUGINS` 리스트에 `(url, name)` 한 줄 + `packages/zsh/zshrc`에 `plugins=(... new_plugin)` 등록.
4. **새 도구(예: `direnv`)를 추가한다** — `devenv/cli/_direnv.py` 작성 + `devenv/packages/direnv/` 추가 + `_TOOL_REGISTRY`에 등록 + `_tool_status()`의 markers에 라인 추가 + 테스트 추가.

세 시나리오 모두 `coding-conventions.md`, `contribution-guide.md`를 함께 참조하라.
