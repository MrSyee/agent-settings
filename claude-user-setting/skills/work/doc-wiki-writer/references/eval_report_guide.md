# Eval Report 생성 가이드

## 개요

`aggregation.json` 파일에서 데이터를 추출하여 평가 리포트를 생성하는 방법을 설명합니다.

## aggregation.json 구조

```json
{
  "aggregation": {
    "overall": {
      "metrics": {
        "metric_name": {
          "mean": 0.75,
          "std": 0.02,
          "min": 0.70,
          "max": 0.80,
          "median": 0.75
        }
      },
      "n_runs": 5,
      "n_samples": 50
    },
    "per_sample": [
      {
        "id": 1,
        "raw_scores": {
          "metric_name": [0.8, 0.7, 0.9, 0.75, 0.85]
        },
        "mean_scores": {
          "metric_name": 0.80
        },
        "std_scores": {
          "metric_name": 0.07
        }
      }
    ]
  }
}
```

## 이상치 판단 기준

### 기본 기준

| 유형 | 기준 | 설명 |
|------|------|------|
| 완전 실패 | mean = 0.0 | 모든 실행에서 0점 |
| 완벽 성공 | mean = 1.0 | 모든 실행에서 만점 |
| 높은 변동성 | std > 0.3 | 실행마다 결과가 불안정 |

### 유연한 기준 조정

데이터 특성에 따라 조정 가능:

- **전체 평균이 낮은 메트릭**: std > 0.2로 낮출 수 있음
- **이진 결과(0 or 1)가 많은 메트릭**: mean < 0.5를 저조 기준으로 사용

## 시각화 파일 경로

```
eval/{eval_type}_app/visualizations/
├── aggregation_summary.png
├── pass_at_k.png
├── run_comparison.png
└── sample_variability.png
```

## 리포트 구조

### 1. 핵심 지표 요약
- **모든 메트릭 포함**: 평가 유형별로 aggregation.json의 summary에 있는 모든 메트릭을 테이블에 포함
- 이상치 샘플 요약 테이블

**핵심 지표 요약 테이블 예시:**
```markdown
| 평가 유형 | 주요 메트릭 | 평균 점수 |
|----------|------------|----------|
| **RAG** | context_precision | **0.74** |
| **RAG** | context_recall | **0.96** |
| **RAG** | faithfulness | **0.88** |
| **RAG** | deepeval_answer_relevancy | **0.93** |
| **Router (GR)** | routing_accuracy | **0.66** |
...
```

> **중요**: 핵심 지표 요약에는 각 평가 유형의 모든 메트릭을 누락 없이 기재해야 합니다.

### 2. 평가 개요
- 평가 일시, Agent, 실행 횟수, 평가 유형

### 3. 상세 결과 (각 평가 타입별)
- Summary 테이블 (Mean, Std, Min, Max, Median)
- 이상치 샘플 테이블
- 시각화 이미지 (2x2 배치)

## Langfuse 세션 링크

### run_id 추출 방법

각 `eval_*_app/run_1/eval_result.json`의 samples 내 `run_id` 필드에서 UUID 부분을 추출합니다:

```
"run_id": "69d0c37b-30fa-4a0e-bf07-ac8f93a46e9b_run1"
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
          이 부분이 세션 ID
```

**추출 명령어:**
```bash
grep -o '"run_id": "[^"]*"' eval_result.json | head -1 | sed 's/"run_id": "\([^_]*\).*/\1/'
```

### Langfuse URL 형식

```
https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3B{session_id}
```

### 평가 유형별 세션 매핑

| 평가 디렉토리 | 세션 명칭 | 설명 |
|-------------|----------|------|
| eval_rag_app | RAG 세션 | RAG 평가 |
| eval_tool_gt_app | Guidance Tool 세션 | Guidance Agent Tool 평가 |
| eval_tool_ut_app | Guidance + Universe Tool 세션 | Guidance + Universe Tool 평가 |
| eval_router_gr_app | Guidance Router 세션 | Guidance Agent 라우팅 평가 |
| eval_router_rr_app | Main Router 세션 | Main Router 라우팅 평가 |

### 참고 문서 패널 구조

리포트 상단의 참고 문서 패널에 Langfuse 세션 링크를 포함합니다:

```markdown
| 문서 형식 | 링크 |
|----------|------|
| Langfuse | - |
| RAG 세션 | [세션 링크](langfuse_url) |
| Guidance Tool 세션 | [세션 링크](langfuse_url) |
| Guidance + Universe Tool 세션 | [세션 링크](langfuse_url) |
| Guidance Router 세션 | [세션 링크](langfuse_url) |
| Main Router 세션 | [세션 링크](langfuse_url) |
| 평가 데이터 | YYMMDD_평가결과 |
```

## 처리 절차

1. **데이터 수집**: 각 `eval_*_app/aggregation.json` 파일 읽기
2. **run_id 추출**: 각 `eval_*_app/run_1/eval_result.json`에서 세션 ID 추출
3. **이상치 추출**: `per_sample` 배열 순회하며 기준에 맞는 샘플 추출
4. **마크다운 생성**: 템플릿에 맞춰 리포트 작성 (Langfuse 링크 포함)
5. **파일 저장**: 지정된 경로에 `.md` 파일 저장
