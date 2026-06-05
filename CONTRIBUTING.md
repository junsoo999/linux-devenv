# Contributing to linux-devenv

`linux-devenv` 레포지토리에 기여해 주셔서 감사합니다! 이 문서는 팀원이 설치 로직과 dotfile을 안전하고 일관되게 추가·개선할 수 있도록 작성되었습니다. 기여를 시작하기 전에 아래 지침을 반드시 확인해 주세요.

---

## 🛠 권장 환경

기여 시 아래 환경을 기준으로 작업해 주세요.

- **언어**: Python 3.10+ (CLI 본체), Bash (부트스트랩 스크립트 한정)
- **CLI 프레임워크**: [Click](https://click.palletsprojects.com/) 8.x
- **패키지 관리**: [uv](https://github.com/astral-sh/uv)
- **품질 검증**: pre-commit, ruff, ty, bashate, markdownlint
- **대상 OS**: Linux 서버 + macOS 워크스테이션 (그 외는 `ensure_supported()`가 차단)

초기 셋업:

```bash
make install
# 또는
bash scripts/install_packages.sh --python_ver 3.10
```

위 명령이 `uv sync` + `uv pip install -e .` + `pre-commit install`까지 한 번에 처리합니다.

---

## 📁 디렉토리 규칙

설치 로직과 dotfile 자산은 **명확히 분리**해 관리합니다.

```text
devenv/
├── cli/                    # 실행 로직 (Python + Click)
│   ├── __init__.py         # Click group, _TOOL_REGISTRY 등록
│   ├── _installer.py       # 공통 헬퍼 (직접 작성한 로직보다 우선 사용)
│   ├── _platform.py        # OS 가드 (Linux / macOS)
│   └── _<tool>.py          # 도구별 installer (install(ctx) 진입점)
└── packages/               # 정적 dotfile 자산 (wheel package-data)
    └── <tool>/             # → ~/.<dotfile> 또는 ~/.<tool>/... 로 배치
```

### 모듈 명명 규칙

- 도구별 installer 모듈은 **`_<tool>.py`** (leading underscore). 외부에 노출하지 않음.
- 도구 이름은 **lowercase, 영숫자만** (`zsh`, `vim`, `tmux`, `direnv`). dotfile 디렉토리 이름과 일치해야 함.
- 모듈은 `install(ctx: InstallContext) -> None` 함수를 export — `_TOOL_REGISTRY`가 이 시그니처를 기대합니다.

### Installer 작성 규칙

```python
"""<Tool> installer."""

from __future__ import annotations

from devenv.cli._installer import (
    InstallContext,
    deploy_dotfile,
    ensure_command,
    ensure_dir,
    git_clone_idempotent,
    package_file,
    run,
)


def install(ctx: InstallContext) -> None:
    """Install <tool> stack into ``ctx.home``."""
    ensure_command("<tool>")
    ensure_command("git")
    # 1) 디렉토리 보장
    # 2) 외부 자원(git clone) idempotent 호출
    # 3) deploy_dotfile로 dotfile 배치 (자동 백업)
```

- **반드시 헬퍼를 사용**: `subprocess.run`, `shutil.copy`, `Path.mkdir`를 직접 부르지 마세요. dry-run / 로깅 / 백업이 깨집니다.
- **`ctx.home`을 통해서만** HOME에 접근하세요. `Path.home()`이나 `os.environ["HOME"]` 하드코딩은 `--home` 옵션과 테스트를 깨뜨립니다.
- **dotfile 자산 접근은 `package_file(...)`**. `Path(__file__).parent / "packages"`는 wheel install 시 깨집니다.

### dotfile 작성 규칙

- 평문 텍스트. 실행 권한(`+x`) 부여 금지.
- **사내 비밀 / 토큰 / 개인 경로 절대 금지** — 사용자 머신에 그대로 들어갑니다.
- 개인 환경변수는 `devenv/packages/zsh/devconfig`(`~/.devconfig`)에 두고, 진짜 비밀은 사용자가 로컬에서 추가하도록 README에 안내합니다.
- 외부 플러그인 매니저(Vundle, TPM, oh-my-zsh)가 자동 설치하는 항목은 dotfile에 플러그인 이름만 적고, 실제 fetch는 installer에서 수행합니다.

---

## 🌿 브랜치 네이밍 규칙

브랜치 이름은 PR 타입 태그를 **대문자 prefix**로 사용하고, 그 뒤 설명은 **소문자 kebab-case**로 작성합니다.

- **형식**: `<TAG>-<description>`
- **예시**:
  - `FEAT-add-direnv-installer`
  - `FIX-zsh-plugin-path`
  - `REFACTOR-extract-deploy-dotfile`
  - `DOCS-update-contributing`
  - `HOTFIX-zsh-clobber-on-install`

---

## ✍️ 커밋 메시지 컨벤션

### 제목 형식

`[TAG] <요약 내용>` (영문 작성 권장, 50자 이내). Jira 이슈 ID가 있다면 `[SW-123] <subject>` 형식을 우선합니다 — `.gitmessage.txt` 템플릿 참고.

### 본문 규칙

- 제목과 본문 사이에 빈 줄 한 줄.
- 한 줄 72자 이내.
- "어떻게" 보다는 **"무엇을"**, **"왜"** 변경했는지 설명합니다.
- 명령형(Imperative) 어조를 사용합니다. (예: "Add direnv installer" (O), "Added installer" (X))
- 자동화 / 페어 작업에는 `Co-Authored-By:` trailer를 사용합니다.

---

## 🚀 풀 리퀘스트 (PR) 절차

### 1. PR 제목 규칙

PR 제목은 `[TAG] <요약 내용>` 형식을 따릅니다.

#### 태그 종류

| 태그 | 의미 |
|---|---|
| `[FEAT]` | 새로운 기능 추가 (신규 도구, 신규 subcommand) |
| `[FIX]` | 버그 수정 |
| `[DOCS]` | 문서 변경 |
| `[STYLE]` | 코드 포맷팅 |
| `[REFACTOR]` | 동작 변화 없는 리팩토링 |
| `[PERF]` | 성능 개선 |
| `[TEST]` | 테스트 추가/수정 |
| `[BUILD]` | 빌드 시스템 또는 외부 종속성 변경 |
| `[CI]` | CI 설정 파일 및 스크립트 변경 |
| `[CHORE]` | 그 외 기타 변경 |
| `[REVERT]` | 이전 커밋 되돌리기 |
| `[HOTFIX]` | 긴급 수정 |
| `[BOT]` | 자동화 작업 (dependabot, uv-lock-update 등) |

- 본문은 **영문**, 1–150자, 영숫자와 `` _-.,&*[]:/`<>=#+ `` 만 허용.
- 태그와 본문 사이는 공백 한 칸.

#### 예시

- `[FEAT] Add direnv installer`
- `[FIX] Avoid clobbering user .zshrc on install`
- `[REFACTOR] Extract deploy_dotfile backup logic`
- `[DOCS] Document --dry-run semantics`
- `[HOTFIX] Restore Linux guard in devenv install`

### 2. PR 본문 구성

별도 템플릿이 없으므로 다음 구조를 권장합니다.

1. **요약** — 이 PR이 무엇을 바꾸는가 (1–3문장).
2. **변경 사항** — bullet list로 핵심 변경.
3. **관련 이슈** — `Closes SW-XXX` (있으면).
4. **테스트 방법** — 어떤 환경에서 어떤 명령을 돌렸고 결과가 어땠는지.
5. **리뷰어 메모** — 주의 깊게 봐야 할 부분.

### 3. PR 체크리스트

제출 전 다음 사항을 확인하세요.

#### CLI / 설치 로직 변경

- [ ] `uv run --no-sync pytest tests/unit_test` 통과
- [ ] `uv run --no-sync pre-commit run --all-files` 통과 (ruff / ty / bashate / markdownlint)
- [ ] `uv run --no-sync devenv install --dry-run --home /tmp/<x>` 출력 확인
- [ ] (가능하면) 깨끗한 Ubuntu 컨테이너에서 `devenv install --yes` 끝까지 실행
- [ ] 같은 머신에서 `devenv install`을 **두 번** 실행해도 깨지지 않음 (idempotency)
- [ ] 사용자 기존 dotfile을 백업 없이 덮어쓰지 않음 (`deploy_dotfile` 사용 확인)
- [ ] 새 도구를 추가했다면 `_TOOL_REGISTRY`에 등록, `_tool_status()` markers에 라인 추가, 단위 테스트 추가

#### dotfile / packages 변경

- [ ] 사내 비밀 / 토큰 / 개인 경로 미포함
- [ ] 새 플러그인은 installer의 fetch 단계(`_ZSH_PLUGINS` 등)에도 등록
- [ ] `pyproject.toml`의 `package-data` 와일드카드가 새 파일을 포함하는지 확인
- [ ] `README.md`의 설정 파일 설명 섹션 갱신

#### Python 패키지 / 의존 변경

- [ ] `pyproject.toml`의 `dependencies` 또는 `dependency-groups.dev` 갱신
- [ ] `uv lock`으로 `uv.lock` 재생성, 커밋 포함
- [ ] type hints + Google docstring 추가
- [ ] `uv run --no-sync ty check devenv` 통과

---

## 🔍 코드 리뷰 기준

리뷰어는 다음 사항을 중점적으로 검토합니다.

- **Idempotency**: 두 번 실행해도 안전한가? `_installer.py`의 헬퍼를 사용했는가?
- **Safety**: 사용자 데이터 파괴 없는가? `--force`만 백업을 생략하는가? 무경고 `sudo` 없는가?
- **Testability**: `ctx.home`을 통해 HOME을 받고, `fake_home` fixture로 테스트 가능한가?
- **Cross-distro**: `apt-get` / `apt` 분기처럼 패키지 매니저 의존 코드는 OS 분기 또는 안내가 있는가?
- **Docs in sync**: 코드 변경과 README / CLAUDE.md / `.claude/rules/`의 설명이 일치하는가?
- **Consistency**: 기존 로깅(`click.secho`, `[dry-run]`, `✓` / `!`), 모듈 구조, Click 옵션 명명 컨벤션과 일관적인가?

---

## 🤝 기여 방법 (Step-by-Step)

1. **Repository Clone**: `git clone https://github.com/Hyper-Accel/linux-devenv.git`
2. **환경 설정**: `make install`
3. **Branch Out**: 규칙에 맞는 이름으로 새 브랜치 생성
4. **코드 / dotfile 작성**: 위의 디렉토리 규칙과 installer 패턴을 따라 작성
5. **Local 검증**:
   - `uv run --no-sync pytest tests/unit_test`
   - `uv run --no-sync pre-commit run --all-files`
   - `uv run --no-sync devenv install --dry-run --home /tmp/devenv-check`
6. **Submit PR**: PR 본문에 요약 / 변경 사항 / 검증 방법을 상세히 작성하여 제출

---

여러분의 기여는 Simulator 팀의 신규 서버 셋업 시간을 줄이고, 환경을 표준화하는 데 도움이 됩니다. 궁금한 점이 있다면 언제든 이슈를 통해 문의해 주세요!
