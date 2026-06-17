<!---
Copyright 2026 The HyperAccel. All rights reserved.
-->

<h3 align="center">
Linux / macOS 개발 환경(Z-Shell · Neovim · Tmux)을 한 줄로 부트스트랩하는 Click 기반 CLI
</h3>

<p align="center">
| <a href="./CONTRIBUTING.md"><b>Contributing</b></a> | <a href="./CLAUDE.md"><b>Agent Guide</b></a> | <a href="https://hyperaccel.ai"><b>Company Information</b></a> |
</p>

---

`linux-devenv`은 HyperAccel Simulator 팀이 새 Linux 서버나 macOS 워크스테이션을 셋업할 때 **팀 공통의 셸·에디터·멀티플렉서 환경을 한 번에 재현**하기 위한 도구입니다. 설치 로직은 모두 **Click 기반 Python CLI (`devenv`)** 로 작성되어 있고, 사용자 dotfile은 패키지에 번들된 정적 자산(`devenv/packages/`)으로 관리됩니다.

## ✨ 주요 특징

- **한 줄 부트스트랩**: `devenv install` 한 번으로 oh-my-zsh + powerlevel10k + Neovim/Vundle/coc.nvim + Tmux/TPM + 표준 플러그인까지 동시 설치 (nvim이 없으면 `~/.local/opt/nvim/`에 공식 stable 릴리스를 자동 설치하고 `~/.local/bin/nvim`을 심볼릭 링크)
- **멱등성 기본**: 모든 단계가 N번 실행해도 안전하도록 헬퍼 레벨에서 가드 (`git_clone_idempotent`, `deploy_dotfile`)
- **비파괴 백업**: 기존 dotfile은 `<file>.bak.<UTC-timestamp>`로 자동 백업, `--force`만 백업 생략
- **Dry-run 지원**: `--dry-run`으로 실제 실행 없이 명령 시퀀스만 확인
- **테스트 격리**: `--home <path>`로 임의 디렉토리를 HOME으로 지정 가능 → CI / 컨테이너 / 단위 테스트에서 안전
- **품질 검증 파이프라인**: pre-commit + ruff + ty + pytest + bashate + markdownlint

## 🗂️ 디렉토리 구조

```text
linux-devenv/
├── devenv/                        # Python 패키지 (핵심)
│   ├── __init__.py                # __version__
│   ├── cli/                       # Click CLI 구현
│   │   ├── __init__.py            # Click group + _TOOL_REGISTRY
│   │   ├── _installer.py          # InstallContext + 공통 헬퍼
│   │   ├── _platform.py           # OS 가드 (Linux / macOS)
│   │   ├── _dir.py                # workspace 디렉토리 생성
│   │   ├── _zsh.py                # zsh + oh-my-zsh + p10k + 플러그인
│   │   ├── _nvim.py               # neovim + Vundle + coc.nvim + 플러그인
│   │   └── _tmux.py               # tmux + TPM + 플러그인
│   └── packages/                  # dotfile 자산 (wheel package-data)
│       ├── zsh/{zshrc,aliases.zsh,devconfig,p10k.zsh}
│       ├── nvim/{init.vim,coc-settings.json}
│       └── tmux/tmux.conf
├── tests/unit_test/               # pytest + CliRunner + fake_home fixture
├── scripts/install_packages.sh    # uv sync + pre-commit install 부트스트랩
├── pyproject.toml                 # devenv 패키지 정의 (`devenv` 엔트리)
├── .pre-commit-config.yaml
├── Makefile                       # install / lint / test / clean (uv 위임)
├── README.md
├── CONTRIBUTING.md
└── CLAUDE.md                      # Claude Code 에이전트 진입점
```

`devenv/cli/`(실행 로직)와 `devenv/packages/`(dotfile 자산)는 역할이 명확히 분리됩니다. 새 도구를 추가할 땐 두 곳을 함께 건드립니다.

## 🚀 시작하기

### 1. 레포지토리 Clone

```bash
git clone https://github.com/Hyper-Accel/linux-devenv.git
cd linux-devenv
```

