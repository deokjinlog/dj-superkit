# G4: Failure Isolation

**Scenario:** Wave 1 의 task 1, 2, 3 동시 dispatch. Task 2 spec FAIL 강제 (테스트 fixture 가 reviewer ❌ 강제 응답).

**Expected:**
- Task 1 ✓ commit 됨
- Task 2 ✗ 격리 (working tree rollback + manifest 삭제)
- Task 3 ✓ commit 됨
- Task 2 의 후행 task 들 (있다면) blocked 마킹
