---
name: og-executing-plans
description: "Upstream-original (superpowers 5.0.7) executing-plans, exposed under intent-locked-workflow. Use when invoked via /og-execute-plan after /og-write-plan. Identical behavior to upstream executing-plans — load plan, review critically, execute task-by-task, follow steps exactly. No 변경이력 / 위험주석 / git-fast mode / batched logging — those are intent-locked-workflow extensions, intentionally absent here."
---

# Executing Plans (og — upstream original)

This is the **upstream-original superpowers `executing-plans` skill**, preserved verbatim under the `og-` prefix so users of intent-locked-workflow can opt back into the original behavior without uninstalling intent-locked-workflow and reinstalling upstream. It is identical to upstream except:

1. `name` is `og-executing-plans` (avoids collision with intent-locked-workflow's modified `executing-plans`)
2. The note about subagent path points to the untouched-upstream `subagent-driven-development` (which intent-locked-workflow did not modify, so no og-* sibling is needed)

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the og-executing-plans skill to implement this plan."

**Note:** Tell your human partner that Superpowers works much better with access to subagents. The quality of its work will be significantly higher if run on a platform with subagent support (such as Claude Code or Codex). If subagents are available, use intent-locked-workflow:subagent-driven-development instead of this skill (untouched-upstream, no og- variant needed — intent-locked-workflow did not modify it).

## Checklist

- [ ] Step 1 — Plan 로드 + 비판적 검토 (Load and Review Plan)
- [ ] Step 2 — Task 실행 (Execute Tasks)
- [ ] Step 3 — Complete Development

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
- **REQUIRED SUB-SKILL:** Use intent-locked-workflow:finishing-a-development-branch
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
- **격리 워크스페이스 (전용 스킬 없음 — 직접 실행)** - 시작 전에 `git worktree add ../<repo>-<slug> -b <slug>` 로 격리. 이 플러그인엔 워크트리 스킬이 없으므로 스킬 호출을 기다리지 말 것
- **intent-locked-workflow:og-writing-plans** - Creates the plan this skill executes
- **intent-locked-workflow:finishing-a-development-branch** - Complete development after all tasks
