# LLM Agent 평가 결과 리포트

## 📊 핵심 지표 요약

### 📝 평가 유형 약어 설명

| 약어 | 전체 명칭 | 설명 |
|------|----------|------|
| GR | Guidance Router | Guidance Agent의 라우팅 평가 |
| RR | Main Router | Main Router의 라우팅 평가 |
| GT | Guidance Tool | Guidance Agent의 Tool 사용 평가 |
| UT | Guidance + Universe Tool | Guidance Agent + Universe Tool 평가 |

### 📈 메트릭 요약

| 평가 유형 | 주요 메트릭 | 평균 점수 |
|----------|------------|----------|
| **RAG** | context_precision | **0.00** |
| **RAG** | context_recall | **0.00** |
| **RAG** | faithfulness | **0.00** |
| **RAG** | deepeval_answer_relevancy | **0.24** |
| **Router (GR)** | routing_accuracy | **0.66** |
| **Router (RR)** | routing_accuracy | **0.97** |
| **Tool (GT)** | tool_call_f1 | **0.58** |
| **Tool (GT)** | agent_goal_accuracy | **0.40** |
| **Tool (GT)** | semantic_tool_call_f1 | **0.58** |
| **Tool (UT)** | tool_call_f1 | **0.14** |
| **Tool (UT)** | agent_goal_accuracy | **0.04** |
| **Tool (UT)** | semantic_tool_call_f1 | **0.14** |

### 🚨 이상치 샘플 요약

| 평가 유형 | 이상치 샘플 ID | 사유 |
|----------|---------------|------|
| RAG | 3, 9, 35, 36, 43, 49 | answer_relevancy = 0.0 |
| RAG | 40 | answer_relevancy = 1.0 (5회 모두 완벽) |
| Router (GR) | 4, 15-25, 44, 45 | routing_accuracy = 0.0 |
| Router (GR) | 13, 26, 27, 35, 49 | 높은 변동성 (std > 0.4) |
| Router (RR) | 15 | routing_accuracy = 0.0 (유일한 실패) |
| Tool (GT) | 1, 4, 5, 6, 10 | agent_goal_accuracy = 0.0 |
| Tool (UT) | 1, 3, 4, 6, 8, 9, 10 | 모든 메트릭 = 0.0 |

---

## 📋 평가 개요

| 항목 | 값 |
|------|-----|
| 평가 일시 | 2026-02-05 |
| Agent | guidance |
| 실행 횟수 | 5 runs |
| 평가 유형 | RAG, Router, Tool |

### 📎 참고 문서

