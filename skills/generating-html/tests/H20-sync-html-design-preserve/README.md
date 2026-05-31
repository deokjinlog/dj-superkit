# H20 — `/sync-html` 두번째 호출 시 디자인 보존 + 내용만 sync (메타 dogfood)

> v2.2.2 신규. fixture 는 README 만 (Python 코드 없음). 검증은 다음 외부 피처 dogfood 시 발현.

## 시나리오 (디자인 보존 + 내용 sync 흐름)

1. **첫 `/sync-html <slug>` 호출** — `.html` 없음 → subagent 가 디자인 + 내용 둘 다 새로 생성. CSS / Mermaid 색 / 레이아웃 / 여백 등 처음으로 결정.
2. **사용자 `.md` 부분 수정** — 텍스트 문장 일부 / 항목 추가 / 표 행 변경 등
3. **두번째 `/sync-html <slug>` 호출** — `.html` 존재 → subagent 가 분기 룰 진입
4. **분기 룰: 디자인 보존 + 내용만 sync** — 기존 `.html` 의 `<style>` 블록 / Mermaid 테마 / 레이아웃 (grid / flex / 여백 / 색 토큰) 보존. 텍스트 노드 (`<h*>`, `<p>`, `<li>`, `<td>` 등) 만 `.md` 최신본 기준 갱신.
5. **fire-and-forget < 100ms** — `run_in_background=true`, 메인 turn 대기 X
6. **자동 호출 경로 0 (v2.2.2+)** — `change-propagation` 마지막 단계에서 자동 호출 X. **안내문만** 출력 (`이 변경으로 .html 이 stale 됐을 수 있음. 필요시 /sync-html <slug>`). stale 허용 철학 보존.

## 검증 체크리스트

- [ ] 두번째 호출 후 `<style>` 블록 SHA256 변동 0 (디자인 보존)
- [ ] Mermaid 테마 토큰 (`mermaid.initialize({...theme...})`) 변동 0
- [ ] 레이아웃 컨테이너 (`.container`, `.layout`, grid-template-* 등) 변동 0
- [ ] 텍스트 노드만 갱신 (DOM diff — `.md` 변경분만 반영)
- [ ] 메인 turn elapsed < 100ms (fire-and-forget)
- [ ] `change-propagation` 흐름에서 `/sync-html` 자동 호출 X (안내문만 출력)
- [ ] `.html` 푸터 stale 표시 갱신 (`[CH-... @ ...]` 최신 CH-id)

## 디자인 보존 SHA 비교 룰

```bash
# 두번째 호출 전 .html 의 <style> SHA256
awk '/<style>/,/<\/style>/' <slug>-requirements.html | sha256sum > /tmp/style.before
# /sync-html 호출
# 두번째 호출 후 SHA256
awk '/<style>/,/<\/style>/' <slug>-requirements.html | sha256sum > /tmp/style.after
diff /tmp/style.before /tmp/style.after
# expected: empty (디자인 보존)

# Mermaid 테마 보존 비교 (initialize 블록)
grep -A5 "mermaid.initialize" <slug>-requirements.html | sha256sum
# 두번째 호출 전/후 일치
```

## 실패 모드 검증

| 시나리오 | 기대 동작 |
|---|---|
| subagent 가 디자인 재생성 시도 | prompt 룰 본문 명시 (`.html` 존재 분기 → 디자인 보존). 자체 verification 후 write 안 함 |
| 텍스트 노드 외 변경 시도 | DOM 노드 종류 외 변경 차단. silent log + write 안 함 |
| `.md` 변경분 누락 | subagent 자체 verification (헤더 count / sentence count) 후 write 안 함 |
| Sonnet API 일시 장애 | silent log 기록 + 기존 `.html` 무변경 (stale 채로 유지) |
| 사용자가 자동 호출 기대 (v2.2.1 시절 습관) | 발동 안 됨 — v2.2.2+ 안내문만 룰. `/sync-html <slug>` 명시 호출 안내. |

## Anti-Patterns 회귀 catch

```bash
# /sync-html 자동 호출 박힘 (v2.2.2+ 안내문만 룰 위반)
grep -nE "/sync-html" skills/change-propagation/SKILL.md
# expected: 안내문 표현만 (자동 호출 X). "필요시 /sync-html" 등 사용자 안내 문구만 허용.

grep -rn "/sync-html" \
  skills/{brainstorming,tech-design,writing-plans,executing-plans,auto-*,og-*}/SKILL.md
# expected: 0 (안내문 외 자동 호출 경로 없음)

# subagent prompt 에 디자인 보존 룰 누락
grep -nE "디자인 보존|design.*preserve|<style>.*보존" commands/sync-html.md
# expected: ≥ 1 (분기 룰 본문 명시)

# 메인이 결과 대기 (fire-and-forget 위반)
grep -nE "await.*Task|sync.*dispatch.*sync-html" commands/sync-html.md
# expected: 0
```
