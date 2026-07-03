# 개발방향: v1.1.15 — 브레인스토밍/디자인 흐름 슬림화 (6종 통합)

> **For agentic workers:** This document is the technical spec (architecture, components, decisions, risks, test strategy). It is anchored to `flow-slim-requirements.md` (the PRD) and consumed by `flow-slim-implementation-plan.md` (step-by-step plan). NEXT STEP: invoke `writing-plans` skill (or run `/write-plan`) to produce `flow-slim-implementation-plan.md` from this design. Do NOT include step-by-step implementation tasks here — those belong in the plan.

> **FR-1 spirit dogfood (AC-8):** 활성 토픽 — 1 아키텍처, 2 컴포넌트, 5 결정+대안, 6 위험, 7 테스트 / 비활성 — 3 데이터 모델, 4 외부 인터페이스 (이유: skill 본문 + helper script 변경, DB/API 무관)

> **CH-004 amendment (2026-05-10 16:30):** PRD CH-003 cascade — FR-5 (docs-pretty pre-review timing 통일) + FR-6 (TaskCreate 이름 사용자 친화화) 추가. §2 영향 파일 + §5 D-T10/D-T11 + §6 R9/R10 + §7 F6/F7/H5/H6 추가.

## 1. 아키텍처 개요

본 릴리즈는 **skill 본문 + helper script 변경** 만으로 구성. 신규 모듈 추가 X, 기존 모듈 시그니처 변경 최소화. 4 FR 의 변경 위치를 layered view 로 정리:

```text
Layer 1 — Skill body (Markdown)
  ├─ skills/brainstorming/SKILL.md
  │    ├─ FR-3: Step 0 라우터 (Verify input 직전)
  │    └─ FR-2: Checklist 끝 transition reminder
  ├─ skills/designing-direction/SKILL.md
  │    ├─ FR-1: Step 3 7-topic dialogue → adaptive
  │    ├─ FR-1: Step 2 Survey 슬림 (PRD §2 재활용)
  │    ├─ FR-2: Checklist 9+10 통합 (10 제거)
  │    └─ FR-2: Checklist 끝 transition reminder
  ├─ skills/writing-plans/SKILL.md
  │    └─ FR-2: Checklist 끝 transition reminder
  └─ skills/{docs-pretty,code-pretty,executing-plans,dj-superkit-subagent-driven-development}/SKILL.md
       └─ FR-4: Pre-flight 섹션 통일 boilerplate (exit 1 / exit ≠0,1 분기)

Layer 2 — Helper script (Python)
  └─ scripts/preflight.py
       └─ FR-4: PreflightResult 에 human_reason 필드 추가 (backward compat)

Layer 3 — Coupling memo (CLAUDE.md)
  └─ FR-4 결합 메모 추가 — preflight schema 변경 시 4 skill boilerplate 동시 동기화 룰
```

**상호작용 흐름** (FR-3 라우터 + FR-1 adaptive + FR-2 reminder):

```text
User → /brainstorm OR 자연어 ("…를 만들어")
  ↓
dj-superkit:brainstorming Step 0 (NEW, FR-3)
  ├─ small 신호 감지 → og-brainstorming auto-invoke + notice
  └─ 그 외 → AskUserQuestion 게이트 (og- / dj-superkit)
       ↓ (dj-superkit 선택)
       dj-superkit:brainstorming 본 흐름 (Checklist 1~9)
         └─ Checklist 끝 reminder (FR-2): invoke 직전 모든 task completed
              ↓
              designing-direction Step 0 (announce, FR-1)
                ├─ requirements.md Read → AI 가 활성/비활성 토픽 판정
                └─ 한 줄 노출: "활성: ... / 비활성: ... (이유: ...)"
                     ↓
                     Step 2 Survey (슬림, FR-1) — PRD §2 재활용 + 필요시 grep
                     Step 3 dialogue (활성 토픽만)
                     ...
                     Checklist 9 (통합, FR-2) — gate Q + invoke writing-plans
```

**Pre-flight 게이트 흐름** (FR-4):

```text
4 skill 진입
  ↓
Pre-flight bash one-liner 호출 → scripts/preflight.py
  ↓
exit code 분기:
  0  → 정상 진행 (현재와 동일)
  1  → AskUserQuestion 게이트 (수정/강제진행/스킵)
  ≠0,1 → AskUserQuestion 게이트 (디버깅/스킵) + stderr 노출
```

