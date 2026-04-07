---
phase: 31
reviewers: [gemini, claude]
reviewed_at: 2026-04-06T15:58:29Z
plans_reviewed:
  - .planning/phases/31-translation-contracts-and-representation-loss-semantics/31-01-PLAN.md
  - .planning/phases/31-translation-contracts-and-representation-loss-semantics/31-02-PLAN.md
  - .planning/phases/31-translation-contracts-and-representation-loss-semantics/31-03-PLAN.md
---

# Cross-AI Plan Review — Phase 31

## Gemini Review

# Phase 31 Plan Review: Translation Contracts and Representation Loss Semantics

## 1. Summary
The implementation plans for Phase 31 provide a robust, additive framework for bridging Zomic-native candidates into external materials-LLM representations. By separating the **contract definition** (Plan 01), **normalization logic** (Plan 02), and **fixture-backed validation** (Plan 03), the strategy ensures that downstream interoperability does not compromise the "source-of-truth" authority of Zomic. The emphasis on "representational honesty" through a dedicated `lossy` fidelity tier and explicit loss reasons is a standout feature that directly addresses the geometric incompatibility between quasicrystals and periodic CIF-based formats.

## 2. Strengths
*   **Decoupled Schema and Logic:** Placing the contract in `llm/schema.py` and the normalization in `llm/translation.py` maintains clear architectural boundaries consistent with the existing codebase.
*   **Honest Fidelity Modeling:** The decision to create a new `TranslationFidelityTier` instead of overloading the existing `FidelityTier` prevents semantic pollution and correctly identifies `lossy` as a critical state for QC-to-CIF translations.
*   **Leverage of Existing Backends:** Reusing `structure_realization.py` for coordinate conversion ensures consistency and avoids "reinventing the wheel" for site-position derivation.
*   **Fixture-Driven Freezing:** Plan 03's focus on anchoring the contract with real `CandidateRecord` fixtures (both periodic-safe and QC-native) provides a concrete handoff for Phase 32 exporters.
*   **Deterministic Traceability:** The requirement to record coordinate-origin diagnostics (e.g., whether sites came from stored fractional data or qphi-derived fallbacks) is essential for auditable research.

## 3. Concerns
*   **Classification Complexity (MEDIUM):** In Plan 02, Task 2, determining "exact" versus "lossy" based on "repo-local evidence" might be tricky if a `CandidateRecord` lacks an explicit `is_periodic` flag. 
    *   *Mitigation:* The plan mentions using `template_family` as a hint, which should be the primary heuristic.
*   **Optional Dependency Fragility (LOW):** While the plans mention isolating heavy dependencies (`ase`, `pymatgen`), the normalization seam must be careful not to trigger these imports during basic artifact generation if only coordinate math is needed.
*   **Registry Extensibility (LOW):** Plan 01 hardcodes the target registry. While fine for an MVP, the implementation should ensure that adding a new target (e.g., a new variant of CSLLM strings) doesn't require a fundamental schema redesign.

## 4. Suggestions
*   **Explicit Periodicity Hint:** In `TranslationTargetDescriptor`, consider adding a boolean `requires_periodic_cell` property to make the target requirements even more explicit for the classification logic.
*   **Loss Reason Standardization:** In the `TranslatedStructureArtifact`, provide a set of standard `LossReason` constants (e.g., `APERIODIC_TO_PERIODIC_PROXY`, `QPHI_PRECISION_LOSS`) to ensure consistency across different candidate types.
*   **Coordinate Precision Warning:** Add a diagnostic field specifically for "precision drift" when converting from Golden Field $Z[\phi]$ to floating-point cartesian/fractional coordinates, even if the result is nominally "exact."

## 5. Risk Assessment
**Overall Risk Level: LOW**

**Justification:**
The phase is strictly additive and does not mutate existing generation or evaluation pathways. The technical complexity is managed by reusing the stable `structure_realization` logic. The primary challenge is conceptual (defining the boundaries of representational loss), which the plans handle by forcing explicit developer documentation and fixture-backed regression tests. The dependency on `CandidateRecord` as the input ensures that the translation bridge is grounded in compiled, validated geometry rather than raw text.

---

## Claude Review

# Phase 31 Plan Review: Translation Contracts and Representation Loss Semantics

---

## Plan 31-01: Schema, Fidelity Contract, and Target Registry

