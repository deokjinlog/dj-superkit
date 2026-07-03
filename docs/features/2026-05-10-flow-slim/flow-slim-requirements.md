# 요구사항: v1.1.15 — 브레인스토밍/디자인 흐름 슬림화 (6종 통합)

> **For agentic workers:** This document is the PRD (planning-level only). NEXT STEP: invoke `designing-direction` skill (or run `/design`) to produce `flow-slim-tech-design.md` from this document. Do NOT add tech decisions or implementation details here — those belong in the next two artifacts.

> **카테고리:** (c) 기존 기능 수정 / 리팩터 — skill 본문 + 진입 라우터 변경

## 1. 배경/목적

### 배경

v1.1.14 dogfood 결과 사용자가 brainstorming/designing-direction 흐름에서 6건 마찰 catch:

1. (2026-05-10) *"개발디자인 계획서가 훨씬 더 느린 거같이 느껴져"* — designing-direction Step 3 의 7-topic dialogue 가 작은 피처(UI-only / 1-3 task / 리팩터)도 7개 모두 거쳐 사용자 입력 1.5~2배 누적.
2. (2026-05-10) *"Task 작성에 자꾸 이전 자동 완료 태스크가 안 사라지고 남아있어"* — skill 의 마지막 transition task ("9. designing-direction 자동 진입" / "D10. /write-plan 자동 invoke OR 종료" 등) 가 invoke 직전 마킹 안 되고 새 skill 컨텍스트로 넘어가서 in_progress 영구 잔존.
3. (이번 세션) `/brainstorm` 진입 시 구현 크기에 따라 og-brainstorming(가벼운 단발) vs dj-superkit:brainstorming(3-MD 풀 트랙) 선택 부재. 작은 변경도 무겁게 흐름.
4. (이번 세션) *"preflight 가 실패할때마다 너한테 물어보는것도 아니지 않니?"* — 4 skill (docs-pretty / code-pretty / executing-plans / subagent-dd) 의 preflight 실패 처리가 soft instruction (`exit 1 → 종료`) 만 명시되어 LLM 강제력 부재. invocation 자체 실패 (exit 127 / venv 미활성 등 환경 이슈) 처리 룰도 없음. 사용자 게이트 누락.
5. (이번 세션) *"흐름이 좀 이상하긴 하네.. docs-pretty가 왜 Step 6보다 아래에있지?"* — `docs-pretty/SKILL.md:8` 본문이 명시적으로 *"user reviews a clean version"* 을 safety net 으로 가정하는데, 실제 brainstorming/designing-direction 흐름은 사용자 승인 후 docs-pretty (post-approval) 로 발화 → 사용자 검증 없이 prettified 가 change-history 에 박힘. implementation-plan 만 pre-review 패턴 (per-draft 재발화). 일관성 결여 + safety net 미발동.
6. (이번 세션) *"태스크 목록에 나오는 명칭같은게 너무 사용자 친화적이질 못해;; 예를들면 P10. change-history CH-003 이렇게 떳거나 P11. Gate #14 + 실행 핸드오프 이런식으로.. 웬 게이트 ? 가 포함되었거나 등"* — dj-superkit skill 의 Checklist 본문에 박힌 내부 용어 (`Invoke ... skill`, `Gate #N`, `CH-id`) 가 TaskCreate task 이름에 그대로 노출 → 사용자 시점 의미 파악 어려움.

### 목적

v1.1.9~v1.1.14 게이트/checklist 합리화 흐름의 자연스러운 연장으로 brainstorming/designing-direction 진입+진행 마찰 점 6건을 한 릴리즈로 묶어 슬림화.

## 2. 사용자 스토리 / 시나리오

해당 없음 — 메타 워크플로우 변경, 외부 사용자 없음.

## 3. 기능 요구사항 (FR)

### FR-1: designing-direction 7-topic adaptive 슬림화

`skills/designing-direction/SKILL.md` Step 3 의 7-topic dialogue 를 AI 판단 기반 adaptive 로 변환.

