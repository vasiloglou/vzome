# Phase 20: Specialized Lane Integration and Workflow Compatibility - Research

**Date:** 2026-04-05  
**Status:** Complete  
**Requirements:** `LLM-15`, `LLM-16`, `OPS-09`

## Goal

Make at least one `specialized_materials` lane operationally meaningful inside
the shipped closed-loop workflow without pretending that off-the-shelf
materials models are already strong direct Zomic generators.

Phase 20 must:

- use one real specialized lane for an honest workflow role
- keep `llm-generate`, `llm-launch`, `llm-replay`, and `llm-compare`
  compatible when local or specialized serving is involved
- preserve auditable serving lineage across generation, evaluation, launch,
  replay, and comparison artifacts
- stay additive to the existing file-backed, operator-governed, no-DFT system

Phase 20 must not:

- fork a specialized-only pipeline
- force a direct-generation use case that the first specialized model cannot
  support honestly
- turn Phase 20 into the full comparative benchmark milestone
- weaken the explicit fallback and replay-identity rules introduced in Phase 19

## Current Surface

### Phase 19 already solved lane-aware generation and replay identity

The repo now has:

- shared serving-lane resolution through the generation and launch path
- additive `serving_identity` on run and launch artifacts
- explicit fallback semantics
- replay-safe hard identity vs transport-drift handling

Relevant files:

- `materials-discovery/src/materials_discovery/llm/runtime.py`
- `materials-discovery/src/materials_discovery/llm/generate.py`
- `materials-discovery/src/materials_discovery/llm/launch.py`
- `materials-discovery/src/materials_discovery/llm/replay.py`
- `materials-discovery/src/materials_discovery/llm/compare.py`

That means Phase 20 does **not** need a new serving framework. It needs to
make the specialized lane meaningful inside the existing one.

### `llm-evaluate` is the clearest specialized-lane insertion point

The existing evaluation path already speaks the right conceptual language for
specialized materials models:

- synthesizability score
- precursor hints
- anomaly flags
- literature context
- rationale

Relevant files:

- `materials-discovery/src/materials_discovery/llm/evaluate.py`
- `materials-discovery/src/materials_discovery/llm/schema.py`
- `materials-discovery/tests/test_llm_evaluate_schema.py`
- `materials-discovery/tests/test_llm_evaluate_cli.py`

What is missing today:

- `llm-evaluate` cannot choose a serving lane explicitly
- evaluation artifacts do not yet carry the richer lane-aware serving identity
- compare/report logic sees LLM assessment results, but not a first-class
  evaluation-lane lineage story

### Existing configs already reserve the lane, but not the role

Phase 19 committed:

- `materials-discovery/configs/systems/al_cu_fe_llm_local.yaml`
- `materials-discovery/configs/systems/sc_zn_llm_local.yaml`

Both already define `general_purpose` and `specialized_materials` under
`llm_generate.model_lanes`, but they do not yet give `llm-evaluate` or
operator docs a concrete specialized-lane behavior.

## Key Design Findings

### 1. Evaluation-primary is the honest first specialized-lane role

The docs and landscape research are consistent:

- CrystaLLM / CrystalTextLLM / MatLLMSearch are strong precedent for
  periodic-crystal text generation, but not for direct quasicrystal/Zomic
  generation
- CSLLM-style models are a much cleaner fit for synthesizability, precursor,
  and materials plausibility tasks

So the best Phase 20 cut is:

- keep generation compatibility across all lane-aware commands
- make the first specialized lane operationally meaningful through
  `llm-evaluate` and additive downstream interpretation

This satisfies the milestone honestly instead of inflating a weak direct
generation claim.

### 2. `llm-evaluate` should reuse the Phase 19 lane resolver

Phase 19 already pinned the serving-lane contract. Phase 20 should not invent a
second resolver for evaluation.

Recommended additive seam:

- add a single evaluation-lane selector such as
  `llm_evaluate.model_lane: Literal["general_purpose", "specialized_materials"] | None`
- let CLI `--model-lane` override that value
- resolve the winning lane through the shared Phase 19 serving-lane helper
- preserve the same explicit fallback rules

That keeps config authoritative and avoids divergent lane semantics across
generate, evaluate, launch, and replay.

### 3. Evaluation artifacts need the same lineage richness as generation artifacts

Current evaluation artifacts record:

- adapter key
- provider
- model

Phase 20 needs additive evaluation lineage that mirrors generation lineage:

- requested lane
- resolved lane
- resolved-lane source
- `serving_identity`

