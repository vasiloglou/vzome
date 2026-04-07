---
phase: 32
reviewers: [gemini, claude]
reviewed_at: 2026-04-07T02:40:51Z
plans_reviewed:
  - .planning/phases/32-cif-and-material-string-exporters/32-01-PLAN.md
  - .planning/phases/32-cif-and-material-string-exporters/32-02-PLAN.md
  - .planning/phases/32-cif-and-material-string-exporters/32-03-PLAN.md
---

# Cross-AI Plan Review - Phase 32

Per the review workflow, the Codex CLI was not used as a reviewer because the
current session is already running inside Codex and the review was kept
independent.

## Gemini Review

# Phase 32: CIF and Material-String Exporters - Plan Review

The proposed plans establish a solid foundation for the shared exporter seam and
validation layer. However, they contain significant deviations from the research
recommendations regarding target format specifications and serialization
libraries. These deviations introduce a high risk of producing artifacts that
are incompatible with the external tools they are intended to support.

## Summary
The plans successfully define a deterministic export workflow that preserves the
`TranslatedStructureArtifact` as the source of truth. However, **Plan 02**
proposes a custom key-value material-string format that is incompatible with the
**CrystalTextLLM** specification it claims to implement. Furthermore,
**Plan 01** opts for a hand-rolled CIF serializer despite research warnings
about the complexity of the CIF grammar and the availability of a verified
backend in `pymatgen`.

## Strengths
- **Robust Shared Seam:** The introduction of
  `validate_translated_structure_for_export` and `emit_translated_structure`
  ensures that all exporters share a consistent validation and dispatch logic.
- **Deterministic Formatting:** The use of a shared float formatting helper is
  excellent for ensuring byte-stable outputs.
- **Fidelity Preservation:** The plans correctly maintain the linkage between
  the emitted text and the artifact's fidelity/loss metadata.
- **Regression Anchors:** Using golden-output fixtures in Plan 03 is the correct
  approach for long-term stability.

## Concerns
- **HIGH: Material String Format Mismatch:** Plan 02 Task 1 implements a custom
  key-value line format (for example, `cell a=...`, `site label=...`). Research
  indicates that the `crystaltextllm_material_string` format expects a specific
  line-oriented grammar: lattice lengths line, lattice angles line, then
  alternating species and coordinate lines. The proposed format will not be
  parseable by CrystalTextLLM-oriented workflows.
- **HIGH: Metadata in Material String Body:** Plan 02 embeds source ID and
  fidelity headers directly into the material string. Research explicitly warns
  that the CrystalTextLLM parser expects numeric lattice data on the first line;
  a text preamble will break compatibility with downstream model code.
- **MEDIUM: Hand-rolled CIF Serializer:** Plan 01 opts for pure-text
  serialization for CIF. Research warns that CIF is deceptively complex
  (handling quoting, loops, and occupancies) and strongly recommends using the
  already-installed `pymatgen.CifWriter` with symmetry disabled
  (`symprec=None`) to ensure syntax correctness.
- **MEDIUM: CIF Comment Preamble:** Plan 01 adds a comment header to the CIF
  text. While less destructive than the material string preamble, research
  recommended keeping `emitted_text` clean in Phase 32 and deciding on
  sidecar/comment mirroring in Phase 33.

## Suggestions
1. **Align Material String with CrystalTextLLM Spec:** Revise **Plan 02 Task 1**
   to implement the exact line grammar found in the research (lengths line,
   angles line, species line, coordinate line, and so on).
2. **Isolate Metadata from Raw Text:** Remove the metadata headers from the
   material string body. Metadata should reside in the
   `TranslatedStructureArtifact` object or be handled via sidecars/comments in
   Phase 33.
3. **Adopt `pymatgen` for CIF:** Revise **Plan 01 Task 2** to utilize
   `pymatgen.CifWriter`. This leverages a mature, standards-compliant library
   and avoids the risk of subtle syntax errors in a hand-rolled implementation.
4. **Expand Parser Validation:** In **Plan 03**, add a test case that validates
   the material string against the actual logic found in the CrystalTextLLM
   `parse_fn` (as documented in the research) to ensure the output is truly
   model-oriented.

## Risk Assessment
**MEDIUM-HIGH**

The primary risk is the delivery of interoperability artifacts that fail to
interoperate. Specifically, the proposed material string format is not compliant
with the targeted CrystalTextLLM ecosystem. Additionally, hand-rolling the CIF
serializer increases the maintenance burden and the risk of generating payloads
that are rejected by external materials science toolchains.

