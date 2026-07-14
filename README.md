<div align="center">

# dj-superkit

### AI는 빠르게, 코드는 안전하게.

아이디어에서 코드까지 **4단계** — 매 단계, 한 번 더 확인합니다.
문서와 코드가 따로 놀지 않도록, AI가 멋대로 진행하지 않도록.

<br/>

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1.2.2-7c3aed?style=for-the-badge&labelColor=0d1117">
  <img alt="Upstream" src="https://img.shields.io/badge/upstream-superpowers%205.0.7-f97316?style=for-the-badge&labelColor=0d1117">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge&labelColor=0d1117">
  <img alt="Language" src="https://img.shields.io/badge/lang-한국어-3b82f6?style=for-the-badge&labelColor=0d1117">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-Plugin-a78bfa?style=for-the-badge&labelColor=0d1117">
</p>

<p>
  <img alt="Commands" src="https://img.shields.io/badge/commands-12-06b6d4?style=flat-square&labelColor=0d1117">
  <img alt="Skills" src="https://img.shields.io/badge/skills-27-06b6d4?style=flat-square&labelColor=0d1117">
  <img alt="Zero deps" src="https://img.shields.io/badge/dependencies-zero-22c55e?style=flat-square&labelColor=0d1117">
</p>

<sub>upstream <a href="https://github.com/obra/superpowers">superpowers</a> 5.0.7 (MIT, Jesse Vincent) 의 프로덕션 안전성 확장</sub>

</div>

<br/>

---

## 왜 만들었나

> AI 코딩 에이전트는 빠릅니다. 그 빠름이 오히려 **검토 · 통제 · 맥락**을 무너뜨립니다.

리뷰해 줄 동료 없이 혼자 AI 로 프로덕션 코드를 짜다 보면, 세 가지가 반복돼요.

<table>
<tr>
<td width="33%" valign="top">

#### 🔍 검토가 벅차다

AI 가 코드를 쏟아내는데, 뭘 왜 그렇게 했는지 따라가기 어려워요.

**→ 단계마다 검토용 문서를 자동으로.** 사람이 읽을 `.md` + 보기 좋은 `.html` 사본. 사람은 `.html` 만 훑고, AI 는 `.md` 만 읽어요.

</td>
<td width="33%" valign="top">

#### 🛑 AI 가 멋대로 간다

되묻지 않고 코드를 갈아엎거나, 중요한 결정을 몰래 내려요.

**→ 단계마다 확인 게이트.** 자잘한 건 알아서, **위험한 결정만 사람에게** 물어봐요 — 자리에 없어도 OS 알람으로 catch.

</td>
<td width="33%" valign="top">

#### 🔗 문서와 코드가 따로 논다

요구사항은 계속 바뀌는데, 설계 · 계획 · 코드가 어긋나요.

**→ 하나 바꾸면 아래로 자동 전파.** 위험한 코드엔 `# RISK` 주석, 문서엔 "왜 · 언제 · 무엇이" 변경이력이 자동으로 쌓여요.

</td>
</tr>
</table>

<div align="center">

**아이디어에서 코드까지를 `기획 → 설계 → 계획 → 실행` 4 단계로 나누고,**
**매 단계에 _검토 문서 · 확인 게이트 · 자동 기록_ 을 끼워 넣은 것 — 그게 dj-superkit 입니다.**

<sub>👤 리뷰해 줄 동료 없이 AI 로 실제 코드를 짜는 <b>1인 개발자</b>를 위해 — 속도와 안전을 혼자 다 챙겨야 하는 사람.</sub>

</div>

<br/>

---

## 1 분이면 시작합니다

**1. 설치** — Claude Code 안에서:

```
/plugin marketplace add deokjinlog/dj-superkit
/plugin install dj-superkit@dj-superkit
```

세션 한 번 재시작하면 끝.

**2. 첫 피처 만들기** — 슬래시 4 줄로:

```
/brainstorming 사용자 잔액 출금 기능
/tech-design
/writing-plans
/executing-plans
```

