---
commit_policy: per-task
---

# auto-flow 구현계획서

> **For agentic workers:** REQUIRED SUB-SKILL: `js-super-subagent-driven-development` (recommended for 14+ tasks) 또는 `executing-plans`. Steps use checkbox (`- [ ]`) syntax for tracking. Plan has 14 tasks total.

> **Bootstrap notice:** 본 plan 자체는 v1.1.15 의 정상 흐름 (manual /brainstorm → /design → /write-plan → /execute-plan) 으로 실행. 자기 자신 (auto-flow) 적용은 다음 dogfood 에서 (`/auto-brainstorm <new feature>`).

> **버전 결정:** auto-flow 는 **v1.1.17** 단독 release. v1.1.16 = backlog 2건 (DAG ordering bug + preflight regex false positive) micro-patch 우선. v1.1.16 fix 후 auto-flow 의 wave-parallel 더 안전.

**Goal:** js-super 4 단계 spec-driven 워크플로우를 자동 chain 으로 진행하는 4 신규 auto-* skill + 4 신규 slash command + CLAUDE.md 결합 메모.

**Architecture:** Layer 1 (slash command 4 entry) / Layer 2 (auto-* skill 4 본문 — og-* mirror 패턴, 게이트 자동 yes / clarifying Q only / verify 노출 후 chain) / Layer 3 (CLAUDE.md 결합 메모).

**Tech Stack:** Markdown (skill body + slash command), Python 3.13 (auto_flow.py helper + tests), pytest.

**Spec inputs:**
- `auto-flow-requirements.md` — D1~D12 (PRD D9 amend: docs-pretty SKIP) / 우려 6 / 다음 단계 3
- `auto-flow-tech-design.md` — D-T1~D-T12 (D-T12 = docs-pretty 호출 부재) / R1~R11 / F1~F8 정적 + H7~H10 dogfood + 2 unit test

---

## 1. 단계별 작업

### Task 1: scripts/auto_flow.py — `parse_interrupt` + `find_latest_slug` helper + tests

**Files:**
- Create: `scripts/auto_flow.py`
- Create: `scripts/tests/test_auto_flow.py`

**Model**: sonnet

- [ ] **Step 1: failing test 작성** — `scripts/tests/test_auto_flow.py`:

```python
import pytest
from pathlib import Path
from scripts.auto_flow import parse_interrupt, find_latest_slug


@pytest.mark.parametrize("text,expected", [
    ("stop", True),
    ("멈춰", True),
    ("잠깐", True),
    ("중단", True),
    ("abort", True),
    ("취소", True),
    ("어 잠시만", True),
    ("Stop please", True),
    ("계속 진행", False),
    ("OK 좋아요", False),
    ("그래 다음 단계로", False),
])
def test_parse_interrupt(text, expected):
    assert parse_interrupt(text) is expected


def test_find_latest_slug_picks_most_recent_mtime(tmp_path):
    older = tmp_path / "2026-05-01-old"
    older.mkdir()
    newer = tmp_path / "2026-05-10-new"
    newer.mkdir()
    # ensure newer is more recent
    import os, time
    time.sleep(0.01)
    os.utime(newer, None)
    assert find_latest_slug(tmp_path) == "new"


def test_find_latest_slug_returns_none_when_empty(tmp_path):
    assert find_latest_slug(tmp_path) is None


def test_find_latest_slug_skips_non_dirs(tmp_path):
    (tmp_path / "2026-05-01-real").mkdir()
    (tmp_path / "stray.md").write_text("noise")
    assert find_latest_slug(tmp_path) == "real"
```

- [ ] **Step 2: 테스트 fail 확인** — `pytest scripts/tests/test_auto_flow.py -v` → FAIL (ModuleNotFoundError).

- [ ] **Step 3: 구현 작성**

**수정 후** (new file: `scripts/auto_flow.py`):

```python
"""Helpers for auto-flow skills (v1.1.17+).

- parse_interrupt: detect user interrupt keyword (stop / 멈춰 / etc.) in transition turns.
- find_latest_slug: infer the latest <slug> from docs/features/ when slash command arg is omitted.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

_INTERRUPT_PATTERNS = [
    r"\bstop\b",
    r"\babort\b",
    r"멈춰",
    r"잠깐",
    r"잠시만",
    r"중단",
    r"취소",
]
_INTERRUPT_RE = re.compile("|".join(_INTERRUPT_PATTERNS), re.IGNORECASE)

_FOLDER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-(?P<slug>.+)$")


def parse_interrupt(text: str) -> bool:
    """Return True if `text` contains an interrupt keyword."""
    return bool(_INTERRUPT_RE.search(text))


def find_latest_slug(features_dir: Path) -> Optional[str]:
    """Return the slug of the most recently modified feature folder, or None."""
    if not features_dir.exists():
        return None
    candidates = []
    for child in features_dir.iterdir():
        if not child.is_dir():
            continue
        m = _FOLDER_RE.match(child.name)
        if not m:
            continue
        candidates.append((child.stat().st_mtime, m.group("slug")))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]
```

- [ ] **Step 4: 테스트 PASS 확인** — `pytest scripts/tests/test_auto_flow.py -v` → 11+ PASS.

- [ ] **Step 5: Commit** — `git add scripts/auto_flow.py scripts/tests/test_auto_flow.py && git commit -m "feat(auto_flow): parse_interrupt + find_latest_slug helpers (v1.1.17 prep)"`

---

### Task 2: skills/auto-brainstorming/SKILL.md — Socratic 자동 + clarifying Q 적응형

