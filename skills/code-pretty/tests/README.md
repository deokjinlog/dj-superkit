# code-pretty fixtures

각 fixture는 dogfood 검증 자료. 새 세션에서 `/code-pretty <fixture-path>`로 직접 호출은 안 되므로 (PRD 범위 밖), `writing-plans` 흐름 중에 자동 호출되는 결과를 비교하는 용도.

| Fixture | 기대 동작 | 검증 AC |
|---|---|---|
| F1 basic-pair | 원본 byte-equal, 수정 후 prettify | AC-2, AC-4 |
| F2 new-file | 원본 부재 OK, 수정 후 prettify | AC-2 |
| F3 forbidden-ops | 중첩 if / magic number 변환 안 됨 | AC-6 |
| F4 1pct-suspicion | 비슷한 helper 통합 안 됨 | AC-7 |
| F5 already-clean | byte-equal 보존 | (R7 검증) |

수동 dogfood 절차: `/write-plan` 흐름 중 fixture를 plan으로 취급해 code-pretty 호출되는지 확인 (또는 hook으로 우회 호출).
