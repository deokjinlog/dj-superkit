# H17 — generating-html `.html` companion (메타 dogfood)

> v2.2.0 신규 → v2.2.1 갱신 (A 제거 + fire-and-forget). fixture 는 README 만 (Python 코드 없음). 검증은 다음 외부 피처 dogfood 시 발현.

## 시나리오 (정상 fire-and-forget 흐름)

1. **정상 1회 발동** — `generating-html` 가 `<slug>-requirements.md` 작성 직후 발동
2. **단일 fire-and-forget dispatch (v2.2.1+)** — 메인이 Task tool 1회 호출 (Sonnet `.html` 시각화 only, `run_in_background=true`). v2.2.0 의 A (`.md` format-only) 책임 제거.
3. **`.md` 는 RAW 그대로 + `.html` 사이드카 생성** — 같은 디렉토리, 같은 basename, 다른 확장자
4. **basename 매칭** — `foo-requirements.md` ↔ `foo-requirements.html` (1:1)
5. **메인 latency < 100ms** — fire-and-forget 검증 (Task dispatch 비용만, 결과 대기 X)
6. **offline 렌더 OK** — `.html` 더블클릭 (브라우저 file://) → 표 / Mermaid 다이어그램 / syntax highlight 모두 렌더링
7. **다크모드 자동 전환** — OS 설정 다크 시 다크 색상, 라이트 시 라이트 색상
8. **`.html` 푸터 stale 표시** — CH-id + 시각 (`이 파일은 ... [CH-... @ ...] 기준입니다`)
9. **live doc 진입 후 `.html` 재생성 X (자동)** — `change-history` 첫 entry append 후 부분 수정 시 `generating-html` 발동 X → `.html` 자동 갱신 X (boundary 보존). `change-propagation` 또는 `/sync-html` 수동 호출만 발동.

## 검증 체크리스트

- [ ] `.html` basename === `.md` basename
- [ ] `.html` 의 H1/H2/H3 헤더 개수 == `.md` 의 H1/H2/H3 헤더 개수 (±0)
- [ ] `.html` 의 `<pre><code>` 개수 == `.md` 의 코드 블록 개수 (±0)
- [ ] `.html` 외부 URL 참조 0 (`grep -E "https?://" *.html` → 0 결과, inline 만)
- [ ] `.html` 의 sentence-level node 수 vs `.md` 의 sentence (line) 수 차이 5% 이내
- [ ] `git status` 에 `.html` 미노출 (`.gitignore` 차단 동작)
- [ ] live doc 진입 후 추가 `generating-html` 발동 X 확인

## 실패 모드 검증 (v2.2.1+ — fire-and-forget)

| 시나리오 | 기대 동작 |
|---|---|
| B subagent 성공 | `.html` 사이드카 생성 + silent log (`.js-super/html-regen.log`) |
| B subagent 실패 | silent log 만, 사용자에게 push X. 사용자가 `.html` 부재 인지 시 `/sync-html` 수동 호출 |
| semantic drift (헤더 count mismatch) | B 가 자체 verification 후 write 안 함 (B prompt 룰). `.html` 미생성 → silent log |
| 메인이 결과 대기 (fire-and-forget 위반) | Anti-Pattern — 즉시 회귀 catch (디바운스 cancel 룰 + Task `run_in_background=true` 강제) |
| 자세한 race / 디바운스 / 실패 시나리오 | [H18-html-fire-and-forget](../H18-html-fire-and-forget/README.md) 참조 |

## Cross-machine 공유 가이드 (R7 mitigation)

`.html` 은 `.gitignore` 로 차단되어 git 으로 공유 불가. PR 리뷰용 공유는:

- **zip** — feature 디렉토리 통째 압축
- **drive** — Google Drive / Dropbox / 사내 파일 서버
- **수동 send** — Slack / 메신저 첨부

또는 사용자가 `.gitignore` exception 으로 cherry-pick 가능 (`!docs/features/<slug>/<file>.html` 추가).

## Anti-Patterns 회귀 catch

```bash
# 외부 CDN 참조 / .html 의존성
grep -nE "https?://.*\.(css|js)|read_file.*\.html|Read.*\.html" \
  skills/generating-html/SKILL.md skills/generating-html/html-companion-prompt.md
# expected: 0 (Anti-Patterns 표 안의 catch 라인만 허용)

# 다른 skill 본문에 .html 참조
grep -rn "\.html" \
  skills/{brainstorming,tech-design,writing-plans,executing-plans,auto-*,og-*}/SKILL.md
# expected: 0
```
