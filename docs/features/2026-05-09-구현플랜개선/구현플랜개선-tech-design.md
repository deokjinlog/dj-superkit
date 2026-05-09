# 개발방향: 구현플랜개선

> **For agentic workers:** This document is the technical spec. It is anchored to `구현플랜개선-requirements.md` (PRD, Socratic 모드) and consumed by `구현플랜개선-implementation-plan.md`. NEXT STEP: invoke `writing-plans` skill (or run `/write-plan`). Do NOT include step-by-step implementation tasks here.

---

## 1. 아키텍처 개요

이번 변경은 **신규 외부 컴포넌트 도입 0개**, **신규 내부 스킬 1개 (`code-pretty`)**, 그리고 **3개 caller 스킬의 트리거 재배선**으로 구성된다. 데이터 영속성·외부 API·서비스 호출 없음. 모든 변경은 Markdown 스킬 문서와 그 안의 호출 시퀀스에 한정.

### 변경 축

```
[축 1: 호출 시퀀스 재배선]
  brainstorming/designing-direction/writing-plans
    └─ docs-pretty 호출 위치 = (사용자 리뷰 직전) → (사용자 승인 직후, 변경이력 직전)

[축 2: 스킬 신설]
  skills/code-pretty/SKILL.md (신규, 서브에이전트 디스패처)

[축 3: 스키마 컨벤션]
  writing-plans 산출물의 task 코드블록 = "원본/수정 후" 라벨 쌍
```

### 이유

세 caller 스킬에 **공통의 호출 시퀀스 패턴**(작성 → 검증 → docs-pretty → 사용자 리뷰)이 박혀 있다. PRD §결정 1은 이 시퀀스의 "docs-pretty 위치"만 한 단계 뒤로 미는 것이라, 각 SKILL.md의 Process / Process Flow 다이어그램 / Anti-Patterns 표를 동일 패턴으로 수정하면 된다.

`code-pretty`는 docs-pretty 패턴(서브에이전트 + 엄격 negative constraint + 사전/사후 sanity check)을 그대로 재사용한다. 서브에이전트 모델, 디스패치 인터페이스, 사후 검증 표 모두 docs-pretty의 형태와 동일. **새 메커니즘이 아니라 docs-pretty의 형제 스킬**이라는 입장.

---

## 2. 영향 받는 컴포넌트/파일

| 파일                                                                               | 변경 종류        | 변경 내용                                                                                                              |
| ---------------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `skills/brainstorming/SKILL.md`                                                    | Modify           | Checklist 항목 6/7 순서 변경, Process Flow 다이어그램, "User reviews" 단계 wording (raw markdown 명시)                |
| `skills/designing-direction/SKILL.md`                                              | Modify           | Checklist 항목 6/7 순서 변경, Process Flow 다이어그램, "Single combined approval gate" wording                        |
| `skills/writing-plans/SKILL.md`                                                    | Modify           | Checklist 항목 7/8 순서 변경, Process Flow 다이어그램, **task 스키마에 Before/After 컨벤션 추가**, code-pretty 호출 추가 |
| `skills/docs-pretty/SKILL.md`                                                      | Modify           | 프론트매터 description, HARD-GATE 본문, "When to Use" 표, Process Flow에 새 트리거 위치 반영                            |
| `skills/code-pretty/SKILL.md`                                                      | Create           | 신규 스킬 본문 전체 (frontmatter + HARD-GATE + Process + 서브에이전트 prompt template + sanity-check + Anti-Patterns) |
| `skills/code-pretty/tests/`                                                        | Create           | fixture 기반 수동 검증 자료 (입력 MD + 기대 출력 MD)                                                                   |
| `skills/code-pretty/scripts/` (선택)                                               | Create?          | 코드블록 추출 헬퍼 (LLM이 직접 처리해도 되면 생략)                                                                     |
| `README.md` (line 22 부근)                                                         | Modify           | 현재 "3-MD 사용자 리뷰 **직전마다** Sonnet 서브에이전트가 포맷만 정돈" 문구를 새 정책에 맞춰 갱신                       |
| `docs/features/2026-05-09-구현플랜개선/구현플랜개선-requirements.md`              | Modify (cascade) | 사용자 추가 우려 R7 ("이미 이쁜 코드 강제 변경") 을 PRD §우려·해결에 1행 추가 — change-propagation 호출               |

**범위 밖 (PRD와 일관)**: `skills/og-*` (upstream 미러), `skills/executing-plans/`, `skills/api-auto-testing/`, `skills/risk-annotation/`, `skills/change-history/` 등 — 변경 없음.