## 2. 영향 받는 컴포넌트/파일

| FR       | 파일                                                                          | 변경 유형                                                                           |
| -------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| FR-1     | `skills/designing-direction/SKILL.md`                                         | Step 3 dialogue 룰 + Step 2 Survey 룰 + 진입 announce 한 줄 추가                   |
| FR-2     | `skills/brainstorming/SKILL.md`                                               | Checklist 끝 reminder 한 문단 추가                                                  |
| FR-2     | `skills/designing-direction/SKILL.md`                                         | Checklist 끝 reminder + items 9+10 → 9 통합 (10 제거)                              |
| FR-2     | `skills/writing-plans/SKILL.md`                                               | Checklist 끝 reminder 한 문단 추가                                                  |
| FR-3     | `skills/brainstorming/SKILL.md`                                               | Checklist 1번 직전 Step 0 라우터 섹션 추가 + Process Flow 다이어그램 노드 추가      |
| FR-4     | `skills/docs-pretty/SKILL.md`                                                 | Step 1 Pre-flight 섹션 — exit ≠ 0 분기 boilerplate 통일                            |
| FR-4     | `skills/code-pretty/SKILL.md`                                                 | 동일                                                                                |
| FR-4     | `skills/executing-plans/SKILL.md`                                             | 동일 (mode-check 부)                                                                |
| FR-4     | `skills/dj-superkit-subagent-driven-development/SKILL.md`                        | 동일 (Entry Guard 부)                                                               |
| FR-4     | `scripts/preflight.py`                                                        | `PreflightResult` 에 `human_reason: str` 필드 추가 (NamedTuple → 3-field). 기존 호출자 호환 (default value). |
| FR-4     | `scripts/tests/test_preflight.py`                                             | 9 unit test 의 `human_reason` 검증 추가                                             |
| (결합)   | `CLAUDE.md`                                                                   | "FR-4 preflight schema ↔ 4 skill boilerplate" 결합 메모 추가                       |
| (테스트) | `skills/dj-superkit-subagent-driven-development/tests/H1~H6/` (신규)            | dogfood fixture (H1 라우터 small / H2 라우터 ambiguous / H3 adaptive N/A / H4 preflight fail / H5 docs-pretty pre-review / H6 task name friendly) |
| FR-5 | `skills/docs-pretty/SKILL.md` | frontmatter description 갱신 + Trigger timing 섹션 단일화 (모든 doc 타입 pre-review per-draft) + Anti-Trigger 일부 룰 제거 |
| FR-5 | `skills/brainstorming/SKILL.md` | Checklist Step 6 (사용자 리뷰) ↔ Step 7 (docs-pretty) 순서 swap. user-fix 시 re-pretty loop. |
| FR-5 | `skills/designing-direction/SKILL.md` | 동일 swap (combined approval gate ↔ docs-pretty) + per-draft loop 명시 |
| FR-5 | `skills/writing-plans/SKILL.md` | 변경 X (이미 pre-review 패턴). 참조 정렬만. |
| FR-6 | `skills/brainstorming/SKILL.md` | Checklist 본문 한국어 사용자 친화 명칭 rename (e.g. `Invoke change-history skill` → `변경이력 기록`) |
| FR-6 | `skills/designing-direction/SKILL.md` | 동일 rename |
| FR-6 | `skills/writing-plans/SKILL.md` | 동일 rename + Gate #13/#14 표현 사용자화 (`Gate #N — X` → `X`) |
| FR-6 | `skills/executing-plans/SKILL.md` | task 별 명칭 룰 추가 (구현계획서 task 이름 가이드) |
| FR-6 | `skills/finishing-a-development-branch/SKILL.md` | Step 명칭 사용자화 |
| FR-6 | `CLAUDE.md` | "TaskCreate 명칭 룰" 글로벌 가이드 한 줄 추가 — 신규 skill 작성 시 일관 적용 |

**삭제/Out of scope (PRD §5 와 일관)**:

- ~~`scripts/design_topic_classifier.py`~~ — 백로그 제안. AI judgment 로 대체, 신규 작성 X.
- ~~`scripts/tests/test_design_topic_classifier.py`~~ — 동일.

## 3. 데이터 모델/스키마 변경 — N/A: 본 피처는 DB/스키마 무관 (skill 본문 + Python helper 변경)