각 단계가 끝날 때마다 AI 가 한 번씩 물어봐요. 답변에 따라 다음 단계로.

<sub>산출물은 <code>docs/features/2026-05-23-사용자-잔액-출금/</code> 폴더에 3 개 <code>.md</code> + 보기 좋은 <code>.html</code> 사본까지 알아서 만들어 둡니다.</sub>

<br/>

---

## 핵심 — 아이디어에서 코드까지, 4 단계

`기획 → 설계 → 계획 → 실행`. 각 단계 사이 **확인 게이트** 에서 AI 가 한 번 멈춥니다. 다음 단계로 자동으로 넘어가지 않아요.

```mermaid
flowchart LR
    classDef cmd fill:#7c3aed,stroke:#a78bfa,color:#fff,stroke-width:2px
    classDef doc fill:#1e293b,stroke:#06b6d4,color:#e2e8f0,stroke-width:2px
    classDef gate fill:#dc2626,stroke:#fca5a5,color:#fff,stroke-width:2px
    classDef out fill:#15803d,stroke:#86efac,color:#fff,stroke-width:2px

    A["/brainstorming"]:::cmd --> B[요구사항.md]:::doc
    B --> G1{확인 게이트}:::gate
    G1 --> C["/tech-design"]:::cmd
    C --> D[기술설계.md]:::doc
    D --> G2{확인 게이트}:::gate
    G2 --> E["/writing-plans"]:::cmd
    E --> F[구현계획.md]:::doc
    F --> G3{확인 게이트}:::gate
    G3 --> H["/executing-plans"]:::cmd
    H --> I[코드 + 변경이력 + 위험 주석]:::out
```

그리고 매 단계는 **세 가지 얼굴** 을 남깁니다 — AI 가 읽는 진짜 문서, 사람이 보는 사본, 코드에 붙는 위험 표시.

<table>
<tr>
<td width="33%" valign="top" align="center">

#### `.md` — 진짜 문서

요구사항 / 기술설계 / 구현계획 각자 1 개씩.

문서 하단에 **누가 / 언제 / 왜 바꿨는지** 자동으로 쌓여요.

AI 는 항상 이 `.md` 만 봐요.

</td>
<td width="33%" valign="top" align="center">

#### `.html` — 사람용 사본

같은 내용을 다크 모드로 보기 좋게.

차트 / 다이어그램 / 카드를 알아서 골라 넣어요.

**구현계획에서 코드 변경은 초록(+) / 빨강(−)** 으로 한눈에.

</td>
<td width="33%" valign="top" align="center">

#### 코드 — 위험 주석

```python
# RISK(side-effect):
#   외부 결제 호출
#   by: /writing-plans T5
```

3 가지 카테고리로 자동 부착.

PR 리뷰 시 `grep "# RISK"` 한 줄로 catch.

</td>
</tr>
</table>

<sub>각 조각이 어떻게 생겼는지는 아래 <a href="#더-깊이-알고-싶다면">더 깊이</a> 에서 펼쳐 볼 수 있어요.</sub>

<br/>

---

## 파워 기능

4 단계 루프 위에, 실무에서 진짜 시간을 줄여 주는 기능들이 얹혀 있어요.

### ① 서브에이전트 모드 — 계획서 그대로 복붙 + 자동 병렬

> *"피처가 커서 task 가 7-8 개인데, 하나씩 하면 시간 너무 걸려요"*
> *"근데 AI 가 코드 새로 짓는 건 더 무서워요. 계획 그대로만 했으면 좋겠어요"*

**복붙해요.** 구현계획.md 의 task 마다 `**원본**` → `**수정본**` 변경이 적혀 있어요. 일꾼 AI 는 그 변경을 **한 글자도 안 틀리게 복사** 해서 코드에 적용합니다. 자기 머리로 새 코드를 짓지 않고, 의심스러우면 즉시 멈춰요.

**동시에 굴려요.** 7 개 task 를 무작정 7 개 동시에 돌리지 않고, 먼저 task 사이 의존관계를 분석해 **wave 단위** 로 묶어 단계적으로 처리합니다.