---

## 3. 데이터 모델/스키마 변경

### 3.1 `<slug>-implementation-plan.md` task 코드블록 스키마 (신규 컨벤션)

기존 task 본문에서 코드를 보여줄 때 단일 코드블록만 사용했으나, 새 스키마는 **라벨 + 페어 블록**:

```markdown
**원본** (`<file>:<line-range>`):
` ``ts
<original code>
` ``

**수정 후**:
` ``ts
<new code>
` ``
```

- "원본" 블록의 라벨 prefix는 정확히 `**원본**` (마크다운 굵은 텍스트). 그 뒤에 파일경로 인용 (` `` `) — 옵션이지만 강력 권장.
- "수정 후" 블록의 라벨은 정확히 `**수정 후**`.
- 신규 파일 작성 task는 **원본 블록 생략**, 수정 후만.
- code-pretty가 이 라벨을 통해 prettify 대상("수정 후")과 불가침("원본")을 구별한다.

이 라벨 컨벤션은 `writing-plans/SKILL.md`의 schema/anti-patterns/process에 명시한다.

### 3.2 데이터 영속화

없음. 파일 시스템상 변경은 위 §2의 SKILL.md 파일들과 신규 `code-pretty/` 디렉토리뿐.

---

## 4. 외부 인터페이스

### 4.1 사용자 노출 인터페이스

- **변경 없음**: 사용자가 직접 호출하는 슬래시 커맨드 (`/brainstorm`, `/design`, `/write-plan`, `/execute-plan`, `/api-test`, `/worktree`)는 그대로.
- **PRD 범위 밖 명시**: 사용자가 직접 `/code-pretty`를 임의 파일에 돌리는 standalone 진입점은 도입하지 않음.

### 4.2 스킬 간 호출 인터페이스

- `writing-plans` → `code-pretty` (신규 dispatch 경로)
- `brainstorming` → `docs-pretty` (호출 시점만 변경, 시그니처 동일)
- `designing-direction` → `docs-pretty` (호출 시점만 변경)
- `writing-plans` → `docs-pretty` (호출 시점만 변경, code-pretty 직후)

### 4.3 서브에이전트 prompt 인터페이스

`code-pretty`가 디스패치하는 Sonnet 서브에이전트의 prompt template (외부 인터페이스로 관리):

- 입력: 대상 파일 절대경로
- 명세: "수정 후" 라벨 직후 코드블록만 prettify, "원본" 라벨 블록 절대 불가침, 허용/금지 작업 표 명시
- 출력: 변경된 라인 diff 요약 + 변경된 파일 내용 Write
- 위반 시: write 하지 않고 실패 보고

---

## 5. 핵심 결정 + 대안

### 결정 D1 — `code-pretty` 구현 패턴 = 서브에이전트 디스패처 (`model: sonnet`)

**채택**: docs-pretty와 동일한 패턴. Main agent가 pre-flight check 후 Sonnet 서브에이전트로 dispatch.

**대안 A (메인 인라인)**: Main agent가 직접 코드블록 파싱 → prettify.

- 장점: 디스패치 오버헤드 0, 토큰 절약
- 단점: Main context에 코드 raw 텍스트 다 적재 (수정 후 블록 다수 시 비용 큼). 또 reasoning 모델로 prettify는 과도.

**대안 B (외부 스크립트 + LLM)**: 정규식/AST 파서가 블록을 추출해서 LLM에 단일 블록만 던짐.

- 장점: 라벨 라우팅을 결정론적으로 처리 가능.
- 단점: 신규 스크립트 추가 비용. js-super는 "스킬 우선, 스크립트는 hook 등 반드시 필요할 때만" 정책. v1.1.5 메모리 심링크 hook이 그 예외.

**채택 이유**: docs-pretty가 이미 검증된 패턴. negative constraint("의미 불변")에 강한 Sonnet의 instruction-following이 핵심 안전장치(1% 의심 룰). 새 패턴 도입 비용 없음.

### 결정 D2 — Before/After 라벨 검출 = 마크다운 굵은 텍스트 라벨

**채택**: 직전 줄에 `**원본**` / `**수정 후**` 라벨이 있는 코드블록을 페어로 인식.

**대안 A (HTML 주석 마커)**: `<!-- code-pretty:target -->` / `<!-- code-pretty:skip -->` 식.

- 장점: 결정론적 파싱, 사람 읽기에는 보이지 않음.
- 단점: 사용자가 읽는 구현계획서에 "내부 마크업"이 노출. 굵은 라벨은 사람한테도 자연스럽게 도움 됨.

