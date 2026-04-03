# Phase 2 Research: Ingestion Platform MVP

**Phase:** 02  
**Date:** 2026-04-03  
**Goal:** Plan the first executable multi-source ingestion framework for
`materials-discovery/` without breaking the current CLI or processed ingest
contract.

## Research Question

What do we need to know to plan Phase 2 well so that the team can implement:

- a reusable `data_sources/` runtime package
- one shared adapter model for direct, CIF-conversion, and OPTIMADE flows
- first-wave adapters for `HYPOD-X`, `COD`, `Materials Project`, `OQMD`, and
  `JARVIS`
- QA artifacts and tests that prove the framework is truly multi-source
- additive compatibility with the current `mdisc ingest` flow

## Key Findings

### 1. The current ingest seam is intentionally too small for the new goal

The existing runtime is still built around:

- `backends.types.IngestBackend.load_rows(...) -> list[dict[str, Any]]`
- `data.normalize.normalize_raw_record(...) -> IngestRecord`
- `data.ingest_hypodx.ingest_rows(...)` for filtering, dedupe, QA, and writeout

This is good for fixture and pinned HYPOD-X snapshots, but it is too narrow for
canonical raw-source staging because it jumps almost directly into the current
processed `IngestRecord` shape. The current `IngestRecord` only carries:

- `system`
- `phase_name`
- `composition`
- `source`
- `metadata`

That is not enough to satisfy the Phase 1 raw-source contract or to support
source-specific lineage, snapshot metadata, structure payload variants, or
schema-drift checks.

### 2. The repo already has the right implementation patterns; they just live one layer downstream

The current codebase already provides reusable patterns Phase 2 can borrow:

- `common/schema.py` establishes the Pydantic style and additive config pattern
- `common/io.py` provides the file-backed JSON/JSONL helpers
- `common/manifest.py` establishes manifest hashing and run metadata
- `backends/registry.py` and `backends/types.py` show the registry + protocol
  style already used for runtime dispatch
- `cli.py` shows the JSON-summary-on-success contract and stable stage-manifest
  emission pattern
- `tests/test_ingest.py`, `tests/test_ingest_real_backend.py`, and
  `tests/test_cli.py` show the testing style the new ingestion layer should fit

Phase 2 does not need to invent a new platform style. It needs to apply the
existing style one layer earlier, at source staging time.

### 3. Phase 2 should build a framework-first runtime, then prove it with concrete adapters

The present code and tests strongly suggest that a one-shot “add five providers”
plan would be brittle. The safer path is:

1. land the `data_sources/` package, canonical models, registry, manifests, and
   QA framework
2. land one direct snapshot-backed adapter and one CIF-conversion or OPTIMADE
   proof path
3. extend to the remaining priority providers using the shared framework

That decomposition minimizes the risk of ending Phase 2 with five ad hoc source
modules and no durable architecture.

### 4. Configuration should extend `SystemConfig` additively, not overload `BackendConfig`

Phase 1’s integration design already points to the right move:

- keep `BackendConfig` focused on execution mode selection
- add an optional `ingestion` block for source/staging choices

That is a better fit than packing provider-specific keys into `backend`,
because:

- it preserves current config semantics
- it keeps default existing YAMLs valid
- it draws a clean line between execution adapters and external source staging

### 5. QA needs to grow from threshold checks into artifact-producing source validation

The current `data/qa.py` only checks:

- invalid rate
- duplicate rate
- minimum deduped rows

Phase 2 must expand QA into something source-aware and artifact-backed:

- missing mandatory core fields
- invalid composition parsing
- malformed structure payloads
- duplicate collision counts by canonical fingerprint
- schema drift counts against the raw-source contract
- counts by record kind and source key

Those results should be written as JSON artifacts, not just returned in-memory.

### 6. `HYPOD-X` should remain the regression anchor, but not the architectural template

`HYPOD-X` is the easiest scientific continuity source because:

- it already exists in the codebase
- it already has fixture and pinned workflows
- it is closest to the QC/approximant mission

But the current HYPOD-X path should be treated as the regression anchor, not the
schema model for other providers. The framework should generalize beyond it.

## Recommended Runtime Shape

### Package layout

Phase 2 should start from the Phase 1 package layout and implement the minimum
runtime subset:

```text
materials_discovery/
  data_sources/
    __init__.py
    schema.py
    types.py
    registry.py
    storage.py
    manifests.py
    qa.py
    projection.py              # can start as a stub or bridge seam for Phase 3
    adapters/
      __init__.py
      hypodx.py
      cod.py
      optimade.py
      materials_project.py
      oqmd.py
      jarvis.py
      cif_conversion.py
```

