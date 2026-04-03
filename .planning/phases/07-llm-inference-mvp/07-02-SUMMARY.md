---
phase: 07-llm-inference-mvp
plan: 02
subsystem: llm-generate-core
tags: [llm, generation, prompts, compile, candidate-conversion, cli]
requires:
  - phase: 07-llm-inference-mvp
    provides: typed llm runtime contracts, adapter seam, llm_generate config block
provides:
  - config-driven prompt assembly and seed loading
  - bounded retry llm generation engine with run artifacts
  - compile-backed conversion into standard CandidateRecord JSONL
  - operator-facing mdisc llm-generate command
affects: [phase-07, llm, cli, candidate-generation, configs]
tech-stack:
  added: [llm generation engine, prompt builder, llm calibration metrics]
  patterns: [compile-authoritative validation, persisted attempt audit trail, additive candidate provenance]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/prompting.py
    - materials-discovery/src/materials_discovery/llm/generate.py
    - materials-discovery/configs/systems/al_cu_fe_llm_mock.yaml
    - materials-discovery/configs/systems/sc_zn_llm_mock.yaml
    - materials-discovery/tests/test_llm_generate_core.py
    - materials-discovery/tests/test_llm_generate_cli.py
  modified:
    - materials-discovery/src/materials_discovery/llm/compiler.py
    - materials-discovery/src/materials_discovery/generator/candidate_factory.py
    - materials-discovery/src/materials_discovery/common/stage_metrics.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/Progress.md
key-decisions:
  - "Keep the Java/vZome bridge as the only parse/compile authority; the Python layer only classifies returned failures and persists them."
  - "Convert successful llm outputs into standard CandidateRecord rows by loading compiled orbit-library JSON, not by reusing the Z[phi] perturbation branch."
  - "Use a deterministic run directory keyed by config hash, requested count, temperature, and seed path so llm runs are reproducible and auditable."
patterns-established:
  - "Phase 7 engine pattern: prompt.json + attempts.jsonl + compile_results.jsonl + run_manifest.json under data/llm_runs/{system}_{hash}/."
  - "llm candidate provenance stays additive inside CandidateRecord.provenance instead of introducing a separate candidate schema."
requirements-completed: [LLM-02]
duration: 35min
completed: 2026-04-03
---

# Phase 7: Plan 02 Summary

**Config-driven llm-generate core, compile-backed candidate conversion, and CLI wiring**

## Performance

- **Duration:** 35 min
- **Completed:** 2026-04-03T23:25:00Z
- **Tasks:** 2
- **Files modified:** 13

## Accomplishments

- Added `llm/prompting.py` and `llm/generate.py` to build concrete prompts, validate optional seed scripts, run bounded retries, and persist per-attempt artifacts.
- Extended the compile seam so llm attempts now record parse/compile status, stable error kinds, and persisted raw-export/orbit-library paths.
- Added `build_candidate_from_prototype_library(...)` so compiled llm outputs become normal `CandidateRecord` rows without reusing the generator’s Z[phi] mutation path.
- Wired `mdisc llm-generate` into the CLI with calibration JSON, stage-manifest emission, and committed mock configs for `Al-Cu-Fe` and `Sc-Zn`.
- Added focused core/CLI coverage and verified the full `materials-discovery` suite stays green after the shared-factory refactor.

## Task Commits

This plan was checkpointed as one combined commit after the focused and full-suite verification passes.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/prompting.py` - prompt builder and seed loader
- `materials-discovery/src/materials_discovery/llm/generate.py` - bounded retry engine and run-artifact writer
- `materials-discovery/src/materials_discovery/llm/compiler.py` - persisted compile outputs and explicit error taxonomy
- `materials-discovery/src/materials_discovery/generator/candidate_factory.py` - compiled-template candidate helper
- `materials-discovery/src/materials_discovery/common/stage_metrics.py` - llm generation calibration metrics
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Phase 7 exports
- `materials-discovery/src/materials_discovery/cli.py` - `llm-generate` command
- `materials-discovery/configs/systems/al_cu_fe_llm_mock.yaml` - committed mock inference config
- `materials-discovery/configs/systems/sc_zn_llm_mock.yaml` - committed mock inference config with seed path
- `materials-discovery/tests/test_llm_generate_core.py` - engine and retry coverage
- `materials-discovery/tests/test_llm_generate_cli.py` - CLI coverage
- `materials-discovery/tests/test_cli.py` - seed-error regression coverage
- `materials-discovery/Progress.md` - required materials-discovery progress update

## Decisions Made

- Kept `llm-generate` config-driven and seed-aware, but not a free-form chat interface.
- Counted parse and compile passes per attempt, then left richer prompt/raw-output lineage in the separate run manifest instead of bloating stage manifests.
- Treated provider and conversion failures as explicit attempt outcomes so retries stay auditable rather than silently swallowing bad generations.

## Deviations from Plan

- None. The core engine, CLI surface, mock configs, and required regression lanes all landed in this plan.

## Issues Encountered

- The only mid-plan hiccup was a patch-context mismatch while updating docs; the fix was to split the patch and reapply with exact anchors. No code or test regressions resulted.

## User Setup Required

- None for mock mode. The committed `*_llm_mock.yaml` configs are runnable without network access.

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_cli.py -x -v`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
- `git diff --check`

## Next Phase Readiness

Plan 03 can now build the offline benchmark comparison layer against a real `mdisc llm-generate` command instead of a stubbed design.

---
*Phase: 07-llm-inference-mvp*
*Completed: 2026-04-03*