**대안 B (위치 기반 페어링)**: 짝수 번째 블록이 "원본", 홀수가 "수정 후".

- 장점: 마크업 없음.
- 단점: 신규 파일(원본 없음) 케이스에서 깨짐. fragile.

**채택 이유**: 라벨이 사람한테도 의미 있고 LLM이 검출하기 쉬움. PRD §결정 2의 출력 형식과 자연스럽게 일치.

### 결정 D3 — `docs-pretty` 자체 스킬 본문도 업데이트

**채택**: 호출 시점이 바뀌므로 docs-pretty/SKILL.md의 frontmatter description, HARD-GATE 본문 텍스트, "When to Use" 표를 새 시점에 맞춰 수정.

**대안 (caller만 수정, docs-pretty는 둠)**: 시간 절약.

- 단점: 미래의 LLM agent가 docs-pretty SKILL.md 본문(현재: "fires BEFORE showing it to the user")을 읽고 caller의 새 호출 시점과 충돌하는 지시를 해석할 수 있음. 위험.

**채택 이유**: SKILL.md는 LLM 행동 형성 코드다. caller만 고치고 callee 본문을 그대로 두면 가이드라인이 분기됨.

### 결정 D4 — code-pretty diff 출력 = main agent 채팅 메시지

**채택**: code-pretty 서브에이전트가 diff 요약 텍스트를 main agent에 반환, main agent는 이걸 사용자에게 그대로 보여줌. 별도 파일 안 만듦.

**대안 A (별도 파일 저장)**: `<slug>-code-pretty-diff.txt` 등.

- 장점: 감사 추적 가능.
- 단점: 일회성 정보가 디스크에 남음. 변경이력 footer가 이미 감사 추적 역할 — 이중화.

**대안 B (구현계획서 안에 diff 섹션 추가)**:

- 단점: 구현계획서 본문이 노이즈로 더러워짐. 변경이력 footer와 책임 중복.

**채택 이유**: diff 요약은 사용자 즉시 검토용. 영구 저장 가치 낮음. 변경이력은 본문 변경 자체를 추적.

### 결정 D6 — "이미 이쁜 코드는 손대지 않는다" no-op 규칙 (사용자 추가 우려 대응)

**채택**: code-pretty 서브에이전트 prompt에 강한 negative constraint 추가:

> "If the '수정 후' code block is already well-formatted (consistent whitespace, no obvious readability issues, no duplicate import / dead comment / inconsistent quote), **leave it byte-identical**. You MUST be able to articulate a concrete readability improvement for any change you make. If you cannot, do nothing."

추가 안전장치:

1. **블록 단위 no-op 게이트**: 서브에이전트는 각 "수정 후" 블록을 처리한 뒤, "이 블록에 어떤 readability 개선이 있는가?"를 자체 보고. 답할 수 없으면 byte-equal 보존.
2. **Diff 요약에 "변경 없음 N개" 표시**: 사용자가 한눈에 "code-pretty가 무리하게 손대지 않았다"는 시그널을 받음.
3. **공백/들여쓰기만의 trivial 변경은 변경 카운트에서 제외**: prettifier가 "변경한 것처럼 보이려고" 의미 없는 공백 정리만 하는 것을 방지. diff 요약은 substantive 변경만 셈.

**대안 (idempotent assertion)**: code-pretty를 두 번 연속 돌렸을 때 두 번째는 0 변경이어야 한다는 idempotency 검증.

- 단점: 비용 두 배. 첫 회만 실행하고 사용자에게 diff를 보여주는 것으로 충분.

**채택 이유**: PRD §결정 3 "1% 의심 룰"은 *의미 변경* 의심을 다룸. 이번 우려는 *불필요한 형식 변경*. 두 가지를 prompt에서 분리해 명시해야 안전.

### 결정 D5 — code-pretty 호출 위치 = `writing-plans` 흐름 안 (검증 후, docs-pretty 직전)

**채택**: PRD §결정 3 위치 그대로. `verifying-spec → code-pretty → docs-pretty → change-history → 사용자 리뷰` 순서.

**대안 (사용자 리뷰 후, 승인 직후)**: docs-pretty와 함께 1회씩만 돌게.

- 단점: 사용자가 raw "수정 후" 코드를 검토하게 됨. 리뷰 단계에서 prettified 코드를 보면 가독성 향상이 곧바로 체감됨. 또 검증 직후 시점이 "본문이 안정화된" 자연스러운 prettify 트리거.

**채택 이유**: 사용자가 prettified 결과를 보고 검토할 수 있는 게 코드 프리티 도입 취지에 부합.

