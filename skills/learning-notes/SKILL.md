---
name: learning-notes
description: Use when the user asks to capture, organize, extend, or prune what they learned as a durable study note — natural-language triggers like "이거 학습 정리해줘", "방금 배운 거 학습노트로 남겨줘", "이 노트에 이어줘", "그 부분 빼줘". Turns a conversation OR a pointed source (code/doc/URL) into a hybrid-structured Korean study doc (개요 → 핵심 개념 → 헷갈렸던 점 Q&A → 도식 → 한 줄 요약) under docs/learning/<date>-<주요내용-슬러그>/, plus a readable HTML companion. Same-chapter follow-ups APPEND to the existing note (one growing doc per topic, not fragments); supports partial/whole deletion. PERSONAL KNOWLEDGE CAPTURE — NOT feature-development requirements (that is brainstorming). Do NOT trigger on plain summarization where the user did not ask to save a note.
---

# 학습노트 (learning-notes)

배운 내용을 **나중에 봐도 이해되는 문서**로 정리해 `docs/learning/` 에 durable 하게 보관한다. 반복 학습으로 조각나지 않게 **주제당 하나로 자라는** 문서를 유지하고, 필요없는 부분은 쉽게 지운다. 개인 지식 관리 도구.

## 언제 발동하나 (auto-trigger)

사용자가 **학습 내용을 문서로 남기거나, 기존 노트에 이어붙이거나, 일부를 지워달라**고 명시할 때. 예:

- "이거 학습 정리해줘" / "방금 배운 거 정리해줘" / "이 코드 학습 정리해줘"
- "이 노트에 이어줘" / "여기 추가해줘" (누적)
- "그 Q&A 빼줘" / "이 학습노트 지워줘" (삭제)

**발동 안 함** (오발동 방지): 기능 개발 요구사항(→ brainstorming), 저장 요청 없는 단순 설명/요약, 코드 리뷰·디버깅·구현. 애매하면 발동 X.

## 입력 판별 (두 종류)

- **대화 기반** — "지금까지 대화 정리해줘" → 현재까지 대화에서 학습 추출
- **지정 자료 기반** — 파일/URL/코드를 가리킴 → 그 자료를 읽어 정리
- 섞임 OK (소스 읽으며 대화한 경우 둘 다 반영)

## 주제 범위 (granularity) — 챕터 레벨

주제는 **챕터 레벨**로 잡는다. 너무 넓지도 좁지도 않게:

| | 예시 |
|---|---|
| ✅ 딱 맞음 (챕터) | "도구 실행 파이프라인", "알림 시스템", "탐색 전략" |
| ❌ 너무 넓음 (도메인 전체) | "Claude Code 전체" |
| ❌ 너무 좁음 (질문 하나) | "validateInput 함수" |

같은 챕터에 대한 후속 질문(validateInput / classifier / 병렬·직렬 등)은 **새 파일이 아니라 그 챕터 노트에 누적**한다.

## 누적(append) vs 신규 판단

1. 발동 시 `docs/learning/` 의 **기존 노트 목록(폴더명)** 을 먼저 확인
2. 현재 학습이 **기존 노트의 주제를 확장**(같은 챕터/카테고리)하면 → 그 노트에 **append**
3. **명확히 다른 챕터**면 → 신규 노트
4. **애매하면 딱 한 번** 물어봄: "기존 '<주제>' 노트에 이어붙일까요, 새로 만들까요?"

→ 목표: 반복 학습이 **주제당 문서 하나로 자라게** (4조각 X, 1개 성장 O). HTML 목차로 한눈에 훑기.

## 절차

### 1. 노트 결정 (신규 or 누적)

- 챕터 레벨로 주제 판정 → 위 "누적 vs 신규" 규칙 적용
- **신규**: `docs/learning/<YYYY-MM-DD>-<주요내용-슬러그>/<슬러그>.md` 생성
  - 폴더/파일명 자체가 "날짜 + 주요내용" 을 담아 스캔만으로 파악 (별도 INDEX X)
- **누적**: 기존 노트 파일을 열어 이어씀

### 2. 하이브리드 구조로 작성/누적

뼈대 (주제에 맞게 가감):

1. **개요** — 뭘 배웠고 왜 (누적 시 갱신)
2. **핵심 개념** — 개념을 카드/섹션으로 (누적 시 블록 추가)
3. **헷갈렸던 점 Q&A** — `### Q. ...` / `A. ...` **블록 단위** (누적 시 블록 추가, 독립적이라 개별 삭제 쉬움)
4. **도식/비유** — 복잡한 건 그림·표·비유로
5. **한 줄 요약** — 복습용 핵심 (누적 시 갱신)
6. (선택) **출처/참고** — 소스 `파일:라인`, 링크

> 핵심: "개념(체계) + Q&A(내가 막힌 지점)" 둘 다 잡아 나중에 봤을 때 이해되게. **Q&A 는 반드시 블록 단위**로 (추가·삭제 용이).

### 3. HTML 사본 (재)생성

- `generating-html` 과 동일한 방식으로 `<슬러그>.html` 생성
- **신규·누적·삭제·정리 — `.md` 가 바뀔 때마다 HTML 을 다시 뽑는다** (항상 최신 상태 유지)
- self-contained, 의미 1:1 보존, `.md` 가 source-of-truth. HTML 은 gitignore 가능

### 4. 위치 안내

- 저장 경로 + HTML 위치 한 줄. 끝.

## 삭제 / 정리 (prune)

사용자가 관리 편의로 요청할 때:

- **부분 삭제** — "그 <X> Q&A/섹션 빼줘" → 해당 블록만 제거 → HTML 재생성
- **전체 삭제** — "이 학습노트 지워줘" → 해당 `docs/learning/<...>/` 폴더 통째 삭제
- **중복 정리** — "이 노트 정리해줘" → 겹치거나 낡은 부분 다듬기 (의미 보존, 재구조화 X) → HTML 재생성

## 원칙 / 범위 밖

- **정리·보관·성장·삭제만** — 복습 알림·스페이스드 리피티션 X, 검색 엔진·태그 시스템 X
- **앞으로 배우는 것** — 과거 대화 소급 일괄 역생성 X
- **개인 로컬 지식 관리** — 다국어·공유·게시 X

## Anti-Patterns

| Wrong | Right |
|---|---|
| 저장 요청 없는데 요약만 했는데 발동 | 명시적 "학습 정리/저장/이어줘/빼줘" 의도일 때만 |
| 같은 챕터 후속인데 새 파일 생성 (조각남) | 기존 노트에 **append** |
| 주제를 "Claude Code 전체" 로 너무 넓게 | 챕터 레벨 ("도구 파이프라인") |
| 주제를 "validateInput 하나" 로 너무 좁게 | 챕터 레벨 (그 안에 누적) |
| Q&A 를 한 덩어리 산문으로 | `### Q./A.` **블록 단위** (개별 삭제 위해) |
| `.md` 만 고치고 HTML 그대로 둠 | 변경 시 HTML **재생성** |
| 기능 개발 요구사항인데 발동 | 그건 `brainstorming`. 학습노트는 지식 캡처 |

## Related Skills

- `generating-html` — HTML 사본 생성 엔진 (재활용)
- `change-propagation` — 부분 삭제·정리 시 참고 가능한 국소 편집 패턴
