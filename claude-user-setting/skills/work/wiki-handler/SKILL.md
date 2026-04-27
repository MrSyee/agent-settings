---
name: wiki-handler
description: >
  Confluence(Wiki) 페이지를 자유자재로 다루는 스킬입니다.
  "위키 페이지 조회해줘", "컨플루언스에 문서 올려줘", "위키 페이지 수정해줘",
  "wiki page 만들어줘", "confluence space 조회", "위키 검색해줘" 등
  Confluence/Wiki 관련 CRUD 작업 요청 시 사용합니다.
  atlassian-python-api 라이브러리를 사용하며, API 토큰 기반 인증을 지원합니다.
user_invocable: true
tools: "Read, Write, Edit, Bash, Grep, Glob"
---

# Wiki Handler

Confluence(Wiki) 페이지 조회, 생성, 수정 등 모든 Wiki 작업을 수행하는 스킬입니다.

**중요: 이 스킬은 페이지를 실제로 삭제하지 않습니다.**
삭제 요청 시 페이지 제목에 `(삭제)` 접두어를 붙여 소프트 삭제 표시만 합니다.
실행 후 반드시 사용자에게 "실제 삭제가 아닌 제목 마킹만 수행되었습니다"라고 안내합니다.

## 초기 설정 (필수)

스킬 실행 시 **가장 먼저** 인증 정보를 확인합니다.

### 1단계: 환경 변수 확인

아래 환경 변수가 설정되어 있는지 확인합니다:

```bash
echo "CONFLUENCE_BASE_URL=${CONFLUENCE_BASE_URL:-not set}"
echo "CONFLUENCE_TOKEN=${CONFLUENCE_TOKEN:+set (hidden)}"
echo "CONFLUENCE_USERNAME=${CONFLUENCE_USERNAME:-not set}"
echo "CONFLUENCE_NO_VERIFY_SSL=${CONFLUENCE_NO_VERIFY_SSL:-not set}"
```

> **환경 변수 설정 위치**: `~/.claude/.env` (`.claude-settings-repo/claude-user-setting/.env.local` 심볼릭 링크)
>
> | 환경변수 | 설명 | 예시 |
> |---|---|---|
> | `CONFLUENCE_BASE_URL` | Confluence 서버 URL | `https://wiki.sgr.com` |
> | `CONFLUENCE_TOKEN` | Personal Access Token | `your-token-here` |
> | `CONFLUENCE_NO_VERIFY_SSL` | SSL 검증 비활성화 (내부망) | `true` |

### 2단계: 환경 변수가 없으면 사용자에게 질문

환경 변수가 설정되어 있지 않으면 사용자에게 다음 정보를 요청합니다:

1. **Confluence Base URL** (예: `https://wiki.example.com`)
2. **인증 방식 선택**:
   - **API Token** (권장): Personal Access Token
   - **Username + Password**: 기본 인증

### 3단계: 헬퍼 스크립트 실행

인증 정보를 확보한 후 `scripts/confluence_cli.py`를 사용하여 작업을 수행합니다.

---

## 사용 가능한 명령

### 페이지 조회

```bash
# 페이지 ID로 조회 (환경변수 자동 사용)
python scripts/confluence_cli.py get-page --page-id "12345"

# 제목으로 검색
python scripts/confluence_cli.py search --space-key "MYSPACE" --query "검색어"

# 스페이스 내 모든 페이지 목록
python scripts/confluence_cli.py list-pages --space-key "MYSPACE" --limit 50
```

### 페이지 생성

```bash
# 새 페이지 생성 (Wiki Markup)
python scripts/confluence_cli.py create-page \
  --space-key "MYSPACE" \
  --title "페이지 제목" \
  --body-file /path/to/content.html \
  --parent-id "12345"  # 선택: 부모 페이지 ID
```

### 페이지 수정

```bash
# 기존 페이지 내용 수정
python scripts/confluence_cli.py update-page \
  --page-id "12345" \
  --title "수정된 제목" \
  --body-file /path/to/updated_content.html
```

### 페이지 삭제 표시 (소프트 삭제)

이 스킬은 페이지를 실제로 삭제하지 않습니다. 대신 제목에 `(삭제)` 접두어를 붙여 마킹합니다.
실행 후 사용자에게 **"실제 삭제가 아닌 제목 마킹만 수행되었습니다"** 라고 반드시 안내합니다.

```bash
# 페이지 제목에 (삭제) 표시
python scripts/confluence_cli.py mark-deleted --page-id "12345"
```

실행 결과 예시:
- 기존 제목: `장비 재련 가이드` → 변경 후: `(삭제)장비 재련 가이드`
- 이미 `(삭제)` 표시된 페이지는 중복 마킹하지 않음

