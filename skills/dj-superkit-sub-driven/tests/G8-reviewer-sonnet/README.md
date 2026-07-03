# G8: Spec-reviewer Always Sonnet

**Scenario:** plan task 1 에 `**Model**: haiku` 박힘 (implementer 는 haiku). 동시에 spec-reviewer dispatch 가 sonnet 인지 검증. G5 plan 재사용.

**Expected dispatch:**
- Implementer: `model: "haiku"` (Task 1 의 hint)
- Spec reviewer: `model: "sonnet"` (D11 고정, hint 무관)
