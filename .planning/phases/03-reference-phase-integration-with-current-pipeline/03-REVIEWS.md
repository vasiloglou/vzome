---
phase: 3
reviewers:
  - gemini
  - claude
reviewed_at: 2026-04-03T14:07:20Z
plans_reviewed:
  - 03-01-PLAN.md
  - 03-02-PLAN.md
  - 03-03-PLAN.md
---

# Cross-AI Plan Review — Phase 3

`Codex` was intentionally skipped for this review pass because the current
runtime is already Codex and the goal here was independent peer review.

## Gemini Review

# Phase 3 Plan Review: Reference-Phase Integration with Current Pipeline

This review covers the three-plan sequence designed to bridge the multi-source ingestion layer (Phase 2) into the existing materials discovery pipeline (Phase 3).

## Summary

The proposed plans provide a robust and architecturally sound strategy for integrating the new data ingestion runtime with the existing discovery pipeline. By introducing a dedicated `projection.py` layer, the design avoids the "HYPOD-X coupling" trap while maintaining a stable operator CLI. The sequencing is logical: first establishing the semantic mapping (Plan 01), then wiring the CLI and provenance (Plan 02), and finally enforcing system-wide integrity and no-DFT guardrails (Plan 03). The approach successfully balances richer data acquisition with the strict requirement for backward compatibility and no-DFT execution.

## Strengths

- **Clean Abstraction Boundary**: Moving projection logic to `data_sources/projection.py` prevents the legacy normalization code from becoming a bottleneck for new, structure-rich data sources.
- **Reserved Adapter Pattern**: Using the `source_registry_v1` key as the bridge selector is a precise way to introduce the new runtime without disrupting the existing `mock`/`real` backend dispatch logic.
- **Additive Provenance**: The decision to enrich `ArtifactManifest` and `IngestRecord.metadata` additively ensures that downstream consumers (like `hull_proxy.py`) remain functional while gaining access to deeper lineage when needed.
- **Deterministic Derivation**: The explicit precedence policy for `phase_name` (provider label > title > formula > ID) addresses a critical gap in structure-only datasets (e.g., Materials Project, COD) where explicit phase names are often missing.
- **Proactive Guardrails**: Plan 03 includes explicit checks to ensure the ingest path remains offline and no-DFT, which is vital for maintaining the project's core performance and scientific boundary.

## Concerns

- **System Matching Narrowness (LOW)**: While the plan mentions "source-aware matching," there is a risk that different providers represent chemical systems differently (e.g., "Al-Cu-Fe" vs "Cu-Al-Fe" vs "Al30Cu10Fe1").
    - *Mitigation*: Ensure the matching logic in `projection.py` reduces all system identifiers to sorted element sets (e.g., `frozenset(['Al', 'Cu', 'Fe'])`) before comparison.
- **Manifest Schema Evolution (LOW)**: Adding lineage fields to `ArtifactManifest` must ensure that existing JSON parsers or external tools that don't expect these fields won't fail.
    - *Mitigation*: The plan already specifies "additive" changes; ensuring these fields are optional in the Pydantic model is key.
- **Test Data Volume (MEDIUM)**: Providing "offline fixtures" for multi-source tests can bloat the repository if large CIF or JSONL files are included.
    - *Mitigation*: Use "thin" fixtures—truncated versions of canonical records that contain just enough variety to test projection and filtering logic.

## Suggestions

- **Composition Normalization**: Explicitly verify that the projection layer handles the conversion of various source composition formats (e.g., atomic fractions vs. weight percentages) into the pipeline's expected fractional `dict[str, float]` format.
- **Duplicate Handling**: In `projection.py`, clarify the strategy for "dedupe." If two different sources (e.g., MP and OQMD) provide the same phase for the same system, the projection layer should have a clear preference (e.g., "most recent" or "priority source") to avoid redundant reference phases in the hull calculation.
- **CLI Logging**: When `mdisc ingest` runs in the `source_registry_v1` mode, the CLI should output a brief summary of the source/snapshot being projected (e.g., "Projecting 142 records from Materials Project snapshot 2026-04-03...") to provide immediate operator feedback before the final JSON summary.

## Risk Assessment

**Risk Level: LOW**

The plans are highly detailed and ground every implementation step in existing research findings. The dependency ordering is correct, and the "must-haves" align perfectly with the project's requirements for stability and scientific integrity. The separation of the projection logic from the CLI minimizes the blast radius of any bugs in the new data mapping. The primary remaining risk is the semantic quality of the projected phase names, which is well-managed by the proposed deterministic fallback policy and focused unit testing.

---

