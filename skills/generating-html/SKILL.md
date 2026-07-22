---
name: generating-html
description: Use during the initial-creation iteration loop of <slug>-requirements.md / <slug>-tech-design.md / <slug>-implementation-plan.md. Fires before user review on every draft (v1.1.15+ unified timing — pre-review per-draft). Re-fires on each user-fix iteration. STOPS firing once the first change-history entry is logged — that boundary marks "live doc". Dispatches a single Sonnet subagent (B) in fire-and-forget mode (v2.2.1+) — generates a sibling `.html` companion (사람 전용 시각화 사본) with semantic 1:1 preservation. Main does NOT wait for the result. RAW `.md` is shown to user as-is (v2.2.1 removed the v2.2.0 A format-only pass — B alone now handles human readability). NEVER invoked on change-history appends, change-propagation cascades (use `/sync-html` instead), or partial revisions.
---

# Generating HTML (Pre-Review Formatting)

This skill prettifies a freshly written or rewritten feature MD just before the user reviews it during the initial creation phase. It exists because the agent-authored draft is content-correct but visually noisy (inconsistent header levels, ad-hoc list bullets, unaligned tables, rough spacing). This pass tightens visual hierarchy WITHOUT touching meaning, so the user reviews a clean version. The user's review is the safety net: if the format pass ever drifts meaning, they catch it BEFORE it gets locked into change-history.

**Announce at start:** "I'm using the generating-html skill to format `<file>` before the user reviews it."

<HARD-GATE>
Trigger timing (v1.1.15+ 통일 — pre-review per-draft):

모든 doc 타입에서 동일하게 발화: 메인이 RAW 작성 → generating-html (사용자 리뷰 직전) → 사용자가 RAW `.md` 본문 검토 → 승인 → change-history. 사용자 fix 요청 시 메인이 in-memory raw 갱신 후 generating-html 재발화 (per-draft loop).

- **requirements.md** — brainstorming 흐름 끝, 사용자 리뷰 직전. user-fix 시 재발화.
- **tech-design.md** — tech-design 흐름 끝, 사용자 리뷰 직전 (combined approval gate 와 결합). user-fix 시 재발화.
- **implementation-plan.md** — writing-plans 흐름 끝, verifying-spec + code-pretty 통과 후, 사용자 리뷰 직전. user-fix 시 재발화 (기존 패턴 유지).

STOPS firing the moment the first `change-history` entry has been logged. That boundary marks the doc as "live" — from then on, no generating-html.

Specifically, generating-html MUST NOT run on:
- Any user-requested edit AFTER the first change-history entry exists (partial revisions, fixes, additions)
- Any `change-history` entry append (the `## 변경이력` footer is the audit trail — never reformat it)
- Any `change-propagation` cascade
- Any in-task code-edit logging during `/executing-plans`

If you are unsure whether this is still in the "initial creation phase" — STOP. Look for an existing `## 변경이력` footer with one or more entries. If ANY entry exists, this is NOT initial creation. Skip this skill.
</HARD-GATE>

## When to Use

| Trigger (yes) | Anti-trigger (no) |
|---|---|
| `brainstorming` just wrote RAW `<slug>-requirements.md`, about to show to user for review, no entries yet | User asked to update FR-3 wording in an already-live requirements.md (one with change-history entries) |
| `tech-design` just wrote RAW `<slug>-tech-design.md`, about to show combined approval gate (doc + verify report), no entries yet | `change-propagation` is cascading edits across MDs |
| `writing-plans` just completed verifying-spec + code-pretty on `<slug>-implementation-plan.md`, about to show RAW plan to user, no `## 변경이력` entries yet | `change-history` is appending a `[코드-수정]` entry mid-`/executing-plans` |
| `brainstorming` or `tech-design` user requested fix on draft — revise RAW, re-fire generating-html (per-draft loop) | First change-history entry has been logged — doc is now "live", do NOT fire |
| `writing-plans` user requested revision, plan re-written, verifying-spec re-ran, code-pretty re-ran — fire generating-html again | (none for pre-review timing — generating-html now fires before every user review) |

## Why fire-and-forget B (v2.2.1+)

HTML companion generation is a pure transformation task — no domain reasoning, no decisions. Loading the full doc into the main agent context is wasteful, and the main agent's reasoning model is overkill.

