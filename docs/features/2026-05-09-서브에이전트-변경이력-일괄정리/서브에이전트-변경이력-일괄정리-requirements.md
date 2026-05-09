# 요구사항: 서브에이전트 변경이력 일괄정리

> **Mode:** Socratic (free-form). Downstream `designing-direction` reads this prose without expecting fixed PRD section IDs.
>
> **For agentic workers:** This document is the PRD (planning-level only). NEXT STEP: invoke `designing-direction` skill (or run `/design`) to produce `<slug>-tech-design.md` from this document. Do NOT add tech decisions or implementation details here — those belong in the next two artifacts.
>
> **입력 backlog:** `docs/backlog/v1.1.7-subagent-batch-changelog.md` (2026-05-09 신고 본문)

## 배경

v1.1.6 릴리즈 작업에서 `js-super-subagent-driven-development` 스킬로 10개 task를 서브에이전트로 실행. 모든 task 완료 후 사용자가 "변경이력 footer가 task별로 매번 떴는데 뭔가 이상하다"라고 신고. dogfood 직후 실시간으로 들어온 신고로 인지가 가장 fresh한 시점.

신고는 3-layer 문제로 정리됨:

1. **(메인) 누적 후 일괄 vs 즉시 매번** — 사용자가 원한 워크플로우는 "서브에이전트 일이 다 끝나면 메인이 한꺼번에 계획서와 차이를 정리". 현재 구현은 정반대로 task당 즉시 [코드-수정] entry append + log commit. N task = N entries + N log commits.
2. **git history와 변경이력 정보 중복** — `commit_policy: per-task` (git-fast 모드)일 때 [코드-수정] entry의 변경 전/후 코드 블록은 `git show <sha>` 와 동일한 정보. 이중 저장소.
3. **schema에 비-코드 entry type 부재** — v1.1.6 Task 10은 검증/grep + git tag만 했고 코드 변경 0건이었는데도 [코드-수정] 태그로 기록됨. tag/reality 불일치.

## 사용자 의도 (정확한 인용)

> 내가 원하는건 서브에이전트 일이 다끝나면 메인에이전트가 한꺼번에 계획서와 다른점 싹다 정리해주길 원했어 (서브에이전트 결과에 만약 코드 기존과 바뀐게 있으면 어디 바뀌었다라고 같이 메인에이전트에게 결과를 미리 남겨놓고 나중에 메인에이전트가 한번에 정리)

핵심 인터페이스 변경: 서브에이전트(implementer)가 "변경 위치/요약"을 메인 에이전트에 어떤 형식으로 넘길지 명시되어야 함. 현재는 implementer 프롬프트에 "거버넌스는 메인이 한다"만 박혀 있고, 메인은 자유롭게 git diff로 추출. 이걸 더 명확한 인터페이스로 바꿔야 batch processing이 가능.

## 원하는 동작 (요지)

### 1. per-task 누적 → end-of-run 일괄 정리

- 서브에이전트 모드로 N개 task 실행 중에는 변경이력 footer에 entry append 하지 않음 (각 task의 본 commit은 그대로 진행).
- 모든 task 완료 직후, 메인이 한 번에 누적된 변경 요약을 종합 entry(들)로 footer에 append. 이때 plan vs 실제 코드 갭(누락/초과)이 한 메시지로 사용자에게 노출됨 — 다음 단계(PR 작성, finishing-a-development-branch) 진입의 자연스러운 게이트.

### 2. git-fast 모드 entry 슬림화

- `commit_policy: per-task`일 때 변경이력 entry는 메타정보 위주: id / 이유 / 영향범위 / 위험 카테고리 / 연관 commit SHA.
- 변경 전/후 코드 블록은 git이 이미 audit trail이므로 entry에서 생략 가능. 필요 시 `git show <sha>` 한 줄로 조회.
- `commit_policy: single` / `none` (memory-fallback) 일 때만 변경 전/후 코드를 entry에 보존 (git이 못 추적하니까 종전 schema 유지).

### 3. 비-코드 task entry type 보강

- 코드 변경 0건인 task (검증 / grep / 릴리즈 / git tag만)는 [코드-수정] 태그로 기록되지 않아야 함.
- 신규 entry type ([검증] 또는 [릴리즈]) 도입, 또는 schema에서 "코드 변경 0건" 케이스를 entry-skip으로 명시.

### 4. implementer → main 보고 인터페이스

- implementer 서브에이전트의 보고 형식에 "어디를 무엇으로 바꿨는지"를 메인이 batch로 받기 쉬운 구조 추가. 자유 산문 → 구조화된 status / files-changed / commit-sha / risk-hints (또는 임시 파일 buffer / git notes 등) 중 하나.
- 구체 후보(A/B/C/D)는 backlog §"후보 인터페이스" 표에 정리됨. **선택은 designing-direction 단계의 결정 사항** — 이 PRD에서는 옵션 자체를 못 박지 않고 "메인이 batch로 받기 쉬운 구조여야 한다"는 요구사항만 명시.

