#!/bin/bash
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 스크립트 위치 (agent-deck 디렉토리)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DECK_DIR="$HOME/.agent-deck"
BACKUP_SUFFIX=".backup.$(date +%Y%m%d_%H%M%S)"

echo -e "${GREEN}Agent Deck 설정 설치 스크립트${NC}"
echo "================================"

# 1. ~/.agent-deck 디렉토리 확인/생성
if [ ! -d "$AGENT_DECK_DIR" ]; then
    echo -e "${YELLOW}~/.agent-deck 디렉토리가 없습니다. 생성합니다...${NC}"
    mkdir -p "$AGENT_DECK_DIR"
fi

# 2. 기존 파일 백업
echo ""
echo "기존 파일 백업 중..."

# config.toml 백업
if [ -e "$AGENT_DECK_DIR/config.toml" ] && [ ! -L "$AGENT_DECK_DIR/config.toml" ]; then
    echo -e "  ${YELLOW}config.toml 백업 → config.toml${BACKUP_SUFFIX}${NC}"
    mv "$AGENT_DECK_DIR/config.toml" "$AGENT_DECK_DIR/config.toml${BACKUP_SUFFIX}"
elif [ -L "$AGENT_DECK_DIR/config.toml" ]; then
    echo "  config.toml은 이미 심볼릭 링크입니다. 제거 후 재생성합니다."
    rm "$AGENT_DECK_DIR/config.toml"
fi

# 3. 심볼릭 링크 생성
echo ""
echo "심볼릭 링크 생성 중..."

ln -s "$SCRIPT_DIR/config.toml" "$AGENT_DECK_DIR/config.toml"
echo -e "  ${GREEN}✓${NC} config.toml → $SCRIPT_DIR/config.toml"

# 4. 완료 메시지
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}설치가 완료되었습니다!${NC}"
echo ""
echo "설치 확인:"
echo "  ls -la ~/.agent-deck/config.toml"
echo ""

# 백업 파일 안내
BACKUP_COUNT=$(find "$AGENT_DECK_DIR" -maxdepth 1 -name "*.backup.*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$BACKUP_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}백업된 파일이 있습니다:${NC}"
    find "$AGENT_DECK_DIR" -maxdepth 1 -name "*.backup.*" -exec basename {} \;
    echo ""
fi
