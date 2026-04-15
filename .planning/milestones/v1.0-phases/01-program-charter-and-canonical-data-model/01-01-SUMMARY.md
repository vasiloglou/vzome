---
phase: 01-program-charter-and-canonical-data-model
plan: 01
subsystem: planning
tags: [ingestion, data-contract, source-registry, integration-design, materials-discovery]
requires: []
provides:
  - canonical raw-source record contract for multi-source staging
  - provider registry and priority matrix covering primary, watchlist, restricted, and OPTIMADE-horizon sources
  - integration design preserving mdisc ingest while introducing a data_sources package boundary
affects: [02-ingestion-platform-mvp, 03-reference-phase-integration-with-current-pipeline, requirements-traceability]
tech-stack:
  added: [markdown]
  patterns: [docs-first contract design, file-backed source staging, stable-core-plus-source-metadata schema]
key-files:
  created:
    - .planning/phases/01-program-charter-and-canonical-data-model/01-DATA-CONTRACT.md
    - .planning/phases/01-program-charter-and-canonical-data-model/01-SOURCE-REGISTRY.md
    - .planning/phases/01-program-charter-and-canonical-data-model/01-INTEGRATION-DESIGN.md
    - .planning/phases/01-program-charter-and-canonical-data-model/01-01-SUMMARY.md
  modified:
    - .planning/phases/01-program-charter-and-canonical-data-model/01-01-PLAN.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
key-decisions:
  - "Keep the canonical raw-source contract separate from the existing processed IngestRecord."
  - "Use materials_discovery/data_sources/ as the provider-ingestion package and keep backends/ as a thin runtime-mode bridge."
  - "Lock Phase 2 priority to HYPOD-X, COD, Materials Project, OQMD, and JARVIS while preserving the broader watchlist and tooling inventory."
patterns-established:
  - "Stable raw-source core: provenance, access, license, snapshot, QA, and lineage are mandatory on every staged record."
  - "Registry-driven source planning: each provider carries adapter-family, access, tooling, and priority metadata."
  - "CLI preservation: mdisc ingest stays stable while canonical source staging is added behind it."
requirements-completed: [OPS-01, OPS-02]
duration: 9min
completed: 2026-04-02
---

# Phase 1 Plan 01: Lock The Ingestion Contract Summary

**Canonical raw-source contract, provider priority registry, and `mdisc ingest` bridge design for a file-backed multi-source ingestion layer**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-03T03:52:43Z
- **Completed:** 2026-04-03T04:02:07Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Defined a canonical raw-source record model with mandatory provenance,
  licensing, access, snapshot, QA, and lineage fields distinct from the current
  processed `IngestRecord`.
- Built the authoritative source registry covering primary v1 targets,
  secondary open watchlist providers, restricted sources, OPTIMADE-horizon
  providers, and the official tooling surfaces that affect implementation cost.
- Wrote the integration design that preserves `mdisc ingest`, introduces the
  `materials_discovery/data_sources/` boundary, and documents the migration path
  from the current HYPOD-X-shaped ingest seam.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define the canonical raw-source contract** - `992bc341` (`feat`)
2. **Task 2: Define the source registry and priority matrix** - `30a16210` (`feat`)
3. **Task 3: Define the integration boundary with the current pipeline** - `84127a99` (`feat`)

Plan metadata is captured in the follow-up planning docs commit that includes
this summary, the verification report, and the planning-state updates.

## Files Created/Modified

- `.planning/phases/01-program-charter-and-canonical-data-model/01-DATA-CONTRACT.md` - Canonical raw-source record contract and package-placement strategy
- `.planning/phases/01-program-charter-and-canonical-data-model/01-SOURCE-REGISTRY.md` - Provider registry, access/licensing posture, priority matrix, and tooling inventory
- `.planning/phases/01-program-charter-and-canonical-data-model/01-INTEGRATION-DESIGN.md` - Package, manifest, artifact, and CLI bridge design for multi-source ingestion
- `.planning/phases/01-program-charter-and-canonical-data-model/01-01-PLAN.md` - Added explicit requirement IDs for workflow traceability and automated completion
- `.planning/STATE.md` - Reconstructed execution state for the active phase
- `.planning/ROADMAP.md` - Expanded Phase 1 deliverables to include the broader source/tooling inventory
- `.planning/REQUIREMENTS.md` - Marked `OPS-01` and `OPS-02` complete while leaving `DATA-01` and `DATA-02` pending until implementation exists

## Decisions Made

- Kept the raw-source staging contract separate from `materials_discovery.common.schema.IngestRecord` so Phase 2 does not overfit to the current HYPOD-X normalization path.
- Treated official client and tooling surfaces as part of the source registry because they materially change implementation cost and mapping confidence.
- Preserved `mdisc ingest` as the stable operator-facing entrypoint while pushing provider-specific ingestion logic into a new `data_sources/` package.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added missing requirement IDs to the plan frontmatter**

- **Found during:** Metadata and state update pass
- **Issue:** `01-01-PLAN.md` did not include a `requirements:` frontmatter field, which would have blocked the standard requirements-completion step and left traceability inconsistent with the completed work.
- **Fix:** Added `DATA-01`, `DATA-02`, `OPS-01`, and `OPS-02` to the plan frontmatter so requirement completion could run through the normal workflow.
- **Files modified:** `.planning/phases/01-program-charter-and-canonical-data-model/01-01-PLAN.md`
- **Verification:** The plan now carries the requirement IDs needed by the state-update workflow.
- **Committed in:** final metadata docs commit

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix was metadata-only and kept the workflow aligned with the work already completed.

## Issues Encountered

- Verification showed that `DATA-01` and `DATA-02` remain implementation-gated.
  The design artifacts are complete, but the actual ingest code still lacks
  canonical raw-source staging and multi-source adapters, so those
  requirements were returned to pending status.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 2 can now implement the adapter framework against a fixed raw-source
  contract, provider taxonomy, and artifact layout.
- Phase 3 has an explicit bridge design for preserving `mdisc ingest` and the
  no-DFT boundary while projecting canonical source snapshots into processed
  reference-phase outputs.
- `DATA-01` and `DATA-02` should stay pending until the canonical raw-source
  contract and multi-source ingest path are implemented in code.

## Known Stubs

None.

## Self-Check: PASSED

- Verified the three design artifacts and summary file exist on disk.
- Verified task commits `992bc341`, `30a16210`, and `84127a99` exist in git history.
