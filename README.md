<p align="center">
  <img src="https://raw.githubusercontent.com/deokjinlog/intent-locked-workflow/main/assets/banner.svg" alt="intent-locked-workflow — 기획 의도를 고정하고, 그 위에서만 코드가 자란다" width="100%">
</p>

<div align="center">

### 기획 의도를 고정하고, 그 위에서만 코드가 자란다

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1.7.0-7c3aed?style=flat-square&labelColor=0d1117">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-Plugin-a78bfa?style=flat-square&labelColor=0d1117">
  <img alt="Skills" src="https://img.shields.io/badge/skills-27-06b6d4?style=flat-square&labelColor=0d1117">
  <img alt="Upstream" src="https://img.shields.io/badge/superpowers-5.0.7%20계승-f97316?style=flat-square&labelColor=0d1117">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-22c55e?style=flat-square&labelColor=0d1117">
</p>

<sub>upstream <a href="https://github.com/obra/superpowers">superpowers</a> 5.0.7 (MIT, Jesse Vincent) 의 프로덕션 안전성 확장</sub>

<br/>
<br/>

<sub>
  <a href="#어떻게-쓰나">어떻게 쓰나</a>
  &nbsp;·&nbsp;
  <a href="#뭐가-남나--md-세-장">뭐가 남나</a>
  &nbsp;·&nbsp;
  <a href="#왜-이렇게-하나">왜</a>
  &nbsp;·&nbsp;
  <a href="#설치">설치</a>
  &nbsp;·&nbsp;
  <a href="docs/세-문서-읽는-법.md">더 깊이</a>
</sub>

</div>

<br/>

> ## 코드보다 먼저, 의도를 맞춘다.
>
> AI한테 *"출금 기능 만들어줘"* 하면 **바로 코드를 짭니다.**
> 잘못 알아들었어도 **다 만들고 나서야** 압니다.
>
> 이 도구는 **코드 앞에 문서 세 장**을 세웁니다.
> 당신은 그 문서를 보고 **"맞다 / 아니다"만** 답합니다.

---

## 어떻게 쓰나

**한 줄만 칩니다.**

```
/brainstorming 출금기능
```

그 다음부터는 **안 칩니다.** 네 단계가 알아서 이어져요. 당신은 **묻는 말에 답하고, 문서마다 "맞다/아니다"만** 하면 됩니다.

<br/>

### 갈림길 하나 — **기획서가 있나요?**

가장 먼저 이걸 묻습니다. 답에 따라 **완전히 다르게** 갑니다.

| | **기획서가 있다** <br/><sub>PPT · PDF · 워드 · 붙여넣기</sub> | **아직 머릿속에만 있다** |
|---|---|---|
| **고를 모드** | **PRD** *(기본)* | **소크라테스** |
| **도구가 하는 일** | 그 기획서를 **읽고 분해** | AI와 **대화하며 만들어감** |
| **나오는 것** | `FR-1` `FR-2` … **번호 붙은 계약** | 번호 없는 **자유 산문** |
| **원조** | intent-locked 가 더한 것 | **upstream superpowers 원본** 그대로 |

> **번호가 왜 중요하냐면** — `FR-5` 라는 번호가 ② 의 매핑표(`FR-4,5,6 → csv_parser.py`)와 ③ 의 task 에 박힙니다. 나중에 *"FR-5 바꿔줘"* 하면 그 번호를 따라 **어디까지 번지는지 짚어냅니다.** 소크라테스를 고르면 번호가 없어서 그 추적이 약해져요.
> **기획서가 있으면 PRD 를 고르세요.** 기본값이 PRD 인 이유입니다.

<br/>

### 기획서는 **그냥 던지면** 됩니다

포맷을 안 가립니다. 아래는 지어낸 예시가 아니라 **실제로 그렇게 만든 프로젝트의 ① 맨 윗줄**입니다:

