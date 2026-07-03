---
commit_policy: per-task
---

# v1.1.15 — 브레인스토밍/디자인 흐름 슬림화 (6종 통합) 구현계획서

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` (Inline, recommended for ≤12 tasks) or `dj-superkit-subagent-driven-development` (Subagent, recommended for 13+ tasks). Steps use checkbox (`- [ ]`) syntax for tracking. Plan has 16 tasks total.

> **Bootstrap notice:** 이 plan 자체는 v1.1.14 sequential 패턴 (메인 직접 / inline) 으로 실행. 본 release 의 FR-1 (adaptive 7-topic) 과 FR-3 (브레인스토밍 라우터) 가 이 흐름 자체를 변경하지만, 자기 자신 적용은 다음 dogfood (외부 피처) 에서. v1.1.14 의 "자기 자신 wave-parallel 적용 X" 와 동일 원칙.

**Goal:** v1.1.9~v1.1.14 게이트/checklist 합리화 흐름의 자연스러운 연장으로 brainstorming/designing-direction 진입+진행 마찰 점 4건 (designing-direction 7-topic adaptive / Skill checklist transition 잔존 / brainstorm 라우터 / preflight 실패 사용자 게이트) 한 릴리즈로 묶어 슬림화.

**Architecture:** Layer 1 — skill 본문 (Markdown) 7 파일 / Layer 2 — `scripts/preflight.py` (Python helper, NamedTuple `human_reason` 필드 추가) / Layer 3 — CLAUDE.md 결합 메모. 신규 모듈 X. AI judgment 우선 (deterministic classifier 도입 X).

**Tech Stack:** Markdown (skill body), Python 3.13 (NamedTuple, pathlib), pytest (TDD), bash (preflight one-liner).

**Spec inputs:**
- `flow-slim-requirements.md` — FR-1 (adaptive 7-topic) / FR-2 (transition reminder + items 9+10 통합) / FR-3 (Step 0 라우터) / FR-4 (preflight 실패 게이트) / FR-5 (docs-pretty pre-review timing 통일) / FR-6 (TaskCreate 이름 사용자 친화화). AC-1~17.
- `flow-slim-tech-design.md` — D-T1~11 결정 / R1~R10 위험 / F1~F7 정적 + G1~G4 + H5/H6 dogfood + ~9 unit test 추가.

---

## 1. 단계별 작업

### Task 1: scripts/preflight.py — `PreflightResult.human_reason` 필드 추가 + 한국어 reason 매핑

**Files:**
- Modify: `scripts/preflight.py:12-14` (PreflightResult NamedTuple)
- Modify: `scripts/preflight.py:45-87` (4 helper 의 reason 인자에 한국어 1줄 동반)
- Test: `scripts/tests/test_preflight.py` (Task 2 에서 단독 처리)

**Model**: sonnet

- [ ] **Step 1: failing test 작성** — `scripts/tests/test_preflight.py` 끝에 임시 sentinel 추가:

```python
def test_preflight_result_has_human_reason_field():
    from scripts.preflight import PreflightResult
    r = PreflightResult(False, "file_not_found")
    assert hasattr(r, "human_reason")
    assert r.human_reason == ""  # default empty string

def test_docs_pretty_check_returns_human_reason_korean():
    from pathlib import Path
    from scripts.preflight import docs_pretty_check
    r = docs_pretty_check(Path("/tmp/__nonexistent__-requirements.md"))
    assert r.ok is False
    assert "대상 파일이 존재하지 않습니다" in r.human_reason
```

- [ ] **Step 2: 테스트 fail 확인** — `source .venv/bin/activate && pytest scripts/tests/test_preflight.py::test_preflight_result_has_human_reason_field scripts/tests/test_preflight.py::test_docs_pretty_check_returns_human_reason_korean -v` → **FAIL** (`AttributeError: 'PreflightResult' object has no attribute 'human_reason'`).

- [ ] **Step 3: PreflightResult 에 `human_reason` 필드 추가**

**원본** (`scripts/preflight.py:12-14`):

```python
class PreflightResult(NamedTuple):
    ok: bool
    reason: str
```

**수정 후**:

```python
class PreflightResult(NamedTuple):
    ok: bool
    reason: str
    human_reason: str = ""  # v1.1.15+ optional 한국어 1줄 설명. backward compat: default 빈 문자열.
```

- [ ] **Step 4: 4 helper 의 fail 케이스에 `human_reason` 한국어 동반**

**원본** (`scripts/preflight.py:45-53`, `docs_pretty_check`):

```python
def docs_pretty_check(file_path: Path) -> PreflightResult:
    if not file_path.exists():
        return PreflightResult(False, f"file not found: {file_path}")
    if not _FEATURE_MD_PATTERN.match(str(file_path)):
        return PreflightResult(False, "filename doesn't match feature MD pattern")
    text = file_path.read_text(encoding="utf-8")
    if _has_changelog_entries(text):
        return PreflightResult(False, "변경이력 footer not empty (doc is live)")
    return PreflightResult(True, "ok")
```

**수정 후**:

```python
def docs_pretty_check(file_path: Path) -> PreflightResult:
    if not file_path.exists():
        return PreflightResult(
            False,
            f"file not found: {file_path}",
            f"대상 파일이 존재하지 않습니다: {file_path}",
        )
    if not _FEATURE_MD_PATTERN.match(str(file_path)):
        return PreflightResult(
            False,
            "filename doesn't match feature MD pattern",
            "파일명이 feature MD 패턴 (-requirements.md / -tech-design.md / -implementation-plan.md) 과 일치하지 않습니다",
        )
    text = file_path.read_text(encoding="utf-8")
    if _has_changelog_entries(text):
        return PreflightResult(
            False,
            "변경이력 footer not empty (doc is live)",
            "이미 변경이력 entry 가 존재합니다 (live doc). docs-pretty 는 최초 생성 단계에서만 발화합니다",
        )
    return PreflightResult(True, "ok", "정상")
```

(`code_pretty_check`, `execute_plan_mode_check`, `subagent_task_entry_check` 도 동일 패턴으로 한국어 `human_reason` 동반 — 4 helper 모두.)

- [ ] **Step 5: 테스트 PASS 확인** — `pytest scripts/tests/test_preflight.py -v` → **PASS** (기존 9 + 신규 2 = 11 + 추가 검증). 4 helper 의 모든 fail/ok path 가 `human_reason` 동반 확인.

- [ ] **Step 6: Commit (per-task)** — git-fast 모드. `git add scripts/preflight.py scripts/tests/test_preflight.py && git commit -m "feat(preflight): PreflightResult.human_reason 필드 추가 (FR-4)"`

---

### Task 2: scripts/tests/test_preflight.py — 4 helper × fail 케이스 한국어 검증 추가

**Files:**
- Modify: `scripts/tests/test_preflight.py` (~끝부분, 신규 test 5~7개 추가)

**Model**: sonnet

- [ ] **Step 1: failing test 추가** — 기존 fail-path 검증을 `human_reason` 까지 확장:

```python
def test_code_pretty_check_human_reason_for_wrong_filename():
    from pathlib import Path
    from scripts.preflight import code_pretty_check
    r = code_pretty_check(Path("/tmp/foo-requirements.md"))
    assert r.ok is False
    assert "implementation-plan" in r.human_reason  # 한국어 1줄 안내

def test_code_pretty_check_human_reason_for_no_modified_blocks(tmp_path):
    from scripts.preflight import code_pretty_check
    p = tmp_path / "x-implementation-plan.md"
    p.write_text("# title\n## 변경이력\n", encoding="utf-8")
    r = code_pretty_check(p)
    assert r.ok is False
    assert "수정 후" in r.human_reason

def test_execute_plan_mode_check_human_reason_for_missing_plan():
    from pathlib import Path
    from scripts.preflight import execute_plan_mode_check
    r = execute_plan_mode_check(Path("/tmp/__nonexistent__-implementation-plan.md"))
    assert r.ok is False
    assert "구현계획서를 찾을 수 없습니다" in r.human_reason

def test_subagent_entry_check_human_reason_for_wrong_policy(tmp_path):
    from scripts.preflight import subagent_task_entry_check
    p = tmp_path / "x-implementation-plan.md"
    p.write_text("---\ncommit_policy: single\n---\n# title\n", encoding="utf-8")
    r = subagent_task_entry_check(p)
    assert r.ok is False
    assert "per-task" in r.human_reason
```

- [ ] **Step 2: 테스트 fail 확인** — `pytest scripts/tests/test_preflight.py -v` → **PASS** (Task 1 의 helper 변경이 모든 fail 케이스를 커버하면 즉시 PASS, 그렇지 않으면 fail 메시지 보고 Task 1 helper 보강).

- [ ] **Step 3: 누락된 fail-path 의 `human_reason` 보강** — Task 1 의 4 helper 에서 누락된 한국어 메시지가 있으면 `scripts/preflight.py` 보강. (예: `code_pretty_check` 의 "no '수정 후' code blocks found" → `"'수정 후' 코드 블록이 없습니다 (prettify 대상 0건)"`).

- [ ] **Step 4: 테스트 PASS 확인** — `pytest scripts/tests/test_preflight.py -v` → 모두 PASS. 새로 추가된 4 test + 기존 11 = 총 15+ PASS.

- [ ] **Step 5: Commit** — `git add scripts/tests/test_preflight.py scripts/preflight.py && git commit -m "test(preflight): human_reason 한국어 검증 4 helper 케이스 (FR-4)"`

---

### Task 3: skills/docs-pretty/SKILL.md — Pre-flight 섹션 통일 boilerplate

**Files:**
- Modify: `skills/docs-pretty/SKILL.md:54-72` (Step 1 — Pre-flight check)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep 시뮬레이션** — `grep -nE "AskUserQuestion|exit code != 0,1" skills/docs-pretty/SKILL.md` → **현재 매치 0건** (boilerplate 미박힘). Task 끝에서 매치 ≥ 2 기대.

- [ ] **Step 2: Pre-flight 섹션 교체**

**원본** (`skills/docs-pretty/SKILL.md:54-72`):

```markdown
### Step 1 — Pre-flight check (v1.1.14+ deterministic)

Before dispatching, run the deterministic helper:

​```bash
source .venv/bin/activate && python -c "
import sys
from pathlib import Path
from scripts.preflight import docs_pretty_check
result = docs_pretty_check(Path('<TARGET>'))
print(f'ok={result.ok} reason={result.reason}')
sys.exit(0 if result.ok else 1)
"
​```

- exit code 0 → 검증 통과, Step 2 dispatch 진행
- exit code 1 → reason 한 줄 노출 후 즉시 종료. **메인은 검증 retry 또는 LLM 재추론 X**

