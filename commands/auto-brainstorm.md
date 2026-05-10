---
description: auto-flow 진입 — Socratic clarifying Q + AI 자동 진행 + 4 단계 chain (brainstorm → design → write-plan → execute-plan) 끝까지. 사용자 입력은 clarifying Q 답변에만.
---

# /auto-brainstorm

피처명을 인수로 주거나 (`/auto-brainstorm 사용자 잔액 출금`) 인수 없이 호출하면 한 줄 안내 후 진행. 이 커맨드는 `auto-brainstorming` skill 을 invoke 합니다.

산출물:
- `docs/features/<오늘날짜>-<slug>/<slug>-requirements.md` (Socratic free-form, RAW)

다음 단계 (자동): `/auto-design` → `/auto-write-plan` → `/auto-execute-plan`

mid-flight 인터럽트: 각 skill 전환 시 1줄 notice — `stop` / `멈춰` / `잠깐` 등 입력 시 cleanly exit.
