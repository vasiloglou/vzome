# Phase 7: LLM Inference MVP - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a useful `mdisc llm-generate` path before full training. This phase should
deliver:

- a constrained inference runtime with deterministic mock coverage and one real
  hosted API provider
- config-driven Zomic generation with optional seed-script variation
- parse and compile validation using the existing Zomic bridge/compiler path
- conversion of valid generations into standard `CandidateRecord` JSONL
- an offline benchmark comparing the LLM path to the deterministic generator on
  validity and screen pass-through

This phase does not include local-model serving, `llm-evaluate`, fine-tuning,
free-form operator prompting, or a full hi-fi benchmark lane. Those belong to
later phases.

</domain>

<decisions>
## Implementation Decisions

### Inference runtime
- **D-01:** Phase 7 should satisfy `LLM-02` with `mock` plus one real hosted
  API adapter in v1. Local model serving is explicitly deferred.
- **D-02:** The runtime seam should stay provider-neutral so later phases can
  add local or alternative hosted adapters without reworking the CLI contract.

### Generation envelope
- **D-03:** `mdisc llm-generate` should be config-driven and constrained by the
  existing system/config surface, not a free-form operator chat prompt.
- **D-04:** The MVP generation path should support both fresh generation and
  controlled variation from an optional seed Zomic script.
- **D-05:** Valid generations must be converted into the same standard
  `CandidateRecord` artifact family used by `mdisc generate`, so downstream
  stages can consume them without a schema fork.

### Failure handling
- **D-06:** Parse and compile failures should use a bounded retry loop rather
  than a single-shot drop path.
- **D-07:** Phase 7 should not add a model-driven repair pass. Retries may vary
  sampling or request count, but not run an explicit self-healing prompt loop.
- **D-08:** Every raw completion, parse failure, compile failure, and retry
  outcome must be preserved in run artifacts for later audit and evaluation.

### Evaluation contract
- **D-09:** The MVP offline benchmark should use `Al-Cu-Fe` and `Sc-Zn` as the
  two required systems.
- **D-10:** Phase 7 success should be judged on parse rate, compile rate,
  `CandidateRecord` conversion rate, and screen pass-through versus the existing
  deterministic generator.
- **D-11:** Full hi-fi validation, ranking, and experiment-facing benchmark
  comparisons are deferred to Phase 8.

### Artifact and provenance shape
- **D-12:** Provenance should be rich at the run level: prompt template,
  resolved inputs, seed context, provider/model/settings, retry history, raw
  completions, and parse/compile outcomes.
- **D-13:** Generated `CandidateRecord` rows should stay lighter-weight and link
  back to run-level lineage by stable IDs or paths instead of embedding full raw
  prompt/output transcripts.
- **D-14:** New lineage and benchmark outputs must remain additive and
  file-backed so the current CLI/schema/manifests stay compatible.

### Project-level inheritance from earlier phases
- **D-15:** The no-DFT boundary remains explicit. Generated candidates enter the
  existing no-DFT downstream pipeline rather than introducing a new validation
  stack.
- **D-16:** Phase 7 should build on the implemented `materials_discovery/llm/`
  package, the existing Zomic compiler/bridge, and current file-backed manifest
  conventions rather than inventing a parallel runtime.
- **D-17:** Phase 7 is inference-only. It must not absorb `llm-evaluate`,
  `llm-suggest`, or model fine-tuning work from later roadmap phases.

### the agent's Discretion
- The exact provider chosen for the first hosted API adapter
- The exact prompt template format and sampling knobs, provided generation
  remains config-driven and constrained
- The exact retry count and stop conditions for the bounded retry loop
- The exact storage layout for raw completions and run-level lineage artifacts
- The exact CLI flags for optional seed Zomic input and benchmark execution

</decisions>

<specifics>
## Specific Ideas

- The fastest credible MVP is a hosted-provider-first path that proves the
  `Zomic -> parse -> compile -> CandidateRecord` loop before investing in local
  serving.
- `Sc-Zn` should stay in scope because it exercises the existing Zomic bridge
  path, while `Al-Cu-Fe` provides a strong deterministic generator baseline.
- `mdisc llm-generate` should feel like the existing generator workflow:
  config-led, reproducible, and compatible with later `screen` execution rather
  than a chat-style exploration surface.
- Raw prompt/completion artifacts should live outside the generated candidate
  JSONL so candidate rows stay compact and downstream-safe.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Program controls
- `.planning/PROJECT.md` — overall program sequencing and the rule that LLM
  work must reinforce, not outrun, the trusted data and no-DFT pipeline
- `.planning/ROADMAP.md` — Phase 7 goal, deliverables, and the boundaries
  between inference, evaluation, and fine-tuned model phases
