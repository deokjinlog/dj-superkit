# H17 — docs-pretty `.html` companion (메타 dogfood)

> v2.2.0 신규. fixture 는 README 만 (Python 코드 없음). 검증은 다음 외부 피처 dogfood 시 발현.

## 시나리오

1. **정상 1회 발동** — `docs-pretty` 가 `<slug>-requirements.md` 작성 직후 발동
2. **두 subagent 병렬 dispatch** — 메인이 한 메시지 안에서 Task tool 2회 호출 (A: Sonnet `.md` format-only / B: Sonnet `.html` 시각화)
3. **`.md` + `.html` 둘 다 생성** — 같은 디렉토리, 같은 basename, 다른 확장자
4. **basename 매칭** — `foo-requirements.md` ↔ `foo-requirements.html` (1:1)
5. **offline 렌더 OK** — `.html` 더블클릭 (브라우저 file://) → 표 / Mermaid 다이어그램 / syntax highlight 모두 렌더링
6. **다크모드 자동 전환** — OS 설정 다크 시 다크 색상, 라이트 시 라이트 색상
7. **live doc 진입 후 `.html` 재생성 X** — `change-history` 첫 entry append 후 부분 수정 시 `docs-pretty` 발동 X → `.html` 갱신 X (boundary 보존)

## 검증 체크리스트

- [ ] `.html` basename === `.md` basename
- [ ] `.html` 의 H1/H2/H3 헤더 개수 == `.md` 의 H1/H2/H3 헤더 개수 (±0)
- [ ] `.html` 의 `<pre><code>` 개수 == `.md` 의 코드 블록 개수 (±0)
- [ ] `.html` 외부 URL 참조 0 (`grep -E "https?://" *.html` → 0 결과, inline 만)
- [ ] `.html` 의 sentence-level node 수 vs `.md` 의 sentence (line) 수 차이 5% 이내
- [ ] `git status` 에 `.html` 미노출 (`.gitignore` 차단 동작)
- [ ] live doc 진입 후 추가 `docs-pretty` 발동 X 확인

## 실패 모드 검증

| 시나리오 | 기대 동작 |
|---|---|
| A 성공 / B 실패 | `.md` 만 갱신 + 사용자에게 "`.html` 생성 실패, 수동 retry 가능" 알림 |
| A 실패 / B 성공 | 둘 다 폐기 (A 가 핵심) |
| A·B 둘 다 실패 | `docs-pretty` 자체 abort, RAW `.md` 유지 |
| semantic drift (헤더 count mismatch) | B 결과 폐기 → `.md` 만 갱신 |

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
  skills/docs-pretty/SKILL.md skills/docs-pretty/html-companion-prompt.md
# expected: 0 (Anti-Patterns 표 안의 catch 라인만 허용)

# 다른 skill 본문에 .html 참조
grep -rn "\.html" \
  skills/{brainstorming,designing-direction,writing-plans,executing-plans,auto-*,og-*}/SKILL.md
# expected: 0
```