이 단계는 v1.1.14 에서 LLM 추론 → 코드로 이관. 동일 검사 (file 존재 / 변경이력 footer 비어있음 / filename 패턴) 가 deterministic 으로 처리되어 응답 속도 + 토큰 비용 모두 0 수준. 자세한 룰은 `scripts/preflight.py:docs_pretty_check`.
```

**수정 후**:

````markdown
### Step 1 — Pre-flight check (v1.1.15+ user-gate)

Before dispatching, run the deterministic helper. **stderr 도 capture** — 실패 시 사용자에게 그대로 노출:

```bash
source .venv/bin/activate && python -c "
import sys
from pathlib import Path
from scripts.preflight import docs_pretty_check
result = docs_pretty_check(Path('<TARGET>'))
print(f'ok={result.ok} reason={result.reason} | {result.human_reason}')
sys.exit(0 if result.ok else 1)
" 2>&1
```

**exit code 분기 (v1.1.15 user-gate)**:

- **exit 0** → 검증 통과, Step 2 dispatch 진행.
- **exit 1** (helper semantic fail, ok=False) → `human_reason` 한 줄 노출 후 `AskUserQuestion` 게이트:
  - choices:
    - `"수정 후 재시도"` → 사용자가 doc 수정 후 메인이 helper 재호출.
    - `"강제 진행 (위험)"` → preflight 무시하고 Step 2 진입. 메인이 `⚠️ preflight 우회. <reason> 무시하고 진행.` 한 줄 안내.
    - `"스킵 (이번만)"` → docs-pretty 단계 스킵, caller 에게 abnormal return (caller 가 change-history 직행 결정).
- **exit ≠ 0,1** (invocation 실패: 127 / 2 / etc., harness 환경 이슈) → stderr 전문 노출 + `AskUserQuestion` 게이트:
  - 메시지: `"preflight helper invocation 실패 (exit <code>): <stderr 전문>. 어떻게 할까요?"`
  - choices:
    - `"직접 디버깅"` → 사용자가 환경 점검 (venv / python 경로 / `scripts/preflight.py` 존재) 후 알려주면 메인이 재호출.
    - `"skill 단계 스킵"` → preflight 우회하고 Step 2 진입 (위와 동일).

자세한 룰은 `scripts/preflight.py:docs_pretty_check`. helper 검사: file 존재 / 변경이력 footer 비어있음 / filename 패턴.
````

- [ ] **Step 3: 정적 grep 검증** — `grep -nE "AskUserQuestion|exit ≠ 0,1|강제 진행" skills/docs-pretty/SKILL.md` → 매치 ≥ 2 PASS. `grep -c "v1.1.15+ user-gate" skills/docs-pretty/SKILL.md` → 1.

- [ ] **Step 4: Commit** — `git add skills/docs-pretty/SKILL.md && git commit -m "feat(docs-pretty): Pre-flight 사용자 게이트 boilerplate 통일 (FR-4)"`

---

### Task 4: skills/code-pretty/SKILL.md — Pre-flight 섹션 동일 boilerplate

**Files:**
- Modify: `skills/code-pretty/SKILL.md:44-64` (Step 1 — Pre-flight check)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `grep -nE "AskUserQuestion|exit ≠ 0,1" skills/code-pretty/SKILL.md` → 매치 0건.

- [ ] **Step 2: Pre-flight 섹션 교체** — Task 3 와 동일 boilerplate 패턴, helper 명만 `code_pretty_check` 로 치환. **추가 한 줄**: code-pretty 의 캐일러 책임 명시 (`Caller 책임: verifying-spec 직전 통과`) 는 그대로 유지.

**원본** (`skills/code-pretty/SKILL.md:44-64`):

```markdown
### Step 1 — Pre-flight check (v1.1.14+ deterministic)

Before dispatching, run the deterministic helper:

​```bash
source .venv/bin/activate && python -c "
import sys
from pathlib import Path
from scripts.preflight import code_pretty_check
result = code_pretty_check(Path('<TARGET>'))
print(f'ok={result.ok} reason={result.reason}')
sys.exit(0 if result.ok else 1)
"
​```

- exit code 0 → 검증 통과, Step 2 dispatch 진행
- exit code 1 → reason 노출 후 즉시 종료

**Caller 책임 (helper 가 검증 X)**: verifying-spec 가 직전에 통과했는지 — 이건 writing-plans 흐름의 책임이고 helper 가 검사할 수 없음. 호출자가 보장.

helper 의 검사: file 존재 / 변경이력 footer 비어있음 / filename `*-implementation-plan.md` / 최소 1개 `**수정 후**` 블록 존재. 자세히는 `scripts/preflight.py:code_pretty_check`.
```

**수정 후**:

````markdown
### Step 1 — Pre-flight check (v1.1.15+ user-gate)

Before dispatching, run the deterministic helper:

```bash
source .venv/bin/activate && python -c "
import sys
from pathlib import Path
from scripts.preflight import code_pretty_check
result = code_pretty_check(Path('<TARGET>'))
print(f'ok={result.ok} reason={result.reason} | {result.human_reason}')
sys.exit(0 if result.ok else 1)
" 2>&1
```

**exit code 분기 (v1.1.15 user-gate)**:

- **exit 0** → 검증 통과, Step 2 dispatch 진행.
- **exit 1** (helper semantic fail) → `human_reason` 노출 후 `AskUserQuestion` 게이트:
  - `"수정 후 재시도"` / `"강제 진행 (위험)"` (메인이 `⚠️ preflight 우회. <reason> 무시.` 한 줄 안내) / `"스킵 (이번만)"` (caller 에게 abnormal return).
- **exit ≠ 0,1** (invocation 실패) → stderr 전문 + `AskUserQuestion` 게이트:
  - `"직접 디버깅"` / `"skill 단계 스킵"`.

**Caller 책임 (helper 가 검증 X)**: verifying-spec 가 직전에 통과했는지 — 이건 writing-plans 흐름의 책임이고 helper 가 검사할 수 없음. 호출자가 보장.

helper 의 검사: file 존재 / 변경이력 footer 비어있음 / filename `*-implementation-plan.md` / 최소 1개 `**수정 후**` 블록 존재. 자세히는 `scripts/preflight.py:code_pretty_check`.
````

- [ ] **Step 3: 정적 grep 검증** — 매치 ≥ 2 PASS.

- [ ] **Step 4: Commit** — `git add skills/code-pretty/SKILL.md && git commit -m "feat(code-pretty): Pre-flight 사용자 게이트 boilerplate 통일 (FR-4)"`

---

### Task 5: skills/executing-plans/SKILL.md — Mode-check Pre-flight 섹션 통일

**Files:**
- Modify: `skills/executing-plans/SKILL.md:41-73` (HARD-GATE 의 mode-check 섹션)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `grep -nE "AskUserQuestion|exit ≠ 0,1" skills/executing-plans/SKILL.md` → 매치 0건.

- [ ] **Step 2: HARD-GATE mode-check 1번 항목 교체** — 기존 항목 1 (Run mode-check helper) 의 분기 부분만 user-gate 로:

**원본** (`skills/executing-plans/SKILL.md:44-62`, mode-check helper 직후 분기 부분):

```markdown
이 helper 가 plan frontmatter 의 `commit_policy` 를 deterministic 으로 읽어 반환. exit code 0 시 reason 에 `commit_policy=per-task` 형식. 메인은 reason 의 policy 값으로 모드 분기:
   - `per-task` → candidate mode = git-fast
   - `single` → candidate mode = memory-fallback (all tasks → one commit at end)
   - `none` → candidate mode = memory-fallback (no commits during run)

기존 LLM 산문 추론 단계 제거 (v1.1.14). frontmatter 파싱 결과를 그대로 신뢰. 자세한 룰은 `scripts/preflight.py:execute_plan_mode_check`.
```

**수정 후**:

````markdown
이 helper 가 plan frontmatter 의 `commit_policy` 를 deterministic 으로 읽어 반환.

**exit code 분기 (v1.1.15 user-gate)**:

- **exit 0** → reason 에 `commit_policy=per-task` 형식. 메인은 policy 값으로 모드 분기:
  - `per-task` → candidate mode = git-fast
  - `single` → candidate mode = memory-fallback (all tasks → one commit at end)
  - `none` → candidate mode = memory-fallback (no commits during run)
- **exit 1** (semantic fail — plan not found) → `human_reason` 노출 후 `AskUserQuestion` 게이트:
  - `"수정 후 재시도"` (사용자가 plan 경로 확인) / `"강제 진행 (위험)"` (사용자가 입력한 plan 경로 직접 사용 — 메인이 추가 안내) / `"스킵 (이번만)"` (executing-plans 종료).
- **exit ≠ 0,1** (invocation 실패) → stderr 노출 + `AskUserQuestion` 게이트:
  - `"직접 디버깅"` / `"skill 단계 스킵"`.

기존 LLM 산문 추론 단계 제거 (v1.1.14). frontmatter 파싱 결과를 그대로 신뢰. 자세한 룰은 `scripts/preflight.py:execute_plan_mode_check`.
````

- [ ] **Step 3: 정적 grep 검증** — 매치 ≥ 2 PASS.

- [ ] **Step 4: Commit** — `git add skills/executing-plans/SKILL.md && git commit -m "feat(executing-plans): mode-check Pre-flight 사용자 게이트 (FR-4)"`

---

### Task 6: skills/dj-superkit-subagent-driven-development/SKILL.md — Entry Guard 사용자 게이트

**Files:**
- Modify: `skills/dj-superkit-subagent-driven-development/SKILL.md:53-71` (## Entry Guard)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `grep -nE "AskUserQuestion|exit ≠ 0,1" skills/dj-superkit-subagent-driven-development/SKILL.md` → 매치 0건 (또는 Plan Analysis 섹션의 다른 매치만).

- [ ] **Step 2: Entry Guard 섹션 교체**

**원본** (`skills/dj-superkit-subagent-driven-development/SKILL.md:53-71`):

```markdown
## Entry Guard (v1.1.14+)

이 skill 호출 시 메인은 즉시 helper 검사:

​```bash
source .venv/bin/activate && python -c "
import sys
from pathlib import Path
from scripts.preflight import subagent_task_entry_check
result = subagent_task_entry_check(Path('<PLAN_PATH>'))
print(f'ok={result.ok} reason={result.reason}')
sys.exit(0 if result.ok else 1)
"
​```

- exit code 0 → Plan Analysis 단계 진입
- exit code 1 → 한 줄 안내 후 즉시 종료. 예: `❌ <reason>. /write-plan 먼저 실행하세요.`