## Claude Review

# Phase 3 Plan Review: Reference-Phase Integration With Current Pipeline

## Overall Assessment

The three plans form a well-sequenced wave structure (projection core -> CLI bridge -> pipeline compatibility) that correctly decomposes the Phase 3 goal. The research and context documents are thorough, and the plans respect the existing architecture. The main risks are around test isolation and the gap between "projection works" and "projection works with real provider diversity."

---

## Plan 01: Build The Reference-Phase Projection Core

### Summary

Solid foundational plan that puts the semantic hinge — projection from `CanonicalRawSourceRecord` to `IngestRecord` — in its own module with focused tests. The two-task structure (implement, then lock with tests) is appropriate for a wave-1 deliverable that later plans depend on.

### Strengths

- Correctly places projection in `data_sources/projection.py` rather than overloading `data/normalize.py` — prevents the HYPOD-X coupling risk identified in research
- Explicit phase-name derivation precedence policy addresses the biggest determinism risk
- Acceptance criteria include a negative check (no committee/phonon/md/xrd imports)
- Tests are designed to cover both `phase_entry` and periodic `structure`/`material_entry` records
- Keeps `IngestRecord` backward-compatible with additive metadata only

### Concerns

- **MEDIUM**: The plan mentions `project_snapshot_to_ingest_records(...)` alongside `project_canonical_records(...)` but doesn't clarify the division of responsibility. If the snapshot-level function loads records from disk and the record-level function does the mapping, that's fine — but the plan should say so explicitly to avoid the executor building two overlapping entrypoints.
- **MEDIUM**: No explicit handling of records where `common.composition` is `None` or `common.elements` is empty. The `CanonicalCommonFields` model allows both. The projection module needs a clear policy: skip these records, derive composition from formula, or fail. The research mentions composition normalization but the plan's action text doesn't call out this edge case.
- **LOW**: The plan says "If needed, extend `data_sources/schema.py` or `common/schema.py` additively" — this is vague. A `ProjectionSummary` model (counts of matched, filtered, deduped, projected) will almost certainly be needed for Plan 02's manifest lineage. Better to state it now so the executor builds it.
- **LOW**: No mention of how dedupe keys are chosen. The legacy path dedupes by `(system, phase_name, composition)`. If the new projection uses a different key (e.g., `local_record_id`), the behavior diverges silently. The plan should lock this decision.

### Suggestions

- Add an explicit task or acceptance criterion for a `ProjectionSummary` dataclass that Plan 02 can consume for manifest lineage
- Specify the dedupe key explicitly: recommend `(system, phase_name, normalized_composition_tuple)` to match legacy behavior while remaining source-agnostic
- Add a test case for records with missing composition — either a skip-with-warning test or a derive-from-formula test
- Clarify the two public entrypoints: one that takes a list of `CanonicalRawSourceRecord` and a `SystemConfig` and returns `list[IngestRecord]`, and one convenience wrapper that loads from a staged snapshot path

### Risk Assessment: **LOW**

Well-scoped, clear deliverables, and the acceptance criteria are tight enough to prevent drift. The medium concerns are about edge cases the executor will likely handle but that should be specified rather than left to discretion.

---

## Plan 02: Wire The Source-Registry Bridge Into `mdisc ingest`

### Summary

This is the highest-stakes plan in the phase because it modifies the CLI entrypoint and the manifest contract. The three-task decomposition (bridge wiring, manifest lineage, integration tests) is sound. The plan correctly avoids forcing `SourceAdapter` through the `IngestBackend` protocol and instead branches in the CLI.

### Strengths

- Correctly branches on the reserved `source_registry_v1` key rather than adding a new CLI command — preserves the operator surface
- Manifest lineage is additive with an optional field — non-bridge stages and legacy manifests stay valid
- Explicit requirement that `SystemConfig.ingestion` must be present for the bridge path, with a test for the failure case when it's missing
- Tests use local fixtures or inline payloads — no network dependency
- Legacy test preservation is an explicit acceptance criterion

### Concerns

