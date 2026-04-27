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

# 플래그 파싱
INSTALL_WORK=false
for arg in "$@"; do
    case $arg in
        --work) INSTALL_WORK=true ;;
    esac
done

echo -e "${GREEN}Claude 설정 설치 스크립트${NC}"
echo "================================"
if [ "$INSTALL_WORK" = true ]; then
    echo -e "  모드: ${YELLOW}work 스킬 포함${NC}"
else
    echo "  모드: common 스킬만"
fi

# 1. ~/.claude 디렉토리 확인/생성
if [ ! -d "$CLAUDE_DIR" ]; then
    echo -e "${YELLOW}~/.claude 디렉토리가 없습니다. 생성합니다...${NC}"
    mkdir -p "$CLAUDE_DIR"
fi

# 2. 기존 파일 백업 및 처리
echo ""
echo "기존 파일 처리 중..."

# settings.json — symlink면 제거, 일반 파일이면 유지(merge할 것임)
if [ -L "$CLAUDE_DIR/settings.json" ]; then
    echo "  settings.json 심볼릭 링크 제거 후 재생성합니다."
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

# skills — symlink면 제거, 일반 디렉토리면 유지(추가 복사할 것임)
if [ -L "$CLAUDE_DIR/skills" ]; then
    echo "  skills/ 심볼릭 링크 제거 후 디렉토리로 재생성합니다."
    rm "$CLAUDE_DIR/skills"
fi

# 3. hooks 심볼릭 링크 생성
echo ""
echo "심볼릭 링크 생성 중..."

ln -s "$SCRIPT_DIR/hooks" "$CLAUDE_DIR/hooks"
echo -e "  ${GREEN}✓${NC} hooks/ → $SCRIPT_DIR/hooks"

# 4. settings.json — 기존 파일과 merge, 없으면 복사
echo ""
echo "settings.json 설정 중..."

if [ -f "$CLAUDE_DIR/settings.json" ]; then
    if command -v jq &>/dev/null; then
        echo "  기존 settings.json 발견 → jq로 merge합니다."
        MERGED=$(jq -s '.[0] * .[1]' "$CLAUDE_DIR/settings.json" "$SCRIPT_DIR/settings.json")
        echo "$MERGED" > "$CLAUDE_DIR/settings.json"
        echo -e "  ${GREEN}✓${NC} settings.json merge 완료"
    else
        echo -e "  ${YELLOW}jq가 없습니다. 기존 settings.json을 백업하고 복사합니다.${NC}"
        cp "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.json${BACKUP_SUFFIX}"
        cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
        echo -e "  ${GREEN}✓${NC} settings.json 복사 완료 (백업: settings.json${BACKUP_SUFFIX})"
    fi
else
    cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
    echo -e "  ${GREEN}✓${NC} settings.json 복사 완료"
fi

# 5. skills 복사
echo ""
echo "skills 복사 중..."

rm -rf "$CLAUDE_DIR/skills"
mkdir -p "$CLAUDE_DIR/skills"

# common 스킬 복사 (항상)
if [ -d "$SCRIPT_DIR/skills/common" ]; then
    cp -r "$SCRIPT_DIR/skills/common"/. "$CLAUDE_DIR/skills/"
    COMMON_COUNT=$(ls "$SCRIPT_DIR/skills/common" | wc -l | tr -d ' ')
    echo -e "  ${GREEN}✓${NC} common 스킬 ${COMMON_COUNT}개 복사 완료"
else
    echo -e "  ${YELLOW}skills/common 디렉토리가 없습니다. 건너뜁니다.${NC}"
fi

# work 스킬 복사 (--work 플래그 시)
if [ "$INSTALL_WORK" = true ]; then
    if [ -d "$SCRIPT_DIR/skills/work" ]; then
        cp -r "$SCRIPT_DIR/skills/work"/. "$CLAUDE_DIR/skills/"
        WORK_COUNT=$(ls "$SCRIPT_DIR/skills/work" | wc -l | tr -d ' ')
        echo -e "  ${GREEN}✓${NC} work 스킬 ${WORK_COUNT}개 복사 완료"
    else
        echo -e "  ${YELLOW}skills/work 디렉토리가 없습니다. 건너뜁니다.${NC}"
    fi
fi

# 6. .env.local 파일 설정
echo ""
echo "환경변수 파일 설정 중..."

if [ ! -f "$SCRIPT_DIR/.env.local" ]; then
    echo -e "  ${YELLOW}.env.local이 없습니다. .env.example에서 복사합니다...${NC}"
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env.local"
    echo -e "  ${GREEN}✓${NC} .env.example → .env.local 복사 완료"
else
    echo "  .env.local이 이미 존재합니다."
fi

ln -s "$SCRIPT_DIR/.env.local" "$CLAUDE_DIR/.env"
echo -e "  ${GREEN}✓${NC} ~/.claude/.env → $SCRIPT_DIR/.env.local"

# 7. 실행 권한 설정
chmod +x "$SCRIPT_DIR/hooks/"*.sh 2>/dev/null || true

# 8. 완료 메시지
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
