---
name: airflow-trigger
description: Airflow DAG를 트리거하고 실행 상태를 모니터링합니다. "DAG 트리거해줘", "airflow 실행해줘", "다시 트리거해줘", "DAG 상태 확인해줘", "로그 확인해줘" 같은 요청 시 사용합니다. 사용자가 DAG ID와 request JSON을 함께 제공하거나, 이전 대화에서 사용한 DAG 정보를 재사용할 때도 반드시 이 스킬을 사용하세요.
---

# Airflow Trigger

Airflow DAG를 트리거하고, 태스크 상태를 모니터링하며, 실패 시 로그를 자동 확인하는 스킬.

## 트리거

- "DAG 트리거해줘", "airflow 실행해줘", "다시 트리거해줘"
- "DAG 상태 확인해줘", "태스크 상태 봐줘"
- "로그 확인해줘", "에러 로그 보여줘"
- DAG ID + request JSON과 함께 실행 요청

## 접속 정보

환경변수에서 읽는다. 없으면 사용자에게 질문하여 받는다.

| 환경변수 | 설명 | 기본값 |
|---------|------|-------|
| `AIRFLOW_URL` | Airflow 웹서버 URL | 없음 (필수) |
| `AIRFLOW_USERNAME` | 인증 사용자명 | `admin` |
| `AIRFLOW_PASSWORD` | 인증 비밀번호 | `admin` |

환경변수 확인 방법:
```bash
echo $AIRFLOW_URL
```

환경변수가 설정되어 있지 않으면 사용자에게 AskUserQuestion으로 URL을 물어본다.
username/password는 기본값 `admin/admin`을 사용하되, 인증 실패 시 사용자에게 재확인한다.

## 워크플로우

### Step 1: 인증 (JWT 토큰 획득)

```bash
curl -s --insecure -X POST "{AIRFLOW_URL}/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"{USERNAME}","password":"{PASSWORD}"}'
```

응답에서 `access_token`을 추출한다. 이후 모든 API 호출에 `Authorization: Bearer {token}` 헤더를 사용한다.

토큰은 세션 내에서 재사용한다. `401 Not authenticated` 응답 시 토큰을 재발급한다.

### Step 2: DAG 트리거

```bash
TOKEN=$(curl -s --insecure -X POST "{AIRFLOW_URL}/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"{USERNAME}","password":"{PASSWORD}"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

LOGICAL_DATE=$(python3 -c "from datetime import datetime,timezone;print(datetime.now(timezone.utc).isoformat())")

curl -s --insecure -X POST "{AIRFLOW_URL}/api/v2/dags/{DAG_ID}/dagRuns" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"logical_date":"'$LOGICAL_DATE'","conf":{CONF_JSON}}'
```

주의사항:
- `logical_date`는 사용자가 제공하지 않으면 현재 UTC 시각을 자동 생성한다
- `conf` 필드에 사용자가 제공한 request JSON을 넣는다
- 응답에서 `dag_run_id`와 `state`를 확인하여 사용자에게 알린다

토큰 획득과 DAG 트리거를 하나의 bash 명령으로 체이닝하면 효율적이다.

### Step 3: 상태 모니터링

트리거 후 30초 대기한 뒤 태스크 인스턴스 상태를 확인한다.

```bash
curl -s --insecure \
  "{AIRFLOW_URL}/api/v2/dags/{DAG_ID}/dagRuns/{DAG_RUN_ID}/taskInstances" \
  -H "Authorization: Bearer $TOKEN"
```

dag_run_id에 `+`, `:` 등 특수문자가 포함되므로 반드시 URL 인코딩한다.
- `+` → `%2B`
- `:` → `%3A`

응답에서 각 태스크의 `task_id`와 `state`를 추출하여 표 형태로 출력한다.

```
=== 태스크 상태 ===
  wiki_to_markdown          | success
  create_collection         | success
  notify_slack              | failed     ← 로그 확인 필요
```

**추가 폴링 조건**: running 상태 태스크가 있으면 15초 간격으로 재확인한다. 최대 5분까지 폴링한다.

### Step 4: 실패 태스크 로그 확인

failed 태스크가 있으면 자동으로 로그를 조회한다.

```bash
curl -s --insecure \
  "{AIRFLOW_URL}/api/v2/dags/{DAG_ID}/dagRuns/{DAG_RUN_ID}/taskInstances/{TASK_ID}/logs/1" \
  -H "Authorization: Bearer $TOKEN"
```

로그 응답은 JSON 배열 형태다. 각 항목에서 `event`, `level`, `error_detail` 필드를 확인한다.

로그 필터링:
- `level`이 `error`인 이벤트를 우선 표시
- `Slack`, `Exception`, `Error`, `Failed` 등 키워드 포함된 이벤트 표시
- 전체 로그가 길면 마지막 3000자만 출력

## 출력 형식

트리거부터 결과까지 단계별로 간결하게 출력한다:

```
트리거 완료: dag_run_id=manual__2026-03-17T02:16:42+00:00, state=queued

=== 태스크 상태 (30초 후) ===
  task_a                    | success
  task_b                    | success
  task_c                    | failed

=== task_c 에러 로그 ===
  [error] 에러 메시지 내용...
```

## 재트리거

사용자가 "다시 트리거해줘"라고 하면 이전 대화에서 사용한 DAG_ID와 conf를 그대로 재사용한다.
이전 정보를 찾을 수 없으면 사용자에게 다시 물어본다.

## 에러 처리

| 에러 | 원인 | 대응 |
|------|------|------|
| `401 Not authenticated` | 토큰 만료 | 토큰 재발급 후 재시도 |
| `404 Not Found` | DAG ID 오류 | DAG 목록 조회하여 유사한 DAG 제안 |
| `409 Conflict` | 동일 logical_date 중복 | 새 logical_date로 재시도 |
| `Field required: logical_date` | 필수 필드 누락 | 자동으로 현재 시각 추가 |
