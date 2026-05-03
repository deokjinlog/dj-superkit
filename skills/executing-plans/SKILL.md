---
name: executing-plans
description: Use when you have a written implementation plan (<slug>-implementation-plan.md) to execute in a separate session with review checkpoints. js-superpowers extension — code edits use a per-edit fast path (before-snapshot → risk-annotation 6-checklist → apply edit with RISK comments) and ONE consolidated change-history [코드-수정] entry per task (not per edit), drastically reducing 구현계획서.md Read/Edit cost.
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks task-by-task, with strict per-edit discipline that captures before/after code and risk annotations into <slug>-implementation-plan.md change-history.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** This plugin works much better with subagent support. If subagents are available (Claude Code, Codex), prefer `subagent-driven-development` over this skill — fresh subagent per task with two-stage review yields higher quality.

## When to Use

- A <slug>-implementation-plan.md exists in `docs/features/<date>-<slug>/`
- Inline (single-session) execution preferred over per-task subagents
- Each task in the plan follows TDD bite-sized steps

## Plan Loading

### Step 1: Load and Review Plan
1. Read `docs/features/<date>-<slug>/<slug>-implementation-plan.md`
2. Review critically — list any gaps or concerns
3. If concerns exist: raise them with the user before starting
4. If clean: create TodoWrite tasks (one per plan task) and proceed

## Code Edit Discipline (REQUIRED — js-superpowers extension)

<HARD-GATE>
Code edits in a task use a **two-phase pattern** (per-edit fast steps + one batched log at task end):

**Phase 1 — Per code edit (repeat for each edit in the task):**
1. **Before-snapshot**: Read the target file → capture the original code for the affected line range. Hold the snapshot in memory; do NOT write to 변경이력 yet.
2. **Risk check**: Run risk-annotation 6-checklist on the planned change.
3. **Apply edit**: Edit/Write the file (insert `# ⚠️ RISK(...)` comments above risky lines as needed). Trust the Edit tool's success/failure return — do NOT re-Read just to confirm the comment landed.

(Repeat 1-3 for every code edit in the task. Track all `(file:line, before, after, risk_categories)` tuples in memory.)

**Phase 2 — Once per task, AFTER all task edits + tests pass:**
4. **Batched log**: Read <slug>-implementation-plan.md ONCE. Build ONE consolidated [코드-수정] entry covering ALL code edits made in this task. Edit ONCE to append. (Schema: id / 이유 / 무엇이 / 영향범위 / 위험 카테고리 / 세부 변경 list / 변경 전 코드 / 변경 후 코드 — see change-history skill for batched format.)

NEVER commit code without completing Phase 2. The before-snapshots must be captured BEFORE each edit (otherwise originals are gone) and held in memory until Phase 2.
</HARD-GATE>

## Trivial-Edit Exception (skip full discipline for tiny changes)

For changes that meet ALL of the following criteria, you MAY substitute a "trivial" path:

- Edit affects ≤ 3 lines
- No logic change (comments / docstrings / typos / unused-import cleanup / import reordering / whitespace only)
- risk-annotation 6-checklist returns 0/6 triggers (no side-effect / race / breaking / perf signal)

When trivial:

1. **Skip Step 1 (Before-snapshot)** — no full block will be logged, so capture is unnecessary
2. Step 2 (risk check) still runs to confirm 0/6
3. Step 3 (Apply edit) runs as usual (typically no RISK comment needed since 0/6)
4. Step 4 (Log) writes a **trivial entry** instead of the full schema:

```markdown
### [YYYY-MM-DD HH:MM] [코드-수정] (trivial)
- **id**: CH-YYYYMMDD-NNN
- **이유**: <one-line reason, e.g. "타이포 수정 (witdraw → withdraw)">
- **무엇이**: <file:line>
```

No 영향범위, no 위험 카테고리, no before/after code blocks.

**If ANY criterion is uncertain → fall back to full discipline.** Trivial is a fast path, not a shortcut for "anything that looks small".

<HARD-GATE>
Triviality is determined ONLY by the three criteria above. Logic changes — even one-line ones — are NOT trivial. When in doubt, take the safe path.
</HARD-GATE>

## Process Flow

