# Phase 1 Research: Program Charter and Canonical Data Model

**Phase:** `01-program-charter-and-canonical-data-model`  
**Project:** Material Design Data Ingestion  
**Date:** 2026-04-02

## Research Scope

This research pass answers one question:

How should a multi-source materials-data ingestion layer fit inside the current
`materials-discovery/` subsystem without breaking the documented CLI, schema,
manifest, and file-backed execution model?

It uses the current repo docs as the primary design source and then checks the
proposed source set against current official access surfaces.

## Repo-Grounded Findings

### 1. The current ingest path is intentionally narrow

The implemented `mdisc ingest` flow is a single-source normalization path, not a
general ingestion platform yet.

- `cli.py` resolves an `IngestBackend`, calls `backend.load_rows(...)`, passes
  those rows into `ingest_rows(...)`, then writes a processed JSONL plus stage
  manifest.
- `backends/types.py` defines `IngestBackend` as a minimal protocol:
  `info()` plus `load_rows(config, fixture_path) -> list[dict[str, Any]]`.
- `backends/registry.py` only registers two ingest adapters today:
  `mock:hypodx_fixture` and `real:hypodx_pinned_v2026_03_09`.
- `data/normalize.py` converts raw rows into a very small `IngestRecord`
  contract shaped around the current HYPOD-X-like fixture.

Implication:

Phase 1 should not stretch `IngestRecord` into the new canonical external-data
contract. It is already functioning as a downstream processed reference-phase
artifact, not as a general source-staging model.

### 2. The subsystem already gives us the right architectural patterns

The `developers-docs` set is consistent about how new features should fit:

- `architecture.md`: file-backed state, one CLI orchestration layer, JSONL for
  row artifacts, JSON for manifests/calibration.
- `backend-system.md`: registry + protocol abstraction is the preferred adapter
  pattern.
- `configuration-reference.md`: config changes should land through Pydantic
  models and preserve the current `SystemConfig` / `BackendConfig` approach.
- `data-schema-reference.md`: shared contracts live in `common/schema.py` and
  use validation-heavy Pydantic models.
- `pipeline-stages.md`: `mdisc ingest` is part of the documented operator
  surface and should remain a stable entrypoint.

Implication:

The ingestion project should be added as a new package area plus new schema
models and registry contracts, not as a second orchestration stack or a
database-first redesign.

### 3. A raw-source model must be distinct from pipeline-ready reference phases

The current pipeline needs processed reference phases for proxy hull, ranking,
and report logic. External databases expose a broader and messier space:

- raw provider identifiers
- source-specific schema fields
- diverse structure encodings
- different licensing and access rules
- source-level snapshots and versioning

Implication:

Phase 1 should define at least three logical layers:

1. `Source registry metadata`
2. `Canonical raw-source records`
3. `Normalized reference-phase records` for the existing discovery pipeline

Keeping these separate avoids overfitting the platform to current HYPOD-X rows
and keeps future LLM corpus work possible.

### 4. The existing backend registry is a useful precedent, but probably not the final home

The current `backends/` package is focused on runtime execution modes for the
discovery pipeline: mock, pinned real, exec, and native validation providers.

Inference from the code and docs:

It is cleaner to introduce a dedicated package such as
`materials_discovery/data_sources/` for external dataset adapters instead of
continuing to overload `backends/`. The current `backend.ingest_adapter` field
can remain the Phase 3 integration hook into `mdisc ingest`, while the new
source-ingestion layer uses its own source registry and normalization pipeline.

### 5. Artifact layout should stay file-backed and snapshot-oriented

The architecture docs and current code strongly favor reproducible filesystem
artifacts over a service/database design.

Recommended direction:

- keep raw/source snapshots on disk
- write row-oriented records as JSONL
- write source/snapshot/manifests as JSON
- preserve stage manifests and hashes as the system-of-record for provenance

This fits the current operator model and makes it easier to version snapshots,
compare runs, and feed downstream phases.

## Current Contract Gaps

The current ingest contracts are not yet sufficient for a multi-source program.

### Missing source-governance fields

The current `IngestRecord` only carries:

- `system`
- `phase_name`
- `composition`
- `source`
- `metadata`

That is too small for the roadmap requirements. Missing fields include:

- stable local record ID
- source-native record ID
- source URL or retrieval path
- source snapshot/version date
- license metadata
- access level (`open`, `restricted`, `subscription`)
- structure payload type and encoding
- normalization status and issues

### Missing adapter taxonomy

The codebase currently has only a HYPOD-X-shaped backend path. The roadmap
requires explicit support for:

