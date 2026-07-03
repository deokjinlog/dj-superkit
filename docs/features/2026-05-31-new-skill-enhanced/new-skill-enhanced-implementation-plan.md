---
commit_policy: per-task
---

# 구현계획서: new-skill-enhanced

> **상위 문서**: `new-skill-enhanced-requirements.md` (PRD) + `new-skill-enhanced-tech-design.md` (개발방향). 이 문서는 그 설계를 task-by-task 로 실행하는 계획입니다.

## 1. 개요

skill 빌더 3종 고도화. 마커 파일(`.dj-superkit-skill.json`)을 출처 표식으로 도입하고, 생성 스코프(프로젝트/전체)를 분기하며, 조회·삭제를 dj-superkit 출처로 제한한다.

실행 모드: **메인 인라인** (instruction-only 마크다운 편집, 테스트 경계 없음 — 병렬 byte-copy 보조 에이전트보다 안전). 각 task 종료 시 변경이력 1건 + per-task commit.

## 2. 위험 코드 지점 (R-N → 위치 매핑)

| R-N | 위치 | mitigation (코드 주석 / 안내문) |
|---|---|---|
| R1 (마커 위조) | `commands/list-skills.md`, `commands/remove-skill.md` 판별부 | 마커는 신뢰 신호일 뿐 보안 경계 아님 — 안내문에 명시. RISK 주석 불필요(문서) |
| R2 (cwd≠프로젝트루트) | `commands/list-skills.md`, `commands/remove-skill.md` 스캔부 | 보고에 스캔한 실제 경로 명시 |
| R3 (마커 없는 기존 skill 누락) | 세 command 안내문 | "마커 있는 것만 대상" + 수동 정리 안내 |
| R4 (slug 양쪽 중복) | `commands/remove-skill.md` | 스코프 플래그 요구/prose 확인 |
| R5 (frontmatter description 파싱) | `commands/list-skills.md` | grep fallback "(설명 없음)" |

instruction-only 마크다운이라 코드 RISK 주석(`# ⚠️ RISK`) 대상 아님 — 위험은 안내문 표현으로 흡수.

## 3. Task 분해

### Task 1 — `commands/new-skill.md`: 스코프 분기 + 마커 작성
- **Files**: `commands/new-skill.md`
- **Model**: sonnet (한국어 산문 다중 섹션 수정)
- **변경 내용**:
  1. frontmatter `argument-hint` 에 `[--project|--global]` 추가, description 에 "프로젝트/전체 선택" 반영
  2. § 2 입력 파싱: `--project` / `--global` 플래그 인식 추가
  3. 신규 § "스코프 결정" 단계: 플래그 있으면 그대로, 없으면 prose 질문("프로젝트 `.claude/skills/` / 전체 `~/.claude/skills/` 어디에 만들까요?") 1회 후 확정. 조용한 기본값 없음.
  4. § 5 Write 분기: 경로를 `<SKILL_BASE>` 로 일반화 (`~/.claude/skills/` 또는 `<project-root>/.claude/skills/`)
  5. § 5-4 신규 (정상 Write) + § 5-3 (force) 에 **마커 파일 작성 step 추가**: `<SKILL_BASE>/<slug>/.dj-superkit-skill.json` 에 `{"generated_by":"dj-superkit:new-skill","scope":"<project|global>","created":"<ISO ts>"}` Write
  6. § 6 성공 보고에 생성 스코프 + 경로 명시
- **TDD/검증**: dogfood 시나리오 생성-프로젝트/전체/질문 (§5). grep: `grep -F '.dj-superkit-skill.json' commands/new-skill.md` ≥ 1, `grep -F -- '--project' commands/new-skill.md` ≥ 1
- **변경이력**: [코드-수정] (task: Task 1)

### Task 2 — `commands/remove-skill.md`: 마커 검사 + 프로젝트 스코프
- **Files**: `commands/remove-skill.md`
- **Model**: sonnet
- **변경 내용**:
  1. frontmatter `argument-hint` 에 `[--project|--global]` 추가, description 에 "dj-superkit 가 만든 것만" 반영
  2. § 2 입력 파싱: `--project`/`--global` 플래그 추가
  3. § 3 존재 검증: 탐색을 **프로젝트(`<cwd>/.claude/skills/<slug>/`) → 전체(`~/.claude/skills/<slug>/`)** 양쪽으로. 양쪽 동시 존재 시 스코프 플래그 요구(미지정 시 prose 확인)
  4. **신규 § 4-0 마커 검사 (분기 실행 맨 앞)**: 대상 디렉토리에 `.dj-superkit-skill.json` 부재 시 **무조건 차단**(--force 로도 우회 X) + 안내(`/list-skills` 로 대상 확인). 신규 § 5-5 차단 보고 양식
  5. 기존 safe-rename/force/dry-run 분기는 마커 존재 시에만 진입
  6. § 6 금지에 "마커 없는 skill 삭제 금지" 추가
- **TDD/검증**: dogfood 삭제-허용/차단/차단-force/모호 (§5). grep: `grep -F '.dj-superkit-skill.json' commands/remove-skill.md` ≥ 1
- **변경이력**: [코드-수정] (task: Task 2)

