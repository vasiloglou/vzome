# Canonical Raw-Source Data Contract

## Purpose

Phase 1 needs a source-staging contract that is broader than the current
`materials_discovery.common.schema.IngestRecord` and still disciplined enough to
drive Phase 2 adapter work without reopening basic modeling questions.

This document defines that contract.

## Locked Design Constraints

- The current `mdisc ingest` path remains a processed reference-phase path, not
  the canonical raw-source model.
- The new ingestion layer stays file-backed, schema-driven, and compatible with
  the documented `materials-discovery` operator model.
- Phase 1 defines the contract and boundaries only. It does not implement all
  adapters or replace the current pipeline.
- Shared cross-source fields must live in a strict stable core.
- Provider-specific details must live under `source_metadata`.
- The model must capture provenance, licensing, access posture, QA status, and
  structure payload references for both open and restricted sources.

## Three Logical Layers

The program should treat provider data as three separate layers.

| Layer | Purpose | Owner in Phase 1 | Notes |
|---|---|---|---|
| `SourceRegistryEntry` | Provider-level metadata and prioritization | `01-SOURCE-REGISTRY.md` | One entry per provider/access surface |
| `CanonicalRawSourceRecord` | One immutable staged record from an external provider | This document | Stable source-facing core plus nested provider metadata |
| `ReferencePhaseProjection` | Pipeline-ready derived record for `mdisc ingest` | Phase 3 design/implementation | Produces the current processed `IngestRecord` shape or its deliberate successor |

This separation is required by `DATA-01`, `DATA-02`, `OPS-01`, and `OPS-02`.

## Contract Overview

### Record Identity

Each staged record represents exactly one provider-native entry from one
retrieval snapshot.

- A provider-native entry may be a structure row, phase entry, computed
  material, curated dataset member, or repository dataset object.
- The same source-native record may appear in multiple snapshots.
- The same physical material may appear in multiple providers. Cross-source
  deduplication is a QA concern, not an identifier rewrite.

### Required top-level shape

```text
CanonicalRawSourceRecord
  schema_version
  local_record_id
  record_kind
  source
  access
  license
  snapshot
  raw_payload
  common
  qa
  lineage
  source_metadata
```

### Stable identity rule

`local_record_id` must be immutable for a given `(source_key, snapshot_id,
source_record_id)` tuple.

Recommended derivation:

```text
src_{source_key}_{sha256(source_key + "|" + snapshot_id + "|" + source_record_id)[:16]}
```

This keeps IDs deterministic, filesystem-safe, and independent of provider path
length or URL changes outside the snapshot identity.

## CanonicalRawSourceRecord

### Core fields

| Field | Required | Type | Meaning |
|---|---|---|---|
| `schema_version` | Yes | `str` | Contract version such as `raw-source-record/v1` |
| `local_record_id` | Yes | `str` | Immutable local ID derived from source identity |
| `record_kind` | Yes | `enum` | Canonical kind: `structure`, `material_entry`, `phase_entry`, `dataset_member`, `repository_asset` |
| `source` | Yes | object | Provider identity and source-native record identifiers |
| `access` | Yes | object | Access level and authentication posture |
| `license` | Yes | object | License and redistribution posture |
| `snapshot` | Yes | object | Snapshot/version lineage for the staged record |
| `raw_payload` | Yes | object | Where the provider-native payload is stored and how it is encoded |
| `common` | Yes | object | Cross-source normalized common fields, still source-adjacent |
| `qa` | Yes | object | Validation state, issues, and duplicate/schema-drift flags |
| `lineage` | Yes | object | Adapter, manifest, and transformation lineage |
| `source_metadata` | Yes | object | Provider-specific content with no cross-source guarantees |

### `source` block

The `source` block is the minimal provider identity boundary.

| Field | Required | Meaning |
|---|---|---|
| `source_key` | Yes | Registry key such as `hypod_x`, `cod`, `materials_project`, `oqmd`, `jarvis` |
| `source_name` | Yes | Human-readable provider name |
| `source_record_id` | Yes | Provider-native identifier such as `mp-149`, COD ID, OQMD ID |
| `source_record_url` | Recommended | Stable landing page or API URL for the record |
| `source_namespace` | Optional | Namespace or collection identifier when the provider has multiple collections |
| `record_title` | Optional | Human-readable title or label from the source |

