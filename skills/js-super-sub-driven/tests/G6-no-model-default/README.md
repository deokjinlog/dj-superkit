# G6: No Model Field — Sonnet Default

**Scenario:** plan task block 에 `**Model**:` 줄 없음 (v1.1.13 이전 plan 시뮬레이션). G2 plan 재사용.

**Expected:** 메인이 implementer dispatch 시 `model: "sonnet"` (디폴트) + 한 줄 dispatch log: "Task 1 model: sonnet (default)".
