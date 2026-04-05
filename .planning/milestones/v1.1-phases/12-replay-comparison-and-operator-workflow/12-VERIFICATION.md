---
phase: 12-replay-comparison-and-operator-workflow
verified: 2026-04-05T00:47:16Z
status: passed
score: 3/3 requirements verified
re_verification:
  previous_status: gaps_found
  previous_score: 0/3
  gaps_closed:
    - "Added the missing 12-VERIFICATION.md proof artifact."
    - "Restored the missing 12-01-SUMMARY.md and 12-02-SUMMARY.md evidence chain."
    - "Prepared Phase 15 traceability closeout for LLM-09, LLM-11, and OPS-07."
  gaps_remaining: []
  regressions: []
---

# Phase 12: Replay, Comparison, and Operator Workflow Verification Report

**Phase Goal:** Make the closed-loop LLM workflow reproducible, comparable, and usable by operators through strict replay, dual-baseline comparison, and a documented end-to-end command sequence.
**Verified:** 2026-04-05T00:47:16Z
**Status:** passed
**Re-verification:** Yes - after milestone audit gap closure

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Replay is strict and launch-bundle-driven: it reuses recorded launch artifacts, preserves launch-time inputs, records config drift, and writes additive replay lineage instead of mutating the original launch. | ✓ VERIFIED | `.planning/phases/12-replay-comparison-and-operator-workflow/12-01-SUMMARY.md`; `.planning/phases/12-replay-comparison-and-operator-workflow/12-02-SUMMARY.md`; `.planning/phases/12-replay-comparison-and-operator-workflow/12-VALIDATION.md`; `materials-discovery/src/materials_discovery/llm/replay.py`; `materials-discovery/src/materials_discovery/cli.py`; `materials-discovery/tests/test_llm_replay_core.py`; `materials-discovery/tests/test_llm_replay_cli.py`; `materials-discovery/developers-docs/llm-integration.md`; `materials-discovery/developers-docs/pipeline-stages.md` |
| 2 | Comparison freezes launch outcomes into typed snapshots and always evaluates the current launch against the originating acceptance-pack baseline plus the most recent prior launch when one exists. | ✓ VERIFIED | `.planning/phases/12-replay-comparison-and-operator-workflow/12-01-SUMMARY.md`; `.planning/phases/12-replay-comparison-and-operator-workflow/12-02-SUMMARY.md`; `.planning/phases/12-replay-comparison-and-operator-workflow/12-VALIDATION.md`; `materials-discovery/src/materials_discovery/llm/compare.py`; `materials-discovery/src/materials_discovery/llm/storage.py`; `materials-discovery/src/materials_discovery/cli.py`; `materials-discovery/tests/test_llm_compare_core.py`; `materials-discovery/tests/test_llm_compare_cli.py`; `materials-discovery/developers-docs/llm-integration.md`; `materials-discovery/developers-docs/pipeline-stages.md` |
| 3 | The operator workflow is documented, regression-backed, and remains safely operator-governed: suggest -> approve -> launch -> replay -> compare, with manual downstream continuation preserved. | ✓ VERIFIED | `.planning/phases/12-replay-comparison-and-operator-workflow/12-02-SUMMARY.md`; `.planning/phases/12-replay-comparison-and-operator-workflow/12-03-SUMMARY.md`; `.planning/phases/12-replay-comparison-and-operator-workflow/12-VALIDATION.md`; `materials-discovery/RUNBOOK.md`; `materials-discovery/developers-docs/llm-integration.md`; `materials-discovery/developers-docs/pipeline-stages.md`; `materials-discovery/tests/test_real_mode_pipeline.py`; `materials-discovery/tests/test_llm_campaign_lineage.py` |

