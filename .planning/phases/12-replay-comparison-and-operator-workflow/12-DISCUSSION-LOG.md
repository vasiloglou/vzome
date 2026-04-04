# Phase 12: Replay, Comparison, and Operator Workflow - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or
> execution agents. Decisions are captured in `12-CONTEXT.md` - this log
> preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 12-replay-comparison-and-operator-workflow
**Areas discussed:** Replay authority, Comparison baselines, CLI surface, Comparison outputs, Operator runbook scope, Replay strictness

---

## Replay authority

| Option | Description | Selected |
|--------|-------------|----------|
| Launch artifact authority | Replay uses the recorded launch artifact as authority, with campaign spec as provenance context | ✓ |
| Campaign-spec recomputation | Replay recomputes behavior from the approved campaign spec each time | |
| Hybrid fallback | Replay prefers the launch artifact but falls back to the campaign spec when fields are missing | |

**User's choice:** Launch artifact authority
**Notes:** User accepted the recommendation that replay should reproduce what
actually ran, not reinterpret prior approval-time intent.

---

## Comparison baselines

| Option | Description | Selected |
|--------|-------------|----------|
| Acceptance pack + prior launch | Compare against the originating acceptance pack and the most recent prior launch | ✓ |
| Acceptance pack only | Compare only against the acceptance pack | |
| Prior launch only | Compare only against the most recent prior launch | |

**User's choice:** Acceptance pack plus prior launch
**Notes:** User accepted the recommendation that operators need both absolute
and relative comparison signal.

---

## CLI surface

| Option | Description | Selected |
|--------|-------------|----------|
| Separate commands | Add `mdisc llm-replay` and `mdisc llm-compare` | ✓ |
| Launch flags | Fold replay and compare under `llm-launch` flags | |
| One multipurpose command | Use one higher-level command with internal mode switching | |

**User's choice:** Separate commands
**Notes:** User accepted the clearer operator model and audit trail of explicit
replay/compare commands.

---

## Comparison outputs

| Option | Description | Selected |
|--------|-------------|----------|
| JSON + human summary | Emit typed JSON artifacts and concise human-readable summaries | ✓ |
| JSON only | Emit typed machine-readable artifacts only | |
| Human summary only | Emit terminal-friendly summaries only | |

**User's choice:** JSON plus human summary
**Notes:** User accepted the recommendation that Phase 12 should serve both
operators and later tooling.

---

## Operator runbook scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full end-to-end runbook | Cover suggest, approve, launch, replay, compare, and interpretation | ✓ |
| Minimal command docs | Keep documentation short and command-focused | |
| Runbook plus helper scripts | Add wrapper scripts in addition to the runbook | |

**User's choice:** Full end-to-end runbook
**Notes:** User accepted the recommendation that this phase should make the
workflow safe and repeatable for human operators.

---

## Replay strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Strict replay only | No behavioral overrides in Phase 12 | ✓ |
| Strict with small safe overrides | Allow limited overrides such as output location | |
| Flexible replay | Allow lane, prompt, or action overrides | |

**User's choice:** Strict replay only
**Notes:** User accepted the recommendation that reproducibility matters more
than flexibility in the first replay/comparison phase.

## the agent's Discretion

- Exact replay/comparison helper boundaries
- Exact JSON artifact filenames and summary rendering format
- Exact metric naming as long as it stays typed and additive
- Exact deterministic rule for selecting the most recent prior launch

## Deferred Ideas

- Replay-time overrides
- Resume semantics
- Autonomous campaign execution
- UI-first orchestration
- Local or fine-tuned serving infrastructure
