# H18 — docs-pretty fire-and-forget race / 디바운스 / 실패 시나리오 (메타 dogfood)

> v2.2.1 신규. H17 (정상 fire-and-forget 흐름) 의 예외 시나리오 분리. fixture 는 README 만 (Python 코드 없음). 검증은 다음 외부 피처 dogfood 시 발현.

## 시나리오 1 — race (subagent 미완료 시 사용자 접근)

1. `.md` 작성 → `docs-pretty` 발동 → B subagent dispatch (`run_in_background=true`)
2. 메인 turn 즉시 return (latency < 100ms)
3. **사용자가 즉시 `.html` 열려고 시도** → 부재 또는 빈 파일
4. 기대 동작: 사용자가 인지 → `/regen-html <slug>` 수동 호출 → 재생성

## 시나리오 2 — 디바운스 (연속 fix 시 cancel)

1. `.md` 작성 → B subagent #1 dispatch
2. **3초 이내 사용자가 fix #1 입력** → `.md` 갱신 + B subagent #2 dispatch
3. 메인이 #1 cancel + #2 dispatch (디바운스 룰)
4. **3초 이내 사용자가 fix #2 입력** → `.md` 갱신 + B subagent #3 dispatch
5. 메인이 #2 cancel + #3 dispatch
6. 사용자 fix 멈춤 → 3초 후 #3 완료 → `.html` 사이드카
7. `.js-super/html-regen.log` 에 cancel 2건 + 완료 1건 기록

## 시나리오 3 — 실패 silent log

1. `.md` 작성 → B subagent dispatch
2. **B 실패** (예: Sonnet API 일시 장애, semantic drift verification 실패 등)
3. 메인은 결과 대기 X (fire-and-forget) → 사용자에게 푸시 X
4. `.js-super/html-regen.log` 에 실패 기록
5. 사용자가 `.html` 부재 인지 시 → `/regen-html` 수동 호출

## 시나리오 4 — `change-propagation` 자동 호출

1. live doc 상태 (`change-history` 첫 entry 이후)
2. 사용자가 의미 변경 요청 (`"FR-3 라벨을 X 로 바꿔"` 등)
3. `change-propagation` 발동 → 영향 매트릭스 → 사용자 승인 → cascading 변경
4. **마지막 단계에 `/regen-html <slug>` 자동 호출** (v2.2.1+ Acceptance 5번)
5. `.html` 자동 재생성 (fire-and-forget, 메인 대기 X)

## 시나리오 5 — `.md` 직접 편집 후 사용자 수동 `/regen-html`

1. live doc 상태
2. 사용자가 오타 한두 글자 등 `.md` 직접 편집
3. `docs-pretty` 발동 X (boundary 보존) + `change-propagation` 호출 안 됨 → `.html` stale
4. 사용자가 `.html` 푸터의 stale 표시 인지 → `/regen-html <slug>` 명시 호출
5. `.html` 재생성

## 검증 체크리스트

- [ ] 시나리오 1: `.html` 부재 시 사용자 인지 가능 (푸터 stale 표시 또는 brower 404)
- [ ] 시나리오 2: 디바운스 3초 동작 (`grep "cancel" .js-super/html-regen.log` ≥ 1)
- [ ] 시나리오 3: 실패 시 silent log 기록 (`grep "ERROR" .js-super/html-regen.log` ≥ 1)
- [ ] 시나리오 4: `change-propagation` 마지막 단계에서 `/regen-html` 자동 발화 확인
- [ ] 시나리오 5: 사용자 수동 `/regen-html` 명시 호출 시 `.html` 갱신 + 푸터 새 CH-id

## 메인 latency 측정 룰

```bash
# 메인이 docs-pretty 발동 전후 turn elapsed 차이
# 기대: < 100ms (fire-and-forget — Task dispatch 비용만)
```

향후 자동 측정 hook 추가 검토 (v2.2.x patch 후보).

## Anti-Patterns 회귀 catch

```bash
# 메인이 fire-and-forget subagent 결과 대기 (fire-and-forget 위반)
grep -nE "await.*Task|sync.*dispatch.*\.html" skills/docs-pretty/SKILL.md
# expected: 0

# A (.md format-only) 부활 시도
grep -nE "format-only pass on .*\.md|Subagent A" skills/docs-pretty/SKILL.md
# expected: 0

# change-propagation 자동 호출 누락
grep -c "/regen-html" skills/change-propagation/SKILL.md
# expected: ≥ 1
```