```mermaid
flowchart LR
    classDef wave fill:#1e293b,stroke:#06b6d4,color:#e2e8f0,stroke-width:2px

    subgraph W1["Wave 1 — 의존 없음, 동시"]
        direction TB
        T1["T1: User.balance 컬럼"]:::wave
        T2["T2: 마이그레이션"]:::wave
    end

    subgraph W2["Wave 2 — Wave 1 끝나야"]
        direction TB
        T3["T3: withdraw API"]:::wave
    end

    subgraph W3["Wave 3 — Wave 2 끝나야"]
        direction TB
        T4["T4: 라우트 등록"]:::wave
        T5["T5: 단위 테스트"]:::wave
    end

    W1 --> W2 --> W3
```

**막히면 먼저 복구해요.** 일꾼이 막히면 조정자가 자동으로 붙어 복구를 먼저 시도하고, 그래도 안 될 때만 사람에게 넘어옵니다.

```mermaid
flowchart LR
    classDef main fill:#7c3aed,stroke:#a78bfa,color:#fff
    classDef sub fill:#1e293b,stroke:#06b6d4,color:#e2e8f0
    classDef block fill:#dc2626,stroke:#fca5a5,color:#fff

    P[구현계획.md]:::sub --> I["일꾼 (haiku)<br/>복붙 + 의존 분석"]:::sub
    I -->|성공| M[메인 AI]:::main
    I -.-> B(("막힘")):::block
    B -.->|자동 호출| R["조정자 (sonnet)<br/>복구 시도"]:::sub
    R -.->|복구| I
    R -.->|실패| M
```

**그래서 뭐가 좋아요?** — 7 task 가 3 wave 로 묶이면 체감 시간이 **⅓ ~ ½** 로 줄고, 계획서가 기준이라 **AI 멋대로 코드 짓는 사고 0**, 의존 있는 건 순서대로 처리돼 race / 깨짐이 차단돼요. 일꾼은 haiku(저렴), 조정자는 sonnet(똑똑) 이라 **비용 · 속도 · 안전을 동시에** 챙깁니다.

<br/>

### ② 요구사항 하나 바꾸면, 3 개 문서가 같이 따라옵니다

> *"기획에서 갑자기 FR 하나 추가됐어요. 기술설계랑 구현계획도 다 다시 봐야 해요. 코드는 어디까지 영향 있는지도 모르겠어요"*

스펙은 살아있는 동안 계속 바뀝니다. 그때마다 3 개 문서를 손으로 정합 맞추는 건 사람의 일이 아니에요. **dj-superkit 는 그걸 자동으로**:

```mermaid
flowchart LR
    classDef in fill:#7c3aed,stroke:#a78bfa,color:#fff
    classDef sub fill:#1e293b,stroke:#06b6d4,color:#e2e8f0
    classDef out fill:#15803d,stroke:#86efac,color:#fff

    A["요구사항.md<br/>FR-3 신규 추가"]:::in --> B[자동 영향 분석]:::sub
    B --> C{"기술설계<br/>영향?"}:::sub
    B --> D{"구현계획<br/>영향?"}:::sub
    B --> E{"이미 작성된<br/>코드 영향?"}:::sub
    C -->|YES| F["§4 갱신 제안"]:::sub
    D -->|YES| G["T7~T9 갱신 제안"]:::sub
    E -->|YES| H["해당 코드 위치 표시"]:::sub
    F --> I[사용자 확인]:::sub
    G --> I
    H --> I
    I --> J["3 개 md 동기화 + .html 재생성"]:::out
```

요구사항을 수정하면 기술설계 · 구현계획 **둘 다** 영향 분석이 돌고, 이미 작성된 코드가 있다면 **어디서 깨질지** 위치까지 표시해요. 사용자 확인 후 3 개 md 가 한 번에 정렬되고, 각 문서 footer 에는 **"왜 · 언제 · 무엇이 바뀌었는지"** 가 자동으로 기록됩니다. 덕분에 기획자가 새 요구사항을 던져도 3 개 문서가 따로 놀지 않고, 한 달 뒤 본인이 다시 봐도 맥락이 살아있어요. 깜박하고 한 문서만 고쳐 어긋나는 사고를 차단합니다.