Recommended places to add this:

- `LlmAssessment`
- `LlmEvaluationRunManifest`
- `LlmEvaluateSummary`
- candidate provenance block under `llm_assessment`

Without this, operators can see that an assessment ran, but not which exact
specialized lane or endpoint produced it.

### 4. Comparison and reporting need both generation and evaluation lane context

`llm/compare.py` and report surfaces already aggregate:

- generation success rates
- downstream stage metrics
- synthesizability mean

But the current outcome snapshot is still generation-centric. Phase 20 needs to
surface both:

- the generation lane / serving identity that produced the candidate run
- the evaluation lane / serving identity that produced the assessment metrics

The right approach is additive:

- preserve the existing artifact shapes
- extend comparison and report evidence with explicit specialized-lane lineage
- do not create specialized-only output files

### 5. One real system plus one thin proof is the right scope

The milestone context already locked this, and the current configs support it
well.

Recommended proof split:

- **Real proof:** `Al-Cu-Fe`
  - simpler current local lane config
  - no extra `seed_zomic` dependency in the config itself
  - good candidate for the first specialized evaluation lane story
- **Thin compatibility proof:** `Sc-Zn`
  - already has a seeded local LLM workflow
  - good place to prove that specialized lineage does not break launch/replay
    or downstream compatibility

This keeps Phase 20 focused and leaves broader benchmark parity to Phase 21.

### 6. A runnable OpenAI-compatible specialized endpoint is sufficient for v1.2

Phase 20 does not need to solve model packaging as a separate problem.

The serving contract from Phase 19 already allows:

- local OpenAI-compatible servers
- proxied specialized endpoints that still look OpenAI-compatible

The important thing for Phase 20 is that the specialized lane is **real**,
lane-aware, and traceable. The plan should therefore:

- prefer local where available
- accept a compatible specialized endpoint when that is the practical way to
  prove the lane
- keep all tests offline by monkeypatching the endpoint path

## Recommended Implementation Split

### Plan 01: lane-aware evaluation foundation

Land the specialized-lane seam where it is most honest:

- extend `llm_evaluate` config with a lane selector
- add additive evaluation serving identity to typed artifacts
- reuse the Phase 19 lane resolver and readiness checks in `llm-evaluate`
- keep legacy evaluation configs and artifacts readable

This plan satisfies the foundational part of `LLM-15` and `OPS-09`.

### Plan 02: real specialized-lane proof and compatibility propagation

Once evaluation is lane-aware:

- wire `mdisc llm-evaluate --model-lane ...`
- make one real system config use `specialized_materials` for evaluation
- propagate specialized evaluation lineage into compare/report/campaign
  compatibility surfaces
- prove launch/replay/compare remain green when specialized lineage is present

This is the main `LLM-15` / `LLM-16` / `OPS-09` plan.

### Plan 03: second-system compatibility proof and additive docs

After the real proof is stable:

- add the thinner second-system proof
- lock end-to-end real-mode regression coverage
- update docs to explain the evaluation-primary specialized-lane role,
  compatibility boundaries, and operator expectations

This keeps Phase 20 honest and hands Phase 21 a clean benchmark baseline.

## Risks and Edge Cases To Lock In Planning

### Specialized lane role drift

If the plan tries to make the first specialized lane “also” a strong Zomic
generator, it will likely dilute the phase and create noisy acceptance
criteria. The plan should explicitly treat direct generation as compatibility,
not the headline proof.

### Artifact-shape drift

Comparison and report outputs should gain richer lineage, but their existing
machine-readable structure should remain stable. Otherwise Phase 20 would spend
time rebreaking the workflow Phase 11 and Phase 12 just stabilized.

### Replay confusion between generation identity and evaluation identity

The compare/replay story now has two identities that can matter:

- generation lane
- evaluation lane

The plan must keep these distinct rather than flattening them into one generic
“model” label.

### Overcommitting system scope

Trying to run the full proof equally on both `Al-Cu-Fe` and `Sc-Zn` would turn
Phase 20 into an early benchmark phase. The plan should keep one system as the
deep proof and the other as a compatibility guard.

## Planning Implications

- Phase 20 should be **three plans in three waves**.
- Wave 1 should establish the evaluation-lane contract before CLI or compare
  work expands the regression surface.
- Wave 2 should make the specialized lane real on `Al-Cu-Fe` and propagate its
  lineage into compare/report/campaign compatibility.
- Wave 3 should use `Sc-Zn` as the thinner compatibility proof and finish the
  additive docs/regression story.
