# Phase 15 Research: Phase 12 Replay and Operator Workflow Audit Closure

**Completed:** 2026-04-04
**Mode:** Gap-closure evidence research

## Research Question

What evidence already exists to prove `LLM-09`, `LLM-11`, and `OPS-07`, and
what specific artifacts are still missing to make Phase 12 audit-ready?

## Findings

### 1. The shipped Phase 12 behavior already exists

The v1.1 audit says the launch -> replay -> compare flow is already verified
locally and not currently broken.

Phase 12 shipped three distinct evidence layers, but only the last one has a
committed summary artifact today:

- replay/comparison foundation
  - `12-01-PLAN.md`
  - `materials-discovery/src/materials_discovery/llm/schema.py`
  - `materials-discovery/src/materials_discovery/llm/storage.py`
  - `materials-discovery/src/materials_discovery/llm/replay.py`
  - `materials-discovery/src/materials_discovery/llm/compare.py`
  - `materials-discovery/tests/test_llm_replay_core.py`
  - `materials-discovery/tests/test_llm_compare_core.py`
- CLI workflow and output surface
  - `12-02-PLAN.md`
  - `materials-discovery/src/materials_discovery/cli.py`
  - `materials-discovery/tests/test_llm_replay_cli.py`
  - `materials-discovery/tests/test_llm_compare_cli.py`
  - `materials-discovery/tests/test_cli.py`
- operator workflow and end-to-end proof
  - `12-03-SUMMARY.md`
  - `materials-discovery/RUNBOOK.md`
  - `materials-discovery/developers-docs/llm-integration.md`
  - `materials-discovery/developers-docs/pipeline-stages.md`
  - `materials-discovery/tests/test_real_mode_pipeline.py`
  - `materials-discovery/tests/test_llm_campaign_lineage.py`

### 2. The missing artifacts are documentary, not architectural

The audit identifies the Phase 12 gaps directly:

- `12-VERIFICATION.md` does not exist
- `REQUIREMENTS.md` still leaves `LLM-09`, `LLM-11`, and `OPS-07` pending
- Phase 12 only has a `12-03-SUMMARY.md`, while `12-01-SUMMARY.md` and
  `12-02-SUMMARY.md` are missing from the expected proof chain

Unlike Phase 13 and Phase 14, `12-VALIDATION.md` is already green and does not
appear to be the primary audit blocker.

### 3. Phase 12 needs both a summary-chain repair and a verification report

The proof gap is wider than “missing one file.” The audit wants:

- plan-level evidence for the replay/comparison foundation
- plan-level evidence for the CLI/operator surface
- a formal verification artifact that proves replay, comparison, and operator
  workflow safety

That suggests Phase 15 should explicitly recreate the missing summary chain
before drafting `12-VERIFICATION.md`.

### 4. Existing tests already align to that split

The focused Phase 12 test surface already maps neatly to the missing summaries:

- `test_llm_replay_core.py` and `test_llm_compare_core.py` for the replay and
  comparison contract foundation
- `test_llm_replay_cli.py`, `test_llm_compare_cli.py`, and `test_cli.py` for
  the CLI/operator surface
- `test_real_mode_pipeline.py` and `test_llm_campaign_lineage.py` for the
  end-to-end workflow already captured by `12-03-SUMMARY.md`

So the cleanest planning posture is to reuse that existing split rather than
invent a new audit taxonomy.

### 5. No external research is needed

This is a repository-internal gap-closure phase. All needed information is
already present in planning artifacts, shipped code, tests, docs, and the
milestone audit.

## Recommended Planning Posture

- Skip external/domain research.
- Use the audit as the scope authority.
- Rerun the narrow replay/compare core and CLI slices for proof freshness.
- Reuse the already-green `12-VALIDATION.md` unless the new summary chain
  exposes a real contradiction.
- Keep the phase docs-first and avoid `materials-discovery/` edits unless a
  real proof mismatch is found.

## Plan Implications

Phase 15 should break into three waves:

1. create `12-01-SUMMARY.md` and `12-02-SUMMARY.md` from fresh focused evidence
2. create `12-VERIFICATION.md`
3. restore `LLM-09`, `LLM-11`, and `OPS-07` traceability and hand off to a
   milestone audit rerun

---

*Phase: 15-phase-12-replay-and-operator-workflow-audit-closure*
*Research completed: 2026-04-04*
