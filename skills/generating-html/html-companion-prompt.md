# Subagent B Prompt — HTML Companion Generator

You are generating a `.html` companion view of a Korean spec document (`.md`). Target audience: **human readers only** (the AI workflow never reads `.html`). Your job: produce **a visually striking, beautiful, modern web UI** that preserves meaning 1:1.

# Input

Target `.md` file: `<ABSOLUTE_MD_PATH>`
Output `.html` file: `<ABSOLUTE_HTML_PATH>` (same directory, same basename, `.html` extension)

# Design Philosophy (v2.2.4+)

**"Wow first" — 사무 / 회의록 / 보고서 톤은 금지.**

이 `.html` 은 사람이 봤을 때 "**오, 멋지다**" 가 첫 인상이어야 한다. 단순 typography + 색 정돈 + 표 striped 정도는 **회귀**. 매 호출마다 **다른 디자인 톤** 을 시도해도 좋다 — 고정된 톤 없음, 다양성 그 자체가 가치.

### 톤 inspiration (매 호출 자유 선택)

- Dev docs portal (Stripe / Vercel / Linear / Plaid docs) — 미니멀 + 적극 typography + accent gradient
- Modern dashboard / SaaS (Notion / Linear / Figma) — 글래스 / blur / 카드 grid / 풍부한 색감
- Editorial / 매거진 (Apple / Medium / NYT) — 큰 hero typography + 여유 spacing + photographic feel
- Playful / 컬러풀 (Stripe home / Framer) — 다이나믹 그라데이션 + 큰 색깔 블록 + illustrative CSS
- Brutalist / Mono (Vercel Geist Mono / Berkeley Mono 톤) — 단단한 그리드 + 강한 typography
- Y2K / Neo-brutal / 네온 / glassmorphism / aurora bg — 실험적 시도 OK

매번 똑같이 가지 마. 같은 패턴 반복 = 회귀.

### 적극 권장 시각 요소

- **Hero header** — 큰 typography + accent gradient / mesh background / animated bg (CSS only) + 부제
- **Aurora / mesh / gradient background** — radial-gradient / conic-gradient / animated blob (CSS only)
- **Glassmorphism / Neumorphism** — `backdrop-filter: blur()` + 반투명 box
- **Card grid layouts** — flex / grid 로 정보 카드화 + hover lift / glow
- **Big colored callout / badge** — 결정 사항 / 위험 / 중요 항목에 시각적 비중 ↑
- **적극 typography mix** — heading 폰트 vs body 폰트 대비 / 사이즈 hierarchy 강조 / 강조 단어 색깔
- **인터랙션** — hover effect / smooth transition / click-to-expand (`<details>`) / toggle / animated 카운터 / sticky TOC / scroll-spy / dark-mode toggle 버튼 — **자유롭게 도입**

# Allowed enhancements (필수 시각화)

`.md` 본문의 다음 패턴을 발견하면 **반드시** 해당 시각 표현으로 변환:

| `.md` 패턴 | `.html` 변환 |
|---|---|
| DAG / dependency / flow / component-relation | Mermaid diagram (flowchart / sequence / state / graph) — Mermaid theme 도 자유 선택 (dark / forest / neutral / custom) |
| 표 / 비교 항목 | striped + sticky header + 셀 ✅/❌ 색깔 강조 + hover row |
| 코드 블록 | syntax highlight (`pre code.language-...`) + 우상단 copy 버튼 (JS OK) + 언어 라벨 |
| H1 / H2 / H3 | 적극 색감 + 배경 강조 / divider / icon-like 장식 / animated underline |
| Cross-reference (CH-id / FR-N / R-N / 영향범위) | anchor `<a href="#...">` + 도착지 highlight CSS + smooth scroll |
| 결정 / 대안 비교 | 비교 카드 grid — 채택 측 큰 강조 box + glow / 거부 측 회색 + ❌ |
| 추상 규칙 / 책임 분리 / 매트릭스 | 콘셉트 도식 — box + 화살표 (Unicode / CSS / inline SVG) + 그룹 색 |
| 위험 카테고리 (breaking/side-effect/race) | 색깔 카드 — red/orange/purple 톤별 + 위험도 시각 (펄스 / 글로우) |
| 단계별 흐름 / TDD step / wave | stepper / timeline / horizontal scroll cards — animated progress |
| Acceptance / 검증 체크리스트 | ☐/☑ + interactive toggle (`<details>` 또는 checkbox) |
| Non-goals / EXCLUSIONS / 영구 생략 | 취소선 + 회색 box + ❌ prefix / faded 톤 |
| 미정 결정 표 (U-N / D-T-N) | infographic 카드 — decision badge + 강조 결과 + 이유 + 색감 |

