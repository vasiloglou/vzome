# Phase 7 Research: LLM Inference MVP

**Phase:** 07  
**Date:** 2026-04-03  
**Goal:** Plan the first useful `llm-generate` path so the repo can turn
constrained LLM-produced Zomic into standard `CandidateRecord` artifacts and
judge that path against the existing deterministic generator.

## Research Question

What do we need to know to plan Phase 7 well so that the team can:

- add a provider-neutral LLM runtime with deterministic `mock` coverage and one
  real hosted API provider
- keep generation config-driven rather than turning the CLI into a chat surface
- validate generated Zomic through the existing compile bridge and preserve rich
  run-level provenance
- emit standard `CandidateRecord` JSONL that can flow into `screen`
- benchmark the LLM path against the deterministic generator without pulling
  full hi-fi comparison into the MVP

## Key Findings

### 1. Phase 6 already built the right substrate for Phase 7

The repo now has a real `materials_discovery/llm/` package with:

- corpus schemas and provenance models in
  `materials-discovery/src/materials_discovery/llm/schema.py`
- a compile seam in
  `materials-discovery/src/materials_discovery/llm/compiler.py`
- corpus build storage/manifests/QA patterns that already match the project’s
  file-backed architecture
- `mdisc llm-corpus build` wired through `cli.py`

Phase 7 should therefore extend the existing `llm/` package rather than
creating a separate runtime namespace. The clean additive shape is:

```text
materials_discovery/llm/
  runtime.py        adapter protocol + provider resolution
  prompting.py      config-driven prompt assembly
  generate.py       generation loop, retries, validation, candidate conversion
```

### 2. The current compile helper is useful, but too coarse for Phase 7 metrics

`materials-discovery/src/materials_discovery/llm/compiler.py` currently:

- writes a temporary `.zomic` file and design YAML
- calls `export_zomic_design(...)`
- returns a simple dict with `parse_status`, `compile_status`, and
  `error_message`

The important limitation is that it treats any bridge failure as both
`parse_status="failed"` and `compile_status="failed"`. That was acceptable for
Phase 6 corpus grading, but Phase 7 explicitly wants:

- parse rate
- compile rate
- bounded retries with better diagnostics
- run-level auditability for each raw completion

Planning implication: Phase 7 should **extend** the compile/validation seam so
the runtime can record a richer per-attempt result model. It should not invent a
second parser authority in Python, but it does need a clearer failure taxonomy
than “bridge threw an exception.”

### 3. `CandidateRecord` conversion can reuse the existing generator path

There is no dedicated “orbit library to candidate” helper today, but the repo
already has almost everything needed:

- `generator/zomic_bridge.py` turns Zomic into orbit-library JSON
- `generator/approximant_templates.py` can load orbit-library JSON back into an
  `ApproximantTemplate`
- `generator/candidate_factory.py` already knows how to turn a template plus
  system composition bounds into a standard `CandidateRecord`

That means Phase 7 does not need a brand-new candidate schema or a second
generation artifact family. The right planning move is to extract or add a
small helper around the existing candidate-factory logic so `llm-generate` can
build one candidate per validated orbit-library template while preserving
standard provenance and downstream compatibility.

### 4. The configuration seam is not ready for LLM generation yet

`materials-discovery/src/materials_discovery/common/schema.py` currently exposes
backend configuration for ingest and the hi-fi stages, but nothing yet for LLM
generation. The docs in
`materials-discovery/developers-docs/llm-integration.md` suggest adding fields
such as:

- `llm_adapter`
- `llm_provider`
- `llm_model`
- `llm_temperature`
- `llm_max_tokens`

However, not all of those belong in the same layer.

Recommended split:

- keep **execution-lane selection** in `BackendConfig`
  - `llm_adapter`
  - `llm_provider`
  - `llm_model`
  - optional `llm_api_base`
- add a dedicated **generation-behavior config** under `SystemConfig`
  - prompt template ID
  - retry count / attempt budget
  - default temperature / max tokens
  - seed-Zomic defaults
  - raw-artifact root override

This keeps provider selection aligned with the existing backend pattern while
avoiding an overloaded `backend:` block for every generation detail.

