---
name: pr-description
description: >
  Generate a PR description based on the current branch's commits and diffs compared to the base branch.
  Use this skill whenever the user asks to create, generate, or write a PR description, PR body, pull request summary,
  or mentions wanting to fill in a PR template. Also trigger when the user says things like "PR 작성해줘",
  "PR description 만들어줘", "PR 설명 생성해줘", or any Korean/English request related to drafting pull request content.
user_invocable: true
---

# PR Description Generator

Generate a structured PR description by analyzing the current branch's git history (commits and diffs) relative to the base branch.

## Workflow

1. **Determine the base branch**: Default to `main`. If the user specifies a different base branch, use that instead.

2. **Gather git information**: Run these commands to understand the changes:
   ```bash
   git log --oneline <base-branch>..HEAD
   git diff <base-branch>...HEAD --stat
   git diff <base-branch>...HEAD
   ```

3. **Generate the PR title and description** using the template below.
   - 결과를 마크다운 코드블록(```markdown ... ```)으로 감싸서 출력한다.
   - 사용자가 그대로 복사하여 PR title과 body에 붙여넣을 수 있도록 한다.

## Template

```markdown
# PR 제목
<conventional commit tag>: <한글 제목>

## 요약
<3줄 이내로 이 PR이 무엇을 하는지 요약. 핵심 변경 사항과 목적을 간결하게 서술한다.>

## 작업 내역
<각 작업 항목을 commit tag 스타일의 prefix와 함께 나열한다.>
```

## PR 제목 Rules

- 맨 앞에 conventional commit tag를 붙인다: `feat:`, `fix:`, `refactor:`, `chore:` 등.
- PR에 여러 종류의 변경이 섞여 있으면, 가장 비중이 큰 변경의 tag를 사용한다.
- 제목은 한글로 작성하며, 70자 이내로 간결하게 핵심을 요약한다.
- 예시: `feat: 모범답안 가드 조건 추가 및 에러 핸들링 개선`

## 요약 Section Rules

- 최대 3줄(문장)으로 작성한다.
- 이 PR의 목적과 핵심 변경 내용을 간결하게 서술한다.
- 불필요한 기술적 디테일은 빼고, "왜" 이 변경이 필요한지에 초점을 맞춘다.

## 작업 내역 Section Rules

- 각 항목 앞에 conventional commit tag를 prefix로 붙인다:
  - `feat:` — 새로운 기능 추가
  - `fix:` — 버그 수정
  - `refactor:` — 기능 변경 없이 코드 구조 개선
  - `style:` — 코드 포맷팅, 세미콜론 등 스타일 변경
  - `docs:` — 문서 변경
  - `test:` — 테스트 추가/수정
  - `chore:` — 빌드, 설정, 의존성 등 기타 변경
  - `perf:` — 성능 개선
  - `ci:` — CI/CD 관련 변경

- 관련 커밋이 여러 개라도 논리적으로 하나의 작업이면 하나의 항목으로 묶는다.
- 반대로 하나의 커밋이 여러 종류의 변경을 포함하면 분리한다.
- 각 항목은 `-` 로 시작하는 bullet point로 작성한다.
- 변경된 주요 파일이나 모듈명을 괄호 안에 포함하면 좋다. 예: `(server/src/services/answer_service.py)`
- 각 항목 끝에 관련 커밋 해시(short hash)를 괄호로 표기한다. 여러 커밋이 하나의 항목으로 묶인 경우 관련 커밋 해시를 모두 나열한다. 예: `(830b18c)`, `(830b18c, e5d1656)`
- 하위 상세 내용이 필요하면 들여쓰기로 sub-bullet을 사용한다.

## Example Output

```markdown
# PR 제목
feat: 채점 결과 조회 API 경량화 및 Firestore 쿼리 최적화

## 요약
채점 결과 조회 API의 응답 페이로드를 경량화하고 Firestore 쿼리를 최적화하여 조회 성능을 개선합니다.
AnswerSummaryDTO 도입으로 건당 불필요한 대용량 필드 전송을 제거하고, 쿼리 레벨에서 삭제된 문서를 필터링합니다.

## 작업 내역
- feat: `AnswerSummaryDTO` 경량 DTO 추가 (`server/src/schemas/answer.py`) (a1b2c3d)
  - 목록 조회 시 `parsed_answer`, `grading_comment`, `sections` 필드 제외
  - `GetAnswersResponseDTO.answers` 타입을 `list[AnswerSummaryDTO]`로 변경
- feat: `get_active_answers_by_project_id` Repository 메서드 추가 (`server/src/services/repository.py`) (a1b2c3d)
  - Firestore 쿼리 레벨에서 `grading_status != "deleted"` 필터 적용
- refactor: `AnswerService.get_answers` 수정 (`server/src/services/answer/answer_service.py`) (d4e5f6a)
  - 신규 Repository 메서드 + AnswerSummaryDTO 변환 적용
- test: `TestAnswerSummaryDTO` 신규 테스트 3개 추가 (d4e5f6a, a1b2c3d)
  - 필드 매핑, 대용량 필드 제외, 반환 타입 검증
- docs: `test_scenario.md` 업데이트 (d4e5f6a)
```

## Notes

- PR description은 한국어로 작성한다 (이 프로젝트의 관행).
- 커밋 메시지가 한국어인 경우 그대로 활용하되, commit tag prefix는 영어 conventional commit 형식을 사용한다.
- 요약은 반드시 3줄 이내를 지킨다. 넘기지 않는다.
- 변경이 서버/프론트 등 여러 영역에 걸치면 작업 내역에서 `### 서버`, `### 프론트엔드` 등으로 구분해도 좋다.
