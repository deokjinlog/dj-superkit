# 개발방향: 서브에이전트 변경이력 일괄정리

> **For agentic workers:** This document is the technical spec (architecture, components, data, interfaces, decisions, risks, test strategy). It is anchored to `서브에이전트-변경이력-일괄정리-requirements.md` (the PRD) and consumed by `서브에이전트-변경이력-일괄정리-implementation-plan.md` (step-by-step plan). NEXT STEP: invoke `writing-plans` skill (or run `/write-plan`) to produce `<slug>-implementation-plan.md` from this design. Do NOT include step-by-step implementation tasks here — those belong in the plan.

## 1. 아키텍처 개요

### 1.1 현행 (v1.1.6) 흐름

```
[per task]
  Snapshot BASE_SHA
  → implementer subagent (TDD + 코드 + 본 commit)
  → spec reviewer subagent (line-by-line)
  → main: git diff BASE_SHA HEAD
  → main: 3-checklist
  → main: (트리거 시) RISK 주석 + follow-up commit
  → main: Read plan.md / Edit plan.md (변경이력 [코드-수정] entry)  ★
  → main: git commit -m "[log] task N"                              ★

[final] finishing-a-development-branch
```

★ 단계가 task별로 매번 발화 → N task = N entries + N log commits.

### 1.2 신규 (v1.1.7) 흐름

```
[per task]
  Snapshot BASE_SHA
  → implementer subagent (TDD + 코드 + 본 commit + Changes Manifest 보고 + buffer 파일 기록)  ★
  → spec reviewer subagent (line-by-line) — 종전과 동일
  → main: git diff BASE_SHA HEAD
  → main: 3-checklist
  → main: (트리거 시) RISK 주석 + follow-up commit
  → main: in-memory accumulator + buffer 파일 무결성 확인 (footer 건드리지 않음)         ★
  → TodoWrite 체크 (task 본 commit + risk-annotate commit 까지만 history)

[all tasks complete]
  → main: buffer 파일 + accumulator 종합 → "구현 요약" 메시지 사용자 노출  ★
  → main: Read plan.md / Edit plan.md (consolidated [코드-수정] entry 묶음 1회 append) ★
  → main: git commit -m "[log] all tasks: <요약>"   (단일 log commit)               ★
  → main: buffer 디렉토리 cleanup
  → finishing-a-development-branch
```

★ 표시한 단계가 v1.1.7 신규/이전 동작.

### 1.3 핵심 추상화

- **Changes Manifest**: implementer 서브에이전트가 종료 시 보고하는 구조화 입력. status / files-changed (path + line-range) / commit SHAs / risk-hints / 한 줄 요약 포함.
- **Changelog Buffer**: 구조화 매니페스트의 사본을 task 직후 디스크에 기록한 임시 파일 (`.js-super/changelog-buffer/<slug>/task-NN.md`). 메인 세션 인터럽트 시 복구 가능 (R2 mitigation).
- **End-of-run Consolidator**: 모든 task 완료 후 메인이 1회 실행. 누적 매니페스트 + buffer 파일을 모아 footer entry 묶음 + plan ↔ 실제 갭 요약 메시지 생성.

## 2. 영향 받는 컴포넌트/파일

| 파일                                                                 | 변경 종류                                                                                                                                                        | 영향              |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| `skills/js-super-subagent-driven-development/SKILL.md`               | Per-task Sequence 재작성 (per-task append 제거 / end-of-run consolidator 추가), Acceptance 갱신                                                                  | AC-1, AC-2        |
| `skills/js-super-subagent-driven-development/implementer-prompt.md`  | Report Format 섹션에 Changes Manifest 형식 추가, buffer 파일 기록 단계 추가                                                                                      | AC-5              |
| `skills/change-history/SKILL.md`                                     | 신규 entry type `[검증]` `[릴리즈]` 추가, git-fast 모드 슬림 schema 명시 (코드 블록 생략 + 연관 commit SHA 필수), end-of-run consolidated batch entry 형식 명시  | AC-3, AC-4        |
| `skills/executing-plans/SKILL.md`                                    | 인라인 모드도 end-of-run batch로 통일 (D5 결정 따름) — Phase 2 단계 재구성, in-memory accumulator 사용                                                           | AC-1 (인라인)     |
| `.gitignore`                                                         | `.js-super/changelog-buffer/` 추가                                                                                                                               | R4 mitigation     |
| `scripts/changelog_buffer.py` (신규)                                 | buffer 파일 read/write helper, end-of-run consolidator 유틸                                                                                                      | DRY (skill 본문에 sed/jq 산문 박지 않기) |
| `README.md`                                                          | v1.1.7 정책 한 줄 갱신                                                                                                                                           | 문서 정합성       |
| `package.json` + 5 manifests                                         | 1.1.6 → 1.1.7 bump                                                                                                                                               | 릴리즈            |

