# Roadmap: Materials Design Program

**Milestone:** `v1.2`
**Focus:** Project 3 expansion - Local and Specialized LLM Serving MVP
**Numbering mode:** continue after `v1.1` (`Phase 19+`)

## Milestone Summary

This milestone extends the shipped `v1.1` closed-loop LLM campaign workflow.

`v1.1` proved that the platform can:
- generate typed campaign proposals from acceptance packs
- require explicit operator approval before execution
- launch approved campaigns through the existing `llm-generate` path
- replay and compare launched campaigns safely and reproducibly

`v1.2` turns the current hosted-plus-mock LLM seam into a real multi-lane
serving surface:
- local serving becomes a first-class execution target
- specialized materials-model lanes become real, not just metadata
- operators can compare hosted, local, and specialized lanes inside the same
  governed workflow

Important scope note: off-the-shelf specialized materials models are not
assumed to understand Zomic notation natively. In this milestone, a
specialized lane may prove its value through generation-adjacent reasoning,
synthesis-aware evaluation, or another workflow role that fits the existing
contracts honestly.

## Phase Roadmap

## Phase 19: Local Serving Runtime and Lane Contracts

**Goal:** add the runtime contracts, config surface, and diagnostics needed to
execute `llm-generate` and campaign launches through local and lane-aware model
serving without breaking the current hosted/manual workflow.

**Deliverables**

- additive local-serving adapter contract under `materials_discovery/llm/`
- config/schema support for local endpoints or local model/checkpoint
  identifiers
- deterministic lane resolution for `general_purpose` and
  `specialized_materials`
- clear operator-facing errors for missing dependencies, unavailable lanes,
  invalid endpoints, and unresolvable serving config

**Primary requirements**

- `LLM-13`, `LLM-14`, `OPS-08`

**Success criteria**

1. `mdisc llm-generate` can target a configured local serving lane without
   changing standard candidate or manifest contracts.
2. Manual generation and approved campaign launches resolve model lanes
   deterministically and record whether a lane was explicitly configured or
   selected by default.
3. Invalid or unavailable local/specialized serving configs fail early with
   clear diagnostics rather than late provider errors.
4. Existing mock and hosted paths remain backward-compatible.

**Notes**

- This phase should add serving capability, not introduce autonomous behavior.

## Phase 20: Specialized Lane Integration and Workflow Compatibility

**Goal:** integrate local and specialized model lanes into the shipped closed
loop so generation, evaluation, launch, replay, and lineage remain compatible
across serving modes.

**Deliverables**

- one specialized-materials lane with a real workflow role beyond generic
  hosted prompting
- additive run and candidate lineage for local/specialized provider details
- campaign launch, replay, and compare compatibility for local/specialized runs
- lane-aware evaluation or generation wiring that stays within the current
  no-DFT pipeline contracts

**Primary requirements**

- `LLM-15`, `LLM-16`, `OPS-09`

**Success criteria**

1. At least one specialized-materials lane is operationally meaningful in the
   workflow, not just declared in config.
2. `llm-launch`, `llm-replay`, and `llm-compare` remain green when the
   originating run used local or specialized serving.
3. Run artifacts preserve auditable provider, model, checkpoint, and serving
   endpoint/path lineage.
4. The milestone keeps the no-DFT boundary explicit and does not invent a
   separate nonstandard pipeline path for local models.

**Notes**

- The first specialized lane may be stronger for synthesis-aware assessment than
  for raw Zomic generation; the phase should choose the highest-value supported
  role instead of forcing symmetry between tasks.
- Zomic-native local generation is a likely follow-on milestone once the team
  has stable hosted/local/specialized serving baselines and can benchmark any
  adapted checkpoints responsibly.

## Phase 21: Comparative Benchmarks and Operator Serving Workflow

**Goal:** make the new serving lanes usable and measurable for operators
through comparative benchmarks, smoke tests, and a stable runbook.

**Deliverables**

- benchmark workflow comparing hosted, local, and specialized lanes against the
  same acceptance or benchmark context
- operator-facing smoke-test and fallback procedure for serving setup
- runbook updates for setup, lane selection, failure diagnosis, and comparison
- regression coverage protecting the new serving workflow boundaries

**Primary requirements**

- `LLM-17`, `OPS-10`

**Success criteria**

1. Operators can compare hosted, local, and specialized lanes against the same
   benchmark context without hand-assembling artifacts.
2. The runbook explains setup, smoke testing, fallback, and when to prefer one
   lane over another.
3. The serving workflow remains reproducible and file-backed.
4. The milestone ends with a benchmarkable, operator-usable serving surface,
   not just an adapter hidden behind tests.

**Notes**

- Fully autonomous campaign execution remains out of scope until the expanded
  serving surface proves reliable in operator hands.

## Scope Boundaries

- This milestone does **not** add fully autonomous campaign execution.
- This milestone does **not** make new chemistry breadth the headline.
- This milestone does **not** require training a foundation model from scratch.
- This milestone does **not** replace the current CLI/file-backed workflow with
  a UI-first orchestration layer.

## Previous Milestones

- `v1.1` archive: `.planning/milestones/v1.1-ROADMAP.md`
- `v1.0` archive: `.planning/milestones/v1.0-ROADMAP.md`
