# Phase 35: External Target Registration and Reproducible Execution - Research

**Researched:** 2026-04-07
**Domain:** Immutable external benchmark-target registration, smoke checks, and reproducibility lineage
**Confidence:** MEDIUM-HIGH

## User Constraints

Phase 35 has an explicit context file: `35-CONTEXT.md`.

Honor the locked decisions from that context and the milestone research:

- keep the phase benchmark-first, CLI-first, operator-governed, and file-backed
- support only a curated handful of already-downloaded external targets
- do not turn this phase into a generic model marketplace, downloader, or
  long-lived serving platform
- keep internal controls on the shipped checkpoint machinery instead of mixing
  them into the new external-target contract
- any change under `materials-discovery/` must update
  `materials-discovery/Progress.md`

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| OPS-17 | Operator can register each curated downloaded external materials LLM as an immutable benchmark target with pinned revision or snapshot identity, compatible translation families, runtime settings, smoke checks, and reproducibility-grade environment lineage before benchmark execution. | Mirror the checkpoint-registration pattern with a dedicated external-target artifact family, immutable fingerprinting, typed smoke and environment artifacts, and a narrow benchmark-only runtime seam. |

</phase_requirements>

## Summary

The strongest repo precedent is the existing checkpoint-registration workflow in
`materials_discovery.llm.checkpoints`. It already solves the key control
problem: turn one operator-authored YAML spec into an immutable, file-backed
registration artifact; reject ID reuse when the fingerprint changes; and keep
later workflow stages consuming stable facts instead of ad hoc shell history.
Phase 35 should reuse that shape closely, but without checkpoint lifecycle
promotion or retirement.

The new external-target artifact family should live under
`data/llm_external_models/{model_id}/`. The minimal credible family is:

- `registration.json` — immutable normalized target facts and fingerprint
- `environment.json` — reproducibility-grade environment capture for the last
  successful smoke or explicit inspection run
- `smoke_check.json` — latest typed readiness result with status, latency,
  detail, and pointers back to the resolved target and captured environment

That keeps immutable identity distinct from observed readiness while still
giving Phase 36 a stable surface to consume.

The registration schema should capture benchmark-relevant identity explicitly:

- `model_id`
- `model_family`
- `supported_systems` or `system_scope`
- `supported_target_families`
- `runner_key`
- `provider`
- `model`
- `model_revision`
- `tokenizer_revision`
- `local_snapshot_path`
- `snapshot_manifest_path` or equivalent repo-relative lineage path when present
- `dtype`
- `quantization`
- `prompt_contract_id`
- `response_parser_key`
- `notes`
- `fingerprint`

The fingerprint should be based on normalized immutable facts only, not on
mutable smoke status or timestamps. That mirrors `register_llm_checkpoint(...)`
and preserves honest ID stability.

For the runtime seam, Phase 35 should stay narrower than Phase 36. The goal is
not full comparative execution yet. The safest MVP is a benchmark-only external
runtime helper that resolves a registered target, captures environment facts,
and performs a smoke check with one explicit runner contract. The repo research
leans toward local snapshot-backed runners, not a generic serving platform.
Given the current codebase and dependencies, the most practical design is:

- `transformers_causal_lm` — default local snapshot runner shape
- `peft_causal_lm` — optional adapter-backed variant when the selected target
  needs PEFT-style composition

Implementation detail: keep heavy imports optional and local to the runtime
functions. `materials-discovery/pyproject.toml` does not currently include
`transformers`, `huggingface_hub`, `safetensors`, `accelerate`, or `peft`, so
Phase 35 should either add a dedicated optional dependency group or keep the
runtime functions import-isolated so schema, storage, and CLI tests do not
require those packages.

Smoke checks should follow the same pattern as
`materials_discovery.llm.serving_benchmark.run_serving_smoke_check(...)`:
typed result, explicit pass or fail status, captured detail text, and no silent
fallback. The difference is that external targets are resolved from
`registration.json`, not from `SystemConfig` model lanes. If a target cannot
reconstruct its snapshot lineage or environment facts, smoke should fail closed.

For committed examples, the repo should not ship real third-party weights.
Instead, use repo-backed fixture snapshots or small fake manifests that model
the real contract shape honestly. This is the same principle used elsewhere in
the repo: tests exercise artifact contracts and CLI behavior without requiring
production-only assets. The example surface should still look like a real local
snapshot registration workflow, not a toy contract that Phase 36 would have to
replace.