### 2. 개발자 부트스트랩 (uv 환경 + pre-commit)

```bash
make install                       # Python 3.10 (기본)
make install PYTHON_VERSION=3.12   # 다른 버전 지정
```

내부적으로 `scripts/install_packages.sh`를 호출하며, 직접 실행해도 동일합니다. 이 단계는 **개발자용**이고, 실제 zsh/nvim/tmux 환경은 다음 단계에서 설치합니다.

### 3. `devenv` CLI 설치

```bash
uv pip install -e .          # editable
devenv --help
```

### 4. 실제 환경 설치

```bash
devenv doctor                # 선행 조건(Linux/macOS + zsh/nvim/tmux/git/curl) 점검
devenv install               # 전체 설치 (dir → zsh → nvim → tmux)
```

### 주요 CLI 커맨드

| 커맨드 | 설명 |
|---|---|
| `devenv install` | 전체 도구 설치. `--only zsh,tmux`, `--skip nvim`, `--force`, `--dry-run`, `--yes`, `--home PATH` 지원 |
| `devenv setup` | `$HOME/workspace`, `$HOME/worktrees` 디렉토리만 생성 |
| `devenv list` | 관리되는 도구 + 설치 상태. `--installed`로 설치된 것만 |
| `devenv where` | 번들된 dotfile 자산 경로와 기본 HOME |
| `devenv doctor` | 선행 명령(zsh/nvim/tmux/git/curl) 및 OS 점검 |
| `devenv clean` | `*.bak.<ts>` 백업 파일 정리. `--dry-run` 지원 |

전체 옵션은 `devenv <command> --help`에서 확인할 수 있습니다.

## ✍️ 새로운 도구 추가하기

1. `devenv/cli/_<tool>.py`에 `install(ctx: InstallContext) -> None` 작성 (헬퍼 사용)
2. `devenv/packages/<tool>/`에 dotfile 자산 배치
3. `devenv/cli/__init__.py`의 `_register("<tool>", "<desc>", _<tool>.install)`에 등록
4. `_tool_status()`의 markers 딕셔너리에 한 줄 추가
5. `tests/unit_test/`에 단위 테스트 추가
6. `make lint` + `make test` 통과 확인 → PR 제출

자세한 절차와 컨벤션은 [CONTRIBUTING.md](./CONTRIBUTING.md)를 참고하세요.

## 🧰 Make 타깃

| 타깃 | 설명 |
|---|---|
| `make install` | 개발자 부트스트랩: `uv sync` + `uv pip install -e .` + pre-commit install (`PYTHON_VERSION=3.10\|3.11\|3.12\|3.13`) |
| `make lint` | 모든 파일에 pre-commit 훅 실행 |
| `make test` | `tests/unit_test/` 하위 pytest 실행 (`TEST_WORKERS=N`) |
| `make clean` | 빌드 산출물·캐시 제거 |
| `make help` | 타깃 목록 표시 |

> **주의**: `make install`은 **개발자용 부트스트랩**이고, 실제 zsh/nvim/tmux 설치는 **`devenv install`** 입니다.

## 🛠 기술 스택

- **언어**: Python 3.10+ (CLI), Bash (부트스트랩 1개)
- **CLI 프레임워크**: [Click](https://click.palletsprojects.com/) 8.x
- **패키지 관리**: [uv](https://github.com/astral-sh/uv)
- **품질 검증**: [pre-commit](https://pre-commit.com/), [Ruff](https://docs.astral.sh/ruff/), [ty](https://github.com/astral-sh/ty), [bashate](https://github.com/openstack/bashate), [markdownlint](https://github.com/igorshubovych/markdownlint-cli)
- **테스트**: pytest + Click `CliRunner`

## 📄 라이선스

이 프로젝트는 HyperAccel의 소유입니다. 자세한 라이선스 정보는 프로젝트 루트의 라이선스 파일을 참조하세요.

## 📞 지원

- 이슈 리포트: [GitHub Issues](https://github.com/Hyper-Accel/linux-devenv/issues)
- 이메일: [simulator.team@hyperaccel.ai](mailto:simulator.team@hyperaccel.ai)

---