## 우려 / 제약

- **인라인 모드(`executing-plans`)와의 일관성**: 인라인 모드에서도 batch end-of-run으로 통일할지, 아니면 서브에이전트 모드만 변경하고 인라인은 종전 (per-task append) 유지할지는 design에서 결정. 두 모드의 commit history 모양이 갈릴 수 있음을 인지.
- **사용자 인터럽트 시 누락 위험**: end-of-run 일괄이면 모든 task 완료 전 세션 끊기면 변경이력이 누락. mitigation 필요 (임시 buffer / hook 등).
- **변경이력 ↔ git history 단일 진실원**: per-task 모드에서 entry 슬림화 시 사용자가 "변경 전/후 코드를 변경이력에서 바로 보고 싶다"는 요구를 가질 가능성. 옵션화 또는 명시적 trade-off 문서화 필요.
- **`commit_policy` 영향 안 받는 영역 명시**: 본 commit / `[log] task N` commit 의 message 형식, per-task vs single vs none 정책 자체는 그대로. 인터페이스만 변경.

## 수용 기준 (Acceptance Criteria)

- **AC-1**: 서브에이전트 모드로 N개 task 실행 후, 변경이력 footer에 누적된 entry는 N개가 아닌 종합 형태(1개 또는 batch entry 묶음)로 한 commit에 append됨. 매 task 시점에는 변경이력 추가 안 됨.
- **AC-2**: 종합 정리 시 plan과 실제 코드의 차이점(누락된 작업, 초과 작업, follow-up commit 발생 여부)이 하나의 메시지로 main agent를 통해 사용자에게 노출됨.
- **AC-3**: 코드 변경 0건인 task (검증/태그만)는 [코드-수정] entry로 기록되지 않음. 별도 entry type을 사용하거나 entry skip + git tag/log로 대체 추적.
- **AC-4**: `commit_policy: per-task` (git-fast) 모드에서 변경 전/후 코드 블록을 entry에서 생략해도 되고, 연관 commit SHA로 `git show <sha>` 즉시 조회 가능하다는 것이 schema에 명시됨. `single`/`none` 모드는 종전 schema(코드 블록 보존) 유지.
- **AC-5**: implementer 서브에이전트의 보고 형식에 메인이 batch로 받기 쉬운 구조(파일/라인/요약/위험 힌트/연관 commit SHA 등)가 명시되어, 메인이 자유 산문 파싱이 아닌 구조화된 입력으로 종합 정리할 수 있음.

## 범위 밖 (Out of Scope)

- `commit_policy: per-task | single | none` 정책 자체의 변경 (그대로 유지).
- 본 commit 및 `[log] task N` commit의 commit message 형식 변경.
- `risk-annotation` 3-checklist 자체의 변경 (적용 시점만 영향 받음).
- 인라인 모드(`executing-plans`)의 batch 적용 여부는 design 단계에서 결정 — 이 요구사항에서는 서브에이전트 모드(`js-super-subagent-driven-development`)가 1차 타깃.
- 과거 v1.1.6 dogfood에서 이미 작성된 `docs/features/2026-05-09-구현플랜개선/구현플랜개선-implementation-plan.md` 의 변경이력 entry 사후 재정리. (마이그레이션 없음, 신규 정책은 v1.1.7 이후 신규 plan에만 적용.)

## 다음 단계

1. `/design` 으로 designing-direction 진입 → 4 후보 옵션 (A 임시 파일 buffer / B 보고 형식 구조화 / C git notes / D `git log --since` 기반) 비교 + 결정.
2. `/write-plan` 으로 implementation-plan 작성 — `js-super-subagent-driven-development` 스킬 + `implementer-prompt.md` + `change-history` 스킬 schema 수정 task 분해.
3. dogfood 실행 (이번엔 새 패턴으로!) — v1.1.7 자체를 신규 batch 패턴으로 실행해서 self-validation.

---

## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-09 17:30] [요구사항-수정]
- **id**: CH-20260509-001
- **이유**: 신규 피처 brainstorming 결과 (Socratic 모드)
- **무엇이**: 서브에이전트-변경이력-일괄정리-requirements.md 전체 (배경 / 사용자 의도 / 원하는 동작 4항 / 우려·제약 / AC-1~5 / 범위 밖 / 다음 단계)
- **영향범위**: 없음 (최초 생성). 다음 단계에서 designing-direction → tech-design 작성 시 4 후보 옵션(A/B/C/D) 비교가 트리거됨.
- **연관 항목**: backlog `docs/backlog/v1.1.7-subagent-batch-changelog.md` (commit c8036f2)