이유: helper 가 (a) plan 존재, (b) `commit_policy: per-task` 두 조건 모두 검사 — 단일 호출. plan 없는 dispatch 또는 `single`/`none` mode plan 모두 deterministic 거부.
```

**수정 후**:

````markdown
## Entry Guard (v1.1.15+ user-gate)

이 skill 호출 시 메인은 즉시 helper 검사:

```bash
source .venv/bin/activate && python -c "
import sys
from pathlib import Path
from scripts.preflight import subagent_task_entry_check
result = subagent_task_entry_check(Path('<PLAN_PATH>'))
print(f'ok={result.ok} reason={result.reason} | {result.human_reason}')
sys.exit(0 if result.ok else 1)
" 2>&1
```

**exit code 분기 (v1.1.15 user-gate)**:

- **exit 0** → Plan Analysis 단계 진입.
- **exit 1** (semantic fail — plan 없음 또는 `commit_policy ≠ per-task`) → `human_reason` 노출 후 `AskUserQuestion` 게이트:
  - `"수정 후 재시도"` (사용자가 plan 작성 / commit_policy 변경 후 메인 재호출) / `"강제 진행 (위험)"` (단, 매우 위험 — plan 없으면 Wave Build 자체 불가, 메인이 한 번 더 안내) / `"스킵 (이번만)"` (subagent 모드 포기, executing-plans inline 으로 fallback 제안).
- **exit ≠ 0,1** (invocation 실패) → stderr 노출 + `AskUserQuestion` 게이트:
  - `"직접 디버깅"` / `"skill 단계 스킵"` (inline fallback).

이유: helper 가 (a) plan 존재, (b) `commit_policy: per-task` 두 조건 모두 검사 — 단일 호출. plan 없는 dispatch 또는 `single`/`none` mode plan 모두 deterministic 거부 + 사용자 확인.
````

- [ ] **Step 3: 정적 grep 검증** — 매치 ≥ 2 PASS.

- [ ] **Step 4: Commit** — `git add skills/dj-superkit-subagent-driven-development/SKILL.md && git commit -m "feat(subagent-dd): Entry Guard 사용자 게이트 (FR-4)"`

---

### Task 7: skills/brainstorming/SKILL.md — Step 0 라우터 추가 (FR-3) + Checklist 끝 reminder (FR-2)

**Files:**
- Modify: `skills/brainstorming/SKILL.md:23-37` (Checklist 본문 + 끝 한 줄)
- Modify: `skills/brainstorming/SKILL.md` (Process Flow 다이어그램 — Step 0 노드 추가)
- Modify: `skills/brainstorming/SKILL.md` 본문 (Step 0 섹션 신규 추가, "## Mode Selection" 섹션 직전)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `grep -nE "Step 0|Auto-routing to og-brainstorming|Before invoking the next skill" skills/brainstorming/SKILL.md` → 매치 0건. Task 끝에서 모두 매치 ≥ 1.

- [ ] **Step 2: Checklist 1번 직전에 0번 (Step 0 라우터) 추가**

**원본** (`skills/brainstorming/SKILL.md:23-37`):

```markdown
You MUST create a TaskCreate task for each of these items and complete them in order:

1. **Explore project context** — files, docs, recent commits
2. **Confirm feature name + slug** — one question, then create `docs/features/YYYY-MM-DD-<slug>/`
3. **Mode selection gate** — ask user PRD (default) or Socratic. Parse intent (any language). On ambiguous reply, default to PRD with a one-line note. See "Mode Selection" below.
4. **Run mode-specific dialogue**:
   - **[PRD mode]** Feature category mini-question → **Visual Companion offer** (if UI/layout/visual feature based on category — own message, mode-aware trigger) → Question plan agreement → Adaptive PRD questions (only the agreed subset). See "PRD Adaptive Planning" below.
   - **[Socratic mode]** **Visual Companion offer** (if visual questions ahead — own message) → Free-form upstream-style dialogue: one question at a time, propose 2-3 approaches with tradeoffs, section-by-section approval. See "Socratic Mode" below.
5. **Self-review** — mode-specific (PRD: 6-item PRD scan + 4-item abstract scan; Socratic: 4-item abstract scan only)
6. **User reviews <slug>-requirements.md** — show the RAW (un-prettified) file, get approval (loop until OK; on changes → revise → re-show raw)
7. **Invoke docs-pretty skill** — format-only pass (Sonnet subagent) on the APPROVED draft, AFTER user approval and BEFORE change-history. Single shot per feature (final-1회). Stops once first change-history entry is logged.
8. **Invoke change-history skill** — append first `[요구사항-수정]` entry
9. **Auto-proceed to designing-direction (v1.1.9+ — gate removed)** — Right after the change-history entry is logged, auto-invoke `designing-direction` via the Skill tool with a one-line interrupt-notice. On user "stop"/"멈춰"/"잠깐" → exit cleanly with notice telling the user to run /design later.

If you find yourself skipping ahead, stop and create the missing task.
```

**수정 후**:

```markdown
You MUST create a TaskCreate task for each of these items and complete them in order:

0. **Entry Router (v1.1.15+, FR-3)** — 사용자 입력에 명시적 small 신호 감지 시 즉시 og-brainstorming auto-invoke + notice 한 줄. 그 외 → AskUserQuestion 게이트 (og- / dj-superkit 양자택일). 자세한 룰은 "Entry Router" 섹션 참조.
1. **Explore project context** — files, docs, recent commits
2. **Confirm feature name + slug** — one question, then create `docs/features/YYYY-MM-DD-<slug>/`
3. **Mode selection gate** — ask user PRD (default) or Socratic. Parse intent (any language). On ambiguous reply, default to PRD with a one-line note. See "Mode Selection" below.
4. **Run mode-specific dialogue**:
   - **[PRD mode]** Feature category mini-question → **Visual Companion offer** (if UI/layout/visual feature based on category — own message, mode-aware trigger) → Question plan agreement → Adaptive PRD questions (only the agreed subset). See "PRD Adaptive Planning" below.
   - **[Socratic mode]** **Visual Companion offer** (if visual questions ahead — own message) → Free-form upstream-style dialogue: one question at a time, propose 2-3 approaches with tradeoffs, section-by-section approval. See "Socratic Mode" below.
5. **Self-review** — mode-specific (PRD: 6-item PRD scan + 4-item abstract scan; Socratic: 4-item abstract scan only)
6. **User reviews <slug>-requirements.md** — show the RAW (un-prettified) file, get approval (loop until OK; on changes → revise → re-show raw)
7. **Invoke docs-pretty skill** — format-only pass (Sonnet subagent) on the APPROVED draft, AFTER user approval and BEFORE change-history. Single shot per feature (final-1회). Stops once first change-history entry is logged.
8. **Invoke change-history skill** — append first `[요구사항-수정]` entry
9. **Auto-proceed to designing-direction (v1.1.9+ — gate removed)** — Right after the change-history entry is logged, auto-invoke `designing-direction` via the Skill tool with a one-line interrupt-notice. On user "stop"/"멈춰"/"잠깐" → exit cleanly with notice telling the user to run /design later.

If you find yourself skipping ahead, stop and create the missing task.

**Before invoking the next skill via Skill tool, mark ALL checklist TaskCreate items as completed (in_progress → completed). The Skill tool transition does NOT auto-complete prior tasks. (v1.1.15+, FR-2)**
```

- [ ] **Step 3: "## Entry Router (v1.1.15+, FR-3)" 섹션 신규 — "## Mode Selection" 직전에 추가**

**원본** (`skills/brainstorming/SKILL.md` "## Mode Selection" 섹션 직전):

(아무 섹션 없음 — Mode Selection 위 직접 다른 산문)

**수정 후** (Mode Selection 직전 신규 섹션):

````markdown
## Entry Router (v1.1.15+, FR-3)

dj-superkit:brainstorming 진입 시 1순위 발화. `/brainstorm` slash command 진입 / 자연어 진입 ("…를 만들어 / 브레인스토밍 시작해") 모두 동일 path.

### 라우팅 룰

**1. 명시적 small 신호 감지 → og-brainstorming auto-invoke + notice 한 줄**

다음 중 하나라도 사용자 입력에 명시되면 small 판정:

- **small 키워드**: `간단`, `잠깐`, `한 줄`, `단순`, `og로`, `og-`, `가볍게`
- **단일 파일/단일 함수 변경 명시**: 예 — "`README.md` 한 줄 수정", "`utils.py:foo` 만 수정"
- **메타 워크플로우 / 순수 config 변경 명시**: 예 — "`.gitignore` 추가", "tsconfig 옵션 한 개 추가"

→ 즉시 `og-brainstorming` skill 을 Skill tool 로 invoke. 직전에 한 줄 notice 노출:

```
ℹ️ Auto-routing to og-brainstorming ('<감지된 키워드 / 신호>'). Switch back? "dj-superkit" 라고 답하세요.
```

사용자가 "dj-superkit" 라고 응답하면 라우터 무시하고 본 skill 의 Checklist 1번 (Explore) 으로 진입.

**2. 그 외 모두 → AskUserQuestion 게이트**

명시적 small 신호 부재 (= 의도파악력 약한 케이스 포함). AI 가 "이건 분명 large 다" 판정할 필요 X. AskUserQuestion 호출:

```json
{
  "question": "이 피처는 og-brainstorming(가벼운 단발) 또는 dj-superkit:brainstorming(3-MD 풀 트랙) 중 어느 모드로 진행할까요?",
  "header": "진입 모드",
  "multiSelect": false,
  "options": [
    {"label": "og-brainstorming", "description": "가벼운 단발 / upstream superpowers 원본 / 자유 탐색"},
    {"label": "dj-superkit:brainstorming", "description": "3-MD 풀 트랙 / PRD + tech-design + plan / 변경이력 + 위험 주석"}
  ]
}
```

사용자 선택 → og 면 og-brainstorming Skill invoke / dj-superkit 면 본 skill Checklist 1번 진입.

### 의도파악력 약해도 됨

AI 가 small/large 분명 판정할 필요 없음. 명시적 small 신호 catch 만 정확하면 나머지는 게이트로 사용자 결정. false positive 안 발생.

### og-brainstorming 본문 unchanged

라우터는 본 skill 진입에만 박힘. og-brainstorming SKILL.md 는 영향 X.
````

- [ ] **Step 4: Process Flow 다이어그램 노드 추가** — 기존 다이어그램의 entry 직전에 "Step 0 Router" 분기 노드 삽입.

**원본** (`skills/brainstorming/SKILL.md` Process Flow 첫 줄):

```dot
"Explore project context" [shape=box];
```

**수정 후** (그 직전에 추가):

```dot
"Step 0 Router (FR-3)\n명시적 small 신호?" [shape=diamond];
"Auto-invoke og-brainstorming\n+ notice" [shape=box];
"AskUserQuestion 게이트\n(og / dj-superkit)" [shape=diamond];
"Step 0 Router (FR-3)\n명시적 small 신호?" -> "Auto-invoke og-brainstorming\n+ notice" [label="small"];
"Step 0 Router (FR-3)\n명시적 small 신호?" -> "AskUserQuestion 게이트\n(og / dj-superkit)" [label="그 외"];
"AskUserQuestion 게이트\n(og / dj-superkit)" -> "Auto-invoke og-brainstorming\n+ notice" [label="og"];
"AskUserQuestion 게이트\n(og / dj-superkit)" -> "Explore project context" [label="dj-superkit"];
```

(메인은 기존 다이어그램 의 entry edge `"Explore project context"` 들어오는 첫 노드를 위 새 노드들로 link 만 재연결.)

- [ ] **Step 5: 정적 grep 검증** — `grep -nE "Step 0 Router|Auto-routing to og-brainstorming|Before invoking the next skill" skills/brainstorming/SKILL.md` → 모두 매치 ≥ 1.

- [ ] **Step 6: Commit** — `git add skills/brainstorming/SKILL.md && git commit -m "feat(brainstorming): Step 0 entry router + transition reminder (FR-2 + FR-3)"`

---

### Task 8: skills/designing-direction/SKILL.md — Step 3 adaptive (FR-1) + items 9+10 통합 (FR-2) + Checklist 끝 reminder (FR-2) + Step 2 Survey 슬림 (FR-1)

**Files:**
- Modify: `skills/designing-direction/SKILL.md:14-30` (Checklist)
- Modify: `skills/designing-direction/SKILL.md` (Process / Step 2 Survey wording / Step 3 dialogue)
- Modify: `skills/designing-direction/SKILL.md` (Process Flow 다이어그램)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `grep -nE "Step 0 announce|adaptive|항상 활성|조건부 활성|Before invoking the next skill" skills/designing-direction/SKILL.md` → 매치 0건.

- [ ] **Step 2: Checklist 본문 교체 (item 9+10 통합 + Step 0 announce 추가 + 끝 reminder)**

**원본** (`skills/designing-direction/SKILL.md:14-30`):

```markdown
## Checklist

