#!/bin/bash
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CLAUDE_DIR="$HOME/.claude"

echo -e "${RED}Claude 설정 제거 스크립트${NC}"
echo "================================"

# 심볼릭 링크 제거
echo ""
echo "심볼릭 링크 제거 중..."

# hooks 링크 제거
if [ -L "$CLAUDE_DIR/hooks" ]; then
    rm "$CLAUDE_DIR/hooks"
    echo -e "  ${GREEN}✓${NC} hooks/ 링크 제거됨"
elif [ -e "$CLAUDE_DIR/hooks" ]; then
    echo -e "  ${YELLOW}hooks/는 심볼릭 링크가 아닙니다. 건너뜁니다.${NC}"
else
    echo "  hooks/ 링크가 존재하지 않습니다."
fi

# settings.json 링크 제거
if [ -L "$CLAUDE_DIR/settings.json" ]; then
    rm "$CLAUDE_DIR/settings.json"
    echo -e "  ${GREEN}✓${NC} settings.json 링크 제거됨"
elif [ -e "$CLAUDE_DIR/settings.json" ]; then
    echo -e "  ${YELLOW}settings.json은 심볼릭 링크가 아닙니다. 건너뜁니다.${NC}"
else
    echo "  settings.json 링크가 존재하지 않습니다."
fi

# .env 링크 제거
if [ -L "$CLAUDE_DIR/.env" ]; then
    rm "$CLAUDE_DIR/.env"
    echo -e "  ${GREEN}✓${NC} .env 링크 제거됨"
elif [ -e "$CLAUDE_DIR/.env" ]; then
    echo -e "  ${YELLOW}.env는 심볼릭 링크가 아닙니다. 건너뜁니다.${NC}"
else
    echo "  .env 링크가 존재하지 않습니다."
fi

# skills 링크 제거
if [ -L "$CLAUDE_DIR/skills" ]; then
    rm "$CLAUDE_DIR/skills"
    echo -e "  ${GREEN}✓${NC} skills/ 링크 제거됨"
elif [ -e "$CLAUDE_DIR/skills" ]; then
    echo -e "  ${YELLOW}skills/는 심볼릭 링크가 아닙니다. 건너뜁니다.${NC}"
else
    echo "  skills/ 링크가 존재하지 않습니다."
fi

# 백업 파일 복원
echo ""
echo "백업 파일 확인 중..."

restore_latest_backup() {
    local target_name="$1"
    local latest_backup=""

    # 가장 최근 백업 찾기
    latest_backup=$(find "$CLAUDE_DIR" -maxdepth 1 -name "${target_name}.backup.*" 2>/dev/null | sort -r | head -1)

    if [ -n "$latest_backup" ] && [ -e "$latest_backup" ]; then
        echo -e "  ${YELLOW}$target_name 복원: $(basename "$latest_backup")${NC}"
        mv "$latest_backup" "$CLAUDE_DIR/$target_name"
        echo -e "  ${GREEN}✓${NC} $target_name 복원 완료"
        return 0
    fi
    return 1
}

# hooks 복원
if [ ! -e "$CLAUDE_DIR/hooks" ]; then
    if ! restore_latest_backup "hooks"; then
        echo "  hooks 백업 파일이 없습니다."
    fi
fi

# settings.json 복원
if [ ! -e "$CLAUDE_DIR/settings.json" ]; then
    if ! restore_latest_backup "settings.json"; then
        echo "  settings.json 백업 파일이 없습니다."
    fi
fi

# .env 복원
if [ ! -e "$CLAUDE_DIR/.env" ]; then
    if ! restore_latest_backup ".env"; then
        echo "  .env 백업 파일이 없습니다."
    fi
fi

# skills 복원
if [ ! -e "$CLAUDE_DIR/skills" ]; then
    if ! restore_latest_backup "skills"; then
        echo "  skills 백업 파일이 없습니다."
    fi
fi

# 완료 메시지
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}제거가 완료되었습니다!${NC}"
echo ""

# 남은 백업 파일 안내
BACKUP_COUNT=$(find "$CLAUDE_DIR" -maxdepth 1 -name "*.backup.*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$BACKUP_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}남은 백업 파일들:${NC}"
    find "$CLAUDE_DIR" -maxdepth 1 -name "*.backup.*" -exec basename {} \;
    echo ""
    echo "수동으로 삭제하려면:"
    echo "  rm ~/.claude/*.backup.*"
    echo ""
fi