### Summary

Plan 01 is a well-scoped schema-first wave that defines the typed translation contract before any normalization or serialization logic lands. It correctly identifies the need for a separate `TranslationFidelityTier` (with `lossy`) distinct from the existing corpus `FidelityTier` (which uses `heuristic`), and it sets up a target-family registry so downstream exporters inherit stable names. The two-task split — artifact contract first, then registry — is clean and appropriately sized for a single wave.

### Strengths

- **Correct fidelity separation.** The existing `FidelityTier = Literal["exact", "anchored", "approximate", "heuristic"]` at `schema.py:20` serves corpus conversion, not export loss. Creating a parallel translation-specific enum avoids semantic overloading and breaking existing imports.
- **Explicit must_haves truths.** The five invariants are well-chosen guard rails, especially "must not replace Zomic or alter shipped behavior" and "do not overload the older corpus FidelityTier."
- **Key_links are accurate.** The declared dependency from `CandidateRecord` and `StructureRepresentation` to the new schema models matches the actual code surface I verified.
- **TDD behavior specs are specific.** Five concrete test behaviors for Task 1 and four for Task 2 give the executor clear pass/fail targets rather than vague "it should work" instructions.
- **Additive-only design.** The plan is explicit that no existing imports or models are modified — only new types are added to the 2,344-line `schema.py` and re-exported from `__init__.py`.

### Concerns

- **MEDIUM — `schema.py` is already 2,344 lines.** Adding 5+ new models (TranslationFidelityTier, TranslationTargetFamily, TranslationTargetDescriptor, TranslatedStructureArtifact, TranslatedStructureDiagnostic) to an already-large file continues a growth pattern that will eventually become unwieldy. This isn't a blocker for Phase 31, but it's worth noting for future refactoring decisions.

- **LOW — Registry design is underspecified at the persistence level.** Task 2 says "built-in translation target registry" but doesn't clarify whether this is a module-level dict, a class with a lookup method, or a set of typed constants. The executor has freedom, which is usually fine, but if Plan 02 assumes a specific lookup API (e.g., `get_target_descriptor("cif")`), any mismatch could cause rework. The `must_haves.artifacts` section lists `TranslationTargetFamily` and `TranslationTargetDescriptor` as the exports, which constrains the shape enough to be workable.

- **LOW — Missing negative test for artifact creation without source linkage.** Task 1's behavior tests cover lossy-reason validation and additive compatibility, but don't explicitly test that an artifact *without* a source candidate ID is rejected. The acceptance criteria mention "typed source linkage" but no test behavior explicitly covers the rejection path for missing provenance.

- **LOW — No explicit test for TranslatedStructureDiagnostic in isolation.** The diagnostic model is listed as an export but doesn't appear in any behavior spec. It's presumably tested through the artifact that contains it, but a standalone validation test would strengthen the contract.

### Suggestions

- Add a behavior spec: "Test 6: a translated artifact without a source candidate ID is rejected at construction time" to Task 1. This directly anchors the "auditable source reference" requirement (LLM-27).
- Consider whether the registry lookup function should be specified as a must_have export (e.g., `resolve_translation_target`) so Plan 02 can depend on a stable API name rather than discovering it at execution time.
- The `__init__.py` exports list in `must_haves.artifacts` only includes 3 of the 5 new types. Confirm whether `TranslationTargetFamily` and `TranslatedStructureDiagnostic` are intentionally kept internal or whether this is an omission.

### Risk Assessment

**LOW.** This is a clean additive schema wave with no runtime behavioral changes to existing workflows. The main risk is an oversized file, which is a maintenance concern rather than a correctness risk. The TDD approach with focused test behaviors makes regression unlikely.

---

## Plan 31-02: Deterministic Normalization and Fidelity Classification

### Summary

Plan 02 introduces the runtime translation logic: a normalization seam that turns a compiled `CandidateRecord` into a `TranslatedStructureArtifact`, plus fidelity classification that decides exact vs. lossy outcomes. It correctly reuses the existing `structure_realization.py` coordinate pipeline rather than duplicating it, and it places the new logic in a dedicated `translation.py` module. The two-task split — normalization first, then fidelity classification — follows a natural dependency chain.

### Strengths

