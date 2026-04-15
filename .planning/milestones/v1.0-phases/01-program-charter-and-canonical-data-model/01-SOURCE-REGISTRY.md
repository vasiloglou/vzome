# Source Registry And Priority Matrix

## Purpose

This document is the Phase 1 source authority for the Material Design Data
Ingestion project.

It answers four operational questions:

1. Which providers are in scope for the program?
2. Which ones are Phase 2 implementation targets versus watchlist inventory?
3. What adapter family should each provider use?
4. Which official client or tooling surfaces matter for implementation cost?

## Registry Contract

Each provider should have one `SourceRegistryEntry` with the following fields.

| Field | Meaning |
|---|---|
| `source_key` | Stable internal key such as `materials_project` or `oqmd` |
| `display_name` | Human-readable provider name |
| `portfolio_group` | `primary_v1`, `secondary_watchlist`, `restricted`, or `optimade_horizon` |
| `access_level` | `open`, `restricted`, `subscription`, or `manual` |
| `license_posture` | High-level license/read-use posture such as `CC0`, `CC-BY`, `source-defined`, `custom`, `licensed`, `unknown` |
| `access_surface` | Main access mode: `direct_api`, `optimade`, `bulk_snapshot`, `cif_download`, `repository_archive`, `manual_import`, or mixed |
| `primary_adapter_family` | `direct`, `optimade`, `cif_conversion`, `curated_manual`, or `archive_repository` |
| `secondary_adapter_family` | Optional fallback or follow-on adapter family |
| `expected_record_kinds` | Main canonical raw record kinds likely to appear |
| `official_tooling_surface` | Official or de facto client/tooling surface that should shape implementation |
| `scientific_value` | Relative Phase 2 value: `high`, `medium`, `low` |
| `implementation_cost` | Relative Phase 2 cost: `low`, `medium`, `high` |
| `licensing_friction` | Relative friction: `low`, `medium`, `high` |
| `phase2_priority` | `P0`, `P1`, `P2`, or `deferred` |
| `v1_posture` | `build_now`, `design_for_later`, or `do_not_block_v1` |
| `notes` | Important caveats or gating details |

## Adapter Family Taxonomy

| Family | Use when | Typical sources |
|---|---|---|
| `direct` | The provider has a meaningful native API, download flow, or dataset package that should stay first-class | HYPOD-X, Materials Project, OQMD, JARVIS, AFLOW |
| `optimade` | The provider exposes a mature OPTIMADE endpoint and the interoperable path is a good first implementation | OQMD, JARVIS, Alexandria, OPTIMADE-horizon providers |
| `cif_conversion` | The provider is effectively a structure/CIF source and the integration work is dominated by parsing and normalization | COD |
| `curated_manual` | The source is specialized, researcher-curated, or awkward enough that manual or semi-manual import remains acceptable initially | B-IncStrDB, ICSD in restricted mode |
| `archive_repository` | The source behaves more like a dataset archive or repository than a query-first materials API | Materials Cloud, NIMS MDR, NOMAD repository-style exports |

## Acceptance Policy

- `primary_v1` sources must be open or clearly accessible and must not require
  subscription-only access to make the MVP useful.
- `restricted` sources must be tracked with explicit gating metadata so the
  program does not accidentally depend on them for v1.
- `optimade_horizon` sources should stay visible in the registry even when they
  are not selected for the first implementation wave.
- Official client or documentation surfaces are part of the source inventory.
  Phase 2 planning should treat them as cost and correctness inputs.

## Phase 2 Implementation Order

This is the recommended first-wave order after Phase 1.

| Rank | Source | Why this order | Scientific value | Implementation cost | Licensing friction | Recommended first adapter |
|---|---|---|---|---|---|---|
| 1 | `HYPOD-X` | Closest fit to the QC and approximant mission and already aligned with current ingest thinking | High | Medium | Low | `direct` snapshot adapter |
| 2 | `COD` | Open, broad, easy to retrieve, and valuable for structure/CIF normalization | High | Medium | Low | `cif_conversion` with optional OPTIMADE follow-on |
| 3 | `Materials Project` | Mature ecosystem and benchmark relevance justify early authenticated support | High | Medium | Medium | `direct` API adapter |
| 4 | `OQMD` | Open license plus both REST and OPTIMADE options make it strategically reusable | High | Medium | Low | `direct` API first, OPTIMADE second |
| 5 | `JARVIS` | Strong materials-design fit and official tooling make it a good closing P0 source | High | Medium | Low | `optimade` or `direct` depending endpoint maturity |