**PRD 충돌 해결 (사용자 확정)**: PRD §결정 1과 §결정 3의 흐름이 writing-plans에서 충돌했으나, 사용자가 다음과 같이 확정:

| 단계 | brainstorming / designing-direction          | writing-plans                                                                    |
| ---- | -------------------------------------------- | -------------------------------------------------------------------------------- |
| 1    | Q&A → 초안                                   | Q&A → 초안 (Before/After 블록 포함)                                              |
| 2    | —                                            | verifying-spec                                                                   |
| 3    | —                                            | code-pretty (수정 후 블록만)                                                     |
| 4    | —                                            | docs-pretty (1회)                                                                |
| 5    | **사용자 리뷰 (raw 마크다운)**               | **사용자 리뷰 (prettified + diff 요약)**                                         |
| 6    | 수정 요청 → 재작성 → 다시 raw 리뷰 (loop)   | 수정 요청 → 재작성 → 검증 → code-pretty → docs-pretty 재실행 → 다시 prettified 리뷰 (loop) |
| 7    | 승인                                         | 승인                                                                             |
| 8    | docs-pretty (최종 1회)                       | — (이미 docs-pretty 4단계에서 처리됨)                                            |
| 9    | 변경이력 ([요구사항-수정] 또는 [개발방향-수정]) | 변경이력 ([구현계획서-수정])                                                    |
| 10   | 다음 게이트 (/design 또는 /write-plan)       | /execute-plan 게이트                                                             |

**핵심 차이 (사용자 직접 설명)**: writing-plans 산출물은 코드 블록을 포함하므로 **사용자가 prettified 상태에서 신중하게 검토**해야 함. 그래서 prettify는 사용자 리뷰 *직전*. 산문 위주의 brainstorming/designing-direction은 raw 마크다운 검토로 충분 → prettify는 *승인 후*.

**"1회"의 해석**: PRD §결정 1의 "최종 1회"는 *per draft state*로 해석. 즉 사용자 수정 요청 시 재작성 후 prettify 재실행 가능. 단, 동일 draft 상태에서 두 번 이상 발화하지 않음 (현행 "리뷰 직전마다 재발화"와의 차이).

---

## 6. 위험/사이드이펙트 (preliminary)

| ID  | 카테고리    | 위험 시나리오                                                                                                             | 완화                                                                                                                                                                         |
| --- | ----------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | side-effect | code-pretty가 라벨 검출 실패해서 "원본" 블록을 prettify 대상으로 오인 → 원본이 변형됨                                    | (a) 1% 의심 룰 (b) 사후 sanity check: "원본" 블록 byte-equal 검증 (c) diff-only 출력으로 사용자가 즉시 거부                                                                 |
| R2  | side-effect | Sonnet이 "중복 통합" 단계에서 의미 미세 차이가 있는 헬퍼를 합쳐버림                                                       | prompt에 "1% 의심이라도 들면 SKIP" 명시, 통합한 항목은 diff 요약에 별도 표시                                                                                                |
| R3  | breaking    | 3개 caller 스킬 (`brainstorming`/`designing-direction`/`writing-plans`)의 wording이 동기화되지 않으면 LLM 혼란             | 모든 변경을 단일 PR-스타일 commit으로 묶고, change-history에 cross-link 기록 (change-propagation 호출)                                                                      |
| R4  | breaking    | docs-pretty SKILL.md 본문을 caller보다 늦게 업데이트하면 중간 시점 LLM이 conflict 해석                                   | 변경 순서를 docs-pretty 먼저, caller 나중으로 (commit 단위로 atomic 보장)                                                                                                    |
| R5  | side-effect | 결정 D5에서 명시한 PRD 결정 1 vs 결정 3 충돌이 추가 사용자 확인 없이 묻히면, 미래 사용자 신고 재발 가능                   | 사용자 리뷰 단계에서 D5 ⚠️ 부분 명시적 확인. 필요시 PRD를 정정 (change-propagation)                                                                                         |
| R6  | side-effect | 기존 (이미 작성된) 구현계획서를 새 정책으로 잘못 reprocess (재 docs-pretty / 재 code-pretty)                              | docs-pretty/code-pretty 둘 다 pre-flight: `## 변경이력` footer에 entry 1개 이상이면 즉시 abort                                                                              |
| R7  | side-effect | code-pretty가 이미 이쁜 "수정 후" 블록을 **불필요하게** 변형 (의미 변경은 없으나 형식 변경) — 사용자 신뢰 잠식            | (a) 결정 D6의 "이미 이쁜 코드 byte-identical 보존" 규칙 (b) 블록별 no-op 게이트 (c) trivial 공백 변경은 diff 카운트 제외 (d) 사용자가 diff에서 "변경 없음 N개" 노출 받음    |

