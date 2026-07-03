# H3 — Adaptive 7-topic: 비활성 토픽 N/A 박힘

## 시나리오

메타 워크플로우 변경 PRD 로 tech-design 진입. 비활성 토픽 (3 데이터 모델, 4 외부 인터페이스) 는 dialogue 스킵 + N/A 한 줄로 박힘.

## 입력

flow-slim-requirements.md (본 v1.1.15 PRD) — meta 워크플로우, DB/API 무관

## 기대 동작

1. tech-design Step 0 announce:
   ```
   ℹ️ 활성 토픽: 1,2,5,6,7 / 비활성: 3 데이터모델, 4 외부IF (이유: skill 본문 + helper script 변경, DB/API 무관). 추가 활성 필요시 알려주세요.
   ```
2. Step 3 dialogue 가 활성 토픽만 (1,2,5,6,7) 발화 — 3,4 스킵
3. flow-slim-tech-design.md 의 §3, §4 가 다음 형식으로 한 줄:
   ```markdown
   ## 3. 데이터 모델/스키마 변경 — N/A: 본 피처는 DB/스키마 무관 (skill 본문 + Python helper 변경)
   ## 4. 외부 인터페이스 — N/A: API/event 노출 없음 (skill 내부 + 로컬 Python helper)
   ```

## 매핑

- AC-1 (announce 한 줄 + N/A 박힘)
- AC-8 (메타 워크플로우 피처 dogfood)
- FR-1 (adaptive 7-topic)

## 참고

본 v1.1.15 의 flow-slim-tech-design.md 가 실제로 위 패턴을 따랐음 (CH-002). 자기 자신 dogfood 1차 통과.