**항상 활성 (4개)**:

- 1 아키텍처
- 2 영향 컴포넌트
- 5 결정+대안 비교
- 6 위험 (preliminary)

**조건부 활성 (3개) — 메인 에이전트가 `<slug>-requirements.md` 읽고 판단**:

- 3 데이터 모델 — DB / 스키마 / 마이그레이션 / 영구 저장 / 외부 시스템 데이터 교환을 implicit/explicit 시사하면 활성. 메타 워크플로우 / 순수 함수 / 산문 처리만이면 비활성.
- 4 외부 인터페이스 — REST/GraphQL/webhook/이벤트 발행/외부 노출 시사하면 활성. 내부 모듈 간 호출만이면 비활성.
- 7 테스트 전략 — FR 수가 많거나 (≥3), 위험 카테고리 다수, 다중 파일 영향이면 활성. trivial 변경/단일 함수면 비활성.

**판단 후 announce (항상 노출)**:

```text
ℹ️ 활성 토픽: 1,2,3,5,6 / 비활성: 4 외부IF, 7 테스트전략 (이유: 내부 모듈 변경, 단일 함수). 추가 활성 필요시 알려주세요.
```

→ 케이스 무관 (전부 활성이든 비활성 있든) 사용자에게 한 줄 노출. white box / override 시점 일관.

**비활성 토픽 처리**: tech-design.md schema 의 해당 섹션을 `## N. <섹션명> — N/A: <skip 이유>` 한 줄로 박고 끝.

**Step 2 Survey 슬림** (추가 효과):

- AS-IS: brainstorming PRD §2 (영향 컴포넌트) 식별 결과 무시하고 메인이 처음부터 grep/Read 다시
- TO-BE: `<slug>-requirements.md` §2 먼저 Read, 추가 grep/Read 는 tech-design 결정 (아키텍처/data flow/pattern) 에 깊이 부족할 때만

**deterministic Python classifier 도입 X** — backlog 가 제안한 `scripts/design_topic_classifier.py` + 키워드 룰 (hardcode list) 은 brittle (Postgres 등 미스매칭) + 메인 에이전트 판단으로 충분. 키워드 룰 폐기, AI judgment + 사용자 override 로 대체.

### FR-2: Skill Checklist 마지막 transition task 잔존 버그 수정

3 skill (`brainstorming` / `designing-direction` / `writing-plans`) 의 Checklist 끝 transition task 가 다음 skill invoke 직전 `completed` 마킹 안 되고 컨텍스트가 넘어가는 버그 수정. 백로그 `v1.1.15-checklist-completion-bug.md` 의 **Option A + Option B 둘 다** 적용.

**(A) 3 skill Checklist 끝 reminder 추가**:

```markdown
If you find yourself skipping ahead, stop and create the missing task.

**Before invoking the next skill via Skill tool, mark ALL checklist TaskCreate items as completed (in_progress → completed). The Skill tool transition does NOT auto-complete prior tasks.**
```

→ `brainstorming/SKILL.md`, `designing-direction/SKILL.md`, `writing-plans/SKILL.md` 3 skill 본문에 동일 reminder 박음.

**(B) designing-direction items 9 + 10 통합**:

- AS-IS:
  - 9. Ask proceed-to-writing-plans gate
  - 10. On approval → invoke writing-plans / On hold → exit
- TO-BE (1 item):
  - 9. Ask proceed-to-writing-plans gate (v1.1.12+ — restored). On `yes` → invoke writing-plans via Skill tool. On `no` → exit with notice telling the user to run /write-plan later.

→ semantic redundancy 제거. TaskCreate 1개로 줄어 잔존 위험 감소.

### FR-3: /brainstorm 진입 시 og- vs dj-superkit 라우터 (NEW)

`dj-superkit:brainstorming` SKILL.md 의 Checklist 1번 (Explore project context) 직전 step 0 라우터 추가.

**라우팅 룰**:

