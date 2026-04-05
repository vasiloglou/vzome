# Phase 21: Comparative Benchmarks and Operator Serving Workflow - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 21-comparative-benchmarks-and-operator-serving-workflow
**Areas discussed:** Benchmark context authority, Comparison dimensions, Smoke-test posture, Benchmark surface, Recommendation output

---

## Benchmark context authority

| Option | Description | Selected |
|--------|-------------|----------|
| One shared benchmark context per comparison | Run hosted, local, and specialized lanes against the same acceptance-pack or benchmark context | ✓ |
| Lane-specific benchmark inputs | Let each lane use its own tailored input set | |
| Shared core context plus optional lane extras | Keep a shared baseline but allow extra lane-specific benchmark material | |

**User's choice:** One shared benchmark context per comparison
**Notes:** Chosen to keep the benchmark honest and directly comparable across hosted, local, and specialized serving lanes.

---

## Comparison dimensions

| Option | Description | Selected |
|--------|-------------|----------|
| Quality + cost + latency + operator friction | Measure practical tradeoffs, not just technical validity | ✓ |
| Quality only | Focus strictly on output quality | |
| Quality + latency only | Compare output quality and speed without cost or setup burden | |

**User's choice:** Quality + cost + latency + operator friction
**Notes:** Chosen because Phase 21 is meant to guide operator decisions, not only determine whether a lane technically works.

---

## Smoke-test posture

| Option | Description | Selected |
|--------|-------------|----------|
| Mandatory per-lane smoke test before benchmark | Every requested lane must pass a preflight check first | ✓ |
| Best-effort smoke test with warnings | Benchmark continues even if a lane is unhealthy | |
| No separate smoke step | Discover failures only inside benchmark execution | |

**User's choice:** Mandatory per-lane smoke test before benchmark
**Notes:** Chosen to keep benchmark evidence trustworthy and prevent silent or misleading lane downgrade behavior.

---

## Benchmark surface

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated operator entrypoint | Add a benchmark command that orchestrates hosted/local/specialized runs over one context | ✓ |
| Docs recipe only | Leave operators to stitch the workflow together manually | |
| Fold it into llm-compare | Overload compare with benchmark orchestration behavior | |

**User's choice:** Dedicated operator entrypoint
**Notes:** Chosen so Phase 21 ends with a genuinely operator-usable workflow surface rather than a docs-only recipe.

---

## Recommendation output

| Option | Description | Selected |
|--------|-------------|----------|
| Typed artifacts plus operator guidance | Preserve machine-readable outputs and also explain when to prefer each lane | ✓ |
| Typed artifacts only | Keep the output automation-friendly without a human-focused summary | |
| Human-readable summary only | Focus on operator readability without structured benchmark artifacts | |

**User's choice:** Typed artifacts plus operator guidance
**Notes:** Chosen so the benchmark stays reproducible and auditable while still helping operators pick the right lane in practice.

---

## the agent's Discretion

- Exact benchmark command name and flag layout
- Exact smoke-test mechanics and output wording
- Exact benchmark artifact field names
- Exact way operator friction is summarized in the final outputs

## Deferred Ideas

- Lane-specific benchmark contexts as the default behavior
- Silent fallback during comparative benchmarking
- Docs-only benchmark orchestration with no dedicated entrypoint
- UI-first benchmark orchestration replacing the existing CLI
- Autonomous campaign execution layered onto this milestone