### 스페이스 관리

```bash
# 스페이스 목록 조회
python scripts/confluence_cli.py list-spaces

# 특정 스페이스 정보 조회
python scripts/confluence_cli.py get-space --space-key "MYSPACE"
```

### 첨부 파일

```bash
# 페이지에 파일 첨부
python scripts/confluence_cli.py attach-file \
  --page-id "12345" \
  --file-path /path/to/file.pdf

# 첨부 파일 목록 조회
python scripts/confluence_cli.py list-attachments --page-id "12345"
```

### 자식 페이지 조회

```bash
# 특정 페이지의 자식 페이지 목록
python scripts/confluence_cli.py get-children --page-id "12345"
```

---

## 워크플로우

### 문서 조회 워크플로우
```
[인증 확인] → [검색/조회 명령 실행] → [결과를 사용자에게 표시]
```

### 문서 업로드 워크플로우
```
[인증 확인] → [콘텐츠 준비 (HTML/Storage Format)] → [create-page 실행] → [생성된 페이지 URL 반환]
```

### 문서 수정 워크플로우
```
[인증 확인] → [get-page로 현재 내용 확인] → [내용 수정] → [update-page 실행] → [결과 확인]
```

### 문서 삭제 표시 워크플로우
```
[인증 확인] → [사용자에게 소프트 삭제 방식임을 안내] → [mark-deleted 실행] → [결과 확인 및 사용자 알림]
```
실행 완료 후 반드시 사용자에게 아래 내용을 전달:
- "페이지가 실제로 삭제되지 않았으며, 제목에 (삭제)가 추가되었습니다"
- 변경된 제목과 페이지 URL

---

## 콘텐츠 포맷

Confluence는 **Storage Format (XHTML)** 을 사용합니다.

### 기본 변환 규칙 (Markdown → Storage Format)

| Markdown | Confluence Storage Format |
|----------|--------------------------|
| `# H1` | `<h1>H1</h1>` |
| `## H2` | `<h2>H2</h2>` |
| `**bold**` | `<strong>bold</strong>` |
| `*italic*` | `<em>italic</em>` |
| `` `code` `` | `<code>code</code>` |
| `[text](url)` | `<a href="url">text</a>` |
| `- item` | `<ul><li>item</li></ul>` |
| `1. item` | `<ol><li>item</li></ol>` |
| ` ```lang ` | `<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">lang</ac:parameter><ac:plain-text-body><![CDATA[...]]></ac:plain-text-body></ac:structured-macro>` |

### 유용한 매크로 (Storage Format)

```html
<!-- 정보 패널 -->
<ac:structured-macro ac:name="info">
  <ac:parameter ac:name="title">제목</ac:parameter>
  <ac:rich-text-body><p>내용</p></ac:rich-text-body>
</ac:structured-macro>

<!-- 코드 블록 -->
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:plain-text-body><![CDATA[print("hello")]]></ac:plain-text-body>
</ac:structured-macro>

<!-- 테이블 -->
<table>
  <tr><th>Header 1</th><th>Header 2</th></tr>
  <tr><td>Cell 1</td><td>Cell 2</td></tr>
</table>

<!-- 목차 -->
<ac:structured-macro ac:name="toc">
  <ac:parameter ac:name="minLevel">2</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
</ac:structured-macro>
```

---

## 주의사항

1. **인증 정보 보안**: API 토큰은 절대 파일에 하드코딩하지 말 것. 환경 변수 또는 사용자 입력으로만 전달
2. **Storage Format**: Confluence API는 XHTML 기반 Storage Format을 사용. 일반 HTML이 아닌 Confluence Storage Format으로 작성
3. **버전 관리**: 페이지 수정 시 현재 버전 번호를 반드시 조회한 후 +1하여 전달
4. **권한 확인**: 사용자의 API 토큰이 해당 스페이스/페이지에 대한 권한이 있는지 확인
5. **대량 작업 주의**: 대량 페이지 조회 시 limit 파라미터를 적절히 설정하여 API 과부하 방지

---

## 에러 처리

| 에러 코드 | 원인 | 해결 방법 |
|-----------|------|----------|
| 401 | 인증 실패 | API 토큰/비밀번호 확인 |
| 403 | 권한 없음 | 스페이스/페이지 접근 권한 확인 |
| 404 | 페이지 없음 | 페이지 ID/스페이스 키 확인 |
| 409 | 버전 충돌 | 최신 버전 번호로 재시도 |

## 의존성

이 스킬은 `atlassian-python-api` 라이브러리를 사용합니다.
스크립트 첫 실행 시 자동으로 설치 여부를 확인합니다.
