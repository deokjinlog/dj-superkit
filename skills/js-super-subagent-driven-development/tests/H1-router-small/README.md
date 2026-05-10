# H1 — Entry Router: small 신호 자동 라우팅

## 시나리오

사용자가 `/brainstorm` 또는 자연어로 "README 한 줄 수정" 류 small 피처 요청.

## 입력 (사용자 메시지 시뮬레이션)

```
README.md 의 v1.1.13 → v1.1.15 한 줄 간단히 수정해줘
```

## 기대 동작

1. js-super:brainstorming Step 0 라우터 발화
2. small 신호 감지 (키워드: `간단`, 단일 파일/한 줄 변경)
3. 한 줄 notice 노출:
   ```
   ℹ️ Auto-routing to og-brainstorming ('간단', 단일 파일 변경). Switch back? "js-super" 라고 답하세요.
   ```
4. og-brainstorming Skill tool 호출

## 매핑

- AC-6 (작은 메타 피처로 라우터 small 자동 라우팅 확인)
- FR-3 (Step 0 라우터)