You MUST create a TaskCreate task for each of these items and complete them in order:

1. **Verify input** — confirm <slug>-requirements.md exists (HARD-GATE if not)
2. **Survey existing code** — Grep/Read impacted areas for each FR
3. **Run technical design questions** — architecture (2-3 candidates) → impacted components → data model → external interfaces → key decisions + alternatives → risk candidates → test strategy
4. **Self-review (internal)** — FR mapping coverage, alternatives present, risk categorization (no user prompt yet)
5. **Run verifying-spec FIRST** (with Tolerance for missing skill) — main agent runs A+C verification, produces 4-axis report internally
6. **Single combined approval gate** — show the full RAW `<slug>-tech-design.md` AND the verify-spec report in one message; ask once "Approve and proceed? — yes / no". On `no` → revise → loop back to step 4 (Self-review → re-verify → re-show RAW).
7. **Invoke docs-pretty skill** — format pass on the APPROVED draft (Sonnet subagent). Runs AFTER user approval and BEFORE change-history. Single shot per feature (final-1회). Stops once first change-history entry is logged.
8. **Invoke change-history skill** — append first `[개발방향-수정]` entry
9. **Ask proceed-to-writing-plans gate (v1.1.12+ — restored)** — change-history 직후 사용자에게 명시적 yes/no 게이트.
10. **On approval → invoke writing-plans via Skill tool. On hold → exit with notice telling the user to run /write-plan later.**

If you find yourself skipping ahead, stop and create the missing task.
```

**수정 후**:

```markdown
## Checklist

You MUST create a TaskCreate task for each of these items and complete them in order:

1. **Verify input** — confirm <slug>-requirements.md exists (HARD-GATE if not)
2. **Survey existing code (v1.1.15+ slim)** — `<slug>-requirements.md` §2 (영향 컴포넌트) 먼저 Read. 추가 grep/Read 는 tech-design 결정 (아키텍처 / data flow / pattern) 깊이 부족할 때만.
3. **Adaptive 7-topic dialogue (v1.1.15+, FR-1)** — `<slug>-requirements.md` 읽고 활성/비활성 토픽 판정 후 한 줄 announce. 항상 활성 4개 (1 아키텍처 / 2 컴포넌트 / 5 결정+대안 / 6 위험), 조건부 3개 (3 데이터 모델 / 4 외부 인터페이스 / 7 테스트 전략). 자세한 룰은 "Adaptive Topics" 섹션 참조.
4. **Self-review (internal)** — FR mapping coverage, alternatives present, risk categorization (no user prompt yet)
5. **Run verifying-spec FIRST** (with Tolerance for missing skill) — main agent runs A+C verification, produces 4-axis report internally
6. **Single combined approval gate** — show the full RAW `<slug>-tech-design.md` AND the verify-spec report in one message; ask once "Approve and proceed? — yes / no". On `no` → revise → loop back to step 4 (Self-review → re-verify → re-show RAW).
7. **Invoke docs-pretty skill** — format pass on the APPROVED draft (Sonnet subagent). Runs AFTER user approval and BEFORE change-history. Single shot per feature (final-1회). Stops once first change-history entry is logged.
8. **Invoke change-history skill** — append first `[개발방향-수정]` entry
9. **Ask proceed-to-writing-plans gate (v1.1.12+ — restored)** — change-history 직후 사용자에게 명시적 yes/no 게이트. On `yes` → invoke writing-plans via Skill tool. On `no` → exit with notice telling the user to run /write-plan later.

If you find yourself skipping ahead, stop and create the missing task.

**Before invoking the next skill via Skill tool, mark ALL checklist TaskCreate items as completed (in_progress → completed). The Skill tool transition does NOT auto-complete prior tasks. (v1.1.15+, FR-2)**
```

→ item 10 제거됨 (item 9 에 통합). Checklist 9 items 로 축소.

- [ ] **Step 3: "## Adaptive Topics (v1.1.15+, FR-1)" 섹션 신규 추가** — 기존 "## Process (detail)" 섹션 직전에:

**수정 후** (Process detail 직전 신규 섹션):

````markdown
## Adaptive Topics (v1.1.15+, FR-1)

Step 3 의 7-topic dialogue 를 사용자 마찰 줄이기 위해 adaptive 진행. 메인 에이전트가 `<slug>-requirements.md` 본문을 읽고 판단.

### 항상 활성 (4개)

- 1 아키텍처
- 2 영향 컴포넌트
- 5 결정+대안 비교
- 6 위험 (preliminary)

### 조건부 활성 (3개) — 메인 판단

- **3 데이터 모델** — DB / 스키마 / 마이그레이션 / 영구 저장 / 외부 시스템 데이터 교환을 implicit/explicit 시사하면 활성. 메타 워크플로우 / 순수 함수 / 산문 처리만이면 비활성.
- **4 외부 인터페이스** — REST / GraphQL / webhook / 이벤트 발행 / 외부 노출 시사하면 활성. 내부 모듈 간 호출만이면 비활성.
- **7 테스트 전략** — FR 수가 많거나 (≥3), 위험 카테고리 다수, 다중 파일 영향이면 활성. trivial 변경 / 단일 함수면 비활성.

### Step 0 announce — 항상 노출

판단 직후 사용자에게 한 줄 노출 (case 무관, 전부 활성이든 비활성 있든):

```
ℹ️ 활성 토픽: 1,2,3,5,6 / 비활성: 4 외부IF, 7 테스트전략 (이유: 내부 모듈 변경, 단일 함수). 추가 활성 필요시 알려주세요.
```

→ white box / override 시점 일관. 사용자가 즉시 catch + 활성 추가 요청 가능.

### 비활성 토픽 처리

`<slug>-tech-design.md` 의 해당 섹션은 다음 형식으로 한 줄만 박음:

```markdown
## 3. 데이터 모델/스키마 변경 — N/A: 본 피처는 DB/스키마 무관 (skill 본문 + Python helper 변경)
## 4. 외부 인터페이스 — N/A: API/event 노출 없음
```

비활성 토픽은 dialogue 자체를 스킵 — 빈 섹션도 아니고 placeholder 도 아님. N/A 한 줄.

### deterministic Python classifier 도입 X

키워드 hardcode list (예: `테이블 / 마이그레이션 / API / 엔드포인트`) 는 brittle (Postgres 만 있고 DB 없는 경우 등 미스매칭). 메인 에이전트의 컨텍스트 이해가 더 정확. 사용자 override 한 줄로 false negative 즉시 catch.
````

- [ ] **Step 4: Process Flow 다이어그램 — Step 0 announce 노드 + 비활성 토픽 N/A 표기 추가**

**원본** (`skills/designing-direction/SKILL.md` Process Flow 의 architecture 직전):

```dot
"Survey existing code\n(impacted files via Grep)" -> "Q: architecture candidates (2-3)?";
```

**수정 후** (그 사이에 announce 노드 추가):

```dot
"Survey existing code\n(PRD §2 재활용 v1.1.15+)" -> "Step 0 announce\n활성/비활성 토픽 한 줄";
"Step 0 announce\n활성/비활성 토픽 한 줄" -> "Q: architecture candidates (2-3)?";
"Step 0 announce\n활성/비활성 토픽 한 줄" -> "Q: data model changes?\n[활성 시만]" [label="활성"];
"Step 0 announce\n활성/비활성 토픽 한 줄" -> "Q: external interfaces?\n[활성 시만]" [label="활성"];
"Step 0 announce\n활성/비활성 토픽 한 줄" -> "Q: test strategy?\n[활성 시만]" [label="활성"];
```

- [ ] **Step 5: 정적 grep 검증** — `grep -nE "Adaptive Topics|항상 활성|조건부 활성|Before invoking the next skill|Step 0 announce" skills/designing-direction/SKILL.md` → 매치 ≥ 5. Checklist count = 9 확인 (`grep -c "^[0-9]\. " skills/designing-direction/SKILL.md` ≤ 12 정도, 본문 중 다른 numbered list 영향 받음 — 최소 9 ≤ x ≤ 12 OK).

- [ ] **Step 6: Commit** — `git add skills/designing-direction/SKILL.md && git commit -m "feat(designing-direction): adaptive 7-topic + items 9+10 통합 + transition reminder (FR-1 + FR-2)"`

---

### Task 9: skills/writing-plans/SKILL.md — Checklist 끝 transition reminder (FR-2)

**Files:**
- Modify: `skills/writing-plans/SKILL.md:28-30` (Checklist 끝)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `grep -nE "Before invoking the next skill" skills/writing-plans/SKILL.md` → 매치 0건.

- [ ] **Step 2: Checklist 끝 한 문단 추가**

**원본** (`skills/writing-plans/SKILL.md:28-30`):

```markdown
11. **Hand off to /execute-plan** — count tasks first, then offer the choice using the Execution Handoff message below. Upstream `subagent-driven-development` is NOT offered here; only invoke it if the user explicitly asks for the upstream original.