**Files:**
- Create: `skills/auto-brainstorming/SKILL.md`

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `ls skills/auto-brainstorming/SKILL.md` → 없음.

- [ ] **Step 2: SKILL.md 작성** — Socratic clarifying Q (1~5개 적응) + AI 자동 approach 선택 + AI 자동 section 작성 + change-history 자동 + skill 전환 1줄 notice + parse_interrupt 활용. docs-pretty 호출 부재 (D-T12). Visual Companion 단계 부재 (D-T11). AskUserQuestion 부재 (R4). 본문 ~120~180 lines.

**수정 후** (new file: `skills/auto-brainstorming/SKILL.md`):

```markdown
---
name: auto-brainstorming
description: auto-flow 진입점 — Socratic clarifying Q (1~5개 적응) + AI 자동 approach 선택 + 자동 section 작성 + change-history 자동 + auto-designing-direction 자동 invoke. 사용자 입력은 clarifying Q 답변에만. AskUserQuestion / Visual Companion / docs-pretty 호출 X.
---

# Auto Brainstorming → <slug>-requirements.md (Socratic auto)

js-super:auto-brainstorming 은 명시적 사용자 invoke (`/auto-brainstorm <피처명>`) 시에만 작동. PRD `auto-flow-requirements.md` D1~D12 (D9 amend) + tech-design D-T1~D-T12 의 자동 흐름 본문.

**Announce at start:** "I'm using the auto-brainstorming skill — Socratic clarifying Q + 자동 진행."

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
- docs-pretty 호출 X (D-T12). RAW 본문 그대로.

### Step 5 — change-history 자동

`change-history` skill invoke → 첫 `[요구사항-수정]` entry append. CH-id 자동 생성.

### Step 6 — Transition notice + auto-designing-direction invoke

```
ℹ️ Auto-proceeding to /design. Type "stop" to abort.
```

다음 사용자 turn 의 입력에 `parse_interrupt` (scripts/auto_flow.py) 매치 시 cleanly exit + `ℹ️ OK. /design 나중에 직접 실행.` 안내. 매치 X 시 즉시 `js-super:auto-designing-direction` skill invoke.

## Anti-Patterns

| Wrong | Right |
|---|---|
| AskUserQuestion 호출 | NEVER. auto-flow 의 사용자 입력은 clarifying Q 답변에만. |
| docs-pretty 호출 | NEVER. PRD D9 amend — auto-flow 는 review 없으므로 prettify 의미 없음. |
| Visual Companion offer | NEVER. D-T11. |
| 일반 brainstorming skill body 호출 | NEVER. self-contained mirror (D-T1). |
| transition notice 후 사용자 응답 wait sleep | NEVER. harness 모델은 자동 다음 turn — sleep X. |

## Related Skills

- `auto-designing-direction` — 다음 단계
- `change-history` — 첫 entry append
- `scripts/auto_flow.parse_interrupt` — interrupt 키워드 catch
```

- [ ] **Step 3: 정적 grep 검증** —
  - `grep -c "AskUserQuestion" skills/auto-brainstorming/SKILL.md` → 1 (Anti-Patterns 표 안 만)
  - `grep -c "docs-pretty" skills/auto-brainstorming/SKILL.md` → 1 (Anti-Patterns 표 안 만)
  - `grep -c "Auto-proceeding to" skills/auto-brainstorming/SKILL.md` → 1
  - `grep -c "parse_interrupt" skills/auto-brainstorming/SKILL.md` → 2

- [ ] **Step 4: Commit** — `git add skills/auto-brainstorming/SKILL.md && git commit -m "feat(auto-brainstorming): Socratic auto + clarifying Q + transition (v1.1.17)"`

---

### Task 3: skills/auto-designing-direction/SKILL.md — adaptive 7-topic 자동 + design decision 자동 + verify 노출

**Files:**
- Create: `skills/auto-designing-direction/SKILL.md`

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `ls skills/auto-designing-direction/SKILL.md` → 없음.

- [ ] **Step 2: SKILL.md 작성**

**수정 후** (new file: `skills/auto-designing-direction/SKILL.md`):

```markdown
---
name: auto-designing-direction
description: auto-flow 2단계 — requirements.md 읽기 + adaptive 7-topic 자동 판정 + design decision 자동 alternatives 비교 → recommendation 자동 선택 + verifying-spec 4축 보고서 transition 직전 노출 + auto-writing-plans 자동 invoke. AskUserQuestion / docs-pretty 호출 X.
---

# Auto Designing Direction → <slug>-tech-design.md (auto)

## Process

### Step 1 — 입력 확인 + slug 추론

`<slug>-requirements.md` 존재 확인. 인자 누락 시 `scripts/auto_flow.find_latest_slug(Path("docs/features"))` 호출.

### Step 2 — adaptive 7-topic 자동 판정

`<slug>-requirements.md` 본문 분석. 항상 활성 4 (1,2,5,6) + 조건부 3 (3,4,7). 메인이 본문 컨텍스트로 판단 + 한 줄 announce:

```
ℹ️ 활성 토픽: ... / 비활성: ... (이유: ...). [auto-flow — 사용자 응답 없이 진행]
```

→ 사용자 catch 가능 위치이지만 응답 wait X.

### Step 3 — AI 자동 design decision

각 활성 토픽에 대해 메인이 2-3 alternatives + recommendation 1개 자동 선택 (D-T3). reasoning 은 §5 결정+대안 비교 에 logged. 비활성 토픽은 N/A 한 줄.

### Step 4 — 산출물 자동 작성

`<slug>-tech-design.md` 7-section schema 따라 작성. RAW 본문, docs-pretty 호출 X.

### Step 5 — verifying-spec 자동 실행

`verifying-spec` skill invoke (메인 자체 수행 또는 skill 호출). 4축 보고서 생성. 결과는 다음 단계 transition notice 직전 노출.

### Step 6 — change-history 자동

`change-history` skill invoke → 첫 `[개발방향-수정]` entry. CH-id 자동.

### Step 7 — Transition notice + auto-writing-plans invoke

```
🔍 verifying-spec 결과:
   - A1 consistency: ✅
   - A2 ...
   - C1 impact: ⚠️ 영향 N 컴포넌트
   - C2 ...

