# 요구사항: new-skill-enhanced

> **다음 단계 안내**: 이 문서는 PRD (기획 단계 요구사항만) 입니다. 다음 단계로 `tech-design` skill (또는 `/tech-design` 슬래시) 을 호출해서 `new-skill-enhanced-tech-design.md` (기술 설계서) 를 만드세요. 기술 결정이나 구현 세부사항(특히 "dj-superkit 출처 표식"을 어떻게 구현할지)은 여기 박지 마세요 — 그건 다음 단계에 들어갑니다.

## 1. 배경/목적

dj-superkit 의 skill 빌더 3종(`/new-skill` 생성, 신규 `/list-skills` 조회, `/remove-skill` 삭제)을 고도화한다. 현재 동작에 두 가지 문제가 있다.

- **문제 1 — 생성 위치가 무조건 전체(글로벌)**: 지금 `/new-skill` 은 `~/.claude/skills/` 에만 만든다. 특정 프로젝트에서만 쓸 skill도 전역에 퍼져서, 다른 프로젝트에서도 자동 발동 후보로 떠다니고 관리가 어렵다.
- **문제 2 — 삭제 대상에 제한이 없음**: 지금 `/remove-skill` 은 글로벌 skill 이면 출처와 무관하게 무엇이든 정리한다. dj-superkit 가 만들지 않은 skill(다른 플러그인/사용자가 직접 만든 것)까지 건드릴 수 있어, 의도치 않게 많은 걸 망가뜨릴 위험이 크다.

**목적**: (1) 생성 스코프를 프로젝트/전체로 나누고, (2) dj-superkit 가 만든 skill 만 조회·(3) 삭제하도록 제한해서, 빌더가 만든 skill 의 위치·출처를 명확히 통제한다.

## 2. 사용자 스토리 / 시나리오

해당 없음 — dj-superkit 플러그인 자체의 내부 개발 도구(슬래시 명령)라 외부 사용자 스토리가 없다.

## 3. 기능 요구사항 (FR)

- **FR-1 — 생성 스코프 분기 (`/new-skill`)**
  - `/new-skill` 은 생성 위치를 **프로젝트(`<project-root>/.claude/skills/`)** 와 **전체(`~/.claude/skills/`)** 중에서 고른다.
  - 스코프가 명시되지 않으면 **매번 사용자에게 묻는다** ("프로젝트 / 전체 어디에 만들까요?"). 조용히 적용되는 기본값은 없다.
  - 선택한 위치에 `<slug>/SKILL.md` 를 생성한다. 그 외 생성 로직(입력 파싱, 분해, 충돌/백업, 비밀값 catch 등)은 기존과 동일하게 유지한다.

- **FR-2 — dj-superkit 출처 skill 조회 (신규 `/list-skills`)**
  - 신규 슬래시 명령 `/list-skills` 를 추가한다.
  - **dj-superkit 가 만든 skill 만** 조회한다(출처 표식이 있는 것만). 표식 없는 skill 은 목록에 뜨지 않는다.
  - 조회 범위는 두 곳: **현재 프로젝트의 `.claude/skills/`** 와 **전체(글로벌 `~/.claude/skills/`)**.
  - 각 항목에 **스코프 라벨**(프로젝트 / 전체)을 표시한다. 프로젝트 항목에는 **어느 프로젝트인지(프로젝트 경로 또는 이름)** 도 함께 표시한다.
  - **다른 프로젝트에서 만든 프로젝트-스코프 skill 은 보이지 않는다** (현재 프로젝트 + 전체만). 즉 모든 프로젝트를 가로지르는 중앙 목록은 만들지 않는다.

- **FR-3 — dj-superkit 출처 skill 만 삭제 (`/remove-skill`)**
  - `/remove-skill` 은 **dj-superkit 가 만든 skill 만** 정리할 수 있다.
  - 출처 표식이 없는 skill 삭제 시도 시 **무조건 차단**하고, 안내 메시지를 띄운다(예: "dj-superkit 가 만든 skill 이 아니라 정리할 수 없습니다. `/list-skills` 로 대상을 확인하세요"). `--force` 같은 옵트인으로도 우회되지 않는다.
  - 삭제 대상 탐색은 **프로젝트 + 전체 양쪽 스코프**를 지원한다(`/new-skill` 이 양쪽에 만들 수 있으므로).
  - 출처 표식이 있는 skill 에 대한 기존 동작(기본 safe-rename, `--force` hard-delete, `--dry-run`)은 유지한다.

- **FR-4 — dj-superkit 출처 표식 부여 (`/new-skill`)**
  - `/new-skill` 로 skill 을 생성할 때 **dj-superkit 가 만들었다는 출처 표식**을 함께 남긴다. 이 표식이 FR-2 조회·FR-3 삭제의 판별 기준이 된다.
  - (표식의 구체적 형태 — frontmatter 필드 / 별도 manifest 등 — 는 tech-design 에서 결정한다.)

## 4. 비기능 요구사항 (NFR)

해당 없음 — 사용자가 지정한 별도 비기능 요구가 없다. (기존 빌더의 응답 지연 최소·safe-rename 우선 같은 성질은 FR-3 의 "기존 동작 유지"로 흡수한다.)

## 5. 범위 밖 (Out of Scope)

- **비-dj-superkit skill 강제 삭제 우회** — 출처 표식이 없는 skill 은 `--force` 로도 삭제 불가(FR-3). 우회 옵션을 두지 않는다.
- **기존(고도화 전 생성) skill 마이그레이션** — 옛 `/new-skill` 로 만든 표식 없는 글로벌 skill 에 표식을 자동 부여하지 않는다. 이들은 `/list-skills` 에 안 뜨고 `/remove-skill` 로도 정리 불가하며, 사용자가 수동으로 정리한다.
- **다른 프로젝트의 프로젝트-스코프 skill 조회/삭제** — 현재 프로젝트 + 전체만 다룬다. 모든 프로젝트를 가로지르는 중앙 레지스트리는 만들지 않는다.

## 6. 수용 기준 (Acceptance Criteria)

- **AC-1**: 스코프를 명시하지 않고 `/new-skill` 을 호출하면 "프로젝트 / 전체" 선택 질문이 뜨고, 선택한 위치(`<project-root>/.claude/skills/` 또는 `~/.claude/skills/`)에 `<slug>/SKILL.md` 가 생성된다. 생성된 skill 에는 dj-superkit 출처 표식이 남는다.
- **AC-2**: `/list-skills` 호출 시 dj-superkit 출처 표식이 있는 skill 만, 현재 프로젝트 + 전체 두 곳 기준으로 뜬다. 각 항목에 스코프 라벨이 붙고, 프로젝트 항목에는 프로젝트 경로/이름이 표시된다. 표식 없는 기존 skill 과 다른 프로젝트의 skill 은 뜨지 않는다.
- **AC-3**: `/remove-skill` 로 출처 표식이 있는 skill 은 (프로젝트/전체 무관) 정리된다. 표식이 없는 skill 을 지우려 하면 변경 없이 차단되고 안내 메시지가 뜬다.

---
## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-31 21:45] [요구사항-수정]
- **id**: CH-20260531-001
- **이유**: 신규 피처 brainstorming 결과
- **무엇이**: new-skill-enhanced-requirements.md 전체 (FR-1..FR-4, AC-1..AC-3)
- **영향범위**: 없음 (최초 생성)