If you find yourself skipping ahead, stop and create the missing task.
```

**수정 후**:

```markdown
11. **Hand off to /execute-plan** — count tasks first, then offer the choice using the Execution Handoff message below. Upstream `subagent-driven-development` is NOT offered here; only invoke it if the user explicitly asks for the upstream original.

If you find yourself skipping ahead, stop and create the missing task.

**Before invoking the next skill via Skill tool, mark ALL checklist TaskCreate items as completed (in_progress → completed). The Skill tool transition does NOT auto-complete prior tasks. (v1.1.15+, FR-2)**
```

- [ ] **Step 3: 정적 grep 검증** — 매치 1 PASS.

- [ ] **Step 4: Commit** — `git add skills/writing-plans/SKILL.md && git commit -m "feat(writing-plans): transition reminder (FR-2)"`

---

### Task 10: CLAUDE.md — FR-4 결합 메모 추가

**Files:**
- Modify: `CLAUDE.md` (마지막 섹션 — 기존 "scripts/preflight.py ↔ 4 skill" 결합 메모 보강)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `grep -nE "preflight schema 변경|human_reason 필드|FR-4 user-gate" CLAUDE.md` → 매치 0건.

- [ ] **Step 2: 기존 "scripts/preflight.py ↔ 4 skill Pre-flight 결합" 섹션 끝에 한 문단 추가**

**원본** (`CLAUDE.md` 끝부분, 해당 섹션 마지막 줄):

```markdown
요약: 이 helper 와 4 skill 의 Pre-flight 섹션 변경은 atomic 하게 묶어 처리할 것.
```

**수정 후**:

```markdown
요약: 이 helper 와 4 skill 의 Pre-flight 섹션 변경은 atomic 하게 묶어 처리할 것.

### v1.1.15+ — `human_reason` 필드 + 사용자 게이트 결합

`scripts/preflight.py` 의 `PreflightResult.human_reason` 필드 추가 (v1.1.15+) 와 4 skill 의 user-gate boilerplate (FR-4) 는 결합되어 있다:

- helper 의 `human_reason` 필드 시그니처 변경 시 4 skill bash one-liner 의 `result.human_reason` 출력 표현식도 동시 수정
- user-gate boilerplate 의 AskUserQuestion choices 변경 시 4 skill 동시 적용 (한 군데만 누락 시 사용자 마찰 일관성 깨짐)

요약: helper schema + user-gate boilerplate 변경은 atomic 하게 묶어 처리할 것. 5 파일 (preflight.py + 4 skill SKILL.md) 동시 push.
```

- [ ] **Step 3: 정적 grep 검증** — 매치 ≥ 1 PASS.

- [ ] **Step 4: Commit** — `git add CLAUDE.md && git commit -m "docs(claude-md): v1.1.15 human_reason + user-gate 결합 메모 (FR-4)"`

---

### Task 11: skills/dj-superkit-subagent-driven-development/tests/H1~H6/ — dogfood fixture 6개 신규

**Files:**
- Create: `skills/dj-superkit-subagent-driven-development/tests/H1-router-small/README.md`
- Create: `skills/dj-superkit-subagent-driven-development/tests/H2-router-ambiguous/README.md`
- Create: `skills/dj-superkit-subagent-driven-development/tests/H3-adaptive-na/README.md`
- Create: `skills/dj-superkit-subagent-driven-development/tests/H4-preflight-fail/README.md`
- Modify: `skills/dj-superkit-subagent-driven-development/tests/README.md` (색인에 H1~H4 추가)

**Model**: sonnet

- [ ] **Step 1: failing 검증** — `ls skills/dj-superkit-subagent-driven-development/tests/H*` → 0건.

- [ ] **Step 2: H1 fixture 작성**

**수정 후** (`skills/dj-superkit-subagent-driven-development/tests/H1-router-small/README.md`, new file):

```markdown
# H1 — Entry Router: small 신호 자동 라우팅

## 시나리오

사용자가 `/brainstorm` 또는 자연어로 "README 한 줄 수정" 류 small 피처 요청.

## 입력 (사용자 메시지 시뮬레이션)

```
README.md 의 v1.1.13 → v1.1.15 한 줄 간단히 수정해줘
```

## 기대 동작

1. dj-superkit:brainstorming Step 0 라우터 발화
2. small 신호 감지 (키워드: `간단`, 단일 파일/한 줄 변경)
3. 한 줄 notice 노출:
   ```
   ℹ️ Auto-routing to og-brainstorming ('간단', 단일 파일 변경). Switch back? "dj-superkit" 라고 답하세요.
   ```
4. og-brainstorming Skill tool 호출

## 매핑

- AC-6 (작은 메타 피처로 라우터 small 자동 라우팅 확인)
- FR-3 (Step 0 라우터)
```

- [ ] **Step 3: H2 fixture 작성**

**수정 후** (`skills/dj-superkit-subagent-driven-development/tests/H2-router-ambiguous/README.md`, new file):

```markdown
# H2 — Entry Router: 모호한 피처 → AskUserQuestion 게이트

## 시나리오

명시적 small 신호 없는 피처. AI 가 small/large 분명 판정 X → 게이트 발화.

## 입력

```
로그 포맷 변경하고 싶어
```

## 기대 동작

1. dj-superkit:brainstorming Step 0 라우터 발화
2. small 신호 부재 (키워드 X, 단일 파일/함수 명시 X)
3. AskUserQuestion 호출:
   - question: "이 피처는 og-brainstorming(가벼운 단발) 또는 dj-superkit:brainstorming(3-MD 풀 트랙) 중 어느 모드로 진행할까요?"
   - header: "진입 모드"
   - options: og-brainstorming / dj-superkit:brainstorming
4. 사용자 선택 → 해당 skill 진입

## 매핑

- AC-7 (모호한 피처로 라우터 게이트 발화 확인)
- FR-3 (Step 0 라우터)
```

- [ ] **Step 4: H3 fixture 작성**

**수정 후** (`skills/dj-superkit-subagent-driven-development/tests/H3-adaptive-na/README.md`, new file):

```markdown
# H3 — Adaptive 7-topic: 비활성 토픽 N/A 박힘

## 시나리오

메타 워크플로우 변경 PRD 로 designing-direction 진입. 비활성 토픽 (3 데이터 모델, 4 외부 인터페이스) 는 dialogue 스킵 + N/A 한 줄로 박힘.

## 입력

flow-slim-requirements.md (본 v1.1.15 PRD) — meta 워크플로우, DB/API 무관

## 기대 동작

1. designing-direction Step 0 announce:
   ```
   ℹ️ 활성 토픽: 1,2,5,6,7 / 비활성: 3 데이터모델, 4 외부IF (이유: skill 본문 + helper script 변경, DB/API 무관). 추가 활성 필요시 알려주세요.
   ```
2. Step 3 dialogue 가 활성 토픽만 (1,2,5,6,7) 발화 — 3,4 스킵
3. flow-slim-tech-design.md 의 §3, §4 가 다음 형식으로 한 줄:
   ```markdown
   ## 3. 데이터 모델/스키마 변경 — N/A: 본 피처는 DB/스키마 무관 (skill 본문 + Python helper 변경)
   ## 4. 외부 인터페이스 — N/A: API/event 노출 없음 (skill 내부 + 로컬 Python helper)
   ```

## 매핑

- AC-1 (announce 한 줄 + N/A 박힘)
- AC-8 (메타 워크플로우 피처 dogfood)
- FR-1 (adaptive 7-topic)

## 참고

본 v1.1.15 의 flow-slim-tech-design.md 가 실제로 위 패턴을 따랐음 (CH-002). 자기 자신 dogfood 1차 통과.
```

- [ ] **Step 5: H4 fixture 작성**

**수정 후** (`skills/dj-superkit-subagent-driven-development/tests/H4-preflight-fail/README.md`, new file):

````markdown
# H4 — Preflight 강제 실패: AskUserQuestion 게이트 발화

## 시나리오

`<slug>-requirements.md` 에 가짜 변경이력 entry 박은 채로 docs-pretty 호출. preflight 가 `변경이력 footer not empty` 로 fail (exit 1) → 게이트 발화.

## 입력 (시뮬레이션 setup)

`/tmp/test-h4-requirements.md` 작성. 본 파일에는 다음 구조가 들어가야 함 (markdown literal 그대로 실제 fixture 파일에 넣을 것):

- H1: `# 요구사항: test-h4`
- H2 섹션: `## 1. 배경/목적` 본문 한 줄
- 구분선 `---`
- H2 footer: `## 〔변경이력〕` (실제 파일에는 `## 변〇경〇이〇력` 대신 정상 한국어 `변경이력` 헤더)
- H3 entry: `### [2026-05-10 12:00] [요구사항-수정]`
- entry 본문: id, 이유, 무엇이, 영향범위 4 필드

→ 메인이 fixture 작성 시 위 구조를 그대로 정상 markdown 으로 옮길 것. 본 plan 본문에는 markdown 헤더 리터럴을 의도적으로 escape (preflight regex false positive 회피).

## 기대 동작

1. docs-pretty Step 1 — preflight bash one-liner 실행
2. exit 1, `human_reason` = `"이미 변경이력 entry 가 존재합니다 (live doc). docs-pretty 는 최초 생성 단계에서만 발화합니다"`
3. 메인이 `human_reason` 한 줄 노출 후 AskUserQuestion 게이트:
   - choices: `"수정 후 재시도"` / `"강제 진행 (위험)"` / `"스킵 (이번만)"`
4. 사용자가 `"수정 후 재시도"` 선택 → entry 제거 후 재호출 → preflight ok=True → Step 2 dispatch
5. 사용자가 `"스킵 (이번만)"` 선택 → caller (brainstorming/designing-direction/writing-plans) 에게 abnormal return → caller 가 docs-pretty 단계 스킵하고 change-history 직행

## 매핑

- AC-11 (preflight 강제 실패 시뮬레이션)
- FR-4 (user-gate)
````

- [ ] **Step 6: tests/README.md 색인 갱신**

**원본** (`skills/dj-superkit-subagent-driven-development/tests/README.md` 끝부분):

```markdown
- G8 — reviewer fixed sonnet
```

**수정 후**:

