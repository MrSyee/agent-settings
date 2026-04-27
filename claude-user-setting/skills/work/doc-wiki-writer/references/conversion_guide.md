# Markdown to Wiki Markup Conversion Guide

Markdown과 Confluence Wiki Markup 간 변환 규칙 상세 가이드입니다.

## 목차

- [Text Formatting](#text-formatting)
- [Headings](#headings)
- [Lists](#lists)
- [Links](#links)
- [Images](#images)
- [Tables](#tables)
- [Code Blocks](#code-blocks)
- [Blockquotes](#blockquotes)
- [Task Lists](#task-lists)
- [Special Elements](#special-elements)
- [Eval Report 전용 변환](#eval-report-전용-변환)

## Text Formatting

| Description | Markdown | Wiki Markup | Notes |
|-------------|----------|-------------|-------|
| Bold | `**text**` or `__text__` | `*text*` | Markdown has two syntaxes |
| Italic | `*text*` or `_text_` | `_text_` | Markdown has two syntaxes |
| Bold+Italic | `***text***` | `*_text_*` | Combine both |
| Strikethrough | `~~text~~` | `-text-` | GFM extension |
| Code | `` `text` `` | `{{text}}` | Inline code |
| Underline | N/A | `+text+` | No Markdown equivalent |
| Superscript | N/A | `^text^` | No standard Markdown |
| Subscript | N/A | `~text~` | No standard Markdown |

## Headings

| Level | Markdown | Wiki Markup |
|-------|----------|-------------|
| H1 | `# Heading` | `h1. Heading` |
| H2 | `## Heading` | `h2. Heading` |
| H3 | `### Heading` | `h3. Heading` |
| H4 | `#### Heading` | `h4. Heading` |
| H5 | `##### Heading` | `h5. Heading` |
| H6 | `###### Heading` | `h6. Heading` |

## Lists

### Unordered Lists

**Markdown:**
```markdown
- Item 1
- Item 2
  - Sub-item 2.1
  - Sub-item 2.2
- Item 3
```

**Wiki Markup:**
```wiki
* Item 1
* Item 2
** Sub-item 2.1
** Sub-item 2.2
* Item 3
```

### Ordered Lists

**Markdown:**
```markdown
1. Step 1
2. Step 2
   1. Sub-step 2.1
   2. Sub-step 2.2
3. Step 3
```

**Wiki Markup:**
```wiki
# Step 1
# Step 2
## Sub-step 2.1
## Sub-step 2.2
# Step 3
```

### Mixed Lists

**Markdown:**
```markdown
1. Ordered item
   - Unordered sub-item
   - Another unordered
2. Next ordered
```

**Wiki Markup:**
```wiki
# Ordered item
#* Unordered sub-item
#* Another unordered
# Next ordered
```

## Links

### External Links

**Markdown:**
```markdown
[Link Text](http://example.com)
```

**Wiki Markup:**
```wiki
[Link Text|http://example.com]
```

### Internal/Page Links

**Markdown:**
```markdown
[Page Title](PageTitle)
```

**Wiki Markup:**
```wiki
[Page Title]
```

### Anchor Links

**Markdown:**
```markdown
[Jump to section](#section-id)
```

**Wiki Markup:**
```wiki
[Jump to section|#section-id]
```

## Images

**Markdown:**
```markdown
![Alt Text](image.png)
```

**Wiki Markup:**
```wiki
!image.png|alt=Alt Text!
```

**With Attributes:**
```wiki
!image.png|width=600, thumbnail, alt=설명!
```

## Tables

**Markdown:**
```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1.1 | Cell 1.2 | Cell 1.3 |
| Cell 2.1 | Cell 2.2 | Cell 2.3 |
```

**Wiki Markup:**
```wiki
||Header 1||Header 2||Header 3||
|Cell 1.1|Cell 1.2|Cell 1.3|
|Cell 2.1|Cell 2.2|Cell 2.3|
```

**변환 규칙:**
- 헤더 행: `| Header |` → `||Header||`
- 구분 행 (---): 제거
- 데이터 행: `| Cell |` → `|Cell|`

### 테이블 셀 내 특수문자 처리 (중요)

Confluence 테이블에서 `|`, `[`, `]`, `{`, `}` 문자는 특별한 의미를 가진다. 셀 안에 이 문자들이 포함되면 표가 깨지므로, 반드시 아래 규칙에 따라 변환해야 한다.

#### 1. 파이프 문자 (`|`) — 셀 구분자 충돌

`|`는 Confluence 테이블의 셀 구분자이므로, 셀 내용에 포함되면 컬럼이 어긋난다. `{{...}}` 인라인 코드 안에 있어도 동일하게 깨진다.

**해결:** `|` 대신 `or`로 표기한다.

| 원본 (깨짐) | 변환 후 (정상) |
|-------------|--------------|
| `{{string \| null}}` | `{{string}} or {{null}}` |
| `{{integer \| null}}` | `{{integer}} or {{null}}` |
| `{{object \| null}}` | `{{object}} or {{null}}` |

#### 2. 대괄호 (`[`, `]`) — 링크 구문 충돌

`[text]`는 Confluence에서 링크로 해석된다. `{{...}}` 인라인 코드 안에 있어도 깨질 수 있다.

**해결:** 제네릭 타입은 대괄호를 분리하여 `of` 키워드로 표기한다.

| 원본 (깨짐) | 변환 후 (정상) |
|-------------|--------------|
| `{{list[string]}}` | `{{list}} of {{string}}` |
| `{{list[integer]}}` | `{{list}} of {{integer}}` |
| `{{list[SearchHit]}}` | `{{list}} of {{SearchHit}}` |
| `{{dict[str, Any]}}` | `{{dict}} of {{str, Any}}` |

복합 타입 예시:

| 원본 (깨짐) | 변환 후 (정상) |
|-------------|--------------|
| `{{list[string] \| null}}` | `{{list}} of {{string}} or {{null}}` |
| `{{list[integer] \| null}}` | `{{list}} of {{integer}} or {{null}}` |

#### 3. 중괄호 (`{`, `}`) — 매크로 구문 충돌

`{macro}` 형태는 Confluence에서 매크로로 해석된다. `{{...}}` 인라인 코드 안의 단일 중괄호도 문제를 일으킬 수 있다.

**해결:** 인라인 코드 안에서 중괄호 리터럴이 필요하면, 전체를 한 단어로 표현하거나 중괄호를 제거한다.

| 원본 (깨짐) | 변환 후 (정상) |
|-------------|--------------|
| `{{"{keyword} {question}"}}` | `{{"keyword question"}}` |

#### 4. 백슬래시 이스케이프 (`\_`, `\[`, `\]`)

Markdown의 백슬래시 이스케이프는 Confluence wiki markup에서 동작하지 않는다. `{{...}}` 인라인 코드 안에서 `\_`는 리터럴 백슬래시로 표시되어 깨진다.

**해결:** `{{...}}` 안에서는 백슬래시 이스케이프를 제거하고 원본 문자를 그대로 사용한다.

| 원본 (깨짐) | 변환 후 (정상) |
|-------------|--------------|
| `{{collection\_name}}` | `{{collection_name}}` |
| `{{top\_k}}` | `{{top_k}}` |
| `{{yyyyMMdd\_HHmmss}}` | `{{yyyyMMdd_HHmmss}}` |

#### 5. 부등호/범위 표기

Constraint 컬럼 등에서 부등호 범위를 표기할 때는 인라인 코드 없이 일반 텍스트로 작성한다.

| 원본 (복잡) | 변환 후 (깔끔) |
|------------|--------------|
| `{{1 ≤ top_k ≤ 100}}` | `1 ~ 100` |
| `{{1 ≤ dense_top_k ≤ 200}}` | `1 ~ 200` |

## Code Blocks

### Fenced Code Blocks

**Markdown:**
````markdown
```python
def hello():
    print("Hello")
```
````

**Wiki Markup:**
```wiki
{code:language=python}
def hello():
    print("Hello")
{code}
```

### Inline Code

**Markdown:**
```markdown
Use `git commit` to save changes.
```

**Wiki Markup:**
```wiki
Use {{git commit}} to save changes.
```

## Blockquotes

**Markdown:**
```markdown
> This is a quote.
> It can span multiple lines.
```

**Wiki Markup (Quote Macro):**
```wiki
{quote}
This is a quote.
It can span multiple lines.
{quote}
```

## Horizontal Rules

**Markdown:**
```markdown
---
```

**Wiki Markup:**
```wiki
----
```

## Task Lists

**Markdown:**
```markdown
- [ ] Unchecked task
- [x] Checked task
```

**Wiki Markup:**
```wiki
[] Unchecked task
[x] Checked task
```

## Special Elements

### Info/Tip/Note/Warning Blocks

**Markdown (Admonitions):**
```markdown
> **Info:** This is important information.
> **Tip:** This is a helpful tip.
> **Warning:** Be careful!
```

**Wiki Markup:**
```wiki
{info}
This is important information.
{info}

{tip}
This is a helpful tip.
{tip}

{warning}
Be careful!
{warning}
```

### Table of Contents

**Markdown:**
```markdown
[TOC]
```

**Wiki Markup:**
```wiki
{toc}
```

### Anchor Definitions

**Markdown:**
```markdown
## Section Name {#custom-id}
```

**Wiki Markup:**
```wiki
h2. Section Name
{anchor:custom-id}
```

---

## Eval Report 전용 변환

### Langfuse 세션 링크

Eval Report 변환 시, Langfuse 세션 링크를 참고 문서 패널에 포함해야 합니다.

#### run_id 추출 방법

각 `eval_*_app/run_1/eval_result.json`의 samples 내 `run_id` 필드에서 UUID 부분을 추출합니다:

```
"run_id": "69d0c37b-30fa-4a0e-bf07-ac8f93a46e9b_run1"
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
          이 부분이 세션 ID
```

#### Langfuse URL 형식

```
https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3B{session_id}
```

#### 평가 유형별 세션 매핑

| 평가 디렉토리 | 세션 명칭 | 설명 |
|-------------|----------|------|
| eval_rag_app | RAG 세션 | RAG 평가 |
| eval_tool_gt_app | Guidance Tool 세션 | Guidance Agent Tool 평가 |
| eval_tool_ut_app | Guidance + Universe Tool 세션 | Guidance + Universe Tool 평가 |
| eval_router_gr_app | Guidance Router 세션 | Guidance Agent 라우팅 평가 |
| eval_router_rr_app | Main Router 세션 | Main Router 라우팅 평가 |

#### 참고 문서 패널 구조 (Wiki Markup)

```wiki
{panel:title=참고 문서|borderStyle=solid|borderColor=#FFD700|titleBGColor=#FFF8DC|bgColor=#FFFEF0}
||문서 형식||링크||
|Langfuse| - |
|RAG 세션|[세션 링크|https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3B{rag_session_id}]|
|Guidance Tool 세션|[세션 링크|https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3B{gt_session_id}]|
|평가 데이터|YYMMDD_평가결과|
|시각화 이미지|첨부파일 참조|
{panel}
```

---

## Best Practices

1. **변환 전 테스트**: 샘플 문서로 먼저 변환 테스트
2. **다이어그램 선처리**: Mermaid는 PNG로 렌더링 후 이미지로 참조
3. **출력 검증**: Confluence 미리보기에서 확인 후 게시
4. **원본 보관**: 변환 후에도 원본 Markdown 보관

---

**Version**: 1.0.0
**Last Updated**: 2026-02-09
