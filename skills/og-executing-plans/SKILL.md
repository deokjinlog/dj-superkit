---
name: og-executing-plans
description: "Upstream-original (superpowers 5.0.7) executing-plans, exposed under js-super. Use when invoked via /og-execute-plan after /og-write-plan. Identical behavior to upstream executing-plans — load plan, review critically, execute task-by-task, follow steps exactly. No 변경이력 / 위험주석 / git-fast mode / batched logging — those are js-super extensions, intentionally absent here."
---

# Executing Plans (og — upstream original)

This is the **upstream-original superpowers `executing-plans` skill**, preserved verbatim under the `og-` prefix so users of js-super can opt back into the original behavior without uninstalling js-super and reinstalling upstream. It is identical to upstream except:

1. `name` is `og-executing-plans` (avoids collision with js-super's modified `executing-plans`)
2. The note about subagent path points to the untouched-upstream `subagent-driven-development` (which js-super did not modify, so no og-* sibling is needed)

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the og-executing-plans skill to implement this plan."

**Note:** Tell your human partner that Superpowers works much better with access to subagents. The quality of its work will be significantly higher if run on a platform with subagent support (such as Claude Code or Codex). If subagents are available, use superpowers:subagent-driven-development instead of this skill (untouched-upstream, no og- variant needed — js-super did not modify it).

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create TodoWrite and proceed

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **superpowers:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
- **js-super:og-writing-plans** - Creates the plan this skill executes
- **superpowers:finishing-a-development-branch** - Complete development after all tasks