```markdown
- G8 — reviewer fixed sonnet

## v1.1.15+ — flow-slim dogfood fixtures (FR-1/FR-3/FR-4)

- H1 — entry router: small 신호 자동 라우팅 (FR-3, AC-6)
- H2 — entry router: 모호 피처 게이트 발화 (FR-3, AC-7)
- H3 — adaptive 7-topic: 비활성 N/A 박힘 (FR-1, AC-1, AC-8)
- H4 — preflight 강제 실패 게이트 (FR-4, AC-11)
```

- [ ] **Step 7: 검증** — `ls skills/dj-superkit-subagent-driven-development/tests/H*/README.md` → 4건. `grep -c "^- H[1-4]" skills/dj-superkit-subagent-driven-development/tests/README.md` → 4.

- [ ] **Step 8: H5 fixture (FR-5 docs-pretty pre-review)** — `skills/dj-superkit-subagent-driven-development/tests/H5-docs-pretty-pre-review/README.md` (new file). 시나리오: `/brainstorm` 새 피처 → 첫 사용자 노출 본문이 prettified 인지 + fix 시 docs-pretty 재발화 검증. 매핑: AC-14, FR-5.

- [ ] **Step 9: H6 fixture (FR-6 task name friendly)** — `skills/dj-superkit-subagent-driven-development/tests/H6-task-name-friendly/README.md` (new file). 시나리오: `/brainstorm` / `/design` / `/write-plan` / `/execute-plan` 진입 시 TaskCreate 목록에 `Invoke`, `Gate #`, `skill`, `CH-id` 패턴 미노출 검증. 매핑: AC-15, AC-17, FR-6.

- [ ] **Step 10: tests/README.md 색인 갱신** — H5, H6 행 추가:

```markdown
- H5 — docs-pretty pre-review 통일 (FR-5, AC-14)
- H6 — task name friendly (FR-6, AC-15, AC-17)
```

- [ ] **Step 11: 검증** — `ls skills/dj-superkit-subagent-driven-development/tests/H*/README.md` → 6건. README.md 색인에 H1~H6 모두 등재.

- [ ] **Step 12: Commit** — `git add skills/dj-superkit-subagent-driven-development/tests/H*/ skills/dj-superkit-subagent-driven-development/tests/README.md && git commit -m "test(subagent-dd): H1~H6 dogfood fixtures (FR-1 + FR-3 + FR-4 + FR-5 + FR-6)"`

---

### Task 12: FR-5 — docs-pretty pre-review timing 통일 (3 skill swap + docs-pretty 본문 단일화)

**Files:**
- Modify: `skills/docs-pretty/SKILL.md` (frontmatter description + Trigger timing 섹션 + Anti-Trigger 일부 룰 제거)
- Modify: `skills/brainstorming/SKILL.md` (Checklist Step 6/7 swap + per-draft re-pretty loop 명시)
- Modify: `skills/designing-direction/SKILL.md` (combined approval gate ↔ docs-pretty swap + per-draft loop 명시)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `grep -nE "사용자가 prettified|per-draft|pre-review timing" skills/docs-pretty/SKILL.md` → 매치 0건.

- [ ] **Step 2: docs-pretty/SKILL.md frontmatter description 갱신** — "depending on doc type" 분기 wording 제거, "fires before user review on every draft" 단일 룰화.

- [ ] **Step 3: docs-pretty/SKILL.md Trigger timing 섹션 (line 13~18) 단일화**

**원본** (`skills/docs-pretty/SKILL.md` Trigger timing 섹션):

```markdown
Trigger timing depends on the doc type:

- **requirements.md / tech-design.md (산문 위주)** — invoked AFTER the user APPROVES the raw draft, BEFORE the change-history entry is logged. Single shot per feature (final-1회).
- **implementation-plan.md (코드 블록 다수)** — invoked AFTER verifying-spec passes AND code-pretty completes, BEFORE user review. Re-fires on each user-fix iteration (per-draft-state).
```

**수정 후**:

```markdown
Trigger timing (v1.1.15+ 통일 — pre-review per-draft):

모든 doc 타입에서 동일하게 발화: 메인이 RAW 작성 → docs-pretty (사용자 리뷰 직전) → 사용자가 prettified 본문 검토 → 승인 → change-history. 사용자 fix 요청 시 메인이 in-memory raw 갱신 후 docs-pretty 재발화 (per-draft loop).

- **requirements.md** — brainstorming 흐름 끝, 사용자 리뷰 직전. user-fix 시 재발화.
- **tech-design.md** — designing-direction 흐름 끝, 사용자 리뷰 직전 (combined approval gate 와 결합). user-fix 시 재발화.
- **implementation-plan.md** — writing-plans 흐름 끝, verifying-spec + code-pretty 통과 후, 사용자 리뷰 직전. user-fix 시 재발화 (기존 패턴 유지).

STOPS firing the moment the first `change-history` entry has been logged. That boundary marks the doc as "live" — from then on, no docs-pretty.
```

- [ ] **Step 4: docs-pretty/SKILL.md Anti-Trigger 룰 제거** — line 25 의 `requirements.md / tech-design.md BEFORE user approval — wait for approval first` 항목 삭제 (pre-review 패턴으로 변경되어 무의미).

- [ ] **Step 5: brainstorming/SKILL.md Checklist Step 6/7 swap**

**원본** (`skills/brainstorming/SKILL.md` Checklist Step 6/7):

```markdown
6. **User reviews <slug>-requirements.md** — show the RAW (un-prettified) file, get approval (loop until OK; on changes → revise → re-show raw)
7. **Invoke docs-pretty skill** — format-only pass (Sonnet subagent) on the APPROVED draft, AFTER user approval and BEFORE change-history. Single shot per feature (final-1회). Stops once first change-history entry is logged.
```

**수정 후** (swap + per-draft loop):

```markdown
6. **Invoke docs-pretty skill (v1.1.15+ pre-review)** — format-only pass (Sonnet subagent) on the RAW draft BEFORE user review. Re-fires on each user-fix iteration (per-draft).
7. **User reviews <slug>-requirements.md (prettified)** — show the prettified file, get approval (loop until OK; on changes → revise → back to step 6 → re-show prettified). Stops once first change-history entry is logged.
```

- [ ] **Step 6: designing-direction/SKILL.md Step 6/7 swap** — combined approval gate (RAW doc + verify report) 가 docs-pretty 후 발화하도록 swap. (현재 Step 6 = combined approval gate, Step 7 = docs-pretty 라서 swap.)

**원본** (`skills/designing-direction/SKILL.md` Checklist Step 6/7):

```markdown
6. **Single combined approval gate** — show the full RAW `<slug>-tech-design.md` AND the verify-spec report in one message; ask once "Approve and proceed? — yes / no". On `no` → revise → loop back to step 4 (Self-review → re-verify → re-show RAW).
7. **Invoke docs-pretty skill** — format pass on the APPROVED draft (Sonnet subagent). Runs AFTER user approval and BEFORE change-history. Single shot per feature (final-1회). Stops once first change-history entry is logged.
```

**수정 후**:

```markdown
6. **Invoke docs-pretty skill (v1.1.15+ pre-review)** — format pass on the RAW draft BEFORE user review. Re-fires on each user-fix iteration (per-draft).
7. **Single combined approval gate** — show the full PRETTIFIED `<slug>-tech-design.md` AND the verify-spec report in one message; ask once "Approve and proceed? — yes / no". On `no` → revise → loop back to step 4 (Self-review → re-verify → re-pretty → re-show prettified). Stops once first change-history entry is logged.
```

- [ ] **Step 7: 정적 grep 검증** — `grep -cE "v1.1.15.*pre-review|per-draft" skills/docs-pretty/SKILL.md` ≥ 1 + `grep -cE "Invoke docs-pretty skill \(v1.1.15\+ pre-review\)" skills/brainstorming/SKILL.md skills/designing-direction/SKILL.md` ≥ 1 each.

- [ ] **Step 8: Commit** — `git add skills/docs-pretty/SKILL.md skills/brainstorming/SKILL.md skills/designing-direction/SKILL.md && git commit -m "feat(docs-pretty): pre-review timing 통일 (FR-5)"`

---

### Task 13: FR-6 — TaskCreate task 이름 사용자 친화화 (5 skill Checklist + CLAUDE.md 글로벌 룰)