## 4. 외부 인터페이스 — N/A: API/event 노출 없음 (skill 내부 + 로컬 Python helper)

## 5. 핵심 결정 + 대안 비교

### D-T1 — FR-1 adaptive: AI judgment vs deterministic classifier

**선택**: AI judgment (메인 에이전트가 requirements.md 읽고 판단)

**대안**:

- (a) `scripts/design_topic_classifier.py` — 키워드 hardcode list (백로그 원안)
- (b) AI judgment + 사용자 override 안전망 ✅ **선택**

**이유**: 백로그 자체에서 키워드 미스매칭 위험 인정 ("Postgres" 만 있고 "DB" 없는 경우). v1.1.14 의 DAG 추론처럼 메인 에이전트의 컨텍스트 이해가 deterministic 키워드 매칭보다 정확. 사용자 override 한 줄 노출로 false negative 즉시 catch.

### D-T2 — FR-1 announce 문구 형식: 항상 노출 vs 비활성 있을 때만

**선택**: 항상 노출 (PRD Q1-b 사용자 결정)

**대안**:

- (a) 비활성 토픽 있을 때만 announce — 전부 활성이면 침묵
- (b) 항상 노출 (전부 활성 / 비활성 있음 둘 다) ✅ **선택**

**이유**: white box / override 시점 일관. 사용자가 "어 7개 다 도는구나" 인지 가능. 전부 활성도 announce 비용 한 줄.

### D-T3 — FR-1 Step 2 Survey 슬림: 항상 grep vs PRD §2 재활용

**선택**: PRD §2 재활용 + 결정 트리거 시점만 추가 grep

**대안**:

- (a) 현재 (항상 처음부터 grep/Read) — brainstorming PRD §2 결과 무시
- (b) PRD §2 먼저 Read, 추가 grep 은 tech-design 결정 (아키텍처 / data flow / pattern) 깊이 부족할 때만 ✅ **선택**

**이유**: brainstorming 단계에서 이미 영향 컴포넌트 식별. 메인 토큰 + tool call 절감. 깊이 필요한 부분만 grep 으로 보강.

### D-T4 — FR-2 reminder 위치: Checklist 끝 vs Anti-Patterns 표

**선택**: Checklist 끝 (단일 문단, "If you find yourself skipping ahead" 직후)

**대안**:

- (a) Anti-Patterns 표에 "마지막 task 미마킹" 행 추가
- (b) Checklist 끝 reminder 단일 문단 ✅ **선택**

**이유**: action-trigger 시점 가시성. Anti-Patterns 표는 사후 참조용, Checklist 끝은 invoke 직전 LLM 의 마지막 read. 동일 wording 으로 3 skill 통일.

### D-T5 — FR-2 designing-direction items 9+10 통합 wording

**선택**: backlog 권장 그대로

```markdown
9. **Ask proceed-to-writing-plans gate (v1.1.12+ — restored)** — change-history 직후 사용자에게 명시적 yes/no 게이트. On `yes` → invoke writing-plans via Skill tool. On `no` → exit with notice telling the user to run /write-plan later.
```

**대안**:

- (a) item 10 만 제거하고 9 의 wording 그대로 유지
- (b) item 9 + 10 통합 with 단일 액션 문장 ✅ **선택**

**이유**: 9 는 "ask gate" 만, 10 은 "answer handler" 만 — 두 task 가 사실상 같은 transition 이라 분리 의미 X. 통합으로 TaskCreate 1개 = 잔존 위험 절반.

### D-T6 — FR-3 라우터 위치: skill body Step 0 vs slash command vs CLAUDE.md

**선택**: skills/brainstorming/SKILL.md Step 0 (Checklist 1번 직전)

**대안**:

- (a) `/brainstorm` slash command 정의에 라우터 추가 — 자연어 진입 catch X
- (b) CLAUDE.md global rule — 신뢰성 낮음, 매 세션 LLM 해석 의존
- (c) skill body Step 0 ✅ **선택**

**이유**: dj-superkit:brainstorming 진입 시 1순위로 발화. /brainstorm 과 자연어 진입 모두 동일 path. CLAUDE.md 보다 결정적.

### D-T7 — FR-3 small 신호 감지: keyword list vs AI semantic vs hybrid

**선택**: keyword list + structural signals (단일 파일/함수, 메타 워크플로우)

**대안**:

- (a) AI semantic judgment 만 — 의도파악력 약해도 OK 정책과 충돌 (false positive 위험)
- (b) keyword + structural ✅ **선택**