- **Correct reuse boundary.** The plan explicitly requires reusing `candidate_fractional_positions`, `candidate_cartesian_positions`, and `candidate_cell_matrix` from `structure_realization.py` rather than re-implementing coordinate conversion. This matches the existing code at `structure_realization.py:15-48`.
- **Coordinate-origin tracking fills a real gap.** The research correctly identifies that no coordinate-origin tracking exists in the current codebase (`coordinates.py` has no origin metadata). The plan addresses this by recording which source was used per site (stored fractional → stored cartesian → qphi fallback), which is essential for honest fidelity classification.
- **Determinism is explicitly tested.** Behavior specs include "repeated normalization yields byte-stable model output" and "deterministic site ordering across repeated runs" — these are exactly the properties Phase 32 serializers need.
- **Honest fidelity design.** Task 2's classification logic correctly uses the priority chain: stored fractional positions indicate periodic-safe data, qphi-only candidates indicate QC-native geometry that requires lossy marking for CIF targets. This directly implements the conceptual boundary from `llm-quasicrystal-landscape.md`.
- **Existing test regression guard.** Both tasks include `test_structure_realization.py` in the verification command, ensuring the additive helpers don't break shipped behavior.

### Concerns

- **MEDIUM — The coordinate-origin inference heuristic needs more specification.** The plan says "records which source was used" but the actual decision tree is non-trivial. Looking at `structure_realization.py:15-29`, the function already implements a priority chain (fractional → cartesian-to-fractional → qphi fallback), but it doesn't expose *which* branch was taken. The plan says "extend structure-realization helpers only if needed" but doesn't specify whether this means adding a parallel `candidate_coordinate_origins()` function or modifying return values. The executor will need to make an architectural choice here, and the wrong one could either bloat the realization module or miss the origin data entirely.

- **MEDIUM — Fidelity classification relies on `template_family` naming heuristics.** The research notes say "prefer explicit source classification when provenance makes it available and only use deterministic fallbacks such as `template_family` naming." But looking at `CandidateRecord`, `template_family` is a free-form string (e.g., `"icosahedral_approximant_1_1"` in the test fixture). The plan doesn't specify which template_family patterns map to periodic-safe vs. QC-native. If this heuristic is wrong or incomplete, fidelity classification silently produces incorrect results. Task 2's behavior tests cover the *outcomes* but not the *classification inputs*.

- **LOW — No test for mixed-origin candidates.** Real candidates could have some sites with stored fractional positions and others with only qphi coordinates. The behavior specs test the priority chain but don't explicitly cover the mixed case where coordinate origin varies *within* a single candidate. This matters because the fidelity classification needs to decide: is a candidate with 90% stored-fractional and 10% qphi-fallback sites "anchored" or "lossy"?

- **LOW — `assess_translation_fidelity` and `infer_coordinate_sources` ordering.** Both functions are listed as exports from `translation.py`, but the plan doesn't specify whether `assess_translation_fidelity` calls `infer_coordinate_sources` internally or whether the caller must chain them. This affects the API contract Plan 03 fixtures will test against.

### Suggestions

- Add a brief specification for the coordinate-origin inference API shape. Something like: "Add a `candidate_coordinate_origins(candidate) -> list[Literal['fractional', 'cartesian', 'qphi']]` helper to `structure_realization.py` that returns the per-site source used, parallel to `candidate_fractional_positions`." This prevents architectural ambiguity at execution time.
- Add a behavior spec for Task 2: "Test 5: a candidate with mixed coordinate origins (some stored fractional, some qphi-only) classifies no higher than anchored for periodic targets." This closes the mixed-origin gap.
- Document in the plan which `template_family` patterns are treated as periodic-safe vs. QC-native, or specify that the classifier should be conservative (default to lossy unless positive evidence of periodicity exists). The current plan leaves this to the executor, which is fine for flexibility but risks inconsistency with later phases.

### Risk Assessment

**LOW-MEDIUM.** The normalization seam is well-grounded in existing code, but the fidelity classification heuristic has enough ambiguity that the executor could make decisions that later conflict with Phase 32 serializer expectations. The coordinate-origin tracking fills a genuine gap and is the right architectural choice. The main risk is that under-specified classification rules produce results that fixtures in Plan 03 then lock in, making corrections expensive later.

---

## Plan 31-03: Fixtures, Regression Anchors, and Developer Docs

### Summary

