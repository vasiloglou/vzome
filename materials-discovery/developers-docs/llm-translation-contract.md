# LLM Translation Contract

This note is the Phase 31 implementation handoff for Phase 32 exporter work.
It describes the normalized translation artifact, the current target registry,
and the fidelity semantics that serializer code must preserve.

This is not an operator runbook. CLI workflow, artifact storage workflow, and
benchmark reuse docs remain Phase 33 work.

## Source Of Truth Boundary

Compiled Zomic candidates remain the source of truth. Export artifacts are
additive interoperability views derived from a `CandidateRecord`; they do not
replace Zomic as the QC-native representation.

The translation layer therefore starts from the compiled candidate contract:

- `CandidateRecord` is the only Phase 31 source input.
- `TranslatedStructureArtifact` records the source candidate ID, system,
  template family, and provenance hints.
- Downstream exporters must preserve that linkage instead of emitting ad hoc
  CIF or material-string payloads with detached provenance.

If a downstream target cannot preserve QC-native semantics, the export still
may exist, but it must say so explicitly in the artifact fidelity and
diagnostics instead of pretending the result is native or lossless.

## Built-In Target Families

Phase 31 registers two target families through
`list_translation_targets()` / `resolve_translation_target()`:

| Family | Target Format | Requires Periodic Cell | Preserves QC-Native Semantics | Intended Use |
|---|---|---|---|---|
| `cif` | `cif_text` | yes | no | CIF-oriented crystal and materials workflows |
| `material_string` | `crystaltextllm_material_string` | yes | no | CrystalTextLLM-style line-oriented text workflows |

Both built-in targets currently require periodic-cell structure data and
fractional coordinates. Neither target is allowed to claim that it preserves
QC-native Zomic semantics exactly.

## Normalized Artifact Contract

Phase 32 serializers should consume `TranslatedStructureArtifact`, not raw
candidate dicts and not reparsed Zomic text.

Relevant fields:

- `source`: typed linkage back to the source candidate record
- `target`: resolved target descriptor with periodic-cell and semantics flags
- `fidelity_tier`: `exact`, `anchored`, `approximate`, or `lossy`
- `loss_reasons`: explicit reasons when a target drops source semantics
- `composition`, `cell`, `sites`: normalized structure payload for serializers
- `diagnostics`: warnings/errors about coordinate origin and representation loss
- `emitted_text`: reserved for later serializer output and intentionally `None`
  in Phase 31

Site ordering is deterministic and matches the input `CandidateRecord` site
order so later serializers can emit stable text artifacts.

## Coordinate-Origin Contract

The normalization seam reuses structure realization and makes coordinate origin
explicit. Exporters should treat these origins as part of the contract:

- `stored_fractional`: the candidate already carried periodic-safe fractional
  positions
- `stored_cartesian`: the candidate carried cartesian positions and the
  normalized fractional coordinates were derived from them
- `qphi_derived`: the candidate only carried QC-native/qphi geometry and the
  periodic-coordinate view was derived during normalization

When any site needs derived coordinates, the artifact emits the
`coordinate_derivation_required` diagnostic with per-site source metadata.

## Fidelity Semantics

Serializer code must not recalculate or silently weaken fidelity. Phase 31
already classifies the export posture:

- `exact`: strong periodic-safe evidence exists and every site already has
  stored fractional coordinates compatible with the target family
- `anchored`: the structure intent is still periodic-safe, but one or more
  coordinates came from stored cartesian data rather than already-stored
  fractional coordinates
- `approximate`: the structure is not QC-native/lossy, but normalization had to
  rely on a mixed-origin or otherwise weaker periodic proxy
- `lossy`: the target cannot faithfully preserve the source semantics; this is
  the required state when a QC-native source is forced into a periodic export

Supported loss reasons today:

- `aperiodic_to_periodic_proxy`
- `coordinate_derivation_required`
- `qc_semantics_dropped`
- `unsupported_exactness_claim`

For periodic exporters, the key rule is simple: a QC-native source may still be
exported, but the result is a periodic proxy and must remain explicitly lossy.

## Fixture Boundary For Phase 32

Phase 31 freezes two repo-backed fixture classes under
`tests/fixtures/llm_translation/`:

- `al_cu_fe_periodic_candidate.json`: periodic-safe fixture with stored
  fractional positions on every site, proving the exact/export-ready path
- `sc_zn_qc_candidate.json`: QC-native fixture with qphi-only site geometry,
  proving the explicit lossy periodic-proxy path

Those fixtures make the distinction visible in data shape, not only in prose.

The `approximate` tier is intentionally not a separate fixture in this wave.
That middle case is already locked by
`tests/test_llm_translation_core.py` through the mixed-origin candidate path.
Phase 31 fixture coverage is focused on the two exporter-facing boundary cases
that Phase 32 must not regress: periodic-safe exactness and QC-native lossy
translation.

## Phase 32 Handoff

Phase 32 should serialize from the normalized artifact exactly as produced:

1. Resolve a built-in target descriptor with `resolve_translation_target(...)`.
2. Build a `TranslatedStructureArtifact` with `prepare_translated_structure(...)`.
3. Emit CIF or material-string text from the normalized `cell` and `sites`.
4. Carry forward `source`, `fidelity_tier`, `loss_reasons`, and `diagnostics`
   into the exported artifact or its sidecar metadata.

Phase 32 should not:

- treat emitted CIF or material strings as a new source of truth
- bypass the typed target registry
- erase lossy or approximate semantics because the text serializer succeeded
- replace this developer contract with operator-facing workflow guidance

Operator docs, CLI walkthroughs, and benchmark reuse guidance belong in Phase
33 after the serializer surface exists.
