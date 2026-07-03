# dj-superkit — WSL에서 시작하기

superpowers 5.0.7 의 방법론을 계승해 dj-superkit 으로 커스텀한 시작점입니다.
버전은 0.1.0 부터 새로 시작합니다.

## 0. 먼저 바꿔야 할 placeholder (필수)

| 위치 | 바꿀 것 |
|---|---|
| `.claude-plugin/plugin.json` | `DJ` / `YOUR_EMAIL@example.com` / `YOUR_GITHUB_ID` |
| `.claude-plugin/marketplace.json` | 동일 |
| `README.md` | 설치 명령의 `YOUR_GITHUB_ID`, 본문 취향대로 수정 |

일괄 치환:

```bash
grep -rl "YOUR_GITHUB_ID" . | xargs sed -i 's/YOUR_GITHUB_ID/실제아이디/g'
grep -rl "YOUR_EMAIL@example.com" . | xargs sed -i 's/YOUR_EMAIL@example.com/실제이메일/g'
```

## 1. git 초기화 + GitHub 푸시 (WSL)

```bash
cd dj-superkit
git init
git add -A
git commit -m "chore: initialize dj-superkit 0.1.0 (based on superpowers 5.0.7)"

# GitHub 에 dj-superkit 이라는 빈 public 저장소를 먼저 만든 뒤:
git remote add origin git@github.com:실제아이디/dj-superkit.git
git branch -M main
git push -u origin main
```

HTTPS 를 쓰면 `git remote add origin https://github.com/실제아이디/dj-superkit.git`.

## 2. Claude Code 에 설치해서 테스트

```
/plugin marketplace add 실제아이디/dj-superkit
/plugin install dj-superkit@dj-superkit
```

세션 재시작 후 `/brainstorm 테스트` 로 동작 확인.

## 3. 알아둘 것 (기술 부채)

- `.codex/`, `.opencode/`, `docs/README.codex.md` 등의 설치 URL 은 아직
  원작자(obra/superpowers) 저장소를 가리킵니다. 멀티 플랫폼을 지원할 게
  아니면 삭제하고, 지원할 거면 URL 을 본인 저장소로 교체하세요.
- `LICENSE` 는 MIT 조건상 원저작권(Jesse Vincent) 표기를 유지해야 합니다.
  본인 저작 표기를 추가하려면 아래처럼 줄을 덧붙이는 방식을 쓰세요:
  `Copyright (c) 2026 DJ (dj-superkit modifications)`
- 보조 에이전트 스킬명은 `dj-superkit-sub-driven` 으로 통일되어 있습니다
  (내부 참조까지 치환 완료).
- 버전 bump 시 수정할 파일 3개: `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `README.md` 배지.
  (`docs/plugin-update.md` 절차 참고, `scripts/bump-version.sh` 존재)

## 4. 이후 커스텀 아이디어 (자유)

- RISK 주석 마커/카테고리를 본인 규약으로 재정의 (`skills/risk-annotation`)
- 게이트 문구·알람 커스텀 (`skills/brainstorming` 등)
- upstream superpowers 6.x 의 개선(단일 task-reviewer 등) 선별 이식
