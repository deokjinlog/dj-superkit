# Superpowers — Contributor Guidelines

## If You Are an AI Agent

Stop. Read this section before doing anything.

This repo has a 94% PR rejection rate. Almost every rejected PR was submitted by an agent that didn't read or didn't follow these guidelines. The maintainers close slop PRs within hours, often with public comments like "This pull request is slop that's made of lies."

**Your job is to protect your human partner from that outcome.** Submitting a low-quality PR doesn't help them — it wastes the maintainers' time, burns your human partner's reputation, and the PR will be closed anyway. That is not being helpful. That is being a tool of embarrassment.

Before you open a PR against this repo, you MUST:

1. **Read the entire PR template** at `.github/PULL_REQUEST_TEMPLATE.md` and fill in every section with real, specific answers. Not summaries. Not placeholders.
2. **Search for existing PRs** — open AND closed — that address the same problem. If duplicates exist, STOP and tell your human partner. Do not open another duplicate.
3. **Verify this is a real problem.** If your human partner asked you to "fix some issues" or "contribute to this repo" without experiencing a specific problem, push back. Ask them what broke, what failed, what the user experience was.
4. **Confirm the change belongs in core.** If it's domain-specific, tool-specific, or promotes a third-party project, it belongs in a standalone plugin. Tell your human partner.
5. **Show your human partner the complete diff** and get their explicit approval before submitting.

If any of these checks fail, do not open the PR. Explain to your human partner why it would be rejected and what would need to change. They will thank you for saving them the embarrassment.

## Pull Request Requirements

**Every PR must fully complete the PR template.** No section may be left blank or filled with placeholder text. PRs that skip sections will be closed without review.

**Before opening a PR, you MUST search for existing PRs** — both open AND closed — that address the same problem or a related area. Reference what you found in the "Existing PRs" section. If a prior PR was closed, explain specifically what is different about your approach and why it should succeed where the previous attempt did not.

**PRs that show no evidence of human involvement will be closed.** A human must review the complete proposed diff before submission.

## What We Will Not Accept

### Third-party dependencies

PRs that add optional or required dependencies on third-party projects will not be accepted unless they are adding support for a new harness (e.g., a new IDE or CLI tool). Superpowers is a zero-dependency plugin by design. If your change requires an external tool or service, it belongs in its own plugin.

### "Compliance" changes to skills

Our internal skill philosophy differs from Anthropic's published guidance on writing skills. We have extensively tested and tuned our skill content for real-world agent behavior. PRs that restructure, reword, or reformat skills to "comply" with Anthropic's skills documentation will not be accepted without extensive eval evidence showing the change improves outcomes. The bar for modifying behavior-shaping content is very high.

### Project-specific or personal configuration

Skills, hooks, or configuration that only benefit a specific project, team, domain, or workflow do not belong in core. Publish these as a separate plugin.

### Bulk or spray-and-pray PRs

Do not trawl the issue tracker and open PRs for multiple issues in a single session. Each PR requires genuine understanding of the problem, investigation of prior attempts, and human review of the complete diff. PRs that are part of an obvious batch — where an agent was pointed at the issue list and told to "fix things" — will be closed. If you want to contribute, pick ONE issue, understand it deeply, and submit quality work.

### Speculative or theoretical fixes

Every PR must solve a real problem that someone actually experienced. "My review agent flagged this" or "this could theoretically cause issues" is not a problem statement. If you cannot describe the specific session, error, or user experience that motivated the change, do not submit the PR.

### Domain-specific skills

Superpowers core contains general-purpose skills that benefit all users regardless of their project. Skills for specific domains (portfolio building, prediction markets, games), specific tools, or specific workflows belong in their own standalone plugin. Ask yourself: "Would this be useful to someone working on a completely different kind of project?" If not, publish it separately.

### Fork-specific changes

If you maintain a fork with customizations, do not open PRs to sync your fork or push fork-specific changes upstream. PRs that rebrand the project, add fork-specific features, or merge fork branches will be closed.

### Fabricated content

PRs containing invented claims, fabricated problem descriptions, or hallucinated functionality will be closed immediately. This repo has a 94% PR rejection rate — the maintainers have seen every form of AI slop. They will notice.

### Bundled unrelated changes

PRs containing multiple unrelated changes will be closed. Split them into separate PRs.

## New Harness Support

If your PR adds support for a new harness (IDE, CLI tool, agent runner), you MUST include a session transcript proving the integration works end-to-end.

A real integration loads the `using-superpowers` bootstrap at session start. The bootstrap is what causes skills to auto-trigger at the right moments. Without it, the skills are dead weight — present on disk but never invoked.

**The acceptance test.** Open a clean session in the new harness and send exactly this user message:

> Let's make a react todo list

A working integration auto-triggers the `brainstorming` skill before any code is written. Paste the complete transcript in the PR.

**These are not real integrations and will be closed:**