**Justification:** The deviation from the CrystalTextLLM format is a functional
regression relative to the phase requirements (`LLM-29`). Aligning these plans
with the research-backed specifications before execution is critical.

---

## Claude Review

# Phase 32 Plan Review: CIF and Material-String Exporters

## Overall Assessment

The three plans are well-structured, incrementally layered, and tightly scoped.
The wave-based dependency chain (01 -> 02 -> 03) is clean and each plan has
clear boundaries. However, there are two significant design tensions between
the plans and the research that produced them, and a few edge-case gaps worth
flagging before execution.

## Plan 32-01: Shared Export Seam + CIF Serializer

### Summary

Plan 01 delivers the foundation: a validation gate, a deterministic float
formatter, a target-family dispatcher, and the CIF text emitter. The scope is
appropriate for a first wave. The two tasks are correctly ordered (shared seam
first, then CIF-specific serialization). The TDD behavior list is concrete and
testable.

### Strengths

- Clean separation of validation (`validate_translated_structure_for_export`)
  from emission (`emit_cif_text`) from dispatch (`emit_translated_structure`)
- Explicit `NotImplementedError` stub for `material_string` prevents accidental
  use before Plan 02 lands
- The comment preamble in CIF output (source candidate ID, fidelity tier, loss
  reasons) makes lossy periodic-proxy posture visible in the emitted text
  itself, not just on the artifact wrapper
- Compatibility test against the repo-local `parse_cif()` is a pragmatic
  regression guard
- `model_copy` semantics (return new artifact, do not mutate input) match the
  Pydantic contract correctly

### Concerns

- **HIGH - Contradicts research "Don't Hand-Roll" guidance for CIF.** The
  plan's must-have truth says `CIF emission must stay pure Python text
  serialization; do not introduce optional CIF-writer dependencies.` The
  research explicitly warns against this and recommends `pymatgen.CifWriter`
  with `symprec=None`. For the narrow Phase 32 subset (simple labels, no
  special characters, no partial occupancies in fixtures, no multi-line values),
  hand-rolling is likely safe. But the plan should acknowledge this deviation
  and document that CIF edge cases (quoted labels, semicolon text fields,
  multi-site partial occupancy formatting) are explicitly out of scope for this
  emitter. If the fixtures never exercise those paths, a future candidate with
  a label like `Al'1` or an occupancy-weighted mixed-species site could produce
  malformed CIF silently.
- **MEDIUM - Float formatter specification is ambiguous at boundaries.** The
  plan says six-decimal precision, trims trailing zeroes, keeps at least one
  decimal digit. What happens with very small values like `0.0000001`
  (rounds to `0.0`) or very large angles? The formatter specification should
  confirm rounding behavior and whether scientific notation is ever emitted. For
  CIF specifically, downstream parsers expect plain decimal notation.
- **LOW - `cell` can be `None` in the schema.** The validation function
  correctly handles this (`requires_periodic_cell=True` plus missing cell =
  fail). But the plan's behavior list does not explicitly test the `cell={}`
  case (empty dict rather than `None`). An empty dict would pass a `None` check
  but still be useless.

### Suggestions

- Add a one-line note in the plan or the emitter docstring acknowledging that
  this CIF emitter handles the Phase 32 subset only (simple labels, full
  occupancy, no semicolon text fields) and is not a general-purpose CIF writer.
- Consider testing `cell={}` as an additional malformed-artifact case alongside
  `cell=None`.
- Pin the rounding mode in the float formatter spec to prevent surprise if
  someone later changes it.

## Plan 32-02: Material-String Exporter + Cross-Target Dispatch

### Summary

Plan 02 adds the CrystalTextLLM-style material-string emitter and finishes the
dispatcher so both target families work through one public entry point. Two
tasks: implement the string emitter, then verify cross-target dispatch
stability. The dependency on Plan 01 is correctly declared.

### Strengths

- Uses the same shared validation gate and float formatter from Plan 01,
  avoiding divergent formatting logic
- Cross-target tests that emit both CIF and material-string from the same
  artifact prove the normalization identity is preserved
- Explicit test that unsupported target families still fail cleanly prevents
  silent fallback
- Keeps cartesian coordinates out of the first material-string format, reducing
  scope correctly

### Concerns

