---
description: Reference when creating PRs, writing commits, or naming branches.
globs:
  - ".github/**"
  - ".gitmessage.txt"
alwaysApply: false
---

# Contribution guide

이 파일은 에이전트용 빠른 참조다. 실제 사용자용 문서는 `README.md`의 "커밋 메시지 규칙" 섹션과 `.gitmessage.txt` 템플릿이다.

## Branch naming

- 형식: `<TAG>-<short-description>` — TAG는 UPPER_CASE, description은 lowercase kebab-case.
- 예시:
  - `Feature-add-direnv-installer`
  - `Hotfix-fix-zsh-plugin-path`
  - `Refactor-extract-deploy-dotfile`
  - `Docs-update-readme`

기존 `git log` (`[Feature]`, `[Hotfix]` 등)와 일관된 태그를 사용하라.

## Commit messages

`.gitmessage.txt` 템플릿을 따른다.

### Subject

`[<jira-issue-id>] <subject>` — 영어, 50자 이내, 명령형(imperative), 마침표 없음.

- Jira 이슈 ID는 `[SW-123]` 형식.
- 카테고리 태그(`[Feature]`, `[HOTFIX]`)도 기존 히스토리에 쓰임. **Jira ID가 있으면 그것을 우선**.

### Body

- subject와 body 사이 빈 줄 1줄.
- 한 줄 72자 이내.
- **무엇 / 왜**를 설명. **어떻게**는 코드.
- bullet point는 `-`로 시작.
- 자동화 / 페어 작업은 `Co-Authored-By:` trailer.

### Examples

```text
[SW-201] Port install scripts to devenv CLI

- Replace scripts/install_*.sh with devenv/cli/_{zsh,vim,tmux}.py
- Add InstallContext + idempotent helpers in _installer.py
- Move packages/ under devenv/ as wheel package-data
```

```text
[Hotfix] Avoid clobbering user .zshrc on devenv install

- deploy_dotfile now backs up to ~/.zshrc.bak.<UTC-ts> by default
- --force opts out of backup creation
```

## PR title

- 형식: `[<TAG>] <body>` — 기존 머지된 PR과 일관 (`[Feature] ...`, `[HOTFIX] ...`).
- TAG 후보: `Feature`, `Fix`, `Hotfix`, `Refactor`, `Docs`, `Chore`, `CI`, `Build`, `Test`, `Revert`.
- body: 영어, 명령형. PR 번호 `(#N)`은 머지 시 자동 append.

## PR body

별도 템플릿이 없으므로 다음 구조를 권장:

1. **요약** — 이 PR이 무엇을 바꾸는가 (1–3문장).
2. **변경 사항** — bullet list.
3. **관련 이슈** — `Closes SW-XXX` (있으면).
4. **테스트 방법** — 어떤 환경에서 어떤 명령을 돌렸고 결과가 어땠는지 (`uv run --no-sync pytest`, `devenv install --dry-run`, 컨테이너 통합 등).
5. **리뷰어 메모** — 주의 깊게 봐야 할 부분.

## PR checklist (CLI / 설치 로직 변경 시)

- [ ] `uv run --no-sync pytest tests/unit_test` 통과.
- [ ] `uv run --no-sync pre-commit run --all-files` 통과 (ruff, ty, bashate, markdownlint).
- [ ] `uv run --no-sync devenv install --dry-run --home /tmp/<x>` 출력 확인.
- [ ] (가능하면) 깨끗한 Ubuntu 컨테이너에서 `devenv install --yes` 끝까지 실행.
- [ ] 같은 머신에서 `devenv install`을 **두 번** 실행해도 깨지지 않음 (idempotency).
- [ ] 사용자 기존 dotfile을 백업 없이 덮어쓰지 않음 (`deploy_dotfile` 사용 확인).
- [ ] 새 도구를 추가했다면 `_TOOL_REGISTRY`에 등록, `_tool_status()`의 markers에 라인 추가, 단위 테스트 추가.

## PR checklist (dotfile / packages 변경 시)

- [ ] 사내 비밀 / 토큰 / 개인 경로 미포함.
- [ ] 새 플러그인은 installer의 fetch 단계(`_ZSH_PLUGINS` 등)에도 등록.
- [ ] `pyproject.toml`의 `package-data` 와일드카드가 새 파일을 포함하는지 확인.
- [ ] `README.md`의 설정 파일 설명 섹션 갱신.

## PR checklist (Python 패키지 / 의존 변경 시)

- [ ] `pyproject.toml`의 `dependencies` 또는 `dependency-groups.dev` 갱신.
- [ ] `uv lock`으로 `uv.lock` 재생성, 커밋 포함.
- [ ] type hints + Google docstring 추가.
- [ ] `ty check devenv` 통과.

## Code review criteria

리뷰어 관점:

- **Idempotency**: 두 번 실행 안전한가? `_installer.py`의 헬퍼를 사용했는가?
- **Safety**: 사용자 데이터 파괴 없는가? `--force`만 백업을 생략하는가? 무경고 `sudo` 없는가?
- **Testability**: `ctx.home` 통해 HOME을 받고, `fake_home` fixture로 테스트 가능한가?
- **Cross-distro**: apt-get / apt 분기처럼 패키지 매니저 의존 코드는 OS 분기 또는 안내가 있는가?
- **Docs in sync**: 코드 변경과 README / CLAUDE.md / `.claude/rules/` 의 설명이 일치하는가?
- **Consistency**: 기존 로깅(`click.secho`, `[dry-run]`, `✓` / `!`), 모듈 구조, Click 옵션 명명 컨벤션과 일관적인가?