1. 사용자 입력에 **명시적 small 신호** 감지 시 — 즉시 og-brainstorming invoke + notice 한 줄.
   - small 신호 키워드: `간단`, `잠깐`, `한 줄`, `단순`, `og로`, `og-`, `가볍게`
   - 단일 파일/단일 함수 변경이 명시된 경우
   - 메타 워크플로우 / 순수 config 변경이 명시된 경우
   - notice 형식: `ℹ️ Auto-routing to og-brainstorming ('<감지된 키워드>'). Switch back? "dj-superkit" 라고 답하세요.`
2. **그 외 모두 → AskUserQuestion 게이트**:
   - `question`: "이 피처는 og-brainstorming(가벼운 단발) 또는 dj-superkit:brainstorming(3-MD 풀 트랙) 중 어느 모드로 진행할까요?"
   - `header`: "진입 모드"
   - choices: og-brainstorming / dj-superkit:brainstorming
   - default 추천 표시 X — 사용자가 컨텍스트 보고 판단

**의도파악력 약해도 됨** — AI 가 "이건 분명 large 다" 판정할 필요 없음. 명시적 small 신호 catch 만 정확하면 나머지는 게이트로 사용자가 결정.

**라우터는 `/brainstorm` slash command 호출 시에도 동일 적용** — 자연어 진입 / slash 진입 구분 없이 step 0 에서 항상 발화.

**og-brainstorming 본문 수정 X** — 라우터는 dj-superkit:brainstorming 진입에만 박힘. og- 는 unchanged.

### FR-4: Preflight 실패 시 사용자 게이트 추가 (NEW)

`scripts/preflight.py` 호출 부의 4 skill (`docs-pretty` / `code-pretty` / `executing-plans` / `dj-superkit-subagent-driven-development`) preflight 섹션을 통일된 패턴으로 교체. 현재 soft instruction (`exit 1 → 종료`) 만 명시되어 LLM 이 무시 가능 + 사용자 확인 부재.

**현재 (AS-IS)**:

```text
- exit code 0 → 검증 통과, 진행
- exit code 1 → reason 한 줄 노출 후 즉시 종료. 메인은 검증 retry 또는 LLM 재추론 X
```

**개선 (TO-BE)**:

```text
- exit code 0 → 검증 통과, 진행
- exit code 1 (helper 가 ok=False 반환, semantic fail) → 한 줄 노출 + AskUserQuestion 게이트
  - choices:
    - "수정 후 재시도" → 사용자가 doc 수정 후 메인이 preflight 재호출
    - "강제 진행 (위험)" → preflight 무시하고 다음 단계 진행 (사용자 명시 책임)
    - "스킵 (이번만)" → 해당 skill 단계 스킵, 다음 단계로 (e.g. docs-pretty 스킵 → change-history 로 직행)
- exit code ≠ 0,1 (invocation 실패: 127 / 2 / etc., harness 환경 이슈) → 즉시 사용자 안내 + AskUserQuestion 게이트
  - 메시지: "preflight helper invocation 실패 (exit <code>): <stderr 전문>. 어떻게 할까요?"
  - choices:
    - "직접 디버깅" → 사용자가 환경 점검 (venv / python 경로 / scripts/preflight 존재) 후 알려주면 메인이 재호출
    - "skill 단계 스킵" → preflight 우회하고 다음 단계로
```

**추가 변경**:

- `scripts/preflight.py` 의 reason 메시지 명확화 — 현재 한 단어 (`ok` / `file_not_found` / `footer_not_empty` / `wrong_filename` 등) 인데 사용자 화면 노출 시 1줄 한국어 설명 부족.
- 4 skill preflight 본문을 동일 boilerplate 로 통일 — 현재 wording 미세하게 다름.

**범위 제한**:

- AskUserQuestion 게이트는 **on-demand** — preflight 실패 시에만 발화. 정상 진행 시 게이트 0개.
- "강제 진행 (위험)" 선택 시 메인이 한 줄 안내 ("⚠️ preflight 우회. <reason> 무시하고 진행.") 후 본 skill 의 dispatch / Edit 단계 직진.