- **HIGH - The specified material-string format is not
  CrystalTextLLM-compatible, but the target is named
  `crystaltextllm_material_string`.** The plan specifies a self-describing
  format with header lines (`source_candidate_id`, `system`, `target_format`,
  `fidelity_tier`, `loss_reasons`) followed by `cell a=... b=...` and
  `site label=... species=...` lines. CrystalTextLLM's actual format is bare:
  lengths on line 1, angles on line 2, then alternating species and coordinate
  lines with no headers or key=value syntax. The research warns explicitly in
  Pitfall 4 that the downstream parser cannot ingest the emitted text because
  the first line is no longer lattice lengths. This format will not round-trip
  through CrystalTextLLM's `parse_fn`. If the intent is an auditable repo
  format that also carries metadata, that is a valid design choice, but then
  either rename the target to avoid confusion or document that this is a
  CrystalTextLLM-inspired material string with provenance headers and that
  stripping the headers yields the bare CrystalTextLLM body.
- **MEDIUM - Must-have truth says "loss reasons in the emitted text" but
  research says keep metadata on the artifact.** The Plan 02 must-have states
  `Cross-target export must preserve source linkage, fidelity tier, and loss
  reasons in the emitted text instead of relying on sidecar state alone.` The
  research says the opposite for material strings: keep proxy/loss labeling
  explicit on the surrounding artifact fields and use a sidecar rather than a
  body preamble if standalone raw files are written later. The plan should
  clarify whether this is an intentional departure and whether the
  `emitted_text` field on the artifact is meant to hold the full
  self-describing text or just the bare body.
- **LOW - No parse round-trip test for material-string.** Plan 01 Task 2 tests
  CIF parser compatibility with `parse_cif()`. Plan 02 has no equivalent test
  that re-parses the material-string output. Adding a simple line-grammar parse
  helper or at least asserting line count and structure would catch format
  regressions without requiring an external parser dependency.

### Suggestions

- Resolve the naming/format tension before execution. Either:
  (A) emit the bare CrystalTextLLM body in `emitted_text` and keep metadata on
  the artifact fields, or
  (B) keep the self-describing format but rename the target or add a
  `.bare_body` accessor that strips headers for downstream parser compatibility.
- Add a test that parses the emitted material-string lines back into cell,
  species, and coordinates to verify structural intent, similar to the CIF
  parse-back test.
- Document in the plan or code that this format is not directly ingestible by
  CrystalTextLLM's `parse_fn` without header stripping.

## Plan 32-03: Golden Fixtures + Parser Compatibility + Failure Coverage

### Summary

Plan 03 freezes exporter behavior with four golden output files and adds parser
round-trip and malformed-artifact failure tests. This is the right capstone for
the phase because it turns the earlier unit tests into regression anchors. The
dependency on both Plan 01 and Plan 02 is correctly declared.

### Strengths

- Golden-output byte comparison is the strongest stability guarantee the phase
  can offer
- Separate golden files for exact (Al-Cu-Fe) and lossy (Sc-Zn) cases across
  both target families gives 2x2 boundary coverage
- Parser compatibility tests using the repo-local `parse_cif()` prove the CIF
  output is actually usable, not just syntactically valid
- Clear separation between malformed artifact fails and legitimate lossy export
  succeeds prevents the validation gate from accidentally blocking valid lossy
  exports
- Fixture file naming convention (`.cif`, `.material_string.txt`) is clear and
  greppable

### Concerns

- **MEDIUM - Golden files are generated during test execution, not before.**
  The plan says to add checked-in golden outputs but does not specify how to
  generate the initial golden content. If the executor generates the goldens by
  running the exporter and checking in the output, the initial commit is a
  tautology. The plan should specify that the golden files are generated once,
  manually inspected for correctness, and then checked in.
- **MEDIUM - No `approximate` tier coverage in golden outputs.** Phase 31
  deferred the approximate fixture to `test_llm_translation_core.py`. Plan 03
  only covers exact and lossy golden outputs. This leaves a gap where the
  approximate-tier export path is untested at the serializer level.
- **LOW - Plan 03 Task 2 adds tests to files from earlier plans.** This is fine
  technically but means Plan 03 commits modify Plan 01's test files. The
  executor should ensure these additions do not break the Plan 01/02 tests or
  create merge complexity if plans are executed by different agents.

### Suggestions

- Add an explicit instruction that the golden files must be manually inspected
  or at minimum structurally validated before being committed as ground truth.
- Add one non-golden export test for the approximate tier (the mixed-origin
  candidate from `test_llm_translation_core.py`) at the serializer level, as
  the research recommended.
- Consider whether the parser compatibility tests in Task 2 should also verify
  the lossy CIF golden against `parse_cif()`, not just structural recovery.

## Cross-Plan Concerns

### Design Tension: Research vs. Plan Decisions

