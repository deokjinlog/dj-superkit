# H2 — Entry Router: 모호한 피처 → AskUserQuestion 게이트

## 시나리오

명시적 small 신호 없는 피처. AI 가 small/large 분명 판정 X → 게이트 발화.

## 입력

```
로그 포맷 변경하고 싶어
```

## 기대 동작

1. js-super:brainstorming Step 0 라우터 발화
2. small 신호 부재 (키워드 X, 단일 파일/함수 명시 X)
3. AskUserQuestion 호출:
   - question: "이 피처는 og-brainstorming(가벼운 단발) 또는 js-super:brainstorming(3-MD 풀 트랙) 중 어느 모드로 진행할까요?"
   - header: "진입 모드"
   - options: og-brainstorming / js-super:brainstorming
4. 사용자 선택 → 해당 skill 진입

## 매핑

- AC-7 (모호한 피처로 라우터 게이트 발화 확인)
- FR-3 (Step 0 라우터)