```dot
digraph exec_flow {
    "Load <slug>-implementation-plan.md" [shape=box];
    "Critical review,\nraise concerns?" [shape=diamond];
    "Discuss with user" [shape=box];
    "Create TodoWrite" [shape=box];
    "Pick next [ ] task" [shape=box];
    "TDD: write failing test" [shape=box];
    "Run test → FAIL" [shape=box];
    "More edits in task?" [shape=diamond];
    "Read target file (before-snapshot)\n— hold in memory" [shape=box];
    "risk-annotation 6-checklist" [shape=box];
    "Apply Edit (with RISK comments)" [shape=box];
    "Run tests for this task" [shape=box];
    "All pass?" [shape=diamond];
    "BATCHED LOG: ONE [코드-수정] entry\nfor whole task\n(Read+Edit 구현계획서.md once)" [shape=box];
    "Commit (skip if no git)" [shape=box];
    "Mark task [x]" [shape=box];
    "All tasks done?" [shape=diamond];
    "Fix and retry" [shape=box];
    "Use finishing-a-development-branch" [shape=doublecircle];

    "Load <slug>-implementation-plan.md" -> "Critical review,\nraise concerns?";
    "Critical review,\nraise concerns?" -> "Discuss with user" [label="yes"];
    "Discuss with user" -> "Create TodoWrite";
    "Critical review,\nraise concerns?" -> "Create TodoWrite" [label="no"];
    "Create TodoWrite" -> "Pick next [ ] task";
    "Pick next [ ] task" -> "TDD: write failing test";
    "TDD: write failing test" -> "Run test → FAIL";
    "Run test → FAIL" -> "More edits in task?";
    "More edits in task?" -> "Read target file (before-snapshot)\n— hold in memory" [label="yes"];
    "Read target file (before-snapshot)\n— hold in memory" -> "risk-annotation 6-checklist";
    "risk-annotation 6-checklist" -> "Apply Edit (with RISK comments)";
    "Apply Edit (with RISK comments)" -> "More edits in task?";
    "More edits in task?" -> "Run tests for this task" [label="no — task edits done"];
    "Run tests for this task" -> "All pass?";
    "All pass?" -> "BATCHED LOG: ONE [코드-수정] entry\nfor whole task\n(Read+Edit 구현계획서.md once)" [label="yes"];
    "All pass?" -> "Fix and retry" [label="no"];
    "Fix and retry" -> "Apply Edit (with RISK comments)";
    "BATCHED LOG: ONE [코드-수정] entry\nfor whole task\n(Read+Edit 구현계획서.md once)" -> "Commit (skip if no git)";
    "Commit (skip if no git)" -> "Mark task [x]";
    "Mark task [x]" -> "All tasks done?";
    "All tasks done?" -> "Pick next [ ] task" [label="no"];
    "All tasks done?" -> "Use finishing-a-development-branch" [label="yes"];
}
```

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails repeatedly, instruction unclear)
- Plan has critical gaps preventing the next task
- A 위험 카테고리 is genuinely ambiguous AND the trigger seems significant
- Verification fails after two retries

Ask the user rather than guessing.

## When to Revisit Earlier Steps

**Return to Step 1 (Load and Review Plan) when:**
- The user updates the plan based on your feedback
- A fundamental approach in the plan needs rethinking (e.g., chosen library doesn't fit, an FR was misread)
- Mid-execution discoveries invalidate later tasks

**Don't force through blockers** — stop and ask. The plan can be wrong. If it is, route the change through `change-propagation` so <slug>-implementation-plan.md is updated coherently before resuming.

## Anti-Patterns

| Wrong | Right |
|---|---|
| Edit first, capture before-snapshot later | Always Read → snapshot → Edit. Otherwise original is gone. |
| Batch change-history entries at session end | Per-task immediate logging. Context evaporates fast. |
| Skip RISK annotation because "looks safe" | Run the 6-checklist. 0/6 means no annotation, but the check happens. |
| Commit without completing all 4 steps | HARD-GATE violation. Revert + redo. |
| Marking a logic-changing edit as "trivial" to skip discipline | Triviality requires zero logic change AND 0/6 risk triggers AND ≤3 lines. Logic changes are NEVER trivial. |
| Force progress through a blocker | Stop. Ask. The plan can be wrong. |

## Red Flags

| Thought | Reality |
|---|---|
| "This is a tiny tweak, skip discipline" | Tiny tweaks are exactly where regressions hide. Run the 4 steps. |
| "User won't notice if I skip the entry" | The user is reviewing 변경이력 later. They'll notice. |
| "Plan said do X, but I think Y is better" | Stop. Update the plan via change-propagation, then proceed. |

## Step 3: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use `finishing-a-development-branch`
- Follow that skill to verify tests, present options, execute the user's choice

## Remember
- Review plan critically before starting
- Follow plan steps exactly
- 4-step discipline per code edit (HARD-GATE)
- Don't skip verifications — if a step says "run X, expect Y", run X and confirm Y
- Reference skills when the plan says to (e.g., "use risk-annotation here")
- Never start implementation on main/master without explicit user consent
- Ask when blocked

## Related Skills

- `risk-annotation` — invoked on every code edit for the 6-checklist
- `change-history` — invoked on every code edit for the [코드-수정] entry
- `change-propagation` — invoked when an in-flight insight requires plan/spec edits
- `subagent-driven-development` — alternative execution mode (per-task subagent)
- `finishing-a-development-branch` — final wrap-up after all tasks
