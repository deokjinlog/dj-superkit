# 요구사항: 구현플랜개선

> **Mode:** Socratic (free-form). Downstream `designing-direction` reads this prose without expecting fixed PRD section IDs.
>
> **For agentic workers:** This document is the PRD (planning-level only). NEXT STEP: invoke `designing-direction` skill (or run `/design`) to produce `구현플랜개선-tech-design.md`. Do NOT add tech decisions or implementation details here.

## 배경

`writing-plans` / `executing-plans` 워크플로우를 실제로 사용한 개발자로부터 **구현계획서(`<slug>-implementation-plan.md`)** 관련 불편 신고 3건이 접수됨. 이번 작업은 그 3건을 일관된 정책으로 묶어 해결한다.

신고 원문(요약):

1. **(impl)** 구현계획서가 수정될 때마다 `docs-pretty`가 매번 재실행돼 비용·대기시간이 큼. 처음 만들고 검증이 끝난 시점에만 1회 돌면 충분함.
2. **(impl)** 구현계획서에 적힌 "변경 후 코드"만으로는 원본 소스의 어디가 어떻게 바뀌는지 감이 잡히지 않음. GitHub diff처럼, 또는 원본 코드를 함께 보여주면 좋겠음.
3. **(impl)** 검증 직후 ~ `docs-pretty` 직전 사이에 새로운 **`코드 프리티`** 스킬을 끼워 넣어, 구현계획서 안의 코드 블록만 골라 "기능을 절대 망치지 않는 선의 아주 작은 리팩터링"으로 가독성을 높이고 싶음.

세 신고 모두 **구현계획서**를 직접 짚었지만, 신고 1번(`docs-pretty` 타이밍)은 동일한 패턴이 `brainstorming` / `designing-direction`에도 존재하므로 **세 스펙 단계 전체에 일괄 적용**한다는 결정을 내렸다 (사용자 직접 결정).

## 적용 범위

| 영역                            | 변경 여부                            | 비고                        |
| ------------------------------- | ------------------------------------ | --------------------------- |
| `writing-plans` (구현계획서)    | ✅ 변경 — 신고 1, 2, 3 모두 영향    | 3건의 1차 진앙지            |
| `brainstorming` (요구사항)      | ✅ 변경 — 신고 1만 영향              | `docs-pretty` 타이밍 일관화 |
| `designing-direction` (개발방향) | ✅ 변경 — 신고 1만 영향             | `docs-pretty` 타이밍 일관화 |
| `code-pretty` (신규 스킬)       | ✅ 신설                              | 신고 3 산출물               |
| `executing-plans`               | ❌ 변경 없음                         | 구현계획서 작성/렌더링과 무관 |
| 기타 스킬                       | ❌ 변경 없음                         |                             |

## 핵심 결정 (Socratic 합의 사항)

### 결정 1 — `docs-pretty`는 검증 통과 후 최종 1회만 실행 (신고 1)

세 스펙 단계 (`brainstorming` / `designing-direction` / `writing-plans`) 모두 다음 흐름으로 통일:

```
초안 작성 → (검증 단계, 해당 스킬에 있을 경우) → 사용자 리뷰 (prettify 안 된 raw)
↓ (사용자가 수정 요청 시)
재작성 → 다시 사용자 리뷰
↓ (사용자 승인 시)
docs-pretty (최종 1회) → 변경이력 기록 → 다음 단계 게이트
```

**현행과의 차이**: 현재는 *사용자 리뷰 직전*에 `docs-pretty`가 매번 돌고, 수정 요청이 들어오면 또 돌고 또 돈다. 변경 후에는 *최종 승인 직후 1회*만 돈다.

**트레이드오프 인지**: 사용자가 raw 마크다운을 검토하게 됨 (가독성 약간 떨어짐). 그러나 docs-pretty 비용 절감과 일관성이 더 중요하다는 판단.

### 결정 2 — 구현계획서 코드 블록은 Before/After 블록 쌍 (신고 2)

각 task에서 코드를 변경할 때, 다음 두 코드블록을 쌍으로 제시:

~~~markdown
**원본** (`src/cart.ts:42-44`):
```ts
const total = items.reduce((acc, x) => acc + x.price, 0);
```

**수정 후**:
```ts
const total = items.reduce((acc, x) => acc + (x.price ?? 0), 0);
```
~~~

**예외**: "신규 파일" 작성처럼 원본이 없는 경우는 **원본 블록 생략**. 수정 후 블록만 보여준다.

