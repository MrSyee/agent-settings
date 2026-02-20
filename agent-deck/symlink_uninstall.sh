#!/bin/bash
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

AGENT_DECK_DIR="$HOME/.agent-deck"

echo -e "${RED}Agent Deck 설정 제거 스크립트${NC}"
echo "================================"

# 심볼릭 링크 제거
echo ""
echo "심볼릭 링크 제거 중..."

if [ -L "$AGENT_DECK_DIR/config.toml" ]; then
    rm "$AGENT_DECK_DIR/config.toml"
    echo -e "  ${GREEN}✓${NC} config.toml 링크 제거됨"
elif [ -e "$AGENT_DECK_DIR/config.toml" ]; then
    echo -e "  ${YELLOW}config.toml은 심볼릭 링크가 아닙니다. 건너뜁니다.${NC}"
else
    echo "  config.toml 링크가 존재하지 않습니다."
fi

# 백업 파일 복원
echo ""
echo "백업 파일 확인 중..."

restore_latest_backup() {
    local target_name="$1"
    local latest_backup=""

    latest_backup=$(find "$AGENT_DECK_DIR" -maxdepth 1 -name "${target_name}.backup.*" 2>/dev/null | sort -r | head -1)

    if [ -n "$latest_backup" ] && [ -e "$latest_backup" ]; then
        echo -e "  ${YELLOW}$target_name 복원: $(basename "$latest_backup")${NC}"
        mv "$latest_backup" "$AGENT_DECK_DIR/$target_name"
        echo -e "  ${GREEN}✓${NC} $target_name 복원 완료"
        return 0
    fi
    return 1
}

if [ ! -e "$AGENT_DECK_DIR/config.toml" ]; then
    if ! restore_latest_backup "config.toml"; then
        echo "  config.toml 백업 파일이 없습니다."
    fi
fi

# 완료 메시지
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}제거가 완료되었습니다!${NC}"
echo ""

# 남은 백업 파일 안내
BACKUP_COUNT=$(find "$AGENT_DECK_DIR" -maxdepth 1 -name "*.backup.*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$BACKUP_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}남은 백업 파일들:${NC}"
    find "$AGENT_DECK_DIR" -maxdepth 1 -name "*.backup.*" -exec basename {} \;
    echo ""
    echo "수동으로 삭제하려면:"
    echo "  rm ~/.agent-deck/*.backup.*"
    echo ""
fi
