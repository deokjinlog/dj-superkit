# G1: Entry Guard

**Scenario:** plan 없는 폴더에서 skill 진입 → 즉시 ABORT

**Setup:** `docs/features/2026-01-01-empty-fixture/` 폴더만 존재 (plan 파일 없음).

**Expected:** 메인이 entry guard 검사 → `subagent_task_entry_check` exit 1 → 한 줄 안내 출력 + 종료