**Files:**
- Modify: `skills/brainstorming/SKILL.md` (Checklist 한국어 친화 명칭 rename)
- Modify: `skills/designing-direction/SKILL.md` (동일)
- Modify: `skills/writing-plans/SKILL.md` (동일 + Gate #13/#14 표현)
- Modify: `skills/executing-plans/SKILL.md` (구현계획서 task 이름 가이드 추가)
- Modify: `skills/finishing-a-development-branch/SKILL.md` (Step 명칭 사용자화)
- Modify: `CLAUDE.md` ("TaskCreate 명칭 룰" 글로벌 가이드 추가)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `for f in skills/brainstorming/SKILL.md skills/designing-direction/SKILL.md skills/writing-plans/SKILL.md skills/executing-plans/SKILL.md skills/finishing-a-development-branch/SKILL.md; do awk '/^## Checklist/,/^## /' "$f" | grep -cE "Invoke .* skill|Gate #|CH-[0-9]"; done` → 매치 ≥ 1 (각 skill). Task 끝에서 모두 0.

- [ ] **Step 2: brainstorming/SKILL.md Checklist 한국어 친화 명칭 rename** — `Invoke change-history skill` → `변경이력 기록`, `Invoke docs-pretty skill` → `문서 포맷 정리`, `Mode selection gate` → `모드 선택`, `Auto-proceed to designing-direction` → `개발방향 단계 자동 진행` 등. 본문 다른 부분 (Process Flow / Detailed sections) 의 영어 식별자 unchanged.

- [ ] **Step 3: designing-direction/SKILL.md Checklist 동일 rename** — `Invoke verifying-spec` → `사양 정합성 검증`, `Single combined approval gate` → `초안 검토 및 승인`, `Invoke change-history skill` → `변경이력 기록`, `Ask proceed-to-writing-plans gate` → `다음 단계 진입 확인` 등.

- [ ] **Step 4: writing-plans/SKILL.md Checklist 동일 rename + Gate #13/#14 표현** — `Invoke verifying-spec` → `사양 정합성 검증`, `Invoke code-pretty skill` → `코드 블록 포맷 정리`, `Invoke docs-pretty skill` → `문서 포맷 정리`, `Hand off to /execute-plan` → `구현 단계 핸드오프`, `Gate #13 — plan + verify 결합 승인` → `초안 검토 및 승인`, `Gate #14 — 실행 모드 선택` → `실행 모드 선택`.

- [ ] **Step 5: executing-plans/SKILL.md task 이름 가이드 추가** — 구현계획서 §1 의 각 Task 이름이 사용자 친화 표현인지 확인 룰 한 줄. (실제 plan 의 task 이름은 plan 작성자 책임 — executing-plans 는 plan 따름. 단 본 skill 본문에 한 줄 가이드.)

- [ ] **Step 6: finishing-a-development-branch/SKILL.md Step 명칭 사용자화** — 슬림 75줄 본문이라 영향 작음. Step 1 (test gate) / Step 2 (termination message) 명칭 한국어 친화로.

- [ ] **Step 7: CLAUDE.md 글로벌 룰 추가**

**원본** (`CLAUDE.md` 끝부분):

```markdown
요약: helper schema + user-gate boilerplate 변경은 atomic 하게 묶어 처리할 것. 5 파일 (preflight.py + 4 skill SKILL.md) 동시 push.
```

**수정 후** (한 섹션 추가):

```markdown
요약: helper schema + user-gate boilerplate 변경은 atomic 하게 묶어 처리할 것. 5 파일 (preflight.py + 4 skill SKILL.md) 동시 push.

## TaskCreate 명칭 룰 (v1.1.15+, FR-6)

dj-superkit 자체 skill 의 Checklist 본문에 박힌 task 명칭은 **사용자 시야 (TaskCreate UI) 에 직접 노출**됨. 다음 룰 적용:

- **사용자 친화 한국어 표현 사용** — 내부 용어 (`Invoke ... skill`, `Gate #N`, `CH-id`, `verifying-spec`, `docs-pretty` 등 영어 식별자) 미노출
- **본문의 다른 부분 (Process Flow, Detailed Step) 의 영어 식별자는 유지** — 메인 에이전트가 정확한 skill 호출에 필요
- **upstream og-* skill 들 (verbatim)** — 손대지 않음
- **변경이력 footer 의 entry tag** (`[요구사항-수정]` 등) — schema 매직 키워드라 유지

신규 skill 작성 시도 본 룰 따를 것. 회귀 시 `grep -nE "Invoke .* skill|Gate #|CH-[0-9]" <skill 본문 Checklist>` 로 catch.
```

- [ ] **Step 8: 정적 grep 검증** — `for f in skills/brainstorming/SKILL.md skills/designing-direction/SKILL.md skills/writing-plans/SKILL.md skills/executing-plans/SKILL.md skills/finishing-a-development-branch/SKILL.md; do awk '/^## Checklist/,/^## /' "$f" | grep -cE "Invoke .* skill|Gate #|CH-[0-9]"; done` → 모두 0. CLAUDE.md 매치 ≥ 1.

- [ ] **Step 9: Commit** — `git add skills/brainstorming/SKILL.md skills/designing-direction/SKILL.md skills/writing-plans/SKILL.md skills/executing-plans/SKILL.md skills/finishing-a-development-branch/SKILL.md CLAUDE.md && git commit -m "feat(skills): TaskCreate 친화 명칭 + CLAUDE.md 룰 (FR-6)"`

---

### Task 14: 정적 grep 검증 (F1~F7) + pytest 통합 PASS

**Files:**
- (검증 only — 코드 수정 없음. `[검증]` change-history entry 발화 예정)

**Model**: haiku

- [ ] **Step 1: F1 (FR-1 announce + Step 2 슬림 wording)** — `grep -E "활성 토픽|항상 활성|PRD §2 재활용" skills/designing-direction/SKILL.md` → 매치 ≥ 3.

- [ ] **Step 2: F2 (FR-2 3 skill 동일 reminder)** — 3 skill 의 reminder 문장 byte-equal 확인:

```bash
for f in skills/brainstorming/SKILL.md skills/designing-direction/SKILL.md skills/writing-plans/SKILL.md; do
  grep -c "Before invoking the next skill via Skill tool, mark ALL checklist TaskCreate items as completed" "$f"
done
```

→ 모두 1 출력 PASS.

- [ ] **Step 3: F3 (FR-2 designing-direction Checklist count = 9)** — `awk '/^## Checklist/,/^## /' skills/designing-direction/SKILL.md | grep -cE "^[0-9]+\. \*\*"` → 9 PASS.

- [ ] **Step 4: F4 (FR-3 brainstorming Step 0 라우터 본문 + small 키워드)** — `grep -nE "Step 0 Router|간단.*잠깐.*한 줄|Auto-routing to og-brainstorming" skills/brainstorming/SKILL.md` → 매치 ≥ 2.

- [ ] **Step 5: F5 (FR-4 4 skill 통일 boilerplate)** — `for f in skills/docs-pretty/SKILL.md skills/code-pretty/SKILL.md skills/executing-plans/SKILL.md skills/dj-superkit-subagent-driven-development/SKILL.md; do grep -c "v1.1.15.*user-gate\|exit ≠ 0,1\|AskUserQuestion 게이트" "$f"; done` → 모두 ≥ 1 출력 PASS.

- [ ] **Step 5b: F6 (FR-5 docs-pretty 통일 timing)** — `grep -cE "v1.1.15.*pre-review|per-draft" skills/docs-pretty/SKILL.md` ≥ 1 + `for f in skills/brainstorming/SKILL.md skills/designing-direction/SKILL.md; do grep -c "Invoke docs-pretty skill (v1.1.15+ pre-review)" "$f"; done` → 모두 ≥ 1.

- [ ] **Step 5c: F7 (FR-6 task name friendly)** — `for f in skills/brainstorming/SKILL.md skills/designing-direction/SKILL.md skills/writing-plans/SKILL.md skills/executing-plans/SKILL.md skills/finishing-a-development-branch/SKILL.md; do awk '/^## Checklist/,/^## /' "$f" | grep -cE "Invoke .* skill|Gate #|CH-[0-9]"; done` → 모두 0 출력 PASS. `grep -c "TaskCreate 명칭 룰" CLAUDE.md` ≥ 1.

- [ ] **Step 6: pytest 전체 통과** — `source .venv/bin/activate && pytest scripts/tests/ -v` → 기존 30 + 신규 ~5 (Task 1~2) = 35+ PASS.

- [ ] **Step 7: Commit (verification-only entry, no code change)** — 본 Task 는 코드 변경 X. change-history 의 `[검증]` entry 로 처리 (executing-plans batch consolidator 가 자동 처리). 별도 commit 생략 가능 (다음 task 의 commit 에 포함되거나 batch 마지막에 단독 verification entry).

---

### Task 15: bump-version.sh 1.1.14 → 1.1.15 (6 manifest 동기화)

**Files:**
- Run: `bash scripts/bump-version.sh 1.1.15`
- Verify: `.claude-plugin/plugin.json`, `marketplace.json`, `package.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json` 모두 1.1.15 일치

**Model**: haiku

- [ ] **Step 1: bump 스크립트 실행**

```bash
bash scripts/bump-version.sh 1.1.15
```

기대 출력: 6 manifest 가 1.1.14 → 1.1.15 로 변경됨 + 산문 "v1.1.14" 매치 경고 (정상 — release notes / HANDOFF 등 다음 task 에서 정리).

- [ ] **Step 2: 6 manifest 일치 검증**

```bash
for f in .claude-plugin/plugin.json marketplace.json package.json .codex-plugin/plugin.json .cursor-plugin/plugin.json gemini-extension.json; do
  echo -n "$f: "
  grep -oE '"version"[^,]*' "$f" | head -1
done
```

모두 `"1.1.15"` 출력 PASS.

- [ ] **Step 3: Commit** — `git add .claude-plugin/plugin.json marketplace.json package.json .codex-plugin/plugin.json .cursor-plugin/plugin.json gemini-extension.json && git commit -m "chore: bump version 1.1.14 → 1.1.15"`

---

### Task 16: HANDOFF.md 갱신 (v1.1.15 진행 상태 + 회고)

**Files:**
- Modify: `HANDOFF.md`

**Model**: sonnet

- [ ] **Step 1: HANDOFF.md 업데이트** — v1.1.15 4 backlog 통합 결과 / 산출물 / What Worked / What Didn't / Risk Register / Next Steps (v1.1.16 후보).

- [ ] **Step 2: 검증** — `grep -c "v1.1.15" HANDOFF.md` ≥ 5.

- [ ] **Step 3: HANDOFF.md 는 .gitignore 됨** — local only, commit X. 본 task 는 commit 없이 종료.

---

## 2. 위험 코드 지점

tech-design §6 R1~R8 → 구체 위치 + mitigation 매핑:

- `skills/designing-direction/SKILL.md` Step 0 announce / Adaptive Topics 섹션 (Task 8) — **side-effect**: AI 가 DB/API 시사 토픽 놓치면 tech-design 비어있음. mitigation: 진입 announce 한 줄 + 사용자 즉시 override 가능. (R1)
- `skills/{brainstorming,designing-direction,writing-plans}/SKILL.md` Checklist 끝 reminder (Task 7+8+9) — **breaking**: LLM 행동 강제력 100% X — reminder 무시 가능. mitigation: 명시 vs 미명시 차이 큼. dogfood 1회로 잔존 0건 검증 (H3 시나리오). (R2)
- `skills/brainstorming/SKILL.md` Step 0 라우터 (Task 7) — **side-effect**: small 키워드 false positive ("이건 간단하지 않아"). mitigation: notice + "dj-superkit 라고 답하세요" override. (R3)
- `skills/{docs-pretty,code-pretty,executing-plans,dj-superkit-subagent-driven-development}/SKILL.md` Pre-flight 섹션 4곳 (Task 3+4+5+6) — **breaking**: boilerplate 4곳 동시 변경. 한 군데만 누락 시 동작 불일치. mitigation: CLAUDE.md 결합 메모 (Task 10) + dogfood 4 skill 케이스 (H4 + 3 skill 별도 시나리오). (R4)
- 4 skill Pre-flight 섹션 "강제 진행 (위험)" 옵션 (Task 3+4+5+6) — **side-effect**: 사용자 매번 강제진행 누르면 게이트 무력화. mitigation: "(위험)" 라벨 + `⚠️ preflight 우회. <reason> 무시.` 한 줄 안내. (R5)
- `scripts/preflight.py:12-14` PreflightResult NamedTuple (Task 1) — **breaking**: 필드 추가가 기존 caller 깨뜨림 가능성. mitigation: NamedTuple `human_reason: str = ""` default value 사용. 9 unit test + 4 helper × ~3 fail 케이스 (Task 2) 호환 검증. (R6)
- `flow-slim-implementation-plan.md` 자체 (본 plan) — **race**: bootstrap paradox — 본 release 의 FR-1/FR-3 가 본 release 의 brainstorming/designing-direction 흐름 자체를 변경. dogfood 시 신구 혼재. mitigation: plan header 의 "Bootstrap notice" 명시 + 본 plan 자체는 v1.1.14 sequential + 7-topic 으로 실행 (이미 본 designing-direction 흐름이 그러함). (R7)
- `skills/brainstorming/SKILL.md` Step 0 라우터 ambiguous 분기 (Task 7) — **side-effect**: 라우터 false positive — small 신호 없는데도 의도된 풀 트랙이 게이트 발화. mitigation: 게이트 발화 = 사용자 즉시 결정. 손해 X (사용자 1번 클릭 비용). (R8)
- `skills/{brainstorming,designing-direction}/SKILL.md` Checklist Step 6/7 swap (Task 12) — **side-effect**: 메인 in-memory raw vs file pretty divergence — 사용자 fix 시 메인이 in-memory raw 갱신 후 다시 docs-pretty → 파일 덮어씀. mitigation: implementation-plan 에서 이미 검증된 패턴. docs-pretty post-dispatch sanity check (header / frontmatter / footer byte-identical) 가 의미 drift 자동 검출. (R9)
- `skills/{brainstorming,designing-direction,writing-plans,executing-plans,finishing-a-development-branch}/SKILL.md` Checklist 한국어 rename (Task 13) — **breaking**: 메인 에이전트가 친화 이름만 보고 정확한 skill 호출 못할 위험. mitigation: 본문 내 Detailed Step + Process Flow 다이어그램에 영어 식별자 명시. CLAUDE.md 글로벌 룰 (Task 13 Step 7) 재차 보강. (R10)

## 3. 롤백 전략

- **Code**: per-task commit 으로 진행 → 문제 시 `git revert` 또는 `git reset --hard <SHA-before-task>` (각 task 가 단일 commit). batch [코드-수정] entry 가 SHA 리스트 보관해 추적 가능.
- **`scripts/preflight.py` 시그니처 변경 (R6)**: NamedTuple default value 가 기존 caller 호환. 만약 caller bug 발생 시 (가능성 낮음) `git revert <Task-1 SHA>` 만으로 schema 복원 (4 skill bash one-liner 가 `result.human_reason` 안 쓰는 형태로 같이 revert 필요 — 4 skill SHA 도 revert).
- **Skill 본문 변경**: skill 은 disk 상 markdown — `git revert` 만으로 즉시 이전 버전 복원. 외부 의존성 없음.
- **CLAUDE.md 결합 메모**: revert 만으로 복원.
- **Manifest bump**: `git revert` 로 1.1.15 → 1.1.14 복원. 단, marketplace 가 이미 update 했다면 사용자 측에서 `/plugin marketplace update dj-superkit` 재실행 필요.
- **Feature flag X**: 본 release 는 skill body + helper schema 변경. feature flag 무관.

---
## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-10 17:00] [구현계획서-수정]
- **id**: CH-20260510-005
- **이유**: 신규 구현계획서 작성 (v1.1.15 — 6 FR / 6 backlog 통합 / 16 task TDD 분해 / Model 힌트 / Bootstrap notice)
- **무엇이**: flow-slim-implementation-plan.md 전체 (Header + §1 16 task + §2 R1~R10 위험 코드 지점 매핑 + §3 롤백 전략)
- **영향범위**: 없음 (최초 생성)
- **연관 항목**: CH-20260510-001 (PRD 원본), CH-20260510-002 (tech-design 원본), CH-20260510-003 (PRD amend FR-5/FR-6), CH-20260510-004 (tech-design amend D-T10/D-T11/R9/R10)
### [2026-05-10 18:00] [코드-수정] (batch: tasks 1..13)
- **id**: CH-20260510-006
- **이유**: 서브에이전트 모드 task batch 종합 (end-of-run consolidation)
- **무엇이**: CLAUDE.md, scripts/preflight.py, scripts/tests/test_preflight.py, skills/brainstorming/SKILL.md, skills/code-pretty/SKILL.md, skills/designing-direction/SKILL.md, skills/docs-pretty/SKILL.md, skills/executing-plans/SKILL.md, skills/finishing-a-development-branch/SKILL.md, skills/dj-superkit-subagent-driven-development/SKILL.md, skills/dj-superkit-subagent-driven-development/tests/H1-router-small/README.md, skills/dj-superkit-subagent-driven-development/tests/H2-router-ambiguous/README.md, skills/dj-superkit-subagent-driven-development/tests/H3-adaptive-na/README.md, skills/dj-superkit-subagent-driven-development/tests/H4-preflight-fail/README.md, skills/dj-superkit-subagent-driven-development/tests/H5-docs-pretty-pre-review/README.md, skills/dj-superkit-subagent-driven-development/tests/H6-task-name-friendly/README.md, skills/dj-superkit-subagent-driven-development/tests/README.md, skills/writing-plans/SKILL.md
- **영향범위**: 누적 (task별 세부 참조)
- **위험 카테고리**: breaking, side-effect
- **task별 세부 (13건)**:
  - Task 1: `scripts/preflight.py:12-100` — PreflightResult.human_reason 필드 추가 + 4 helper 한국어 메시지 (`breaking`) — commits: 
  - Task 1: `scripts/tests/test_preflight.py:80-93` — human_reason 필드 + docs_pretty 한국어 검증 2 신규 test (`none`) — commits: 
  - Task 2: `scripts/tests/test_preflight.py:97-130` — 4 helper × fail 한국어 검증 신규 test (`none`) — commits: 
  - Task 2: `scripts/preflight.py:100-103` — execute_plan_mode_check missing-plan human_reason → 구현계획서를 찾을 수 없습니다 보강 (`none`) — commits: 
  - Task 3: `skills/docs-pretty/SKILL.md:54-84` — Step 1 Pre-flight 사용자 게이트 boilerplate 통일 (`breaking`) — commits: 
  - Task 4: `skills/code-pretty/SKILL.md:44-72` — Step 1 Pre-flight 사용자 게이트 boilerplate (`breaking`) — commits: 
  - Task 5: `skills/executing-plans/SKILL.md:57-69` — mode-check 분기 부분 사용자 게이트 boilerplate (`breaking`) — commits: 
  - Task 6: `skills/dj-superkit-subagent-driven-development/SKILL.md:53-76` — Entry Guard 사용자 게이트 boilerplate (`breaking`) — commits: 
  - Task 7: `skills/brainstorming/SKILL.md:23-40 (checklist), 78-113 (diagram), 220-268 (Entry Router section)` — Checklist 0번 라우터 + Entry Router 섹션 + Process Flow 노드 + 끝 reminder (`side-effect`) — commits: 
  - Task 8: `skills/designing-direction/SKILL.md:14-31,65-88,106-148` — Checklist 9 items + Adaptive Topics 섹션 + Process Flow announce + 끝 reminder + Step 2 슬림 (`side-effect`) — commits: 
  - Task 9: `skills/writing-plans/SKILL.md:30-32` — Checklist 끝 transition reminder 한 문단 추가 (`none`) — commits: 
  - Task 10: `CLAUDE.md:144-155` — v1.1.15 human_reason + user-gate 결합 서브섹션 신규 (`none`) — commits: 
  - Task 11: `skills/dj-superkit-subagent-driven-development/tests/H1-router-small/README.md:1-25` — router small fixture (`none`) — commits: 
  - Task 11: `skills/dj-superkit-subagent-driven-development/tests/H2-router-ambiguous/README.md:1-25` — router ambiguous fixture (`none`) — commits: 
  - Task 11: `skills/dj-superkit-subagent-driven-development/tests/H3-adaptive-na/README.md:1-30` — adaptive N/A fixture (`none`) — commits: 
  - Task 11: `skills/dj-superkit-subagent-driven-development/tests/H4-preflight-fail/README.md:1-30` — preflight fail fixture (`none`) — commits: 
  - Task 11: `skills/dj-superkit-subagent-driven-development/tests/H5-docs-pretty-pre-review/README.md:1-25` — docs-pretty pre-review fixture (`none`) — commits: 
  - Task 11: `skills/dj-superkit-subagent-driven-development/tests/H6-task-name-friendly/README.md:1-30` — task name friendly fixture (`none`) — commits: 
  - Task 11: `skills/dj-superkit-subagent-driven-development/tests/README.md:27-50` — 색인 H1~H6 추가 (`none`) — commits: 
  - Task 12: `skills/docs-pretty/SKILL.md:1-38` — frontmatter + Trigger timing 단일화 + Anti-Trigger 룰 제거 (`breaking`) — commits: 
  - Task 12: `skills/brainstorming/SKILL.md:33-34` — Checklist Step 6/7 swap + per-draft loop 명시 (`side-effect`) — commits: 
  - Task 12: `skills/designing-direction/SKILL.md:23-24` — Checklist Step 6/7 swap + per-draft loop 명시 (`side-effect`) — commits: 
  - Task 13: `skills/brainstorming/SKILL.md:26-36` — Checklist bold prefix 한국어 친화 (items 1-9) (`breaking`) — commits: 
  - Task 13: `skills/designing-direction/SKILL.md:18-26` — Checklist bold prefix 한국어 친화 (items 1-9) (`breaking`) — commits: 
  - Task 13: `skills/writing-plans/SKILL.md:18-28` — Checklist bold prefix 한국어 친화 (items 1-11) (`breaking`) — commits: 
  - Task 13: `skills/executing-plans/SKILL.md:22-25` — Task 이름 가이드 한 줄 추가 (When to Use 섹션) (`breaking`) — commits: 
  - Task 13: `skills/finishing-a-development-branch/SKILL.md:19-35` — Step 1/2 명칭 한국어 친화 (`none`) — commits: 
  - Task 13: `CLAUDE.md:153-165` — TaskCreate 명칭 룰 글로벌 가이드 섹션 추가 (`none`) — commits: 
- **연관 commits**: 
- **변경 전/후 코드**: 생략 — `git show <SHA>` 로 조회


### [2026-05-10 18:00] [검증] (Task 14)
- **id**: CH-20260510-007
- **이유**: F1~F7 정적 grep + pytest 통합 검증 (Task 14 — 코드 변경 0건)
- **무엇이**: F1 (designing-direction adaptive 매치 13) / F2 (3 skill reminder byte-equal 1 each) / F3 (Checklist 9 items) / F4 (brainstorming Step 0 라우터 매치 5) / F5 (4 skill user-gate boilerplate ≥ 1 each, 총 ≥ 13) / F6 (docs-pretty pre-review 4 + brainstorming/designing-direction Process detail/Process Flow pre-review 보존 6/7) / F7 (5 skill Checklist 영어 식별자 0 + CLAUDE.md TaskCreate 명칭 룰 1) / pytest 36 PASS
- **영향범위**: 없음 (검증 only)
- **연관 항목**: CH-20260510-006 (batch tasks 1..13)