### `access` block

This block satisfies the governance requirement that open, restricted, and
subscription-backed sources remain explicit.

| Field | Required | Meaning |
|---|---|---|
| `access_level` | Yes | `open`, `restricted`, `subscription`, or `manual` |
| `auth_required` | Yes | Whether credentials or institution-specific access are required |
| `access_surface` | Yes | `api`, `optimade`, `bulk_download`, `cif_download`, `manual_import`, `repository_archive`, or mixed |
| `terms_url` | Optional | Terms-of-use or access-policy URL |
| `redistribution_posture` | Yes | `allowed`, `allowed_with_attribution`, `unknown`, `not_allowed` |

### `license` block

| Field | Required | Meaning |
|---|---|---|
| `license_expression` | Yes | SPDX-like value if available, otherwise source-native string |
| `license_url` | Recommended | Canonical license reference URL |
| `license_category` | Yes | `open`, `restricted`, `subscription`, `custom`, `unknown` |
| `attribution_required` | Yes | Whether downstream attribution must be carried |
| `commercial_use_allowed` | Optional | Useful when the source terms distinguish research-only vs broader use |
| `notes` | Optional | Free-text clarifications when the source posture is not machine-clean |

### `snapshot` block

| Field | Required | Meaning |
|---|---|---|
| `snapshot_id` | Yes | Local snapshot identifier used on disk and in manifests |
| `source_version` | Optional | Provider version string if published |
| `source_release_date` | Optional | Provider release or snapshot date |
| `retrieved_at_utc` | Yes | Timestamp when the snapshot was pulled or staged |
| `retrieval_mode` | Yes | `api`, `optimade`, `bulk`, `manual`, `fixture`, or mixed |
| `snapshot_manifest_path` | Yes | Path to the snapshot manifest JSON |

### `raw_payload` block

The contract must keep the original provider payload addressable without
forcing every source into one in-memory schema.

| Field | Required | Meaning |
|---|---|---|
| `payload_path` | Yes | Workspace-relative path to the stored payload or row bundle |
| `payload_format` | Yes | `json`, `jsonl`, `cif`, `csv`, `xml`, `zip_member`, or similar |
| `payload_encoding` | Optional | Compression or text encoding details |
| `content_hash` | Yes | Stable digest of the stored raw payload |
| `raw_excerpt` | Optional | Small adapter-produced excerpt for debugging only |

### `common` block

This block contains normalized cross-source fields that Phase 2 and Phase 3 can
reason over without erasing provider detail.

| Field | Required | Meaning |
|---|---|---|
| `chemical_system` | Recommended | Canonical chemical system label such as `Al-Cu-Fe` |
| `elements` | Recommended | Sorted unique element list |
| `formula_raw` | Optional | Provider formula as published |
| `formula_reduced` | Recommended | Reduced formula when derivable |
| `composition` | Recommended | Normalized element fractions if derivable |
| `structure_representations` | Optional | One or more structure payload references, such as CIF, OPTIMADE structure, lattice+sites |
| `space_group` | Optional | Provider-reported symmetry metadata |
| `dimension_class` | Optional | `periodic`, `quasiperiodic`, `approximant`, `unknown` |
| `reported_properties` | Optional | Provider-supplied metrics such as formation energy, band gap, tags |
| `citations` | Optional | Published references or dataset citations |
| `keywords` | Optional | Provider tags carried through for later filtering |

`common` is normalized enough for downstream matching and QA, but it is still a
source-staging block, not a pipeline-ready reference-phase output.

### `qa` block

This block is mandatory because Phase 2 is required to emit QA metrics.

