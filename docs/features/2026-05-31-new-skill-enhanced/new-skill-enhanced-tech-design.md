# 개발방향: new-skill-enhanced

> **상위 문서**: `new-skill-enhanced-requirements.md` (PRD). 이 문서는 그 PRD 의 FR-1..FR-4 를 어떻게 구현할지 기술 설계만 담습니다. 다음 단계는 `writing-plans` (`/write-plan`) — 이 설계를 bite-sized TDD task 로 분해합니다.

## 1. 아키텍처 개요

세 빌더 모두 기존과 동일하게 **instruction-only 슬래시 명령**(bash 호출 최소, Read/LS/Write/Bash 도구만)으로 유지한다. 신규 helper 스크립트나 중앙 레지스트리를 도입하지 않는다 (D-T4 단순성 — 빌더 latency 보존, 사용자 PC 에 상태 파일 누적 X).

- `commands/new-skill.md` — (수정) 스코프 분기 + 출처 표식 부여
- `commands/remove-skill.md` — (수정) 출처 표식 검증 + 프로젝트 스코프 탐색
- `commands/list-skills.md` — (신규) 출처 표식 있는 skill 조회

빌더가 만든 skill 인지의 판별은 **각 skill 디렉토리 안의 마커 파일 존재 여부**로 한다 (§3 데이터 모델). 이렇게 하면 조회·삭제 양쪽이 동일한 deterministic 검사(파일 존재)만으로 판별 가능하고, 중앙 상태가 desync 될 일이 없다.

## 2. 영향 컴포넌트

| 컴포넌트 | 변경 | 내용 |
|---|---|---|
| `commands/new-skill.md` | 수정 | 입력 파싱에 `--project`/`--global` 플래그 추가, 스코프 미지정 시 prose 질문, Write 경로를 스코프 따라 분기, 생성 시 마커 파일 작성 |
| `commands/remove-skill.md` | 수정 | 탐색을 프로젝트 + 전체 양쪽으로, 마커 파일 부재 시 무조건 차단(§4-2 신규 분기), 보고 양식 보강 |
| `commands/list-skills.md` | 신규 | 두 스코프 스캔 + 마커 필터 + 스코프 라벨 + 프로젝트 경로 표시 |
| `CLAUDE.md` | 수정 | 기존 `/new-skill`·`/remove-skill` 결합 메모에 v2.7+ 분기 추가 + 신규 `/list-skills` 결합 메모 |
| 6 manifest | 수정 | 버전 bump (2.6.2 → 2.7.0) — `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`, `package.json` |

비-목표: `skills/` 아래에는 아무것도 추가하지 않는다 (빌더는 command 라는 기존 룰 유지 — skill 로 만들면 자동 발동 사고 위험).

## 3. 데이터 모델 — 출처 표식 (마커 파일)

FR-4 의 "dj-superkit 출처 표식" 을 구현하는 핵심 결정. **`/new-skill` 이 skill 생성 시 그 디렉토리 안에 마커 파일을 함께 쓴다.**

- **경로**: `<skill-dir>/.dj-superkit-skill.json`
- **내용**:
  ```json
  {
    "generated_by": "dj-superkit:new-skill",
    "scope": "project",
    "created": "2026-05-31T21:50:00"
  }
  ```
- **판별 규칙**: 어떤 skill 이 "dj-superkit 가 만든 것" ⇔ 그 디렉토리에 `.dj-superkit-skill.json` 파일이 존재한다. (내용 파싱은 `scope` 표시·`created` 표시용 부가 정보일 뿐, 판별은 파일 존재로 충분.)

이 마커는 `/list-skills` 필터 기준이자 `/remove-skill` 차단 기준이 된다.

## 4. 외부 인터페이스

해당 없음 — 외부 API / 네트워크 / 서드파티 의존 없음. 모든 동작은 로컬 파일시스템(`~/.claude/skills/`, `<project-root>/.claude/skills/`) 내에서 완결.