### Recommended responsibilities

| Module | Responsibility |
|---|---|
| `schema.py` | canonical raw-source models, manifest-side record counts, QA summary types |
| `types.py` | `SourceAdapter`, `SourceAdapterInfo`, fetch/list/normalize protocol shapes |
| `registry.py` | provider registry keyed by source key and adapter key |
| `storage.py` | snapshot directory layout, attachment paths, stable record path helpers |
| `manifests.py` | source snapshot manifest builders and writers |
| `qa.py` | raw-source QA metrics and drift checks |
| `projection.py` | Phase 3 bridge seam from raw-source staging to processed reference phases |
| `adapters/*.py` | provider-specific source logic |

### Relationship to existing packages

- `backends/` should keep runtime-mode selection and, at most, expose a thin
  bridge adapter that invokes the new source registry.
- `data/` should keep the existing HYPOD-X-style processed ingest helpers until
  Phase 3 replaces or wraps them.
- `common/` should remain the home for shared primitives, but the raw-source
  contract should stay in `data_sources/schema.py` during this phase.

## Recommended Config Direction

The cleanest additive configuration move is:

```yaml
backend:
  mode: real
  ingest_adapter: source_registry_v1

ingestion:
  source_key: materials_project
  adapter_key: materials_project_api_v1
  snapshot_id: materials_project_default
  use_cached_snapshot: true
  query:
    elements: [Al, Cu, Fe]
    limit: 500
```

Why this direction is strongest:

- current configs remain valid when `ingestion` is absent
- existing `backend.ingest_adapter` still controls which ingest path is active
- provider-specific runtime knobs move into an additive block that can evolve
  without distorting execution-mode settings

## Adapter Strategy Research

### `HYPOD-X`

Best first implementation posture:

- direct snapshot-backed adapter
- preserve current fixture and pinned workflows
- emit canonical raw-source records plus raw/provider snapshot artifacts

Why:

- lowest migration risk
- fastest way to prove the framework without introducing auth or live API noise

### `COD`

Best first implementation posture:

- CIF-conversion adapter
- optionally layered later with OPTIMADE or alternative discovery/query paths

Why:

- the main complexity is parsing and canonicalizing structure payloads, not auth
- it proves the framework can handle structure-heavy periodic sources rather
  than only HYPOD-X-style phase rows

### `Materials Project`

Best first implementation posture:

- direct API adapter first
- keep OPTIMADE compatibility as future leverage, not the primary MVP path

Why:

- official client/tooling maturity is strong
- authenticated direct access will likely be less ambiguous than constraining
  the first implementation through a generic interoperability layer

### `OQMD`

Best first implementation posture:

- direct adapter plus shared OPTIMADE groundwork

Why:

- OQMD is an excellent place to prove that the framework can support both a
  native provider shape and an OPTIMADE-compatible path
- it is the best candidate for keeping direct-vs-OPTIMADE optionality visible
  during implementation

### `JARVIS`

Best first implementation posture:

- use the shared OPTIMADE path if endpoint completeness is good enough at
  implementation time
- otherwise fall back to a direct adapter

Why:

- the program already decided JARVIS can legitimately use either path
- this makes JARVIS the best final proof that the framework is not ideologically
  tied to a single access pattern

## Existing Test Surface

Current tests already give us three useful anchors:

- `tests/test_ingest.py` verifies dedupe, deterministic output, and ordering
- `tests/test_ingest_real_backend.py` verifies pinned-snapshot ingest,
  manifest creation, and summary structure
- `tests/test_cli.py` verifies CLI success and error code behavior

What is missing for Phase 2:

- unit tests for canonical raw-source schemas
- registry resolution tests for source adapters
- QA drift/malformed-structure tests
- adapter contract tests for direct, CIF-conversion, and OPTIMADE flows
- CLI tests for additive `ingestion` config while preserving old configs
- integration tests that prove at least one source uses the OPTIMADE path

## Main Risks

### Risk 1: Overloading the old ingest backend interface

If Phase 2 tries to force multi-source staging through
`IngestBackend.load_rows(...) -> list[dict]`, the framework will inherit the old
shape’s limitations and lose the provenance guarantees Phase 1 locked in.

**Recommendation:** add a dedicated `SourceAdapter` protocol under
`data_sources/types.py`.

### Risk 2: Prematurely merging raw-source and processed-reference contracts

