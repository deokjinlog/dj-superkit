---
description: 다중 가벼운 task 를 한 batch 로 처리 (Socratic 2~3 Q × N + 단일 MD + parallel dispatch). 명시 슬래시 호출만 — 자동 발동 X.
---

# /fast-tasks

사용자에게 task 5~15개 한꺼번에 할당된 경우의 **lightweight batch 경로**. 명시 `/fast-tasks` 호출 시에만 발동.

## 영구 생략 (가벼움이 의도)

본 흐름은 다음 항목을 **절대 자동으로 추가하지 말 것**:

- `<slug>-tech-design.md`
- `<slug>-implementation-plan.md`
- `verifying-spec` 4축 보고서
- 변경이력 footer / `change-history` skill 호출
- `risk-annotation` (RISK 주석)
- `docs-pretty` / `code-pretty` 호출
- AskUserQuestion 게이트 (Socratic Q 외)

→ 최종 산출물은 단일 `<batch-slug>-tasks.md` **1 파일** + 실제 코드 변경만.

## Process

### Step 1 — Per-task Mini Socratic

사용자 첫 입력에서 task 목록 파싱. 각 task **마다** Socratic 질문 **2~3개** 던짐 (3개 초과 금지).

- 라운드 N회: task 1 질문 → 답 → task 2 질문 → 답 → ...
- 목표: 각 task 의 **입력/출력/제약** 최소 명확화
- 답이 명확하면 2개로 끝, 모호하면 3개까지

### Step 2 — 단일 `<batch-slug>-tasks.md` 작성

```
docs/features/YYYY-MM-DD-fast-tasks-<batch-slug>/<batch-slug>-tasks.md
```

본문:

```markdown
# <Batch slug> — Fast tasks (N개)

## Task 1: <title>
- 명세: <Socratic 합의>
- 영향 파일: <메인 추정>

## Task 2: <title>
...

---

## 병렬화 계획 (DAG)

- Chain A: 1 → 4 → 5   (이유: 4 가 1 산출물 의존, 5 가 4 산출물 의존)
- Chain B: 2 → 7       (이유: 7 이 2 export 사용)
- Independent: 3, 6, 8, 9, 10
```

### Step 3 — Smart Parallel Dispatch

메인이 §병렬화 계획 읽고:

- **Chain**: 하나의 서브에이전트가 순서대로 (1 → 4 → 5)
- **Independent**: 각각 별도 서브에이전트 동시 dispatch (Agent tool multi-call single message)
- **종속 판단**: LLM 휴리스틱 (명세 + 영향 파일 기반). 사용자 명시 X.

각 서브에이전트가 **commit 자체 수행** (per-task commit). 메인은 dispatch + 결과 종합만.

### Step 4 — 한 줄 요약

```
✅ fast-tasks <batch-slug> 완료: N tasks / M commits / 0 blocked.
   다음 단계: PR 또는 git merge 직접.
```

→ AskUserQuestion 게이트 X. 사용자가 직접 후속 처리.

## Non-goals

- 사용자가 명시 종속 그래프 그려주는 모드 (LLM 휴리스틱만)
- chain 내부 task 실패 시 자동 재시도 (사용자 수동 재실행)
- 풀 brainstorming 흐름으로 fallback (원하면 별도 `/brainstorm`)

## 입력 예시

```
/fast-tasks

이번 스프린트 할당 10개:
1) 로그인 페이지 다크모드 토글 추가
2) /api/users GET endpoint 추가 (페이지네이션)
3) Button 컴포넌트 size variant (sm/md/lg)
...
```