## 3. 데이터 모델/스키마 변경

### 3.1 Changes Manifest (implementer → main 인터페이스, AC-5)

```yaml
# .js-super/changelog-buffer/<slug>/task-NN.md (frontmatter + body)
---
task_id: 5
task_name: "Update X module"
status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
base_sha: <SHA-before-task>
commits:
  - sha: <SHA1>
    message: "test: ..."
  - sha: <SHA2>
    message: "feat: ..."
files_changed:
  - path: src/foo.py
    line_range: "42-58"
    summary: "Add wallet validation"
    risk_hints: ["side-effect"]
  - path: tests/test_foo.py
    line_range: "1-25"
    summary: "Add unit test for validation"
    risk_hints: []
concerns: []  # implementer self-review에서 발견한 항목
---
<free-form supplementary notes>
```

`risk_hints` 는 implementer가 *추측*만 함 (확정은 메인의 3-checklist). 메인이 풍부한 hint 받으면 3-checklist 추론이 빨라짐.

### 3.2 변경이력 entry schema 확장

#### 신규 entry type: `[검증]`

```markdown
### [YYYY-MM-DD HH:MM] [검증] (task: Task N — <task name>)
- **id**: CH-YYYYMMDD-NNN
- **이유**: <검증 목적 — e.g., 정적 grep 통과 / 릴리즈 전 sanity>
- **무엇이**: <검증한 항목들 — e.g., AC-1 grep / G1 fixture run>
- **결과**: PASS | FAIL | PARTIAL — <상세>
- **연관 commit**: <SHA, 해당 시>
- **연관 항목**: CH-... (omit if none)
```

코드 변경 블록 없음. AC-3 충족.

#### 신규 entry type: `[릴리즈]`

```markdown
### [YYYY-MM-DD HH:MM] [릴리즈]
- **id**: CH-YYYYMMDD-NNN
- **이유**: <버전 bump 이유>
- **무엇이**: vX.Y.Z 태그 + N개 manifest 동기화
- **연관 commit**: <SHA>, <tag SHA>
```

#### git-fast 모드 슬림 schema (per-task / consolidated)

```markdown
### [YYYY-MM-DD HH:MM] [코드-수정] (batch: tasks N..M)
- **id**: CH-YYYYMMDD-NNN
- **이유**: <feature-level 종합 요약>
- **무엇이**: <comma-separated file list (전체 task 합쳐서)>
- **영향범위**: <combined>
- **위험 카테고리**: <union>
- **task별 세부 (M건)**:
  - Task N: `<file:lines>` — <요약> (`<risk>`) — commits: `<SHA1>`, `<SHA2>`
  - Task N+1: ...
- **연관 commits**: <전체 SHA 리스트, 또는 BASE_SHA..HEAD>
- **변경 전/후 코드**: 생략 — `git show <SHA>` 로 조회
```

AC-4 충족: 코드 블록 생략 + commit SHA 참조.

#### memory-fallback 모드 schema

종전(`commit_policy: single` / `none`)과 동일 — 변경 전/후 코드 블록 보존. git이 audit trail 못 하므로.

### 3.3 Buffer 파일 라이프사이클