### FR-5: docs-pretty pre-review timing 통일 (NEW)

3 skill (brainstorming / designing-direction / writing-plans) 의 docs-pretty 발화 시점을 모두 **사용자 리뷰 직전 (pre-review, per-draft 재발화)** 으로 통일. 백로그 `v1.1.15-docs-pretty-pre-review.md` 기반.

**현재 (AS-IS — doc 타입별로 다름)**:

- requirements.md / tech-design.md: 사용자 RAW 리뷰 + 승인 후 → docs-pretty → change-history (post-approval, final-1회). **safety net 미발동** — 사용자가 prettified 본문 못 봄.
- implementation-plan.md: verifying-spec + code-pretty 통과 후 → docs-pretty → 사용자 prettified 리뷰 (pre-review, per-draft 재발화).

**개선 (TO-BE — 모든 doc 타입 동일 pre-review)**:

```
메인 작성 → docs-pretty → 사용자 prettified 리뷰 → 승인 → change-history
                              ↑ safety net 발동 (사용자 검증 = 의미 drift catch)

수정 요청 시:
사용자 fix → 메인 revise → docs-pretty 재발화 → 다시 prettified 보여주기 (loop)
```

**설계 근거**: `docs-pretty/SKILL.md:8` 본문이 명시적으로 *"user reviews a clean version"* + *"user's review is the safety net"* 을 전제. 현재 흐름은 본문 전제와 어긋남.

**의미 drift 방지 가드 (이미 박혀있음)**:
- "절대 의미 잃지 말 것" #1 priority (line 8)
- Sonnet 강제 (negative constraint 준수율, line 44)
- Haiku 회피 (Korean prose rephrasing 위험, line 50)
- Forbidden list (reword/paraphrase/summarize/expand/"improve")
- 변경이력 footer byte-identical 강제
- Post-dispatch sanity check (header count / frontmatter / footer)

→ 가드 + 사용자 리뷰 발동 시 의미 drift 사실상 0%.

**범위 제한**:
- writing-plans 는 이미 pre-review 패턴 사용 중 — 변경 없음 (참조 정렬만).
- og-brainstorming 본문 unchanged — dj-superkit:brainstorming 만 영향.
- dispatch 횟수 증가 (사용자 수정 2-3회 가정 시 1회 → 3-4회) — Sonnet format-only 비용 적음 (수 초). implementation-plan 이 이미 같은 패턴.

### FR-6: TaskCreate task 이름 사용자 친화화 (NEW)

dj-superkit 자체 skill (brainstorming / designing-direction / writing-plans / executing-plans / finishing-a-development-branch) 의 Checklist 본문에 박힌 내부 용어를 사용자 친화 한국어로 재작성. 백로그 `v1.1.15-task-name-friendly.md` 기반.

**현재 (AS-IS) — 내부 용어 노출 사례**:

```
8. **Invoke change-history skill** — append first [요구사항-수정] entry
9. **Auto-proceed to designing-direction (v1.1.9+ — gate removed)**
Gate #13 — plan + verify 결합 승인
Gate #14 — 실행 모드 선택
P10. change-history CH-003
P11. Gate #14 + 실행 핸드오프
```

→ "Invoke" / "skill" / "Gate #N" / "CH-id" 모두 내부 용어. 사용자 의미 파악 어려움.

**개선 (TO-BE) — 사용자 친화 한국어 표현**:

| 내부 용어 | 사용자 친화 표현 |
|---|---|
| `Invoke change-history skill` | `변경이력 기록` |
| `Invoke docs-pretty skill` | `문서 포맷 정리` |
| `Invoke code-pretty skill` | `코드 블록 포맷 정리` |
| `Invoke verifying-spec` | `사양 정합성 검증` |
| `Gate #N — X` | `X` (Gate 번호 제거, 의미만 노출) |
| `change-history CH-NNN` | `변경이력 기록` |
| `Run mode-specific dialogue` | `요구사항 질문 진행` |
| `Mode selection gate` | `모드 선택` |
| `RAW 승인` / `Combined approval gate` | `초안 검토 및 승인` |
| `proceed-to-write-plan gate` | `다음 단계 진입 확인` |

