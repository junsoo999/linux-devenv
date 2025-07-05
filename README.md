# Linux Development Environment Setup

Linux 서버 환경에서 개발에 필요한 도구들을 자동으로 설치하고 설정하는 프로젝트입니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [시스템 요구사항](#시스템-요구사항)
- [설치 방법](#설치-방법)
- [프로젝트 구조](#프로젝트-구조)
- [주요 기능](#주요-기능)
- [사용법](#사용법)
- [설정 파일](#설정-파일)
- [커밋 메시지 규칙](#커밋-메시지-규칙)
- [문제 해결](#문제-해결)

## 🎯 프로젝트 개요

이 프로젝트는 Linux 서버 환경에서 개발 작업을 위한 필수 도구들을 자동으로 설치하고 설정하는 스크립트 모음입니다. 다음과 같은 기능을 제공합니다:

- **Z-Shell (Oh My Zsh)** 설치 및 설정
- **Vim** 에디터 및 플러그인 설치
- **Powerlevel10k** 테마 설정
- **프로젝트 디렉토리 구조** 자동 생성
- **개발 환경 변수** 및 **alias** 설정

## 💻 시스템 요구사항

### 필수 요구사항
- **운영체제**: Linux (Ubuntu, CentOS, Debian 등)
- **권한**: sudo 권한이 있는 사용자 계정
- **네트워크**: 인터넷 연결 (GitHub, 패키지 저장소 접근)

### 권장 사항
- **메모리**: 최소 2GB RAM
- **저장공간**: 최소 1GB 여유 공간
- **터미널**: 256색 이상 지원하는 터미널

## 🚀 설치 방법

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd linux-devenv
```

### 2. 전체 환경 설치
```bash
make install
```

### 3. 개별 도구 설치
```bash
# 디렉토리 구조만 설정
make setup

# Z-Shell만 설치
./scripts/install_zsh.sh

# Vim만 설치
./scripts/install_vim.sh
```

## 📁 프로젝트 구조

```
linux-devenv/
├── Makefile                 # 메인 빌드 스크립트
├── README.md               # 프로젝트 문서
├── .gitmessage.txt         # Git 커밋 메시지 템플릿
├── .gitignore              # Git 무시 파일 목록
├── scripts/                # 설치 스크립트들
│   ├── install_dir.sh      # 디렉토리 구조 생성
│   ├── install_zsh.sh      # Z-Shell 설치
│   └── install_vim.sh      # Vim 설치
└── packages/               # 설정 파일들
    ├── vim/
    │   └── vimrc          # Vim 설정 파일
    └── zsh/
        ├── zshrc          # Z-Shell 메인 설정
        ├── zsh_aliases    # Z-Shell 별칭 설정
        ├── zsh_ohmyzsh    # Oh My Zsh 설정
        └── p10k.zsh       # Powerlevel10k 테마 설정
```

## ⚡ 주요 기능

### 1. Z-Shell (Oh My Zsh) 설정
- **Oh My Zsh** 프레임워크 설치
- **Powerlevel10k** 테마 적용
- **다양한 플러그인** 자동 설치:
  - `zsh-autosuggestions`: 명령어 자동 완성
  - `zsh-syntax-highlighting`: 구문 강조
  - `zsh-history-substring-search`: 히스토리 검색
  - `you-should-use`: alias 제안
  - `nvm`: Node.js 버전 관리
  - `fzf`: 퍼지 검색
  - `thefuck`: 명령어 수정 제안
  - `autojump`: 디렉토리 점프

### 2. Vim 에디터 설정
- **Vundle** 플러그인 매니저 설치
- **다양한 플러그인** 자동 설치:
  - `vim-code-dark`: VSCode 다크 테마
  - `nerdtree`: 파일 탐색기
  - `vim-airline`: 상태바
  - `vim-fugitive`: Git 통합
  - `ctrlp`: 파일 검색
  - `syntastic`: 문법 검사
  - `vim-gitgutter`: Git 변경사항 표시
  - `nerdcommenter`: 주석 관리

### 3. 프로젝트 디렉토리 구조
자동으로 생성되는 디렉토리 구조:
```
$HOME/
├── documents/          # 문서 저장소
├── downloads/          # 다운로드 폴더
├── projects/           # 프로젝트 폴더
│   ├── aida/          # AIDA 프로젝트
│   │   └── .setup.sh  # 프로젝트별 설정
│   └── bertha/        # BERTHA 프로젝트
│       └── .setup.sh  # 프로젝트별 설정
└── tasks/             # 작업 관리 폴더
```

## 🛠️ 사용법

### Makefile 명령어

```bash
# 도움말 보기
make help

# 전체 환경 설치 (Linux 서버에서만 실행 가능)
make install

# 디렉토리 구조만 설정
make setup

# 임시 파일 정리
make clean
```

### 개별 스크립트 실행

```bash
# 디렉토리 구조 생성
./scripts/install_dir.sh

# Z-Shell 설치
./scripts/install_zsh.sh

# Vim 설치
./scripts/install_vim.sh
```

### 프로젝트별 설정 사용

각 프로젝트 디렉토리에는 `.setup.sh` 파일이 생성되어 프로젝트별 alias와 설정을 제공합니다:

```bash
# AIDA 프로젝트로 이동
aida

# BERTHA 프로젝트로 이동
ber

# 프로젝트별 개발 명령어
aida-run    # AIDA 프로젝트 실행
ber-build   # BERTHA 프로젝트 빌드
```

## ⚙️ 설정 파일

### Z-Shell 설정 (`packages/zsh/zshrc`)
- Powerlevel10k 인스턴트 프롬프트 활성화
- Oh My Zsh 프레임워크 로드
- NVIDIA CUDA 환경 변수 설정
- UV Framework 환경 설정

### Z-Shell 별칭 (`packages/zsh/zsh_aliases`)
- **파일 관리**: `ll`, `la`, `l` (ls 명령어 확장)
- **권한 관리**: `chdir` (소유권 변경)
- **터미널 관리**: `tt`, `tkill` (tmux 관리)
- **빌드 최적화**: `fmake` (병렬 빌드)
- **모니터링**: `gpu`, `lpu` (GPU 모니터링)
- **설정 편집**: `vc`, `va`, `vv` (설정 파일 편집)

### Vim 설정 (`packages/vim/vimrc`)
- **일반 설정**: 번호 표시, 구문 강조, 자동 들여쓰기
- **플러그인 관리**: Vundle을 통한 플러그인 관리
- **테마**: VSCode 다크 테마 적용
- **단축키**: NERDTree, 버퍼 관리 등

## 📝 커밋 메시지 규칙

프로젝트는 `.gitmessage.txt`에 정의된 커밋 메시지 규칙을 따릅니다:

### 형식
```
[jira-issue-id] <subject>

Body Message
```

### 규칙
- **제목**: 50자 이내, 명령형 문장, 마침표 없음
- **본문**: 72자 이내, 무엇과 왜를 설명
- **JIRA 이슈**: `[SW-123]` 형식으로 이슈 ID 포함

### 예시
```
[SW-123] Add zsh autosuggestions plugin

- Install zsh-autosuggestions for better command completion
- Configure plugin in zsh_ohmyzsh file
- Update installation script to include new plugin
```