> **입력 출처**: `DartWeave_발표_최종완성본1.pptx` **30장**. 30장 전체는 이미 동작하는 시스템 전체를 다루므로, 그중 **첫 수직 슬라이스**만 이 PRD 범위로 잡음.

발표자료 30장 하나가 → **`FR` 10개 · `NFR` 4개 · `AC` 7개 · 범위밖 10건** 으로 분해됐습니다.
원본 `.pptx` 는 gitignore 로 막습니다 — **기획서는 로컬에, 뽑아낸 요구사항만 git 에.**

<br/>

### ★ 그 다음부턴 **아무도 원본을 다시 안 봅니다**

```
기획서 (PPT 30장)
     │   ← ① 만 읽는다
     ▼
① requirements    정본. 여기서 "이건 범위 밖" 을 잘라낸다
     ▼
② 개발방향        기획서 안 봄. ① 만 봄
     ▼
③ 구현계획서      기획서 안 봄. ② 만 봄
     ▼
④ 코드            기획서 안 봄. ③ 만 봄
```

**이게 "의도 잠금" 입니다.** 만약 ③ 이 기획서를 다시 보면 — ① 에서 *"이건 범위 밖"* 이라고 잘라낸 걸 무시하고 만들어버려요. 위 DartWeave 도 **10건을 범위밖으로 잘라냈고**, 그래서 ②③④ 가 그것들을 안 건드립니다.

<br/>

### 전체 흐름

```
당신 │ /brainstorming 출금기능
  AI │ 기획서 있어요? → PRD / 소크라테스
     │ (이름 · 카테고리 · 물어볼 것 목록 확인 — 몇 개 더 묻습니다)
     │ …질문에 답하다 보면…
     │ 📄 출금기능-requirements.md    ← 뭘 만들 건지 적었습니다. 맞나요?
당신 │ ㅇㅋ                                             ← 게이트 ①
  AI │ 📄 출금기능-tech-design.md     ← 어떻게 만들지 정했습니다. 맞나요?
당신 │ ㅇㅋ                                             ← 게이트 ②
  AI │ 📄 출금기능-implementation-plan.md  ← 순서와 코드까지 짰습니다. 맞나요?
당신 │ ㅇㅋ                                             ← 게이트 ③
  AI │ 💻 코드 작성 → 테스트 → 커밋
```

**"아니다" 라고 하면** 그 자리에서 고칩니다. 코드는 아직 한 줄도 안 짰으니까요. **게이트는 사람만 엽니다.**

> 스킬이 27개지만 **당신이 치는 건 `/brainstorming` 하나**입니다. 나머지 26개는 도구가 알아서 부릅니다.

<br/>

> **⚠️ 스킬과 명령은 이름 규칙이 다릅니다** — 처음에 꼭 걸리는 지점이에요.
>
> | | 예 | 그냥 치면 | 앞에 플러그인명을 붙이면 |
> |---|---|---|---|
> | **스킬** | `/brainstorming` | **✅ 됩니다** | ✅ 됩니다 |
> | **명령** | `/audit-risk` | **❌ `Unknown command`** | ✅ `/intent-locked-workflow:audit-risk` |
>
> **명령은 `<플러그인명>:<명령명>` 이 필요합니다.** 그래서 이 README 의 명령은 전부 `/intent-locked-workflow:` 로 시작해요. 슬래시만 치면 자동완성이 뜨니 거기서 고르는 게 제일 편합니다.

---

## 뭐가 남나 — `.md` 세 장

**이게 이 도구의 전부입니다.** 폴더 하나에 문서 세 장이 쌓여요.

```
docs/features/2026-05-31-출금기능/
├── 출금기능-requirements.md          ①  뭘 만드나   (66줄)
├── 출금기능-tech-design.md           ②  어떻게 만드나 (127줄)
└── 출금기능-implementation-plan.md   ③  어떤 순서로 + 실제 코드 (123줄)
```

