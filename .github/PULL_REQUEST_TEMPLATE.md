## 1. PR 타입 (PR Type)

이 PR이 어떤 종류의 변경 사항을 포함하는지 해당하는 모든 항목에 [x] 표시해주세요.

- [ ] feat: 새로운 기능 추가 (A new feature)
- [ ] fix: 버그 수정 (A bug fix)
- [ ] docs: 문서 변경 (Documentation only changes)
- [ ] style: 코드 포맷팅, 세미콜론 누락 등 (Code style changes, e.g., missing semicolons)
- [ ] refactor: 코드 리팩토링 (Code refactoring)
- [ ] perf: 성능 개선 (A code change that improves performance)
- [ ] test: 테스트 코드 추가 또는 수정 (Adding missing tests or correcting existing tests)
- [ ] build: 빌드 시스템 또는 외부 종속성 변경 (Changes that affect the build system or external dependencies)
- [ ] ci: CI 설정 파일 및 스크립트 변경 (Changes to our CI configuration files and scripts)
- [ ] chore: 기타 변경 사항 (Other changes that don't modify src or test files)
- [ ] revert: 이전 커밋 되돌리기 (Reverts a previous commit)

## 2. 변경 사항 요약 (Summary of Changes)

- 이 PR에서 어떤 변경 사항이 발생했는지 간결하게 설명해주세요. (예: "새로운 runtime 최적화 기능 추가", "compiler에서 발생하던 특정 버그 수정")

### prior discussion (optional)

- 이 PR과 관련된 논의했던 사항에 대해서 간결하게 설명해 주세요

## 3. 관련 이슈 (Related Issues)

- 이 PR이 해결하거나 관련 있는 이슈가 있다면 여기에 링크해주세요. (예: Closes ML-123, Fixes CMPL-112)

## 4. 변경 내용 상세 (Detailed Description of Changes)

- 변경된 코드에 대한 자세한 설명을 작성해주세요.
    - 어떤 문제가 해결되었는지?
    - 왜 이런 방식으로 해결했는지?
    - 특별히 고려해야 할 사항은 무엇인지?
    - runtime, compiler, simulator, misc 등 어떤 부분에 영향을 미치는지 명확히 해주세요.

## 5. 테스트 계획 (Test Plan)

- 변경 사항을 어떻게 테스트했는지 설명해주세요.
    - 어떤 테스트 케이스를 실행했는지?
    - 어떤 시나리오에서 테스트를 진행했는지?
    - 테스트 결과는 어떠했는지? (스크린샷, 로그 등 첨부 가능)

## 6. 리뷰어에게 (To Reviewers)

리뷰어에게 특별히 강조하고 싶거나 확인을 요청하고 싶은 부분이 있다면 작성해주세요.

- [ ] 제 코드가 프로젝트의 코드 스타일 가이드라인을 따릅니다.
- [ ] 제 코드가 새로운 경고를 발생시키지 않습니다.
- [ ] 변경 사항에 대한 테스트를 작성했습니다.
- [ ] 기존 테스트가 모두 통과합니다.
- [ ] 필요한 경우 문서(documentation)를 업데이트했습니다.
