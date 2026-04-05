# Phase 22 Research: Phase 19 Verification and Validation Audit Closure

**Completed:** 2026-04-05  
**Mode:** Gap-closure evidence research

## Research Question

What evidence already exists to prove `LLM-13`, `LLM-14`, and `OPS-08`, and
what specific artifacts are still missing to make Phase 19 audit-ready?

## Findings

### 1. The shipped behavior already exists

The v1.2 audit explicitly says the Phase 19 feature set is implemented and the
cross-phase wiring looks green:

- local serving, lane resolution, and replay-safe serving identity are already
  shipped
- summary artifacts exist for `19-01`, `19-02`, and `19-03`
- focused tests exist for schema, runtime, generate, launch, replay, and CLI

This means Phase 22 should be a proof-and-traceability phase, not a feature
rebuild.

### 2. The missing artifact is not ambiguous

The audit names the missing proof directly:

- `19-VERIFICATION.md` does not exist
- `19-VALIDATION.md` is still `status: draft`
- the audit classifies `LLM-13`, `LLM-14`, and `OPS-08` as `orphaned` because
  the formal phase verification chain is incomplete

### 3. Existing evidence is strong enough to support a formal verification report

Phase 19 already has three strong evidence layers:

- planning intent
  - `19-CONTEXT.md`
  - `19-RESEARCH.md`
  - `19-VALIDATION.md`
- execution evidence
  - `19-01-SUMMARY.md`
  - `19-02-SUMMARY.md`
  - `19-03-SUMMARY.md`
- runtime/tests/docs
  - `materials-discovery/src/materials_discovery/llm/runtime.py`
  - `materials-discovery/src/materials_discovery/llm/generate.py`
  - `materials-discovery/src/materials_discovery/llm/launch.py`
  - `materials-discovery/src/materials_discovery/llm/replay.py`
  - `materials-discovery/src/materials_discovery/cli.py`
  - `materials-discovery/tests/test_llm_launch_schema.py`
  - `materials-discovery/tests/test_llm_runtime.py`
  - `materials-discovery/tests/test_llm_generate_core.py`
  - `materials-discovery/tests/test_llm_generate_cli.py`
  - `materials-discovery/tests/test_llm_launch_core.py`
  - `materials-discovery/tests/test_llm_launch_cli.py`
  - `materials-discovery/tests/test_llm_replay_core.py`
  - `materials-discovery/tests/test_cli.py`

### 4. The risky ambiguity is traceability, not implementation

The main planning risk is not whether the code works. It is whether the final
audit will understand the proof chain after the v1.2 requirements were remapped
into Phase 22.

That suggests execution should:

- create `19-VERIFICATION.md` because the audit explicitly calls it missing
- make `19-VALIDATION.md` unambiguously final and current
- update `REQUIREMENTS.md` only after proof exists
- leave a clear state handoff so later audit reruns understand that Phase 22
  closed the Phase 19 proof gap

### 5. No external research is needed

This is a repository-internal closure phase. All needed information is already
present locally in planning artifacts, shipped code, tests, and the milestone
audit.

## Recommended Planning Posture

- Skip external/domain research.
- Use the audit as the scope authority.
- Plan for one fresh focused pytest rerun so the verification artifact is based
  on current evidence, not only historical summary text.
- Keep the phase docs-first and avoid `materials-discovery/` edits unless an
  actual mismatch is found during evidence refresh.
- Close the Phase 22 self-verification loop during execution so the milestone
  does not immediately create a new documentary debt phase.

## Plan Implications

Phase 22 should break into three waves:

1. finalize `19-VALIDATION.md` from real evidence
2. create `19-VERIFICATION.md`
3. restore requirement/state traceability and close the Phase 22 documentary
   loop

---

*Phase: 22-phase-19-verification-and-validation-audit-closure*  
*Research completed: 2026-04-05*
