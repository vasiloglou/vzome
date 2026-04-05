# Phase 28: Checkpoint Lifecycle and Promotion Contracts - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 28-checkpoint-lifecycle-and-promotion-contracts
**Areas discussed:** Lifecycle state shape, Active selection authority, Pinning surface, Retirement semantics, Promotion evidence minimum

---

## Lifecycle state shape

| Option | Description | Selected |
|--------|-------------|----------|
| Central registry only | One lifecycle file per system or checkpoint family tracks promoted, pinned, retired, and history | |
| Per-checkpoint state only | Each checkpoint carries its own lifecycle state | |
| Hybrid model | Immutable per-checkpoint facts plus a central lifecycle index for promoted/default/pin/retirement state | ✓ |

**User's choice:** Hybrid model
**Notes:** Chosen because it keeps checkpoint registration facts stable while making promoted/default state easy to audit and resolve.

---

## Active selection authority

| Option | Description | Selected |
|--------|-------------|----------|
| Registry alone decides default | Promoted checkpoint from lifecycle state always wins when no pin is present | |
| System config pins the exact default checkpoint | Lifecycle state is mostly advisory | |
| Config names family, registry resolves promoted member | Config stays authoritative for the lane/family, registry chooses the active member | ✓ |

**User's choice:** Config names family, registry resolves promoted member
**Notes:** Chosen to preserve config authority while making promotion a real workflow action.

---

## Pinning surface

| Option | Description | Selected |
|--------|-------------|----------|
| CLI/config override only | Only direct/manual workflows can pin by checkpoint id | |
| Campaign/spec only | Only governed campaign artifacts can pin a checkpoint | |
| Both manual and campaign surfaces | Manual and governed workflows share the same explicit pinning semantics | ✓ |

**User's choice:** Both manual and campaign surfaces
**Notes:** Chosen so direct `llm-generate` and later campaign execution remain aligned instead of diverging into separate pinning rules.

---

## Retirement semantics

| Option | Description | Selected |
|--------|-------------|----------|
| No implicit future selection, but still replayable/auditable | Retired checkpoints are excluded from future defaults while history stays reproducible | ✓ |
| Fully blocked everywhere | Retired checkpoints cannot be used even for replay | |
| Warning only | Retirement only emits warnings | |

**User's choice:** No implicit future selection, but still replayable/auditable
**Notes:** Chosen to protect future workflow choices without breaking reproducibility for historical runs.

---

## Promotion evidence minimum

| Option | Description | Selected |
|--------|-------------|----------|
| Typed promotion artifact with benchmark evidence references, no hard thresholds yet | Promotion stays auditable now while numeric policy waits for later phases | ✓ |
| Hard numeric thresholds now | Promotion requires fixed metrics immediately | |
| Manual note only | Promotion is justified only by operator comments | |

**User's choice:** Typed promotion artifact with benchmark evidence references, no hard thresholds yet
**Notes:** Chosen so Phase 28 gets the contract right without dragging Phase 30 benchmark policy into the first lifecycle phase.

---

## the agent's Discretion

- Exact schema names and on-disk file names for lifecycle and promotion artifacts
- Exact family-key mapping from config lanes into lifecycle lookup
- Exact wording for stale/conflicting lifecycle diagnostics
- Exact additive manifest fields for backward compatibility

## Deferred Ideas

- Hard numeric promotion thresholds
- Automated checkpoint training or promotion
- Tournament/fleet management infrastructure
- UI-first lifecycle management
