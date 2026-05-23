---
name: auto-brainstorming
description: auto-flow 진입점 — Socratic clarifying Q (1~5개 적응) + AI 자동 approach 선택 + 자동 section 작성 + change-history 자동 + auto-designing-direction 자동 invoke. 사용자 입력은 clarifying Q 답변에만. AskUserQuestion / Visual Companion / generating-html 호출 X.
---

# Auto Brainstorming → <slug>-requirements.md (Socratic auto)

js-super:auto-brainstorming 은 명시적 사용자 invoke (`/auto-brainstorm <피처명>`) 시에만 작동. PRD `auto-flow-requirements.md` D1~D12 (D9 amend) + tech-design D-T1~D-T12 의 자동 흐름 본문.

**Announce at start:** "auto-brainstorming skill 로 자동 진행하겠습니다 (Socratic clarifying Q + AI 자동 chain)."

## 사용자 질문 룰 (v2.0.3+) — 항상 AskUserQuestion

이 skill 흐름 안에서 사용자에게 질문할 일이 생기면 **반드시** `AskUserQuestion`
도구로 호출한다. 산문으로 "~ 할까요?" 한 줄 던지지 마라.

### Why

Notification 훅 (`elicitation_dialog` 매처) 이 알람을 발화하려면 도구 호출이
실제로 일어나야 함. 산문 질문은 훅이 못 잡아서 사용자가 놓침 (v1.1.8 신고 재발).

### How to apply

- clarifying / Socratic / 모호점 확인 / 게이트 / 모드 선택 — 모두 포함
- 단답 yes/no 도 prose X → `AskUserQuestion` choices `[yes, no]` 사용
- 다중 선택은 enum choices 또는 multi-question batching (의미 결합 시 max 4 questions[])
- **Socratic 자유 응답**: AskUserQuestion 의 question 본문에 "자유롭게 답해주세요. 별도 옵션 선택 불필요" + dummy choice `[알겠음]` 1개 → 트리거만 발화, 응답은 다음 turn prose
- **예외**: 본문 자체의 알람-friendly 안내문 (`ℹ️ Auto-proceeding ...`) 는 질문 아니라 안내 — 도구 호출 불필요

### Other / 모호 응답 처리 (v2.1.1+)

사용자가 "Other" 자유 응답 또는 "모르겠음 / 이해 안 됨" 류 답변 catch 시 → **그 질문만 단독 재호출 + prose 설명 추가**. 다음 단계 자동 진행 X (anchor 질문 강제 X 룰은 명확 yes/no 답변에만 적용).

### 예외 — `--no-ask` 플래그 (v2.5+)

사용자가 슬래시 명령에 `--no-ask` 토큰을 **명시** 한 경우에만 진입. 메인 자체 판단으로 활성화 X.

- 모든 사용자 질문을 prose (메인 turn 자유 텍스트) 로 처리
- `AskUserQuestion` 도구 호출 **0 보장**
- 게이트 자체는 살아 있음 — 사용자 prose 응답 기다림
- 알람 fire X (사용자가 명시 invoke 했으니 인지 가정)

#### skill 진입 시 1회 boilerplate

skill 진입 직후 다음 한 줄을 prose 로 출력:

> ℹ️ `--no-ask` 모드 진입 — AskUserQuestion 도구 호출 X, 응답 알람 X. 백그라운드 작업 중이면 응답 시점을 직접 체크해주세요.

#### 위험 명령 진입 직전 보강

critical 7 케이스 (파일 삭제 / `git push --force` / DB migration / mass commit / 외부 메시지 등) 실행 직전에는 다음 한 줄을 prose 로 출력:

> ⚠️ 위험 명령 진입 — 응답 기다림. 백그라운드 작업 중이면 직접 catch 해주세요.

`⚠️` 마커 + 별도 줄로 일반 prose 보다 두드러지게.

#### auto-* 4 skill 추가 룰

내부 escalation 경로 (BLOCKED 자가복구 실패 / critical 7 재질문 / Other 모호 응답 재질문) 에서도 `AskUserQuestion` 호출 **0 보장**. clarifying Q 자체는 그대로 prose 유지.

