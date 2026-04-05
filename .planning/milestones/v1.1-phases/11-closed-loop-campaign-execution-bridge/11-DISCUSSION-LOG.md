# Phase 11: Closed-Loop Campaign Execution Bridge - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 11-closed-loop-campaign-execution-bridge
**Areas discussed:** Launch CLI shape, Action-to-runtime mapping, Execution scope, Lineage and output layout, Model-lane authority, Failure handling

---

## Launch CLI shape

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated `llm-launch` command | Launch from `mdisc llm-launch --campaign-spec PATH` | ✓ |
| Approval-and-launch command | Launch directly from `llm-approve --launch ...` | |
| Approval-artifact launch | Launch from approval artifact rather than campaign spec | |

**User's choice:** Dedicated `llm-launch --campaign-spec ...`
**Notes:** User accepted the recommended separation between governance and execution.

---

## Action-to-runtime mapping

| Option | Description | Selected |
|--------|-------------|----------|
| Runtime overlay | Resolve approved actions into a derived overlay at launch time without mutating the base YAML config | ✓ |
| Temporary rewritten config | Materialize a rewritten YAML config and launch from that file | |
| Fully expanded spec | Expand every action into concrete runtime fields inside the campaign spec | |

**User's choice:** Runtime overlay
**Notes:** User accepted the recommended approach that keeps the base config stable while still making launches reproducible.

---

## Execution scope

| Option | Description | Selected |
|--------|-------------|----------|
| Generate only | Launch `llm-generate` only and let downstream stages continue separately | ✓ |
| Generate plus screen | Auto-run `llm-generate` and `screen` | |
| Full downstream chain | Auto-run all downstream stages through rank/report | |

**User's choice:** Generate only
**Notes:** User accepted the narrower bridge so Phase 11 does not overreach into later orchestration concerns.

---

## Lineage and output layout

| Option | Description | Selected |
|--------|-------------|----------|
| Keep standard roots | Preserve current roots and add campaign-aware pointers and lineage | ✓ |
| Campaign-root primary | Put launch artifacts under a new campaign-centered root | |
| Dual-write layout | Duplicate artifacts into both current roots and a campaign root | |

**User's choice:** Keep standard roots
**Notes:** User accepted the compatibility-first layout so current downstream consumers stay intact.

---

## Model-lane authority

| Option | Description | Selected |
|--------|-------------|----------|
| Config-authoritative lanes | Config defines available model lanes, campaign actions choose among them | ✓ |
| Campaign-pinned provider/model | Campaign spec overrides config with exact provider/model values | |
| Ignore lane preference | Always use the single configured model and ignore lane metadata | |

**User's choice:** Config-authoritative lanes
**Notes:** User accepted the recommended posture and kept support for specialized materials-model lanes in scope through configured execution lanes.

---

## Failure handling

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve partial artifacts, no resume | Keep partial outputs, mark failure clearly, require explicit relaunch | ✓ |
| Preserve and resume | Keep partial outputs and add `--resume` in Phase 11 | |
| Clean failure | Delete partial outputs and keep only clean reruns | |

**User's choice:** Preserve partial artifacts, no resume
**Notes:** User accepted the recommended audit-first failure posture.

## the agent's Discretion

- Exact helper/module boundaries for the launch overlay
- Exact optional CLI flags beyond the campaign-spec-based command identity
- Exact launch-summary artifact filenames and pointer helpers
- Exact additive lineage field names across manifests

## Deferred Ideas

- Automatic downstream chaining beyond `llm-generate`
- Replay and comparison workflows
- Resume support
- Hard provider/model pinning as the default execution posture
- Local or fine-tuned serving infrastructure

