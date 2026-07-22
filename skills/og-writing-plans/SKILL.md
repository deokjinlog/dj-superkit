---
name: og-writing-plans
description: "Upstream-original (superpowers 5.0.7) writing-plans, exposed under intent-locked-workflow. Use when invoked via /og-write-plan after /og-brainstorm. Identical behavior to upstream writing-plans except for the og- naming and downstream pointer (handoff goes to og-executing-plans / subagent-driven-development). Use this when the intent-locked-workflow extended workflow (변경이력 / 위험주석 / verifying-spec / generating-html) feels heavy and you want the original superpowers experience."
---

# Writing Plans (og — upstream original)

This is the **upstream-original superpowers `writing-plans` skill**, preserved verbatim under the `og-` prefix so users of intent-locked-workflow can opt back into the original behavior without uninstalling intent-locked-workflow and reinstalling upstream. It is identical to upstream except:

1. `name` is `og-writing-plans` (avoids collision with intent-locked-workflow's modified `writing-plans`)
2. Execution Handoff offers `og-executing-plans` for inline execution; subagent-driven path still points to the untouched-upstream `subagent-driven-development` (which intent-locked-workflow did not modify, so no og-* sibling is needed)
3. Supporting file `plan-document-reviewer-prompt.md` was a vendored orphan even in upstream and has been removed during intent-locked-workflow cleanup — this skill never referenced it

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the og-writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by og-brainstorming skill).

**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)

## Checklist

- [ ] Scope Check — 작업 범위 확인
- [ ] File Structure — plan 파일 경로 결정
- [ ] Bite-Sized Task Granularity — task 단위 분해
- [ ] Plan Document Header — frontmatter + 메타
- [ ] Task Structure — 각 task 본문 (Files / TDD steps / Risk / 코드 블록)
- [ ] Self-Review — plan 자체 검토 (no placeholders)
- [ ] Execution Handoff — og-executing-plans 안내

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use intent-locked-workflow:subagent-driven-development (recommended) or intent-locked-workflow:og-executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Remember
- Exact file paths always
- Complete code in every step — if a step changes code, show the code
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using og-executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use **`intent-locked-workflow:subagent-driven-development`** (upstream-untouched). ⚠️ NOT `subagent-driven` — that's the intent-locked-workflow extended variant with wave-parallel + RISK + 변경이력. og 흐름은 upstream 원본만 사용.
- Fresh subagent per task + two-stage review

**If Inline Execution chosen:**
- **REQUIRED SUB-SKILL:** Use intent-locked-workflow:og-executing-plans
- Batch execution with checkpoints for review

## Anti-Patterns (v2.0.2+ — og-flow subagent path 강화)

| Wrong | Right |
|---|---|
| `subagent-driven` 매치 — intent-locked-workflow 확장 wave-parallel 발화 | `intent-locked-workflow:subagent-driven-development` upstream 원본만 사용. og 흐름은 단순 fresh subagent + 2-stage review 유지. |
