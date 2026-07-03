# /sync-html

`<slug>` 인자는 선택입니다. 누락 시 `scripts/auto_flow.find_latest_slug(Path("docs/features"))` 를 호출해서 가장 최근 폴더를 자동으로 선택합니다. `--rebuild` 플래그도 선택입니다.

이 슬래시는 feature 디렉토리의 `.md` 내용을 `.html` 시각화 사본으로 맞춥니다 (sync). 기존 `.html` 의 디자인 (레이아웃 / 색 / 여백) 은 보존하고 내용만 갱신합니다. `--rebuild` 를 명시했을 때만 디자인을 처음부터 재생성합니다.

## 동작

1. 인자 `<slug>` 확인 (또는 latest slug 추론) + `--rebuild` 플래그 검출
2. `docs/features/<slug>/<slug>-{requirements,tech-design,implementation-plan}.md` 중 존재하는 모든 `.md` 검출
3. 각 `.md` 에 대해 같은 위치의 `.html` 존재 여부 확인 후 3-way 분기:

| 케이스 | 동작 |
|---|---|
| `.html` 없음 | 디자인 + 생성 (generating-html 동등 경로 — design 자유 결정) |
| `.html` 존재 | 기존 `.html` 을 subagent 에 같이 입력 → 디자인·레이아웃·색·여백 보존 + 내용만 sync |
| `--rebuild` 플래그 | `.html` 존재 무시 → 디자인 처음부터 재생성 (기존 디자인 폐기) |

4. Subagent dispatch (각 `.md` 별):
   - `subagent_type`: `general-purpose`
   - `model`: `sonnet`
   - `run_in_background`: `true` (fire-and-forget)
   - `prompt`: 분기에 따라 동등 + 내용 sync 룰 / 처음부터 디자인 룰
5. 메인 즉시 다음 turn — 결과 대기 X

## `--rebuild` 경고

> `--rebuild` 사용 시 **기존 디자인이 폐기됩니다**. `.html` 은 `.gitignore` 대상이라 **git revert 로 복원 불가**. 디자인 다시 만들 의도일 때만 사용하세요.

## 사용 시점

- `change-propagation` 후 사용자 명시 호출 — `.md` 사후 cascade 반영을 `.html` 에 sync
- `.html` 부재 / stale 인지 시 사용자 명시 호출
- 디자인 자체 변경 원할 때 `--rebuild` 명시 호출

## 영구 생략

- AskUserQuestion 게이트 — fire-and-forget 의도상 사용자 입력 wait X
- `.md` 가공 (`.md` 는 source-of-truth, 손대지 않음)
- 결과 dispatch 노출 — silent

## `--check` 옵션 (v2.4+)

`--check` 플래그 명시 시 silent log (`.dj-superkit/html-regen.log`) 의 마지막 N entry (default 10) 출력. `.html` 생성 dispatch / success / fail 결과를 사용자가 직접 확인.

### 사용

```
/sync-html --check          # 마지막 10 entry 출력
/sync-html --check 20       # 마지막 20 entry 출력
```

### 출력 형식

```
YYYY-MM-DD HH:MM:SS | DISPATCH | <slug>-<type>.md | agent_id=<id>
YYYY-MM-DD HH:MM:SS | SUCCESS  | <slug>-<type>.html | <bytes> bytes
YYYY-MM-DD HH:MM:SS | FAIL     | <slug>-<type>.md | <reason>
```

### 사용 시점 (B 항목 회귀 dogfood)

- 백그라운드 호출 결과가 명시 안 됐을 때 (메인 응답에 B-4 메시지 누락 catch)
- `.html` 생성 누락 의심 시
- silent log 누적 확인 (rotation 정책 미도입 — append-only)

## 다음 단계

자동 chain 없음. 1회성 액션.
