---
name: docs-pretty
description: Use during the initial-creation iteration loop of <slug>-requirements.md / <slug>-tech-design.md / <slug>-implementation-plan.md. Fires before user review on every draft (v1.1.15+ unified timing — pre-review per-draft). Re-fires on each user-fix iteration. STOPS firing once the first change-history entry is logged — that boundary marks "live doc". Dispatches a single Sonnet subagent (B) in fire-and-forget mode (v2.2.1+) — generates a sibling `.html` companion (사람 전용 시각화 사본) with semantic 1:1 preservation. Main does NOT wait for the result. RAW `.md` is shown to user as-is (v2.2.1 removed the v2.2.0 A format-only pass — B alone now handles human readability). NEVER invoked on change-history appends, change-propagation cascades (use `/regen-html` instead), or partial revisions.
---

# Docs Pretty (Pre-Review Formatting)

This skill prettifies a freshly written or rewritten feature MD just before the user reviews it during the initial creation phase. It exists because the agent-authored draft is content-correct but visually noisy (inconsistent header levels, ad-hoc list bullets, unaligned tables, rough spacing). This pass tightens visual hierarchy WITHOUT touching meaning, so the user reviews a clean version. The user's review is the safety net: if the format pass ever drifts meaning, they catch it BEFORE it gets locked into change-history.

**Announce at start:** "I'm using the docs-pretty skill to format `<file>` before the user reviews it."

<HARD-GATE>
Trigger timing (v1.1.15+ 통일 — pre-review per-draft):

모든 doc 타입에서 동일하게 발화: 메인이 RAW 작성 → docs-pretty (사용자 리뷰 직전) → 사용자가 prettified 본문 검토 → 승인 → change-history. 사용자 fix 요청 시 메인이 in-memory raw 갱신 후 docs-pretty 재발화 (per-draft loop).

- **requirements.md** — brainstorming 흐름 끝, 사용자 리뷰 직전. user-fix 시 재발화.
- **tech-design.md** — designing-direction 흐름 끝, 사용자 리뷰 직전 (combined approval gate 와 결합). user-fix 시 재발화.
- **implementation-plan.md** — writing-plans 흐름 끝, verifying-spec + code-pretty 통과 후, 사용자 리뷰 직전. user-fix 시 재발화 (기존 패턴 유지).

STOPS firing the moment the first `change-history` entry has been logged. That boundary marks the doc as "live" — from then on, no docs-pretty.

Specifically, docs-pretty MUST NOT run on:
- Any user-requested edit AFTER the first change-history entry exists (partial revisions, fixes, additions)
- Any `change-history` entry append (the `## 변경이력` footer is the audit trail — never reformat it)
- Any `change-propagation` cascade
- Any in-task code-edit logging during `/execute-plan`

If you are unsure whether this is still in the "initial creation phase" — STOP. Look for an existing `## 변경이력` footer with one or more entries. If ANY entry exists, this is NOT initial creation. Skip this skill.
</HARD-GATE>

## When to Use

| Trigger (yes) | Anti-trigger (no) |
|---|---|
| `brainstorming` just wrote RAW `<slug>-requirements.md`, about to show to user for review, no entries yet | User asked to update FR-3 wording in an already-live requirements.md (one with change-history entries) |
| `designing-direction` just wrote RAW `<slug>-tech-design.md`, about to show combined approval gate (doc + verify report), no entries yet | `change-propagation` is cascading edits across MDs |
| `writing-plans` just completed verifying-spec + code-pretty on `<slug>-implementation-plan.md`, about to show prettified plan to user, no `## 변경이력` entries yet | `change-history` is appending a `[코드-수정]` entry mid-`/execute-plan` |
| `brainstorming` or `designing-direction` user requested fix on draft — revise RAW, re-fire docs-pretty (per-draft loop) | First change-history entry has been logged — doc is now "live", do NOT fire |
| `writing-plans` user requested revision, plan re-written, verifying-spec re-ran, code-pretty re-ran — fire docs-pretty again | (none for pre-review timing — docs-pretty now fires before every user review) |

## Why fire-and-forget B (v2.2.1+)