**Primary recommendation:** implement a checkpoint-style external-target
registration contract under `data/llm_external_models/`, add typed environment
and smoke artifacts as first-class files, isolate heavy runtime imports, and
split planning into three slices: contract or storage foundation, registration
plus reproducibility core, then CLI/examples/docs.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pydantic` | repo standard | Typed registration, smoke, and environment contracts | Already the repo's contract backbone for checkpoints, benchmarks, and manifests. |
| `typer` | repo standard | CLI registration, inspect, and smoke commands | Matches every current operator-facing workflow. |
| `pytest` | repo standard | Focused contract/core/CLI regression coverage | Existing testing backbone with stable patterns under `materials-discovery/tests/`. |

### Supporting Runtime Libraries

| Library | Recommended Use | Why |
|---------|------------------|-----|
| `transformers` | Optional local snapshot loading for the default external runner | Most realistic benchmark-first runtime for downloaded HF-native checkpoints. |
| `torch` | Optional inference backend and device visibility capture | Required for real local model execution and environment reporting. |
| `huggingface_hub` | Optional snapshot metadata normalization when available | Useful for revision-aware local snapshot lineage without building a downloader. |
| `safetensors` | Optional weight-file inventory and hashing | Helps fingerprint real snapshot contents honestly. |
| `accelerate` | Optional device-map or offload metadata | Useful when the operator's smoke path needs reproducibility about placement. |
| `peft` | Optional adapter-backed target support only | Needed only when the curated shortlist includes adapter-style materials models. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Checkpoint-style immutable registration | Generic provider registry in `SystemConfig` | Wrong boundary. It would blur the benchmark-only surface into the main generation path. |
| Local snapshot-backed runtime seam | Long-lived OpenAI-compatible servers or benchmark daemons | Too much platform gravity for this milestone and weaker reproducibility for downloaded-model evaluation. |
| Typed file-backed environment artifacts | CLI-only text output | Harder for Phase 36 to consume and much weaker for auditability. |
| Repo-backed fixture snapshots for examples | Shipping real external model weights | Unrealistic for the repo and unnecessary to prove the contract. |

## Architecture Patterns

### Pattern 1: Immutable Registration Mirroring Checkpoint Registration

**What:** Load one typed YAML spec, normalize relative paths, validate required
lineage inputs, compute a fingerprint from immutable target facts, and write
`registration.json` under `data/llm_external_models/{model_id}/`.

**When to use:** Always for new external benchmark targets.

**Why:** The repo already trusts this pattern for adapted checkpoints. It is the
best-fit way to keep benchmark-target identity auditable and replayable.

### Pattern 2: Separate Registration Facts From Observed Runtime Artifacts

**What:** Keep `registration.json` immutable, then persist `environment.json`
and `smoke_check.json` as separate artifacts keyed to the resolved registration.

**When to use:** Always. Do not rewrite the registration artifact with mutable
smoke status or environment timestamps.

**Why:** This preserves a clean contract between "what target was registered"
and "what environment or readiness state was observed later."

### Pattern 3: Fingerprint the Snapshot Contract, Not Just the Label

**What:** Include normalized immutable runtime facts in the fingerprint payload:
runner key, provider, model label, revision values, local snapshot path,
supported target families, prompt or parser contract hooks, and any declared
snapshot manifest or weight inventory fields.

**When to use:** Always when writing or reloading a registration.

**Why:** Phase 35's core risk is silent drift. The target ID must not stay the
same while the model bits or runtime expectations change underneath it.

### Pattern 4: Optional Heavy Imports Behind a Benchmark-Only Runtime Seam

**What:** Keep runtime helpers in a separate external-target module and import
heavy libraries inside the functions that need them.

**When to use:** For smoke and later execution helpers.

**Why:** The repo currently does not require the Hugging Face runtime stack for
ordinary tests. Phase 35 should not make schema or CLI coverage depend on those
packages being globally installed.

### Pattern 5: Typed Smoke Checks With No Silent Fallback

**What:** Reuse the repo's typed smoke-check posture: explicit pass or fail
status, captured detail text, latency, and resolved target identity.

**When to use:** Every time the operator validates an external target before
benchmark use.

**Why:** A target that cannot resolve its own snapshot or environment lineage is
not benchmark-ready. Fallback behavior would invalidate the milestone question.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| External benchmark identity | Ad hoc YAML plus shell history | Typed registration + fingerprinted artifact | Keeps Phase 36 consumption stable and auditable. |
| Generic runtime platform | Downloaders, daemons, schedulers, and broad provider abstractions | Narrow benchmark-only external runtime seam | Preserves benchmark-first scope. |
| Mutable registrations | Rewriting registration facts with latest smoke status | Separate immutable registration and mutable environment or smoke artifacts | Prevents target drift from being hidden. |
| Example assets | Fake contract fields disconnected from real local-snapshot semantics | Lightweight fixture snapshots or manifests that model the real contract shape | Lets docs and tests stay honest without shipping real weights. |

## Common Pitfalls

### Pitfall 1: Treating runtime status as registration identity

**What goes wrong:** The same `model_id` gets reused while smoke status,
environment facts, or local snapshot details drift silently.

**How to avoid:** Keep fingerprinted immutable registration facts separate from
observed environment and smoke artifacts.

### Pitfall 2: Letting benchmark-only targets leak into `SystemConfig`

**What goes wrong:** The repo grows a parallel global serving abstraction for
an MVP that only needs a few benchmark targets.

**How to avoid:** Keep external targets on their own artifact family and consume
them from benchmark-specific commands only.

### Pitfall 3: Requiring heavy runtime packages for schema-only tests

**What goes wrong:** Unit tests become fragile because importing the external
runtime path pulls in `transformers` or `torch` even when contract tests do not
need them.

**How to avoid:** Isolate imports and keep runtime helpers out of import paths
used by schema and CLI validation tests unless the command explicitly needs
them.

### Pitfall 4: Example specs that cannot model real operator usage

**What goes wrong:** The repo ships demo configs that pass tests but are too
fake for operators to adapt to real local snapshots later.

**How to avoid:** Use real contract fields and repo-backed fixture manifests or
small snapshot directories so the example flow still resembles real usage.

## Validation Architecture

Phase 35 can stay fully automated if it follows the checkpoint and serving
benchmark testing split:

1. Schema and storage tests for the new contract and artifact root
2. Registry core tests for normalization, fingerprinting, reload, and conflict
   rejection
3. CLI tests for `register`, `inspect`, and `smoke` command behavior
4. Optional runtime tests that use monkeypatching or fixture runners instead of
   real third-party weights

Recommended focused commands:

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_schema.py -x -v`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_registry.py -x -v`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_cli.py -x -v`

