---
description: upstream superpowers 원본 executing-plans 를 호출합니다. /og-write-plan 으로 만든 implementation plan 을 task-by-task 로 실행합니다.
---

# /og-execute-plan

이 커맨드는 `og-executing-plans` skill을 invoke 합니다. **upstream superpowers 5.0.7 의 원본 executing-plans 동작** 을 그대로 재현합니다.

전제: `/og-write-plan` 으로 작성된 plan 이 `docs/superpowers/plans/` 아래에 존재.

## js-super 정식 흐름과의 차이

| 항목 | `/execute-plan` (js-super 확장) | `/og-execute-plan` (upstream 원본) |
|---|---|---|
| 모드 분기 | Inline (executing-plans) / Subagent (js-super-sub-driven) 양자택일 | Inline 단일 (Subagent 원하면 `subagent-driven-development` 직접 호출) |
| 실행 모드 | git-fast / memory-fallback (commit_policy 기준) | upstream 단일 모드 — 그냥 plan 따라 실행 |
| 변경이력 [코드-수정] entry 자동 기록 | 있음 (task당 1번 batched) | 없음 |
| risk-annotation 3-checklist + RISK 주석 | 자동 | 없음 |
| 코드 주석 plan-측 식별자 금지 룰 | 적용 | 적용 안 됨 |

## Subagent 모드를 원할 때

`og-` 흐름 안에서 subagent 실행을 원한다면 `subagent-driven-development` 를 직접 호출하세요. js-super 가 손대지 않은 untouched-upstream 그대로라 별도의 og- 사본은 없습니다.

## 주의

`/og-*` 흐름과 js-super 정식 흐름을 한 피처에서 섞지 마세요.