## Process

### Step 1 — Slug 추론 + 폴더 생성

`/auto-brainstorm <피처명>` 인자 → slug (공백 → 하이픈). 인자 누락 시 메인이 한 줄 묻고 진행.

```bash
mkdir -p docs/features/$(date +%Y-%m-%d)-<slug>/
```

### Step 2 — Socratic clarifying questions (1~5개 적응)

메인 에이전트가 사용자 첫 입력 + slug 으로 첫 질문 던짐. 한 번에 1개. 답변 충분히 명확하면 1개로 끝, 모호하면 최대 5개 (D-T2).

질문 패턴:
- 핵심 user story 한 줄?
- 가장 중요한 acceptance criterion?
- (필요 시) 명시적 범위 밖?
- (필요 시) 외부 의존성?
- (필요 시) 사용자가 우려하는 위험?

→ 사용자 답변 = 본 흐름의 유일한 사용자 입력 지점.

### Step 3 — AI 자동 approach 선택

메인이 2-3 approach + tradeoffs 자체 추론, recommendation 1개 자동 선택. 사용자에게 노출 X. 선택 reasoning 은 산출물 §핵심 결정 에 logged.

### Step 4 — 산출물 자동 작성

`<slug>-requirements.md` 작성 (Socratic free-form):
- H1 + Mode line + 배경 + 핵심 결정 + 우려/해결 + 다음 단계 + 변경이력 footer
- RAW 본문 그대로.

### Step 4.5 — generating-html fire-and-forget dispatch (v2.3.2+)

`<slug>-requirements.md` 작성 직후, **change-history 자동 entry 박히기 전** (footer 아직 비어있는 시점) 에 `generating-html` skill fire-and-forget dispatch:

- `run_in_background: true` (fire-and-forget, 메인 latency 거의 0)
- target: `<slug>-requirements.md`
- 메인은 결과 wait X — 다음 Step 즉시 진행

**왜 v2.3.2+ 도입**: v1.1.17 PRD D9 amend ("auto-flow 는 review 없으므로 prettify 의미 없음") 는 잘못된 가정. transition notice 시점에 사용자가 `.html` 검토 가능 (Type "stop" 으로 abort). v2.3.1 dogfood 에서 사용자 명시 catch — auto-flow 에서도 `.html` 동봉본 필요.

**v2.4+ race delay**: dispatch 후 **5초 delay** 후에 Step 5 (change-history) 진행. background subagent 가 .md 의 footer 0건 시점에 읽도록 보장 (race condition 해결).

### Step 5 — change-history 자동

`change-history` skill invoke → 첫 `[요구사항-수정]` entry append. CH-id 자동 생성.

### Step 6 — Transition notice + auto-designing-direction invoke

```
ℹ️ /design 단계로 자동 넘어갑니다. 멈추려면 "stop" 입력해주세요.
```

다음 사용자 turn 의 입력에 `parse_interrupt` (scripts/auto_flow.py) 매치 시 cleanly exit + `ℹ️ 알겠습니다. /design 은 나중에 직접 실행해주세요.` 안내. 매치 X 시 즉시 `js-super:auto-designing-direction` skill invoke.

## Anti-Patterns

| Wrong | Right |
|---|---|
| AskUserQuestion 호출 | NEVER. auto-flow 의 사용자 입력은 clarifying Q 답변에만. |
| generating-html 동기 호출 (sync wait) | NEVER. v2.3.2+ — Step 4.5 fire-and-forget dispatch 만. 메인이 결과 wait X. (v1.1.17 의 "호출 부재" 룰은 v2.3.2 에서 반전됨.) |
| Visual Companion offer | NEVER. D-T11. |
| 일반 brainstorming skill body 호출 | NEVER. self-contained mirror (D-T1). |
| transition notice 후 사용자 응답 wait sleep | NEVER. harness 모델은 자동 다음 turn — sleep X. |

## Related Skills

- `auto-designing-direction` — 다음 단계
- `change-history` — 첫 entry append
- `scripts/auto_flow.parse_interrupt` — interrupt 키워드 catch