**Score:** 3/3 requirements verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/replay.py` | Strict replay over recorded launch bundles | ✓ VERIFIED | Loads the full launch bundle, validates artifact agreement, reconstructs the effective config, and produces replay metadata from recorded launch truth. |
| `materials-discovery/src/materials_discovery/llm/compare.py` | Typed snapshots and dual-baseline comparison helpers | ✓ VERIFIED | Builds immutable outcome snapshots, resolves prior launches deterministically, and computes deltas versus acceptance-pack and prior-launch baselines. |
| `materials-discovery/src/materials_discovery/cli.py` | Operator-facing `llm-replay` and `llm-compare` commands | ✓ VERIFIED | Ships strict replay and comparison commands, writes durable JSON artifacts, and emits operator-readable summaries. |
| `materials-discovery/RUNBOOK.md` | End-to-end operator loop guidance | ✓ VERIFIED | `## 8. Closed-Loop LLM Workflow` documents the full safe sequence from `llm-suggest` through `llm-compare`, plus on-disk audit artifacts and interpretation notes. |
| `materials-discovery/developers-docs/pipeline-stages.md` | CLI contract sections for replay and compare | ✓ VERIFIED | `## 14. mdisc llm-replay` and `## 15. mdisc llm-compare` define syntax, artifacts, strict replay rules, and baseline rules. |
| `.planning/phases/12-replay-comparison-and-operator-workflow/12-VALIDATION.md` | Audit-ready validation record with green evidence | ✓ VERIFIED | Records the focused replay/compare slices as green, plus the existing Phase 12 full-suite result of `374 passed, 3 skipped, 1 warning`. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/replay.py` | `materials-discovery/src/materials_discovery/cli.py` | `llm-replay` uses `launch_summary.json` as the entry artifact and reconstructs the recorded runtime before delegating back into generation | WIRED | `load_campaign_launch_bundle()`, `build_replay_config()`, and `build_replay_campaign_metadata()` are the strict replay seam consumed by the CLI. |
| `materials-discovery/src/materials_discovery/llm/compare.py` | acceptance-pack lineage in the campaign spec | comparison always anchors current outcomes to the originating acceptance-pack metrics and optionally to the most recent prior launch | WIRED | `_acceptance_baseline_for_bundle()` and `find_prior_campaign_launch()` make the dual-baseline story explicit and deterministic. |
| `materials-discovery/src/materials_discovery/cli.py` | `materials-discovery/src/materials_discovery/llm/compare.py` | `llm-compare` writes typed JSON artifacts before printing human-readable summary lines | WIRED | CLI compare creates or reuses `outcome_snapshot.json`, writes `comparison_{launch_id}.json`, and then prints the summary payload. |
| `materials-discovery/RUNBOOK.md` and `materials-discovery/developers-docs/pipeline-stages.md` | shipped CLI behavior | operator docs match the strict replay and comparison contract rather than promising hidden automation | WIRED | Runbook section `## 8. Closed-Loop LLM Workflow` and pipeline-stages sections `## 14`/`## 15` mirror the shipped command sequence and safe defaults. |

### Required Checks

- Focused replay/compare core rerun performed during Phase 15 audit closure:
  - `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_compare_core.py -x -v`
  - Result: `10 passed in 0.19s`
- Focused replay/compare CLI rerun performed during Phase 15 audit closure:
  - `cd materials-discovery && uv run pytest tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py tests/test_cli.py -x -v`
  - Result: `17 passed in 0.37s`