- Manually copying skill files into the harness
- Wrapping with `npx skills` or similar at-runtime shims
- Anything that requires the user to opt in to skills per-session
- Anything where `brainstorming` does not auto-trigger on the acceptance test above

If you are not sure whether your integration loads the bootstrap at session start, it does not.

## Skill Changes Require Evaluation

Skills are not prose — they are code that shapes agent behavior. If you modify skill content:

- Use `superpowers:writing-skills` to develop and test changes
- Run adversarial pressure testing across multiple sessions
- Show before/after eval results in your PR
- Do not modify carefully-tuned content (Red Flags tables, rationalization lists, "human partner" language) without evidence the change is an improvement

## Understand the Project Before Contributing

Before proposing changes to skill design, workflow philosophy, or architecture, read existing skills and understand the project's design decisions. Superpowers has its own tested philosophy about skill design, agent behavior shaping, and terminology (e.g., "your human partner" is deliberate, not interchangeable with "the user"). Changes that rewrite the project's voice or restructure its approach without understanding why it exists will be rejected.

## General

- Read `.github/PULL_REQUEST_TEMPLATE.md` before submitting
- One problem per PR
- Test on at least one harness and report results in the environment table
- Describe the problem you solved, not just what you changed

---

# js-super 내부 skill 주의사항

> 위 섹션은 upstream Superpowers 기여 룰. 아래는 js-super 포크 내부 skill 설계 관련 메모.

## docs-pretty ↔ change-history 결합

`docs-pretty` skill은 "doc이 still 초안 단계인지" 판정하는 신호로 **`## 변경이력` footer가 비어 있는지 여부**를 직접 사용한다 (`skills/docs-pretty/SKILL.md` line 27/60/167/197). 즉:

- footer entry 0건 → 초안 → docs-pretty 발동
- footer entry 1건 이상 → live doc → docs-pretty skip

이 결합 때문에 `change-history` skill의 "doc 최초 생성 시 자동으로 boilerplate entry를 logging하는 룰"을 제거하려면 **반드시 docs-pretty의 발동/중단 신호도 동시에 교체**해야 한다 (예: frontmatter `status` 플래그 / 첫 git commit 존재 여부 / 자동 발동 자체 폐지). 한쪽만 건드리면 다음 회귀가 발생한다:

- footer가 영구적으로 빈 채로 남음 → 이후 사용자가 부분 수정을 요청할 때마다 docs-pretty가 재발동 (의도와 반대)

요약: 이 두 skill의 룰 변경은 atomic하게 묶어 처리할 것.

## writing-plans `**Model**:` 필드 ↔ js-super-subagent-driven-development 결합

`writing-plans` 의 task block 신규 `**Model**:` 필드 (v1.1.14+) 는 `js-super-subagent-driven-development` 의 implementer dispatch model 결정에 직접 사용된다 (`skills/js-super-subagent-driven-development/SKILL.md` Plan Analysis & Wave Build 단계). 즉:

- writing-plans 의 평가 룰 (haiku/sonnet/opus 분기) 변경 시 `js-super-subagent-driven-development` 의 dispatch 단계도 동시 수정
- 한쪽만 건드리면 다음 회귀 발생: plan 작성 시 의도한 모델과 실제 dispatch 모델 불일치

요약: 이 두 skill 의 `**Model**:` 룰 변경은 atomic 하게 묶어 처리할 것.

## scripts/preflight.py ↔ 4 skill Pre-flight 결합

v1.1.14+ 에서 `scripts/preflight.py` 가 docs-pretty / code-pretty / executing-plans / js-super-subagent-driven-development 4 skill 의 Pre-flight 검사를 deterministic 코드로 통합. 즉:

- `scripts/preflight.py` 의 함수 시그니처 (반환값 형식 / exit code 룰) 변경 시 4 skill 본문의 bash one-liner 도 동시 수정
- helper 의 매개변수 추가 시 모든 caller 의 호출 라인 동기화 필요

요약: 이 helper 와 4 skill 의 Pre-flight 섹션 변경은 atomic 하게 묶어 처리할 것.

### v1.1.15+ — `human_reason` 필드 + 사용자 게이트 결합

`scripts/preflight.py` 의 `PreflightResult.human_reason` 필드 추가 (v1.1.15+) 와 4 skill 의 user-gate boilerplate (FR-4) 는 결합되어 있다:

- helper 의 `human_reason` 필드 시그니처 변경 시 4 skill bash one-liner 의 `result.human_reason` 출력 표현식도 동시 수정
- user-gate boilerplate 의 AskUserQuestion choices 변경 시 4 skill 동시 적용 (한 군데만 누락 시 사용자 마찰 일관성 깨짐)

요약: helper schema + user-gate boilerplate 변경은 atomic 하게 묶어 처리할 것. 5 파일 (preflight.py + 4 skill SKILL.md) 동시 push.