| 시점                    | 동작                                                                                                       |
| ----------------------- | ---------------------------------------------------------------------------------------------------------- |
| Task 시작 시            | (없음)                                                                                                     |
| Task 종료 시 (implementer) | `.js-super/changelog-buffer/<slug>/task-NN.md` 작성                                                    |
| 메인 후처리             | buffer 파일 읽기 + 무결성 검사 + accumulator 갱신 (footer 건드리지 않음)                                   |
| 모든 task 완료 후       | accumulator 종합 → footer 1회 append → buffer 디렉토리 `rm -rf`                                            |
| 다음 세션 시작 시       | 잔존 buffer 발견 시 사용자에게 안내 ("이전 세션의 미정리 buffer 발견 — 복구할까요?")                       |

## 4. 외부 인터페이스

### 4.1 implementer subagent 보고 형식 (변경)

종전 `Report Format` 섹션에 **Changes Manifest** 추가:

```
## Report Format

When done, report:
- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you implemented (or what you attempted, if blocked)
- What you tested and test results
- Self-review findings (if any)
- Any issues or concerns

## Changes Manifest (REQUIRED on DONE / DONE_WITH_CONCERNS)

Write a YAML frontmatter file at:
  .js-super/changelog-buffer/<slug>/task-NN.md

Use the schema in [tech-design §3.1]. Fields:
  - task_id, task_name, status
  - base_sha (received from main), commits (your task's SHAs)
  - files_changed: list of {path, line_range, summary, risk_hints}
  - concerns: list of self-review concerns

Why: the main agent batches these manifests into a single change-history
entry at the end of the run, instead of appending per-task.
```

### 4.2 main agent 후처리 인터페이스 (변경)

```
[per task]
- Read buffer file: .js-super/changelog-buffer/<slug>/task-NN.md
- Validate manifest schema
- Apply 3-checklist (override implementer's risk_hints if needed)
- (RISK trigger 시) RISK 주석 + follow-up commit
- Append to in-memory accumulator
- TodoWrite 체크

[all tasks complete]
- Render "구현 요약" 메시지 (plan vs 실제 갭)
- Read plan.md
- Edit plan.md (consolidated entry + 갭에 따른 [검증] entry 등 추가)
- git commit -m "[log] all tasks: <요약>"
- rm -rf .js-super/changelog-buffer/<slug>/
```

### 4.3 인라인 모드(`executing-plans`) 변경 — D5 결정

서브에이전트 모드와 패턴 통일. Phase 2 단계 재구성:

```
[per task] (인라인)
- 코드 edit + RISK 주석 + 본 commit (plan.md 미수정)
- in-memory: (file:line, risk, summary) 누적

[all tasks complete] (인라인)
- 메인 컨텍스트의 누적 정보 → consolidated entry 1회 + plan commit 1회
```

buffer 파일은 **인라인 모드에서는 생략** (메인이 계속 살아있으므로 인터럽트 손실 시 재실행하면 됨). 서브에이전트 모드에서만 buffer 사용.

## 5. 핵심 결정 + 대안 비교

### D1: implementer → main 보고 인터페이스 (4 후보)

| 옵션                       | 영구성        | 구조화   | 인프라 비용                          | 실패 mode              |
| -------------------------- | ------------- | -------- | ------------------------------------ | ---------------------- |
| A 임시 파일 buffer          | ✅ 디스크     | ✅ YAML  | 폴더 cleanup 필요                    | leftover buffer        |
| B 구조화 보고 (메모리만)    | ❌ 세션 한정  | ✅       | 0                                    | 세션 인터럽트 시 손실  |
| C git notes                | ✅ git        | △ 한 줄  | git plumbing 지식 필요, squash 시 손실 | obscure              |
| D `git log --since`        | ✅ git        | ❌ 산문  | 0                                    | risk-hints 재추론 필요 |

**선택: A + B 하이브리드** (Changes Manifest를 implementer 보고에도 포함 + 같은 데이터를 buffer 파일에도 기록)

이유:

- B 단독은 인터럽트 손실 (PRD §"우려 / 제약" 명시)
- A 단독은 메인이 매번 파일 read 필요 (서브에이전트 보고의 in-memory 사본도 활용 못 함)
- A+B: 메인은 평소 in-memory 보고로 빠르게 진행, 인터럽트 발생 시 buffer로 복구
- C는 git notes obscurity + squash 위험 (PR 단계 squash 권장 정책과 충돌)
- D는 risk-hints 손실 — 메인이 매번 3-checklist를 처음부터 추론