<br/>

### 그 외 — 자동 흐름 · 잡일 묶기 · 배포 전 감사

**`/auto-brainstorming` — 한 번에 끝까지 자동 진행.** 친숙한 영역 / 작은 ~ 중간 피처일 때. clarifying Q 1~5 개만 답하면 PRD → 기술설계 → 구현계획 → 실행까지 4 단계를 자동으로 돌리되, 변경이력 · 위험 주석 · 3 개 MD 산출물은 그대로 챙기고 마지막에 서브에이전트 병렬 실행까지 이어져요.

```
/auto-brainstorming 사용자 잔액 출금 기능
```

**`/fast-tasks` — 잡일 묶어 처리.** PRD 부터 만들기엔 작은데 흔적은 남기고 싶은 일 (자잘한 fix · 의존성 bump · 같은 파일 작은 refactor). 기획/설계 단계는 건너뛰되 변경이력 · 위험 주석 · 확인 게이트는 그대로, footer 는 마지막에 한 번에 정리해요.

```
/fast-tasks
- 결제 API 응답 v1 → v2 호환 처리
- 로그인 폼 placeholder 한국어로
- requirements.txt requests 버전 bump
```

**`/audit-risk` — 배포 직전 한 번 더 훑기.** 5 명의 AI 가 동시에 코드를 다른 각도(비용 · 개인정보 · 민감 로직 · AI 위험 · 거버넌스)로 훑고, 한 명이 모아 HTML 보고서를 만들어 줍니다. 코드는 **건드리지 않아요**. Snyk · Bandit 같은 외부 도구를 대체가 아니라 **보완** 합니다.

```mermaid
flowchart TD
    classDef main fill:#7c3aed,stroke:#a78bfa,color:#fff
    classDef sub fill:#1e293b,stroke:#06b6d4,color:#e2e8f0
    classDef out fill:#15803d,stroke:#86efac,color:#fff

    M[메인 AI]:::main
    A["API 비용 추정"]:::sub
    B["개인정보 노출"]:::sub
    C["민감 로직 검토"]:::sub
    D["AI 자동화 위험"]:::sub
    E["거버넌스 점검"]:::sub
    F["보고서 생성"]:::sub
    R["docs/audit/...html"]:::out

    M --> A & B & C & D & E
    A & B & C & D & E --> F
    F --> R
```

<br/>

---

## 레퍼런스 — 뭐라고 부르면 뭐가 뜨나

dj-superkit 는 **두 가지 방식**으로 움직여요.

- **스킬** — 말로 부르면 알아서 떠요 (`/스킬이름` 슬래시도 가능). 워크플로 4 단계가 전부 스킬이에요.
- **명령어** — 슬래시로만. 자동으로는 안 떠요 (일부러).

#### 스킬 — 이렇게 말하면 떠요

| 스킬 | 자연어 예시 | 결과물 |
|---|---|---|
| `brainstorming` | "새 기능 만들자" · "이거 기획하자" | 요구사항.md |
| `tech-design` | "기술 설계하자" · "어떻게 구현할지 짜줘" | 기술설계.md |
| `writing-plans` | "구현 계획 짜줘" · "plan 작성하자" | 구현계획.md |
| `executing-plans` | "이 계획대로 구현해줘" | 코드 + 변경이력 + 위험 주석 |
| `auto-brainstorming` | "자동으로 끝까지 해줘" | 4 단계 자동 진행 |
| `systematic-debugging` | "이 버그 왜 이러지" · "테스트 자꾸 실패" | 체계적 디버깅 |
| `requesting-code-review` | "이 코드 리뷰해줘" | 리뷰 |
| `finishing-a-development-branch` | "개발 끝났어 마무리하자" | 테스트 게이트 + 정리 |