아래는 **이 저장소가 자기 자신을 개발한 실제 문서**에서 그대로 가져온 겁니다. 지어낸 예시가 아니에요 → [`2026-05-31-new-skill-enhanced/`](docs/features/2026-05-31-new-skill-enhanced/) *(당시엔 도구 이름이 `dj-superkit` 였습니다)*

<br/>

### ① `-requirements.md` — **뭘 만드나**

기술 얘기는 **일부러 뺍니다.** 여기서 의도를 잠급니다.

```markdown
## 3. 기능 요구사항 (FR)

- **FR-1 — 생성 스코프 분기 (`/new-skill`)**
  - 생성 위치를 프로젝트와 전체 중에서 고른다.
  - 스코프가 명시되지 않으면 매번 사용자에게 묻는다.
    조용히 적용되는 기본값은 없다.
```

`FR-1` 처럼 **번호를 붙입니다.** 나중에 "이거 바꿔줘" 할 때 **번호로 추적**하려고요.

<br/>

### ② `-tech-design.md` — **어떻게 만드나 (+ 왜)**

**"왜 이 방법인가"가 여기 남습니다.** 6개월 뒤 "왜 이렇게 짰지?" 할 때 볼 곳이에요.

```markdown
## 5. 핵심 결정 + 대안 비교

### D1 — 출처 표식 메커니즘 (채택: 마커 파일)

| 대안 | 장 | 단 |
|---|---|---|
| **A. 마커 파일** ✅ 채택 | 파일 존재 검사만으로 판별, 중앙 desync 없음 | dotfile 1개 추가 |
| B. frontmatter 필드 | 파일 1개로 끝 | 로더가 unknown 키에 warn 가능성 |
| C. 중앙 manifest | 한곳에서 전체 파악 | 사용자가 수동 삭제 시 stale → desync |

**채택 이유**: C 는 FR-2 의 "다른 프로젝트 것은 안 보임" 요구와 정면 충돌…
```

**탈락한 대안과 그 이유**까지 남습니다. 이게 없으면 6개월 뒤 누가 "C 가 더 낫지 않나?" 하며 되돌립니다.

<br/>

### ③ `-implementation-plan.md` — **어떤 순서로 + 실제 코드**

**이건 사람용이 아닙니다.** AI가 그대로 집행하는 문서라 **파일·변경·검증 명령**이 다 박혀요.

```markdown
### Task 1 — `commands/new-skill.md`: 스코프 분기 + 마커 작성
- **Files**: `commands/new-skill.md`          ← 정확한 파일
- **Model**: sonnet (한국어 산문 다중 섹션 수정)   ← 어느 모델로 시킬지까지
- **변경 내용**:
  1. frontmatter `argument-hint` 에 `[--project|--global]` 추가
  ...
  5. 마커 파일 작성 step 추가: `<SKILL_BASE>/<slug>/.dj-superkit-skill.json` 에
     `{"generated_by":"dj-superkit:new-skill","scope":"<project|global>",...}` Write
- **TDD/검증**: grep: `grep -F '.dj-superkit-skill.json' commands/new-skill.md` ≥ 1
                                              ↑ 검증 명령과 기대 결과까지
```

*"적절히 처리"* 같은 말은 **금지**입니다. 그렇게 쓰면 AI가 알아서 지어내고, 설계와 다른 게 나오니까요.

> 위는 마크다운을 고치는 task 라 검증이 `grep` 입니다. **코드를 만지는 task 면 테스트 코드와 구현 코드가 통째로** 들어가고, 검증은 `Run: pytest …` / `Expected: PASS` 가 됩니다 → [그런 계획서 실물](docs/features/2026-05-10-v2.0.0-implementer-byte-copy/v2.0.0-implementer-byte-copy-implementation-plan.md)

<br/>

### ④ 실행 — 문서를 안 만듭니다

코드는 소스 트리로 가고, **③ 하단에 흔적만** 남습니다. 실물이 이렇게 쌓여 있어요:

