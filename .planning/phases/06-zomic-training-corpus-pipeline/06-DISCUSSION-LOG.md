# Phase 6: Zomic Training Corpus Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 06-zomic-training-corpus-pipeline
**Areas discussed:** Corpus source coverage, Training example contract, Conversion fidelity policy, Corpus QA and release tiers

---

## Corpus source coverage

| Option | Description | Selected |
|--------|-------------|----------|
| A | repo Zomic scripts + pipeline/generated candidates + open approximant conversions from `HYPOD-X` and `COD` + existing vZome/Zomic exports; keep `ICSD` and `PyQCstrc` deferred | |
| B | same as A, but include `PyQCstrc` in required v1 scope | ✓ |
| C | same as A, but include any licensed source we can access, including `ICSD`, in required v1 scope | |

**User's choice:** `1B`
**Notes:** `PyQCstrc` was promoted from deferred/watchlist status into required
v1 Phase 6 scope. Restricted sources remain outside required scope.

## Training example contract

| Option | Description | Selected |
|--------|-------------|----------|
| A | one shared builder emits two corpora: a syntax-first Zomic corpus and a materials-conditioned corpus with system/composition/properties metadata | ✓ |
| B | one unified corpus only, with every example carrying the full materials metadata block | |
| C | one minimal Zomic-only corpus for now; materials-conditioned records wait for a later phase | |

**User's choice:** `2A`
**Notes:** The phase should preserve a clear split between grammar-oriented
training data and richer materials-conditioned records, while building them from
shared source infrastructure.

## Conversion fidelity policy

| Option | Description | Selected |
|--------|-------------|----------|
| A | deterministic and auditable first; approximate mappings are allowed but must be flagged with fidelity tier and provenance | ✓ |
| B | only include near-exact conversions in the corpus; drop approximate mappings entirely | |
| C | prioritize corpus size even if many mappings are heuristic, as long as parse/compile checks pass | |

**User's choice:** `3A`
**Notes:** Auditability and provenance matter more than script prettiness or raw
corpus size. Approximate conversions remain acceptable only when clearly marked.

## Corpus QA and release tiers

| Option | Description | Selected |
|--------|-------------|----------|
| A | tiered release: `gold` requires parse + compile + label-valid + collision-safe + higher-fidelity mapping; `silver` allows lower-confidence mapping with basic QA | ✓ |
| B | single strict release tier only; anything imperfect is excluded | |
| C | single permissive release tier; keep almost everything that parses and compiles | |

**User's choice:** `4A`
**Notes:** The user chose a tiered corpus posture so lower-confidence but still
useful data can remain available without contaminating the highest-trust subset.

## the agent's Discretion

- exact package split between converters, corpus assembly, and QA helpers
- exact artifact naming and manifest schema
- exact fidelity label vocabulary beyond the locked release tiers

## Deferred Ideas

- licensed-source expansion such as `ICSD`
- model training and live inference work
- permissive heuristic corpus inclusion without explicit fidelity tagging