### 5. Hosted-provider support should stay dependency-light

`materials-discovery/pyproject.toml` currently includes:

- base runtime deps: `typer`, `pydantic`, `pyyaml`, `numpy`
- optional `ingestion` deps: `httpx`, `pymatgen`

There is no current dependency on vendor SDKs such as `anthropic` or `openai`.
That matters for Phase 7. The safest planning posture is:

- reuse lazy `httpx` import patterns already established for ingestion adapters
- avoid making a provider SDK mandatory for the default install
- keep the real hosted adapter easy to skip in offline tests

This also fits the user’s choice to keep the first real provider in scope
without making the repo fragile in environments that only need `mock`.

### 6. CLI behavior should mirror the existing stage contract exactly

The current CLI contract documented in
`materials-discovery/developers-docs/pipeline-stages.md` is consistent:

- load config with Pydantic
- error to stderr with exit code `2` on bad input/runtime failures
- write JSON/JSONL artifacts under `data/`
- emit calibration JSON and manifest JSON
- print a JSON summary object to stdout

Phase 7 should follow the same pattern with:

- candidates JSONL under `data/candidates/{slug}_llm_candidates.jsonl`
- calibration JSON under `data/calibration/{slug}_llm_generation_metrics.json`
- manifest under `data/manifests/{slug}_llm_generate_manifest.json`
- run-level raw attempts under a new additive location such as
  `data/llm_runs/{run_id}/`

That preserves `OPS-04`-style compatibility without requiring a CLI version
break.

### 7. The benchmark should be screen-level, not hi-fi, in this phase

The user locked the MVP benchmark to:

- `Al-Cu-Fe`
- `Sc-Zn`
- parse rate
- compile rate
- `CandidateRecord` conversion rate
- screen pass-through against the deterministic generator

This aligns well with current repo seams:

- `Sc-Zn` exercises the Zomic bridge path
- `Al-Cu-Fe` gives a strong non-Zomic deterministic baseline
- `screen` is already fast and deterministic enough for offline benchmark work

Planning implication: Phase 7 should stop at **generation + screen comparison**
and defer full hi-fi/rank/report comparisons to Phase 8.

### 8. Rich provenance belongs at the run layer, not inside every candidate row

Phase 7 decisions explicitly separate:

- heavy run lineage
  - prompt template
  - resolved inputs
  - model/provider/settings
  - retry history
  - raw completions
  - per-attempt parse/compile outcomes
- lighter candidate provenance
  - `source: "llm"`
  - run ID or run manifest path
  - chosen attempt ID
  - model identity / adapter tag if needed for downstream filtering

This is important because `CandidateRecord` rows already flow through the rest
of the pipeline. Embedding raw prompt/output transcripts into each row would
inflate artifacts and couple downstream stages to Phase 7 internals.

### 9. Phase 7 needs new focused tests rather than only extending broad suites

The repo already has strong patterns for focused Typer and stage tests:

- `materials-discovery/tests/test_cli.py`
- `materials-discovery/tests/test_llm_corpus_cli.py`
- `materials-discovery/tests/test_llm_projection2zomic.py`

Phase 7 should add dedicated tests for:

- config/runtime schema and adapter resolution
- prompt assembly and attempt/result models
- generation loop behavior under mock provider responses
- CLI summary/output contract for `mdisc llm-generate`
- benchmark comparison on thin offline fixtures

That is lower risk than trying to prove the entire phase only via broad
end-to-end suite expansion.

## Recommended Implementation Shape

### Runtime and config

Add an additive Phase 7 surface:

```text
materials-discovery/src/materials_discovery/llm/
  runtime.py
  prompting.py
  generate.py
```

And extend config/contracts in:

```text
materials-discovery/src/materials_discovery/common/schema.py
```

with:

- `BackendConfig.llm_adapter`
- `BackendConfig.llm_provider`
- `BackendConfig.llm_model`
- optional `BackendConfig.llm_api_base`
- a dedicated `LlmGenerateConfig` nested under `SystemConfig`
- `LlmGenerateSummary`

### Artifact layout