**이유**: PRD Q3-a "의도파악력 약해도 됨" 룰. 명시적 신호 catch 만 정확하면 됨. AI 가 "분명 small" 판정 X — 아니면 ambiguous → 게이트.

### D-T8 — FR-4 게이트 발화 주체: skill body vs preflight helper

**선택**: skill body (bash one-liner 후 main agent 가 exit code 보고 AskUserQuestion)

**대안**:

- (a) `scripts/preflight.py` 가 직접 AskUserQuestion 호출 — 불가능 (helper 는 pure Python, harness 도구 접근 X)
- (b) skill body 가 exit code 분기 + AskUserQuestion ✅ **선택**

**이유**: helper 의 단일 책임 (deterministic check). 게이트는 harness 도구이므로 LLM 영역. 4 skill 본문 boilerplate 통일로 일관성 유지.

### D-T9 — FR-4 reason 필드 schema 변경: rename vs add field

**선택**: `PreflightResult` NamedTuple 에 `human_reason: str = ""` 필드 추가 (3-field, default value)

**대안**:

- (a) 기존 `reason` 을 한국어 1줄로 rewrite — caller compat 깨짐 (test_preflight.py 9 test + 4 skill bash 출력 grep)
- (b) `human_reason` 필드 추가 (default 빈 문자열) ✅ **선택**
- (c) 별도 dict / dataclass 도입 — overengineering

**이유**: NamedTuple 는 default 값 가능 (Python 3.6.1+). 기존 test 깨지지 않음. caller 가 점진적으로 `human_reason` 채택. backward compat 100%.

### D-T10 — FR-5 docs-pretty timing 통일 위치: skill 별 swap vs docs-pretty 본문 일방 변경

**선택**: 3 skill (brainstorming / designing-direction / writing-plans) 본문에서 Step 6 (사용자 리뷰) ↔ Step 7 (docs-pretty) 순서 swap + docs-pretty 본문의 frontmatter / Trigger timing 섹션 단일 룰화

**대안**:

- (a) docs-pretty/SKILL.md 본문만 수정 — caller skill 들이 여전히 post-approval 로 호출 → 효과 없음
- (b) skill 별 swap + docs-pretty 단일 룰화 ✅ **선택**
- (c) docs-pretty 발화 룰을 caller skill 에 위임 (timing 명시 X) — 결정적 룰 부재로 회귀 위험

**이유**: docs-pretty 본문이 caller 의 호출 시점에 의존 — 본문만 수정하면 효과 없음. caller (3 skill) 본문 swap + docs-pretty 본문의 trigger 룰 단일화 둘 다 필요. writing-plans 는 이미 pre-review 패턴 사용 중이므로 변경 X (참조 정렬만).

### D-T11 — FR-6 task name friendly 적용 범위: Checklist 만 vs 본문 전체 vs 글로벌 룰

**선택**: Checklist 섹션만 한국어 사용자 친화 (본문 다른 부분은 unchanged) + CLAUDE.md 에 글로벌 명칭 룰

**대안**:

- (a) skill 본문 전체를 한국어화 — 메인 에이전트의 정확한 skill 매칭 위험 (Process Flow / Detailed Step 의 영어 식별자 이탈)
- (b) Checklist 만 사용자 친화 + 본문 다른 부분 영어 식별자 유지 + CLAUDE.md 글로벌 룰 ✅ **선택**
- (c) using-superpowers/SKILL.md 에 룰만 박고 본문 unchanged — 회귀 위험 (LLM 이 룰 무시 가능)

**이유**: TaskCreate 가 직접 참조하는 부분은 Checklist. 본문의 다른 부분은 메인 에이전트가 정확한 skill 호출하기 위해 영어 식별자 그대로 필요. CLAUDE.md 글로벌 룰은 신규 skill 작성 시 일관 적용 안전망.

## 6. 위험/사이드이펙트 (preliminary)

risk-annotation taxonomy: `side-effect | breaking | race`