**범위 제한**:
- 메인 에이전트가 정확히 어떤 skill 호출하는지 알아야 하므로 **본문의 다른 부분 (Process Flow diagram, Detailed sections, "Invoke X skill" 등 actual instruction wording) 의 내부 용어는 그대로 유지**. Checklist 명칭만 사용자 친화.
- og-* skill 들 (upstream verbatim) 은 손대지 않음.
- 변경이력 footer 의 entry tag (`[요구사항-수정]` 등) 는 schema 매직 키워드라 유지.
- CLAUDE.md 또는 글로벌 위치에 "TaskCreate 명칭 룰" 한 줄 박아 신규 skill 작성 시 일관 적용.

**의도파악력 보장**: Checklist 가 친화적 이름이라도 본문 내 Detailed Step + Process Flow 다이어그램에 정확한 skill 명 명시. 메인은 본문 전체 읽으므로 매칭 가능.

## 4. 비기능 요구사항 (NFR)

해당 없음 — skill 본문 변경, NFR 의미 적음.

## 5. 범위 밖 (Out of Scope)

대화 중 누적 collected:

- **Python classifier 도입** (FR-1) — `scripts/design_topic_classifier.py` + 키워드 룰 hardcode list. AI 판단으로 대체.
- **Large 휴리스틱 자동 판정** (FR-3) — AI 가 "분명 large" 판정 X. 명시적 small 신호만 catch.
- **og-brainstorming 본문 수정** (FR-3) — 라우터는 dj-superkit 진입에만 박힘.
- **AskUserQuestion JSON required field 보강** (`header`/`description`/`multiSelect: false`) — 별도 v1.1.16 micro-patch. (단 FR-4 의 게이트 자체는 본 릴리즈에서 schema 준수하여 작성.)
- **preflight 자동 retry 룰** (FR-4) — "재시도" 선택 시 자동 N회 retry X. 사용자가 doc 수정 후 메인 재호출 = 1회.
- **finishing-a-development-branch discard 안전망 복원** — v1.1.14 의도된 슬림. 본 v1.1.15 무관.
- **change-propagation cascade 최적화** — v1.1.15 무관.

## 6. 수용 기준 (Acceptance Criteria)