| Field | Required | Meaning |
|---|---|---|
| `schema_valid` | Yes | Passed Pydantic/schema validation for the canonical record |
| `required_field_gaps` | Yes | Missing required source or common fields |
| `normalization_warnings` | Yes | Lossy mappings, unit assumptions, parse fallbacks |
| `duplicate_keys` | Optional | Duplicate fingerprints or likely cross-source duplicate references |
| `structure_status` | Yes | `valid`, `missing`, `malformed`, `unsupported` |
| `composition_status` | Yes | `valid`, `missing`, `malformed`, `partial` |
| `schema_drift_flags` | Yes | Unexpected source fields, changed types, or removed keys |
| `needs_manual_review` | Yes | Gate for sources that parsed but remain operationally risky |

### `lineage` block

| Field | Required | Meaning |
|---|---|---|
| `adapter_key` | Yes | Adapter or profile used to ingest the record |
| `adapter_family` | Yes | `direct`, `optimade`, `cif_conversion`, `curated_manual`, `archive_repository` |
| `adapter_version` | Yes | Code or profile version |
| `fetch_manifest_id` | Yes | Manifest ID for the fetch stage |
| `normalize_manifest_id` | Yes | Manifest ID for the canonical normalization stage |
| `parent_snapshot_ids` | Optional | Useful for merged or incremental snapshots |
| `projection_status` | Optional | Phase 3 status once projected into reference-phase outputs |

### `source_metadata` block

This is the only intentionally loose section.

- It may contain provider-native field names, nested documents, raw OPTIMADE
  attributes, source-specific tags, or dataset-specific annotations.
- It must not be used for fields that should be stable across sources.
- Providers may evolve this block without forcing a contract change, as long as
  the stable core remains valid.

## Example Artifact

```json
{
  "schema_version": "raw-source-record/v1",
  "local_record_id": "src_materials_project_8f0ac5e2471d6b2f",
  "record_kind": "material_entry",
  "source": {
    "source_key": "materials_project",
    "source_name": "Materials Project",
    "source_record_id": "mp-149",
    "source_record_url": "https://materialsproject.org/materials/mp-149",
    "record_title": "Si"
  },
  "access": {
    "access_level": "open",
    "auth_required": true,
    "access_surface": "api",
    "terms_url": "https://materialsproject.org/api",
    "redistribution_posture": "allowed_with_attribution"
  },
  "license": {
    "license_expression": "source-defined",
    "license_url": "https://materialsproject.org/terms",
    "license_category": "open",
    "attribution_required": true,
    "commercial_use_allowed": null,
    "notes": "API key required even though the source is part of the open-access plan."
  },
  "snapshot": {
    "snapshot_id": "materials_project_2026_04_02_api_default",
    "source_version": "mp-api",
    "source_release_date": "2026-04-02",
    "retrieved_at_utc": "2026-04-02T22:30:00Z",
    "retrieval_mode": "api",
    "snapshot_manifest_path": "data/external/sources/materials_project/materials_project_2026_04_02_api_default/snapshot_manifest.json"
  },
  "raw_payload": {
    "payload_path": "data/external/sources/materials_project/materials_project_2026_04_02_api_default/raw_rows.jsonl",
    "payload_format": "jsonl",
    "payload_encoding": "utf-8",
    "content_hash": "sha256:5c8f4b...",
    "raw_excerpt": {
      "material_id": "mp-149"
    }
  },
  "common": {
    "chemical_system": "Si",
    "elements": ["Si"],
    "formula_raw": "Si2",
    "formula_reduced": "Si",
    "composition": {
      "Si": 1.0
    },
    "structure_representations": [
      {
        "kind": "lattice_sites",
        "format": "emmet_structure",
        "path": "data/external/sources/materials_project/materials_project_2026_04_02_api_default/attachments/mp-149.json"
      }
    ],
    "space_group": {
      "symbol": "Fd-3m",
      "number": 227
    },
    "dimension_class": "periodic",
    "reported_properties": {
      "formation_energy_ev_per_atom": -5.42
    },
    "citations": [],
    "keywords": ["computed", "benchmark"]
  },
  "qa": {
    "schema_valid": true,
    "required_field_gaps": [],
    "normalization_warnings": [],
    "duplicate_keys": [],
    "structure_status": "valid",
    "composition_status": "valid",
    "schema_drift_flags": [],
    "needs_manual_review": false
  },
  "lineage": {
    "adapter_key": "materials_project_direct_api_v1",
    "adapter_family": "direct",
    "adapter_version": "v1",
    "fetch_manifest_id": "source_fetch_1234abcd",
    "normalize_manifest_id": "source_normalize_5678efgh",
    "parent_snapshot_ids": [],
    "projection_status": "not_projected"
  },
  "source_metadata": {
    "builder": {
      "provider": "materials_project"
    }
  }
}
```