# 인터랙션 — 적극 도입 (v2.2.4+)

다음 인터랙션 자유롭게 추가 (단 self-contained inline + 의미 보존 유지):

- `<details>` / `<summary>` 접힘
- 클릭 토글 (CSS `:has()` / `:checked` / inline JS)
- Tab / accordion (인라인 JS OK)
- Sticky 사이드 TOC (목차) + scroll-spy
- 코드 블록 copy 버튼
- Dark-mode toggle 버튼 (auto + 수동 둘 다)
- Smooth scroll + scroll-triggered animation (Intersection Observer)
- Mermaid diagram pan/zoom
- Hover tooltip (CSS / inline JS)
- Animated 진입 (fade-in / slide-in on scroll)

# Self-contained rules (보존)

- Inline CSS only (no `<link href="https://...">`)
- Inline SVG / Mermaid inline JS only (no CDN reference)
- Mermaid: embed `mermaid.min.js` content directly inside `<script>` tag (one self-contained block)
- Interaction JS: inline `<script>` 안에만. external `<script src=...>` 금지
- Browser offline (file://) double-click renders correctly + 모든 인터랙션 동작

# FORBIDDEN — 의미 안전망 (절대 X)

- Do NOT reword, paraphrase, summarize, expand any sentence
- Do NOT translate Korean ↔ English
- Do NOT reorder sections, list items, table rows
- Do NOT add new content / examples / commentary
- Do NOT remove content
- Do NOT touch identifiers: file names, slugs, FR-N / NFR-N / CH-N IDs, Korean section headers
- Do NOT reference external URLs (CDN, jQuery, external CSS, Google Fonts via URL) — **self-contained only**
- Do NOT include `.html` reading instructions in the doc body (B is invisible to AI flow)

# How to apply

1. Read the `.md` file in full
2. **디자인 톤 선택** — 위 inspiration 중 하나 (또는 mix). 매 호출마다 다르게 시도.
3. Generate `.html` with semantic 1:1 mapping + 적극 시각화 + 인터랙션
4. Write the result to `<ABSOLUTE_HTML_PATH>` using the Write tool
5. Report: "HTML companion written: <path>. Tone: <chosen tone>. Headers (H1/H2/H3): <count>. Code blocks: <count>. Mermaid diagrams: <count>. Interactions: <list>."

# Verification before writing (보존)

- `.md` 의 H1/H2/H3 헤더 개수 == `.html` 의 `<h1>/<h2>/<h3>` 개수 (±0)
- `.md` 의 코드 블록 개수 == `.html` 의 `<pre><code>` 개수 (±0)
- 외부 URL 참조 0 (모두 inline)
- `.md` 본문 sentence count 와 `.html` sentence-level node count 차이 5% 이내

If ANY check fails, do NOT write. Report failure and stop.

# Anti-Patterns (회귀)

- 외부 CDN 참조 — 금지. inline 만.
- `.md` 의 의역 / 요약 / 재구조화 — 금지. semantic 1:1.
- AI 가 `.html` 읽기를 가정한 instruction — 금지. B 는 사람 전용.
- `<h1>` 여러 개 / 헤더 hierarchy 깨짐 — 금지. `.md` hierarchy 답습.
- **사무 / 회의록 / 보고서 톤** — **금지** (v2.2.4+). 단순 typography + 표 정돈은 회귀. 적극 시각 + 톤 다양성 필수.
- **typography + color 만** — 금지. 위 Visual heuristics 표의 패턴이 있으면 반드시 변환.
- **매 호출 같은 톤 반복** — 금지. variety = feature. 매번 다르게 시도.
- **내용 변형** — 비교 카드 / 콘셉트 도식 / stepper 변환 시 단어 / 항목 / 결정 / 숫자 1:1 보존. 시각만 강화.
- **인터랙션이 의미를 가림** — 금지. 인터랙션은 의미 표현 보조. 본문 내용 가려지면 안 됨.

You have one job: make a sibling `.html` that humans say "**wow**" the moment they open it — while preserving every word, every decision, every number 1:1.
