# Phase 1: Program Charter and Canonical Data Model - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Define the ingestion contract for the Material Design Data Ingestion project
before implementing multiple source adapters. This phase should lock the
canonical external-record model, provenance and licensing rules, source
prioritization logic, and the adapter taxonomy that later ingestion work will
follow.

This phase does not implement the full adapter set yet. It should end with a
clear schema, source registry strategy, and plan-ready technical boundaries for
Phase 2.

</domain>

<decisions>
## Implementation Decisions

### Source scope and priority
- **D-01:** Phase 1 must optimize for open-access or clearly accessible sources
  first. Do not make subscription-only or institution-locked datasets a v1
  dependency.
- **D-02:** Tier 1 sources are `HYPOD-X`, `COD`, `Materials Project`, `OQMD`,
  and `JARVIS`.
- **D-03:** `NOMAD`, `Alexandria`, `Open Materials Database`, `B-IncStrDB`,
  `AFLOW`, `Materials Cloud`, and `NIMS MDR` must be captured in the Phase 1
  source inventory and designed for in the contract, but can follow after the
  MVP adapter wave.
- **D-04:** `MPDS` and `ICSD` are explicitly non-blocking for v1 because of
  access/licensing friction.
- **D-15:** Phase 1 must include a broader source-and-tooling inventory before
  finalizing the source registry and Phase 2 adapter order.
- **D-16:** The source inventory should explicitly distinguish primary v1
  targets, secondary open watchlist sources, and restricted/licensed sources.

### Ingestion contract and provenance
- **D-05:** The ingestion system must define a canonical raw-source record model
  separate from the existing pipeline's processed reference-phase model.
- **D-06:** Every ingested record must carry source identifier, source URL or
  access path, source version/snapshot date, license metadata, ingestion
  timestamp, and a stable local record ID.
- **D-07:** Schema design must avoid overfitting to `HYPOD-X`; the model should
  support both QC-specific datasets and broader periodic/computed materials
  databases.
- **D-08:** The ingestion contract must explicitly distinguish raw-source
  fields, normalized common fields, and pipeline-derived fields.
- **D-17:** Canonical raw-source records should use a strict stable core for
  shared fields, with provider-specific content nested under
  `source_metadata`.

### Adapter architecture
- **D-09:** The source adapter taxonomy must support at least four classes:
  direct source adapters, `OPTIMADE`-backed adapters, `CIF`/structure-conversion
  adapters, and curated/manual import adapters.
- **D-10:** `OPTIMADE` should be treated as a first-class interoperability path
  where providers support it, but not assumed as the only protocol.
- **D-11:** The ingestion architecture should fit inside the current
  `materials-discovery` Python subsystem and preserve the current CLI/schema
  contracts where practical.
- **D-18:** The new multi-source ingestion layer should live in a sibling
  package such as `materials_discovery/data_sources/`, not inside the current
  `backends/` or `data/` package trees.
- **D-19:** Official client/tooling repos and documentation surfaces such as
  `mp-api`, `Emmet`, `JARVIS-Tools`, `optimade-python-tools`, `qmpy`,
  `mpds_client`, `httk`, `NOMAD` docs, and `AFLOW` API docs are required
  planning inputs, but they are not all mandatory runtime dependencies.

### Integration with existing pipeline
- **D-12:** Phase 1 should design for clean integration with `mdisc ingest`,
  existing manifests, and reference-phase downstream consumers.
- **D-13:** The no-DFT execution boundary must remain explicit in required
  execution paths.
- **D-14:** The canonical model must preserve enough chemistry/structure/context
  to support future proxy hull, XRD, ranking, and LLM corpus work.
- **D-20:** `mdisc ingest` should remain the stable operator-facing entrypoint;
  the new source-ingestion layer should integrate behind it.
- **D-21:** Phase 2 should use a mixed adapter strategy: snapshot/bulk where
  that matches the source, and direct API or `OPTIMADE` where the official
  access surface is mature.

### the agent's Discretion
- Whether the canonical record is implemented first as Pydantic models,
  dataclasses, or both
