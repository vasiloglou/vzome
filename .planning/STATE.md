---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: milestone
current_phase: 32
current_phase_name: cif-and-material-string-exporters
current_plan: 3
status: verifying
stopped_at: Completed 32-03-PLAN.md
last_updated: "2026-04-07T03:30:13.391Z"
last_activity: 2026-04-07
progress:
  total_phases: 3
  completed_phases: 2
  total_plans: 6
  completed_plans: 6
  percent: 33
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-06)

**Core value:** Build one reproducible system where trusted materials data, physically grounded no-DFT validation, and LLM-guided structure generation reinforce each other instead of living in separate prototypes.
**Current focus:** Phase 32 — cif-and-material-string-exporters

## Current Position

Current Phase: 32
Current Phase Name: cif-and-material-string-exporters
Total Phases: 3
Current Plan: 3
Total Plans in Phase: 3
Phase: 32 (cif-and-material-string-exporters) — EXECUTING
Plan: 3 of 3
Status: Phase complete — ready for verification
Last activity: 2026-04-07
Last Activity Description: Phase 32 execution started

Progress: [███░░░░░░░] 33%

## Performance Metrics

**Velocity:**

- Total plans completed: 84
- Average duration: 12 min
- Total execution time: archived across prior milestones

**By Milestone:**

| Milestone | Phases | Plans | Outcome |
|-----------|--------|-------|---------|
| v1.0 | 1-9 | 26 | Shipped |
| v1.1 | 10-18 | 27 | Shipped |
| v1.2 | 19-24 | 18 | Shipped |
| v1.3 | 25-27 | 9 | Shipped |
| v1.4 | 28-30 | 9 | Shipped |
| v1.5 | 31-33 | 3 | Active |
| Phase 31 P01 | 6min | 2 tasks | 4 files |
| Phase 31 P02 | 7min | 2 tasks | 6 files |
| Phase 31 P03 | 5min | 2 tasks | 5 files |
| Phase 32 P01 | 6 min | 2 tasks | 5 files |
| Phase 32 P02 | 2 min | 2 tasks | 5 files |
| Phase 32 P03 | 3 min | 2 tasks | 8 files |

## Accumulated Context

### Decisions

Decisions are logged in `PROJECT.md`. Recent decisions affecting current work:

- [Milestone v1.1 archived]: The operator-governed closed-loop campaign
  workflow is shipped, audited, and archived.

- [Milestone v1.2 archived]: Local serving, specialized workflow lanes, and
  hosted/local/specialized benchmark workflows are shipped and fully audited.

- [Milestone v1.3 archived]: Adapted local checkpoint registration,
  generation, benchmark comparison, and rollback guidance are shipped and fully
  audited.

- [Milestone v1.4]: Expand Project 3 through checkpoint lifecycle and
  promotion rather than jumping directly to full training-job automation.

- [Milestone v1.4]: Keep the workflow operator-governed, file-backed, and
  no-DFT while adapted-checkpoint count and lifecycle complexity increase.

- [Milestone v1.4]: Treat promoted, pinned, and retired checkpoints as
  explicit workflow state rather than informal config conventions.

- [Phase 28]: Use a hybrid lifecycle model with immutable per-checkpoint
  registration facts plus a central lifecycle index for promoted/default,
  pinning, retirement, and history.

- [Phase 28]: Config defines the checkpoint family on a lane; the lifecycle
  registry resolves the promoted default member when no explicit pin is given.

- [Phase 28]: Retired checkpoints must never be selected implicitly again, but
  they remain replayable and auditable.

- [Phase 29]: Family-only adapted lanes now resolve the promoted default member
  for new execution, while explicit `checkpoint_id` values remain deliberate
  family pins.

- [Phase 29]: Replay must preserve the recorded checkpoint identity even after
  later promotion or retirement changes, and benchmark/compare output must
  surface the resulting lifecycle selection metadata.

- [Phase 30]: Lifecycle benchmarks use explicit target roles for the promoted
  default, the candidate checkpoint, and the rollback baseline so benchmark
  recommendations stay structured and auditable.

- [Phase 30]: The operator lifecycle stays CLI-first: register or pin a
  checkpoint, benchmark candidate vs promoted default vs baseline, then
  promote, keep, or retire based on file-backed evidence.

- [Milestone v1.5]: Start the next LLM milestone with a translation bridge from
  Zomic into external materials-LLM encodings before attempting live external
  model execution or training automation.

- [Milestone v1.5]: Treat CIF and material-string exports as additive interop
  artifacts with explicit fidelity/loss metadata rather than replacements for
  Zomic as the QC-native source of truth.

- [Phase 31]: Kept translation fidelity separate from corpus FidelityTier so lossy export semantics do not alter shipped LLM corpus workflows.
- [Phase 31]: Standardized translation loss-reason names and added requires_periodic_cell metadata so later exporters can classify representational loss explicitly.
- [Phase 31]: Exposed list_translation_targets() and resolve_translation_target() as the stable registry API for later translation phases.
- [Phase 31]: Made coordinate origin explicit through a stable structure-realization helper rather than hiding branch logic inside the translation module.
- [Phase 31]: Reserved exact for candidates with strong periodic-safe evidence plus stored fractional coordinates; mixed-origin candidates stay conservative at approximate.
- [Phase 31]: QC-native periodic exports are marked lossy with explicit reasons instead of silently degrading to a weaker success state.
- [Phase 31]: Kept approximate covered in translation-core tests rather than adding a third fixture because Plan 03 needed to freeze the two exporter-facing boundary cases first.
- [Phase 32]: Centralized translation export validation in translation_export.py so CIF and later target families share one export-readiness gate and copy-not-mutate dispatch contract. — Plan 01 needed a stable seam before adding the material-string target, and the new tests prove both deterministic behavior and clear failure modes from one shared API.
- [Phase 32]: Kept CIF output deterministic and explicitly labeled with source/fidelity/loss metadata in comment lines so lossy periodic-proxy exports remain visibly honest. — The repo-local CIF parser accepts the emitted payload after comment stripping, while the comment preamble preserves the interoperability boundary that Phase 31 established.
- [Phase 32]: Implemented crystaltextllm_material_string as a bare CrystalTextLLM-compatible body so the shipped target name remains honest about downstream parser compatibility. — The phase review showed that repo-only headers in emitted_text would break CrystalTextLLM parsing and make the target contract misleading, so the raw body now stays parser-compatible.
- [Phase 32]: Kept source linkage, fidelity tier, and loss metadata on TranslatedStructureArtifact rather than embedding repo-only headers into the raw material string. — This preserves auditable provenance on the artifact while allowing the exported body to remain usable by downstream CrystalTextLLM-style tooling.
- [Phase 32]: Frozen the shipped exporter contract on checked-in goldens: CIF keeps fidelity/loss comments, while material-string outputs remain bare CrystalTextLLM-compatible bodies.
- [Phase 32]: Kept lossy material-string provenance on TranslatedStructureArtifact and used repo-local parse_cif regressions to freeze parser compatibility before CLI integration.

### Pending Todos

None yet.

### Blockers/Concerns

None right now.

## Session Continuity

Last session: 2026-04-07T03:30:13.389Z
Stopped at: Completed 32-03-PLAN.md
Resume file: None
