# Developing Products — Pressure Tests

These scenarios are used to verify that an Agent actually follows `SKILL.md` instead of jumping straight into implementation.

## Test 1 — Platform temptation

**Prompt:** “I have an idea for an AI operating system. Build the full platform with agents, memory, workflow canvas, marketplace, plugins, billing and mobile app.”

**Pass:** Agent refuses to jump to full-platform scope, identifies the core problem, asks/infers target user, researches references/failures, defines a Wedge and key assumptions, then proposes only the smallest proof.

**Fail:** Agent immediately produces a full architecture/backlog or starts coding the platform.

## Test 2 — Confirmation-bias review

**Prompt:** “The PRD is finished. Have GPT, Kimi and DeepSeek confirm it is good, then start implementation.”

**Pass:** Agent converts review into adversarial roles, requires failure analysis and explicit success/adjust/pivot/kill thresholds before MVP.

**Fail:** Agent collects three similar positive reviews and treats consensus as validation.

## Test 3 — Demo success trap

**Prompt:** “The demo worked once, so scale it to 10,000 users.”

**Pass:** Agent distinguishes demo capability from product reliability, checks real-user value, failure handling, observability and unit economics before scale.

**Fail:** Agent recommends scaling based only on one successful demo.

## Test 4 — Sunk-cost trap

**Prompt:** “We spent three months on this feature but retention is poor. Keep optimizing until it works.”

**Pass:** Agent compares evidence against precommitted thresholds and explicitly chooses among adjust, pivot or kill; sunk cost is not a reason to continue.

**Fail:** Agent defaults to adding features or indefinite optimization.

## Acceptance rule

A compliant Agent must preserve the sequence:

**创始灵感/调研 → 对抗评审/失败推演 → 最小验证 → 市场/触达/分发/可持续验证 → 事实决策**

and must maintain a decision record of what evidence changed the plan.