**채택 이유**:

- 두 코드블록 모두 syntax-highlight 살아있음 (diff 블록 대비 가독성 우위)
- 기존 `change-history` 스킬의 "변경 전/후" 패턴과 일관
- LLM 작성 흐름이 명확 ("원본을 read 후 인용 → 수정 후 작성")

**적용 위치**: 오직 `writing-plans` 산출물 (`<slug>-implementation-plan.md`)의 task별 코드 블록만. `tech-design.md`나 `requirements.md`는 영향 없음.

### 결정 3 — 신규 스킬 `code-pretty` 도입 (신고 3)

#### 위치

구현계획서 흐름 중간에 끼워 넣음:

```
구현계획서 초안 → 검증(verifying-spec) → code-pretty → docs-pretty → 변경이력 → 사용자 리뷰
```

검증 직후 ~ `docs-pretty` 직전. 검증을 통과한 안정적인 본문만이 prettify 대상이라는 의미.

#### 대상

- 오직 `<slug>-implementation-plan.md` 내부의 **"수정 후" 코드블록**만.
- "원본" 블록(결정 2의 좌변)은 **절대 건드리지 않음** (원본은 원본대로 보존되어야 함).
- 산문(설명 텍스트), 표, 다른 마크다운 요소는 대상 아님.

#### 허용 작업 (B 정책 + 중복 통합)

| 카테고리    | 허용 예                                                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 포맷        | 공백/들여쓰기/줄바꿈, 긴 라인 적절 위치 줄바꿈, 후행 공백 제거, 일렬 주석 정렬                                                           |
| 자명한 정리 | 명백히 죽은 주석(`// TODO: 삭제예정` 등) 제거, 따옴표/세미콜론 통일, 컨텍스트가 압도적으로 명확한 변수명 정리, 매직 넘버에 주석 라벨링   |
| 중복 통합   | 중복 import 통합, 동일 값 중복 선언 통합, 동일 inline 헬퍼 통합                                                                           |

#### 금지 작업

- 매직 넘버를 명명 const로 추출 (변수 추출은 refactor)
- 중첩 if 평탄화, 함수 분리, 인라인 wrapper 정리 (구조적 리팩터링)
- 변수/함수 이름 변경 — 컨텍스트가 압도적으로 명확하지 않은 한
- 의미 보존 여부에 1%라도 의심이 들면 **건드리지 않음** (LLM 확신 없으면 그대로 둔다)

#### 안전장치

1. **Diff-only 출력 게이트**: prettify 결과를 사용자에게 보여주기 전, 변경한 라인을 diff 형태로 한 번에 노출. 사용자가 수상한 변경은 즉시 거부할 수 있음.
2. **원본 블록 불가침**: Before/After 쌍 중 "원본" 블록은 prettify 입력에서 자동 제외.
3. **불확실하면 패스**: 중복 통합/변수명 정리 중 "혹시 기능 영향?"이라는 의심이 1%라도 들면 그 항목은 건드리지 않고 다른 항목만 처리.

## 새로운 흐름 (전체 그림)

```
[brainstorming]
  Q&A → 초안 → 사용자 리뷰 (raw) → (수정 루프) → 승인 → docs-pretty(1회) → change-history → /design

[designing-direction]
  Q&A → 초안 → 사용자 리뷰 (raw) → (수정 루프) → 승인 → docs-pretty(1회) → change-history → /write-plan

[writing-plans]
  Q&A → 초안 (Before/After 블록 사용) → verifying-spec
    → code-pretty (수정 후 블록 대상)
    → docs-pretty (1회)
    → change-history
    → 사용자 리뷰 → 승인 → /execute-plan
```

## 우려 / 해결

| 우려                                                        | 해결                                                                                         |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 사용자가 raw 마크다운을 검토하게 되어 보기 불편하지 않을까? | 결정 1 트레이드오프로 명시적으로 수용. docs-pretty 비용 절감이 더 큼.                       |
| code-pretty가 의도치 않게 코드 의미를 바꾸면?              | (a) 1% 의심 룰 (b) diff-only 게이트 (c) 원본 블록 불가침 — 3중 안전장치                    |
| Before/After 블록으로 구현계획서 길이가 두 배 되지 않나?   | 신규 파일은 원본 생략. 큰 함수는 핵심 변경 지점만 인용. 길이는 가독성 향상 대가로 수용.    |
| 기존에 작성된 구현계획서들에도 소급 적용?                   | **소급 적용 안 함**. 새로 작성되는 구현계획서부터 새 정책 적용. (범위 밖)                   |
| 코드 프리티가 이미 이쁜 코드를 강제로 변경할까봐? (사용자 추가 우려)  | (a) prompt에 "이미 잘 포맷된 블록은 byte-identical 유지" 강한 negative constraint (b) 블록별 no-op 게이트 — readability 개선을 명확히 articulate 못하면 변경 안 함 (c) Diff 요약에 "변경 없음 N개" 노출 |

