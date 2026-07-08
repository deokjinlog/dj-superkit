---
name: learning-notes
description: Use when the user asks to capture, organize, or save what they just learned as a durable study note — natural-language triggers like "이거 학습 정리해줘", "방금 배운 거 학습노트로 남겨줘", "이 내용 정리해서 저장해줘", "학습 정리해줘". Turns either the current conversation OR a pointed source (code/doc/URL) into a hybrid-structured Korean study doc (개요 → 핵심 개념 → 헷갈렸던 점 Q&A → 도식/비유 → 한 줄 요약) saved under docs/learning/<date>-<주요내용-슬러그>/, plus a readable HTML companion. This is PERSONAL KNOWLEDGE CAPTURE — NOT feature-development requirements (that is brainstorming/tech-design). Do NOT trigger on plain summarization answers where the user did not ask to save a note.
---

# 학습노트 (learning-notes)

배운 내용을 **나중에 봐도 이해되는 문서**로 정리해 `docs/learning/` 에 durable 하게 보관한다. 대화창에만 남으면 compact·새 세션에서 사라지는 지식을, 사람이 다시 볼 수 있는 형태로 남기는 개인 지식 관리 도구다.

## 언제 발동하나 (auto-trigger)

사용자가 **방금 학습·이해한 내용을 정리해서 저장해 달라**고 명시할 때. 예:

- "이거 학습 정리해줘" / "방금 배운 거 정리해줘"
- "이 내용 학습노트로 남겨줘" / "정리해서 저장해줘"
- 특정 자료를 가리키며 "이 코드/문서 학습 정리해줘"

**발동 안 함** (중요 — 오발동 방지):

- 기능 개발 요구사항 정리 → `brainstorming` 이 담당
- 저장 요청 없는 **단순 요약 답변** (그냥 "설명해줘")
- 코드 리뷰 / 디버깅 / 구현

애매하면 발동하지 말 것. "학습 내용을 문서로 남겨라" 는 **명시 의도** 가 있을 때만.

## 입력 판별 (두 종류 지원)

요청 맥락으로 판별한다:

- **대화 기반** — "지금까지 대화 정리해줘" 류 → 현재까지 대화에서 학습 내용 추출
- **지정 자료 기반** — 파일/URL/코드를 가리킴 → 그 자료를 읽어 학습 정리
- **섞임 OK** — 소스 읽으며 대화한 경우 둘 다 반영

## 절차

### 1. 주제 & 슬러그 확정

- 학습 내용의 **주요 주제** 를 한 줄로 뽑아 슬러그화 — **알아보기 좋게**
- 폴더: `docs/learning/<YYYY-MM-DD>-<주요내용-슬러그>/`
  - 예: `docs/learning/2026-07-08-claude-code-도구-파이프라인/`
- 파일: `<주요내용-슬러그>.md`
- **폴더/파일명 자체가 "날짜 + 주요내용" 을 담아** 스캔만으로 파악 가능하게 (별도 INDEX 파일 X)

### 2. 하이브리드 구조로 `.md` 작성

다음 뼈대로 작성 (주제에 맞게 가감 — 고정 틀 아님):

1. **개요** — 뭘 배웠고 왜 배웠나 (2~3줄)
2. **핵심 개념** — 배운 개념들을 카드/섹션으로 (체계 잡기)
3. **헷갈렸던 점 Q&A** — 내가 막혔던 질문 + 답 (미래의 나에게)
4. **도식/비유** — 복잡한 건 그림·표·비유로 (이해 보조)
5. **한 줄 요약** — 복습용 핵심 압축
6. (선택) **출처/참고** — 소스 `파일:라인`, 링크 등

> 핵심: **"개념(체계) + Q&A(내가 막힌 지점)" 둘 다** 잡아 나중에 봤을 때 이해되게.

### 3. HTML 사본 생성

- `generating-html` 과 **동일한 방식** 으로 `<슬러그>.html` 사본 생성 (self-contained, 보기 좋은 시각화)
- `.md` 의미를 1:1 보존한 사람 전용 사본. `.md` 가 source-of-truth
- HTML 사본은 프로젝트 컨벤션대로 gitignore 가능 (`.md` 는 커밋)

### 4. 위치 안내

- 저장 경로 + HTML 위치를 한 줄로 안내. 끝.

## 원칙 / 범위 밖

- **정리·보관만** — 복습 알림·스페이스드 리피티션 X, 검색 엔진·태그 시스템 X
- **앞으로 배우는 것** — 과거 대화 소급 일괄 역생성 X
- **개인 로컬 지식 관리** — 다국어·공유·게시 X

## Anti-Patterns

| Wrong | Right |
|---|---|
| 저장 요청 없는데 요약만 했는데 발동 | 명시적 "학습 정리/저장" 의도일 때만 |
| 기능 개발 요구사항인데 발동 | 그건 `brainstorming`. 학습노트는 지식 캡처 |
| 폴더/파일명을 무의미하게 (note-1) | "날짜 + 주요내용" 으로 스캔 가능하게 |
| 개념만 나열, 내가 헷갈린 건 안 남김 | 하이브리드 — Q&A 로 막힌 지점도 남김 |
| `.html` 을 source-of-truth 로 | `.md` 가 원본, `.html` 은 사람용 사본 |

## Related Skills

- `generating-html` — HTML 사본 생성 엔진 (재활용)