```markdown
### [2026-05-31 21:55] [구현계획서-수정]
- **id**: CH-20260531-003
- **이유**: 신규 피처 writing-plans 결과 (tech-design 의 task 분해)
- **영향범위**: commands/new-skill.md, commands/remove-skill.md, CLAUDE.md, 6 manifest
- **연관 항목**: CH-20260531-002          ← 앞 문서와 연결

### [2026-05-31 22:05] [코드-수정] (batch: tasks 1..5)
- **id**: CH-20260531-004
- **이유**: 구현 완료 — 빌더 3종에 스코프 분기 + 출처 표식 마커 도입
```

**계획(003) → 코드(004) → 릴리즈** 가 한 파일에 이어집니다. `연관 항목` 이 앞 문서를 가리켜서, **어디서 시작된 변경인지 거꾸로 따라갈 수 있어요.**

> **`CH-` 번호는 당신이 안 붙입니다.** 17줄짜리 스크립트가 폴더를 훑어서 자동으로 매겨요.
> **`FR`·`AC` 도 AI가 씁니다.** 당신은 읽고 "맞다/아니다"만 하면 됩니다.

---

## 왜 이렇게 하나

세 장을 나눈 이유는 **읽는 사람이 다르기 때문**입니다.

| | 성격 | 누가 읽나 |
|---|---|---|
| ① 요구사항 | **계약** — 뭘 하고, 뭘 **안** 하나 | 사람 · 기획자 |
| ② 개발방향 | **도면** — 왜 이 방법인가 | 사람 · 리뷰어 |
| ③ 구현계획서 | **공정표 + 부품** | **AI가 그대로 집행** |

그래서 **③만 유독 깁니다.** ①② 는 사람이 *판단하려고* 읽으니 짧고, ③ 은 기계가 *실행하려고* 읽으니 코드가 통째로 들어가요.

<br/>

### 나중에 바뀌면 — 아래가 따라옵니다

`FR-5 한도 바꿔줘` 라고 하면, 어디까지 번지는지 **표로 정해져 있습니다.**

| 바꾼 곳 | 자동으로 따라오는 것 |
|---|---|
| ① 요구사항 | ② + ③ + 코드 |
| ② 개발방향 | ③ + 코드 |
| ③ 구현계획서 | 코드 |
| 코드 (직접 수정) | ③ 하단 변경이력만 *(역방향 기록)* |

> **코드 수정은 위로 안 올라갑니다.** 이유는 안 바뀌었고 구현만 옮겼으니까요.

**그리고 몰래 안 고칩니다.** 먼저 목록을 보여주고 **승인을 받습니다:**

```
영향 매트릭스 적용 결과 — 함께 갱신될 항목:
1. 요구사항 §3 FR-3 (직접 변경)
2. 개발방향 §6 위험 (한도 증가에 따른 잔액 검증 강도 재평가)
3. 구현계획서 Task 4 (한도 검증 로직)
4. 코드 src/wallet/service.py:withdraw() (한도 상수)

진행 / 부분 진행(번호 선택) / 취소 중 선택해주세요.
```

**부분 진행**도 됩니다 — 번호를 골라서 3번만 고칠 수 있어요.

> 📖 **[세 문서 읽는 법](docs/세-문서-읽는-법.md)** — `FR`·`AC`·`CH` 가 정확히 뭔지, 변경이력이 왜 *"이전 버전과의 diff"* 가 아닌지, 왜 ③만 길어지는지.

<details>
<summary><b>그 밖에 챙기는 것들</b></summary>

<br/>

- **게이트는 사람만 엽니다** — 자잘한 건 알아서, 위험한 결정만 물어봐요. 자리에 없어도 OS 알람이 잡아줍니다.
- **`.html` 사본** — `.md` 와 내용이 1:1인 사본을 같이 남깁니다. AI는 `.md` 를, 사람은 `.html` 을 봐요. 기획자가 코드를 몰라도 게이트에서 검토하라고요. *(내려받아 더블클릭하면 열립니다 — 외부 의존 0)* → [실물 보기](docs/features/2026-05-24-v2.5-no-ask-flag/v2.5-no-ask-flag-requirements.html)
- **`# RISK` 주석** — 위험한 코드 줄에 카테고리(`side-effect` · `breaking` · `race`)와 이유를 남깁니다.
- **[`docs/features/`](docs/features/) 에 기능 24개** — 전부 이 워크플로로 만든 실제 기록입니다.