## 5. 핵심 결정 + 대안 비교

### D1 — 출처 표식 메커니즘 (채택: 마커 파일)

| 대안 | 설명 | 장 | 단 |
|---|---|---|---|
| **A. 마커 파일** ✅ 채택 | `<skill-dir>/.dj-superkit-skill.json` | 디렉토리와 함께 이동/복사됨(self-contained), `test -f` 만으로 deterministic 판별(파싱 불필요), 중앙 상태 desync 없음, scope/created 메타 저장 가능 | skill 디렉토리에 dotfile 1개 추가 |
| B. SKILL.md frontmatter 필드 | `metadata.generated_by` 등 | 파일 1개로 끝 | skill 로더가 unknown 키에 warn 가능성, 판별 시 YAML 파싱 필요 |
| C. 중앙 manifest | `~/.claude/skills/.dj-superkit-registry.json` 에 slug 목록 | 한곳에서 전체 파악 | 사용자가 수동 삭제 시 stale entry → desync, 프로젝트별 분리 어려움(FR-2 "다른 프로젝트 안 보임" 와 충돌) |

**채택 이유**: A 는 판별이 파일 존재 검사 1회로 끝나 조회/삭제가 동일 로직을 공유하고, 마커가 skill 과 운명을 같이 해 중앙 desync 위험이 없다. C 의 중앙 레지스트리는 FR-2 의 "다른 프로젝트 것은 안 보임" 요구와 정면 충돌(중앙에 모으면 다 보임)하고, B 는 로더 호환성 리스크가 있다.

### D2 — 생성 스코프 분기 (채택: 플래그 + 미지정 시 prose 질문)

- `/new-skill --project "..."` → `<project-root>/.claude/skills/<slug>/`
- `/new-skill --global "..."` → `~/.claude/skills/<slug>/`
- 플래그 없으면 prose 로 "프로젝트 / 전체 어디에 만들까요?" 1회 질문 후 진행 (조용한 기본값 없음 — FR-1).
- **프로젝트 루트 판정**: 현재 작업 디렉토리(cwd)의 `.claude/skills/`. `.claude/` 없으면 생성.
- 대안(항상 prose 질문, 플래그 없음)은 반복 호출 시 마찰이라 기각. 대안(기본값을 프로젝트로 고정)은 FR-1 "조용한 기본값 없음" 위배라 기각.

### D3 — `/list-skills` 조회 범위·형식 (채택: 두 스코프 그룹 출력)

- 스캔 대상: `<cwd>/.claude/skills/*/` + `~/.claude/skills/*/` 두 곳만.
- 필터: 각 디렉토리에 `.dj-superkit-skill.json` 존재하는 것만.
- 출력: 스코프별 그룹.
  - `프로젝트 (<project-root 경로>)`: `<slug>` — `<description>`
  - `전체 (글로벌)`: `<slug>` — `<description>`
  - `<description>` 은 각 SKILL.md frontmatter 의 description 1줄에서 가져옴.
- 다른 프로젝트의 `.claude/skills/` 는 스캔하지 않으므로 자연히 안 보임 (FR-2, 중앙 레지스트리 불필요).
- 둘 다 비면 "dj-superkit 가 만든 skill 이 없습니다" 안내.

### D4 — `/remove-skill` 차단 판정·스코프 (채택: 마커 검사 + 양쪽 탐색)

- 탐색 순서: `<cwd>/.claude/skills/<slug>/` → `~/.claude/skills/<slug>/`.
- 양쪽에 동시 존재 시: `--project`/`--global` 플래그로 대상 지정 요구 (미지정 시 prose 로 어느 쪽인지 확인). 모호한 자동 삭제 방지.
- 대상 디렉토리 확정 후 `.dj-superkit-skill.json` 존재 검사:
  - **부재 → 무조건 차단** + 안내 (`--force` 로도 우회 X, FR-3).
  - **존재 → 기존 동작** (기본 safe-rename / `--force` hard-delete / `--dry-run`).