> 정확한 주문이 아니라 **의도**로 떠요. "이 버그 왜 이러지"든 "테스트 자꾸 실패한다"든 뜻만 통하면 발동. 100% 확실히 하려면 슬래시 `/systematic-debugging` 처럼 직접 부르면 돼요.

#### 명령어 — 슬래시로만 (자동 발동 X)

| 명령 | 하는 일 |
|---|---|
| `/list-skills` · `/new-skill` · `/remove-skill` | 스킬 조회 / 생성 / 정리 |
| `/audit-risk` | 5+1 AI 가 보안·거버넌스 동시 점검 → HTML 보고서 |
| `/api-test` | 구현된 API 자동 테스트 |
| `/fast-tasks` | 잡일 여러 개 묶어 처리 |
| `/sync-html` | `.html` 사본 재생성 |
| `/pretty-md` | `.md` 코드블록 정리 (의미 불변) |
| `/og-brainstorm` · `/og-write-plan` · `/og-execute-plan` | upstream 원본 흐름 |

> 빌더(`/list-skills` · `/new-skill` · `/remove-skill`)가 명령인 이유 — 자동으로 뜨면 실수로 스킬을 만들거나 지울 수 있어서 **일부러 슬래시 전용**으로 뒀어요.

> 워크트리는 Claude Code 내장 `--worktree` 를 사용하세요.

<details>
<summary><b>전체 Skill 27 개 펼쳐 보기</b></summary>

<br/>

**워크플로 코어 (4)** — brainstorming / tech-design / writing-plans / executing-plans

**자동 흐름 (4)** *(v1.1.17+)* — auto-brainstorming / auto-tech-design / auto-writing-plans / auto-executing-plans

**upstream 원본 (3)** — og-brainstorming / og-writing-plans / og-executing-plans

**문서·시각화 (3)** — generating-html / code-pretty / change-history

**검증·거버넌스 (4)** — verifying-spec / verification-before-completion / change-propagation / risk-annotation

**서브에이전트 (2)** — dj-superkit-sub-driven / subagent-driven-development

**테스트·디버깅 (2)** — test-driven-development / systematic-debugging

**리뷰·마무리 (3)** — requesting-code-review / receiving-code-review / finishing-a-development-branch

**API 테스트 (1)** — api-auto-testing

**메타 (1)** — using-superpowers

</details>

<br/>

---

## 더 깊이 알고 싶다면

<details>
<summary><b>3 개의 <code>.md</code> 분리는 왜?</b></summary>

<br/>

한 피처가 한 폴더 안에 세 개의 `.md` 로 나뉘어 있어요.

```
docs/features/2026-05-23-잔액-출금/
├── 잔액-출금-requirements.md      ← /brainstorming
├── 잔액-출금-tech-design.md       ← /tech-design
└── 잔액-출금-implementation-plan.md ← /writing-plans
```

- 날짜는 **생성일** — 작업이 길어져도 폴더명은 안 바뀝니다
- 세 문서가 같은 폴더라 PR 리뷰 한 곳에서 끝
- 각 문서 끝에는 변경이력 footer 가 자동 누적

</details>

<details>
<summary><b>변경이력은 어떻게 생겼나요?</b></summary>

<br/>

```markdown
## 변경이력

### CH-001 [요구사항-추가] 2026-05-23 14:30
- **이유**: 사용자가 출금 한도 추가 요청
- **무엇이**: FR-3 (1 일 출금 한도 100 만원) 신설
- **영향범위**: tech-design §4 / impl-plan T7~T9
- **연관 CH-id**: -
```

- 종류: `[요구사항-추가/수정/삭제]` / `[코드-수정]` / `[검증]` / `[릴리즈]`
- 코드 변경은 commit SHA 만 참조 (문서가 무거워지지 않게)
- 한 작업이 여러 task 로 나뉘어도 **마지막에 한 번에 footer 정리** *(v1.1.7+)*

</details>

<details>
<summary><b>위험 주석 3 종</b></summary>

<br/>