ℹ️ Auto-proceeding to /write-plan. Type "stop" to abort.
```

`parse_interrupt` 매치 시 exit + `ℹ️ OK. /write-plan 나중에 직접 실행.` 안내. 매치 X → `js-super:auto-writing-plans` invoke.

## Anti-Patterns

(auto-brainstorming 의 Anti-Patterns 표 동일 — AskUserQuestion / docs-pretty / 일반 designing-direction body / sleep 모두 NEVER.)

## Related Skills

- `auto-writing-plans` — 다음 단계
- `verifying-spec` — 4축 보고서 생성
- `change-history` — 첫 entry append
- `scripts/auto_flow.parse_interrupt`, `find_latest_slug`
```

- [ ] **Step 3: 정적 grep 검증** —
  - `grep -c "AskUserQuestion" skills/auto-designing-direction/SKILL.md` ≤ 1
  - `grep -c "docs-pretty" skills/auto-designing-direction/SKILL.md` ≤ 1
  - `grep -c "Auto-proceeding to" skills/auto-designing-direction/SKILL.md` → 1
  - `grep -c "활성 토픽" skills/auto-designing-direction/SKILL.md` ≥ 1

- [ ] **Step 4: Commit** — `git add skills/auto-designing-direction/SKILL.md && git commit -m "feat(auto-designing-direction): adaptive 7-topic auto + verify 노출 + transition (v1.1.17)"`

---

### Task 4: skills/auto-writing-plans/SKILL.md — task 자동 분해 + Model 힌트 자동

**Files:**
- Create: `skills/auto-writing-plans/SKILL.md`

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `ls skills/auto-writing-plans/SKILL.md` → 없음.

- [ ] **Step 2: SKILL.md 작성**

**수정 후** (new file: `skills/auto-writing-plans/SKILL.md`):