- direct source adapters
- OPTIMADE-backed adapters
- CIF / structure-conversion adapters
- curated/manual import adapters

### Missing raw-to-normalized split

The current flow jumps directly from provider rows to processed reference-phase
records. A multi-source system needs an intermediate canonical raw model to
preserve provenance and source-specific metadata before downstream filtering or
normalization.

## Expanded External Source and Repo Landscape

This phase is still contract-design, not adapter implementation, but the source
plan should be broad enough that the contract is not accidentally shaped around
only the first few obvious databases. This pass extends the earlier sweep into a
broader source-and-tooling inventory.

### Primary v1 ingestion targets

These remain the best first-wave targets because they balance openness,
scientific value, and operational feasibility.

| Source | Why it matters | Official access surface | Official client/tooling surface | Phase 1 implication |
|---|---|---|---|---|
| `HYPOD-X` | Closest match to the repo's QC/approximant mission | Official dataset/paper reference rather than a clearly documented public live API in this sweep | No official client surfaced in this pass | Treat as a direct snapshot/dataset adapter first |
| `COD` | Open crystal-structure source useful for approximants and CIF-driven normalization | Official site plus OPTIMADE provider listing | Generic CIF + OPTIMADE toolchains | Support direct metadata/CIF retrieval and optional OPTIMADE access |
| `Materials Project` | Mature ecosystem and strong computed-materials coverage | Official API-key-backed API and MP OPTIMADE presence | `mp-api` docs plus `Emmet` document model/docs | Plan a direct authenticated adapter first, while preserving an OPTIMADE path |
| `OQMD` | Open computed database with live API, OPTIMADE, and bulk dumps | Native REST API, OPTIMADE endpoint, full SQL dumps | `qmpy` API/docs referenced from OQMD docs | Support both live-query and bulk-snapshot ingestion modes |
| `JARVIS` | Strong materials-design fit with official OPTIMADE and tooling | Official portal and JARVIS-OPTIMADE endpoint | `JARVIS-Tools` official repo/docs | Support direct or OPTIMADE-backed ingestion; keep toolchain reuse in mind |

### Secondary open watchlist

These sources should influence the canonical record and source registry in Phase
1 even if they do not all become Phase 2 adapters.

| Source | Official access surface | Why it matters | Planning posture |
|---|---|---|---|
| `NOMAD` | Official API/docs, download/programmatic flows, GitHub-linked docs | Broad FAIR materials platform with rich metadata and extensibility | Contract must handle richer metadata and plugin-like ingestion |
| `Alexandria` | Official downloads in JSON/CIF plus OPTIMADE endpoints | Strong open downloadable datasets with CC-BY 4.0 licensing | Good candidate for bulk JSON + OPTIMADE hybrid support |
| `Open Materials Database` | Public searchable site and `httk`-backed programmatic path; OPTIMADE-listed provider | Relevant open ecosystem with its own toolkit and contributed datasets | Treat as database + toolkit pair, not just a bare endpoint |
| `AFLOW` | Official REST/AFLUX documentation and source tooling | Long-running high-throughput materials platform with API and prototype ecosystem | Good secondary computed-materials source and pattern reference |
| `Materials Cloud` | Curated datasets, archive, and OPTIMADE-linked archive tooling | Valuable archive/curation layer and derived datasets, not just one monolithic DB | Useful as archive-style ingestion and benchmark/corpus source |
| `NIMS MDR` | General materials repository with browseable datasets/collections | Good repository-style source for datasets and publication-linked materials data | Treat as repository/archive source, not as a uniform materials API |
| `B-IncStrDB` | Specialized Bilbao database for incommensurate and composite structures | Directly relevant to superspace/incommensurate structure knowledge | Specialized contract input and possible later adapter |

### Restricted or curated-but-frictionful sources

These should shape the registry and licensing model, but not block v1.

| Source | Official access surface | Constraint | Planning posture |
|---|---|---|---|
| `MPDS` | Official API docs and Python client guidance | API-key and commercial/licensing considerations | Capture as restricted/curated source with explicit gating |
| `ICSD` | High scientific value but licensed | Access and redistribution friction | Keep out of v1 dependency chain |

### Additional discovery horizon from the OPTIMADE network

The OPTIMADE providers dashboard surfaces a wider provider ecosystem than the
initial roadmap list alone. In addition to the sources above, it highlights
providers such as `MPOD`, `MPDD`, `ODBX`, `Materials Cloud`, `Matterverse`, and
other interoperable databases. Not all of these need to be Phase 2 targets, but
Phase 1 should record them in the source registry as watchlist entries so the
project does not forget the broader ecosystem.