- Whether raw-source contracts should initially live in
  `data_sources/schema.py` before stabilizing into `common/schema.py`
- The exact split between manifest metadata and source registry metadata
- The exact split between adapter base classes, normalization profiles, and
  source registry entries

</decisions>

<specifics>
## Specific Ideas

- Use the current `materials-discovery` architecture as the host system rather
  than starting a parallel ingestion repo.
- Treat this phase as the contract-design phase for Project A, not as the
  “implement five connectors” phase.
- Treat the source landscape as broader than the original Tier 1 list: Phase 1
  should inventory both data providers and official tooling surfaces before
  Phase 2 starts.
- Keep the resulting model useful for later `record2zomic` / `cif2zomic` work
  from the LLM roadmap.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Program roadmap
- `.planning/PROJECT.md` — overall program framing and key constraints
- `.planning/REQUIREMENTS.md` — requirement IDs and v1 scope
- `.planning/ROADMAP.md` — Phase 1 scope, source prioritization, and project sequencing
- `.planning/phases/01-program-charter-and-canonical-data-model/01-RESEARCH.md` — expanded Phase 1 source and tooling inventory distilled from official docs

### Existing subsystem architecture
- `materials-discovery/README.md` — current implementation summary and operator entrypoint
- `materials-discovery/developers-docs/index.md` — subsystem status, scope, and external resource list
- `materials-discovery/developers-docs/architecture.md` — current package boundaries and data flow
- `materials-discovery/developers-docs/backend-system.md` — adapter design patterns already used in the codebase
- `materials-discovery/developers-docs/pipeline-stages.md` — current `mdisc ingest` behavior and artifact flow
- `materials-discovery/developers-docs/configuration-reference.md` — `SystemConfig` and `BackendConfig` constraints that new ingestion config must fit
- `materials-discovery/developers-docs/data-schema-reference.md` — current schema style, validation patterns, and candidate/provenance contracts
- `materials-discovery/developers-docs/contributing.md` — repo-local development and testing expectations for future ingestion work
- `materials-discovery/REAL_MODE_EXECUTION_PLAN.md` — execution hardening constraints and existing ingestion milestone history

### LLM and future data reuse
- `materials-discovery/developers-docs/llm-integration.md` — future LLM architecture and external dataset references
- `materials-discovery/developers-docs/zomic-llm-data-plan.md` — downstream corpus-building needs from external structure data

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/src/materials_discovery/cli.py`: existing stage orchestration and manifest emission patterns
- `materials-discovery/src/materials_discovery/common/schema.py`: shared typed contracts and validation style
- `materials-discovery/src/materials_discovery/common/io.py`: workspace-relative path helpers and JSON/JSONL utilities
- `materials-discovery/src/materials_discovery/common/manifest.py`: stage-manifest pattern worth reusing for source-ingestion provenance
- `materials-discovery/src/materials_discovery/backends/registry.py`: precedent for registry-driven adapter selection
- `materials-discovery/src/materials_discovery/backends/types.py`: precedent for protocol-based adapter interfaces

### Established Patterns
- File-backed state under `materials-discovery/data/` rather than a database
- Config-driven runtime behavior using Pydantic schemas
- Registry + protocol abstraction for backends
- JSONL for row-oriented artifacts and JSON for manifests/calibration
- Docs-first operator ergonomics via `developers-docs/` references that mirror the code contracts

### Integration Points
- Existing `mdisc ingest` command and `data/processed/*_reference_phases.jsonl`
- `data/registry/` and `data/manifests/` for future source metadata and snapshots
- New package area should live under `materials_discovery/data_sources/`

</code_context>

<deferred>
## Deferred Ideas

- Full implementation of all Tier 1 adapters — Phase 2
- Normalization into pipeline-ready reference phases — Phase 3
- Benchmarking richer reference data in end-to-end discovery runs — Phase 4
- LLM corpus extraction and structure conversion from ingested sources — Phase 6+

</deferred>

---

*Phase: 01-program-charter-and-canonical-data-model*
*Context gathered: 2026-04-02*