- Existing Phase 12 end-to-end workflow evidence:
  - `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
  - Result: `374 passed, 3 skipped, 1 warning`
- Existing Phase 12 operator-workflow regression evidence from `12-03-SUMMARY.md`:
  - `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "llm_replay or llm_compare or campaign" tests/test_llm_campaign_lineage.py -x -v`
  - Result: `4 passed, 7 deselected`
- `git diff --check`
  - Result: passed during Phase 15 proof-closure execution

### Requirements Coverage

| Requirement | Status | Evidence |
| --- | --- | --- |
| `LLM-09` | ✓ SATISFIED | Replay is driven by recorded launch artifacts rather than mutable approval-time intent. The shipped behavior is implemented in `materials-discovery/src/materials_discovery/llm/replay.py` and `materials-discovery/src/materials_discovery/cli.py`, documented in `materials-discovery/developers-docs/llm-integration.md` (`mdisc llm-replay and llm-compare`) and `materials-discovery/developers-docs/pipeline-stages.md` (`## 14. mdisc llm-replay`), summarized in `12-01-SUMMARY.md`, `12-02-SUMMARY.md`, and `12-03-SUMMARY.md`, and proven by `tests/test_llm_replay_core.py::test_load_campaign_launch_bundle_and_build_replay_config_preserve_recorded_runtime`, `tests/test_llm_replay_core.py::test_build_replay_config_rejects_system_or_template_mismatch`, `tests/test_llm_replay_core.py::test_load_campaign_launch_bundle_requires_full_bundle`, `tests/test_llm_replay_cli.py::test_cli_llm_replay_success`, `tests/test_llm_replay_cli.py::test_cli_llm_replay_records_config_drift_without_failing`, and the offline operator regression `tests/test_real_mode_pipeline.py::test_real_mode_llm_replay_compare_campaign_operator_workflow_offline`. |
| `LLM-11` | ✓ SATISFIED | Comparison always includes the acceptance-pack baseline and includes the most recent prior launch baseline when available. The behavior is implemented in `materials-discovery/src/materials_discovery/llm/compare.py`, surfaced through `materials-discovery/src/materials_discovery/cli.py`, documented in `materials-discovery/developers-docs/llm-integration.md` and `materials-discovery/developers-docs/pipeline-stages.md` (`## 15. mdisc llm-compare` and `### Baseline rules`), summarized in `12-01-SUMMARY.md`, `12-02-SUMMARY.md`, and `12-03-SUMMARY.md`, and proven by `tests/test_llm_compare_core.py::test_build_campaign_outcome_snapshot_persists_launch_and_downstream_metrics`, `tests/test_llm_compare_core.py::test_build_campaign_outcome_snapshot_marks_missing_downstream_metrics_explicitly`, `tests/test_llm_compare_core.py::test_find_prior_campaign_launch_uses_created_at_then_launch_id`, `tests/test_llm_compare_core.py::test_build_campaign_comparison_uses_acceptance_and_prior_snapshot`, `tests/test_llm_compare_cli.py::test_cli_llm_compare_with_prior_launch`, `tests/test_llm_compare_cli.py::test_cli_llm_compare_without_prior_launch_reports_missing_baseline`, and `tests/test_real_mode_pipeline.py::test_real_mode_llm_replay_compare_campaign_operator_workflow_offline`. |
| `OPS-07` | ✓ SATISFIED | The operator workflow is safe, documented, and regression-backed. `materials-discovery/RUNBOOK.md` (`## 8. Closed-Loop LLM Workflow`) documents the safe sequence and audit artifacts, `materials-discovery/developers-docs/pipeline-stages.md` defines the CLI contracts for `llm-replay` and `llm-compare`, and `materials-discovery/developers-docs/llm-integration.md` explains the strict replay posture, immutable outcome snapshots, and manual continuation boundary. The shipped workflow is summarized in `12-02-SUMMARY.md` and `12-03-SUMMARY.md`, and regression-backed by `tests/test_llm_replay_cli.py`, `tests/test_llm_compare_cli.py`, `tests/test_cli.py`, `tests/test_llm_campaign_lineage.py::test_build_pipeline_manifest_accepts_campaign_source_lineage`, and `tests/test_real_mode_pipeline.py::test_real_mode_llm_replay_compare_campaign_operator_workflow_offline`. |

### Residual Caveats

No goal-blocking caveats remain for Phase 12.

Two bounded caveats remain, and both are already part of the shipped Phase 12
design rather than missing proof:

- Replay remains intentionally strict in v1.1. There are no replay override or
  resume flags.
- The workflow remains operator-governed. `llm-launch` and `llm-replay` stop at
  candidate generation plus audit artifacts, and downstream continuation
  remains manual.

These caveats are consistent with the green validation state recorded in
`12-VALIDATION.md`.

### Human Verification Required

No blocking human verification remains for Phase 12 completion.

The manual checks listed in `12-VALIDATION.md` remain useful as an operator
audit companion, especially for replay-summary readability and runbook
usability, but they no longer block milestone traceability because the file-
backed contracts, focused tests, runbook, and end-to-end offline workflow proof
are explicit and current.

### Anti-Patterns Found

No goal-blocking anti-patterns remain.

The issue raised by the v1.1 milestone audit was documentary: Phase 12 had
shipped code, tests, docs, validation, and a final summary, but it was missing
`12-VERIFICATION.md` and the earlier `12-01` / `12-02` summary chain. Phase 15
closes that gap without finding any contradiction between the shipped replay,
comparison, and operator-workflow behavior and the original Phase 12 claims.

### Verification Verdict

**Gap closed.**

Phase 12 is now formally audit-ready:

- strict replay is implemented and proven from recorded launch artifacts
- comparison is implemented and proven against acceptance-pack and prior-launch baselines
- operator workflow docs match the shipped CLI behavior
- validation evidence is current and nyquist-complete
- the missing verification artifact and summary chain now exist

This closes the specific Phase 12 proof gap identified by the v1.1 milestone
audit. The milestone itself is still not archive-ready until Phase 15 finishes
its traceability handoff and the milestone audit is rerun.

---

_Verified: 2026-04-05T00:47:16Z_  
_Verifier: Codex (Phase 15 audit-closure execution)_