**Dispatch a single B subagent with `model: "sonnet"` and `run_in_background: true`.** Reasoning:

1. **AI 흐름은 `.md` 만 읽음** — A (v2.2.0 의 `.md` format-only pass) 의 가치는 사람 전용. B 의 `.html` 가 사람 가독성을 더 잘 흡수 (Mermaid / 시각화) → A 중복 제거 (v2.2.1).
2. **fire-and-forget** — 메인 latency 거의 0 (Task dispatch 비용만). 결과는 배경에서 사이드카로 떨어지고, `.intent-locked/html-regen.log` 에 silent log.
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
    - `"스킵 (이번만)"` → generating-html 단계 스킵, caller 에게 abnormal return (caller 가 change-history 직행 결정).
- **exit ≠ 0,1** (invocation 실패: 127 / 2 / etc., harness 환경 이슈) → stderr 전문 노출 + `AskUserQuestion` 게이트:
  - 메시지: `"preflight helper invocation 실패 (exit <code>): <stderr 전문>. 어떻게 할까요?"`
  - choices:
    - `"직접 디버깅"` → 사용자가 환경 점검 (venv / python 경로 / `scripts/preflight.py` 존재) 후 알려주면 메인이 재호출.
    - `"skill 단계 스킵"` → preflight 우회하고 Step 2 진입 (위와 동일).

자세한 룰은 `scripts/preflight.py:docs_pretty_check`. helper 검사: file 존재 / 변경이력 footer 비어있음 / filename 패턴.

### Step 2 — Dispatch single B subagent fire-and-forget (v2.2.1+)

Use ONE `Agent` tool call with `run_in_background: true`. Main agent does NOT wait.

**Subagent B — `.html` companion**:
- `subagent_type`: `general-purpose`
- `model`: `sonnet`
- `run_in_background`: `true`
- `description`: `HTML companion for <filename>.md`
- `prompt`: load `skills/generating-html/html-companion-prompt.md`, fill `<ABSOLUTE_MD_PATH>` + `<ABSOLUTE_HTML_PATH>` (same dir, same basename, `.html` extension) + CH-id + timestamp (for footer stale marker)

**Debounce (3초)**: If a previous B subagent is still running for the same `<slug>`, cancel it before dispatching the new one. Log cancel event to `.intent-locked/html-regen.log`.

**A (v2.2.0 `.md` format-only pass) is REMOVED in v2.2.1.** RAW `.md` is shown to user as-is.

### Step 3 — Yield immediately (v2.2.1+ fire-and-forget)

Main does NOT wait for B subagent completion. Step 2 dispatch 직후:

1. **메인 즉시 return** — caller (brainstorming / tech-design / writing-plans) 가 다음 turn 진행. RAW `.md` 가 사용자 리뷰 surface.
2. **B subagent 가 배경에서** `.html` 사이드카 작성. 자체 verification (B prompt 의 "Verification before writing" 룰) 이후 Write.
3. **silent log** — `.intent-locked/html-regen.log` 에 dispatch / 완료 / 실패 / cancel 모두 기록 (사용자 push X).
4. **사용자 push X** — B 결과는 silent. 사용자가 `.html` 부재 인지 시 `/sync-html` 수동 호출.

Failure handling (v2.2.1+ — fire-and-forget):
- **B 성공** → `.html` 사이드카 + silent log "OK"
- **B 실패** (Sonnet API 일시 장애 / verification 실패 등) → silent log "ERROR". `.html` 미생성. 사용자 다음에 `.html` 열려고 할 때 부재 인지 → `/sync-html` 수동.
- **메인 cancel (디바운스)** → 이전 B 작업 폐기, silent log "CANCEL". 새 B dispatch.

## Subagent Prompt (B)

**B 의 프롬프트는 별도 파일이 정본입니다** — `skills/generating-html/html-companion-prompt.md`. Step 2 의 dispatch 가 그 파일을 로드해 `<ABSOLUTE_MD_PATH>` · `<ABSOLUTE_HTML_PATH>` · CH-id · timestamp 를 채웁니다.

