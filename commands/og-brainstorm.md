---
description: upstream superpowers 원본 brainstorming(자유 탐색 Socratic 방식)을 호출합니다. js-super 확장(PRD/변경이력/위험주석/docs-pretty)을 우회하고 원본 그대로의 경험을 원할 때 사용.
---

# /og-brainstorm

이 커맨드는 `og-brainstorming` skill을 invoke 합니다. **upstream superpowers 5.0.7 의 원본 brainstorming 동작** 을 그대로 재현합니다.

피처명을 인수로 주거나 (`/og-brainstorm 잔액 출금`) 인수 없이 호출하면 자유 탐색 대화로 시작합니다.

## js-super 정식 흐름과의 차이

| 항목 | `/brainstorm` (js-super 확장) | `/og-brainstorm` (upstream 원본) |
|---|---|---|
| 산출물 경로 | `docs/features/<date>-<slug>/<slug>-requirements.md` | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` |
| 산출물 형식 | PRD 6-섹션 또는 Socratic 자유 형식 (모드 선택) | upstream 자유 형식 단일 |
| 변경이력 footer | 자동 누적 | 없음 |
| docs-pretty 포맷 정돈 | 자동 1회 | 없음 |
| 적응형 질문 (카테고리별 스킵) | 있음 | 없음 — 자유 대화 |
| 다음 단계 | `/tech-design` (tech-design) | `/og-write-plan` (og-writing-plans) |

## 다음 단계

`/og-write-plan` — 산출된 design doc 을 기반으로 upstream 원본 implementation plan 작성.

## 주의

`/og-*` 흐름과 `/brainstorm`, `/tech-design`, `/write-plan`, `/execute-plan` 흐름을 **하나의 피처 안에서 섞지 마세요**. 한 피처는 한 흐름으로 일관되게.