Plan 03 freezes the Phase 31 contract with real fixture files and a developer-facing translation note. It creates two fixture candidates (periodic-safe Al-Cu-Fe and QC-native Sc-Zn), adds regression tests against them, and writes a handoff document for Phase 32 implementers. This is the right wave to land last because it depends on both the schema (Plan 01) and the normalization logic (Plan 02).

### Strengths

- **Fixture-backed regression is the right anchor.** The existing test fixtures (`cod_sample.cif`, `hypodx_approximant_sample.cif`, `pyqcstrc_projection_sample.json`) set a good precedent. Adding `llm_translation/` as a subdirectory with explicit candidate JSON fixtures gives Phase 32 a stable starting point.
- **Two-class coverage is sufficient.** One periodic-safe and one QC-native/lossy candidate covers the essential fidelity boundary. The behavior specs require that the QC-native fixture "cannot silently claim exact periodic export," which directly tests the Phase 31 success criterion #2.
- **Developer doc scope is appropriately limited.** The plan correctly scopes the doc to implementer guidance (what the contract means, what Phase 32 should serialize) and defers operator/runbook docs to Phase 33.
- **Must_haves truths are well-calibrated.** "Phase 31 doc is an implementer contract" and "fixture coverage needs both periodic-safe and QC-native/lossy" prevent scope creep in both directions.

### Concerns

- **MEDIUM — Fixture realism depends on Plan 02 implementation details.** The fixture JSON files must be valid `CandidateRecord` instances that exercise specific fidelity classification paths. But Plan 03 doesn't specify what makes a candidate "QC-native" versus "periodic-safe" at the data level. If Plan 02 uses `template_family` heuristics, the fixture's `template_family` value must trigger the right path. If Plan 02 uses coordinate-origin evidence, the fixture's site data must have the right qphi/fractional/cartesian mix. This coupling is implicit rather than documented.

- **MEDIUM — No fixture for the "approximate" fidelity tier.** The plan covers exact/anchored (periodic-safe) and lossy (QC-native) but doesn't mention a fixture that exercises the intermediate "approximate" state. If "approximate" is a valid classification in Plan 02, the regression suite should anchor it too. Otherwise, the middle tier exists in the enum but has no fixture-backed proof that it works.

- **LOW — Developer doc verification is grep-based.** The verify command (`rg -n "exact|anchored|approximate|lossy|QC-native|source of truth"`) only checks that keywords appear in the document, not that the document is structurally complete or accurate. This is acceptable for a non-code artifact, but it means the doc could technically pass verification while being incomplete.

- **LOW — No explicit fixture for unsupported target family failure.** Plan 01 Task 2 tests that unknown target families fail, but the Plan 03 fixture suite doesn't include a regression anchor for that failure path. This is a minor gap since the schema tests cover it, but fixture-backed failure coverage would be stronger.

### Suggestions

- Add a note in the fixture task specifying *which* data properties distinguish the periodic-safe fixture from the QC-native fixture (e.g., "the periodic fixture has stored `fractional_position` on all sites; the QC-native fixture has only `qphi` coordinates and no stored fractional/cartesian positions"). This makes the fixture design deterministic rather than dependent on executor interpretation.
- Consider adding a third fixture or a test variation that exercises the "approximate" fidelity tier, or explicitly document that "approximate" is not exercised in Phase 31 fixtures and will be covered when Phase 32 adds serializer-specific approximation logic.
- The developer doc task's `read_first` includes `llm-integration.md` and `llm-quasicrystal-landscape.md` — good. Consider also including the Plan 01 schema exports list so the doc references the exact type names the contract defines.

### Risk Assessment

**LOW.** This is a stabilization wave with no runtime behavioral changes. The main risk is that fixtures lock in fidelity classification behavior from Plan 02 that later turns out to be wrong, but that's the intended function of regression tests — they make unintentional changes visible. The developer doc is a helpful handoff artifact with minimal risk.

---

## Cross-Plan Assessment

### Dependency Chain

```
Plan 01 (schema + registry) → Plan 02 (normalization + classification) → Plan 03 (fixtures + docs)
```

The wave ordering is correct. Plan 02 depends on Plan 01's exported types. Plan 03 depends on both for fixture validation.

### Requirement Coverage