| 문서 형식 | 링크 |
|----------|------|
| Langfuse | - |
| RAG 세션 | [세션 링크](https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3Bf5131e26-f2f5-4673-ab37-2b5271116966) |
| Guidance Tool 세션 | [세션 링크](https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3B69d0c37b-30fa-4a0e-bf07-ac8f93a46e9b) |
| Guidance + Universe Tool 세션 | [세션 링크](https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3B9552e17c-52f1-421b-9200-0a2da94dfb21) |
| Guidance Router 세션 | [세션 링크](https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3Bfd45ecb5-14ce-4068-b792-76052bf0842e) |
| Main Router 세션 | [세션 링크](https://dev-ai-platform-langfuse.lostark-m.net/project/cmkdksy6d00033q07qqhxg1dw/sessions?filter=id%3Bstring%3B%3Bcontains%3B06c847e0-638e-46c2-997b-2cba3356e64d) |
| 평가 데이터 | 260205_평가결과 |

---

## 🔍 상세 결과

### 1. RAG 평가 (eval_rag_app)

#### Summary
| 메트릭 | Mean | Std | Min | Max | Median |
|--------|------|-----|-----|-----|--------|
| context_precision | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| context_recall | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| faithfulness | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 |
| deepeval_answer_relevancy | 0.24 | 0.02 | 0.21 | 0.26 | 0.25 |

#### 이상치 샘플
| Sample ID | answer_relevancy (mean) | std | 비고 |
|-----------|------------------------|-----|------|
| 3, 9, 35, 36, 43, 49 | 0.00 | 0.00 | 5회 모두 0점 |
| 40 | 1.00 | 0.00 | 5회 모두 만점 |
| 22 | 0.27 | 0.39 | 높은 변동성 |
| 19 | 0.47 | 0.34 | 높은 변동성 |

#### 시각화
| Aggregation Summary | Pass@K |
|---------------------|--------|
| ![Aggregation Summary](./eval_rag_app/visualizations/aggregation_summary.png) | ![Pass@K](./eval_rag_app/visualizations/pass_at_k.png) |

| Run Comparison | Sample Variability |
|----------------|-------------------|
| ![Run Comparison](./eval_rag_app/visualizations/run_comparison.png) | ![Sample Variability](./eval_rag_app/visualizations/sample_variability.png) |

---

### 2. Router 평가 - GR (eval_router_gr_app)

#### Summary
| 메트릭 | Mean | Std | Min | Max | Median |
|--------|------|-----|-----|-----|--------|
| routing_accuracy | 0.66 | 0.01 | 0.64 | 0.68 | 0.66 |

#### 이상치 샘플
| Sample ID | routing_accuracy (mean) | std | 비고 |
|-----------|------------------------|-----|------|
| 4, 15-25, 44, 45 | 0.00 | 0.00 | 5회 모두 실패 |
| 13, 49 | 0.20 | 0.40 | 높은 변동성 |
| 26 | 0.60 | 0.49 | 높은 변동성 |
| 27, 35 | 0.40 | 0.49 | 높은 변동성 |

#### 시각화
| Aggregation Summary | Pass@K |
|---------------------|--------|
| ![Aggregation Summary](./eval_router_gr_app/visualizations/aggregation_summary.png) | ![Pass@K](./eval_router_gr_app/visualizations/pass_at_k.png) |

| Run Comparison | Sample Variability |
|----------------|-------------------|
| ![Run Comparison](./eval_router_gr_app/visualizations/run_comparison.png) | ![Sample Variability](./eval_router_gr_app/visualizations/sample_variability.png) |

---

### 3. Router 평가 - RR (eval_router_rr_app)

#### Summary
| 메트릭 | Mean | Std | Min | Max | Median |
|--------|------|-----|-----|-----|--------|
| routing_accuracy | 0.97 | 0.00 | 0.97 | 0.97 | 0.97 |

#### 이상치 샘플
| Sample ID | routing_accuracy (mean) | std | 비고 |
|-----------|------------------------|-----|------|
| 15 | 0.00 | 0.00 | 유일한 실패 케이스 |

#### 시각화
| Aggregation Summary | Pass@K |
|---------------------|--------|
| ![Aggregation Summary](./eval_router_rr_app/visualizations/aggregation_summary.png) | ![Pass@K](./eval_router_rr_app/visualizations/pass_at_k.png) |

| Run Comparison | Sample Variability |
|----------------|-------------------|
| ![Run Comparison](./eval_router_rr_app/visualizations/run_comparison.png) | ![Sample Variability](./eval_router_rr_app/visualizations/sample_variability.png) |

---

### 4. Tool 평가 - GT (eval_tool_gt_app)

#### Summary
| 메트릭 | Mean | Std | Min | Max | Median |
|--------|------|-----|-----|-----|--------|
| tool_call_f1 | 0.58 | 0.03 | 0.52 | 0.60 | 0.60 |
| agent_goal_accuracy | 0.40 | 0.11 | 0.20 | 0.50 | 0.40 |
| semantic_tool_call_f1 | 0.58 | 0.03 | 0.52 | 0.60 | 0.59 |

#### 이상치 샘플
| Sample ID | tool_call_f1 | agent_goal_accuracy | 비고 |
|-----------|--------------|---------------------|------|
| 1, 4, 5, 6, 10 | 0.32~0.46 | 0.00 | 목표 달성 실패 |
| 7 | 0.80 | 1.00 | 우수 |
| 9 | 0.88 | 1.00 | 우수 |

#### 시각화
| Aggregation Summary | Pass@K |
|---------------------|--------|
| ![Aggregation Summary](./eval_tool_gt_app/visualizations/aggregation_summary.png) | ![Pass@K](./eval_tool_gt_app/visualizations/pass_at_k.png) |

| Run Comparison | Sample Variability |
|----------------|-------------------|
| ![Run Comparison](./eval_tool_gt_app/visualizations/run_comparison.png) | ![Sample Variability](./eval_tool_gt_app/visualizations/sample_variability.png) |

---

### 5. Tool 평가 - UT (eval_tool_ut_app)

#### Summary
| 메트릭 | Mean | Std | Min | Max | Median |
|--------|------|-----|-----|-----|--------|
| tool_call_f1 | 0.14 | 0.00 | 0.14 | 0.15 | 0.14 |
| agent_goal_accuracy | 0.04 | 0.05 | 0.00 | 0.10 | 0.00 |
| semantic_tool_call_f1 | 0.14 | 0.00 | 0.14 | 0.15 | 0.14 |

#### 이상치 샘플
| Sample ID | tool_call_f1 | agent_goal_accuracy | 비고 |
|-----------|--------------|---------------------|------|
| 1, 3, 4, 6, 8, 9, 10 | 0.00 | 0.00 | 모든 메트릭 0 |
| 2 | 0.44 | 0.40 | 유일한 목표 달성 케이스 |
| 5, 7 | 0.50 | 0.00 | tool_call만 성공 |

#### 시각화
| Aggregation Summary | Pass@K |
|---------------------|--------|
| ![Aggregation Summary](./eval_tool_ut_app/visualizations/aggregation_summary.png) | ![Pass@K](./eval_tool_ut_app/visualizations/pass_at_k.png) |

| Run Comparison | Sample Variability |
|----------------|-------------------|
| ![Run Comparison](./eval_tool_ut_app/visualizations/run_comparison.png) | ![Sample Variability](./eval_tool_ut_app/visualizations/sample_variability.png) |
