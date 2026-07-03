---
description: upstream superpowers 원본 writing-plans 를 호출합니다. /og-brainstorm 으로 만든 design doc 을 기반으로 implementation plan 을 작성합니다.
---

# /og-write-plan

이 커맨드는 `og-writing-plans` skill을 invoke 합니다. **upstream superpowers 5.0.7 의 원본 writing-plans 동작** 을 그대로 재현합니다.

전제: `/og-brainstorm` 으로 작성된 design doc 이 `docs/superpowers/specs/` 아래에 존재.

## dj-superkit 정식 흐름과의 차이

| 항목 | `/write-plan` (dj-superkit 확장) | `/og-write-plan` (upstream 원본) |
|---|---|---|
| 입력 | `<slug>-requirements.md` + `<slug>-tech-design.md` (3-MD 분리) | upstream design doc 1개 |
| 산출물 경로 | `docs/features/<date>-<slug>/<slug>-implementation-plan.md` | `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md` |
| `commit_policy` frontmatter | 있음 (per-task / single / none) | 없음 |
| 위험 코드 지점 §2 섹션 | 있음 | 없음 |
| 변경이력 footer | 자동 누적 | 없음 |
| verifying-spec 게이트 | 자동 실행 | 없음 |
| docs-pretty 포맷 정돈 | 자동 1회 | 없음 |
| Execution Handoff | Inline / Subagent (dj-superkit-sub-driven) 양자택일 | Subagent-Driven (subagent-driven-development) / Inline (og-executing-plans) 양자택일 |

## 다음 단계

`/og-execute-plan` — Inline 실행. 또는 Subagent-Driven 선택 시 untouched-upstream `subagent-driven-development` 호출.

## 주의

`/og-*` 흐름과 dj-superkit 정식 흐름을 한 피처에서 섞지 마세요.
