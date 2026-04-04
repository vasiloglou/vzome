# Phase 14 Research: Phase 11 Launch and Lineage Audit Closure

**Completed:** 2026-04-04
**Mode:** Gap-closure evidence research

## Research Question

What evidence already exists to prove `LLM-08`, `LLM-10`, and `OPS-06`, and
what specific artifacts are still missing to make Phase 11 audit-ready?

## Findings

### 1. The shipped Phase 11 behavior already exists

The v1.1 audit says the approved-spec -> `llm-launch` -> downstream pipeline
flow is already verified locally.

Phase 11 shipped three distinct evidence layers:

- launch contract and overlay resolution
  - `11-01-SUMMARY.md`
  - `materials-discovery/src/materials_discovery/common/schema.py`
  - `materials-discovery/src/materials_discovery/llm/schema.py`
  - `materials-discovery/src/materials_discovery/llm/launch.py`
  - `materials-discovery/tests/test_llm_launch_schema.py`
  - `materials-discovery/tests/test_llm_launch_core.py`
- execution bridge and manual-path compatibility
  - `11-02-SUMMARY.md`
  - `materials-discovery/src/materials_discovery/llm/generate.py`
  - `materials-discovery/src/materials_discovery/cli.py`
  - `materials-discovery/tests/test_llm_generate_core.py`
  - `materials-discovery/tests/test_llm_generate_cli.py`
  - `materials-discovery/tests/test_llm_launch_cli.py`
  - `materials-discovery/tests/test_cli.py`
- downstream lineage propagation and pipeline continuity
  - `11-03-SUMMARY.md`
  - `materials-discovery/src/materials_discovery/common/pipeline_manifest.py`
  - `materials-discovery/tests/test_llm_campaign_lineage.py`
  - `materials-discovery/tests/test_report.py`
  - `materials-discovery/tests/test_real_mode_pipeline.py`

### 2. The missing artifacts are again documentary, not architectural

The audit identifies the missing proof directly:

- `11-VERIFICATION.md` does not exist
- `11-VALIDATION.md` is still `status: draft`
- `LLM-08`, `LLM-10`, and `OPS-06` remain pending until the closure phase
  finishes

### 3. Phase 11 needs a broader proof matrix than Phase 10

Phase 10 only had to prove advisory-governance behavior.

Phase 11 has to prove three different things at once:

- `LLM-08`: approved campaign specs launch reproducibly through the bridge
- `LLM-10`: approved campaigns still emit standard artifacts and do not break
  manual `llm-generate`
- `OPS-06`: lineage survives from acceptance pack through launch wrappers,
  generated outputs, downstream manifests, and the pipeline manifest

That means the verification report should likely separate:

1. launch contract and launch-command evidence
2. standard-artifact continuity evidence
3. lineage evidence

### 4. Existing tests are already aligned to that split

The Phase 11 focused test surface is already well partitioned:

- launch schema/core
- `llm-generate` compatibility
- `llm-launch` CLI
- downstream lineage/report propagation
- offline `llm-launch -> screen` compatibility

So Phase 14 should reuse that split rather than inventing a new proof taxonomy.

### 5. No external research is needed

This is a repository-internal gap-closure phase. All needed information is
already present in planning artifacts, shipped code, tests, docs, and the
milestone audit.

## Recommended Planning Posture

- Skip external/domain research.
- Use the audit as the scope authority.
- Rerun the focused launch/lineage slices that matter for proof freshness.
- Keep the phase docs-first and avoid `materials-discovery/` edits unless a
  real evidence mismatch is found.

## Plan Implications

Phase 14 should break into three waves:

1. finalize `11-VALIDATION.md` from fresh focused evidence
2. create `11-VERIFICATION.md`
3. restore `LLM-08`, `LLM-10`, and `OPS-06` traceability and move state to
   Phase 15

---

*Phase: 14-phase-11-launch-and-lineage-audit-closure*
*Research completed: 2026-04-04*