| Requirement | Plan 01 | Plan 02 | Plan 03 | Coverage |
|-------------|---------|---------|---------|----------|
| LLM-27 (deterministic interop artifact) | Schema contract | Normalization logic | Fixture proof | Full |
| LLM-30 (fidelity metadata) | Fidelity enum + loss reason | Classification logic | Regression anchors | Full |

Both Phase 31 requirements are addressed across all three plans. LLM-28 and LLM-29 (CIF and material-string export) are correctly deferred to Phase 32.

### Cross-Plan Risks

- **MEDIUM — Implicit API contract between plans.** Plan 01 defines types; Plan 02 produces instances; Plan 03 freezes expectations. But the API surface connecting them (function signatures, return types, lookup patterns) is specified through `must_haves.artifacts.exports` rather than through explicit interface contracts. The executor of Plan 02 must reverse-engineer the intended API from Plan 01's type definitions. This is workable because TDD behavior specs constrain the shape, but it leaves room for friction.

- **LOW — No full-suite regression gate between waves.** Each plan runs its own test file, but there's no explicit gate that runs *all* Phase 31 tests between waves. The validation strategy specifies this ("after every plan wave, run full suite"), but the individual plans' `verify` commands only run their own files. An executor following just the plan could miss cross-wave regressions.

- **LOW — `__init__.py` is modified in both Plan 01 and Plan 02.** Both plans list `materials-discovery/src/materials_discovery/llm/__init__.py` as a modified file. Since they're in different waves, there's no conflict, but Plan 02's executor must add to Plan 01's exports rather than replacing them. The `must_haves.artifacts` sections for each plan list different exports, which makes the intent clear.

### Overall Risk Assessment

**LOW.** The three-plan structure is well-sequenced with clear scope boundaries. The plans are grounded in actual codebase structures (verified against the 2,344-line schema file, existing coordinate pipeline, and fixture directory). The main risks are around under-specification of fidelity classification heuristics in Plan 02 and implicit coupling between fixture data shapes and classification logic in Plan 03. Neither risk is likely to cause phase failure — they're more likely to produce a first-pass implementation that needs minor adjustment during Plan 03 fixture anchoring, which is exactly what fixture-backed regression is designed to catch.

**Recommendation: Approve for execution.** The two MEDIUM concerns (coordinate-origin API shape and fixture-to-classifier coupling) are worth noting for the executor but don't warrant plan revision.

---

## Consensus Summary

Both reviewers agreed that the overall plan structure is strong: contract first,
normalization second, fixture-backed freeze third. They also agreed that the
new translation layer is appropriately additive, that `TranslationFidelityTier`
should stay separate from the older corpus `FidelityTier`, and that reusing
`structure_realization.py` is the right technical seam.

### Agreed Strengths

- The three-wave split is well sequenced and keeps Phase 31 focused on contract
  and semantics rather than premature serializer work.
- The dedicated export-facing fidelity model with explicit `lossy` semantics is
  the right way to keep QC-native Zomic authoritative while still supporting
  external materials-LLM formats.
- Reusing the existing structure-realization pipeline avoids duplicating
  coordinate conversion logic and keeps the bridge grounded in compiled
  candidates.
- Anchoring the contract with fixture-backed periodic-safe and QC-native cases
  gives Phase 32 a stable handoff surface.

### Agreed Concerns

- The periodic-safe versus QC-native classification rules in Plan 02 need a
  more explicit contract. Right now the plans leave too much room for implicit
  `template_family` or provenance heuristics.
- The coordinate-origin API shape should be pinned down more clearly before
  execution. Both reviews point to the need for an explicit seam that records
  whether site positions came from stored fractional data, stored cartesian
  data, or qphi-derived fallback.
- The fixture design in Plan 03 should spell out what makes a candidate
  periodic-safe versus lossy so the regression suite does not accidentally bake
  in ambiguous classifier behavior.

### Divergent Views

- Gemini saw the phase as overall `LOW` risk with mostly conceptual ambiguity,
  while Claude rated the classification area as `LOW-MEDIUM` because the
  coordinate-origin and periodicity heuristics are still under-specified.
- Claude raised additional maintainability concerns about continuing to grow
  `materials_discovery/llm/schema.py`, while Gemini did not consider file size a
  meaningful near-term risk.
- Gemini suggested standardizing loss reasons and precision-drift diagnostics,
  while Claude focused more on explicit API names, mixed-origin test cases, and
  fixture realism.
