# H5 — docs-pretty pre-review timing 통일

## 시나리오

`/brainstorm` 새 피처 시작. 메인이 RAW PRD 작성 → docs-pretty 호출 (pre-review) → 사용자에게 prettified 본문 노출.

사용자가 fix 요청 → 메인이 in-memory raw 갱신 → docs-pretty 재발화 (per-draft loop) → 사용자가 prettified 재검토.

## 기대 동작

1. brainstorming Checklist Step 6 = docs-pretty (사용자 리뷰 전 발화)
2. brainstorming Checklist Step 7 = User reviews (prettified)
3. tech-design Checklist Step 6 = docs-pretty (combined approval gate 전 발화)
4. tech-design Checklist Step 7 = combined approval gate (prettified 본문 + verify report)
5. 사용자 fix 시 메인이 raw 갱신 → 다시 Step 6 호출 → 다시 Step 7 노출
6. change-history 첫 entry 가 logged 되면 docs-pretty STOPS firing (live doc 진입)

## 매핑

- AC-14 (사용자 첫 노출 본문이 prettified)
- FR-5 (docs-pretty pre-review timing 통일)
