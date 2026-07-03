---
status: draft
---

# 개발방향: auto-flow

> **For agentic workers:** This document is the technical spec for `auto-flow` — 4 신규 auto-* skill + 4 신규 slash command + CLAUDE.md 결합 메모. Anchored to `auto-flow-requirements.md` (PRD D1~D12). NEXT STEP: invoke `writing-plans` to produce `auto-flow-implementation-plan.md`.

> ℹ️ **Adaptive 7-topic 적용**: 활성 1/2/5/6/7 / 비활성 3/4 (DB/API 무관 — meta workflow).

## 1. 아키텍처 개요

### 전체 구조

```
[사용자]
   │
   │ /auto-brainstorm <피처명>   /auto-design   /auto-write-plan   /auto-execute-plan
   ▼                              ▼              ▼                  ▼
[메인 에이전트]
   │
   ├─ Skill tool invoke ──────────┐
   │                              ▼
   │                     [auto-* skill 본문]
   │                          │
   │                          ├─ 게이트 발화 X (자동 yes)
   │                          ├─ Socratic clarifying Q (auto-brainstorming만)
   │                          ├─ AI 자동 결정 (alternatives → recommendation pick)
   │                          ├─ docs-pretty / verifying-spec / change-history 자동 호출
   │                          └─ skill 전환 직전 1줄 notice + transition (D7)
   │
   └─ 끝 (= 다음 auto-* skill auto-invoke 또는 finishing 자동)
```

### Layer

- **Layer 1 — slash command** (`commands/auto-*.md` 4개): 사용자 entry point, 인자 optional + latest <slug> 추론, 대응 auto-* skill invoke 안내
- **Layer 2 — auto-* skill 본문** (`skills/auto-*/SKILL.md` 4개): 핵심 자동 로직 보유. 게이트 자동 yes / clarifying Q only (auto-brainstorming) / verify 보고서 노출 후 auto-chain
- **Layer 3 — 결합 메모** (`CLAUDE.md`): auto-* ↔ 기존 4 skill 의 기능 mirror 관계 + Gate #14 override 명시 + skill body 변경 atomic 유지 룰

### 패턴 — og-* mirror 와 유사

기존 og-* (og-brainstorming / og-writing-plans / og-executing-plans) 가 upstream-original 본문을 mirror 한 패턴과 동일. auto-* 도 본 4 skill 의 핵심 로직 재현 + auto behavior 차이만 분기. 본 4 skill 본문 변경 0 (PRD D8).

## 2. 영향 받는 컴포넌트/파일

### 신규 (8 파일)

| 경로 | 역할 |
|---|---|
| `skills/auto-brainstorming/SKILL.md` | Socratic clarifying Q + AI 자동 approach 선택 + section 자동 작성 + transition |
| `skills/auto-designing-direction/SKILL.md` | adaptive 7-topic 자동 판정 + design decision 자동 + verifying-spec 노출 + transition |
| `skills/auto-writing-plans/SKILL.md` | task 자동 분해 + Model 힌트 자동 + RISK §2 자동 + verify + code-pretty + docs-pretty + transition |
| `skills/auto-executing-plans/SKILL.md` | DAG 분석 + 무조건 wave-parallel subagent + failure isolation + finishing |
| `commands/auto-brainstorm.md` | slash entry — auto-brainstorming invoke |
| `commands/auto-design.md` | slash entry — auto-designing-direction invoke |
| `commands/auto-write-plan.md` | slash entry — auto-writing-plans invoke |
| `commands/auto-execute-plan.md` | slash entry — auto-executing-plans invoke |

### 수정 (1 파일)

