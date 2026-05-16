# H10 — Auto-execute 도중 BLOCKED → failure isolation + 다음 wave 진행

## 시나리오

auto-executing-plans 진입 → wave 2 실행 중 1 task 가 spec-reviewer ❌ retry 후도 ❌ → 격리 → 다음 wave 진행 → finishing 에서 blocked 노출.

## 입력

```
/auto-execute-plan
```

(latest implementation-plan.md 자동 추론)

## 기대 동작

1. auto-executing-plans Entry Guard ✅ → js-super-sub-driven invoke
2. Wave 1 정상 진행
3. Wave 2 실행 중 task X spec-reviewer ❌:
   - implementer 재dispatch + reviewer ❌
   - working tree 변경 폐기 + manifest 삭제
   - task X 의 후행 (deps 포함) blocked 마킹
4. Wave 2 다른 task 들 정상 진행 + commit
5. Wave 3 → blocked task 들 dispatch 제외하고 진행
6. End-of-run consolidator 가 blocked task list 노출:
   ```
   ✅ <slug> 모든 task 완료. 구현 요약:
   ...
   - Blocked tasks: [task-X, task-Y, ...]
   ```
7. finishing-a-development-branch 호출 → 종료 메시지 + 사용자 catch

## 매핑

- AC: D6 (failure isolation + 다음 wave 진행), R2 (다수 fail 시 finishing 메시지 명확화), R9 (부분 commit 잔존 + 사용자 catch)
- FR: auto-flow 안전망
