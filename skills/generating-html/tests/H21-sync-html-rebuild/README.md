# H21 — `/sync-html --rebuild` 디자인 변경 + 영구 손실 (메타 dogfood)

> v2.2.2 신규. fixture 는 README 만 (Python 코드 없음). 검증은 다음 외부 피처 dogfood 시 발현. R7 mitigation 직접 묶음.

## 시나리오 (의도된 디자인 실험 흐름)

1. **사용자 `/sync-html <slug> --rebuild` 명시 호출** — `.html` 존재 여부 무관, `--rebuild` 플래그 명시
2. **분기 룰 우회** — H20 의 "디자인 보존" 분기 우회. subagent 가 디자인 + 내용 처음부터 새로 생성.
3. **사용자 의도된 디자인 실험** — 기존 CSS / 레이아웃 / Mermaid 테마 마음에 안 듦 → 처음부터 재생성 시도
4. **fire-and-forget < 100ms** — `run_in_background=true`, 메인 turn 대기 X
5. **결과** — `.html` 완전 교체. 기존 디자인 영구 손실.

## R7 — 의도 외 호출 시 영구 손실 (mitigation)

`--rebuild` 는 사용자 의도된 디자인 변경을 위한 명시 플래그. **의도 외 사용 시 회복 경로 0**:

- `.html` 은 `.gitignore` 차단 → `git checkout` / `git revert` 불가
- 백업본 자동 보관 없음 (디스크 용량 부담 + 사용자 stale 인지 흐름 무화)
- 다음 호출 plain `/sync-html` 으로 자연 회복 X — plain 모드는 "디자인 보존 + 내용 sync" (H20). 이미 변경된 새 디자인을 보존하므로 옛 디자인 복귀 X
- 유일한 회복: 사용자가 옛 디자인을 기억해서 처음부터 재구성 (수동)

## 사용자 인지 의무

`/sync-html --rebuild` 슬래시 본문에 **명시 경고문** 박힘 — 호출 전 사용자에게 다음 보장 요구:

- 기존 `.html` 디자인 영구 손실 인지
- 회복 경로 0 인지
- 의도된 디자인 실험인지 (의도 외 호출 차단)

호출 시 1초 안내문 노출 후 진행. AskUserQuestion 게이트 X (의도된 명시 호출이므로 추가 마찰 없음 — H20 / H19 와 일관).

## 검증 체크리스트

- [ ] `--rebuild` 플래그 명시 호출 시에만 디자인 변경 (`plain /sync-html` 호출 시 디자인 보존 → H20 와 일관)
- [ ] `/sync-html` 슬래시 본문에 R7 경고문 grep ≥ 1 (`grep -E "영구 손실|gitignored|회복.*불가|회복.*X" commands/sync-html.md`)
- [ ] 자동 호출 경로 0 (`change-propagation` / 다른 skill 본문 어디에도 `--rebuild` 자동 호출 X)
- [ ] 호출 후 `<style>` 블록 SHA256 변경 확인 (디자인 실제 교체 동작 보장)
- [ ] 메인 turn elapsed < 100ms (fire-and-forget)
- [ ] plain `/sync-html` 후속 호출 시 새 디자인 보존 (옛 디자인 자연 회복 X 확인)

## 디자인 변경 검증 룰

```bash
# --rebuild 전 .html 의 <style> SHA256
awk '/<style>/,/<\/style>/' <slug>-requirements.html | sha256sum > /tmp/style.before
# /sync-html --rebuild 호출
# 후 SHA256
awk '/<style>/,/<\/style>/' <slug>-requirements.html | sha256sum > /tmp/style.after
diff /tmp/style.before /tmp/style.after
# expected: 차이 (디자인 실제 교체 동작)

# 이후 plain /sync-html 호출 → 디자인 보존 (옛 디자인 자연 회복 X)
awk '/<style>/,/<\/style>/' <slug>-requirements.html | sha256sum
# expected: --rebuild 후 SHA 와 동일 (옛 SHA 와 다름 — 회복 X 보장)
```

## 실패 모드 검증

| 시나리오 | 기대 동작 |
|---|---|
| 사용자가 의도 외 `--rebuild` 호출 | 경고문 노출 + 진행 (1초 후) → 디자인 영구 손실 → 사용자 인지 후 수동 회복 |
| `--rebuild` 후 plain `/sync-html` 자연 회복 기대 | 회복 X — plain 모드는 새 디자인 보존. 사용자가 처음부터 재구성 필요 |
| 자동 호출 경로 (change-propagation 등) | 차단 — `--rebuild` 자동 호출 경로 0 (의도된 사용자 명시만) |
| Sonnet API 일시 장애 | silent log 기록 + 기존 `.html` 무변경 (회복 가능 — 정상 종료 시점) |

## Anti-Patterns 회귀 catch

```bash
# --rebuild 자동 호출 박힘 (사용자 의도 우회)
grep -rn -- "--rebuild" \
  skills/{brainstorming,tech-design,writing-plans,executing-plans,change-propagation,auto-*,og-*}/SKILL.md
# expected: 0 (사용자 명시 호출만)

# 자동 백업 / 자동 회복 도입 시도
grep -nE "backup.*\.html|restore.*\.html|\.html\.bak|\.html\.backup" commands/sync-html.md
# expected: 0 (디스크 부담 + stale 인지 흐름 무화 차단)

# 슬래시 본문에 R7 경고문 누락
grep -cE "영구 손실|gitignored|회복.*불가|회복.*X" commands/sync-html.md
# expected: ≥ 1

# 메인이 결과 대기 (fire-and-forget 위반)
grep -nE "await.*Task|sync.*dispatch.*--rebuild" commands/sync-html.md
# expected: 0
```