- `CLAUDE.md` — `## auto-flow ↔ 기존 4 skill mirror 결합` 섹션 추가 (D8 약속 + Gate #14 override 명시 + atomic 변경 룰)

### 변경 0 (확인용)

- `skills/brainstorming/SKILL.md` (556 lines) — 변경 X
- `skills/designing-direction/SKILL.md` (329 lines) — 변경 X
- `skills/writing-plans/SKILL.md` (400 lines) — 변경 X
- `skills/executing-plans/SKILL.md` (285 lines) — 변경 X
- `skills/og-*` 3종 — 변경 X
- `skills/finishing-a-development-branch/SKILL.md` — 변경 X (auto-executing-plans 가 호출)
- `skills/docs-pretty/SKILL.md` / `code-pretty/SKILL.md` / `verifying-spec/SKILL.md` / `change-history/SKILL.md` / `risk-annotation/SKILL.md` — 변경 X (auto-* 가 caller 로 호출)
- `scripts/preflight.py` / `scripts/dag_builder.py` / `scripts/changelog_buffer.py` — 변경 X
- 기존 9 slash command (`/brainstorm` 등) — 변경 X

## 3. 데이터 모델/스키마 변경 — N/A: 본 피처는 DB/스키마 무관 (skill 본문 + slash command 추가)

## 4. 외부 인터페이스 — N/A: API/event 노출 없음 (skill 내부 + Skill tool 호출 chain)

## 5. 핵심 결정 + 대안 비교

PRD D1~D12 가 상위 결정. tech-design 은 그 위의 implementation-level 결정.

### D-T1. auto-* skill 본문 = self-contained mirror (D8 강제)

**선택**: og-* 와 동일 패턴. auto-* 가 핵심 process 본문 직접 보유 (clarifying Q, AI 자동 선택, transition notice 등). 기존 4 skill 본문 호출 X.

**대안 1**: 기존 4 skill 본문 invoke + auto context flag 전달 → 기존 본문에 if-auto 분기 추가. **거부**: PRD D8 ("기존 4 skill 변경 0") 위배.

**대안 2**: auto-* 가 기존 4 skill 을 Skill tool 로 invoke + 메인이 게이트 응답 자동 yes 가로채기. **거부**: 게이트 노출 자체가 사용자 마찰. AskUserQuestion 호출 후 메인이 응답하는 패턴 = 사용자에게 잠깐 노출됨. auto-flow 의도 흐려짐.

**이유**: og-* 패턴 검증된 mirror 전략 + DRY 일부 손실 수용 (4 skill mirror 비용 < 명료성 + 안전성 이득).

### D-T2. clarifying Q 횟수 — auto-brainstorming 의 사용자 입력 분량

**선택**: AI 가 적응적 판단 — 1~5개 사이. 첫 답변 + slug 으로 충분히 추론 가능하면 1개로 끝. 모호하면 최대 5개. 한 번에 1개씩.

**대안 1**: 고정 3개. **거부**: 단순 피처는 1개로 충분, 복잡 피처는 5개로 부족. 적응적 우월.

**대안 2**: 사용자가 처음 입력한 한 줄로 끝, AI 가 모두 추론. **거부**: PRD 명시 "수동으로 할 부분은 요구사항 분석" — 사용자 입력 0 은 PRD 위배.

**이유**: 사용자 의도 불충분 시 false 자동 결정 위험. 적응형이 안전.

### D-T3. AI 자동 alternative 선택 기준

**선택**: 메인 에이전트가 LLM 컨텍스트 이해로 가장 적합한 옵션 1 선택. recommendation reasoning 자동 생성하여 tech-design.md §5 (결정+대안 비교) 에 logged. 사후 사용자가 review 가능.

**대안 1**: 항상 첫 번째 alternative 선택 (deterministic). **거부**: 첫 번째가 항상 최선 아님. 컨텍스트 무시 = spec drift 가능성 높음.

**대안 2**: 사용자에게 큰 결정만 묻기 (architectural choice 정도). **거부**: PRD D2 "auto-design 사용자 입력 0" 위배.

**이유**: AI 자동 선택의 spec drift 위험은 PRD 우려 1 에서 인정됨 + 해결책 (verify 보고서 + change-history 보존 + 사후 change-propagation) 이 PRD 에 명시.

### D-T4. transition notice 대기 시간

**선택**: 즉시 다음 skill invoke. 별도 sleep / wait 없음. 사용자가 "stop" / "멈춰" 입력 = 다음 사용자 메시지로 도착하면 메인이 catch.

**대안 1**: 3초 sleep 후 사용자 입력 없으면 진행. **거부**: harness 에 sleep 패턴 도입 비용 + UX 어색함. Claude Code 의 메시지 모델은 사용자가 답변할 때만 다음 turn 진행 — 메인 turn 안에 sleep X.

**이유**: harness 의 자연스러운 흐름. 사용자가 "stop" 메시지 보내면 메인이 다음 turn 시작 시 catch.

### D-T5. verify 보고서 노출 형식 — 한 줄 요약 vs 4축 풀

**선택**: 4축 풀 보고서 노출 (D11). 사용자가 catch 가능한 정보량 우선. transition notice 직전 메시지에 함께.

**대안 1**: 한 줄 요약 ("verify-spec PASS / 영향 5 컴포넌트") 만. **거부**: 한 줄 요약은 spec drift 가 묻힐 가능성. 4축 풀 보고서는 사용자가 빠르게 스캔 가능.

**대안 2**: 보고서 미노출, change-history 에만 logged. **거부**: 사용자가 mid-flight 으로 catch 안 됨. PRD 우려 1 (spec drift) 의 핵심 mitigation 이 사라짐.

### D-T6. auto-execute-plan 의 Entry Guard

**선택**: 기존 `dj-superkit-subagent-driven-development` 의 Entry Guard 그대로 활용 (`scripts/preflight.subagent_task_entry_check`). plan 존재 + commit_policy=per-task 검사. fail 시 v1.1.15 user-gate 발화 (3 choice 중 "스킵 (이번만)" 선택지 = auto-flow 종료 + 사용자 안내).

**대안 1**: auto- 전용 Entry Guard 신설. **거부**: 코드 중복. 기존 helper 재활용이 옳음.

### D-T7. transition 직후 다음 skill invoke 방법

**선택**: Skill tool 사용 (`Skill(skill="dj-superkit:auto-designing-direction")`). 메인이 직접 invoke.

**대안**: 메인이 사용자에게 "다음 단계 슬래시 명령어 안내" 한 줄 노출 후 사용자가 입력. **거부**: PRD D4 (자동 chain) 위배.

### D-T8. clarifying Q 와 transition notice 의 사용자 응답 구분

**선택**: clarifying Q 응답 (장문 답변 가능) 과 transition notice 응답 ("stop" 키워드 catch) 를 메인이 컨텍스트로 구분. clarifying Q turn 에서는 사용자가 어떤 답변이든 일반 대답으로 해석. transition turn 에서는 "stop"/"멈춰"/"잠깐" 키워드 1개라도 매치 시 인터럽트.

**이유**: harness 모델상 사용자 응답이 어느 turn 에 속하는지 메인이 항상 알고 있음. 별도 input parsing 룰 X.

### D-T9. auto-* slash command 인자 패턴

**선택**: 모두 인자 optional. `<slug>` 누락 시 `docs/features/` 의 가장 최근 (mtime 기준) 폴더 자동 추론.

**대안**: 인자 강제. **거부**: PRD D2 (사용자 입력 0) + auto- 흐름의 마찰 회피와 충돌. `/auto-design` 만 입력해도 작동하는 게 자연스러움.

### D-T10. auto-flow 종료 메시지 — finishing 자동 호출 후

**선택**: finishing-a-development-branch 의 슬림 종료 메시지 (테스트 게이트 + commit list + RISK 카운트 + blocked tasks) 자동 노출. 별도 auto-flow 만의 메시지 X — finishing 이 모든 자동 흐름의 일관 종착점.

**이유**: finishing 자체가 v1.1.14 슬림화 (75줄) + AskUserQuestion 게이트 X 라 auto-flow 와 자연스럽게 결합.

### D-T11. Visual Companion offer 처리 (PRD D12 매핑)

**선택**: auto-brainstorming SKILL.md 본문의 Socratic 흐름에서 Visual Companion offer 단계 자체 미박음. 즉 auto-brainstorming 에는 Visual Companion 개념 자체가 없음.

**대안**: offer 단계는 mirror 박되 자동 skip 분기 추가. **거부**: 코드 dead-path. 본문 변경 0 룰 (D8) 과 정신 일치 — auto-* 본문은 필요 없는 흐름 자체를 안 박는다.

**이유**: PRD D12 의 "사용자 입력 최소화" 정신을 본문 차원에서 표현.

### D-T12. docs-pretty 호출 분기 — auto-flow 에서 SKIP (PRD D9 amend 매핑)

**선택**: 4 auto-* skill 본문 어디에도 docs-pretty 호출 단계 박지 않음. RAW 산출물 그대로 change-history → commit. 일반 4 skill 의 docs-pretty 호출 흐름은 본 4 skill 본문 변경 0 룰 (D8) 로 그대로 유지.

**대안 1**: docs-pretty 호출은 박되, "skip" 인자 추가하여 자동 skip. **거부**: docs-pretty 본문 변경 = 일반 caller 영향. 분기 자체 없는 게 깔끔.

**대안 2**: auto-* 가 docs-pretty 호출하되 dispatch 는 안 함 (no-op). **거부**: 코드 dead-path.

**이유**: PRD D9 amend ("docs-pretty 는 사람이 보기 편함" — auto-flow 는 사용자 review 없으므로 prettify 의미 없음). 일반 흐름 영향 0 보장 — auto-* 본문 안에만 호출 부재.

**테스트**: F8 신규 — `for f in skills/auto-*/SKILL.md; do grep -c "docs-pretty" "$f"; done` → 모두 0.

## 6. 위험 / 사이드이펙트

PRD 우려 6건 + 신규 5건 합쳐 11건. 위험 카테고리: side-effect / breaking / race.

| ID | 위험 | 카테고리 | 위치 | mitigation |
|---|---|---|---|---|
| R1 | AI 자동 design decision 의 spec drift (PRD 우려 1) | side-effect | auto-designing-direction Step 3 (alternatives 자동 선택) | verify 보고서 transition 직전 노출 + change-history entry 보존 + 사후 change-propagation |
| R2 | auto-execute-plan 도중 다수 task fail (PRD 우려 2) | side-effect | auto-executing-plans wave 진행 | end-of-run blocked list 노출 + plan 결함 시 사용자 catch + 수동 모드 fallback |
| R3 | Gate #14 override 룰 위반 (PRD 우려 3) | breaking | auto-executing-plans D5 wave-parallel 강제 | CLAUDE.md 결합 메모 + auto-* 명시적 invoke 시에만 작동 + 일반 `/execute-plan` 영향 0 |
| R4 | docs-pretty / verifying-spec / change-history 호출 시 게이트 자동 처리 (PRD 우려 4) | breaking | auto-* skill 본문 (caller 책임) | auto-* SKILL.md 본문에 "게이트 자동 yes / 보고서만 노출 / 첫 entry 자동 logged" 명시 + 기존 helper skill 본문 변경 X (caller 책임 패턴) |
| R5 | mid-flight 변경 욕구 (PRD 우려 5) | side-effect | skill 전환 시점 | D7 transition notice "stop" + 종료 후 change-propagation |
| R6 | 메인 컨텍스트 폭증 (PRD 우려 6) | side-effect | 4 skill chain | D5 wave-parallel subagent + 산출물 file persist + 메인은 file reference 만 |
| R7 | clarifying Q 횟수 잘못 판단 — AI 가 1개로 끝내고 spec 부족 | side-effect | auto-brainstorming 의 D-T2 적응 판단 | 부족하면 verify-spec 4축 보고서가 catch (consistency 축에서 FR 매핑 누락 신호) |
| R8 | auto-* slash command 인자 latest <slug> 추론 false positive — 다른 작업 진행 중인 폴더로 진입 | breaking | auto-designing-direction / writing-plans / executing-plans 의 D-T9 | 진입 시 추론된 <slug> 1줄 노출 ("⚙️ <slug> 자동 선택. 다른 폴더면 'stop' 후 인자 명시") |
| R9 | failure isolation 후 commit 된 부분 코드의 의미 불완전 — auto-flow 종료 후 사용자가 catch 안 하면 mainline 에 이상 상태 | side-effect | auto-executing-plans (D6) | finishing 종료 메시지에 blocked list + 미해결 신호 명확화 + 사용자 직접 push 정책 (직 push 금지) |
| R10 | Skill tool invoke chain 도중 1 단계 실패 — chain 전체 멈춤? 부분 commit 잔존? | breaking | 4 skill chain 모두 | 각 skill 의 끝에서 산출물 commit 시도 + 실패 시 working tree 변경 그대로 두고 사용자 안내 (D7 transition notice 안 발화) |
| R11 | 메인 에이전트가 "stop" 키워드 catch 실패 — 사용자가 "잠깐 이거 멈춰" 라 입력했는데 일반 대답으로 해석 | side-effect | D-T8 transition turn 처리 | "stop"/"멈춰"/"잠깐" 외에도 "중단"/"abort"/"취소"/"어 잠시만" 등 broad pattern catch + 모호 시 메인이 한 번 더 명시 확인 ("⚠️ 인터럽트 의도? yes/no") |

## 7. 테스트 전략

### 정적 검증 (F-시리즈)

- **F1**: `commands/auto-*.md` 4 파일 존재 + 각 파일 description 에 "auto" + invoke target skill 명시
- **F2**: `skills/auto-*/SKILL.md` 4 파일 존재 + 각 frontmatter description 명시
- **F3**: 기존 4 skill (`skills/{brainstorming,designing-direction,writing-plans,executing-plans}/SKILL.md`) byte-equal 변경 0 (`git diff HEAD -- ...` empty)
- **F4**: og-* 3 skill byte-equal 변경 0
- **F5**: CLAUDE.md 신규 섹션 (`## auto-flow ↔ 기존 4 skill mirror 결합`) 추가 + Gate #14 override 명시 매치 ≥ 2
- **F6**: 4 auto-* skill 본문에 "AskUserQuestion" 호출 패턴 0 (게이트 자동 yes 검증)
- **F7**: 4 auto-* skill 본문에 transition notice 형식 (`Auto-proceeding to`) 매치 ≥ 4 (auto-brainstorming/designing-direction/writing-plans 끝 + auto-executing-plans 끝의 finishing transition)

### dogfood 시나리오 (H-시리즈)

기존 G1~G8 + H1~H6 색인에 H7~H10 추가:

- **H7**: `/auto-brainstorm <small 피처>` — 1 clarifying Q + AI 자동 진행 + 4 단계 chain 끝 + commits N. 입력: small 메타 피처
- **H8**: `/auto-design` (이미 PRD 있음) — design 부터 chain 끝까지. latest <slug> 추론
- **H9**: 사용자가 transition notice 직후 "stop" 입력 → cleanly exit + 다음 단계 수동 호출 안내
- **H10**: auto-execute-plan 도중 1 task BLOCKED → failure isolation + 다음 wave 진행 + finishing 에서 blocked list 노출

### unit test

- D-T8 의 "stop" pattern catch 룰 — Python helper `scripts/auto_flow.parse_interrupt(text) -> bool` 신규 + 테스트 (10+ 케이스)
- D-T9 의 latest <slug> 추론 — `scripts/auto_flow.find_latest_slug(features_dir: Path) -> str` 신규 + 테스트 (5+ 케이스)

### 통합 검증

- pytest 전체 — 기존 36 + 신규 ~15 = 51+ PASS

---
## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-10 19:30] [개발방향-수정]
- **id**: CH-20260510-003
- **이유**: 신규 기술 설계 (PRD D1~D12 → tech-design D-T1~D-T12 매핑 + 영향 컴포넌트 9 + 위험 R1~R11 + 테스트 F1~F8 + H7~H10 + 2 unit test)
- **무엇이**: auto-flow-tech-design.md 전체 (§1 아키텍처 / §2 영향 / §3 §4 N/A / §5 결정+대안 / §6 위험 / §7 테스트)
- **영향범위**: 없음 (최초 생성)
- **연관 항목**: CH-20260510-001 (PRD initial), CH-20260510-002 (PRD D9 amend)

### [2026-05-10 19:35] [개발방향-수정]
- **id**: CH-20260510-004
- **이유**: PRD D9 amend (docs-pretty 호출 제거, auto-flow 한정) cascading
- **무엇이**: D-T12 신규 추가 (auto-* skill 본문 docs-pretty 호출 부재 명시), §7 F8 테스트 신규 추가 (auto-* 본문 docs-pretty grep 0 검증)
- **영향범위**: implementation-plan.md (다음 단계, F8 테스트 항목 plan task 에 반영 필요)
- **연관 항목**: CH-20260510-002 (PRD D9 amend)