`NOMAD`, `Alexandria`, `Open Materials Database`, `AFLOW`, `Materials Cloud`,
`NIMS MDR`, and `B-IncStrDB` stay in the registry from day one, but they should
not delay the P0 adapter wave.

## Primary v1 Targets

| Source | Access level | License posture | Access surface | Primary adapter family | Secondary family | Expected record kinds | Official tooling surface | Phase 2 priority | v1 posture | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| `HYPOD-X` | `open` | `source-defined open dataset` | `bulk_snapshot` | `direct` | none | `dataset_member`, `phase_entry` | Dataset and paper reference; no official client surfaced in Phase 1 research | `P0` | `build_now` | Treat as a direct snapshot-backed dataset adapter, not an API-first design |
| `COD` | `open` | `CC0` | `cif_download` plus `optimade` availability | `cif_conversion` | `optimade` | `structure`, `phase_entry` | Generic CIF parsers plus OPTIMADE interoperability stack | `P0` | `build_now` | CIF normalization is the main complexity, not auth or license friction |
| `Materials Project` | `open` with API key | `source-defined open` | `direct_api` plus `optimade` | `direct` | `optimade` | `material_entry`, `structure` | `mp-api`, `Emmet` | `P0` | `build_now` | Authentication is acceptable for v1 because access is clear and ecosystem support is strong |
| `OQMD` | `open` | `CC-BY 4.0` | `direct_api`, `optimade`, `bulk_snapshot` | `direct` | `optimade` | `material_entry`, `structure` | `qmpy`, OQMD REST docs | `P0` | `build_now` | Support live-query first, but keep bulk snapshot mode in the design |
| `JARVIS` | `open` | `source-defined open` | `optimade` plus direct portal/toolkit path | `optimade` | `direct` | `material_entry`, `structure` | `JARVIS-Tools` | `P0` | `build_now` | Choose direct vs OPTIMADE in Phase 2 based on endpoint completeness, not ideology |

## Secondary Open Watchlist

| Source | Access level | License posture | Access surface | Primary adapter family | Secondary family | Expected record kinds | Official tooling surface | Phase 2 priority | v1 posture | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| `NOMAD` | `open` | `source-defined open` | `direct_api`, repository export, OPTIMADE presence | `archive_repository` | `optimade` | `dataset_member`, `material_entry`, `repository_asset` | NOMAD API/docs and GitHub-linked dev surface | `P1` | `design_for_later` | Rich metadata model makes it valuable but also more complex than the P0 set |
| `Alexandria` | `open` | `CC-BY 4.0` | `bulk_snapshot` plus `optimade` | `optimade` | `direct` | `material_entry`, `structure` | Official downloads plus OPTIMADE endpoint | `P1` | `design_for_later` | Good candidate for large-scale computed enrichment once the core adapter framework is stable |
| `Open Materials Database` | `open` | `source-defined open` | `direct_api` and toolkit-driven access; OPTIMADE-listed | `direct` | `optimade` | `material_entry`, `structure` | `httk` | `P1` | `design_for_later` | Should be treated as database-plus-toolkit rather than only a raw endpoint |
| `B-IncStrDB` | `open` or researcher-curated access | `source-defined` | specialized web/manual access | `curated_manual` | `direct` | `structure`, `phase_entry` | Bilbao source docs | `P2` | `design_for_later` | Highly relevant scientifically, but narrow and specialized enough to trail the broader sources |
| `AFLOW` | `open` | `source-defined open` | `direct_api` | `direct` | `optimade-like interoperability if present later` | `material_entry`, `structure` | AFLOW REST and AFLUX docs | `P1` | `design_for_later` | Strong secondary computed-materials source with durable API patterns |
| `Materials Cloud` | `open` | `source-defined open` | `repository_archive` plus archive interoperability | `archive_repository` | `optimade` | `repository_asset`, `dataset_member`, `structure` | Materials Cloud archive docs | `P1` | `design_for_later` | Better modeled as a curated archive source than as one homogeneous API |
| `NIMS MDR` | `open` to browse, repository-specific access patterns | `source-defined` | `repository_archive` | `archive_repository` | `curated_manual` | `repository_asset`, `dataset_member` | NIMS MDR portal/docs | `P2` | `design_for_later` | Important as a repository-style source, but likely lower immediate leverage than the main materials databases |

## Restricted Or Frictionful Sources

| Source | Access level | License posture | Access surface | Primary adapter family | Expected record kinds | Official tooling surface | Phase 2 priority | v1 posture | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `MPDS` | `restricted` | `commercial or custom terms` | `direct_api` | `direct` | `material_entry`, `structure` | `mpds_client` and MPDS developer docs | `deferred` | `do_not_block_v1` | Scientifically valuable, but access and licensing must remain explicit gates |
| `ICSD` | `subscription` | `licensed` | licensed export/manual workflows | `curated_manual` | `structure`, `phase_entry` | Vendor-specific documentation | `deferred` | `do_not_block_v1` | Keep out of the required v1 path entirely |

