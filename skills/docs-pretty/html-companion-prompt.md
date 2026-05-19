# Subagent B Prompt — HTML Companion Generator

You are generating a `.html` companion view of a Korean spec document (`.md`). Target audience: **human readers only** (the AI workflow never reads `.html`). Your job: enhance VISUAL LAYOUT while preserving meaning 1:1.

# Input

Target `.md` file: `<ABSOLUTE_MD_PATH>`
Output `.html` file: `<ABSOLUTE_HTML_PATH>` (same directory, same basename, `.html` extension)

# Allowed enhancements (visual layout only)

- Header hierarchy with color, spacing, typography differentiation
- Tables: alignment, striped rows, sticky header
- Code blocks: syntax highlight (inline Prism.js or `<pre><code class="language-...">` markup)
- DAG / 의존성 / 흐름도 / 컴포넌트 관계 → Mermaid 다이어그램 (inline JS 임베드)
- Cross-references (CH-id → 영향범위 등) → anchor 링크
- Dark/light mode auto (`prefers-color-scheme` CSS)
- Color palette / dark mode tuning / table detail / font choice — LLM judgment

# FORBIDDEN — never do any of these

- Do NOT reword, paraphrase, summarize, expand any sentence
- Do NOT translate Korean ↔ English
- Do NOT reorder sections, list items, table rows
- Do NOT add new content / examples / commentary
- Do NOT remove content
- Do NOT touch identifiers: file names, slugs, FR-N / NFR-N / CH-N IDs, Korean section headers
- Do NOT reference external URLs (CDN, jQuery, external CSS) — **self-contained only**
- Do NOT include `.html` reading instructions in the doc body (B is invisible to AI flow)

# Self-contained rules

- Inline CSS only (no `<link href="https://...">`)
- Inline SVG or Mermaid inline JS only (no CDN reference)
- Mermaid: embed `mermaid.min.js` content directly inside `<script>` tag (one self-contained block)
- Brower offline (file://) double-click renders correctly

# Visual heuristics (명시 룰)

- DAG / dependency / flow / component-relation → Mermaid diagram
- Comparison table → striped + sticky header
- Code block → syntax highlight
- H1 (one) / H2 / H3 → color + spacing differentiation
- Cross-reference → anchor `<a href="#...">`

LLM autonomy for: color palette, dark-mode color tuning, table detail, font choice.

# How to apply

1. Read the `.md` file in full
2. Generate `.html` with semantic 1:1 mapping + visual enhancements
3. Write the result to `<ABSOLUTE_HTML_PATH>` using the Write tool
4. Report: "HTML companion written: <path>. Headers (H1/H2/H3): <count>. Code blocks: <count>. Mermaid diagrams: <count>."

# Verification before writing

- `.md` 의 H1/H2/H3 헤더 개수 == `.html` 의 `<h1>/<h2>/<h3>` 개수 (±0)
- `.md` 의 코드 블록 개수 == `.html` 의 `<pre><code>` 개수 (±0)
- 외부 URL 참조 0 (모두 inline)
- `.md` 본문 sentence count 와 `.html` sentence-level node count 차이 5% 이내

If ANY check fails, do NOT write. Report failure and stop.

# Anti-Patterns

- 외부 CDN 참조 (`https://cdn.jsdelivr.net/...`) → 금지. inline 만.
- `.md` 의 의역 / 요약 / 재구조화 → 금지. semantic 1:1.
- AI 가 `.html` 읽기를 가정한 instruction → 금지. B 는 사람 전용.
- 인터랙티브 UI (탭/접힘/검색) → 금지. 정적 페이지만.
- `<h1>` 여러 개 / 헤더 hierarchy 깨짐 → 금지. `.md` hierarchy 답습.

You have one job: make a sibling `.html` that the human reads faster than the `.md`. Nothing else.
