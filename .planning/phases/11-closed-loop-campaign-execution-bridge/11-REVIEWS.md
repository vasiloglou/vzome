---
phase: 11
reviewers: [gemini, claude]
reviewed_at: 2026-04-04T16:12:23Z
plans_reviewed:
  - 11-01-PLAN.md
  - 11-02-PLAN.md
  - 11-03-PLAN.md
---

# Cross-AI Plan Review — Phase 11

## Gemini Review

# Phase 11 Plan Review: Closed-Loop Campaign Execution Bridge

The proposed plans for Phase 11 provide a robust and surgical bridge between the campaign governance established in Phase 10 and the existing `llm-generate` runtime. By favoring an in-memory "runtime overlay" over permanent YAML mutation and wrapping the existing generation core, the design preserves the integrity of the manual pipeline while fulfilling the requirements for reproducible, operator-governed execution. The three-wave approach correctly sequences the semantic resolution of campaign actions before touching the execution surface or the downstream manifest propagation.

---

### Plan 11-01 (Wave 1): Launch Contract and Resolution Foundation

#### Summary
Wave 1 focuses on the "resolution" layer—turning abstract campaign actions (like "tighten composition window" or "use a specialized model lane") into concrete, executable launch inputs. It introduces the necessary schema additions to `SystemConfig` to support model lanes and defines the storage layout for launch-specific artifacts.

#### Strengths
*   **Lane-Aware Architecture:** Correctly identifies that the current config only supports a single active LLM tuple and adds a first-class `model_lanes` seam to support the Phase 10 requirement for lane selection.
*   **In-Memory Overlay:** Adheres to the decision to avoid mutating the source YAML on disk, ensuring that the "source of truth" remains clean while the "launch intent" is captured in a separate `resolved_launch.json`.
*   **Deterministic Seed Resolution:** Provides a clear fallback strategy for seeds (reuse baseline -> materialize from eval-set -> fail), which is essential for making the abstract `seed_motif_variation` action executable.

#### Concerns
*   **Composition Shrink Heuristic (LOW):** The plan specifies a fixed "10 percent shrink" for composition windows without a target bound. While deterministic, this might be too aggressive or too subtle depending on the system. *Note: As this is "agent's discretion," it is a safe starting point, but should be documented as a v1.1 limitation.*
*   **Lane Selection Fallback (MEDIUM):** If a campaign requests a lane that isn't configured, the fallback to "baseline" only happens if `general_purpose` was requested or the list is empty. This prevents accidental execution on an expensive or inappropriate model, but may cause unexpected launch failures if the baseline *is* the intended lane but wasn't explicitly named.

#### Suggestions
*   Ensure the `CompositionBound` shrink logic handles the golden field precision (Z[phi]) correctly if any rounding is applied during the math.
*   The `resolved_model_lane` in the summary should explicitly record if the fallback was used vs. a configured lane match.

---

### Plan 11-02 (Wave 2): Execution Bridge and `llm-launch` CLI

#### Summary
Wave 2 implements the `llm-launch` CLI and modifies the `generate.py` core to accept additive overrides. It ensures that the existing generation path can now carry campaign metadata and instruction deltas without breaking the manual operator flow.

#### Strengths
*   **Additive Core Modification:** The changes to `generate_llm_candidates` use optional parameters for instruction deltas and campaign metadata, keeping the signature backward-compatible.
*   **Lineage at Candidate Level:** Correctly adds an `llm_campaign` block to the `CandidateRecord` provenance, which is the primary integration point for downstream stages.
*   **Failure Auditability:** The commitment to writing a "failed" `launch_summary.json` while preserving partial generation artifacts is critical for debugging "hallucinating" or crashing models.

#### Concerns
*   **Config Drift Protection (HIGH):** The plan requires `system_config_hash` to match. This is excellent. However, ensure that the error message explicitly tells the operator *which* file changed so they can decide whether to re-approve the proposal.
*   **CLI Argument Precedence (LOW):** `llm-launch` accepts an optional `--out` path. The plan should clarify if this override is recorded in the `resolved_launch.json` for reproducibility.

#### Suggestions
*   In `llm-launch`, consider printing the `launch_id` early so an operator can track it in the logs even if the process is killed before the summary is written.

---

### Plan 11-03 (Wave 3): Downstream Lineage and Compatibility

#### Summary
Wave 3 ensures that the lineage from the campaign survives through `screen`, `hifi-validate`, and `report`. It also provides the final end-to-end proof that LLM-launched candidates are fully compatible with the standard no-DFT pipeline.

#### Strengths
*   **Recursive Lineage Propagation:** The helper to derive campaign lineage from the candidate provenance ensures that `screen` and later stages don't need to "know" about campaigns—they just pass through what they find.
*   **Pipeline Manifest Integration:** Including `source_lineage` in the final `pipeline_manifest.json` fulfills `OPS-06` by providing a single umbrella artifact that traces back to the approval decision.
*   **Mock-Based E2E Test:** The addition to `test_real_mode_pipeline.py` provides high-confidence verification without relying on external network dependencies.

#### Concerns
*   **Metadata Bloat (LOW):** As candidates pass through multiple stages, the `source_lineage` dictionary is carried along. Ensure that the `build_manifest` helper doesn't accidentally duplicate lineage if multiple input files are merged (though in this pipeline, it's usually 1:1 or 1:N from a single source).

#### Suggestions
*   The documentation update should include a "Lineage Audit" section explaining how an operator can trace a report entry back to a specific campaign spec on disk.

---

### Risk Assessment

**Overall Risk: LOW**

The design is highly conservative regarding existing code. By treating the campaign launch as a **wrapper** and an **overlay**, the plans avoid the "second generation path" pitfall. The dependency on Pydantic models for the resolution logic ensures that the contract is strictly enforced before any shell commands or API calls are made. The only significant risk is the logic in `llm/launch.py` (Wave 1) becoming out of sync with future `llm-generate` features, but the TDD approach and focused core tests mitigate this effectively.

**Verification Readiness:** The validation strategy is comprehensive, covering schema, core resolution, CLI behavior, and E2E lineage. The use of the `llm_launch_core` test suite in Wave 1 is particularly important for pinning the resolution semantics early.

---

## Claude Review

Claude CLI did not return a usable review body for this run.

Observed behavior:
- first invocation failed immediately because this local CLI does not support the `--no-input` flag used by the workflow template
- second invocation without that flag hung and produced no review output before it was terminated

No substantive Claude review content was available to incorporate.

---

## Codex Review

Codex CLI was intentionally skipped for this review run because the current runtime is already Codex. The goal of `gsd-review` is independent external feedback, so including the same runtime as a reviewer would have weakened that signal.

---

## Consensus Summary

Only one successful independent review body was returned, so the points below are best treated as the primary external concerns rather than a full cross-model consensus.

### Agreed Strengths

- The three-wave split is well ordered: semantic action resolution first, launch wrapper second, downstream lineage propagation third.
- The plans stay additive to the existing `llm-generate` path instead of creating a competing generation engine.
- The auditability posture is strong: runtime overlay, explicit launch artifacts, and preserved partial-failure outputs.

### Agreed Concerns

- The config-drift failure path should be especially explicit for operators, including which config changed and why re-approval may be required.
- Lane-resolution fallback behavior may need tighter wording so the baseline/general-purpose path is never ambiguous.
- The fixed composition-window shrink heuristic is acceptable for v1.1, but it should be treated as a deliberate heuristic and documented as such.

### Divergent Views

- No cross-review divergence was available because only Gemini returned a substantive review.
