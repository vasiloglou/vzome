# Phase 19: Local Serving Runtime and Lane Contracts - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 19-local-serving-runtime-and-lane-contracts
**Areas discussed:** Local execution form, Serving config shape, Operator setup posture, Diagnostics and fallback, Recorded serving identity

---

## Local execution form

| Option | Description | Selected |
|--------|-------------|----------|
| OpenAI-compatible local server first | Start with local HTTP-serving contracts so vLLM, TGI, Ollama-style gateways, or similar local servers fit behind one runtime seam | ✓ |
| In-process transformers first | Run local models directly inside the Python process | |
| Both from the start | Support external local servers and in-process inference in Phase 19 | |

**User's choice:** OpenAI-compatible local server first
**Notes:** Chosen as the least invasive way to extend the existing hosted runtime and keep Phase 19 focused.

---

## Serving config shape

| Option | Description | Selected |
|--------|-------------|----------|
| Transport in backend, lane choice in `llm_generate.model_lanes` | Backend carries transport defaults while lanes carry the concrete adapter/provider/model identity | ✓ |
| Everything in model lanes | Put endpoint/path/runtime details entirely inside lane objects | |
| Everything in backend | Put all serving/runtime details in backend config | |

**User's choice:** Transport in backend, lane choice in `llm_generate.model_lanes`
**Notes:** Chosen because it best matches the current schema and Phase 11 lane-resolution behavior.

---

## Operator setup posture

| Option | Description | Selected |
|--------|-------------|----------|
| Assume local server already running | Validate configuration and connectivity, but do not manage local processes | ✓ |
| CLI can start local server processes | Add local process management to the CLI | |
| Config only, no connectivity validation yet | Only add schema/config support in this phase | |

**User's choice:** Assume local server already running
**Notes:** Chosen as the safest MVP cut for serving support.

---

## Diagnostics and fallback

| Option | Description | Selected |
|--------|-------------|----------|
| Fail hard unless fallback explicitly configured | Unavailable requested lanes stop with a clear error, with no silent downgrade | ✓ |
| Automatic fallback to baseline | Missing local/specialized lanes fall back automatically | |
| Fallback only for manual generation | Allow fallback for manual `llm-generate`, but not for campaign launch/replay | |

**User's choice:** Fail hard unless fallback is explicitly configured
**Notes:** Chosen to prevent operators from believing a specialized lane ran when the runtime actually used the baseline path.

---

## Recorded serving identity

| Option | Description | Selected |
|--------|-------------|----------|
| Full auditable identity | Record requested lane, resolved lane, adapter, provider, model, endpoint/path, and checkpoint/revision/hash when available | ✓ |
| Medium identity | Record adapter/provider/model plus endpoint or path | |
| Minimal identity | Record only lane plus adapter/provider/model | |

**User's choice:** Full auditable identity
**Notes:** Chosen so later replay and benchmark comparisons can distinguish local and specialized runs honestly.

---

## the agent's Discretion

- Exact field names for transport defaults and explicit fallback controls
- Exact adapter/module naming for the new local runtime seam
- Exact validation mechanics and error text
- Exact additive lineage/manifest field names

## Deferred Ideas

- In-process local inference
- CLI-managed local server lifecycle
- Autonomous or silent fallback behavior
- Zomic-native fine-tuned local generation as part of this phase