- 디렉토리 자체가 없으면 기존 부재 abort 유지.

### D5 — 빌더 형태 (채택: instruction-only command 유지)

신규 `/list-skills` 도 기존 두 빌더와 동일한 instruction-only command 로 만든다. skill 로 만들지 않는다 (자동 발동 사고 방지 — 기존 META-BUILDER 룰 답습).

## 6. 예비 위험

| ID | 위험 | 완화 |
|---|---|---|
| R1 | 사용자가 수동으로 `.dj-superkit-skill.json` 을 복사하면 비-dj-superkit skill 이 dj-superkit 산으로 오인됨 | 낮은 빈도·사용자 의도적 행위라 수용. 마커는 신뢰 신호일 뿐 보안 경계 아님 |
| R2 | cwd 가 프로젝트 루트가 아닐 때 `.claude/skills/` 해석이 어긋남 | Claude Code 관례(cwd=프로젝트 루트) 따름. list/remove 보고에 스캔한 실제 경로 명시 |
| R3 | 옛 `/new-skill` 로 만든 마커 없는 글로벌 skill 이 신규 조회/삭제에서 누락 (범위 밖 마이그레이션) | 의도된 동작. `/list-skills`·`/remove-skill` 안내문에 "마커 있는 것만 대상" 명시 + 수동 정리 안내 |
| R4 | 같은 slug 가 프로젝트·전체 양쪽 존재 시 삭제 모호 | D4 — 양쪽 존재 시 스코프 플래그 요구/확인 |
| R5 | `/list-skills` description 표시를 위해 SKILL.md frontmatter 파싱 필요 | description 한 줄 grep 으로 충분. 실패 시 "(설명 없음)" fallback |

## 7. 테스트 전략 (dogfood 시나리오)

instruction-only command 라 단위 테스트보다 dogfood 시나리오로 검증한다 (기존 new-skill.md §8 패턴 답습).

| 시나리오 | 입력 | 기대 |
|---|---|---|
| 생성-프로젝트 | `/new-skill --project "..."` | `<root>/.claude/skills/<slug>/` 에 SKILL.md + `.dj-superkit-skill.json` 생성 |
| 생성-전체 | `/new-skill --global "..."` | `~/.claude/skills/<slug>/` 에 동일 |
| 생성-질문 | `/new-skill "..."` (플래그 X) | "프로젝트/전체?" prose 질문 후 진행 |
| 조회 | `/list-skills` | 마커 있는 것만 두 스코프 그룹으로, 프로젝트 항목엔 경로 표시 |
| 조회-필터 | 마커 없는 글로벌 skill 존재 시 `/list-skills` | 그 skill 은 목록에 안 뜸 |
| 삭제-허용 | 마커 있는 skill `/remove-skill <slug>` | 기존 safe-rename 동작 |
| 삭제-차단 | 마커 없는 skill `/remove-skill <slug>` | 변경 없이 차단 + 안내 |
| 삭제-차단-force | 마커 없는 skill `/remove-skill <slug> --force` | `--force` 로도 차단 (FR-3) |
| 삭제-모호 | 프로젝트·전체 동시 존재 `/remove-skill <slug>` | 스코프 지정 요구 |

---
## 변경이력
<!-- change-history skill auto-appends entries here, oldest first -->

### [2026-05-31 21:52] [개발방향-수정]
- **id**: CH-20260531-002
- **이유**: 신규 피처 tech-design 결과 (요구사항 FR-1..FR-4 의 기술 설계)
- **무엇이**: new-skill-enhanced-tech-design.md 전체 (D1 마커 파일 채택, D2 스코프 분기, D3 조회, D4 삭제 차단, §3 데이터 모델)
- **영향범위**: commands/new-skill.md, commands/remove-skill.md (수정), commands/list-skills.md (신규), CLAUDE.md, 6 manifest
- **연관 항목**: CH-20260531-001
