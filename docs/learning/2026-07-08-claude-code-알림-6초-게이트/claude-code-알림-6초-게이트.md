# 학습노트: Claude Code 알림 — AskUserQuestion은 왜 알림이 안 떴나 (6초 idle 게이트)

> 📅 2026-07-08 · 🏷️ Claude Code 내부 / 알림 시스템 · 출처: `claude-code-source-code-full`

## 개요

Windows 토스트 알림을 훅으로 걸었는데 이상한 현상이 있었다 — **작업 완료(Stop)는 항상 뜨는데, AskUserQuestion(질문)은 안 떴다.** 소스코드를 파헤쳐 원인을 찾았더니 **버그가 아니라 설계**였다. 원인(6초 idle 게이트)과 우회법(PreToolUse 훅)을 배운 기록.

## 핵심 개념

### 1. 알림 훅이 발화하는 경로

`Notification` 훅(사용자가 settings.json에 건 것)은 이 사슬로 발화한다:

```
useNotifyAfterTimeout (hook)
   → sendNotification (services/notifier.ts)
      → executeNotificationHooks (utils/hooks.ts)
         → settings.json 의 Notification 훅 실행
```

### 2. 6초 idle 게이트 ← 진짜 원인

`useNotifyAfterTimeout.ts` 에 핵심이 박혀 있다:

```
DEFAULT_INTERACTION_THRESHOLD_MS = 6000        // 6초
shouldNotify = 최근 6초 안에 상호작용 "없을 때만" true
```

- 알림이 뜰지 말지를 **"마지막 키 입력 후 6초 지났나"** 로 판단.
- 키를 누를 때마다 `updateLastInteractionTime()` 로 시각 갱신 (App.tsx).
- 즉 **6초 안에 뭐라도 만지면 알림이 억제**된다 — "사용자가 자리에 있다"고 보는 것.

### 3. Stop 은 왜 항상 뜨나

`Stop`(완료) 훅은 **이 6초 게이트를 안 거친다.** 그래서 무조건 발화 → 항상 보임. 반면 `Notification` 은 게이트를 거쳐서 idle일 때만.

### 4. AskUserQuestion 의 정체

`AskUserQuestion` 은 `AskUserQuestionPermissionRequest` — **권한요청 계열**이다. MCP 서버가 쓰는 `Elicitation`(`elicitationHandler.ts`)과는 **다른 것**. 그 알림은 `Notification` 경로(=6초 게이트)를 타서 억제됐던 것.

## 헷갈렸던 점 Q&A

**Q. 왜 완료는 뜨는데 질문은 안 뜨나?**
A. 완료(Stop)는 게이트 없이 무조건 발화. 질문 알림(Notification)은 6초 idle 게이트가 있어서, 내가 화면 보며 바로 답하면 억제된다.

**Q. AskUserQuestion은 Notification이야, Elicitation이야?**
A. 엄밀히는 **권한요청**. 알림은 Notification 경로로 흐르는데 그 경로에 6초 게이트가 있어 안 떴다. Elicitation은 MCP 전용이라 무관.

**Q. 6초 기다리지 말고 즉시 뜨게 하려면?**
A. 그 이벤트의 **`PreToolUse` 훅 + matcher `AskUserQuestion`** 을 건다. 도구가 호출되는 순간 발화 → 게이트 우회.

## 도식 — 알림 발화 판단

```
AskUserQuestion 뜸
      │
      ▼
[최근 6초 안에 키 입력 있었나?]
   ├─ 예  → 알림 억제 ❌ (자리에 있다고 판단)   ← 내가 겪던 상황
   └─ 아니오(6초+ idle) → Notification 훅 발화 ✅ (토스트)

Stop(완료) 은 이 판단을 안 거침 → 항상 ✅
PreToolUse 훅 도 이 판단을 안 거침 → 즉시 ✅ (우회법)
```

## 한 줄 요약

**Notification 알림은 "6초 이상 자리를 비웠을 때만" 뜬다.** 즉시 알림이 필요하면 그 이벤트를 `PreToolUse` 훅으로 잡아 6초 게이트를 우회한다.

## 출처 (파일:라인)

- `src/hooks/useNotifyAfterTimeout.ts:8` — `DEFAULT_INTERACTION_THRESHOLD_MS = 6000`
- `src/hooks/useNotifyAfterTimeout.ts:19` — `shouldNotify` (6초 조건)
- `src/services/notifier.ts:25` — `executeNotificationHooks(notif)` 호출
- `src/utils/hooks.ts:3570` — `executeNotificationHooks` 정의
- `src/components/permissions/AskUserQuestionPermissionRequest/` — AskUserQuestion = 권한요청