| ID      | 카테고리    | 위치                                                              | 설명                                                                                         | 완화                                                                                     |
| ------- | ----------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **R1**  | side-effect | `skills/designing-direction/SKILL.md` Step 0 (FR-1)              | AI 가 DB/API 시사 토픽 놓치면 tech-design 비어있음                                           | 진입 announce 한 줄 + 사용자 즉시 override                                               |
| **R2**  | breaking    | 3 skill Checklist 끝 (FR-2)                                       | LLM 행동 강제력 100% X — reminder 무시 가능                                                  | 명시 vs 미명시 차이 큼. dogfood 1회로 잔존 0건 검증                                     |
| **R3**  | side-effect | `skills/brainstorming/SKILL.md` Step 0 (FR-3)                    | small 키워드 false positive ("이건 간단하지 않아")                                           | notice + "dj-superkit 라고 답하세요" override                                               |
| **R4**  | breaking    | 4 skill Pre-flight 섹션 (FR-4)                                    | boilerplate 4곳 동시 변경. 한 군데만 누락 시 동작 불일치                                     | CLAUDE.md 결합 메모 + dogfood 4 skill 케이스                                             |
| **R5**  | side-effect | FR-4 게이트 "강제 진행 (위험)" 옵션                               | 사용자 매번 강제진행 누르면 게이트 무력화                                                    | "(위험)" 라벨 + "⚠️ preflight 우회. <reason> 무시" 한 줄 안내                           |
| **R6**  | breaking    | `scripts/preflight.py` `PreflightResult` (FR-4)                  | 필드 추가가 기존 caller 깨뜨림 가능성                                                        | NamedTuple default value 사용. 9 unit test 호환 검증                                    |
| **R7**  | race        | bootstrap paradox — 본 release 의 FR-1/FR-3 가 본 release 의 brainstorming/designing-direction 흐름 자체를 변경 | dogfood 시 신구 혼재 | implementation-plan header 에 "이 plan 자체는 v1.1.14 sequential 패턴 + 7-topic 으로 실행" 명시 (v1.1.14 선례) |
| **R8**  | side-effect | FR-3 라우터 false positive                                        | small 신호 없는데도 의도된 풀 트랙이 게이트 발화                                             | 게이트 발화 = 사용자 즉시 결정. 손해 X                                                   |
| **R9**  | side-effect | 3 skill Step 6/7 swap (FR-5) | 메인 in-memory raw vs file pretty divergence — 사용자 fix 시 메인이 in-memory raw 갱신 후 다시 docs-pretty → 파일 덮어씀 | implementation-plan 에서 이미 검증된 패턴. docs-pretty post-dispatch sanity check (header / frontmatter / footer byte-identical) 가 의미 drift 자동 검출 |
| **R10** | breaking    | 5 skill Checklist rename (FR-6) | 메인 에이전트가 Checklist 친화 이름만 보고 정확한 skill 호출 못할 위험 | 본문 내 Detailed Step + Process Flow 다이어그램에 영어 식별자 명시. CLAUDE.md 글로벌 룰 재차 보강 |

## 7. 테스트 전략

### 정적 검증 fixture (F1~F5)

skill 본문 grep 으로 룰 박힘 확인:

| ID      | 대상                                                                                                          | 검증                                                                                          |
| ------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **F1**  | `skills/designing-direction/SKILL.md` (FR-1)                                                                  | 진입 announce 문구 ("활성 토픽" / "비활성") + Step 2 Survey 슬림 wording grep                 |
| **F2**  | `skills/brainstorming/SKILL.md`, `designing-direction/SKILL.md`, `writing-plans/SKILL.md` (FR-2)              | Checklist 끝 reminder 한 문단 byte-equal grep (3개 동일 wording)                              |
| **F3**  | `skills/designing-direction/SKILL.md` (FR-2)                                                                  | Checklist count = 9 (10 제거 확인). item 9 의 통합 wording grep                              |
| **F4**  | `skills/brainstorming/SKILL.md` (FR-3)                                                                        | Step 0 라우터 본문 + small 키워드 list (`간단`, `잠깐`, `한 줄`, `단순`, `og로`, `og-`, `가볍게`) grep |
| **F5**  | 4 skill (FR-4)                                                                                                | 통일 boilerplate (`exit code 1 → AskUserQuestion`, `exit ≠ 0,1 → AskUserQuestion`) byte-equal grep |
| **F6**  | 3 skill (brainstorming / designing-direction / writing-plans) (FR-5)                                          | docs-pretty 호출이 사용자 리뷰 step BEFORE 위치 (numerical step order) + docs-pretty/SKILL.md frontmatter Trigger timing 단일 룰 grep |
| **F7**  | 5 skill + CLAUDE.md (FR-6)                                                                                    | Checklist 섹션에 `Invoke .* skill`, `Gate #\d`, `CH-\d` 패턴 0건 grep + CLAUDE.md "TaskCreate 명칭 룰" 1건 grep |