HTML companion generation is a pure transformation task — no domain reasoning, no decisions. Loading the full doc into the main agent context is wasteful, and the main agent's reasoning model is overkill.

**Dispatch a single B subagent with `model: "sonnet"` and `run_in_background: true`.** Reasoning:

1. **AI 흐름은 `.md` 만 읽음** — A (v2.2.0 의 `.md` format-only pass) 의 가치는 사람 전용. B 의 `.html` 가 사람 가독성을 더 잘 흡수 (Mermaid / 시각화) → A 중복 제거 (v2.2.1).
2. **fire-and-forget** — 메인 latency 거의 0 (Task dispatch 비용만). 결과는 배경에서 사이드카로 떨어지고, `.js-super/html-regen.log` 에 silent log.
3. **의미 보존 우선** — Sonnet 의 instruction-following 이 Haiku 보다 negative constraints ("do NOT reword") 에 안정. 비용 대비 안전.
4. **시각화 휴리스틱 추론** — B 가 "어느 표를 Mermaid 로?" 같은 판단 필요 → Sonnet 추론력 필수.
5. **디바운스 3초** — 사용자 연속 fix 시 이전 subagent cancel + 새 dispatch. 마지막 fix 만 의미 있음.

Do NOT use Opus (overkill) or Haiku (rephrasing risk on Korean prose). Sonnet is the floor and ceiling for B.

## Process

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

### Step 2 — Dispatch single B subagent fire-and-forget (v2.2.1+)

Use ONE `Task` tool call with `run_in_background: true`. Main agent does NOT wait.

**Subagent B — `.html` companion**:
- `subagent_type`: `general-purpose`
- `model`: `sonnet`
- `run_in_background`: `true`
- `description`: `HTML companion for <filename>.md`
- `prompt`: load `skills/docs-pretty/html-companion-prompt.md`, fill `<ABSOLUTE_MD_PATH>` + `<ABSOLUTE_HTML_PATH>` (same dir, same basename, `.html` extension) + CH-id + timestamp (for footer stale marker)

**Debounce (3초)**: If a previous B subagent is still running for the same `<slug>`, cancel it before dispatching the new one. Log cancel event to `.js-super/html-regen.log`.

**A (v2.2.0 `.md` format-only pass) is REMOVED in v2.2.1.** RAW `.md` is shown to user as-is.

### Step 3 — Yield immediately (v2.2.1+ fire-and-forget)

Main does NOT wait for B subagent completion. Step 2 dispatch 직후:

1. **메인 즉시 return** — caller (brainstorming / designing-direction / writing-plans) 가 다음 turn 진행. RAW `.md` 가 사용자 리뷰 surface.
2. **B subagent 가 배경에서** `.html` 사이드카 작성. 자체 verification (B prompt 의 "Verification before writing" 룰) 이후 Write.
3. **silent log** — `.js-super/html-regen.log` 에 dispatch / 완료 / 실패 / cancel 모두 기록 (사용자 push X).
4. **사용자 push X** — B 결과는 silent. 사용자가 `.html` 부재 인지 시 `/regen-html` 수동 호출.

Failure handling (v2.2.1+ — fire-and-forget):
- **B 성공** → `.html` 사이드카 + silent log "OK"
- **B 실패** (Sonnet API 일시 장애 / verification 실패 등) → silent log "ERROR". `.html` 미생성. 사용자 다음에 `.html` 열려고 할 때 부재 인지 → `/regen-html` 수동.
- **메인 cancel (디바운스)** → 이전 B 작업 폐기, silent log "CANCEL". 새 B dispatch.

## Subagent Prompt Template

The dispatched subagent receives this exact prompt (filled in with the target path):

```
You are performing a STRICT format-only pass on a Korean spec document.

Target file: <ABSOLUTE_PATH>

Your job: improve READABILITY ONLY. The user will trust this pass to never alter meaning.

# Allowed changes (formatting only)

- Normalize Markdown header levels so hierarchy is consistent (e.g., one H1, H2 for top sections, H3 for subsections)
- Convert ad-hoc bullet styles to consistent `-` bullets; align nested list indentation to 2 spaces
- Reformat tables: align column pipes, add header separators if missing
- Tighten spacing: exactly one blank line between sections, no trailing whitespace, no triple-blank-line gaps
- Fix code-block fences (` ``` ` open/close), add language hints where the content makes the language obvious
- Add a blank line before/after lists, tables, code blocks where Markdown rendering benefits
- Convert obvious raw URLs to `<url>` autolinks if they appear standalone
- Standardize emphasis: bold for `**...**`, italic for `*...*` (no underscores for emphasis)