### D2: end-of-run entry 형식 — 1개 종합 vs N개 task 묶음

**선택: 1개 consolidated entry (batch: tasks N..M)** + 비-코드 task는 별도 [검증] entry

이유:

- 사용자 의도 ("한꺼번에 ... 싹다 정리") 와 일치
- footer 비대 완화 (10 task = entry 10개 → entry 1개)
- 세부는 `task별 세부 (M건)` 리스트로 보존 — 정보 손실 없음

**대안 (각 task entry 묶음을 한 commit에)**: 정보는 동일하나 footer 길이 길어짐. 거부.

### D3: 코드 변경 0건 task 처리

**선택: 신규 entry type `[검증]` 도입** (`[릴리즈]` 도 함께)

이유:

- v1.1.6 Task 10 같은 케이스 (검증/grep + tag) 가 schema와 일치
- entry-skip만 하면 "그 task가 있었다"는 감사 흔적이 사라짐 — 결과(PASS/FAIL) 기록이 필요한 경우 누락
- 기존 5종 entry type은 그대로 유지 (BC 보장)

**대안 (entry skip)**: 기록 없이 git log에 의존. 거부 — `[검증]` PASS/FAIL 결과는 git에 안 남음.

### D4: per-task 모드 entry 슬림화 적용 범위

**선택: `commit_policy: per-task` (git-fast) 모드에서만 슬림 schema 적용**, `single`/`none` 은 종전 schema 유지

이유:

- single/none 모드는 git이 audit trail 못 하므로 entry에 코드 블록 보존 필요
- per-task 모드는 commit SHA 로 `git show` 즉시 조회 가능 → 이중 저장 불필요
- `commit_policy` 가 이미 schema 분기의 single source of truth

### D5: 인라인 모드(`executing-plans`)도 batch 적용 여부

**선택: 적용** — 두 모드 패턴 통일

이유:

- 사용자 입장에서 "인라인 vs 서브에이전트" 선택은 컨텍스트 절약 여부지, 변경이력 패턴이 다를 이유는 없음
- footer 비대 완화 효과 인라인에도 똑같이 유효
- 인라인은 buffer 파일 없이 in-memory 만 사용 (메인이 끝까지 살아있으므로)

**대안 (서브에이전트만 적용)**: 두 모드 commit history 모양이 갈림 → 사용자 혼란. 거부.

### D6: buffer 파일 레이아웃

**선택: `.js-super/changelog-buffer/<slug>/task-NN.md`** (gitignored)

이유:

- 프로젝트 root 오염 최소화 (`.js-super/` 한 폴더 안)
- feature별 분리 (`<slug>/` ) — 동시 다중 피처 진행 시 충돌 없음
- task-NN.md 형식 — 0-padded 두 자리, 정렬 보장

**대안 (`.git-info/notes/<slug>/...`)**: git 폴더 안에 두면 워크트리 동작 헷갈림. 거부.

## 6. 위험/사이드이펙트 (preliminary)

| ID | 카테고리    | 설명                                                                                                   | mitigation                                                                                            |
| -- | ----------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| R1 | side-effect | implementer가 buffer 디렉토리 생성 실패 (권한/디스크) → manifest 손실                                  | implementer-prompt 에서 `mkdir -p` 명시 + 실패 시 BLOCKED 보고                                        |
| R2 | side-effect | 메인 세션 인터럽트로 end-of-run consolidator 미실행 → buffer 잔존 + footer 갱신 누락                    | 다음 세션 시작 시 `.js-super/changelog-buffer/<slug>/` 잔존 검출 → 사용자에게 복구 prompt              |
| R3 | breaking    | change-history schema 신규 entry type 추가 → 외부 grep/parser 깨짐                                     | 기존 5종 (`요구사항-수정` 등) 그대로 + 신규 (`검증` `릴리즈`) 추가만. 기존 entry 변형 0               |
| R4 | side-effect | buffer 디렉토리 cleanup 실패 시 leftover 누적                                                           | `.gitignore` 추가 + 다음 run 시작 시 stale 검출                                                       |
| R5 | side-effect | per-task 모드 슬림 entry 도입으로 사용자가 "코드 블록 직접 보고 싶다" 라고 push-back                    | schema에 trade-off 명시 + 옵션 escape hatch (`commit_policy: per-task-fat` 같은 별도 모드 v1.1.8 후보로 backlog) |
| R6 | breaking    | 인라인 모드 패턴 변경 → 기존 v1.1.6 plan dogfood 와 호환 안 됨                                         | 신규 plan 부터 적용. 과거 v1.1.6 plan 은 그대로 유지 (PRD 범위 밖 명시 따름)                          |
| R7 | race        | 다중 워크트리에서 같은 slug 의 buffer 디렉토리 충돌                                                     | buffer 경로에 `<slug>` 외 워크트리 ID 또는 BASE_SHA 7자 prefix 추가 (R7 mitigation은 implementer-prompt 에 명시) |