### 단위 테스트 (`scripts/tests/test_preflight.py`)

기존 9 test + 추가:

- `test_preflight_result_has_human_reason_default` — 기존 caller 가 `human_reason` 안 줘도 default 빈 문자열
- `test_docs_pretty_check_human_reason_korean` — 실패 케이스에서 `human_reason` 한국어 1줄 존재 (e.g. `file_not_found: 대상 파일이 존재하지 않습니다`)
- 동일 패턴 4 helper × 3 fail 케이스 = ~9 추가 test

### 통합 dogfood fixture (G1~G4, `skills/dj-superkit-subagent-driven-development/tests/`)

| ID      | 시나리오                                          | 기대 동작                                                                                               | 매핑 AC |
| ------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------- |
| **G1**  | "README 한 줄 수정" 으로 /brainstorm 호출         | small 신호 감지 → og-brainstorming auto-invoke + notice 노출                                            | AC-6    |
| **G2**  | "로그 포맷 변경" 으로 /brainstorm 호출            | small/large 모호 → AskUserQuestion 게이트 발화                                                          | AC-7    |
| **G3**  | 본 PRD 같은 메타 피처로 /design 호출              | adaptive announce 한 줄 + tech-design.md §3/§4 가 N/A 한 줄로 박힘                                     | AC-8    |
| **G4**  | requirements.md 에 가짜 변경이력 entry 박은 채 docs-pretty 호출 | preflight exit 1 → AskUserQuestion 게이트 발화 + 사용자 "수정 후 재시도" → entry 제거 후 재호출 → 정상 진행 | AC-11   |
| **H5**  | `/brainstorm` 새 피처 → 첫 RAW 가 prettified 인지 + fix 시 재발화 / `/design` 동일 패턴 | brainstorming/designing-direction 모두 docs-pretty → 사용자 prettified 리뷰 → 승인 → change-history. fix 요청 시 메인 revise → docs-pretty 재발화 (per-draft loop) | AC-14   |
| **H6**  | dj-superkit 자체 skill 진입 시 TaskCreate 목록 검사 | `Invoke`, `Gate #`, `skill`, `CH-id` 같은 내부 용어 미노출. 한국어 사용자 친화 표현만 | AC-15, AC-17 |

### 런타임 검증

- pytest 통과 (기존 30 + 추가 ~9 = ~39 PASS)
- 4 skill bash one-liner 수동 실행 — 각 skill 의 정상 진행 + 강제 fail 시 게이트 발화 확인
- og-brainstorming 본문 unchanged 확인 (FR-3 범위 밖)

---
## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-10 14:50] [개발방향-수정]
- **id**: CH-20260510-002
- **이유**: 신규 기술 설계 (v1.1.15 — 4 FR 의 영향 파일 매핑 / D-T1~9 결정 / R1~R8 위험 / F1~F5 + G1~G4 테스트)
- **무엇이**: flow-slim-tech-design.md 전체 (§1 layered view + §2 13 영향 파일 + §5 9 결정 + §6 8 위험 + §7 테스트 전략)
- **영향범위**: 없음 (최초 생성)
- **연관 항목**: CH-20260510-001 (요구사항 PRD)

### [2026-05-10 16:30] [개발방향-수정]
- **id**: CH-20260510-004
- **이유**: PRD CH-003 cascade — FR-5 (docs-pretty pre-review timing 통일) + FR-6 (TaskCreate 이름 사용자 친화화) 추가에 따른 tech-design amend
- **무엇이**: 제목 (4종 → 6종) / §2 영향 파일 9건 추가 (docs-pretty/SKILL.md + 3 skill Step swap + 5 skill Checklist rename + CLAUDE.md) / §5 D-T10 + D-T11 추가 / §6 R9 + R10 추가 / §7 F6 + F7 + H5 + H6 추가
- **영향범위**: flow-slim-implementation-plan.md (Task 3/7/8/9 본문 확장 + Task 15 신규 (FR-6 일괄 rename) + H5/H6 fixture 추가, plan 아직 draft)
- **연관 항목**: CH-20260510-001 (PRD 원본), CH-20260510-002 (tech-design 원본), CH-20260510-003 (PRD amendment for FR-5/FR-6)