# FORBIDDEN — never do any of these

- Do NOT reword, paraphrase, summarize, expand, or "improve" any sentence
- Do NOT translate Korean ↔ English
- Do NOT reorder sections, list items, table rows, or paragraphs
- Do NOT add new content, examples, or commentary
- Do NOT remove content, even if it looks redundant or unclear
- Do NOT touch the YAML frontmatter (between `---` delimiters at top) — preserve byte-for-byte
- Do NOT touch the `## 변경이력` footer or anything under it — preserve byte-for-byte
- Do NOT change identifier strings: file names, slugs, function names, FR-N / NFR-N / CH-N IDs, Korean section headers (요구사항, 개발방향, 구현계획서, 변경이력, 위험 코드 지점, 롤백 전략, etc.)
- Do NOT change inline code spans (` `...` `) content — only fix fence consistency

# How to apply

1. Read the file in full
2. Apply ONLY allowed transformations
3. Write the result back to the SAME file path using the Write tool (overwrite)
4. Report: "Format pass done on <path>. Sections: <N>. Frontmatter preserved: yes/no. 변경이력 footer preserved: yes/no."

# Verification before writing

Before you call Write:
- Compare your output's section header list (text only, ignoring level) to the input — they MUST match exactly, in the same order
- Confirm the YAML frontmatter block (if present) is byte-identical
- Confirm the `## 변경이력` heading and everything beneath it is byte-identical

If ANY of these fail, do NOT write. Report the failure and stop.

You have one job: make it cleaner to read. Nothing else.
```

## Process Flow

```dot
digraph docs_pretty {
    "Calling skill ready\n(brainstorming/designing-direction/writing-plans)" [shape=box];
    "Pre-flight: file exists?\n변경이력 empty?\nfilename matches pattern?" [shape=diamond];
    "STOP — log reason, return to caller" [shape=box];
    "Dispatch subagent\n(general-purpose, model=sonnet)" [shape=box];
    "Subagent: Read → format-only → Write" [shape=box];
    "Main: Read file back\nspot-check headers/frontmatter/footer" [shape=box];
    "Sanity OK?" [shape=diamond];
    "Report to user, return to caller\n(caller now invokes change-history)" [shape=doublecircle];
    "Roll back: ask user to choose\n(restore from memory or accept)" [shape=box];

    "Calling skill ready\n(brainstorming/designing-direction/writing-plans)" -> "Pre-flight: file exists?\n변경이력 empty?\nfilename matches pattern?";
    "Pre-flight: file exists?\n변경이력 empty?\nfilename matches pattern?" -> "STOP — log reason, return to caller" [label="any check fails"];
    "Pre-flight: file exists?\n변경이력 empty?\nfilename matches pattern?" -> "Dispatch subagent\n(general-purpose, model=sonnet)" [label="all pass"];
    "Dispatch subagent\n(general-purpose, model=sonnet)" -> "Subagent: Read → format-only → Write";
    "Subagent: Read → format-only → Write" -> "Main: Read file back\nspot-check headers/frontmatter/footer";
    "Main: Read file back\nspot-check headers/frontmatter/footer" -> "Sanity OK?";
    "Sanity OK?" -> "Report to user, return to caller\n(caller now invokes change-history)" [label="yes"];
    "Sanity OK?" -> "Roll back: ask user to choose\n(restore from memory or accept)" [label="no"];
}
```

## Sanity-Check Details (post-dispatch)

The main agent's spot-check after the subagent returns:

| Check | How |
|---|---|
| Frontmatter intact | First Read line still `---`; closing `---` present at expected position |
| Section header count unchanged | Grep `^#{1,6} ` → count matches the pre-dispatch count (which the calling skill already knows from generating the doc) |
| `## 변경이력` heading present and footer empty | Grep `^## 변경이력` → 1 match; Grep `^### \[` after that line → 0 matches |
| Korean identifier headers preserved | Grep for the expected Korean section names (`요구사항`, `개발방향`, `구현계획서`, etc. as applicable to the doc type) |

