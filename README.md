# js-super

> superpowers 베이스 + 한국형 spec-driven 워크플로우, 검증 게이트, 변경이력, 위험 주석, API 자동 테스트.

| 항목 | 값 |
|---|---|
| 버전 | **1.1.5** |
| 작성자 | 이진섭 (dlwlstjq410@gmail.com) |
| upstream | [superpowers](https://github.com/obra/superpowers) v5.0.7 (Jesse Vincent, MIT) |
| 라이선스 | MIT (upstream 동일) |

---

## 플러그인 설명

Claude Code의 [superpowers](https://github.com/obra/superpowers) 플러그인을 베이스로, **한국어 1인/소수 개발 환경**에 맞춘 spec-driven 워크플로우 확장이다. superpowers의 검증된 패턴(brainstorming → writing-plans → executing-plans)은 그대로 두고, 그 위에 다음을 얹었다.

### 워크플로우

1. **3-MD 산출물 분리** — `<slug>-requirements.md` (PRD) → `<slug>-tech-design.md` (기술 설계) → `<slug>-implementation-plan.md` (단계별 plan).
2. **dual-mode brainstorming** *(v1.1)* — PRD (구조화, 기본) / Socratic (자유 탐색, upstream 원본 스타일) 양자택일. PRD 모드는 카테고리(외부향 / 내부 도구 / 수정 / 인프라)별 **적응형 질문**으로 6 질문을 무조건 다 묻지 않는다.
3. **docs-pretty + code-pretty** *(v1.1.6)* — Sonnet 서브에이전트가 포맷만 정돈(의미 보존 strict). docs-pretty는 요구사항/개발방향에서는 **사용자 승인 후 1회**, 구현계획서에서는 **사용자 리뷰 직전 1회 (verifying-spec → code-pretty → docs-pretty)**. code-pretty는 구현계획서의 `**수정 후**` 코드블록만 prettify (원본 블록 불가침, 1% 의심 룰). 첫 변경이력 entry가 찍히면 자동 정지.

### 거버넌스

4. **메인 에이전트 검증 게이트** — 정합성 cross-check + 코드 임팩트 분석을 메인이 직접 수행. 단계 종료 직전 자동 발동.
5. **변경이력 자동 관리** — 3개 MD 하단에 구조화된 이력(언제 / 이유 / 무엇이 / 영향 범위 / 연관 CH-id)이 누적된다. 코드 변경 시 `commit_policy: per-task` 모드는 commit SHA 참조 (slim, v1.1.7), `single`/`none` 모드는 **변경 전·후 코드까지 보존**.
6. **변경 전파 (cascading)** — 상위 산출물 변경 시 하위까지 자동 영향 분석 + 사용자 승인 게이트.
7. **위험 주석 규약** — `# ⚠️ RISK(side-effect|breaking|race): <이유> — by <컨텍스트>` 표준 태그를 코드에 자동 부착 (3종 카테고리).
8. **변경이력 일괄정리 + 신규 entry types** *(v1.1.7)* — 서브에이전트 + 인라인 모드 모두 task별 즉시 footer append → **end-of-run consolidator 1회** 발화 (`[코드-수정] (batch: tasks N..M)` slim schema, per-task 모드는 코드 블록 생략 + `git show <SHA>`로 조회). 코드 0건 task용 `[검증]` / 버전 bump용 `[릴리즈]` entry type 도입. 서브에이전트 인터럽트 시 `.js-super/changelog-buffer/` 잔존 buffer 자동 검출 → 다음 세션에서 복구.
9. **사용자 게이트 인지성 + PRD 슬림** *(v1.1.8)* — 모든 enum-응답 HARD-GATE 8 곳 (brainstorming 모드 선택 / RAW 승인 / proceed-to-design / designing 결합 승인 / proceed-to-write-plan / writing 결합 승인 / 실행 모드 / finishing 옵션) 가 `AskUserQuestion` 도구로 노출 (harness 미지원 시 prose fallback). PRD adaptive rubric 슬림화 — ✅필수 16→8 (안 B), 모든 카테고리에서 ✅필수 §1+§3 두 개로 통일, §6 수용 기준은 ➖간소 디폴트 (게이트에서 "수용 기준 풀로" 명시 시 ✅ 승격).

### 자동화

10. **API 자동 테스트 파이프라인** — 메인이 백엔드 DB 조회 SQL을 안내하고, 사용자가 결과를 paste 하면 pytest 시나리오를 자동 생성·실행.
11. **워크트리 빠른 생성 + 메모리 자동 공유** *(v1.1.5 hook)* — `/worktree` 로 `.worktrees/<브랜치>/` 단수/복수 생성, `.env*` 자동 복사, 그리고 **Claude Code 메모리 폴더 자동 심링크** (PostToolUse hook). 워크트리 첫 세션부터 메인 레포의 user/feedback/project 메모리를 즉시 활용 + 양방향 동기화.

### 출구

12. **og-\* 원본 mirrors** *(v1.1)* — `/og-brainstorm`, `/og-write-plan`, `/og-execute-plan` 으로 upstream 원본 흐름을 별도 호출 가능. js-super 확장이 무거울 때 도망갈 수 있는 출구.

---

## 워크플로우 한눈에

```
/brainstorm     →  <slug>-requirements.md (PRD or Socratic)
      ↓
/design         →  <slug>-tech-design.md
      ↓                         ─── 메인 검증 게이트
/write-plan     →  <slug>-implementation-plan.md
      ↓                         ─── 메인 검증 게이트
/execute-plan   →  코드 구현 + 위험 주석 + 변경이력 자동 기록
      ↓
/api-test       →  DB SQL 안내 → 사용자 paste → pytest 시나리오 생성/실행
```

산출물 위치 (피처 단위):

```
docs/features/2026-05-02-<feature-slug>/
├── <slug>-requirements.md
├── <slug>-tech-design.md
├── <slug>-implementation-plan.md
└── api-tests/
    ├── conftest.py
    ├── scenario-001-<name>.py
    └── results/2026-05-02-1430.json
```

> 날짜는 **생성일 stamp (불변 ID)** — 작업 기간이 길어도 폴더명은 그대로 유지.

---

## 설치

두 가지 방식. 일반 사용자는 **A (GitHub)**, 본인이 직접 코드를 수정하며 쓸 거라면 **B (로컬)**.

### A. GitHub-hosted (사용자 권장)

본인 환경에 git이 깔려 있고 인터넷이 되면 이 방식이 가장 간단합니다.

**한 번만 등록 + install:**

```
# Claude Code 안에서
/plugin marketplace add LonerStayle/js-super
/plugin install js-super@js-super
```

세션 재시작 → 끝.

**업데이트 받기 (새 버전 push 됐을 때):**

```
/plugin marketplace update js-super
/plugin update js-super@js-super        # 버전 bump 있을 때
```

세션 재시작 후 반영. (skill 본문만 바뀌었으면 `update` 생략하고 `marketplace update` + 재시작만 해도 됨.)

**특정 버전(태그) 고정:**

```
/plugin install js-super@js-super --version v1.1.5
```

---

### B. 로컬 (개발자 / 본인)

본인이 skill 본문을 수정하면서 즉시 반영하고 싶거나, 인터넷 없이 쓸 때.

> **Note**: 아래 명령에서 `<JS_SUPER_PATH>` 는 이 저장소를 클론/다운로드한 **본인의 절대 경로**로 치환하세요 (예: `~/projects/js-super`, `/opt/plugins/js-super`).
>
> 환경변수로 미리 지정해두면 편합니다:
>
> ```bash
> export JS_SUPER_PATH="$HOME/path/to/js-super"
> ```

**B-1. 심볼릭 링크 (라이브 반영, 본인 개발에 권장)**

```bash
mkdir -p ~/.claude/plugins
ln -s "$JS_SUPER_PATH" ~/.claude/plugins/js-super
# Claude Code 재시작 → 플러그인 자동 인식
```

수정하면 다음 세션에서 바로 반영된다.

**B-2. 디렉터리 복사 (스냅샷 고정 사용)**

수정 없이 특정 시점 그대로 쓸 때.

```bash
cp -a "$JS_SUPER_PATH" ~/.claude/plugins/js-super
```

**B-3. 로컬 마켓플레이스 등록 (`/plugin` UI로 관리)**

```
# Claude Code 안에서 (절대 경로로 입력)
/plugin marketplace add <JS_SUPER_PATH>
/plugin install js-super@js-super
```

`.claude-plugin/marketplace.json` 을 활용 — 이 저장소에 이미 들어 있다.

---

### 설치 확인 (A/B 공통)

설치 + 세션 재시작 후 다음 슬래시가 자동완성에 보여야 한다:

- `/brainstorm`, `/design`, `/write-plan`, `/execute-plan`, `/api-test`, `/worktree`
- `/og-brainstorm`, `/og-write-plan`, `/og-execute-plan` (upstream 원본 mirror)

`/help` 로도 확인 가능.

### 제거

```
/plugin uninstall js-super@js-super
/plugin marketplace remove js-super
```

(B-1/B-2 로 깔았다면 `~/.claude/plugins/js-super` 디렉터리/심볼릭 링크 직접 삭제.)

---

## 첫 사용 빠른 시작

1. **새 피처 브레인스토밍**

   ```
   /brainstorm 사용자 잔액 출금 기능
   ```

   PRD / Socratic 모드 게이트가 먼저 뜬다 → 모드 선택 → `<slug>-requirements.md` 생성.

2. **기술 설계**

   ```
   /design
   ```

   → `<slug>-tech-design.md` 생성, 끝에 메인이 자동 검증.

3. **구현 계획**

   ```
   /write-plan
   ```

   → `<slug>-implementation-plan.md` 생성, 끝에 메인이 자동 검증.

4. **구현 실행**

   ```
   /execute-plan
   ```

   → 코드 작성 + 위험 주석 자동 부착 + 변경이력 자동 기록.

5. **API 자동 테스트**

   ```
   /api-test
   ```

   → 메인이 SQL 안내 → 사용자 paste → 시나리오 생성/실행.

> 진행 중 "X 바꿔줘"로 변경 요청하면 메인이 cascading 영향을 분석해서 하위 산출물 갱신을 제안한다.

---

## 부가 유틸: 워크트리 빠른 생성 (`/worktree`)

티켓별로 워크트리를 빠르게 만들고 `.env*` 파일을 자동 복사해 바로 빌드/서버 실행할 수 있게 해주는 단축 스킬. **v1.1.5 부터 Claude Code 메모리 폴더 자동 심링크도 포함** — 워크트리 첫 세션부터 메인 레포의 메모리를 즉시 사용한다.

**단수 호출:**

```
/worktree feature-a
```

**복수 호출:**

```
/worktree feature-a feature-b feature-c
```

**자연어 호출:**

```
/worktree
워크트리 3개 만들어줘. 브랜치는 feature-a, feature-b, feature-c.
```

> 티켓명(`TICKET-123-기능명`)을 그대로 브랜치명으로 사용해도 됩니다.

### 동작 요약

| 항목 | 동작 |
|---|---|
| 위치 | `<프로젝트 루트>/.worktrees/<브랜치명>/` |
| 브랜치 생성 | 없으면 현재 HEAD 에서 새로, 있으면 그대로 attach (remote만 있을 땐 origin에서 추적) |
| `.env*` 자동 복사 | 프로젝트 루트의 `.env`, `.env.local`, `.env.production` 등 모두 복사. `.env.example` / `.env.sample` 같은 커밋된 템플릿은 제외. **사용자에게 묻지 않음** — 빌드/실행 즉시 가능. |
| Claude 메모리 자동 심링크 | `worktree-memory-symlink` PostToolUse hook 이 자동 처리. 메인 레포 `~/.claude/projects/<encoded>/memory` 를 워크트리의 동일 위치에 심링크 → 양방향 메모리 공유. 메인에 메모리 0건이거나 워크트리에 이미 메모리 폴더가 있으면 자동 생략. |
| `.gitignore` | `.worktrees/` 가 없으면 자동 추가 |
| 충돌 처리 | 같은 path 가 이미 있으면 skip + notice (덮어쓰기 X) |

**전제**: 현재 디렉터리가 git 저장소여야 함 (아니면 `git init` 안내).

**워크트리 정리 (수동, 의도적으로 자동화 안 함)**:

```bash
git worktree remove .worktrees/<브랜치>
git branch -d <브랜치>   # 더 안 쓰면
```

---

## 의존성 (사용자 환경)

| 용도 | 도구 |
|---|---|
| API 자동 테스트 실행 | `python>=3.10`, `pytest`, `requests`, `pytest-json-report` |
| DB 조회 | 사용자가 직접 (SQL paste 방식, 플러그인은 DB 접근 안 함) |
| Hook JSON 파싱 | `jq` 또는 `python3` (둘 중 하나만 있으면 OK — fallback 자동) |
| Claude Code | 최신 버전 권장 |

API 테스트 의존성은 첫 `/api-test` 실행 시 메인이 install 안내한다.

---

## upstream superpowers와의 관계

- 이 저장소는 **superpowers v5.0.7 풀 카피**에 확장을 얹은 형태(vendoring).
- upstream 업데이트가 있으면 수동 머지로 따라간다 (`.claude-plugin/plugin.json` 의 `upstream.version` 필드로 베이스 버전 추적).
- 변경된 skill 목록은 [`docs/superpowers/specs/2026-05-02-js-superpowers-design.md`](docs/superpowers/specs/2026-05-02-js-superpowers-design.md) §2.3 참조.

원본 superpowers의 라이선스(MIT, Jesse Vincent)는 그대로 유지된다.

### upstream 원본 동작도 같이 살리기 — `/og-*` 커맨드

js-super 1개만 깔고도 upstream 원본 워크플로우에 접근할 수 있도록 **`og-`(original) 접두사 사본**을 제공한다. js-super 확장이 무겁다고 느낄 때 (예: 내부 스크립트, 탐색 작업) upstream 원본 동작으로 도망갈 수 있다.

| 명령 | 호출 skill | 산출물 경로 |
|---|---|---|
| `/og-brainstorm` | `og-brainstorming` | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` |
| `/og-write-plan` | `og-writing-plans` | `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md` |
| `/og-execute-plan` | `og-executing-plans` | (코드만) |

og-* 흐름은 **변경이력 / 위험주석 / docs-pretty / verifying-spec 안 탐**. 진짜 upstream 그대로의 가벼운 경험.

> **중요**: og-* 흐름과 js-super 정식 흐름(`/brainstorm` `/design` `/write-plan` `/execute-plan`)을 **한 피처 안에서 섞지 마세요**. 한 피처는 한 흐름으로 일관되게. 산출물 경로도 다르므로 (`docs/features/...` vs `docs/superpowers/...`) 자연스럽게 분리됨.

다른 upstream skill (subagent-driven-development, finishing-a-development-branch, debugging 등)은 js-super가 손대지 않은 채로 vendor 되어 있어 원본 이름 그대로 동작 — `og-` 사본 별도로 없다.

---

## 설계 문서

전체 설계 결정과 이유는 다음 문서 참조:

- [`docs/superpowers/specs/2026-05-02-js-superpowers-design.md`](docs/superpowers/specs/2026-05-02-js-superpowers-design.md) — 초기 설계
- [`docs/superpowers/plans/2026-05-09-worktree-memory-symlink-hook.md`](docs/superpowers/plans/2026-05-09-worktree-memory-symlink-hook.md) — v1.1.5 메모리 심링크 hook 구현 plan

---

## 라이선스

MIT (upstream superpowers와 동일).
