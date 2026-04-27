---
name: doc-wiki-writer
description: Eval Report 마크다운 생성 및 Confluence Wiki Markup 변환을 지원합니다. "평가 리포트 만들어줘", "위키로 변환해줘" 같은 요청 시 사용합니다.
---

# Doc Wiki Writer

Eval Report 마크다운 생성 및 Confluence Wiki Markup 변환을 지원하는 경량 스킬입니다.

## 워크플로우

```
[Eval 데이터] → [마크다운 생성] → [Wiki Markup 변환]
```

1. **마크다운 생성**: aggregation.json에서 데이터 추출 → 마크다운 리포트 생성
2. **Wiki 변환**: 마크다운 파일을 Confluence Wiki Markup으로 변환

## 핵심 원칙

1. **마크다운 먼저**: Wiki 변환 전에 반드시 마크다운 리포트를 먼저 생성
2. **원본 보존**: 변환 시 원본 마크다운 파일을 임의로 편집/생략/추가하지 마세요
3. **문서 유형별 예시 참조**: 해당 유형의 예시 파일을 먼저 확인하세요

## 문서 유형별 예시

| 문서 유형 | 마크다운 예시 | Wiki 예시 | 설명 |
|----------|-------------|----------|------|
| **Eval Report** | [example/eval_report.md](example/eval_report.md) | [example/eval_report.wiki](example/eval_report.wiki) | 평가 결과 리포트 |
| **General Docs** | - | [example/general_docs.wiki](example/general_docs.wiki) | 일반 문서 |

---

## Part 1: 마크다운 생성 (Eval Report)

### 데이터 소스

**처리 대상**: `eval/results/eval_*_app/aggregation.json`

```json
{
  "aggregation": {
    "overall": {
      "metrics": {
        "metric_name": {
          "mean": 0.75, "std": 0.02, "min": 0.70, "max": 0.80, "median": 0.75
        }
      }
    },
    "per_sample": [
      { "id": 1, "mean_scores": {...}, "std_scores": {...} }
    ]
  }
}
```

### 이상치 판단 기준

| 유형 | 기준 | 설명 |
|------|------|------|
| 완전 실패 | mean = 0.0 | 모든 실행에서 0점 |
| 완벽 성공 | mean = 1.0 | 모든 실행에서 만점 |
| 높은 변동성 | std > 0.3 | 실행마다 결과가 불안정 |

### Langfuse 세션 링크

`eval_*_app/run_1/eval_result.json`에서 run_id 추출:

```
"run_id": "69d0c37b-30fa-4a0e-bf07-ac8f93a46e9b_run1"
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
          이 부분이 세션 ID
```

**URL 형식**:
```
https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3B{session_id}
```

### 리포트 구조

1. **핵심 지표 요약**: 모든 메트릭 + 이상치 샘플 요약
2. **평가 개요**: 평가 일시, Agent, 실행 횟수, Langfuse 링크
3. **상세 결과**: 각 평가 타입별 Summary, 이상치, 시각화(2x2)

상세 가이드: [references/eval_report_guide.md](references/eval_report_guide.md)

---

## Part 2: Wiki Markup 변환

### 기본 변환 규칙

| Markdown | Wiki Markup |
|----------|-------------|
| `# H1` | `h1. H1` |
| `## H2` | `h2. H2` |
| `### H3` | `h3. H3` |
| `**bold**` | `*bold*` |
| `*italic*` | `_italic_` |
| `` `code` `` | `{{code}}` |
| `[text](url)` | `[text\|url]` |
| `![alt](img.png)` | `!img.png\|alt=alt!` |
| `- item` | `* item` |
| `1. item` | `# item` |
| `> quote` | `{quote}...{quote}` |
| ` ```lang ` | `{code:language=lang}...{code}` |
| `---` | `----` |

### 테이블 변환

**Markdown:**
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

**Wiki Markup:**
```
||Header 1||Header 2||
|Cell 1|Cell 2|
```

### 테이블 셀 내 특수문자 처리 (중요)

테이블 셀 안에서 `|`, `[`, `]`, `{`, `}` 문자는 Confluence 구문과 충돌하여 표가 깨진다. `{{...}}` 인라인 코드 안에 있어도 동일하게 깨진다. 반드시 아래 규칙을 따른다.

| 문제 | 원본 (깨짐) | 변환 후 (정상) |
|------|------------|--------------|
| 파이프 충돌 | `{{string \| null}}` | `{{string}} or {{null}}` |
| 대괄호 충돌 | `{{list[string]}}` | `{{list}} of {{string}}` |
| 복합 타입 | `{{list[string] \| null}}` | `{{list}} of {{string}} or {{null}}` |
| 중괄호 충돌 | `{{"{keyword}"}}` | 중괄호 제거 또는 텍스트로 풀어쓰기 |
| 백슬래시 | `{{top\_k}}` | `{{top_k}}` (이스케이프 제거) |
| 범위 표기 | `{{1 ≤ top_k ≤ 100}}` | `1 ~ 100` |

상세 규칙: [references/conversion_guide.md](references/conversion_guide.md)의 "테이블 셀 내 특수문자 처리" 섹션 참조

### 유용한 매크로

```wiki
{status:colour=Green|title=완료}
{info:title=정보}내용{info}
{tip:title=팁}내용{tip}
{note:title=참고}내용{note}
{warning:title=경고}내용{warning}
{anchor:section-id}
[섹션으로 이동|#section-id]
!image.png|thumbnail, width=800!
{panel:title=제목|borderStyle=solid|borderColor=#ccc|bgColor=#f5f5f5}내용{panel}
{toc:minLevel=2|maxLevel=3}
```

### 레이아웃 (섹션/컬럼)

```wiki
{section}
{column:width=75%}
메인 콘텐츠
{column}
{column:width=25%}
사이드바
{column}
{section}
```

상세 가이드: [references/conversion_guide.md](references/conversion_guide.md)

---

## 추가 레퍼런스

- **Eval Report 생성 가이드**: [references/eval_report_guide.md](references/eval_report_guide.md)
- **변환 규칙 상세**: [references/conversion_guide.md](references/conversion_guide.md)
