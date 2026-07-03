# G2: Simple Wave (3 tasks, file-disjoint, all sonnet)

**Scenario:** task 1, 2, 3 이 모두 다른 파일을 건드리고 deps 없음 → 1 wave 동시 dispatch.

**Expected wave 분할:** Wave 1: [1, 2, 3]
**Expected commits:** 3 commits in plan order (task 1 → task 2 → task 3) by main at wave finalization.
**Expected dispatch model:** 모두 sonnet (Model 필드 없음 → 디폴트)