```text
materials-discovery/data/
  candidates/{slug}_llm_candidates.jsonl
  calibration/{slug}_llm_generation_metrics.json
  manifests/{slug}_llm_generate_manifest.json
  llm_runs/{run_id}/
    prompt.json
    attempts.jsonl
    compile_results.jsonl
    manifest.json
```

### Recommended plan split

The cleanest split is three plans:

1. **Runtime foundation**
   - additive config/schema
   - provider-neutral runtime contract
   - deterministic mock adapter
   - one hosted API adapter
   - focused runtime tests

2. **`llm-generate` implementation**
   - prompt assembly
   - bounded retry loop
   - parse/compile classification
   - candidate conversion helper
   - CLI command, calibration, manifest, and summary output

3. **Offline benchmark and proof path**
   - committed thin benchmark configs/fixtures
   - deterministic comparison harness for `Al-Cu-Fe` and `Sc-Zn`
   - docs/runbook updates
   - slower-lane tests for screen-level comparison

This keeps Phase 7 narrow enough to ship while still proving the path is useful.

## Main Risks

1. **Parse vs compile taxonomy stays too fuzzy**
   If Phase 7 never improves beyond the current “bridge failed” signal, the MVP
   metrics will be too noisy to trust.

2. **Hosted provider choice leaks into the core contract**
   The first real provider should not hardwire the entire runtime to one vendor
   SDK or response shape.

3. **Candidate conversion forks from the deterministic generator**
   A separate LLM-only candidate schema would make downstream comparisons much
   harder and undercut the goal of reusing the existing pipeline as judge.

4. **Benchmark scope expands to hi-fi too early**
   That would blur the boundary between Phase 7 and Phase 8 and make execution
   slower and harder to verify.

## Validation Architecture

Phase 7 should use the existing pytest + Typer testing stack under
`materials-discovery/`.

### Fast validation loop

Use focused Phase 7 tests after every task:

```bash
cd materials-discovery && uv run pytest \
  tests/test_llm_generate_schema.py \
  tests/test_llm_runtime.py \
  tests/test_llm_generate_core.py \
  tests/test_llm_generate_cli.py
```

### Benchmark validation loop

Use a slower dedicated benchmark lane after the benchmark plan:

```bash
cd materials-discovery && uv run pytest \
  tests/test_llm_generate_benchmarks.py \
  tests/test_cli.py
```

### Full validation loop

Before final phase sign-off:

```bash
cd materials-discovery && uv run pytest
```

### Minimum Wave 0 verification expectations

Phase 7 execution plans should require:

- schema tests for new config and summary models
- adapter-resolution tests for mock and hosted provider lanes
- monkeypatched runtime tests that prove retries and attempt logging
- CLI tests for JSON summary output and exit-code `2` failures
- offline benchmark tests that compare `llm-generate` against deterministic
  `generate` on `Al-Cu-Fe` and `Sc-Zn`

### Manual checks still worth keeping

- inspect a sample run directory under `data/llm_runs/` to confirm prompt and
  raw-attempt lineage is understandable
- inspect one generated candidate JSONL row to confirm provenance is additive
  and not bloated with raw transcripts
- run `mdisc llm-generate` manually on one mock config and one real-provider
  config to confirm operator ergonomics

## Planning Implications

The Phase 7 plan should not simply say “add llm-generate.” It needs to
explicitly:

- land config/runtime contracts before the CLI command
- preserve standard `CandidateRecord` output instead of inventing a parallel
  artifact type
- make raw-attempt auditability a first-class deliverable
- keep tests offline and deterministic even though a real hosted provider is in
  scope
- end at screen-level benchmarking, not hi-fi comparison

## Recommendation

Phase 7 is ready for planning now.

The highest-confidence planning path is:

1. `07-01` runtime contracts, provider seam, and config/schema foundation
2. `07-02` core `llm-generate` engine plus CLI and provenance/calibration output
3. `07-03` offline benchmark harness, docs, and regression proof

That decomposition matches the locked user decisions, the repo’s current code
seams, and the level of rigor needed to make the first inference path useful
without accidentally swallowing Phase 8.
