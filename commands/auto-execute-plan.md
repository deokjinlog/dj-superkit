---
description: auto-flow 4단계 진입 (마지막) — implementation-plan.md 있는 상태에서 wave-parallel subagent 강제 (Gate #14 override) + failure isolation + finishing 자동.
---

# /auto-execute-plan

`<slug>` 인자 optional. 인자 누락 시 latest implementation-plan.md 자동. 이 커맨드는 `auto-executing-plans` skill 을 invoke 합니다.

동작: 무조건 wave-parallel `js-super-subagent-driven-development` 호출 (Gate #14 자동승인 명시 override). failure isolation + end-of-run consolidator + finishing 자동.

종료 메시지: commit 수 + RISK 카운트 + blocked tasks list.