## 7. 테스트 전략

### 7.1 자동 (정적 grep + fixture)

- **G1**: 신규 스킬 본문에 새 schema 반영 — `grep -n "Changes Manifest" skills/js-super-subagent-driven-development/implementer-prompt.md` ≥1 매치
- **G2**: change-history 스킬에 신규 entry type 명시 — `grep -nE "^\| \[검증\] \|" skills/change-history/SKILL.md` ≥1 매치
- **G3**: `.gitignore` 에 buffer 경로 명시 — `grep "changelog-buffer" .gitignore`
- **F1 fixture**: Mock manifest YAML 3개 (task 1/2/3) → consolidator helper 가 batch entry 1개 생성 → schema 검증
- **F2 fixture**: 코드 0건 task manifest → `[검증]` entry 생성
- **F3 fixture**: per-task vs single 모드 schema 분기 검증 (per-task = 코드 블록 없음 / single = 코드 블록 있음)
- **F4 fixture**: 인터럽트 시뮬레이션 — 메인이 죽었다고 가정, buffer 디렉토리 잔존 → 다음 세션 시작 시 detection 동작
- **F5 fixture**: buffer 디렉토리 cleanup — consolidator 성공 후 `.js-super/changelog-buffer/<slug>/` 사라짐

### 7.2 인터랙티브 (수동 dogfood)

- **I1**: v1.1.7 자체 dogfood — 이 피처 plan 을 신규 batch 패턴으로 실행. self-validation.
- **I2**: 코드 0건 task (검증/tag-only) 가 자동으로 `[검증]` entry로 기록되는지 직접 확인
- **I3**: end-of-run "구현 요약" 메시지가 plan vs 실제 갭을 정확히 보여주는지 확인 (누락/초과/follow-up)
- **I4**: 인터럽트 시뮬레이션 — task 5/10 까지 진행 후 세션 종료 → 새 세션에서 buffer 복구 promprt 동작 확인

### 7.3 회귀 (기존 동작 유지)

- **R-1**: v1.1.6 dogfood plan 의 기존 변경이력 entry 17개는 그대로 유지 (마이그레이션 없음, AC 범위 밖)
- **R-2**: `commit_policy: single` / `none` 모드 plan 은 종전 fat schema (코드 블록 보존) 그대로 동작 — fixture F3 이 covers

---

## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-09 17:50] [개발방향-수정]
- **id**: CH-20260509-002
- **이유**: 신규 기술 설계 (v1.1.7 서브에이전트 변경이력 일괄정리)
- **무엇이**: 서브에이전트-변경이력-일괄정리-tech-design.md 전체 (§1 아키텍처 / §2 영향 파일 / §3 schema / §4 IF / §5 D1~D6 결정 + 4 후보 옵션 비교 / §6 R1~R7 위험 / §7 G1~G3 + F1~F5 + I1~I4 + R-1~R-2 테스트 전략)
- **영향범위**: 없음 (최초 생성). 다음 단계에서 writing-plans → implementation-plan 작성 시 task 분해 트리거됨. AC-1~5 모두 §2 또는 §4 매핑 완료 (verifying-spec gap=0 / conflict=0).
- **연관 항목**: CH-20260509-001 (requirements 신규 생성)
