---
description: <slug>-implementation-plan.md를 task-by-task로 실행합니다. 매 코드 변경마다 위험 주석 자동 부착 + 변경 전·후 코드를 변경이력에 보존합니다.
---

# /execute-plan

이 커맨드는 plan task 수를 세서 실행 모드를 양자택일로 묻고 해당 skill을 invoke 합니다.

전제:
- 동일 피처 폴더에 `<slug>-implementation-plan.md` 존재
- plan frontmatter에 `commit_policy` 필드 (없으면 `per-task`로 간주)

## 실행 모드 양자택일

| Option | skill | Recommended for |
|---|---|---|
| **1) Inline** | `executing-plans` | Medium plans (≤ 12 tasks) |
| **2) Subagent** | `js-super-sub-driven` | Large plans (13+ tasks) |

다음 메시지로 사용자에게 묻습니다:

> "Plan has <N> tasks. Two execution options:
>
> 1. **Inline** (recommended for medium plans, ≤ 12 tasks) — main agent edits directly via `executing-plans`; fast, fewer total tokens; main context accumulates with task count
> 2. **Subagent** (recommended for large plans, 13+ tasks) — implementer + spec reviewer subagents via `js-super-sub-driven`; preserves main context; adds dispatch cost
>
> Which approach?"

upstream 원본 `subagent-driven-development`는 이 양자택일에서 제시하지 않습니다. 사용자가 명시적으로 "원본 upstream으로" 요청한 경우에만 invoke.

## 자동 동작 (Inline / Subagent 공통)

- risk-annotation 3-체크리스트 → 필요 시 `# ⚠️ RISK(...)` 주석 자동 부착
- 매 task 완료 후 <slug>-implementation-plan.md 변경이력에 [코드-수정] entry 추가
- atomic commit (commit_policy = per-task 인 경우)

차이점:
- **Inline**: 메인이 직접 편집. git-fast / memory-fallback 모드 자동 선택.
- **Subagent (js-super)**: implementer + spec reviewer 서브에이전트 → 메인이 후처리(RISK / 변경이력 / atomic commit). 호출: `js-super-sub-driven`

다음 단계 (선택): `/api-test`