### Official client and interoperability repos to track in planning

Phase 1 should track not only datasets and APIs, but also the official tooling
surfaces that strongly influence adapter implementation cost and data-model fit.

| Tool / repo surface | What it gives us | Planning role |
|---|---|---|
| `mp-api` docs (`https://materialsproject.github.io/api/index.html`) | Official Materials Project client implementation surface | Direct MP adapter planning input |
| `Emmet` docs (`https://materialsproject.github.io/emmet/`) | MP document model and pipeline internals, including OPTIMADE support | Useful for field mapping and provenance reasoning |
| `JARVIS-Tools` repo (`https://github.com/usnistgov/jarvis`) | Official open-access toolkit for JARVIS data-driven materials design | Direct JARVIS adapter/tooling input |
| `optimade-python-tools` (`https://github.com/Materials-Consortia/optimade-python-tools`) | Python models, adapters, validator, multi-provider client, CIF/ASE/pymatgen bridges | Critical interoperability layer for OPTIMADE-backed adapters |
| `qmpy` / OQMD API docs (`https://static.oqmd.org/static/docs/restful.html`) | Historic and current OQMD query model, local DB access context | Helps choose between REST, OPTIMADE, and bulk snapshot flows |
| `mpds_client` guidance (`https://developer.mpds.io/`) | Official MPDS Python client and API-key workflow | Important for restricted-source planning, even if not v1 |
| `httk` docs (`https://httk.openmaterialsdb.se/en/v1.1.11/`) | Official framework behind Open Materials Database | Planning input for OMDB adapter posture and local data handling |
| `NOMAD` docs/GitHub (`https://nomad-lab.eu/prod/v1/docs`) | Official API, data, plugin, and GitHub-linked development surface | Planning input for richer metadata and repository-style ingestion |
| `AFLOW` REST/AFLUX docs (`https://aflowlib.org/documentation/`) | Official API model for AFLOW data search and retrieval | Planning input for secondary API-backed adapters |

### Official-access checks used in this expanded pass

- HYPOD-X paper / dataset reference:
  `https://www.nature.com/articles/s41597-024-04043-z`
- Materials Project API docs:
  `https://docs.materialsproject.org/downloading-data/using-the-api/getting-started`
- Materials Project client docs:
  `https://materialsproject.github.io/api/index.html`
- Emmet docs:
  `https://materialsproject.github.io/emmet/`
- OQMD REST API:
  `https://oqmd.org/api`
- OQMD downloads and qmpy compatibility:
  `https://www.oqmd.org/download/`
- OQMD OPTIMADE:
  `https://oqmd.org/optimade/`
- JARVIS portal:
  `https://jarvis.nist.gov/`
- JARVIS OPTIMADE:
  `https://jarvis.nist.gov/optimade/jarvisdft`
- JARVIS-Tools repo:
  `https://github.com/usnistgov/jarvis`
- OPTIMADE providers dashboard:
  `https://www.optimade.org/providers-dashboard/`
- OPTIMADE Python tools:
  `https://github.com/Materials-Consortia/optimade-python-tools`
- NOMAD docs:
  `https://nomad-lab.eu/prod/v1/docs`
- Alexandria:
  `https://alexandria.icams.rub.de/`
- Open Materials Database:
  `https://openmaterialsdb.se/`
- `httk` docs:
  `https://httk.openmaterialsdb.se/en/v1.1.11/`
- COD / crystallography.net:
  `https://www.crystallography.net/`
- AFLOW docs:
  `https://aflowlib.org/documentation/`
- Materials Cloud Discover:
  `https://www.materialscloud.org/discover`
- Materials Cloud Archive:
  `https://archive.materialscloud.org/`
- MPDS API docs:
  `https://developer.mpds.io/`
- B-IncStrDB:
  `https://www.cryst.ehu.eus/bincstrdb/`
- NIMS MDR:
  `https://mdr.nims.go.jp/`

This is still a planning-oriented landscape sweep, not a claim that every
provider has been exhaustively audited endpoint by endpoint. The goal is to make
Phase 1 broad enough that Phase 2 priorities and the canonical source contract
are based on the real ecosystem rather than on a too-small initial list.

### Synthesis for Phase 1

This broader sweep strengthens four planning conclusions:

1. The source registry must distinguish at least four source types:
   structured API databases, OPTIMADE providers, bulk archive/repository
   sources, and toolkit-coupled ecosystems.
2. The project should inventory both data providers and official client/tooling
   repos before finalizing Phase 2 priority order.