- **HIGH**: The plan modifies `ArtifactManifest` by adding an optional field, but `ArtifactManifest` is consumed by every stage's manifest (generate, screen, hifi-validate, hifi-rank, active-learn, report, pipeline). The plan says "keep non-ingest stages valid when the new field is absent" but doesn't specify how. If the field is `Optional[dict]` defaulting to `None`, this is trivial. If it's a nested model, Pydantic's JSON serialization behavior could change the manifest shape for all stages. The plan should lock the field type to `source_lineage: dict[str, Any] | None = None` or equivalent.
- **MEDIUM**: The plan says the bridge should "stage or reuse" source snapshots via `stage_registered_source_snapshot(...)`, but the reuse logic depends on `IngestionConfig.use_cached_snapshot`. The plan doesn't specify what "reuse" means concretely — does it check if the snapshot directory already exists and skip staging? The `stage_source_snapshot` function in `runtime.py` currently always stages. Either the runtime needs a cache-check wrapper, or the CLI branch needs to implement it. This is a meaningful code gap.
- **MEDIUM**: The `IngestSummary` model has `backend_adapter: str = "hypodx_fixture"` as a default. For source-registry runs, this needs to be `"source_registry_v1"`. The plan mentions this in the action text but doesn't call it out as a schema concern — the default value is HYPOD-X-flavored. No schema change needed, just awareness that the executor must set it explicitly.
- **LOW**: The plan lists `materials-discovery/src/materials_discovery/data_sources/runtime.py` in `files_modified` but the action text for task 1 says to use `stage_registered_source_snapshot(...)` as-is. If no runtime changes are needed, remove it from the modified list to avoid confusion. If cache-check logic is added, acknowledge it.

### Suggestions

- Lock the manifest lineage field shape: `source_lineage: dict[str, Any] | None = None` on `ArtifactManifest`, populated only for source-registry ingest
- Add an explicit subtask or note about snapshot reuse/caching: either delegate to the existing runtime (if it already supports it) or add a thin cache-check in the CLI branch that skips staging when the snapshot directory and manifest already exist
- Add a test that verifies a non-ingest manifest (e.g., from `mdisc generate`) still serializes correctly after the `ArtifactManifest` change — this guards against the HIGH concern above
- Consider adding a test that runs legacy ingest followed by source-registry ingest for the same system to verify the processed JSONL is overwritten cleanly

### Risk Assessment: **MEDIUM**

The CLI modification and manifest schema change carry real compatibility risk. The plan is well-designed but needs tighter specification on the manifest field type and snapshot reuse behavior to prevent the executor from making incompatible choices.

---

## Plan 03: Prove Pipeline Compatibility And No-DFT Guardrails

### Summary

Appropriate final wave that validates the whole pipeline rather than just the ingest seam. The three tasks (end-to-end smoke, downstream consumer tests, no-DFT guardrails) directly address `PIPE-01` and `OPS-03`. The no-DFT boundary enforcement via monkeypatching or import guards is a smart defensive measure.

### Strengths

- Directly addresses the research risk that "the bridge path passes ingest tests but breaks real-mode pipeline behavior"
- The no-DFT guard is an explicit test artifact, not just an implied assumption — this is good engineering discipline
- Tests are designed to stay offline and deterministic
- Extends existing test files (`test_hull_proxy.py`, `test_report.py`) rather than creating parallel test suites

### Concerns

- **MEDIUM**: The end-to-end real-mode pipeline smoke test (task 1) needs a source-backed config with `mode: real` plus `ingest_adapter: source_registry_v1`. But the existing real-mode pipeline test uses `al_cu_fe_real.yaml` which has `hypodx_pinned_v2026_03_09`. The plan says to add "at least one offline config path" but doesn't specify whether this is a new YAML file, a dynamically generated config in the test, or a parametrized variant. Given that the real-mode pipeline test already takes ~30-60 seconds per config, this matters for CI runtime.
- **MEDIUM**: The hull proxy test extension needs a processed JSONL with projected/enriched metadata to be on disk before the hull proxy runs. The plan says "bridge-backed reference-phase fixture or processed JSONL setup" but doesn't clarify whether this is a standalone fixture file committed to the repo or generated in-test. If generated in-test, the test becomes coupled to the projection module's internals. If committed, it needs to be maintained.
- **LOW**: The no-DFT guard via monkeypatching downstream adapters is fragile if someone adds a new adapter type in the future. A stronger approach would be to assert that the only imports from `hifi_digital/` or `backends/` in the bridge path are the registry constant check — but this may be over-engineering for a test.
- **LOW**: No mention of `test_ingest.py` (legacy determinism tests) in the verification pass. Plan 03 should confirm these still pass as a sanity check even though they're not being modified.

### Suggestions

- Specify the config strategy: recommend generating the source-registry config dynamically in the test (using `tmp_path` and a local fixture) rather than committing a new YAML file — this avoids fixture maintenance burden
- For the hull proxy test, generate the processed JSONL inline using the projection module from Plan 01 rather than committing a separate fixture — this keeps the test coupled to the actual projection behavior
- Add `test_ingest.py` to the final verification command even though it's not modified — it's the baseline determinism anchor
- Consider marking the source-backed pipeline smoke test with `@pytest.mark.integration` consistent with the existing `test_real_mode_pipeline.py` tests