```markdown
---
name: auto-writing-plans
description: auto-flow 3단계 — requirements + tech-design 읽기 + AI 자동 task 분해 (TDD bite-sized + Model hint 자동) + RISK 코드 지점 §2 자동 + verifying-spec 자동 + code-pretty 호출 X (D-T12 와 일관) + change-history 자동 + auto-executing-plans 자동 invoke. AskUserQuestion / docs-pretty 호출 X.
---

# Auto Writing Plans → <slug>-implementation-plan.md (auto)

## Process

### Step 1 — 입력 확인 + slug 추론

`<slug>-requirements.md` + `<slug>-tech-design.md` 모두 존재 확인. 누락 시 `ℹ️ 입력 누락 (<누락 파일>). /auto-brainstorm 또는 /auto-design 부터 시작하세요.` 안내 후 종료.

### Step 2 — AI 자동 task 분해

tech-design §1~§7 + R1~R10 분석. TDD bite-sized task 자동 생성:
- 각 task 의 Files / Model hint / TDD steps / RISK 자동 결정
- Model 힌트 자동: 1-2 파일 mechanical → haiku / 다중 파일 + 통합 → sonnet / 설계 + 광범위 → opus / Korean prose 조작 → sonnet (Haiku rephrasing 위험)
- Before/After 코드블록 (`**원본**` / `**수정 후**`) 컨벤션

### Step 3 — §2 위험 코드 지점 자동

tech-design §6 R-N → file:line + mitigation 매핑. 모든 R-N 이 §2 에 entry 갖도록 보장 (writing-plans Self-Review 룰).

### Step 4 — 산출물 자동 작성

`<slug>-implementation-plan.md` schema 따라 작성. frontmatter `commit_policy: per-task`. RAW 본문, code-pretty / docs-pretty 호출 X (D-T12 일관).

### Step 5 — verifying-spec 자동 실행

`verifying-spec` invoke. 4축 보고서 생성. 결과는 transition notice 직전 노출.

### Step 6 — change-history 자동

`change-history` invoke → 첫 `[구현계획서-수정]` entry. CH-id 자동.

### Step 7 — Transition notice + auto-executing-plans invoke

```
🔍 verifying-spec 결과: ...
ℹ️ Auto-proceeding to /execute-plan (subagent wave-parallel, Gate #14 override). Type "stop" to abort.
```

`parse_interrupt` 매치 시 exit. 매치 X → `js-super:auto-executing-plans` invoke.

## Anti-Patterns

(동일 — AskUserQuestion / docs-pretty / code-pretty / 일반 writing-plans body 호출 NEVER.)

## Related Skills

- `auto-executing-plans` — 다음 단계 (wave-parallel subagent 강제)
- `verifying-spec` / `change-history`
- `scripts/auto_flow.parse_interrupt`, `find_latest_slug`
```

- [ ] **Step 3: 정적 grep 검증** —
  - `grep -c "AskUserQuestion" skills/auto-writing-plans/SKILL.md` ≤ 1
  - `grep -c "docs-pretty\|code-pretty" skills/auto-writing-plans/SKILL.md` ≤ 2 (Anti-Patterns 표 안)
  - `grep -c "Auto-proceeding to" skills/auto-writing-plans/SKILL.md` → 1
  - `grep -c "Gate #14 override" skills/auto-writing-plans/SKILL.md` ≥ 1

- [ ] **Step 4: Commit** — `git add skills/auto-writing-plans/SKILL.md && git commit -m "feat(auto-writing-plans): auto task 분해 + Model 힌트 + Gate #14 override notice (v1.1.17)"`

---

### Task 5: skills/auto-executing-plans/SKILL.md — wave-parallel subagent 강제 + finishing 자동

**Files:**
- Create: `skills/auto-executing-plans/SKILL.md`

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — 없음.

- [ ] **Step 2: SKILL.md 작성**

**수정 후** (new file: `skills/auto-executing-plans/SKILL.md`):

```markdown
---
name: auto-executing-plans
description: auto-flow 4단계 (마지막) — implementation-plan.md 읽기 + Entry Guard (preflight.subagent_task_entry_check) + DAG 자동 build + 무조건 wave-parallel subagent 강제 (Gate #14 override) + failure isolation 그대로 + End-of-run consolidator 자동 + finishing-a-development-branch 자동 호출. AskUserQuestion / docs-pretty 호출 X.
---

# Auto Executing Plans → wave-parallel + finishing (auto)

## Process

### Step 1 — Entry Guard

`scripts.preflight.subagent_task_entry_check` 호출 (기존 helper 재활용, D-T6). plan 존재 + commit_policy=per-task 검사. fail 시 v1.1.15 user-gate 발화 (3 choice — 단 auto-flow 의도상 "스킵 (이번만)" 선택지가 자연스러운 종료 경로).

### Step 2 — slug 추론

인자 누락 시 `scripts/auto_flow.find_latest_slug` 호출. 추론된 slug 1줄 노출 (R8 mitigation): `⚙️ <slug> 자동 선택. 다른 폴더면 'stop' 후 인자 명시.`

### Step 3 — wave-parallel subagent 강제 invoke

무조건 `js-super:js-super-subagent-driven-development` skill invoke (D5, Gate #14 override). plan 의 task 수 무관 — 1개 task plan 도 subagent 패턴.

### Step 4 — failure isolation 그대로 (D6)

기존 wave-parallel skill 의 failure isolation 패턴 그대로:
- spec-reviewer ❌ retry 후 ❌ → 격리 (working tree 변경 폐기 + manifest 삭제)
- 후행 (deps 포함) blocked 마킹 → 다음 wave dispatch 제외
- 다른 task 정상 진행 + commit
- end-of-run consolidator 가 blocked list 노출

### Step 5 — End-of-run consolidator 자동

기존 v1.1.7+ End-of-Run Consolidator 패턴 그대로 — manifest 종합 → 구현 요약 메시지 → footer batch entry append → [log] commit + buffer cleanup.

### Step 6 — finishing-a-development-branch 자동 호출

`js-super:finishing-a-development-branch` skill invoke. 슬림 75줄 본문이 테스트 게이트 + 종료 메시지 자동 노출 (D-T10).

### Step 7 — auto-flow 완료 메시지

```
ℹ️ ✅ auto-flow 완료. 변경 N commits. blocked tasks: <list 또는 "없음">.
```

→ 사용자가 catch + 다음 액션 (push / merge / discard) 직접 결정.

## Anti-Patterns

| Wrong | Right |
|---|---|
| `executing-plans` (inline) 호출 | NEVER. D5 — 무조건 wave-parallel subagent. |
| Gate #14 게이트 발화 | NEVER. D5 — auto-flow 가 명시 override. |
| AskUserQuestion 호출 | NEVER. |
| docs-pretty 호출 | NEVER. |
| failure 1건 시 종료 | NEVER. D6 — 격리 후 계속. |

## Related Skills

- `js-super-subagent-driven-development` — wave-parallel 본 skill (호출 대상)
- `finishing-a-development-branch` — 끝에 자동 호출
- `scripts/preflight.subagent_task_entry_check` — Entry Guard
- `scripts/auto_flow.find_latest_slug` — slug 추론
```

- [ ] **Step 3: 정적 grep 검증** —
  - `grep -c "AskUserQuestion" skills/auto-executing-plans/SKILL.md` ≤ 1
  - `grep -c "docs-pretty" skills/auto-executing-plans/SKILL.md` ≤ 1
  - `grep -c "wave-parallel" skills/auto-executing-plans/SKILL.md` ≥ 2
  - `grep -c "Gate #14" skills/auto-executing-plans/SKILL.md` ≥ 1
  - `grep -c "finishing-a-development-branch" skills/auto-executing-plans/SKILL.md` ≥ 2

- [ ] **Step 4: Commit** — `git add skills/auto-executing-plans/SKILL.md && git commit -m "feat(auto-executing-plans): wave-parallel 강제 + Gate #14 override + finishing 자동 (v1.1.17)"`

---

### Task 6: commands/auto-brainstorm.md — slash entry

**Files:**
- Create: `commands/auto-brainstorm.md`

**Model**: haiku

- [ ] **Step 1: failing 정적 grep** — 없음.

- [ ] **Step 2: 작성**

**수정 후** (new file: `commands/auto-brainstorm.md`):

```markdown
---
description: auto-flow 진입 — Socratic clarifying Q + AI 자동 진행 + 4 단계 chain (brainstorm → design → write-plan → execute-plan) 끝까지. 사용자 입력은 clarifying Q 답변에만.
---

# /auto-brainstorm

피처명을 인수로 주거나 (`/auto-brainstorm 사용자 잔액 출금`) 인수 없이 호출하면 한 줄 안내 후 진행. 이 커맨드는 `auto-brainstorming` skill 을 invoke 합니다.

산출물:
- `docs/features/<오늘날짜>-<slug>/<slug>-requirements.md` (Socratic free-form, RAW)

다음 단계 (자동): `/auto-design` → `/auto-write-plan` → `/auto-execute-plan`

mid-flight 인터럽트: 각 skill 전환 시 1줄 notice — `stop` / `멈춰` / `잠깐` 등 입력 시 cleanly exit.
```

- [ ] **Step 3: Commit** — `git add commands/auto-brainstorm.md && git commit -m "feat(commands): /auto-brainstorm slash entry (v1.1.17)"`

---

### Task 7: commands/auto-design.md — slash entry

**Files:**
- Create: `commands/auto-design.md`

**Model**: haiku

- [ ] **Step 1**: 작성 (Task 6 패턴 동일, slug 인자 optional + latest 추론).

**수정 후** (new file: `commands/auto-design.md`):

```markdown
---
description: auto-flow 2단계 진입 — requirements.md 있는 상태에서 design 부터 chain 끝까지 자동. 인자 누락 시 latest <slug> 추론.
---

# /auto-design

`<slug>` 인자 optional. 누락 시 `docs/features/` 의 가장 최근 폴더 자동 선택. 이 커맨드는 `auto-designing-direction` skill 을 invoke 합니다.

산출물:
- `<slug>-tech-design.md` (RAW)

다음 단계 (자동): `/auto-write-plan` → `/auto-execute-plan`
```

- [ ] **Step 2: Commit** — `git add commands/auto-design.md && git commit -m "feat(commands): /auto-design slash entry (v1.1.17)"`

---

### Task 8: commands/auto-write-plan.md

**Files:**
- Create: `commands/auto-write-plan.md`

**Model**: haiku

- [ ] **Step 1**: Task 6 패턴 동일.

**수정 후** (new file: `commands/auto-write-plan.md`):

```markdown
---
description: auto-flow 3단계 진입 — tech-design.md 있는 상태에서 write-plan + execute-plan 자동.
---

# /auto-write-plan

`<slug>` 인자 optional. 인자 누락 시 latest <slug> 자동. 이 커맨드는 `auto-writing-plans` skill 을 invoke 합니다.

산출물:
- `<slug>-implementation-plan.md` (RAW, frontmatter `commit_policy: per-task`)

다음 단계 (자동): `/auto-execute-plan`
```

- [ ] **Step 2: Commit** — `git add commands/auto-write-plan.md && git commit -m "feat(commands): /auto-write-plan slash entry (v1.1.17)"`

---

### Task 9: commands/auto-execute-plan.md

**Files:**
- Create: `commands/auto-execute-plan.md`

**Model**: haiku

- [ ] **Step 1**: Task 6 패턴 동일.

**수정 후** (new file: `commands/auto-execute-plan.md`):

```markdown
---
description: auto-flow 4단계 진입 (마지막) — implementation-plan.md 있는 상태에서 wave-parallel subagent 강제 (Gate #14 override) + failure isolation + finishing 자동.
---

# /auto-execute-plan

`<slug>` 인자 optional. 인자 누락 시 latest implementation-plan.md 자동. 이 커맨드는 `auto-executing-plans` skill 을 invoke 합니다.

동작: 무조건 wave-parallel `js-super-subagent-driven-development` 호출 (Gate #14 자동승인 명시 override). failure isolation + end-of-run consolidator + finishing 자동.

종료 메시지: commit 수 + RISK 카운트 + blocked tasks list.
```

- [ ] **Step 2: Commit** — `git add commands/auto-execute-plan.md && git commit -m "feat(commands): /auto-execute-plan slash entry (v1.1.17)"`

---

### Task 10: CLAUDE.md — auto-flow ↔ 기존 4 skill mirror 결합 메모

**Files:**
- Modify: `CLAUDE.md` (끝부분 신규 섹션 추가)

**Model**: sonnet

- [ ] **Step 1: failing 정적 grep** — `grep -c "auto-flow" CLAUDE.md` → 0.

- [ ] **Step 2: 끝부분 신규 섹션 추가**

**원본** (`CLAUDE.md` 끝부분, 마지막 섹션 마지막 줄 — `## TaskCreate 명칭 룰` 직후 마지막 줄을 anchor):

(현재 CLAUDE.md 끝부분 — `## TaskCreate 명칭 룰` 섹션 끝)

**수정 후** (그 직후 신규 섹션):

```markdown
## auto-flow ↔ 기존 4 skill mirror 결합 (v1.1.17+)

`auto-flow` 4 신규 skill (skills/auto-{brainstorming,designing-direction,writing-plans,executing-plans}/) 은 기존 4 skill 의 핵심 로직을 mirror 한 패턴 (og-* 와 동일). 다음 룰 적용:

- **기존 4 skill body 변경 0** — auto-* 본문은 self-contained mirror. 본 4 skill 어떤 라인도 손대지 않음. 회귀 catch: `git diff HEAD~1 HEAD -- skills/{brainstorming,designing-direction,writing-plans,executing-plans}/SKILL.md` empty 보장.
- **Gate #14 (실행 모드 선택) override 명시** — v1.1.12+ "자동승인 절대 X" 룰을 auto-executing-plans 가 명시 override. 일반 `/execute-plan` 영향 0 (게이트 그대로). auto-* 명시적 invoke 시에만 작동.
- **docs-pretty 호출 부재** (v1.1.17+, PRD D9 amend) — auto-* 본문 어디에도 docs-pretty 호출 박지 않음. RAW 산출물 그대로 commit. 일반 흐름 영향 0. 회귀 catch: `for f in skills/auto-*/SKILL.md; do grep -c "docs-pretty" "$f"; done` → 모두 0 (Anti-Patterns 표 안의 1건만 허용).
- **AskUserQuestion 호출 부재** — auto-* 본문 어디에도 AskUserQuestion 호출 X. clarifying Q 는 메인 turn 의 일반 prose 질의로 처리.
- **Visual Companion / 카테고리 미니질문 / question plan 동의 등 PRD-mode 분기 부재** — Socratic only (D3).

요약: auto-* 추가 / 변경은 atomic 으로 묶어 처리. 기존 4 skill 변경 + auto-* 변경 같이 commit X (분리 release).
```

- [ ] **Step 3: 정적 grep 검증** —
  - `grep -c "auto-flow" CLAUDE.md` ≥ 1
  - `grep -c "Gate #14.*override" CLAUDE.md` ≥ 1
  - `grep -c "docs-pretty 호출 부재" CLAUDE.md` ≥ 1

- [ ] **Step 4: Commit** — `git add CLAUDE.md && git commit -m "docs(claude-md): auto-flow ↔ 기존 4 skill mirror 결합 메모 (v1.1.17)"`

---

### Task 11: H7~H10 dogfood fixtures — auto-flow 시나리오

**Files:**
- Create: `skills/js-super-subagent-driven-development/tests/H7-auto-brainstorm-small/README.md`
- Create: `skills/js-super-subagent-driven-development/tests/H8-auto-design-from-existing/README.md`
- Create: `skills/js-super-subagent-driven-development/tests/H9-auto-flow-stop-interrupt/README.md`
- Create: `skills/js-super-subagent-driven-development/tests/H10-auto-execute-blocked-task/README.md`
- Modify: `skills/js-super-subagent-driven-development/tests/README.md` (색인 H7~H10 추가)

**Model**: sonnet

- [ ] **Step 1: failing 검증** — `ls skills/js-super-subagent-driven-development/tests/H{7,8,9,10}*` → 0건.

- [ ] **Step 2: H7 fixture 작성** — `/auto-brainstorm` small 피처 시나리오: 1 clarifying Q + AI 자동 + chain 끝까지.

- [ ] **Step 3: H8 fixture 작성** — `/auto-design` (PRD 있음) → design 부터 chain 끝.

- [ ] **Step 4: H9 fixture 작성** — transition notice 직후 "stop" 입력 → cleanly exit + 다음 단계 수동 안내.

- [ ] **Step 5: H10 fixture 작성** — auto-execute 도중 1 task BLOCKED → failure isolation + 다음 wave + finishing 에서 blocked 노출.

- [ ] **Step 6: tests/README.md 색인 갱신** — `## v1.1.17+ — auto-flow dogfood fixtures` 섹션 추가, H7~H10 4 줄 색인.

- [ ] **Step 7: 검증** — `ls skills/js-super-subagent-driven-development/tests/H{7,8,9,10}*/README.md` → 4건. `grep -c "^- H[7-9]\|^- H10" tests/README.md` ≥ 4.

- [ ] **Step 8: Commit** — `git add skills/js-super-subagent-driven-development/tests/H{7,8,9,10}*/ skills/js-super-subagent-driven-development/tests/README.md && git commit -m "test(subagent-dd): H7~H10 dogfood fixtures (auto-flow v1.1.17)"`

---

### Task 12: 정적 grep 검증 (F1~F8) + pytest 통합 PASS

**Files:**
- (검증 only — 코드 수정 없음. `[검증]` change-history entry 발화)

**Model**: haiku

- [ ] **Step 1: F1 (commands/auto-* 4 파일)** — `ls commands/auto-*.md | wc -l` → 4.
- [ ] **Step 2: F2 (skills/auto-* 4 파일 + frontmatter description)** — `for f in skills/auto-*/SKILL.md; do grep -c "^description:" "$f"; done` → 모두 1.
- [ ] **Step 3: F3 (기존 4 skill 변경 0)** — `git diff HEAD~12 HEAD -- skills/{brainstorming,designing-direction,writing-plans,executing-plans}/SKILL.md` → empty (Task 1~10 외 영향 X 검증, Task 카운트는 실제 SHA 로 조정).
- [ ] **Step 4: F4 (og-* 변경 0)** — `git diff HEAD~12 HEAD -- skills/og-*/SKILL.md` → empty.
- [ ] **Step 5: F5 (CLAUDE.md 신규 섹션)** — `grep -c "auto-flow ↔ 기존 4 skill mirror 결합" CLAUDE.md` → 1.
- [ ] **Step 6: F6 (auto-* 본문 AskUserQuestion 호출 부재)** — `for f in skills/auto-*/SKILL.md; do grep -c "AskUserQuestion" "$f"; done` → 모두 ≤ 1 (Anti-Patterns 표만).
- [ ] **Step 7: F7 (auto-* 본문 transition notice 패턴)** — `grep -c "Auto-proceeding to" skills/auto-*/SKILL.md` → 모든 파일에서 ≥ 1 (auto-executing-plans 는 finishing transition 으로 ≥ 1, 형식은 "auto-flow 완료").
- [ ] **Step 8: F8 (auto-* 본문 docs-pretty 호출 부재)** — `for f in skills/auto-*/SKILL.md; do grep -c "docs-pretty" "$f"; done` → 모두 ≤ 1 (Anti-Patterns 표만).
- [ ] **Step 9: pytest 통합** — `pytest scripts/tests/ -v` → 기존 36 + auto_flow 11+ = 47+ PASS.

- [ ] **Step 10: Commit (verification-only entry)** — `[검증]` change-history entry 자동 처리 (consolidator 시).

---

### Task 13: bump-version.sh 1.1.15 → 1.1.17 (v1.1.16 backlog 미리 분리 명시)

**Files:**
- Run: `bash scripts/bump-version.sh 1.1.17`
- Verify: 6 manifest 일치

**Model**: haiku

- [ ] **Step 1**: bump 실행. v1.1.16 은 backlog 2건 별도 micro-patch — 본 release 와 분리.
- [ ] **Step 2**: 6 manifest 검증.
- [ ] **Step 3: Commit** — `git add .claude-plugin/plugin.json .claude-plugin/marketplace.json package.json .codex-plugin/plugin.json .cursor-plugin/plugin.json gemini-extension.json && git commit -m "chore: bump version 1.1.15 → 1.1.17 (skip 1.1.16 — reserved for backlog micro-patch)"`

---

### Task 14: HANDOFF.md 갱신

**Files:**
- Modify: `HANDOFF.md` (local only — gitignored)

**Model**: sonnet

- [ ] **Step 1**: HANDOFF 갱신 — v1.1.17 release 결과 / 산출물 / What Worked / Risk Register 갱신 / Next Steps (v1.1.16 backlog 미해결 + auto-flow dogfood).
- [ ] **Step 2**: 검증 — `grep -c "v1.1.17\|auto-flow" HANDOFF.md` ≥ 5.
- [ ] **Step 3**: HANDOFF .gitignore — commit X.

---

## 2. 위험 코드 지점

tech-design §6 R1~R11 → 구체 위치 + mitigation 매핑:

- `skills/auto-designing-direction/SKILL.md` Step 3 (AI 자동 design decision) — **side-effect**: spec drift 가능성. mitigation: §5 결정+대안 비교 logged + verifying-spec 4축 보고서 transition 직전 노출 + change-history 보존. (R1)
- `skills/auto-executing-plans/SKILL.md` Step 4 (failure isolation) — **side-effect**: blocked 다수 시 부분 commit 잔존. mitigation: end-of-run blocked list 노출 + finishing 종료 메시지 명확화. (R2, R9)
- `skills/auto-executing-plans/SKILL.md` Step 3 (wave-parallel 강제) — **breaking**: Gate #14 override v1.1.12+ 룰 위반. mitigation: CLAUDE.md 결합 메모 + auto-* 명시적 invoke 시에만 작동. (R3)
- `skills/auto-{brainstorming,designing-direction,writing-plans,executing-plans}/SKILL.md` 본문 docs-pretty / AskUserQuestion 호출 부재 — **breaking**: caller 책임 패턴 위반 가능성. mitigation: F8 정적 grep + Anti-Patterns 표 명시. (R4)
- `skills/auto-*/SKILL.md` Step 6/7 transition (parse_interrupt) — **side-effect**: "stop" catch false negative. mitigation: scripts/auto_flow.py broad pattern (stop/abort/멈춰/잠깐/중단/취소/잠시만) + 메인 모호 시 한 번 더 명시 확인. (R5, R7, R11)
- `skills/auto-executing-plans/SKILL.md` slug 추론 (find_latest_slug) — **breaking**: false positive 다른 폴더 진입. mitigation: 1줄 노출 (`⚙️ <slug> 자동 선택. 다른 폴더면 'stop'`). (R8)
- `skills/auto-*/SKILL.md` Skill tool chain — **breaking**: 1 단계 실패 시 전체 멈춤 + 부분 commit 잔존. mitigation: 각 skill 산출물 commit 시도 + 실패 시 working tree 그대로 + transition notice 안 발화. (R10)
- `scripts/auto_flow.py` (Task 1) — **breaking**: regex pattern 변경 시 caller 4 skill 동시 영향. mitigation: unit test 11+ + CLAUDE.md mirror 결합 메모. (보강)

## 3. 롤백 전략

- **Code**: per-task commit → 문제 시 `git revert` 또는 `git reset --hard <SHA-before-task>`. batch [코드-수정] entry 가 SHA 보관.
- **`scripts/auto_flow.py` 시그니처 변경**: helper 가 신규 — caller 4 skill 도 신규. 같이 revert 하면 깔끔.
- **Skill 본문 4개 신규**: 신규 디렉토리 — `git revert` 만으로 즉시 제거.
- **commands/auto-* 4개 신규**: 동일.
- **CLAUDE.md 결합 메모**: revert 만으로 복원.
- **Manifest bump**: `git revert` 로 1.1.17 → 1.1.15 복원. marketplace 갱신 시 사용자 측에서 `/plugin marketplace update` 재실행.
- **Feature flag X**: skill body + helper 추가만 — feature flag 무관. 일반 흐름 (기존 `/brainstorm` 등) 영향 0 — auto-* 미사용 시 invocable X.

---
## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-10 19:50] [구현계획서-수정]
- **id**: CH-20260510-005
- **이유**: 신규 구현계획서 작성 (v1.1.17 — auto-flow 14 task TDD 분해 / Model 힌트 / Before/After 코드블록 / Bootstrap notice / 버전 결정 v1.1.17 단독 release)
- **무엇이**: auto-flow-implementation-plan.md 전체 (Header + §1 14 task + §2 R1~R11 + §3 롤백 전략)
- **영향범위**: 없음 (최초 생성)
- **연관 항목**: CH-20260510-001 (PRD initial), CH-20260510-002 (PRD D9 amend), CH-20260510-003 (tech-design initial), CH-20260510-004 (tech-design D-T12 amend)
### [2026-05-10 21:00] [코드-수정] (batch: tasks 1..11)
- **id**: CH-20260510-006
- **이유**: 서브에이전트 모드 task batch 종합 (end-of-run consolidation)
- **무엇이**: CLAUDE.md, commands/auto-brainstorm.md, commands/auto-design.md, commands/auto-execute-plan.md, commands/auto-write-plan.md, scripts/auto_flow.py, scripts/tests/test_auto_flow.py, skills/auto-brainstorming/SKILL.md, skills/auto-designing-direction/SKILL.md, skills/auto-executing-plans/SKILL.md, skills/auto-writing-plans/SKILL.md, skills/js-super-subagent-driven-development/tests/H10-auto-execute-blocked-task/README.md, skills/js-super-subagent-driven-development/tests/H7-auto-brainstorm-small/README.md, skills/js-super-subagent-driven-development/tests/H8-auto-design-from-existing/README.md, skills/js-super-subagent-driven-development/tests/H9-auto-flow-stop-interrupt/README.md, skills/js-super-subagent-driven-development/tests/README.md
- **영향범위**: 누적 (task별 세부 참조)
- **위험 카테고리**: breaking
- **task별 세부 (11건)**:
  - Task 1: `scripts/auto_flow.py:1-47` — parse_interrupt + find_latest_slug helper functions (`none`) — commits: 
  - Task 1: `scripts/tests/test_auto_flow.py:1-38` — 14 unit tests (parametrized + explicit) (`none`) — commits: 
  - Task 2: `skills/auto-brainstorming/SKILL.md:1-80` — Socratic auto skill body — clarifying Q + AI 자동 + transition (`breaking`) — commits: 
  - Task 3: `skills/auto-designing-direction/SKILL.md:1-70` — auto-design skill body — adaptive 7-topic + AI 자동 + verify 노출 + transition (`breaking`) — commits: 
  - Task 4: `skills/auto-writing-plans/SKILL.md:1-65` — auto-write-plan skill body (`breaking`) — commits: 
  - Task 5: `skills/auto-executing-plans/SKILL.md:1-60` — auto-execute-plan skill body — wave-parallel 강제 + Gate #14 override + finishing 자동 (`breaking`) — commits: 
  - Task 6: `commands/auto-brainstorm.md:1-13` — slash entry for auto-brainstorming (`none`) — commits: 
  - Task 7: `commands/auto-design.md:1-12` — slash entry for auto-designing-direction (`none`) — commits: 
  - Task 8: `commands/auto-write-plan.md:1-12` — slash entry for auto-writing-plans (`none`) — commits: 
  - Task 9: `commands/auto-execute-plan.md:1-13` — slash entry for auto-executing-plans (`none`) — commits: 
  - Task 10: `CLAUDE.md:165-180` — auto-flow mirror 결합 메모 + Gate #14 override + docs-pretty 부재 (`none`) — commits: 
  - Task 11: `skills/js-super-subagent-driven-development/tests/H7-auto-brainstorm-small/README.md:1-30` — auto-brainstorm small fixture (`none`) — commits: 
  - Task 11: `skills/js-super-subagent-driven-development/tests/H8-auto-design-from-existing/README.md:1-30` — auto-design from existing fixture (`none`) — commits: 
  - Task 11: `skills/js-super-subagent-driven-development/tests/H9-auto-flow-stop-interrupt/README.md:1-30` — stop interrupt fixture (`none`) — commits: 
  - Task 11: `skills/js-super-subagent-driven-development/tests/H10-auto-execute-blocked-task/README.md:1-35` — BLOCKED failure isolation fixture (`none`) — commits: 
  - Task 11: `skills/js-super-subagent-driven-development/tests/README.md:<actual>` — 색인 v1.1.17+ 섹션 + H7~H10 4 줄 (`none`) — commits: 
- **연관 commits**: 
- **변경 전/후 코드**: 생략 — `git show <SHA>` 로 조회

### [2026-05-10 21:00] [검증] (Task 12)
- **id**: CH-20260510-007
- **이유**: F1~F8 정적 grep + pytest 통합 검증 (Task 12 — 코드 변경 0건)
- **무엇이**: F1 (commands/auto-* 4 파일) / F2 (skills/auto-* 4 파일 + frontmatter description 1 each) / F3 (기존 4 skill 변경 0 — git diff empty) / F4 (og-* 변경 0) / F5 (CLAUDE.md 신규 섹션 1) / F6 (auto-* AskUserQuestion 본문 부재 — 2 매치 each = frontmatter + Anti-Patterns 만) / F7 (transition notice 모두 ≥ 1) / F8 (auto-* docs-pretty 본문 호출 부재 — 2~3 매치 each = frontmatter + prose 명시 + Anti-Patterns 만, 실제 호출 0) / pytest 50 PASS
- **영향범위**: 없음 (검증 only)
- **연관 항목**: CH-20260510-006 (batch tasks 1..11)