**위험 카테고리 분류**: PRD가 Socratic 모드라 명시적 NFR이 없지만, "기능 망가지지 않을 것"이 강한 안전 NFR이다 → R1/R2는 그 NFR과 직접 연결.

---

## 7. 테스트 전략

### 7.1 단위 (fixture-based, 자동화 가능)

- **F1** — `code-pretty` 서브에이전트 prompt fixture: 입력 MD에 `**원본**` 페어 + `**수정 후**` 코드블록 → 처리 후 "원본" byte-equal 보존 + "수정 후" 포맷 정돈됨
- **F2** — 신규 파일 케이스 fixture: "원본" 블록 없이 "수정 후"만 → 처리 후 변경됨
- **F3** — 적대적 fixture (금지 작업): 매직 넘버 / 중첩 if / 함수 분리 가능 코드 → 처리 후 변환 안 됨
- **F4** — 적대적 fixture (1% 의심 룰): 동일해 보이는 inline 헬퍼 두 개지만 호출 컨텍스트 미묘 차이 → 통합되지 않음 + diff에 "skipped: ambiguous" 명시
- **F5** — 이미 이쁜 코드 fixture (R7 검증): 깔끔한 들여쓰기 / 일관된 따옴표 / 죽은 주석 없음 / 중복 없음인 "수정 후" 블록 → code-pretty 통과 후 byte-equal 유지, diff 요약에 "변경 없음" 보고

### 7.2 통합 (수동 dogfood)

- **I1** — `/brainstorm` end-to-end: 사용자 승인 전 docs-pretty 호출 0회, 승인 직후 1회 → AC-1 검증
- **I2** — `/design` end-to-end: 동일 패턴 → AC-1 검증
- **I3** — `/write-plan` end-to-end: 사용자 리뷰 직전 단 한 번 (verifying-spec → code-pretty → docs-pretty → 변경이력 → 사용자 리뷰) 흐름 검증 → AC-1, AC-3 검증
- **I4** — `/write-plan` 산출물 검사: 모든 task가 `**원본**`/`**수정 후**` 라벨 사용, 신규 파일은 원본 생략 → AC-2 검증
- **I5** — `/write-plan` 산출물 후 검사: prettify 자국이 "수정 후" 블록에서만 발견됨 → AC-4 검증
- **I6** — diff 요약 노출 검증: code-pretty 출력에 변경 라인 요약 포함 → AC-5 검증
- **I7** — 적대적 입력 통과 테스트: 매직 넘버 / 중첩 if 가 들어간 task 코드 → code-pretty 통과 후 그대로 → AC-6 검증
- **I8** — 1% 의심 룰: 미묘한 중복 → 통합 안 됨 → AC-7 검증

### 7.3 회귀 (구버전 보호)

- **G1** — 이미 작성된 (변경이력 entry 1개 이상) `<slug>-implementation-plan.md`에 code-pretty/docs-pretty 어느 쪽도 발화 안 됨 → R6 검증
- **G2** — `og-*` 스킬 (`og-brainstorming` / `og-writing-plans` / `og-executing-plans`) 비변경 확인 (grep `docs-pretty` / `code-pretty` 호출 없음 변경 없음)

### 7.4 테스트 매트릭스 요약

| AC   | 검증 수단                               |
| ---- | --------------------------------------- |
| AC-1 | I1 / I2 / I3                            |
| AC-2 | I4                                      |
| AC-3 | I3                                      |
| AC-4 | I5 + F1                                 |
| AC-5 | I6                                      |
| AC-6 | I7 + F3                                 |
| AC-7 | I8 + F4                                 |
| AC-8 | 파일 존재 검사 + caller wiring grep     |

---

## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-09 16:03] [개발방향-수정]
- **id**: CH-20260509-002
- **이유**: 신규 기술 설계 (구현계획서 흐름 개선 — docs-pretty 타이밍 / Before/After 코드블록 / code-pretty 신규 스킬)
- **무엇이**: 구현플랜개선-tech-design.md 전체 (§1 아키텍처 / §2 영향 파일 / §3 스키마 / §4 인터페이스 / §5 결정 D1~D6 / §6 위험 R1~R7 / §7 테스트 F1~F5+I1~I8+G1~G2)
- **영향범위**: 없음 (최초 생성)
- **연관 항목**: CH-20260509-001 (요구사항)