```python
# RISK(side-effect): 외부 결제 호출, 멱등성 미보장 — by /writing-plans T5
def charge(user_id, amount):
    return payment_gateway.charge(user_id, amount)

# RISK(breaking): API v1 응답 구조 변경, v1 클라이언트 깨짐 — by /tech-design §3
def get_balance_v2(user_id) -> dict:
    ...

# RISK(race): 동시 출금 시 잔액 차감 충돌 가능 — by /tech-design §5
def withdraw(user_id, amount):
    balance = db.get_balance(user_id)
    ...
```

| 종류 | 무슨 뜻 |
|---|---|
| `side-effect` | 외부 호출 / DB 쓰기 / 파일 / 로그 |
| `breaking` | API 시그니처 / 응답 / DB 스키마 변경 |
| `race` | 동시성 / 트랜잭션 / 멱등성 |

</details>

<details>
<summary><b><code>.html</code> 사본은 어떻게 만들어지나요?</b></summary>

<br/>

`.md` 가 사용자 리뷰 시점에 들어가면, **백그라운드에서 자동으로** `.html` 이 만들어집니다. 메인 작업은 멈추지 않아요.

- **다크 모드 기본** *(v2.3.4+)* — 깊은 어두운 배경 + 보라/시안 악센트
- **상황에 맞게**: 차트 / 인터랙티브 / 다이어그램 / 카드 (필요하면 사용)
- **구현계획의 코드 변경**: 초록(+) / 빨강(−) 한눈에 비교
- **중요 내용은 펼친 채로** *(v2.3.3+)* — FR / AC 본문은 접지 않음
- `.gitignore` 처리되어 있어요. AI 는 항상 `.md` 만 읽습니다
- `/sync-html` 한 줄로 수동 재생성도 가능

</details>

<details>
<summary><b>확인 게이트 — 어디서 멈추나요?</b></summary>

<br/>

8 곳에서 멈춥니다. 모두 한국어로 묻고, **OS 알람**까지 울려서 자리에 없어도 catch 가능 *(v1.1.10+)*.

| 시점 | 게이트 |
|---|---|
| brainstorm 진입 | PRD / 소크라테스식 |
| 요구사항 확인 | 예 / 아니오 |
| → 기술설계로 | (자동) |
| 기술설계 확인 | 예 / 아니오 |
| → 구현계획으로 | 예 / 아니오 |
| 구현계획 확인 | 예 / 아니오 |
| 실행 방식 | 인라인 / 서브에이전트 |
| 마무리 | 머지 / PR / 그대로 / 폐기 |

**v2.3.5+** — 실행 중에는 사소한 결정 (병렬로 할까? task 묶을까?) 은 자율 진행, **위험한 결정만 사람에게**:
- 실행 모드 변경
- 계획 밖 파일 손대기
- 파괴적 작업 (rm / reset / push --force)
- task 끼리 충돌
- 외부 서비스 호출 (push, PR 생성)
- 약속 안 한 새 의존성

</details>

<br/>

---

## upstream superpowers 와의 관계

