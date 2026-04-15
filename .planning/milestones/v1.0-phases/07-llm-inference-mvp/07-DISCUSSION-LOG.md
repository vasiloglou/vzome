# Phase 7: LLM Inference MVP - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 07-llm-inference-mvp
**Areas discussed:** Inference runtime, Generation envelope, Failure handling, Evaluation contract, Artifact and provenance shape

---

## Inference runtime

| Option | Description | Selected |
|--------|-------------|----------|
| A | `mock + one real hosted API adapter` in v1. Keep the adapter seam clean, but defer local-model serving. | ✓ |
| B | `mock + one hosted API adapter + one local adapter` in v1. | |
| C | local-only inference in v1. | |

**User's choice:** Recommended default (`A`)
**Notes:** User answered `all`; interpreted as accepting the recommended option for each Phase 7 gray area to keep discussion moving.

## Generation envelope

| Option | Description | Selected |
|--------|-------------|----------|
| A | Config-driven generation with optional seed Zomic. The command uses system constraints and can do fresh generation or controlled variation, but no arbitrary free-form chat prompt. | ✓ |
| B | Seed-variation only. MVP always starts from an existing Zomic script or corpus example. | |
| C | Free-form operator prompting is allowed in v1. | |

**User's choice:** Recommended default (`A`)
**Notes:** Locks the MVP to a reproducible system-config surface rather than a chat-style interface.

## Failure handling

| Option | Description | Selected |
|--------|-------------|----------|
| A | Bounded retry loop for parse/compile failures, but no model-driven repair pass yet. Keep every raw output and failure reason in run artifacts. | ✓ |
| B | Single-shot only. Invalid outputs are logged and dropped with no retry. | |
| C | Retry plus one repair pass that feeds parse/compile errors back into the model. | |

**User's choice:** Recommended default (`A`)
**Notes:** Captures a pragmatic hardening posture without pulling repair-loop complexity into Phase 7.

## Evaluation contract

| Option | Description | Selected |
|--------|-------------|----------|
| A | Offline benchmark on `Al-Cu-Fe` and `Sc-Zn`, comparing against the deterministic generator on parse rate, compile rate, `CandidateRecord` conversion rate, and screen pass-through. Full hi-fi benchmark waits for Phase 8. | ✓ |
| B | Validity-only evaluation for MVP: parse, compile, and conversion rates only. | |
| C | Full end-to-end benchmark now, including hi-fi validation and ranking. | |

**User's choice:** Recommended default (`A`)
**Notes:** Keeps Phase 7 meaningful enough to judge usefulness, while deferring the heavier benchmark lane to Phase 8.

## Artifact and provenance shape

| Option | Description | Selected |
|--------|-------------|----------|
| A | Rich run-level lineage in manifests. Keep prompt template, resolved inputs, model/provider/settings, raw completions, and parse/compile outcomes in a run artifact; keep each `CandidateRecord` lighter with IDs back to the run. | ✓ |
| B | Minimal provenance only on final candidates: model ID, temperature, and final prompt. | |
| C | Store the full raw prompt/output lineage directly inside every generated `CandidateRecord`. | |

**User's choice:** Recommended default (`A`)
**Notes:** Preserves auditability without bloating downstream candidate artifacts.

## the agent's Discretion

- Exact provider choice for the first hosted adapter
- Exact prompt template structure and sampling defaults
- Exact retry count and stopping rules
- Exact file layout for run-level raw completion artifacts

## Deferred Ideas

- Local-model serving path
- Free-form operator prompt mode
- Model-driven repair loop
- Full hi-fi benchmark lane in Phase 7

