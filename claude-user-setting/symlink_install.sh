#!/bin/bash
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 스크립트 위치 (claude-setting 디렉토리)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
BACKUP_SUFFIX=".backup.$(date +%Y%m%d_%H%M%S)"

echo -e "${GREEN}Claude 설정 설치 스크립트${NC}"
echo "================================"

# 1. ~/.claude 디렉토리 확인/생성
if [ ! -d "$CLAUDE_DIR" ]; then
    echo -e "${YELLOW}~/.claude 디렉토리가 없습니다. 생성합니다...${NC}"
    mkdir -p "$CLAUDE_DIR"
fi

# 2. 기존 파일 백업
echo ""
echo "기존 파일 백업 중..."

# settings.json 백업
if [ -e "$CLAUDE_DIR/settings.json" ] && [ ! -L "$CLAUDE_DIR/settings.json" ]; then
    echo -e "  ${YELLOW}settings.json 백업 → settings.json${BACKUP_SUFFIX}${NC}"
    mv "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.json${BACKUP_SUFFIX}"
elif [ -L "$CLAUDE_DIR/settings.json" ]; then
    echo "  settings.json은 이미 심볼릭 링크입니다. 제거 후 재생성합니다."
    rm "$CLAUDE_DIR/settings.json"
fi

# .env 백업
if [ -e "$CLAUDE_DIR/.env" ] && [ ! -L "$CLAUDE_DIR/.env" ]; then
    echo -e "  ${YELLOW}.env 백업 → .env${BACKUP_SUFFIX}${NC}"
    mv "$CLAUDE_DIR/.env" "$CLAUDE_DIR/.env${BACKUP_SUFFIX}"
elif [ -L "$CLAUDE_DIR/.env" ]; then
    echo "  .env는 이미 심볼릭 링크입니다. 제거 후 재생성합니다."
    rm "$CLAUDE_DIR/.env"
fi

# hooks 디렉토리 백업
if [ -e "$CLAUDE_DIR/hooks" ] && [ ! -L "$CLAUDE_DIR/hooks" ]; then
    echo -e "  ${YELLOW}hooks/ 백업 → hooks${BACKUP_SUFFIX}${NC}"
    mv "$CLAUDE_DIR/hooks" "$CLAUDE_DIR/hooks${BACKUP_SUFFIX}"
elif [ -L "$CLAUDE_DIR/hooks" ]; then
    echo "  hooks/는 이미 심볼릭 링크입니다. 제거 후 재생성합니다."
    rm "$CLAUDE_DIR/hooks"
fi

# skills 디렉토리 백업
if [ -e "$CLAUDE_DIR/skills" ] && [ ! -L "$CLAUDE_DIR/skills" ]; then
    echo -e "  ${YELLOW}skills/ 백업 → skills${BACKUP_SUFFIX}${NC}"
    mv "$CLAUDE_DIR/skills" "$CLAUDE_DIR/skills${BACKUP_SUFFIX}"
elif [ -L "$CLAUDE_DIR/skills" ]; then
    echo "  skills/는 이미 심볼릭 링크입니다. 제거 후 재생성합니다."
    rm "$CLAUDE_DIR/skills"
fi

# 3. 심볼릭 링크 생성
echo ""
echo "심볼릭 링크 생성 중..."

# hooks 디렉토리 링크
ln -s "$SCRIPT_DIR/hooks" "$CLAUDE_DIR/hooks"
echo -e "  ${GREEN}✓${NC} hooks/ → $SCRIPT_DIR/hooks"

# settings.json 링크
ln -s "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
echo -e "  ${GREEN}✓${NC} settings.json → $SCRIPT_DIR/settings.json"

# skills 디렉토리 링크
ln -s "$SCRIPT_DIR/skills" "$CLAUDE_DIR/skills"
echo -e "  ${GREEN}✓${NC} skills/ → $SCRIPT_DIR/skills"

# 4. .env.local 파일 설정
echo ""
echo "환경변수 파일 설정 중..."

if [ ! -f "$SCRIPT_DIR/.env.local" ]; then
    echo -e "  ${YELLOW}.env.local이 없습니다. .env.example에서 복사합니다...${NC}"
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env.local"
    echo -e "  ${GREEN}✓${NC} .env.example → .env.local 복사 완료"
else
    echo "  .env.local이 이미 존재합니다."
fi

# .env.local을 ~/.claude/.env로 심볼릭 링크
ln -s "$SCRIPT_DIR/.env.local" "$CLAUDE_DIR/.env"
echo -e "  ${GREEN}✓${NC} ~/.claude/.env → $SCRIPT_DIR/.env.local"

# 5. 실행 권한 설정
chmod +x "$SCRIPT_DIR/hooks/"*.sh 2>/dev/null || true

# 6. 완료 메시지
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}설치가 완료되었습니다!${NC}"
echo ""
echo "다음 단계:"
echo -e "  1. ${YELLOW}$SCRIPT_DIR/.env.local${NC} 파일을 편집하여"
echo "     SLACK_WEBHOOK_URL을 설정하세요."
echo ""
echo "  2. 설치 확인:"
echo "     ls -la ~/.claude/hooks ~/.claude/settings.json ~/.claude/.env ~/.claude/skills"
echo ""

# 백업 파일 안내
BACKUP_COUNT=$(find "$CLAUDE_DIR" -maxdepth 1 -name "*.backup.*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$BACKUP_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}백업된 파일이 있습니다:${NC}"
    find "$CLAUDE_DIR" -maxdepth 1 -name "*.backup.*" -exec basename {} \;
    echo ""
fi
