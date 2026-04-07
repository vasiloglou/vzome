# Phase 31 Research

## Existing Code Surface

- `materials-discovery/src/materials_discovery/common/schema.py` already gives
  compiled candidates a stable source contract through `CandidateRecord`,
  including explicit `cell`, `sites`, `composition`, and `provenance`.
- `materials-discovery/src/materials_discovery/backends/structure_realization.py`
  already normalizes coordinates from the compiled candidate into fractional,
  cartesian, ASE, and pymatgen forms. That is the right bridge seam for external
  materials-LLM interop because it starts from the post-compile artifact rather
  than reparsing Zomic.
- `materials-discovery/src/materials_discovery/llm/converters/record2zomic.py`
  already records deterministic conversion traces and fidelity reasoning when a
  structured candidate is projected into Zomic. Phase 31 should reuse that
  mindset, but it cannot reuse the exact same fidelity enum because the export
  milestone needs an explicit `lossy` state.
- `materials-discovery/src/materials_discovery/data_sources/schema.py` already
  has additive `StructureRepresentation` metadata (`representation_kind`,
  `payload_format`, `payload_path`, `content_hash`). That gives the repo a
  precedent for typed representation inventories instead of ad hoc filenames.
- The docs already lock the conceptual boundary:
  `materials-discovery/developers-docs/llm-integration.md` and
  `materials-discovery/developers-docs/llm-quasicrystal-landscape.md` both say
  CIF-oriented crystal LLMs are useful, but CIF is not a faithful native
  representation for true quasicrystal geometry. Phase 31 must preserve that
  distinction in code, not only in prose.

## Phase 31 Contract Decisions

- **Source of truth:** the translation layer should start from a compiled
  `CandidateRecord`, not from raw Zomic text and not from notebook-only
  scratch state.
- **Separate export fidelity:** the existing LLM corpus `FidelityTier` is
  `exact|anchored|approximate|heuristic`. Phase 31 needs a separate
  export-facing tier that includes `lossy` because the milestone requirement is
  about downstream representational loss relative to the source Zomic candidate,
  not about corpus-conversion heuristics.
- **Typed target registry:** target family and target format must be typed.
  Phase 31 should register CIF and at least one material-string family in a
  single contract so later CLI/export code cannot invent names opportunistically.
- **Normalized bridge artifact first:** Phase 31 should produce a typed
  translated-structure artifact that captures:
  - source-candidate identity and provenance linkage
  - target family and format intent
  - normalized cell/species/site payload
  - coordinate derivation diagnostics
  - exact/anchored/approximate/lossy status plus reason
  - warnings for dropped QC-native semantics
- **Serializer boundary:** Phase 31 stops at the normalized artifact and its
  loss semantics. Concrete CIF text and CrystalTextLLM/CSLLM-oriented string
  serializers belong to Phase 32.

## Risks To Design Around

- The repo does not yet appear to carry a first-class field that declares
  whether a compiled candidate is a periodic approximant or a QC-native
  structure. Phase 31 should therefore prefer explicit source classification
  when provenance makes it available and only use deterministic fallbacks such
  as `template_family` naming or coordinate-derivation evidence when the source
  metadata is silent.
- Optional heavy dependencies (`pymatgen`, `ase`) are already isolated behind
  runtime imports. Phase 31 should not require those dependencies just to decide
  loss semantics or build the normalized bridge artifact.
- Some candidates only have qphi coordinates and derive fractional/cartesian
  positions indirectly. That coordinate origin needs to stay visible in the
  translated artifact so later exporters can distinguish “exact periodic data
  supplied” from “periodic proxy derived from QC-native source geometry.”
- The interop layer must stay additive to the shipped workflow. Nothing in
  Phase 31 should alter `llm-generate`, `llm-evaluate`, or existing Zomic
  corpus behavior.

## Recommended Plan Split

- **Plan 01:** lock the translation schema, export-fidelity contract, and target
  registry.
- **Plan 02:** implement deterministic normalization from `CandidateRecord` into
  a translated structure artifact with coordinate-origin and loss diagnostics.
- **Plan 03:** freeze the contract with real fixtures and a developer-facing
  translation note so Phase 32 can implement serializers against stable inputs.

## Validation Architecture

- Reuse the existing `pytest` infrastructure in `materials-discovery/`; no new
  framework work is needed.
- Add focused contract coverage in a new
  `materials-discovery/tests/test_llm_translation_schema.py`.
- Add normalization and loss-classification coverage in a new
  `materials-discovery/tests/test_llm_translation_core.py`, with any necessary
  extension to `materials-discovery/tests/test_structure_realization.py`.
- Add fixture-backed regression coverage in a new
  `materials-discovery/tests/test_llm_translation_fixtures.py`.
- Anchor the fixture set on at least two candidate classes:
  - one periodic/approximant-safe candidate that can qualify for exact or
    anchored downstream translation
  - one QC-native/lossy candidate where CIF or material-string exports must
    report representational loss explicitly
- Keep every Phase 31 plan task tied to an automated verification command so the
  phase can execute under the existing GSD validation loop without a Wave 0 test
  bootstrap.
