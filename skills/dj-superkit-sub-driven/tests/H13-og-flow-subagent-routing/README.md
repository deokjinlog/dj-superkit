# H13 — og-flow Subagent path 매칭 검증

**v2.0.2+ — A (rename) + B (handoff 강화) dogfood**

## 시나리오 (positive — 매칭이 upstream 원본)

가상 외부 피처 dogfood:

1. 사용자: `/og-brainstorm 새-피처-이름`
2. og-brainstorming → og-tech-design → `/og-write-plan`
3. plan 작성 끝 Execution Handoff 게이트 → 사용자: "1" 또는 "Subagent-Driven"
4. 메인 에이전트가 매칭하는 skill ID 검증

## 기대 결과 (rename 후)

- 매칭된 skill ID: **`superpowers:subagent-driven-development`** (upstream-untouched)
- NOT `dj-superkit:dj-superkit-sub-driven` (dj-superkit 확장)
- og-writing-plans Anti-Pattern 표 + bold prefix 가 LLM 매칭 catch

## 검증 (수동 dogfood)

`/og-write-plan` 끝 게이트에서 메인이 다음 중 어느 skill 을 invoke 하는지 확인:

- ✅ `superpowers:subagent-driven-development` — 정상
- ❌ `dj-superkit:dj-superkit-sub-driven` — 회귀 (A rename 했는데도 매칭 충돌 잔존 → B handoff 강화 추가 필요 catch)

## 시나리오 (negative — dj-superkit 정식 흐름)

대조군 — `/brainstorm` (dj-superkit 정식) → `/write-plan` → Subagent 선택 시:

- 매칭된 skill ID: **`dj-superkit:dj-superkit-sub-driven`** (정상)
- NOT `superpowers:subagent-driven-development`

## 연결 위험

- R8 (og 흐름 dogfood 미검증) — 본 fixture 가 catch
- R1 (rename breaking — cross-ref 누락) — 매칭 실패 시 누락 file 추적 시작
