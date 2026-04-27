# Claude Code 설정 관리

`~/.claude/` 설정 파일들을 Git으로 관리하는 프로젝트

## 구조

```
claude-user-setting/
├── .env.example     # 환경변수 템플릿
├── .env.local       # 실제 환경변수 (gitignore)
├── hooks/           # Claude Code hooks
│   └── slack-notify.sh
├── settings.json    # Claude Code 설정
├── skills/
│   ├── common/      # 기본 스킬 (항상 설치)
│   └── work/        # 업무용 스킬 (--work 플래그 시 설치)
├── install.sh
└── uninstall.sh
```

## 설치

```bash
# common 스킬만 설치
make install

# work 스킬 포함 설치
./claude-user-setting/install.sh --work
```

설치 후 환경변수 설정:
```bash
vim claude-user-setting/.env.local
```

## 제거

```bash
make uninstall
```

기존 파일이 있었다면 자동으로 백업에서 복원됩니다.

## 설치 확인

```bash
ls -la ~/.claude/hooks ~/.claude/settings.json ~/.claude/.env ~/.claude/skills
```

## 관리되는 파일

| 파일 | 설명 |
|------|------|
| `settings.json` | Claude Code 권한, hooks 설정 |
| `hooks/` | Slack 알림 등 이벤트 훅 |
| `skills/` | Claude Code 스킬 |
| `.env` | 환경변수 (WEBHOOK_URL 등) |