## OPTIMADE Horizon Inventory

These entries come from the broader provider landscape surfaced by the
OPTIMADE network. They are not Phase 2 commitments, but they should remain in
the registry so the ecosystem picture does not collapse back to the first five
sources.

| Source | Access level | Access surface | Primary adapter family | Expected record kinds | Official tooling surface | Priority | Notes |
|---|---|---|---|---|---|---|---|
| `MPOD` | `open` | `optimade` | `optimade` | `structure` | `optimade-python-tools` | `P2` | Track as a structure-focused interoperable source candidate |
| `MPDD` | `open` | `optimade` | `optimade` | `structure`, `material_entry` | `optimade-python-tools` | `P2` | Useful to keep visible even if not in the first program wave |
| `ODBX` | `open` | `optimade` | `optimade` | `material_entry` | `optimade-python-tools` | `P2` | Horizon provider, not a v1 commitment |
| `Matterverse` | `open` | `optimade` | `optimade` | `material_entry` | `optimade-python-tools` | `P2` | Horizon provider from the wider OPTIMADE ecosystem |

## Official Tooling Inventory

The source plan must track tools as first-class planning inputs because they
strongly affect adapter cost and field-mapping confidence.

| Tooling surface | Primary sources influenced | Why it matters |
|---|---|---|
| `mp-api` | Materials Project | Official client for authenticated API access and record retrieval patterns |
| `Emmet` | Materials Project | Clarifies Materials Project document shapes and useful nested fields |
| `JARVIS-Tools` | JARVIS | Official data-access and materials-design tooling surface |
| `optimade-python-tools` | OQMD, JARVIS, Alexandria, COD, MPOD, MPDD, ODBX, Matterverse | Shared client, models, validator, and interoperability bridge for OPTIMADE-backed adapters |
| `qmpy` | OQMD | Official OQMD access model and a clue for bulk/local snapshot postures |
| `httk` | Open Materials Database | Defines the OMDB programmatic posture and local handling expectations |
| `mpds_client` | MPDS | Necessary for restricted-source planning even though MPDS is not a v1 dependency |
| `NOMAD` docs and GitHub-linked developer surface | NOMAD | Important because NOMAD behaves like a richer repository/platform, not just a table API |
| `AFLOW` REST and AFLUX docs | AFLOW | Official query and retrieval model for a likely Phase 2 or Phase 3 source |

## Registry Decisions

### 1. Tiering

- `primary_v1` is locked to `HYPOD-X`, `COD`, `Materials Project`, `OQMD`, and
  `JARVIS`.
- `secondary_watchlist` remains active design input in Phase 1 and should be
  visible in source-aware config and docs.
- `restricted` sources are tracked explicitly, not silently omitted.

### 2. Adapter posture

- Do not force all sources through `OPTIMADE` just because several providers
  support it.
- Do not force all sources through direct API adapters either.
- Use the mixed strategy locked in discuss-phase:
  snapshot or bulk where that fits the source, and direct API or `OPTIMADE`
  where the official access surface is mature.

### 3. Official-tooling posture

- Official client or docs count as part of the source inventory.
- A source with a strong official client surface is cheaper and less ambiguous
  to implement than a source with only ad hoc community wrappers.

## How This Drives Phase 2

Phase 2 should begin with:

1. `HYPOD-X` direct snapshot adapter
2. `COD` CIF-conversion adapter
3. `Materials Project` direct API adapter
4. `OQMD` direct API adapter plus shared `OPTIMADE` groundwork
5. `JARVIS` `OPTIMADE` or direct adapter, chosen by maturity at implementation time

The framework built for those adapters should still anticipate:

- later `optimade` providers from the watchlist and horizon inventory
- repository/archive flows such as `NOMAD`, `Materials Cloud`, and `NIMS MDR`
- curated/manual or restricted-source flows such as `B-IncStrDB`, `MPDS`, and
  `ICSD`

## Requirement Alignment

| Requirement | How this registry satisfies it |
|---|---|
| `DATA-01` | Keeps at least one QC-specific source and multiple general materials databases in the active Phase 2 target set |
| `DATA-02` | Forces every source entry to carry access, license, and tooling posture that feed record-level provenance rules |
| `OPS-01` | Makes open, restricted, subscription, and manual access categories explicit |
| `OPS-02` | Prioritizes sources using scientific value, implementation cost, and licensing friction |