- `.planning/REQUIREMENTS.md` — `LLM-02` as the primary requirement, with
  `LLM-03` to `LLM-05` defining what Phase 7 should not prematurely absorb
- `.planning/STATE.md` — current milestone state and inherited execution notes

### Prior-phase authority
- `.planning/phases/06-zomic-training-corpus-pipeline/06-CONTEXT.md` — locked
  corpus, fidelity, compile, and `materials_discovery/llm/` package decisions
- `.planning/phases/04-reference-aware-no-dft-materials-discovery-v1/04-CONTEXT.md`
  — locked benchmark systems (`Al-Cu-Fe`, `Sc-Zn`) and benchmark artifact
  posture
- `.planning/phases/03-reference-phase-integration-with-current-pipeline/03-CONTEXT.md`
  — additive CLI/schema compatibility and deterministic offline test posture

### LLM and Zomic design docs
- `materials-discovery/developers-docs/llm-integration.md` — planned
  `llm-generate` architecture, provider adapter concepts, and evaluation goals
- `materials-discovery/developers-docs/zomic-llm-data-plan.md` — corpus and
  validation strategy that Phase 7 now consumes as inference input
- `materials-discovery/developers-docs/llm-quasicrystal-landscape.md` — why
  Zomic remains the native representation instead of CIF text generation
- `materials-discovery/developers-docs/zomic-design-workflow.md` — the current
  Zomic compile/export path that the LLM-generated scripts must reuse

### Existing subsystem docs
- `materials-discovery/README.md` — current operator workflows and Zomic-backed
  generation examples
- `materials-discovery/REAL_MODE_EXECUTION_PLAN.md` — current hardening posture
  and compatibility expectations for new runtime paths
- `materials-discovery/developers-docs/architecture.md` — package boundaries,
  planned `llm` runtime placement, and CLI orchestration posture
- `materials-discovery/developers-docs/pipeline-stages.md` — current CLI
  contracts, JSON summary behavior, and the planned `llm-generate` stage shape
- `materials-discovery/developers-docs/configuration-reference.md` — existing
  `SystemConfig` and backend config seams that Phase 7 should extend carefully
- `materials-discovery/developers-docs/data-schema-reference.md` — schema
  conventions, persisted record posture, and additive contract expectations

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/src/materials_discovery/llm/compiler.py`: existing parse
  and compile seam for Zomic scripts
- `materials-discovery/src/materials_discovery/llm/schema.py`: established
  provenance, validation-state, and manifest-oriented schema patterns inside the
  LLM package
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`:
  existing bridge from Zomic to labeled geometry/orbit exports
- `materials-discovery/src/materials_discovery/generator/candidate_factory.py`:
  existing candidate construction and provenance patterns
- `materials-discovery/src/materials_discovery/common/schema.py`: current
  `SystemConfig`, `CandidateRecord`, and stage-summary contracts
- `materials-discovery/src/materials_discovery/cli.py`: current typer command
  patterns, shared error handling, JSON summary output, and `llm-corpus`
  integration examples

### Established Patterns
- File-backed JSON and JSONL artifacts under `materials-discovery/data/`
- Additive manifests and calibration/summary sidecars rather than in-place
  schema replacement
- Deterministic `mock` coverage plus adapter/provider seams for richer modes
- Offline fixture-based tests that avoid live network or provider dependencies
- CLI commands that validate config with Pydantic and print JSON summaries on
  success

### Integration Points
- `materials-discovery/src/materials_discovery/cli.py` for the new
  `llm-generate` command and any benchmark helper wiring
- `materials-discovery/src/materials_discovery/llm/` as the implementation home
  for provider adapters, prompt assembly, retry handling, and run artifacts
- `materials-discovery/data/candidates/` as the likely home for standard
  `CandidateRecord` JSONL outputs from successful inference runs
- `materials-discovery/tests/test_llm_corpus_cli.py`,
  `materials-discovery/tests/test_llm_projection2zomic.py`, and
  `materials-discovery/tests/test_cli.py` as anchors for new Phase 7 test shape

</code_context>

<deferred>
## Deferred Ideas

- Local model serving and local adapter benchmarking — later phase once the
  hosted-provider path is proven
- Free-form operator prompting or chat-style generation surfaces — out of scope
  for this config-driven MVP
- Model-driven repair loops that feed parse/compile errors back into the model —
  possible later hardening step, but not part of Phase 7
- Full hi-fi validation, ranking, and report-side LLM benchmarking — Phase 8
- `llm-evaluate`, `llm-suggest`, and fine-tuned model training — later roadmap
  phases

</deferred>

---

*Phase: 07-llm-inference-mvp*
*Context gathered: 2026-04-03*