If canonical raw-source records are collapsed directly into `IngestRecord`,
Phase 2 will appear simpler but Phase 3 will lose the source richness it needs.

**Recommendation:** keep canonical raw-source JSONL and processed reference-phase
JSONL as separate artifact classes.

### Risk 3: Treating all providers as equal from day one

The priority sources do not share the same access shape. A single forced
abstraction would likely be either too weak or too magical.

**Recommendation:** use a small, shared adapter surface with multiple adapter
families rather than one giant universal adapter.

### Risk 4: QA that only fails closed in memory

The current QA helper is cheap and useful, but Phase 2 needs diagnostics the
team can inspect after a run.

**Recommendation:** emit QA reports as JSON artifacts next to canonical staged
records and source manifests.

### Risk 5: Breaking CLI/config compatibility during the package move

If `mdisc ingest` or `SystemConfig` changes in a non-additive way, Phase 2 will
violate `OPS-04`.

**Recommendation:** treat existing configs and CLI tests as mandatory regression
gates in every plan.

## Recommended Plan Decomposition

The phase is best planned as **three plans**, with either:

- two waves if the adapter plans have fully disjoint write scopes, or
- three waves if shared registry/runtime files remain owned by both adapter tracks

Given the current repo seams, the safer execution choice is three waves because
the direct/CIF path and the API/OPTIMADE path both legitimately touch
`data_sources/registry.py` and `data_sources/runtime.py`.

### Wave 1: Framework foundation

**Plan 02-01**

Build the additive runtime skeleton:

- `data_sources/` package skeleton
- canonical raw-source models
- source adapter protocol and registry
- storage/manifests/QA infrastructure
- additive config extension and CLI bridge seam
- foundational tests

This plan should be the dependency anchor for everything else.

### Wave 2 and Wave 3: Concrete adapters and proof paths

**Plan 02-02**

Implement the direct/snapshot and CIF-conversion side:

- `HYPOD-X` adapter migrated onto the new runtime
- `COD` adapter or CIF-conversion path
- canonical snapshot artifacts and QA report emission
- integration tests for staged output and manifest lineage

**Plan 02-03**

Implement the API/OPTIMADE side:

- shared OPTIMADE adapter foundation
- `Materials Project` direct adapter
- `OQMD` direct adapter plus OPTIMADE proof path
- `JARVIS` adapter using OPTIMADE or direct, whichever fits the concrete runtime
- tests that prove the framework supports both source-specific and OPTIMADE-based paths

This split keeps the concrete write scopes clearer than one giant plan and
gives Phase 2 a clean wave boundary. If the execute phase keeps shared registry
ownership in both adapter plans, run the API/OPTIMADE plan after the
direct/CIF plan instead of in parallel.

## Validation Architecture

Phase 2 should use the existing pytest-based validation stack.

### Fast validation loop

Use focused ingest/data-source tests after every task:

```bash
cd materials-discovery && uv run pytest tests/test_ingest.py tests/test_ingest_real_backend.py tests/test_cli.py
```

### Full validation loop

Use the repo’s full Python suite after each plan wave:

```bash
cd materials-discovery && uv run pytest
```

### Minimum Wave 0 verification expectations

Phase 2 execution plans should require:

- schema tests for canonical raw-source records
- registry tests for adapter resolution
- QA tests for missing fields, duplicate collapse, malformed structures, and drift
- CLI compatibility tests for old configs and additive new configs
- at least one integration test for staged raw-source artifacts and manifests

### Manual checks still worth keeping

- inspect a staged source snapshot directory on disk
- inspect the emitted QA report JSON for meaningful counters
- confirm existing configs without an `ingestion` block still run

## Planning Implications

The Phase 2 plan should not merely say “add adapters.” It needs to explicitly:

- land the package and schema foundation first
- preserve the current CLI and config contracts
- treat tests and QA artifacts as core deliverables, not cleanup
- prove both direct and OPTIMADE-capable ingestion paths in the same phase
- leave the raw-source to processed-reference projection as a deliberate Phase 3 seam

## Recommendation

Phase 2 is ready for planning now. The research is strong enough to proceed
without another discuss-phase round because the locked decisions already exist
in the Phase 1 artifacts and the repo’s current code seams are clear.

The highest-confidence planning path is:

1. `02-01` framework and compatibility foundation
2. `02-02` direct snapshot + CIF conversion adapters
3. `02-03` API + OPTIMADE adapters and end-to-end QA proof

That decomposition gives the execute phase a realistic chance of shipping an MVP
that is reusable rather than provider-by-provider custom glue.