## Cross-Source Fit Check

The stable core is intentionally broad enough for the first-wave sources and the
expanded watchlist.

| Source | How it fits the stable core | What remains in `source_metadata` |
|---|---|---|
| `HYPOD-X` | Dataset member with QC or approximant tags, source paper URL, local snapshot lineage | QC-family annotations, paper-specific descriptors, dataset-native columns |
| `COD` / CIF sources | `record_kind=structure`, CIF payload path, formula/composition in `common`, access via CIF or OPTIMADE | CIF header quirks, deposition metadata, author blocks |
| `Materials Project` | API-backed `material_entry`, authenticated access posture, structure/property bundle | Emmet-specific nested documents and provenance internals |
| `OQMD` / OPTIMADE | Direct API or OPTIMADE source with open license and possibly bulk dump snapshot | OQMD-native query metadata, OPTIMADE attributes not promoted to stable core |
| `JARVIS` | Direct or OPTIMADE-backed `material_entry` with official toolkit lineage | JARVIS-specific descriptors, source portal metadata |

This is the key guard against HYPOD-X overfitting.

## Explicit Separation From Current `IngestRecord`

The current processed model in `materials_discovery.common.schema.IngestRecord`
has only:

- `system`
- `phase_name`
- `composition`
- `source`
- `metadata`

That model is too narrow for raw-source staging and should remain downstream.

### What belongs only in the raw-source contract

- source-native IDs and URLs
- snapshot lineage
- access and license posture
- raw payload references
- structure payload formats
- schema drift and parse warnings
- provider-specific nested metadata

### What belongs only in pipeline-ready derived outputs

- normalized `phase_name`
- reference-phase selection decisions
- pipeline-specific filtering decisions
- downstream benchmark or discovery-stage fields

### What does not belong in either Phase 1 source staging contract

- candidate generation fields
- screen or validation scores
- new DFT computations

## Proposed Pydantic Placement Strategy

Phase 2 should implement the canonical models under:

```text
materials-discovery/src/materials_discovery/data_sources/schema.py
```

Recommended model set:

- `SourceRegistryEntry`
- `SourceSnapshotManifest`
- `CanonicalRawSourceRecord`
- `CommonStructureRepresentation`
- `SourceQaReport`

Placement rationale:

- `common/schema.py` currently defines stable pipeline runtime contracts such as
  `SystemConfig`, `CandidateRecord`, and the current `IngestRecord`.
- Moving the raw-source contract into `common/schema.py` immediately would blur
  the boundary between source staging and downstream discovery artifacts.
- `data_sources/schema.py` keeps Phase 2 additive and low-risk.
- If the raw-source contract later proves useful outside ingestion, specific
  shared enums or submodels can be promoted deliberately.

## Non-Goals

- Replacing `CandidateRecord`, `DigitalValidationRecord`, or other downstream
  pipeline schemas in Phase 1
- Defining the final cross-source deduplication policy across all providers
- Forcing every provider into one structure serialization format
- Building a database-backed warehouse
- Performing DFT or high-fidelity computations during source ingestion

## Requirement Alignment

| Requirement | How this contract satisfies it |
|---|---|
| `DATA-01` | Defines a source-agnostic raw staging model that can represent both QC-specific and general materials datasets |
| `DATA-02` | Makes provenance, snapshot metadata, license metadata, and immutable local IDs mandatory |
| `OPS-01` | Requires explicit `access` and `license` posture on every record |
| `OPS-02` | Preserves adapter-family, source, and QA metadata needed for priority-aware registry decisions |