### Task 3 — `commands/list-skills.md`: 신규 조회 명령
- **Files**: `commands/list-skills.md` (신규)
- **Model**: sonnet
- **변경 내용**: frontmatter(description: "/list-skills 명시 호출 시 발동. dj-superkit 가 만든 skill 만 조회") + 본문:
  1. 스캔: `<cwd>/.claude/skills/*/` + `~/.claude/skills/*/`
  2. 필터: `.dj-superkit-skill.json` 존재하는 디렉토리만
  3. 각 SKILL.md frontmatter description 1줄 추출 (실패 시 "(설명 없음)")
  4. 출력: `프로젝트 (<cwd>)` 그룹 + `전체 (글로벌)` 그룹, 각 `<slug> — <description>`
  5. 둘 다 비면 "dj-superkit 가 만든 skill 이 없습니다" 안내
  6. 스캔 경로 명시 (R2) + 마커 신뢰 신호 안내 (R1/R3)
  7. § 금지: 다른 프로젝트 스캔 X, skill 로 변환 X
- **TDD/검증**: dogfood 조회/조회-필터 (§5). grep: `test -f commands/list-skills.md`, `test ! -d skills/list-skills`
- **변경이력**: [코드-수정] (task: Task 3)

### Task 4 — `CLAUDE.md`: 결합 메모
- **Files**: `CLAUDE.md`
- **Model**: sonnet
- **변경 내용**: 기존 `/new-skill 빌더 결합` + `/remove-skill 빌더 결합` 섹션에 **v2.7+ 분기** 추가 (스코프 분기 + 마커 + 양쪽 탐색) + **신규 `## /list-skills 빌더 결합 (v2.7+)`** 섹션 (적용 범위 / 핵심 룰 / 회귀 패턴 / catch grep / 영향 범위)
- **TDD/검증**: `grep -cF '/list-skills 빌더 결합 (v2.7+)' CLAUDE.md` ≥ 1
- **변경이력**: [코드-수정] (task: Task 4)

### Task 5 — 6 manifest 버전 bump
- **Files**: `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`, `package.json`
- **Model**: haiku (mechanical — 단, 인라인 실행이라 메인이 직접)
- **변경 내용**: 각 파일 dj-superkit `"version": "2.6.2"` → `"2.7.0"` (plugin.json 의 중첩 upstream `5.0.7` 은 손대지 않음)
- **TDD/검증**: `grep -rl '2.7.0' .claude-plugin/ .codex-plugin/ .cursor-plugin/ gemini-extension.json package.json | wc -l` 확인
- **변경이력**: [릴리즈]

## 4. 수용 기준 (PRD AC 매핑)

- **AC-1** (스코프 질문 + 마커): Task 1 — dogfood 생성-프로젝트/전체/질문 PASS
- **AC-2** (마커 있는 것만 조회 + 라벨): Task 3 — dogfood 조회/조회-필터 PASS
- **AC-3** (마커 없으면 차단): Task 2 — dogfood 삭제-차단/차단-force PASS

## 5. 실행 순서

T1 → T2 → T3 (서로 독립, 같은 마커 규약 공유) → T4 (3 command 확정 후 결합 메모) → T5 (마지막 릴리즈 bump). 인라인 직렬 실행, 각 task 후 commit.

---
## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-31 21:55] [구현계획서-수정]
- **id**: CH-20260531-003
- **이유**: 신규 피처 writing-plans 결과 (tech-design 의 task 분해)
- **무엇이**: new-skill-enhanced-implementation-plan.md 전체 (Task 1..5, §2 위험 매핑, §4 AC 매핑)
- **영향범위**: commands/new-skill.md, commands/remove-skill.md, commands/list-skills.md, CLAUDE.md, 6 manifest
- **연관 항목**: CH-20260531-002

### [2026-05-31 22:05] [코드-수정] (batch: tasks 1..5)
- **id**: CH-20260531-004
- **이유**: new-skill-enhanced 구현 완료 — skill 빌더 3종에 스코프 분기 + 출처 표식 마커(`.dj-superkit-skill.json`) 도입
- **무엇이**: commands/new-skill.md, commands/remove-skill.md, commands/list-skills.md (신규), CLAUDE.md, 6 manifest
- **영향범위**: 사용자 환경의 `<project-root>/.claude/skills/` 및 `~/.claude/skills/`. 다른 skill/scripts/hooks 영향 0
- **위험 카테고리**: none (instruction-only 마크다운 — 코드 RISK 주석 대상 아님, R1~R5 는 안내문으로 흡수)
- **task별 세부 (5건)**:
  - Task 1: `commands/new-skill.md` — `--project`/`--global` 플래그 + § 2.5 스코프 결정 + `<SKILL_BASE>` 일반화 + § 5 마커 작성 (none) — commit: `c1d590e`
  - Task 2: `commands/remove-skill.md` — 양쪽 스코프 탐색 + § 4-0 마커 차단 게이트 + § 4-0' 모호 + § 5-5 차단 보고 (none) — commit: `f0275e9`
  - Task 3: `commands/list-skills.md` (신규) — 두 스코프 스캔 + 마커 필터 + 스코프 라벨 + 프로젝트 경로 (none) — commit: `47ac821`
  - Task 4: `CLAUDE.md` — new-skill-enhanced 결합 메모 + 회귀 catch grep (none) — commit: `6ba2dd8`
  - Task 5: 6 manifest — 2.6.2 → 2.7.0 (none) — commit: `5abe01d`
- **변경 전/후 코드**: 생략 — `git show <SHA>` 로 조회
- **연관 항목**: CH-20260531-003

### [2026-05-31 22:05] [릴리즈]
- **id**: CH-20260531-005
- **이유**: new-skill-enhanced 피처 완료 — v2.7.0 버전 bump
- **무엇이**: v2.7.0 — 6 manifest 동기화 (marketplace/plugin/codex/cursor/gemini/package)
- **연관 commit**: `5abe01d`
