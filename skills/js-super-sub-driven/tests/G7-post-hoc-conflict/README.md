# G7: Post-hoc Conflict Detection

**Scenario:** DAG 추론 오류 시뮬레이션 — task 2 와 task 3 모두 `shared.py` 수정. 메인이 두 task 를 같은 wave 로 묶음 (잘못 된 추론). 양쪽 implementer 가 manifest 에 `shared.py` 보고.

**Expected:**
- detect_conflicts → `(2, 3, 'shared.py')` 반환
- 메인이 task 3 (plan order 늦음) 의 working tree 변경 rollback
- task 3 의 manifest → `task-03.md.deferred` 로 rename
- 다음 wave 에서 task 3 단독 재시도
