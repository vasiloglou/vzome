---
phase: 32-cif-and-material-string-exporters
verified: 2026-04-07T03:42:29Z
status: passed
score: 4/4 must-haves verified
---

# Phase 32: CIF and Material-String Exporters Verification Report

**Phase Goal:** implement deterministic exporters that turn supported translated candidates into concrete payloads external materials LLMs can ingest.
**Verified:** 2026-04-07T03:42:29Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | The same translated candidate yields stable downstream text artifacts across repeated runs. | ✓ VERIFIED | `emit_translated_structure(...)` dispatches both built-in target families from one validated artifact in [translation_export.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/src/materials_discovery/llm/translation_export.py). Repeated-emission tests pass for both `cif` and `material_string` in [test_llm_translation_export.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_export.py) and [test_llm_translation_material_string.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_material_string.py). |
| 2 | CIF and material-string outputs preserve composition, cell, and site intent as far as the target format allows. | ✓ VERIFIED | CIF output uses a fixed cell-field order, fixed atom-loop headers, preserved site order, and parser compatibility checks in [test_llm_translation_cif.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_cif.py). Material-string output is a bare CrystalTextLLM-compatible body with ordered lengths, angles, species, and fractional coordinates in [translation_export.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/src/materials_discovery/llm/translation_export.py) and [test_llm_translation_material_string.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_material_string.py). |
| 3 | Exporters document when they are emitting a periodic proxy rather than a QC-native exact representation. | ✓ VERIFIED | CIF payloads include explicit fidelity/loss comment lines and QC-native lossy reasons in [translation_export.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/src/materials_discovery/llm/translation_export.py). Material-string exports keep the lossy semantics on `TranslatedStructureArtifact`, with tests asserting those reasons remain on the artifact contract while the raw body stays parser-compatible in [test_llm_translation_material_string.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_material_string.py) and [test_llm_translation_export_fixtures.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_export_fixtures.py). |
| 4 | External-format translation no longer depends on one-off notebooks or manual scripts. | ✓ VERIFIED | The repo now ships public export helpers (`emit_cif_text`, `emit_material_string_text`, `emit_translated_structure`, `validate_translated_structure_for_export`) from [__init__.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/src/materials_discovery/llm/__init__.py) and freezes outputs with checked-in golden files plus regression tests under [materials-discovery/tests/fixtures/llm_translation](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/fixtures/llm_translation). |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| [translation_export.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/src/materials_discovery/llm/translation_export.py) | Shared export seam plus deterministic CIF and material-string emitters | ✓ VERIFIED | Contains export validation, copy-not-mutate dispatch, fixed CIF serializer, and CrystalTextLLM-compatible material-string body formatter. |
| [__init__.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/src/materials_discovery/llm/__init__.py) | Public export surface for Phase 32 serializers | ✓ VERIFIED | Re-exports `emit_cif_text`, `emit_material_string_text`, `emit_translated_structure`, and `validate_translated_structure_for_export`. |
| [test_llm_translation_export.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_export.py) | Shared validation, dispatch, malformed-artifact, and cross-target identity coverage | ✓ VERIFIED | Covers byte stability, failure paths, shared artifact identity, legitimate lossy exports, and unsupported-family failures. |
| [test_llm_translation_cif.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_cif.py) | Deterministic CIF layout and parser compatibility coverage | ✓ VERIFIED | Covers fixed preamble/layout, checked-in golden parsing, stripped lossy parsing, and explicit lossy metadata. |
| [test_llm_translation_material_string.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_material_string.py) | Material-string layout and stability coverage | ✓ VERIFIED | Confirms CrystalTextLLM-compatible body layout, parser-style decoding, stable emission, and dispatched output. |
| [test_llm_translation_export_fixtures.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_export_fixtures.py) | Golden-output regression coverage across both fixtures and both targets | ✓ VERIFIED | Compares exact emitted bytes to all four checked-in golden outputs and asserts the lossy contract remains explicit. |
| [al_cu_fe_periodic_expected.cif](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/fixtures/llm_translation/al_cu_fe_periodic_expected.cif) | Exact periodic-safe CIF golden | ✓ VERIFIED | Checked in and matched by the golden regression suite. |
| [al_cu_fe_periodic_expected.material_string.txt](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/fixtures/llm_translation/al_cu_fe_periodic_expected.material_string.txt) | Exact periodic-safe material-string golden | ✓ VERIFIED | Checked in and matched by the golden regression suite. |
| [sc_zn_qc_expected.cif](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/fixtures/llm_translation/sc_zn_qc_expected.cif) | Lossy QC-native CIF golden | ✓ VERIFIED | Checked in, retains explicit fidelity/loss comments, and is parseable after comment stripping. |
| [sc_zn_qc_expected.material_string.txt](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/fixtures/llm_translation/sc_zn_qc_expected.material_string.txt) | Lossy QC-native material-string golden | ✓ VERIFIED | Checked in as the shipped bare CrystalTextLLM-compatible body and matched byte-for-byte by regression tests. |
| [Progress.md](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/Progress.md) | Required AGENTS progress tracking for all `materials-discovery/` edits | ✓ VERIFIED | Changelog rows and diary entries exist for all three Phase 32 plans and their RED/green slices. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| [translation.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/src/materials_discovery/llm/translation.py) | [translation_export.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/src/materials_discovery/llm/translation_export.py) | Exporters consume the normalized translated artifact rather than raw candidate state | ✓ WIRED | `emit_translated_structure(...)` and both concrete emitters accept `TranslatedStructureArtifact` directly. |
| [prototype_import.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/src/materials_discovery/generator/prototype_import.py) | [test_llm_translation_cif.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_cif.py) | Repo-local CIF parsing validates emitted payload compatibility | ✓ WIRED | `parse_cif(...)` is exercised against both the periodic golden and the stripped lossy QC payload. |
| [fixtures/llm_translation](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/fixtures/llm_translation) | [test_llm_translation_export_fixtures.py](/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/tests/test_llm_translation_export_fixtures.py) | Golden files freeze the exact shipped exporter bytes | ✓ WIRED | The fixture regression suite loads the Phase 31 candidate fixtures, emits both targets, and compares exact bytes to all four golden files. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Golden-output regression coverage | `cd materials-discovery && uv run pytest tests/test_llm_translation_export_fixtures.py -x -v` | `6 passed in 0.14s` | ✓ PASS |
| Parser/failure regression coverage | `cd materials-discovery && uv run pytest tests/test_llm_translation_cif.py tests/test_llm_translation_export.py tests/test_llm_translation_export_fixtures.py -x -v` | `28 passed in 0.16s` | ✓ PASS |
| Full Phase 32 validation slice and adjacent translation regressions | `cd materials-discovery && uv run pytest tests/test_llm_translation_export.py tests/test_llm_translation_cif.py tests/test_llm_translation_material_string.py tests/test_llm_translation_export_fixtures.py tests/test_llm_translation_schema.py tests/test_llm_translation_core.py tests/test_llm_translation_fixtures.py tests/test_structure_realization.py tests/test_llm_record2zomic.py tests/test_data_source_schema.py -x -v` | `68 passed` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| `LLM-28` | 32-01, 32-03 | Export supported translated candidates as CIF artifacts for CIF-oriented external materials LLM workflows without ad hoc notebook conversion. | ✓ SATISFIED | `emit_cif_text(...)` emits deterministic CIF text from `TranslatedStructureArtifact`; `test_llm_translation_cif.py` and golden fixture tests cover exact and lossy cases plus parser compatibility. |
| `LLM-29` | 32-02, 32-03 | Export at least one model-oriented crystal/material string encoding from the same translated candidate for CrystalTextLLM- or CSLLM-style downstream workflows. | ✓ SATISFIED | `emit_material_string_text(...)` emits a CrystalTextLLM-compatible body from the same translated artifact identity used by CIF; `test_llm_translation_material_string.py`, cross-target dispatch tests, and material-string goldens verify stable, parser-compatible output. |

Orphaned requirements: none. Phase 32 is mapped only to `LLM-28` and `LLM-29`, and both are covered by shipped code and verified tests.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| None | None | No blocking anti-patterns found in the shipped Phase 32 exporter surface | ℹ️ Info | The prior review tension around material-string headers was resolved in favor of an honest, parser-compatible contract. |

### Human Verification Required

None. Phase 32 ships deterministic serializers, regression fixtures, and parser-backed coverage; no manual-only behavior remains to validate before Phase 33 CLI integration.

### Gaps Summary

None. Phase 32 achieved the roadmap goal:

- supported translated candidates now emit deterministic CIF artifacts
- the same translated candidates emit a stable material-string encoding through the same export seam
- lossy periodic-proxy posture remains explicit in the shipped contract
- exporter behavior is frozen with golden files and parser/failure regressions instead of notebook-only assumptions

---

_Verified: 2026-04-07T03:42:29Z_
_Verifier: Codex (manual fallback after stalled verifier agent)_