[superpowers](https://github.com/obra/superpowers) v5.0.7 (MIT, Jesse Vincent) 을 계승한 파생 프로젝트예요. upstream 의 4 단계 방법론 위에 dj-superkit 가 **프로덕션 안전성**(확인 게이트 · 변경이력 · 위험 주석 · 서브에이전트 병렬 · `.html` 사본 · 보안 감사)을 얹고, 게이트를 한국어로 바꿨습니다. upstream 업데이트는 수동 머지로 따라가요.

**`/og-brainstorm` · `/og-write-plan` · `/og-execute-plan`** — upstream 원본 흐름을 그대로 쓰고 싶을 때. 변경이력·위험 주석·`.html` 사본·검증 게이트가 **안 따라오는** 가벼운 흐름이고, 산출물은 `docs/superpowers/...` 로 분리돼요. 정식 `/brainstorming` 흐름과 **한 피처 안에서 섞지 마세요**.

<br/>

---

## 필요한 도구 (사용자 환경)

| 용도 | 필요한 것 |
|---|---|
| Hook 처리 | `jq` 또는 `python3` (둘 중 하나) |
| Claude Code | 최신 버전 권장 |

> dj-superkit 자체는 **외부 의존성 0**.

<br/>

---

## 버전 마일스톤

버전은 `plugin.json` 의 semver 하나로 관리해요 — 마켓플레이스 배포 버전 · git 태그 · 아래 마일스톤이 모두 같은 축입니다. 지금은 **v1.2.2**.

<details open>
<summary><b>최근 릴리즈</b></summary>

<br/>

| 버전 | 무엇이 바뀌었나요 |
|---|---|
| **v1.2.2** | 헤드라인 **"AI는 빠르게, 코드는 안전하게"** 확정 + 디자인 도구 리브랜딩([design-explosion-30-styles](https://github.com/deokjinlog/design-explosion-30-styles)) 반영 |
| **v1.2.0** | `design-style-explorer` → 별도 플러그인 **[design-explosion-30-styles](https://github.com/deokjinlog/design-explosion-30-styles)** 으로 분리. dj-superkit 은 프로덕션 코드 워크플로에 집중 |
| **v1.1.0** | `devlog` 스킬 제거 + README 재구성(핵심 4단계 루프 우선) + **버전 축 통일** — semver 하나로 정리, 옛 태그 정돈 |
| **v1.0.0** | **정식 버전** — 안정 릴리즈 |
| **v0.26.0** | `design-style-explorer` README 쇼케이스 섹션 |
| **v0.25.0** | 결정 프레임워크 + 인터랙티브 결정 갤러리 *(v0.25.1 갤러리 기본값 = 심플)* |
| **v0.24.0** | 실무 프론트 그라운딩(production-quality) + 개인 실명 금지 |
| **v0.23.0** | `design-style-explorer` **30 스타일** — 실무 다빈도 10 추가 + 사이드바·풀 컴포넌트 |
| **v0.21.0** | **20 스타일 확장** + 콘텐츠 견고성 *(v0.22.0 개성 차별화)* |
| **v0.18.0** | `design-style-explorer` 완성 — 12 스타일 v2 + 병렬 · 린트 · 갤러리 *(v0.19.0 concepts.md)* |
| **v0.15.0** | design-gallery → **스킬 승격** + 12 스타일 + Workflow 병렬 *(v0.16~0.17 품질 레이어 · explorer rename)* |
| **v0.9.0** | 껍데기 워크플로 명령 8개 제거 → **스킬 중심** 정리 |

</details>

<details>
<summary><b>v1.0.0 이전 — 기반 기능</b></summary>

<br/>

정식 v1.0.0 이전, 프로덕션 안전성의 뼈대가 만들어진 시기예요.

- **3-MD 분리** + 변경이력 footer + 위험 주석 3종
- **4 단계 확인 게이트** — 한국어화 + OS 알람 (자리에 없어도 catch)
- **서브에이전트 wave-parallel 모드** — 계획서 그대로 복붙 + 막히면 조정자 자동 복구
- **`/auto-*` 4 개 자동 흐름** — clarifying Q 만 답하면 끝까지
- **`/fast-tasks`** 잡일 묶기 · **`/audit-risk`** 보안·거버넌스 감사
- **`.html` 다크 모드 백그라운드 사본** + `/sync-html`
- **요구사항 자동 전파** — 하나 바꾸면 3 문서 동기화
- **`--no-ask` 모드** · 스킬 빌더 3종(`/list-skills`·`/new-skill`·`/remove-skill`) · 워크트리 머지백/정리

</details>

<br/>

---

<div align="center">

### 라이선스

**MIT** (upstream superpowers 와 동일)

<br/>

<sub>버그 / 제안: <a href="https://github.com/deokjinlog/dj-superkit/issues">GitHub Issues</a></sub>

<br/>

<sub>🎨 디자인 방향 탐색이 필요하면 → <a href="https://github.com/deokjinlog/design-explosion-30-styles">design-explosion-30-styles</a></sub>

<br/>

<sub>프로덕션 Claude Code 워크플로우를 위해</sub>

</div>