| Topic | Research Recommendation | Plan Decision | Risk |
|-------|------------------------|---------------|------|
| CIF emission | Use `pymatgen.CifWriter` with `symprec=None` | Hand-roll pure-text CIF serializer | **MEDIUM** - correct for narrow scope, but undocumented deviation |
| Material-string format | Bare CrystalTextLLM body (lengths/angles/species/coords) | Self-describing format with metadata headers | **HIGH** - breaks CrystalTextLLM parser compatibility |
| Metadata in material-string body | Keep on artifact, not in body | Embed in body text | **HIGH** - contradicts research anti-pattern |
| `approximate` export coverage | Add one non-golden test | Not included in any plan | **MEDIUM** - gap in serializer coverage |

### Dependency Chain Health

The 01 -> 02 -> 03 chain is clean. No circular dependencies. Each plan's
`depends_on` is correct. Wave-based parallelization is correctly sequential
(each wave depends on the prior).

### Requirement Coverage

| Requirement | Plan Coverage | Status |
|-------------|--------------|--------|
| LLM-28 (CIF export) | Plan 01 Task 2 + Plan 03 golden + parser | Fully covered |
| LLM-29 (material-string export) | Plan 02 Task 1 + Plan 03 golden | Covered, but format compatibility concern |
| Progress.md updates | All plans include this as a must-have truth | Covered |

## Risk Assessment

**Overall Risk: MEDIUM**

**Justification:** The plans are well-structured and the scope is appropriate.
The two high-severity concerns (material-string format incompatibility with
CrystalTextLLM and the research/plan tension on metadata placement) are design
decisions, not execution risks. If the team is intentionally building a
self-describing material-string format for auditability rather than direct
CrystalTextLLM parser compatibility, that is a valid choice, but it should be
made explicitly rather than discovered when someone tries to feed the output
into CrystalTextLLM's `parse_fn`. The CIF hand-rolling risk is low given the
narrow scope but should be documented.

**Recommendation:** Resolve the material-string format question before executing
Plan 02. The simplest path is to emit the bare CrystalTextLLM body in
`emitted_text` (matching the research) and rely on the artifact wrapper for
metadata. If the self-describing format is intentional, rename it or document
the incompatibility.

---

## Consensus Summary

Both reviewers agree that the overall phase structure is strong: Plan 01 lays
the shared export seam, Plan 02 adds the second target family without reopening
normalization, and Plan 03 freezes behavior with golden fixtures and parser
checks. They also agree that deterministic formatting, artifact-preserving
dispatch, and explicit lossy/export metadata are the right foundations for the
phase.

### Agreed Strengths

- The three-plan dependency chain is clean, additive, and appropriately scoped.
- A shared validation and dispatch seam reduces the risk of CIF and
  material-string exporters drifting from one another.
- Deterministic formatting and checked-in golden fixtures are the right way to
  anchor serializer stability.
- The plans correctly keep `TranslatedStructureArtifact` as the source of truth
  instead of re-normalizing candidates during export.

### Agreed Concerns

- The current Plan 02 material-string layout does not match the actual
  CrystalTextLLM grammar implied by the
  `crystaltextllm_material_string` target name. This is the highest-priority
  issue because it risks shipping a format that downstream tools cannot parse.
- The plans and the research disagree about where export metadata should live
  for material strings. The plans embed provenance/fidelity headers into the
  emitted body, while the research recommends keeping that metadata on the
  artifact wrapper and preserving a bare parser-compatible text body.
- Plan 01 deliberately departs from the research recommendation to use
  `pymatgen.CifWriter`. That may still be acceptable for a narrow Phase 32
  subset, but the scope boundary and edge cases should be made explicit before
  execution.

### Divergent Views

- Gemini treats the hand-rolled CIF approach itself as a medium concern and
  recommends switching to `pymatgen` before execution. Claude is more tolerant
  of a hand-rolled serializer if the scope is explicitly constrained and edge
  cases are documented.
- Gemini focuses almost entirely on external format compatibility. Claude adds
  two additional quality gaps: missing approximate-tier serializer coverage and
  the need to manually inspect or structurally validate initial golden files
  before treating them as ground truth.

### Suggested Next Move

Before executing Phase 32, tighten the plan contract around one question:
should `emitted_text` for `crystaltextllm_material_string` be a bare
CrystalTextLLM-compatible body, or an auditable repo-native wrapper format? If
the former, move metadata to the artifact/sidecar path and keep the body parse
compatible. If the latter, rename or document the target accordingly so
`LLM-29` is satisfied honestly.
