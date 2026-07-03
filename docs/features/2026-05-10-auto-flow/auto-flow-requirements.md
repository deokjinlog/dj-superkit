---
status: draft
---

# 요구사항: auto-flow

> **Mode:** Socratic (free-form). Downstream `designing-direction` reads this prose without expecting fixed PRD section IDs.

## 배경

dj-superkit 의 4 단계 spec-driven 워크플로우 (`/brainstorm` → `/design` → `/write-plan` → `/execute-plan`) 는 매 단계마다 사용자 게이트 (모드 선택, 카테고리, 질문 plan 동의, 게이트 #8/#11/#13/#14, "stop" 인터럽트 가능 지점 등) 를 노출. 이는 의도적 — 1인 개발자가 매 단계 sanity check 하고 spec drift 방지.

그러나 사용자가 **이미 핵심 의도를 명확히 가지고 있을 때** (= 본인이 PRD 의 Socratic 답변만 직접 입력하면 나머지는 AI 의 합리적 추천을 신뢰할 수 있을 때) 게이트 매번 응답이 마찰. 특히 mature 한 사용자가 빠르게 prototype 완성 흐름 원할 때 v1.1.9~12 게이트 합리화 트렌드의 자연스러운 연장.

→ **auto-flow** 는 명시적 invoke 시에만 작동하는 자동 흐름. 4 단계 끝까지 chain. 사용자 입력은 `/auto-brainstorm` 의 Socratic clarifying questions 에만.

## 핵심 결정

### D1. 진입 = 사용자 명시 invoke

`/auto-brainstorm <피처명>` / `/auto-design` / `/auto-write-plan` / `/auto-execute-plan` 4 신규 slash command. 일반 `/brainstorm` 등은 영향 0 (기존 흐름 그대로 manual). auto- prefix 는 명시적 사용자 의도 표현.

### D2. 자동 / 수동 경계

| 단계                | 사용자 입력                                                     |
| ------------------- | --------------------------------------------------------------- |
| auto-brainstorm     | Socratic clarifying questions 답변만 (= "요구사항 분석")        |
| auto-design         | 0 (완전 자동 — alternative 비교 / 결정 모두 AI 자동)            |
| auto-write-plan     | 0 (완전 자동 — task 분해 / Model 힌트 / RISK 모두 AI)           |
| auto-execute-plan   | 0 (완전 자동 — wave-parallel subagent 강제)                     |

### D3. 모드 강제 — Socratic only

auto-brainstorm 은 PRD 분기 X. 이유: PRD 모드의 카테고리 미니질문 + question plan 동의 + adaptive 분기 자체가 "사용자가 게이트마다 답하는 흐름". auto-flow 의 목적과 정면 충돌. Socratic 의 자유 탐색 + AI 가 2-3 approach + recommendation 자동 선택 패턴이 auto 와 자연스러움.

### D4. 자동 chain (4 단계 끝까지)

`/auto-brainstorm <피처명>` 1회 호출 → brainstorm 끝 → design 자동 → write-plan 자동 → execute-plan 자동 → finishing 자동. 어느 진입점에서든 (e.g., `/auto-design` 부터) 그 단계 + 이후 단계 끝까지 chain.

### D5. auto-execute-plan = 무조건 wave-parallel subagent

v1.1.12+ "Gate #14 (실행 모드 선택) 자동승인 절대 X" 룰을 auto-flow 가 명시 override. plan 의 task 수 무관 wave-parallel `dj-superkit-subagent-driven-development` 강제. 메인 컨텍스트 절약 + 병렬 효율성 최대화 일관 정책. 작은 plan 의 경우 subagent overhead > inline 인 trade-off 의도적 수용.

### D6. Failure isolation 그대로 (현 v1.1.14 패턴)

auto-execute-plan 도중 spec-reviewer ❌ retry 후 ❌ 또는 implementer BLOCKED 발생 시:

- 격리 task 의 working tree 변경 폐기, manifest 삭제
- 후행 (deps 포함) blocked 마킹, 다음 wave dispatch 제외
- 다른 task 들은 정상 진행 + commit
- end-of-run consolidator 가 blocked task 리스트 노출

→ 즉 **fail 1건 발생해도 auto-flow 자체는 끝까지 진행**. blocked 결과는 마지막 요약에서 사용자가 catch.

이유: v1.1.14 패턴 일관성 + auto-flow 의 자동성 우선. fail 1건마다 멈추면 auto 가치 손실. blocked 가 다수 발생하는 경우는 plan 자체 결함 가능성, 그 시점에서 사용자가 catch 하고 수동 모드로 전환하면 됨.

### D7. mid-flight 인터럽트 — skill 전환 시 1줄 notice

각 skill 전환 (brainstorm → design / design → write-plan / write-plan → execute-plan) 시점에 1줄 notice:

```
ℹ️ Auto-proceeding to /design. Type "stop" to abort.
```

사용자가 "stop"/"멈춰"/"잠깐" 입력 시 cleanly exit + 다음 단계 수동 호출 안내. 그 외 자동 chain 계속. v1.1.9+ brainstorming → designing-direction transition 패턴 그대로 4 곳 모두 적용.

ESC / Ctrl-C 같은 shell-level 인터럽트는 항상 가능 (auto-flow 와 무관 harness 기능).

### D8. 별도 skill 4개 신규 — 기존 skill 변경 0

```
skills/auto-brainstorming/SKILL.md
skills/auto-designing-direction/SKILL.md
skills/auto-writing-plans/SKILL.md
skills/auto-executing-plans/SKILL.md
```

→ 기존 4 skill (brainstorming / designing-direction / writing-plans / executing-plans) 본문은 변경 없음. 비-auto 진입자 (= 일반 사용자) 영향 0. auto-* skill 은 원본 핵심 로직 패턴을 가져오되 게이트 자동 진행 형태.

### D9. change-history / finishing 자동 호출 — docs-pretty 는 SKIP (auto-flow 한정)

- **docs-pretty: 호출 X** — auto-flow 흐름에서는 사용자가 mid-flight 으로 산출물 review 안 함 (D2: 사용자 입력 0). prettify 는 "사람이 보기 편함" 이 목적 — review 없는 흐름에서 의미 X. 산출물은 RAW 본문 그대로 commit + change-history. 사후 사용자가 git log / diff 로 review 가능 (markdown 자체 가독성은 RAW 도 충분).
- change-history: 첫 entry 자동 logged
- finishing-a-development-branch: 끝에 자동 호출 (테스트 게이트 + 종료 메시지 — slim 75줄 유지)

**일반 흐름 영향 0**: 일반 `/brainstorm` 등은 v1.1.15+ pre-review per-draft 패턴 그대로 (docs-pretty 호출 유지). docs-pretty SKIP 은 auto-* skill 본문에서만 분기.

### D10. AskUserQuestion 게이트 자동 yes 처리

기존 4 skill 의 게이트 (`Gate #8 prettified 산출물 승인` / `Gate #11 verifying-spec 결과 + tech-design 승인` / `Gate #13 plan + verify 승인` / `Gate #14 실행 모드 선택`) 모두 auto- skill 에서는 **자동 yes (또는 D5 의 wave-parallel subagent)** 처리. AskUserQuestion 호출 자체 안 함.

이유: 사용자가 명시적 auto-flow invoke = 모든 게이트 사전 승인 의도. 매번 AskUserQuestion 발화 시 auto-flow 의미 손실.

### D11. verifying-spec 자동 통과 — 단, 보고서는 transition notice 직전 노출

verifying-spec 4축 보고서 (consistency / impact analysis 등) 는 정상 생성. **메인이 다음 skill 전환 직전의 1줄 notice (D7) 위에 보고서 본문을 그대로 노출** — 사용자가 catch 가능한 위치. 단 yes/no 게이트는 발화 X.

```
🔍 verifying-spec 결과:
   - A1 consistency: ✅
   - A2 ...
   - C1 impact: ⚠️ 영향 컴포넌트 5개
   - C2 ...

ℹ️ Auto-proceeding to /write-plan. Type "stop" to abort.
```

이유: spec drift 검출 자체는 가치가 큼 (자동 흐름 안에서 누락 발견 가능). 노출은 하되 게이트 미발화 — 사용자가 catch 하면 stop, 아니면 자동 chain.

### D12. Visual Companion offer skip

auto-* skill 은 사용자 입력 최소화 의도. Visual Companion offer 는 명시적 사용자 동의 필요한 단계 → auto-flow 와 충돌. 자동 skip.

## Slash Command 매핑

| Slash command                  | 진입 skill                  | Chain 시작점                                              |
| ------------------------------ | --------------------------- | --------------------------------------------------------- |
| `/auto-brainstorm <피처명>`    | `auto-brainstorming`        | brainstorm                                                |
| `/auto-design`                 | `auto-designing-direction`  | design (latest <slug> 추론)                               |
| `/auto-write-plan`             | `auto-writing-plans`        | write-plan (latest <slug> 추론)                           |
| `/auto-execute-plan`           | `auto-executing-plans`      | execute-plan (latest <slug>-implementation-plan.md 추론)  |

각 진입점에서 chain 끝까지 자동 진행.

`<slug>` 인자 optional — 비어 있으면 `docs/features/` 의 가장 최근 폴더 자동 선택. 사용자가 명시하면 명시 우선.

## 인터랙션 흐름

```
사용자: /auto-brainstorm 사용자 잔액 출금

[auto-brainstorming skill 진입]
1. 피처명/슬러그 자동 추론 (= "사용자-잔액-출금" 또는 "balance-withdraw")
2. 폴더 생성
3. Socratic clarifying question 1: "이 피처의 핵심 user story 한 줄?"
   사용자: <답변>
4. Socratic clarifying question 2: ...
   ...
   (사용자 입력은 여기 까지)
5. AI 가 2-3 approach 자동 제안 → recommendation 자동 선택
6. AI 가 section-by-section 자동 작성 (사용자 승인 없이)
7. self-review 자동
8. docs-pretty 자동 호출
9. change-history 첫 entry 자동 logged
10. ℹ️ Auto-proceeding to /design. Type "stop" to abort.
    (3초 대기 또는 사용자 입력 없으면 auto)

[auto-designing-direction 진입]
11. requirements.md 읽기, adaptive 7-topic 자동 판정 + announce
12. AI 가 design decision 들 자동 선택 (alternatives 비교 후 가장 적합한 옵션 1 선택)
13. tech-design.md 자동 작성
14. verifying-spec 자동 실행 + 4축 보고서 생성 (logged, 게이트 X)
15. docs-pretty 자동 호출
16. change-history 자동
17. ℹ️ Auto-proceeding to /write-plan. Type "stop" to abort.

[auto-writing-plans 진입]
18. requirements + tech-design 읽기
19. AI 가 task 분해 자동 (TDD bite-sized + Model hint 자동 결정)
20. RISK 코드 지점 §2 자동 추론
21. implementation-plan.md 자동 작성
22. verifying-spec + code-pretty + docs-pretty 자동
23. change-history 자동
24. ℹ️ Auto-proceeding to /execute-plan (subagent wave-parallel). Type "stop" to abort.

[auto-executing-plans 진입]
25. plan 읽기 + DAG 분석 + wave 자동 build
26. 무조건 dj-superkit-subagent-driven-development 호출 (wave-parallel)
27. 모든 wave 자동 진행 (failure isolation 그대로 — blocked 격리 후 다음 wave 진행)
28. End-of-run consolidator 자동
29. finishing-a-development-branch 자동 호출 (테스트 게이트 + 종료 메시지)
30. ℹ️ ✅ auto-flow 완료. 변경 N commits. blocked tasks: <list 또는 "없음">.
```

## 우려 / 해결

### 우려 1: 자동 결정의 spec drift

AI 가 design decision 자동 선택 시 사용자 의도와 어긋날 가능성. 특히 어려운 architectural choice (monolith vs microservice, sync vs async, Postgres vs MongoDB 등) 의 경우.

**해결:**

- verifying-spec 의 4축 보고서가 logged (게이트 X 라도 보고서 자체는 생성됨)
- change-history entry 가 모든 결정 보존 → 끝에 사용자가 검토 가능
- 큰 trade-off 의도적 수용. 사용자가 마음에 안 드는 결정 발견 시 change-propagation 으로 사후 수정.

### 우려 2: auto-execute-plan 도중 다수 task fail

plan 자체 결함 시 wave-parallel 에서 다수 blocked → 부분 commit + 다수 미구현. 사용자가 끝까지 auto-flow 진행 후 catch.

**해결:**

- end-of-run 요약에 blocked task 리스트 명확 노출
- failure isolation 동작은 v1.1.14 의 검증된 패턴
- blocked 다수 발생 시 사용자가 다음 세션에 수동 모드로 전환 가능 (auto-flow 의 fail 자체가 신호)

### 우려 3: Gate #14 자동승인 절대 X 룰 명시 override

v1.1.12+ 의 사용자 강조 룰을 auto-flow 가 명시 override. 일관성 우려.

**해결:**

- auto-flow 는 사용자 명시 invoke 시에만 작동 = 사용자가 룰 override 명시 동의
- CLAUDE.md 에 "auto-flow override 결합 메모" 추가 — 두 룰의 관계 명시
- 일반 `/execute-plan` 은 영향 0 (게이트 그대로)

### 우려 4: docs-pretty / verifying-spec / change-history skill 들이 auto-flow 에서 어떻게 호출되는가

기존 skill 들은 게이트 (e.g., docs-pretty 의 사용자 리뷰) 를 가정. auto- 에서는 게이트 자동 처리.

**해결:**

- auto-* skill 4 곳 본문에 "메인이 게이트를 어떻게 자동 처리하는지" 명시 (auto yes / skip / log only 분기)
- 기존 docs-pretty / verifying-spec / change-history 본문은 변경 X — 호출자 (auto-* skill) 가 게이트 자동 처리
- "Caller 책임" 패턴 (= caller 에게 게이트 처리 책임 위임) 활용

### 우려 5: 사용자가 auto-flow 진행 도중 변경하고 싶을 때

mid-flight 으로 plan 의 한 task 만 수정하고 싶거나 architecture 결정 바꾸고 싶을 때.

**해결:**

- D7: skill 전환 시 1줄 notice + "stop" break 가능
- "stop" 입력 시 다음 단계 수동 진입 안내
- 또는 auto-flow 종료 후 change-propagation 으로 사후 수정

### 우려 6: 메인 컨텍스트 폭증

auto-flow 가 4 skill chain → 메인 컨텍스트 누적 큼.

**해결:**

- D5: wave-parallel subagent 강제 — 메인은 plan 분석 + git diff + commit 만, 코드 자체는 implementer subagent 가
- 각 단계의 큰 산출물 (requirements / tech-design / implementation-plan) 은 file 로 persist + 메인이 매 단계 끝에서 file 만 reference
- HANDOFF 갱신 패턴 그대로

## 다음 단계

1. `auto-flow-tech-design.md` — 4 신규 skill 의 본문 구조 설계 (auto- prefix + 게이트 자동 처리 boilerplate + 호출 chain). slash command 4 신규 추가. CLAUDE.md 결합 메모 추가.
2. `auto-flow-implementation-plan.md` — TDD task 분해.
3. dogfood: auto-flow 자체로 `/auto-brainstorm` 으로 새 작은 피처 만들어 검증.

---

## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-10 19:00] [요구사항-수정]
- **id**: CH-20260510-001
- **이유**: 신규 피처 brainstorming 결과 (Socratic 모드 — dj-superkit 4 단계 워크플로우의 자동 흐름 4 신규 slash + skill)
- **무엇이**: auto-flow-requirements.md 전체 (배경 / 핵심 결정 D1~D12 / Slash Command 매핑 4 / 인터랙션 흐름 / 우려/해결 6 / 다음 단계 3)
- **영향범위**: 없음 (최초 생성)

### [2026-05-10 19:30] [요구사항-수정]
- **id**: CH-20260510-002
- **이유**: 사용자 mid-flight catch ("프리티독스는 사람이 보기 편함" — auto-flow 는 사용자 review 없으므로 prettify 의미 없음)
- **무엇이**: D9 본문 amend — docs-pretty 호출 제거 (auto-* 한정), 일반 흐름 영향 0 명시
- **영향범위**: auto-flow-tech-design.md (D-T 추가 또는 D-T9/D-T11 영역 갱신 필요)
- **연관 항목**: CH-20260510-001