The likely Wave 0 requirement is only the new focused test files; the repo
already has `pytest`, `typer`, and the usual contract helpers. If the runtime
code needs optional packages, keep those tests monkeypatched so the main Phase
35 verification slice remains fast and deterministic.

## Recommended Plan Split

### Plan 01: Contract and storage foundation

Deliver:

- typed schema models for external target specs, registrations, environment
  manifests, smoke results, and summaries
- deterministic storage helpers under `data/llm_external_models/`
- focused schema and storage tests

Why first:

- Phase 35 needs a stable file-backed contract before CLI or runtime logic can
  be trustworthy

### Plan 02: Registration, environment capture, and smoke core

Deliver:

- registration loader and fingerprinting core
- immutable registration writing and reload helpers
- environment capture helpers
- typed smoke-check execution and artifact persistence
- focused registry and smoke tests

Why second:

- this is the actual `OPS-17` core and builds directly on the contract from
  Plan 01

### Plan 03: CLI, example specs, and operator docs

Deliver:

- `mdisc llm-register-external-target` command
- `mdisc llm-inspect-external-target` and/or `mdisc llm-smoke-external-target`
  operator surfaces
- committed example specs and runbook or pipeline docs
- CLI coverage and Progress.md updates

Why last:

- once the contract and runtime core are stable, the operator-facing surface can
  ship without churn

## Output Recommendations for Planner

- Keep the phase to 3 execute plans, one per split above
- Include `materials-discovery/Progress.md` in every plan that edits code or docs
- Treat heavy runtime dependencies as optional or locally imported unless a task
  explicitly adds them to `pyproject.toml`
- Make the must-haves traceable to `OPS-17`: immutable registration identity,
  stable re-resolution to the same local snapshot, and inspectable
  reproducibility lineage before benchmark execution