If any check fails, the main agent reports the failure and asks the user whether to (a) accept the prettified version anyway, (b) revert (caller is responsible for restore — typically by re-running the doc-writing step from memory), or (c) skip docs-pretty and proceed.

## Anti-Patterns

| Wrong | Right |
|---|---|
| Run docs-pretty as part of `change-history` entry append | NEVER. docs-pretty fires before the FIRST entry, and never again. |
| Run docs-pretty when user requested a partial revision | NEVER. Partial revisions go through normal Edit + change-history. |
| Skip the pre-flight `변경이력` empty check | The check is what enforces "first creation only". Don't skip. |
| Use Opus / Haiku / main agent for the formatting | Sonnet only — Opus wastes the call, Haiku risks rephrasing Korean. |
| Let the subagent "make the prose flow better" | Forbidden. Pass prompt forbids all rewording. |
| Reformat the `## 변경이력` footer "to match the new style" | The footer is an audit trail with byte-identical preservation. |
| Skip the post-dispatch sanity check | The HARD-GATE on meaning preservation needs verification. |
| Re-run docs-pretty if the user later complains the doc "still looks rough" | One shot only. Subsequent improvements are normal Edit + change-history entries. |
| Read or reference the `.html` companion from any AI workflow (v2.2.0+) | NEVER. AI reads `.md` only. `.html` is human-only derived view. |
| Reference external CDN / URL in the `.html` (v2.2.0+) | NEVER. Self-contained inline only (D4). |
| Commit `.html` companion to git (v2.2.0+) | `.gitignore` blocks it. `.html` is derived from `.md`, regenerated on each docs-pretty firing. |
| Main waits for B subagent result (v2.2.1+) | NEVER. fire-and-forget — `run_in_background=true` + 즉시 Step 3 return. |
| Revive A (`.md` format-only pass, v2.2.1+) | NEVER. v2.2.1 에서 A 책임 제거. RAW `.md` 가 사용자 리뷰 surface. |
| Skip debounce (cancel 룰 누락, v2.2.1+) | 연속 fix 시 매번 dispatch → 비용 누적. 3초 디바운스 + 이전 cancel 강제. |
| Run docs-pretty for live doc edits without `/regen-html` (v2.2.1+) | live doc 진입 후 `docs-pretty` 자동 X. `change-propagation` 마지막 단계 또는 사용자 수동 `/regen-html` 만. |

## Red Flags (STOP if you think these)

| Thought | Reality |
|---|---|
| "The doc is short, I'll just format it inline in the main agent" | Subagent dispatch is mandatory — clean main context + model isolation. |
| "The user can always re-run if I mess up" | The audit chain begins at the first 변경이력 entry. Recovering is messy. Don't risk meaning loss. |
| "I'll let the subagent fix that one awkward sentence too" | Forbidden by the prompt. Awkward sentences are addressed via change-propagation if the user actually asks. |
| "Two passes will polish it more" | One shot only. Two passes = compound rephrasing risk. |

## Acceptance

A docs-pretty run is correct when ALL hold:

1. Pre-flight checks all passed (file exists, `## 변경이력` empty, filename pattern matches)
2. Subagent was dispatched with `model: sonnet` and the strict format-only prompt
3. Post-dispatch sanity checks all passed (frontmatter intact, header count unchanged, footer empty, Korean identifiers preserved)
4. The calling skill received control back and is about to invoke `change-history` for the first entry
5. No `## 변경이력` entry was added by docs-pretty itself (logging is the caller's job, with `[<doc-type>-수정]` tag for "신규 ... 결과")

## Related Skills

- `brainstorming` — calls this on first save of `<slug>-requirements.md`
- `designing-direction` — calls this on first save of `<slug>-tech-design.md`
- `writing-plans` — calls this on first save of `<slug>-implementation-plan.md`
- `change-history` — invoked by the caller AFTER docs-pretty returns; logs the first entry on the now-prettified doc
- `change-propagation` — for any post-init revision; docs-pretty is NEVER part of that flow