### Risk Assessment: **LOW**

This is primarily a test-extension plan with no production code changes. The risks are about test design choices, not about breaking the system. The concerns are about maintainability, not correctness.

---

## Cross-Plan Assessment

### Dependency Ordering: Sound

Wave 1 (projection) -> Wave 2 (CLI bridge + manifest) -> Wave 3 (pipeline regression) is the correct order. Each wave's outputs are consumed by the next.

### Requirement Coverage

| Requirement | Plan 01 | Plan 02 | Plan 03 | Covered? |
|-------------|---------|---------|---------|----------|
| DATA-05 | Projection logic | Bridge wiring | Downstream proof | Yes |
| PIPE-01 | — | Legacy compat | Full pipeline smoke | Yes |
| OPS-03 | No-DFT in projection | No-DFT in bridge | Explicit guard tests | Yes |

### Gaps Across Plans

1. **Snapshot caching/reuse** — mentioned in the research and context but not concretely specified in any plan. Plan 02 should own this.
2. **Error messaging** — if a user configures `source_registry_v1` but the source adapter can't find the snapshot or the projection yields zero records, what does the CLI print? The error handling should match the existing pattern (stderr + exit code 2) but this isn't called out.
3. **Progress.md update** — per CLAUDE.md, every change to `materials-discovery/` must update `Progress.md`. None of the plans mention this. The executor should be reminded.
4. **`ProjectionSummary` handoff** — Plan 01 should produce this model; Plan 02 should consume it for manifest lineage. This dependency is implicit but should be explicit.

### Overall Phase Risk: **LOW-MEDIUM**

The plans are well-researched and well-decomposed. The main risk is in Plan 02's manifest schema change and snapshot reuse gap. If those two concerns are addressed in the plan text before execution, the phase should land cleanly.

---

## Consensus Summary

Both reviewers agree the phase is well-sequenced and architecturally strong.
They independently endorsed the decision to keep projection in a dedicated
`data_sources/projection.py` module, preserve `mdisc ingest` as the stable
operator entrypoint, and carry provenance additively rather than replacing the
processed reference-phase contract. Both also agreed the no-DFT guardrails and
offline test posture are important strengths of the plan.

### Agreed Strengths

- The wave ordering is correct: projection first, CLI bridge second, full
  pipeline compatibility last.
- The dedicated projection seam is the right abstraction boundary and prevents
  HYPOD-X coupling from leaking into multi-source integration.
- Additive provenance and manifest enrichment are the right compatibility
  strategy for the current pipeline.
- The plans explicitly respect the no-DFT boundary and keep tests offline and
  deterministic.

### Agreed Concerns

- **Plan 02 needs tighter specification around manifest lineage shape and
  snapshot reuse.**
  Both reviews point at the bridge/manifest step as the highest-risk part of
  the phase. The plan should lock the lineage field as optional/additive and
  make the snapshot reuse policy concrete rather than implied.
- **Plan 01 should be more explicit about projection edge cases and handoff
  artifacts.**
  The reviews highlight missing-composition handling, dedupe-key definition,
  and the likely need for a `ProjectionSummary` handoff to support Plan 02.
- **Test strategy should prefer thin or generated offline fixtures.**
  Both reviews warn against heavy committed fixtures or ambiguous setup. The
  plan should bias toward dynamically generated configs/processed inputs where
  that keeps maintenance and CI runtime under control.

### Divergent Views

- Gemini rated the overall phase risk as `LOW`, while Claude rated it
  `LOW-MEDIUM`, mainly because Claude put more weight on the compatibility risk
  of changing `ArtifactManifest` and the current gap around cached snapshot
  reuse.
- Gemini emphasized system-matching normalization and operator-friendly CLI
  feedback, while Claude focused more on plan precision: explicit dedupe keys,
  `ProjectionSummary`, error handling, and non-ingest manifest regression
  checks.

### Recommended Pre-Execution Adjustments

- Amend Plan 01 to lock:
  - how missing or incomplete composition is handled
  - the dedupe key for projected processed rows
  - a small `ProjectionSummary` handoff model for Plan 02
- Amend Plan 02 to lock:
  - the exact optional manifest lineage field shape
  - how `use_cached_snapshot` is honored
  - one regression check that non-ingest manifests still serialize unchanged
- Amend Plan 03 to lock:
  - whether source-backed config is generated in-test or committed
  - that legacy `test_ingest.py` remains in the final verification sweep