3. The mixed Phase 2 adapter posture is validated by the current ecosystem:
   some sources are best as live APIs, some as OPTIMADE, and some as downloads
   or archives.
4. The source registry should include a watchlist tier for broader ecosystem
   coverage, even when implementation is deferred.

## Recommended Phase 1 Outputs

Phase 1 should end with explicit contracts and decision records, not with a
half-built connector set.

### 1. Canonical source registry contract

Define a registry model for one source/provider entry with fields such as:

- `source_key`
- `display_name`
- `category` (`qc_specific`, `periodic_crystal`, `computed_materials`, `specialized`)
- `access_level`
- `license`
- `access_surface` (`api`, `optimade`, `bulk_download`, `cif_lookup`, `manual`)
- `snapshot_strategy`
- `expected_record_kinds`
- `implementation_priority`
- `official_tooling_surface`
- `watchlist_tier`

### 2. Canonical raw-source record contract

Define a source-staging model with separate blocks for:

- identity and source provenance
- chemistry and composition
- structure payload and encoding
- source-native metadata
- normalized common fields
- validation / QA flags

Recommended top-level shape:

- `record_id`
- `source`
- `source_record_id`
- `snapshot_id`
- `retrieved_at`
- `license`
- `access_level`
- `material_classification`
- `composition`
- `structure_payload`
- `common_fields`
- `source_metadata`
- `qa`

### 3. Artifact layout and manifest policy

Define a filesystem layout that mirrors current subsystem behavior:

- `data/external/raw/{source}/{snapshot}.jsonl`
- `data/external/normalized/{source}/{snapshot}.jsonl`
- `data/registry/sources/{source}.json`
- `data/manifests/{source}_{snapshot}_manifest.json`
- `data/qa/{source}_{snapshot}_qa.json`

This is an inference from the current file-backed architecture and manifest
pattern in `common/manifest.py`.

### 4. Integration boundary with the current CLI

Phase 1 should lock the rule that:

- external-source ingestion is its own adapter + staging subsystem
- `mdisc ingest` remains the documented entrypoint that downstream operators use
- later phases decide whether `mdisc ingest` calls the new source layer
  directly, or consumes prepared normalized snapshots through the existing
  backend registry

### 5. QA and acceptance policy

Define source-ingestion QA metrics before implementation:

- duplicate rate
- invalid-composition rate
- malformed-structure rate
- missing-required-field rate
- schema-drift rate
- records-normalized rate
- records-rejected rate

These map directly to `DATA-04` and fit the existing summary/manifest style.

## Recommended Package Direction

The least disruptive direction is:

- keep `materials_discovery/backends/` focused on execution-mode adapters for
  the existing discovery pipeline
- add `materials_discovery/data_sources/` for source registry, raw-source
  schemas, adapters, and normalization profiles
- add any new shared ingestion contracts to `common/schema.py` only when they
  are truly cross-package and stable

This keeps the current backend story understandable and avoids mixing external
dataset federation with runtime validation providers.

## Phase 1 Risks and Open Decisions

### Risks

- Overfitting the canonical raw model to HYPOD-X and making COD/CIF or
  OPTIMADE sources awkward later
- Trying to normalize too aggressively during initial ingestion and losing
  source-native metadata needed for auditing or LLM corpus work
- Hiding licensing/access constraints inside free-form metadata instead of
  making them first-class fields
- Overloading `BackendConfig` too early and making the CLI harder to reason
  about

### Open decisions to resolve in planning

- Should the new canonical raw-source models live in `common/schema.py` or in a
  dedicated `data_sources/schema.py` until they stabilize?
- Should source-specific metadata be a required nested `source_metadata` block
  or a looser provider-extension mechanism?
- Should Phase 2 start with snapshot-driven adapters for every Tier 1 source,
  or mix snapshot and live API adapters immediately?
- Should OPTIMADE be expressed as a concrete adapter base class, a protocol, or
  just one adapter family inside the source registry?

## Top 5 Planning Takeaways

1. The current ingest code is already useful, but it is a processed-reference
   adapter, not a general external-data ingestion platform.
2. The `developers-docs` set strongly favors a file-backed, schema-first,
   registry-driven implementation, so the new work should look like the current
   subsystem rather than a separate service.
3. Phase 1 should define a distinct canonical raw-source model plus a source
   registry before implementing multiple adapters.
4. A dedicated `data_sources/` package is the cleanest fit; it avoids
   overloading the existing `backends/` runtime adapter system.
5. Tier 1 sources still make sense, but the contract must be flexible enough
   for API, OPTIMADE, CIF, and snapshot/manual access patterns from day one.