</details>

---

## 설치

Claude Code 안에서:

```
/plugin marketplace add deokjinlog/intent-locked-workflow
/plugin install intent-locked-workflow@intent-locked-workflow
```

**세션을 한 번 재시작**한 뒤 `/brainstorming 출금기능` 을 치면 첫 게이트가 열립니다.

<details>
<summary><b>이미 설치했다면 — 업데이트</b></summary>

<br/>

**마켓플레이스를 먼저 당기고, 그 다음 플러그인을 올립니다. 둘 다 해야 해요.**
마켓플레이스가 옛 버전에 묶여 있으면 플러그인도 안 올라갑니다.

```bash
claude plugin marketplace update intent-locked-workflow
claude plugin update intent-locked-workflow@intent-locked-workflow
```

**적용은 세션을 재시작해야 됩니다.** 안 하면 옛 버전이 계속 로드돼서, 슬래시 메뉴에 예전 스킬 이름이 그대로 보여요. 지금 뭐가 깔려 있는지는 `claude plugin list` 로 확인합니다.

</details>

<details>
<summary><b>스킬 27개 (알 필요 없지만, 궁금하다면)</b></summary>

<br/>

**당신이 치는 건 `/brainstorming` 하나입니다.** 아래 26개는 도구가 알아서 부릅니다.

| 그룹 | 스킬 |
|---|---|
| **워크플로 코어 (4)** | brainstorming · tech-design · writing-plans · executing-plans |
| **자동 흐름 (4)** | auto-brainstorming · auto-tech-design · auto-writing-plans · auto-executing-plans |
| **upstream 원본 (3)** | og-brainstorming · og-writing-plans · og-executing-plans |
| **문서 · 시각화 (3)** | generating-html · code-pretty · change-history |
| **검증 · 거버넌스 (4)** | verifying-spec · verification-before-completion · change-propagation · risk-annotation |
| **서브에이전트 (2)** | subagent-driven · subagent-driven-development |
| **테스트 · 디버깅 (2)** | test-driven-development · systematic-debugging |
| **리뷰 · 마무리 (3)** | requesting-code-review · receiving-code-review · finishing-a-development-branch |
| **API 테스트 (1)** | api-auto-testing |
| **메타 (1)** | using-superpowers |

명령어도 있어요 — `/intent-locked-workflow:audit-risk`(배포 전 보안 감사), `/intent-locked-workflow:fast-tasks`(잡일 묶어 처리), `/intent-locked-workflow:sync-html`, `/intent-locked-workflow:api-test`, 빌더 3종(`/intent-locked-workflow:list-skills` · `/intent-locked-workflow:new-skill` · `/intent-locked-workflow:remove-skill`).

**스킬이 아니라 명령인 것들**이 있죠 — 빌더 3종은 **일부러** 명령입니다. 스킬은 설명문만 맞으면 저절로 발동하는데, *"랄프한테 넘길까"* 라고 말만 해도 워크트리가 생기고 파일이 지워지면 안 되니까요. **명시 호출만** 받습니다.

</details>

---

## superpowers 계승

[superpowers](https://github.com/obra/superpowers) 5.0.7 (MIT, Jesse Vincent) 위에 프로덕션 안전성을 얹은 파생 프로젝트입니다.
원본 흐름 그대로가 필요하면 `/intent-locked-workflow:og-brainstorm` · `/intent-locked-workflow:og-write-plan` · `/intent-locked-workflow:og-execute-plan` 로 쓸 수 있어요.

---

<div align="center">
<br/>
<sub><b>코드보다 먼저, 의도를 맞춘다.</b></sub>
</div>