- **AC-1** (FR-1): designing-direction Step 3 시작 시 활성/비활성 토픽 한 줄 announce 노출 (전부 활성이든 비활성 있든 일관). 비활성 토픽은 tech-design.md 에 `## N. <섹션> — N/A: <reason>` 한 줄로 박힘.
- **AC-2** (FR-1): designing-direction Step 2 Survey 가 `<slug>-requirements.md` §2 먼저 Read 하도록 본문 변경. 추가 grep 은 결정 트리거 시점에만.
- **AC-3** (FR-2): 3 skill (brainstorming / designing-direction / writing-plans) Checklist 끝에 transition reminder 한 문장 박힘. 동일 wording.
- **AC-4** (FR-2): designing-direction Checklist 가 1~9 (10 제거). item 9 통합 wording 적용.
- **AC-5** (FR-3): dj-superkit:brainstorming step 0 라우터 본문 박힘. 명시적 small 신호 → og-brainstorming auto-invoke + notice. 그 외 → AskUserQuestion 게이트.
- **AC-6** (dogfood): 작은 메타 피처 ("README 한 줄 수정") 으로 라우터 동작 확인 — small 신호 감지 → og 자동 진입 + notice 노출.
- **AC-7** (dogfood): 모호한 피처 ("로그 포맷 변경") 으로 라우터 게이트 발화 확인.
- **AC-8** (dogfood): 본 PRD 같은 메타 워크플로우 피처로 designing-direction adaptive 동작 확인 — 비활성 토픽 N/A 한 줄 + announce 노출.
- **AC-9** (FR-4): 4 skill preflight 본문이 통일된 boilerplate 로 교체. exit 1 / exit ≠0,1 분기 모두 AskUserQuestion 게이트 정의 박힘.
- **AC-10** (FR-4): `scripts/preflight.py` 의 reason 필드가 한국어 1줄 설명 동반 (e.g. `file_not_found: 대상 파일이 존재하지 않습니다 (<path>)`). 기존 단어 reason 호환 유지 (caller 가 split 하지 않도록 dataclass 필드 추가 형태 권장).
- **AC-11** (dogfood): preflight 강제 실패 시뮬레이션 — `<slug>-requirements.md` 에 가짜 변경이력 entry 박은 채로 docs-pretty 호출 → exit 1 + 게이트 발화 + 사용자가 "수정 후 재시도" 선택 → entry 제거 후 재호출 → 정상 진행.
- **AC-12** (FR-5): 3 skill (brainstorming / designing-direction / writing-plans) 모두 docs-pretty 가 사용자 리뷰 직전 발화 (pre-review). 사용자가 prettified 본문 검토 후 승인.
- **AC-13** (FR-5): 사용자 fix 요청 시 모든 doc 종류에서 docs-pretty 재발화 (per-draft 패턴 통일). docs-pretty SKILL.md frontmatter / Trigger timing 섹션 단일 룰로 정리.
- **AC-14** (dogfood FR-5): `/brainstorm` 새 피처 → 첫 RAW 가 prettified 인지 확인 + fix 요청 시 재발화 확인. `/design` 동일 패턴 확인.
- **AC-15** (FR-6): dj-superkit 자체 skill (brainstorming / designing-direction / writing-plans / executing-plans / finishing-a-development-branch) 의 Checklist 가 사용자 친화 한국어 명칭으로 재작성. 내부 용어 (`Invoke ... skill`, `Gate #N`, `CH-id`) 미노출.
- **AC-16** (FR-6): CLAUDE.md 또는 글로벌 위치에 "TaskCreate 명칭 룰" 한 줄 박힘 — 신규 skill 작성 시 일관 적용.
- **AC-17** (dogfood FR-6): `/brainstorm` / `/design` / `/write-plan` / `/execute-plan` 진입 시 TaskCreate 목록에 `Invoke`, `Gate #`, `skill` 같은 내부 용어 미노출.

---
## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-10 14:30] [요구사항-수정]
- **id**: CH-20260510-001
- **이유**: 신규 피처 brainstorming 결과 (v1.1.15 — 브레인스토밍/디자인 흐름 마찰 4종 통합 PRD 최초 생성)
- **무엇이**: flow-slim-requirements.md 전체 (FR-1 adaptive 7-topic / FR-2 transition task 잔존 fix / FR-3 brainstorm 라우터 / FR-4 preflight 실패 게이트 + AC-1~11 + 범위 밖 7항목)
- **영향범위**: 없음 (최초 생성)

### [2026-05-10 16:10] [요구사항-수정]
- **id**: CH-20260510-003
- **이유**: 사용자 catch — `v1.1.15-docs-pretty-pre-review.md` + `v1.1.15-task-name-friendly.md` 2 backlog 통합. (a) docs-pretty 발화 시점이 doc 타입별로 다름 → 일관성 + safety net 발동, (b) Checklist 본문의 내부 용어 (Invoke / Gate # / CH-id) 가 TaskCreate 이름에 그대로 노출 → 사용자 친화화. 5번째 + 6번째 FR 동시 추가.
- **무엇이**: §1 배경 (4건 → 6건 + 5/6번 catch 추가) / §1 목적 (4 → 6) / §3 FR-5 + FR-6 신규 추가 / §6 AC-12~17 신규 추가 / 제목 (4종 → 6종)
- **영향범위**: flow-slim-tech-design.md (CH-004 cascade — D-T10/D-T11 + R9/R10 추가), flow-slim-implementation-plan.md (Task 3/7/8/9 본문 확장 + Task 15 신규 (FR-6 일괄 rename) + H5/H6 fixture 추가, plan 아직 draft)
- **연관 항목**: CH-20260510-001 (원본 PRD)