> **v2.2.0 의 A(`.md` format-only pass) 프롬프트가 이 자리에 남아 있어 삭제했습니다.** 그 프롬프트는 `.md` 를 Write 로 **덮어쓰는** 내용이라, *"A is REMOVED in v2.2.1"* · *"Revive A | NEVER"* 선언과 정면 충돌하고 실행되면 사용자 스펙을 훼손할 수 있었습니다.

## Process Flow

```dot
digraph generating_html {
    "Calling skill ready\n(brainstorming/tech-design/writing-plans)" [shape=box];
    "Pre-flight: file exists?\n변경이력 empty?\nfilename matches pattern?" [shape=diamond];
    "STOP — log reason, return to caller" [shape=box];
    "Dispatch B subagent\n(general-purpose, model=sonnet,\nrun_in_background: true)" [shape=box];
    "Main returns IMMEDIATELY\n(RAW .md is the review surface)" [shape=doublecircle];
    "silent log → .intent-locked/html-regen.log\n(dispatch / done / fail / cancel)" [shape=box];

    "Calling skill ready\n(brainstorming/tech-design/writing-plans)" -> "Pre-flight: file exists?\n변경이력 empty?\nfilename matches pattern?";
    "Pre-flight: file exists?\n변경이력 empty?\nfilename matches pattern?" -> "STOP — log reason, return to caller" [label="any check fails"];
    "Pre-flight: file exists?\n변경이력 empty?\nfilename matches pattern?" -> "Dispatch B subagent\n(general-purpose, model=sonnet,\nrun_in_background: true)" [label="all pass"];
    "Dispatch B subagent\n(general-purpose, model=sonnet,\nrun_in_background: true)" -> "silent log → .intent-locked/html-regen.log\n(dispatch / done / fail / cancel)";
    "Dispatch B subagent\n(general-purpose, model=sonnet,\nrun_in_background: true)" -> "Main returns IMMEDIATELY\n(RAW .md is the review surface)" [label="does NOT wait"];
}
```

## B 서브에이전트가 스스로 검사한다 (메인은 안 기다린다)

v2.2.1 이전엔 메인이 서브에이전트 완료를 기다렸다가 `.md` 를 되읽어 검사했습니다. **지금은 둘 다 불가능합니다** — 메인은 기다리지 않고(`Main does NOT wait`), B 는 `.html` 만 쓰므로 검사할 `.md` 변경분 자체가 없습니다.

검증 책임은 **B 프롬프트 안의 "Verification before writing" 룰**로 옮겨갔습니다. 실패는 `.intent-locked/html-regen.log` 에 남고, 사용자에게 push 하지 않습니다.

## Anti-Patterns

| Wrong | Right |
|---|---|
| Run generating-html as part of `change-history` entry append | NEVER. generating-html fires before the FIRST entry, and never again. |
| Run generating-html when user requested a partial revision | NEVER. Partial revisions go through normal Edit + change-history. |
| Skip the pre-flight `변경이력` empty check | The check is what enforces "first creation only". Don't skip. |
| Use Opus / Haiku / main agent for the formatting | Sonnet only — Opus wastes the call, Haiku risks rephrasing Korean. |
| Let the subagent "make the prose flow better" | Forbidden. Pass prompt forbids all rewording. |
| Reformat the `## 변경이력` footer "to match the new style" | The footer is an audit trail with byte-identical preservation. |
| Re-run generating-html if the user later complains the doc "still looks rough" | One shot only. Subsequent improvements are normal Edit + change-history entries. |
| Read or reference the `.html` companion from any AI workflow (v2.2.0+) | NEVER. AI reads `.md` only. `.html` is human-only derived view. |
| Reference external CDN / URL in the `.html` (v2.2.0+) | NEVER. Self-contained inline only (D4). |
| Commit `.html` companion to git (v2.2.0+) | `.gitignore` blocks it. `.html` is derived from `.md`, regenerated on each generating-html firing. |
| Main waits for B subagent result (v2.2.1+) | NEVER. fire-and-forget — `run_in_background=true` + 즉시 Step 3 return. |
| Revive A (`.md` format-only pass, v2.2.1+) | NEVER. v2.2.1 에서 A 책임 제거. RAW `.md` 가 사용자 리뷰 surface. |
| Skip debounce (cancel 룰 누락, v2.2.1+) | 연속 fix 시 매번 dispatch → 비용 누적. 3초 디바운스 + 이전 cancel 강제. |
| Run generating-html for live doc edits without `/sync-html` (v2.2.1+) | live doc 진입 후 `generating-html` 자동 X. `change-propagation` 마지막 단계 또는 사용자 수동 `/sync-html` 만. |

