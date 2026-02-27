#!/bin/bash

# 환경변수 파일 로딩
[ -f ~/.claude/.env ] && source ~/.claude/.env

WEBHOOK_URL="${SLACK_WEBHOOK_URL}"

INPUT=$(cat)
EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // "unknown"')

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')
CWD=$(echo "$INPUT" | jq -r '.cwd // ""')
DIR_NAME=$(basename "$CWD" 2>/dev/null || echo "$CWD")

if [ "$EVENT" = "Notification" ]; then
  MESSAGE="Claude Code 알림: 클로드 확인하세요."
elif [ "$EVENT" = "Stop" ]; then
  MESSAGE="<!channel> Claude Code: 응답이 완료되었습니다. [${DIR_NAME}]"
elif [ "$EVENT" = "PermissionRequest" ]; then
  MESSAGE="<!channel> Claude Code: 권한 승인 요청이 있습니다. [${DIR_NAME}] (tool: ${TOOL_NAME}) 확인해주세요."
else
  MESSAGE="Claude Code: ${EVENT}"
fi

curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"text\": \"${MESSAGE}\"}" \
  "$WEBHOOK_URL" > /dev/null 2>&1

exit 0