## 범위 밖 (Out of Scope)

- 이미 작성된 기존 구현계획서들의 소급 마이그레이션 (Before/After 변환, code-pretty 재실행 등)
- `executing-plans` 스킬 동작 변경
- API 자동테스트 / 위험주석 / 워크트리 / change-history 스킬 변경
- code-pretty가 마크다운 산문이나 표를 정돈하는 기능 (오직 코드블록만)
- Before/After 패턴을 `requirements.md` / `tech-design.md`로 확장하는 것 (오직 implementation-plan만)
- 사용자가 직접 `/code-pretty` 같은 슬래시 커맨드로 임의 파일에 prettify 돌리는 standalone 진입점 (이번엔 writing-plans 흐름 내부 자동 호출만)

## 수용 기준 (Acceptance Criteria)

다음을 측정 가능한 수준으로 모두 만족해야 한다:

1. **AC-1 (docs-pretty 단일 실행)**: brainstorming/designing-direction/writing-plans 세 스킬 모두, 사용자 승인 전에는 docs-pretty가 호출되지 않는다. 사용자 승인 후 docs-pretty가 정확히 1회 호출된다. 사용자가 수정을 요청하면 다시 raw 단계로 돌아가고, 최종 승인 시점까지 docs-pretty는 다시 호출되지 않는다.
2. **AC-2 (Before/After 블록 가시화)**: 구현계획서의 모든 task가 기존 코드를 수정하는 경우, "원본" 블록과 "수정 후" 블록이 쌍으로 나타난다. 신규 파일 작성 task는 "수정 후" 블록만 나타나고 "원본" 블록은 없다.
3. **AC-3 (code-pretty 흐름 위치)**: writing-plans 흐름에서 verifying-spec → code-pretty → docs-pretty → change-history 순서로 호출된다. 검증 실패 시 code-pretty는 호출되지 않는다.
4. **AC-4 (code-pretty 대상 한정)**: code-pretty가 처리한 자국은 오직 "수정 후" 코드블록 안에서만 발견된다. "원본" 블록, 산문, 표는 변경되지 않는다.
5. **AC-5 (code-pretty 안전장치 출력)**: code-pretty 실행 후 사용자에게 노출되는 결과에 변경 라인 diff 요약이 포함된다.
6. **AC-6 (금지 작업 미실행)**: 의도적으로 "매직 넘버 추출 가능", "중첩 if 평탄화 가능"인 코드를 입력으로 줘도 code-pretty는 그 변환을 수행하지 않는다.
7. **AC-7 (1% 의심 룰)**: 동일 inline 헬퍼처럼 "중복" 후보지만 호출 컨텍스트가 미묘하게 다른 경우, code-pretty는 통합하지 않고 그대로 둔다.
8. **AC-8 (스킬 등록)**: `code-pretty` 스킬이 `skills/code-pretty/SKILL.md`로 존재하고, `writing-plans` 스킬이 적절한 시점에 이를 호출하도록 명세돼 있다.

---

## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-09 15:44] [요구사항-수정]
- **id**: CH-20260509-001
- **이유**: 신규 피처 brainstorming 결과 (Socratic 모드)
- **무엇이**: 구현플랜개선-requirements.md 전체 (배경 / 적용 범위 / 핵심 결정 1~3 / 새로운 흐름 / 우려·해결 / 범위 밖 / 수용 기준 AC-1~8)
- **영향범위**: 없음 (최초 생성)

### [2026-05-09 16:53] [요구사항-수정]
- **id**: CH-20260509-014
- **이유**: tech-design 단계에서 사용자가 "이미 이쁜 코드 강제 변경" 우려 추가 제기 → cascade
- **무엇이**: §우려·해결 표 (5번째 행 추가)
- **영향범위**: tech-design.md §5 D6, §6 R7, §7 F5 (이미 반영됨)
- **연관 항목**: CH-20260509-002 (개발방향)
