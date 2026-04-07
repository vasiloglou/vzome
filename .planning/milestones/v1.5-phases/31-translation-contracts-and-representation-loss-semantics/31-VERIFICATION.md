---
phase: 31-translation-contracts-and-representation-loss-semantics
verified: 2026-04-07T00:11:32Z
status: passed
score: 4/4 must-haves verified
---

# Phase 31: Translation Contracts and Representation Loss Semantics Verification Report

**Phase Goal:** define the supported downstream representation targets and the typed contract that explains when a Zomic candidate can be translated exactly, approximately, or only lossily.
**Verified:** 2026-04-07T00:11:32Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | A translated candidate has one auditable source of truth tying the export back to the original Zomic/candidate artifact. | ✓ VERIFIED | `TranslatedStructureArtifact.source` requires typed candidate linkage and provenance hints in `llm/schema.py`; `prepare_translated_structure()` populates those fields directly from `CandidateRecord` in `llm/translation.py`; schema tests reject blank candidate linkage and fixture/core tests assert preserved source IDs. |
| 2 | Exact versus lossy translation is encoded in the artifact contract rather than implied by docs alone. | ✓ VERIFIED | `TranslationFidelityTier` defines `exact`, `anchored`, `approximate`, `lossy`; `TranslatedStructureArtifact` enforces `loss_reasons` for lossy artifacts; `assess_translation_fidelity()` and `_build_fidelity_assessment()` classify exact/anchored/approximate/lossy in code; schema/core/fixture tests cover all tiers. |
| 3 | Unsupported target exports fail clearly before operators confuse them for native QC-safe structure representations. | ✓ VERIFIED | `resolve_translation_target()` raises `KeyError` for unknown families; `assess_translation_fidelity(..., requested_fidelity="exact")` raises `ValueError` on unsupported exactness claims; schema/core tests and direct runtime spot-checks confirm both failure paths. |
| 4 | The contract stays additive to the existing Zomic-first workflow instead of replacing it. | ✓ VERIFIED | Existing `FidelityTier` remains unchanged with `heuristic`; translation APIs are additive exports in `materials_discovery.llm`; translation starts from `CandidateRecord` and docs explicitly keep compiled Zomic candidates as source of truth. Existing adjacent tests (`test_llm_record2zomic.py`, `test_data_source_schema.py`) still pass in the full verification run. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/schema.py` | Typed translation contract, fidelity semantics, target registry | ✓ VERIFIED | Artifact verifier passed; contains source reference, target descriptor, artifact model, loss validation, built-in target registry, and registry resolution helpers. |
| `materials-discovery/src/materials_discovery/llm/__init__.py` | Public translation exports without breaking existing imports | ✓ VERIFIED | Artifact verifier passed; translation schema and runtime helpers are re-exported and existing LLM imports remain intact. |
| `materials-discovery/src/materials_discovery/llm/translation.py` | Deterministic candidate-to-artifact normalization and fidelity classification | ✓ VERIFIED | Artifact verifier passed; module produces normalized artifacts, explicit coordinate-source diagnostics, and fidelity/loss classification from repo-local evidence. |
| `materials-discovery/src/materials_discovery/backends/structure_realization.py` | Shared coordinate realization/origin helpers reused by translation | ✓ VERIFIED | Artifact verifier passed; per-site coordinate source helper is implemented and reused by translation instead of duplicating conversion logic. |
| `materials-discovery/tests/fixtures/llm_translation/al_cu_fe_periodic_candidate.json` | Periodic-safe fixture for exact/anchored boundary | ✓ VERIFIED | Artifact verifier passed; fixture has stored fractional coordinates and periodic-safe provenance used by fixture regression tests. |
| `materials-discovery/tests/fixtures/llm_translation/sc_zn_qc_candidate.json` | QC-native fixture for lossy boundary | ✓ VERIFIED | Artifact verifier passed; fixture is qphi-only with QC-native provenance and is asserted lossy across both target families. |
| `materials-discovery/developers-docs/llm-translation-contract.md` | Developer handoff documenting targets and fidelity semantics | ✓ VERIFIED | Artifact verifier passed; note documents source-of-truth boundary, built-in targets, all four fidelity states, fixture boundary, and Phase 32 serializer handoff. |
| `materials-discovery/Progress.md` | AGENTS/CLAUDE progress tracking for all `materials-discovery/` edits | ✓ VERIFIED | Changelog rows and diary entries exist for Phase 31 Plan 01-03 work, satisfying repo progress-tracking policy. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/common/schema.py` | `materials-discovery/src/materials_discovery/llm/schema.py` | Source-of-truth candidate contract feeds translation schema | ✓ WIRED | Plan verifier passed; translation source model matches `CandidateRecord`/site/provenance fields. |
| `materials-discovery/src/materials_discovery/data_sources/schema.py` | `materials-discovery/src/materials_discovery/llm/schema.py` | Typed representation inventory precedent informs target registry | ✓ WIRED | Plan verifier passed; schema reuses the same typed-inventory pattern. |
| `materials-discovery/src/materials_discovery/backends/structure_realization.py` | `materials-discovery/src/materials_discovery/llm/translation.py` | Translation reuses shipped structure realization logic | ✓ WIRED | Plan verifier passed; translation imports `candidate_fractional_positions_with_sources()` and `candidate_cartesian_positions()`. |
| `materials-discovery/src/materials_discovery/common/schema.py` | `materials-discovery/src/materials_discovery/llm/translation.py` | Candidate site/qphi/fractional/cartesian/template data drives fidelity and diagnostics | ✓ WIRED | Plan verifier passed; translation consumes `CandidateRecord` plus site/provenance/template-family evidence. |
| `materials-discovery/tests/fixtures/llm_translation/` | `materials-discovery/src/materials_discovery/llm/translation.py` | Repo fixtures freeze periodic-safe and lossy expectations | ✓ WIRED | Manual verification: `test_llm_translation_fixtures.py` loads fixture JSON files into `CandidateRecord`, resolves targets, and calls `prepare_translated_structure()` / `assess_translation_fidelity()` across both targets. |
| `materials-discovery/developers-docs/llm-translation-contract.md` | `materials-discovery/developers-docs/llm-integration.md` | Contract doc inherits Zomic-first/QC-native boundary | ✓ WIRED | Plan verifier passed; doc explicitly states compiled Zomic candidates remain the source of truth and downstream exports are additive. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/translation.py` | `TranslatedStructureArtifact.source/cell/sites/fidelity_tier` | `CandidateRecord` input plus `candidate_fractional_positions_with_sources()` and `candidate_cartesian_positions()` from structure realization | Yes | ✓ FLOWING |
| `materials-discovery/tests/test_llm_translation_fixtures.py` | Fixture-backed translation outputs | Repo JSON fixtures loaded with `CandidateRecord.model_validate(...)` and passed into `prepare_translated_structure()` / `assess_translation_fidelity()` | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Built-in target registry exposes supported downstream targets | `cd materials-discovery && uv run python -c "from materials_discovery.llm import list_translation_targets; print([(t.family, t.target_format, t.requires_periodic_cell, t.preserves_qc_native_semantics) for t in list_translation_targets()])"` | `[('cif', 'cif_text', True, False), ('material_string', 'crystaltextllm_material_string', True, False)]` | ✓ PASS |
| Periodic fixture produces exact translated artifact tied to source candidate | `cd materials-discovery && uv run python -c "...prepare_translated_structure(periodic_fixture, cif_target)..."` | `exact [] 3 al_cu_fe_fixture_periodic_001` | ✓ PASS |
| QC-native fixture produces explicit lossy artifact with diagnostics | `cd materials-discovery && uv run python -c "...prepare_translated_structure(qc_fixture, cif_target)..."` | `lossy ['aperiodic_to_periodic_proxy', 'coordinate_derivation_required', 'qc_semantics_dropped'] ['coordinate_derivation_required', 'periodic_proxy_required', 'qc_semantics_dropped']` | ✓ PASS |
| Unknown target lookup fails clearly | `cd materials-discovery && uv run python - <<'PY' ... resolve_translation_target('imaginary') ... PY` | `KeyError 'unknown translation target family: imaginary'` | ✓ PASS |
| Full automated regression slice for Phase 31 and adjacent additive contracts | `cd materials-discovery && uv run pytest tests/test_llm_translation_schema.py tests/test_llm_translation_core.py tests/test_llm_translation_fixtures.py tests/test_structure_realization.py tests/test_llm_record2zomic.py tests/test_data_source_schema.py -x -v` | `36 passed in 0.17s` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| `LLM-27` | 31-01, 31-02, 31-03 | Translate a compiled Zomic candidate into a deterministic structure-interoperability artifact with explicit cell, species, positions, provenance, and representation metadata reusable by downstream crystal/material workflows. | ✓ SATISFIED | `TranslatedStructureArtifact` and `TranslatedStructureSite` define the additive artifact contract; `prepare_translated_structure()` deterministically populates source, cell, composition, sites, and target metadata; fixture/core tests verify deterministic normalized output and source linkage. |
| `LLM-30` | 31-01, 31-02, 31-03 | Record whether a translation artifact is exact, anchored, approximate, or lossy relative to the source Zomic candidate, plus the reason when exact preservation is impossible. | ✓ SATISFIED | `TranslationFidelityTier` and `TranslationLossReason` define the typed contract; artifact validation requires loss reasons for lossy outputs; fidelity classification and lossy diagnostics are implemented in `translation.py`; schema/core/fixture tests and runtime spot-checks verify exact and lossy boundaries plus explicit failure modes. |

Orphaned requirements: none. `REQUIREMENTS.md` maps only `LLM-27` and `LLM-30` to Phase 31, and both are covered by the implemented artifacts and tests.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| None | None | No blocking or warning anti-patterns found in modified Phase 31 files | ℹ️ Info | Grep hits were benign empty-list/dict initializers and empty-collection assertions in tests, not production stubs or hollow wiring. |

### Human Verification Required

None. This phase delivers typed contracts, deterministic normalization/classification logic, fixtures, and developer docs; the implemented goal is fully programmatically verifiable and the validation plan already marked manual-only verification as unnecessary.

### Gaps Summary

None. Phase 31 achieved the roadmap goal:

- supported downstream target families are defined and registry-backed
- the translation contract encodes exact, anchored, approximate, and lossy semantics in code
- unsupported target/export claims fail clearly
- the bridge remains additive to the existing Zomic-first workflow

---

_Verified: 2026-04-07T00:11:32Z_
_Verifier: Claude (gsd-verifier)_
