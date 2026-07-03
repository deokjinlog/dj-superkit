# H19 — `/pretty-md` 호출 시 `.md` format-only + footer byte-equal (메타 dogfood)

> v2.2.2 신규. fixture 는 README 만 (Python 코드 없음). 검증은 다음 외부 피처 dogfood 시 발현.

## 시나리오 (정상 흐름 — opt-in `/pretty-md` 호출)

1. **사용자 명시 호출** — `/pretty-md <slug>` (인자 optional + latest slug 추론)
2. **자동 발동 경로 없음** — `docs-pretty` (v2.2.0~v2.2.1) 와 달리 v2.2.2+ 는 RAW `.md` 가 기본. 사용자가 정형이 필요하다고 판단한 시점에만 명시 호출.
3. **메인이 Sonnet subagent fire-and-forget dispatch** — `run_in_background=true`. feature 디렉토리의 모든 `<slug>-*.md` 대상 format-only pass.
4. **메인 turn elapsed < 100ms** — 결과 대기 X
5. **subagent 동작 룰**:
   - 헤더 위계 / 표 정렬 / 코드 펜스 / 리스트 들여쓰기 등 표면 포맷만 정리
   - 본문 의역 / 재구조화 / 요약 / 누락 모두 금지
   - `## 변경이력` footer **byte-equal** 보존 (audit chain 손상 차단)
6. **사용자 검토** — `git diff <slug>-*.md` 로 정형 결과 확인. 의역 의심 시 revert.
7. **footer 보존 검증** — 정형 전/후 footer 영역 SHA256 일치

## 검증 체크리스트

- [ ] `/pretty-md` 명시 호출 시에만 발동 (다른 skill 자동 발동 경로 0)
- [ ] 메인 turn elapsed < 100ms (`run_in_background=true` 확인)
- [ ] 정형 전/후 `## 변경이력` footer SHA256 일치 (`sha256sum` 비교)
- [ ] 의미 보존 검증 — sentence 수 / 헤더 수 / 코드 블록 수 정형 전/후 동일
- [ ] `git diff` 출력에 의역 / 본문 재구조화 / 요약 없음 (표면 포맷만)
- [ ] subagent 실패 시 silent log 만 (`.dj-superkit/html-regen.log` 또는 동등 채널) — 사용자에게 push X

## footer byte-equal 검증 룰

```bash
# 정형 전 footer SHA256
awk '/^## 변경이력$/,/^$/' <slug>-requirements.md | sha256sum
# /pretty-md 호출
# 정형 후 footer SHA256
awk '/^## 변경이력$/,/^$/' <slug>-requirements.md | sha256sum
# 두 값 일치 보장 → audit chain 무손상
```

## 실패 모드 검증

| 시나리오 | 기대 동작 |
|---|---|
| subagent 의역 시도 | 자체 verification (sentence count / 헤더 count) 후 write 안 함 → silent log |
| footer byte mismatch | subagent 자체 차단 → write 안 함 → silent log + 원본 보존 |
| Sonnet API 일시 장애 | silent log 기록 + 원본 `.md` 무변경 |
| 사용자가 자동 발동 기대 (`docs-pretty` 시절 습관) | 발동 안 됨 — v2.2.2+ opt-in 룰 명시. `/pretty-md` 호출 안내. |

## Anti-Patterns 회귀 catch

```bash
# /pretty-md 가 자동 발동 경로로 박혀 있는지 (의도 외)
grep -rn "/pretty-md" \
  skills/{brainstorming,tech-design,writing-plans,executing-plans,auto-*,og-*}/SKILL.md
# expected: 0 (자동 발동 경로 없음 — opt-in 호출만)

# subagent prompt 에 footer byte-equal 룰 누락
grep -nE "byte-equal|byte equal|sha256.*footer|footer.*sha256" \
  commands/pretty-md.md
# expected: ≥ 1 (R6 mitigation 본문 명시)

# 메인이 결과 대기 (fire-and-forget 위반)
grep -nE "await.*Task|sync.*dispatch.*pretty-md" commands/pretty-md.md
# expected: 0
```