## Red Flags (STOP if you think these)

| Thought | Reality |
|---|---|
| "The doc is short, I'll just format it inline in the main agent" | Subagent dispatch is mandatory — clean main context + model isolation. |
| "The user can always re-run if I mess up" | The audit chain begins at the first 변경이력 entry. Recovering is messy. Don't risk meaning loss. |
| "I'll let the subagent fix that one awkward sentence too" | Forbidden by the prompt. Awkward sentences are addressed via change-propagation if the user actually asks. |
| "Two passes will polish it more" | One shot only. Two passes = compound rephrasing risk. |

## Acceptance

A generating-html run is correct when ALL hold:

1. Pre-flight checks all passed (file exists, `## 변경이력` empty, filename pattern matches)
2. B subagent was dispatched with `model: sonnet`, `run_in_background: true`, and the strict format-only prompt
3. A DISPATCH entry was written to `.intent-locked/html-regen.log` (메인이 결과를 기다렸다는 증거가 아니라, **던졌다는** 증거다)
4. The calling skill received control back and is about to invoke `change-history` for the first entry
5. No `## 변경이력` entry was added by generating-html itself (logging is the caller's job, with `[<doc-type>-수정]` tag for "신규 ... 결과")

## Related Skills

- `brainstorming` — calls this on first save of `<slug>-requirements.md`
- `tech-design` — calls this on first save of `<slug>-tech-design.md`
- `writing-plans` — calls this on first save of `<slug>-implementation-plan.md`
- `change-history` — invoked by the caller AFTER generating-html returns; logs the first entry on the now-RAW doc
- `change-propagation` — for any post-init revision; generating-html is NEVER part of that flow

## 비동기 신뢰성 룰 (v2.4+) — silent log monitor (v2.4+)

`generating-html` 백그라운드 호출이 처음 `.md` 생성 시 가끔 실패하던 회귀를 해결한 4 룰. 호출자 측 (auto-* / `/sync-html` / `/audit-risk` 등) 이 같이 답습.

### B-1 — dispatch 결과 verify

호출 직후 메인이 dispatch id 를 받았는지 확인 (Agent tool return). 시간 경과 후 (사용자가 transition notice 받기 전) `.html` 파일 존재 확인. id 부재 시 메인이 직접 호출 (sync fallback).

### B-3 — silent log monitor

호출 시 `.intent-locked/html-regen.log` 에 entry 자동 append:

```
YYYY-MM-DD HH:MM:SS | DISPATCH | <slug>-<type>.md | agent_id=<id>
YYYY-MM-DD HH:MM:SS | SUCCESS  | <slug>-<type>.html | <bytes> bytes
YYYY-MM-DD HH:MM:SS | FAIL     | <slug>-<type>.md | <reason>
```

`/sync-html --check` 옵션으로 마지막 N entry (default 10) 조회. rotation 정책은 후속 후보 (현재는 append-only).

### B-4 — 메인 응답에 dispatch 결과 명시

호출자 측 (auto-brainstorming / auto-tech-design / auto-writing-plans / `/sync-html` / `/audit-risk`) 의 transition notice 시점에 결과를 함께 알림:

- 완료 시: "백그라운드 호출 완료 (N KB)"
- 실패 시: "실패 — `/sync-html` 으로 사용자가 직접 재시도 필요"

자동 retry 는 도입하지 않음 (사용자 의도 외 비용 누적 위험). 사용자 명시 호출만 trigger. 자동 retry 는 v2.4.x 후속 후보.

### B-2 race delay 는 호출자 측에

dispatch 와 change-history footer 추가 사이 race condition 해결을 위한 5초 delay 는 `generating-html` 자체에 박지 않고, 호출자 측 (auto-* 3 skill 의 Step 4.5/4.6) 에 박힘. 본 skill 은 호출 받으면 즉시 작업 시작 (delay 무관).
