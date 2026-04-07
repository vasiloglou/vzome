# Phase 32: CIF and Material-String Exporters - Research

**Researched:** 2026-04-06
**Domain:** Deterministic external-structure serialization from `TranslatedStructureArtifact`
**Confidence:** HIGH

## User Constraints

No phase-specific `32-CONTEXT.md` exists.

Honor the explicit scope from the user prompt and milestone docs:

- Cover `LLM-28` and `LLM-29` explicitly.
- Keep the research repo-specific and implementation-oriented.
- Focus on:
  - where CIF export should live and how to emit deterministic CIF text from the translated artifact rather than from ad hoc notebook code
  - what model-oriented material-string format is the best first target for this repo, given the contract names already shipped in Phase 31
  - whether CIF and material-string export should share a common normalized serialization helper layer or branch independently
  - what fixture/failure coverage is needed for representative Al-Cu-Fe and Sc-Zn exports
  - how to keep lossy periodic-proxy labeling explicit in the emitted artifacts
  - how to validate deterministic output stability without overfitting tests to formatting trivia

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LLM-28 | The platform can export supported translated candidates as CIF artifacts for CIF-oriented external materials LLM workflows without requiring ad hoc notebook conversion. | Add a repo-owned exporter module under `materials_discovery.llm` that serializes `TranslatedStructureArtifact` to CIF via `pymatgen.CifWriter` with symmetry discovery disabled and artifact-derived labels/occupancies preserved. |
| LLM-29 | The platform can export at least one model-oriented crystal/material string encoding from the same translated candidate for CrystalTextLLM- or CSLLM-style downstream workflows. | Keep the shipped `crystaltextllm_material_string` contract and implement a deterministic CrystalTextLLM-style body formatter from the same normalized artifact; do not pivot to CSLLM’s symmetry/Wyckoff string in Phase 32. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Any change under `materials-discovery/` must update `materials-discovery/Progress.md`.
- That update must add:
  - one new Changelog row
  - one timestamped Diary entry under the current date heading

## Summary

Phase 31 already established the right boundary: `prepare_translated_structure()` produces a deterministic, typed `TranslatedStructureArtifact` with source linkage, fidelity tier, loss reasons, diagnostics, cell data, and ordered sites. Phase 32 should not reopen normalization. It should add a thin exporter layer that accepts the Phase 31 artifact and emits target-specific text while preserving the artifact as the auditable wrapper.

For CIF, the repo should use `pymatgen` as a controlled backend, not a hand-built CIF string and not the current `build_pymatgen_structure(candidate)` helper. Local inspection showed that `CifWriter` is stable for ordered structures when symmetry detection is off, but symmetry detection materially rewrites the cell, multiplicities, labels, and formula units. That means the safe pattern is: build a `Structure` from `TranslatedStructureArtifact.sites`, preserve labels and occupancies explicitly, and call `CifWriter(..., symprec=None, significant_figures=8)` so the emitted text reflects the translated artifact rather than a reinterpreted structure.

For the first material-string target, the best fit is the CrystalTextLLM body format already implied by the shipped `crystaltextllm_material_string` target name. CrystalTextLLM’s own code uses a simple line-oriented schema of lattice lengths, lattice angles, and alternating species / fractional-coordinate lines. CSLLM’s released preprocessing code instead converts structures into a symmetry- and Wyckoff-based string through `pyxtal`, which would require new inference, new dependencies, and semantics that Phase 31’s artifact does not carry. Phase 32 should therefore ship a deterministic CrystalTextLLM-style formatter and defer any CSLLM-style symmetry string to a later phase if external benchmarking proves it necessary.

**Primary recommendation:** Add `materials_discovery.llm.exporters` as an artifact-first serialization module, use `pymatgen.CifWriter` with symmetry disabled for CIF, and implement a deterministic CrystalTextLLM-style material-string formatter from the same normalized artifact while keeping fidelity/loss metadata on the artifact rather than injecting it into the raw material-string body.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `materials_discovery.llm.translation` | repo | Produces the normalized `TranslatedStructureArtifact` | Phase 31 already froze this as the exporter source of truth; reopening normalization would duplicate logic and risk fidelity drift. |
| `pymatgen` | `2025.10.7` installed in current `uv` env | CIF writing and CIF parsing for verification | Already declared in repo optional deps, already available locally, and provides a mature CIF writer/parser so Phase 32 does not hand-roll CIF syntax. |
| `pydantic` | `2.12.5` | Additive artifact model updates (`emitted_text`, copied artifacts, validation) | Already central to repo contracts and Phase 31 schema models. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | `9.0.2` | Exporter regression coverage | Use for byte-stability, semantic parse checks, and failure-path tests. |
| `numpy` | `2.4.2` | Already present transitively in the repo runtime | No new Phase 32 role beyond existing repo usage. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pymatgen.CifWriter` for CIF text | Hand-written CIF string builder | Not recommended. CIF quoting, loop formatting, comments, and occupancy handling are easy to get subtly wrong. |
| CrystalTextLLM-style line body | CSLLM symmetry/Wyckoff string | Not recommended for Phase 32. CSLLM’s released code requires symmetry reduction through `pyxtal` and emits Wyckoff strings that the Phase 31 artifact does not natively contain. |
| Thin shared helper layer plus target-specific emitters | One generic serializer engine | Over-abstract for this phase. The two formats share cell/site ordering but diverge at final text shape. |
| Export directly from `CandidateRecord` or `build_pymatgen_structure(candidate)` | Export from `TranslatedStructureArtifact` | Wrong boundary. It bypasses Phase 31 fidelity/loss semantics and, in the current helper, drops label/occupancy intent unless extended. |

**Installation:**
```bash
cd materials-discovery
uv sync --extra dev --extra mlip
```

**Version verification:** Verified against the package registry and current environment on 2026-04-06.

- `pymatgen`: PyPI latest `2026.3.23` published 2026-03-23; current env `2025.10.7`. The required `Structure(labels=...)` and `CifWriter` APIs are already present, so Phase 32 does not need a version bump unless a concrete writer bug appears in tests.
- `pytest`: PyPI latest and current env `9.0.2`, published 2025-12-06.
- `pydantic`: PyPI latest and current env `2.12.5`, published 2025-11-26.

## Architecture Patterns

### Recommended Project Structure

```text
materials-discovery/src/materials_discovery/llm/
├── translation.py        # Phase 31 normalized artifact creation
├── exporters.py          # New Phase 32 target dispatch + text emitters
└── __init__.py           # Additive exporter exports

materials-discovery/tests/
├── test_llm_translation_exporters.py
└── fixtures/llm_translation_exports/
    ├── al_cu_fe_periodic.cif
    ├── al_cu_fe_periodic.material.txt
    ├── sc_zn_qc_proxy.cif
    └── sc_zn_qc_proxy.material.txt
```

### Pattern 1: Artifact-First Export Dispatch

**What:** Keep normalization and serialization as separate steps. Build the translated artifact first, then dispatch to a target-specific emitter using `artifact.target.family`.

**When to use:** Always. This is the Phase 31 handoff contract.

**Example:**
```python
from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    prepare_translated_structure,
    resolve_translation_target,
)


def export_candidate(candidate: CandidateRecord, target_family: str):
    target = resolve_translation_target(target_family)
    artifact = prepare_translated_structure(candidate, target)
    emitted_text = render_translated_structure(artifact)
    return artifact.model_copy(update={"emitted_text": emitted_text})
```

Source: local contract in `materials-discovery/src/materials_discovery/llm/translation.py` and `materials-discovery/developers-docs/llm-translation-contract.md`.

### Pattern 2: Deterministic CIF Through `pymatgen` With Symmetry Detection Disabled

**What:** Build a `pymatgen.Structure` from the already-normalized artifact, preserving site order, labels, and occupancies, then emit CIF with `CifWriter(..., symprec=None, significant_figures=8)`.

**When to use:** For `target.family == "cif"` only.

**Example:**
```python
from pymatgen.core import Lattice, Structure
from pymatgen.io.cif import CifWriter


def emit_cif_text(artifact) -> str:
    lattice = Lattice.from_parameters(
        artifact.cell["a"],
        artifact.cell["b"],
        artifact.cell["c"],
        artifact.cell["alpha"],
        artifact.cell["beta"],
        artifact.cell["gamma"],
    )
    structure = Structure(
        lattice=lattice,
        species=[{site.species: site.occupancy} for site in artifact.sites],
        coords=[site.fractional_position for site in artifact.sites],
        coords_are_cartesian=False,
        labels=[site.label for site in artifact.sites],
    )
    return str(CifWriter(structure, symprec=None, significant_figures=8))
```

Source: `pymatgen` `CifWriter` and `Structure` APIs plus local runtime inspection in the current `uv` environment.

### Pattern 3: CrystalTextLLM Body Formatter, But Without Training-Time Augmentation

**What:** Emit the CrystalTextLLM line grammar directly from the artifact cell and ordered fractional coordinates:

1. lengths line
2. angles line
3. alternating species and fractional-coordinate lines

**When to use:** For `target.family == "material_string"` and `target.target_format == "crystaltextllm_material_string"`.

**Example:**
```python
def emit_crystaltextllm_material_string(artifact) -> str:
    lengths = " ".join(f"{artifact.cell[key]:.1f}" for key in ("a", "b", "c"))
    angles = " ".join(f"{int(round(artifact.cell[key]))}" for key in ("alpha", "beta", "gamma"))
    site_lines = "\n".join(
        f"{site.species}\n"
        + " ".join(f"{coord:.2f}" for coord in site.fractional_position)
        for site in artifact.sites
    )
    return f"{lengths}\n{angles}\n{site_lines}"
```

Source: CrystalTextLLM’s official `get_crystal_string` / `parse_fn` format, adapted to remove their random unit-cell translation because Phase 32 requires deterministic output.

### Pattern 4: Shared Thin Canonical Helper Layer, Independent Final Emitters

**What:** Share only the helper functions that are genuinely common:

- ordered cell access
- ordered site iteration
- required-field validation before emit
- target dispatch

Branch independently at final text assembly:

- CIF needs labels, occupancies, and CIF grammar.
- CrystalTextLLM body needs bare lengths/angles/species/coords with no metadata preamble.

**When to use:** For all exporter implementations in this phase.

### Anti-Patterns to Avoid

- **Direct candidate export:** Do not emit CIF or material strings directly from `CandidateRecord` or notebook scratch state. The Phase 31 artifact is the source of export truth.
- **Symmetry-refined CIF output:** Do not pass `symprec` or any other symmetry-discovery path to `CifWriter` for the default exporter. Local tests showed that it can rewrite the lattice, multiplicities, formula units, and labels.
- **Reusing `build_pymatgen_structure(candidate)` unchanged:** The current helper is backend-focused, candidate-based, and does not preserve artifact-specific label/occupancy intent.
- **Copying CrystalTextLLM’s random translation augmentation:** Their training code intentionally random-translates structures inside the unit cell. That is correct for data augmentation and wrong for deterministic repo exports.
- **Embedding proxy/loss text inside the raw material-string body:** CrystalTextLLM’s parser expects lengths on the first line. A metadata preamble will break compatibility.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CIF syntax emission | Manual string concatenation for loops, comments, field quoting, and occupancies | `pymatgen.CifWriter` driven from artifact-built `Structure` | CIF is deceptively complex and Phase 32 gains nothing from reimplementing its grammar. |
| Symmetry/Wyckoff reduction for a CSLLM-like string | New `pyxtal`/space-group inference stack in this phase | CrystalTextLLM-style body formatter | Phase 31 artifact does not contain Wyckoff positions; inferring them adds new heuristics, dependencies, and failure modes. |
| Coordinate normalization for export | Fresh candidate-to-fractional conversion logic in exporter code | `prepare_translated_structure()` | Phase 31 already solved determinism, fidelity, and coordinate-origin diagnostics. |
| Loss/proxy annotations in target text bodies | Format-specific comment hacks for every target | Keep fidelity, `loss_reasons`, and diagnostics on the artifact; decide raw-file mirroring later | Raw material strings need to stay parseable by downstream model code. |

**Key insight:** Phase 31 already created the hard part. Phase 32 should be a controlled text-emission layer over that artifact, not a second normalization or symmetry-inference project.

## Common Pitfalls

### Pitfall 1: Letting the CIF backend "improve" the structure

**What goes wrong:** The emitted CIF no longer matches the translated artifact. Cell parameters, multiplicities, `Z`, and labels can change.

**Why it happens:** `pymatgen.CifWriter` can perform symmetry analysis and refined-structure conversion when `symprec` is set.

**How to avoid:** Use `symprec=None` for the default exporter. Preserve the artifact’s direct periodic proxy as-is.

**Warning signs:** A simple three-site structure suddenly emits non-`P 1` symmetry, different lattice lengths/angles, or multiplied formula units.

### Pitfall 2: Bypassing the translated artifact

**What goes wrong:** Export succeeds, but fidelity tier, loss reasons, diagnostics, and source linkage are no longer guaranteed to match the emitted text.

**Why it happens:** Export code reaches back to `CandidateRecord` or backend helpers instead of consuming `TranslatedStructureArtifact`.

**How to avoid:** Make the public exporter API take `TranslatedStructureArtifact` or return one with `emitted_text` filled.

**Warning signs:** Export tests pass while `loss_reasons`, `coordinate_derivation_required`, or source IDs disappear from the returned object.

### Pitfall 3: Treating CrystalTextLLM’s training formatter as an exact export spec

**What goes wrong:** The repo copies the random unit-cell translation augmentation from CrystalTextLLM and loses determinism.

**Why it happens:** Their official `get_crystal_string` helper random-translates structures before formatting to diversify training data.

**How to avoid:** Keep the same line grammar, but emit the artifact’s canonical coordinates exactly once and do not augment.

**Warning signs:** Repeated exports of the same artifact produce different fractional coordinates while fidelity metadata remains unchanged.

### Pitfall 4: Trying to make the raw material string self-describing

**What goes wrong:** The downstream parser cannot ingest the emitted text because the first line is no longer lattice lengths.

**Why it happens:** The format is intentionally bare and line-oriented.

**How to avoid:** Keep proxy/loss labeling explicit on the surrounding artifact fields. If Phase 33 later writes standalone raw files, use a sidecar rather than a body preamble.

**Warning signs:** A CrystalTextLLM-style parse helper fails before it reaches the species lines.

### Pitfall 5: Snapshot-only tests that lock in trivia instead of behavior

**What goes wrong:** Harmless whitespace or formula-order changes fail tests, while semantic regressions can still slip through.

**Why it happens:** The suite only compares raw text and never reparses emitted payloads.

**How to avoid:** Use a layered test strategy:

- byte-stability checks for repeated export of the same artifact
- semantic parse checks for CIF and material strings
- a small number of golden text fixtures for representative exact and lossy outputs

**Warning signs:** Test failures point at comment lines or blank lines rather than changed structure meaning.

## Code Examples

Verified patterns from official sources and current repo constraints:

### CIF Export From Artifact

```python
from pymatgen.core import Lattice, Structure
from pymatgen.io.cif import CifWriter


def emit_cif_text(artifact) -> str:
    structure = Structure(
        lattice=Lattice.from_parameters(
            artifact.cell["a"],
            artifact.cell["b"],
            artifact.cell["c"],
            artifact.cell["alpha"],
            artifact.cell["beta"],
            artifact.cell["gamma"],
        ),
        species=[{site.species: site.occupancy} for site in artifact.sites],
        coords=[site.fractional_position for site in artifact.sites],
        coords_are_cartesian=False,
        labels=[site.label for site in artifact.sites],
    )
    return str(CifWriter(structure, symprec=None, significant_figures=8))
```

Source: `pymatgen` official writer API and Phase 31 artifact contract.

### CrystalTextLLM-Style Material String

```python
def emit_crystaltextllm_material_string(artifact) -> str:
    lengths = " ".join(f"{artifact.cell[key]:.1f}" for key in ("a", "b", "c"))
    angles = " ".join(f"{int(round(artifact.cell[key]))}" for key in ("alpha", "beta", "gamma"))
    body = "\n".join(
        f"{site.species}\n"
        + " ".join(f"{coord:.2f}" for coord in site.fractional_position)
        for site in artifact.sites
    )
    return f"{lengths}\n{angles}\n{body}"
```

Source: CrystalTextLLM official `get_crystal_string` / `parse_fn`, minus its random translation augmentation.

### Fixture-Derived Example Body

```text
14.2 14.2 14.2
90 90 90
Al
0.12 0.25 0.38
Cu
0.42 0.55 0.68
Fe
0.72 0.85 0.12
```

Source: repo fixture `al_cu_fe_periodic_candidate.json` formatted with the CrystalTextLLM line grammar.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Ad hoc notebook/manual CIF conversion | Repo-owned exporter over `TranslatedStructureArtifact` | Phase 31 -> Phase 32 boundary (2026-04-06) | Keeps export reproducible, typed, and testable. |
| Candidate-based export with hidden normalization | Artifact-first export with frozen fidelity/loss semantics | Phase 31 shipped on 2026-04-06 | Later exporter work cannot silently reinterpret QC-native structures. |
| Symmetry-inferred CIF as a default serialization path | `P 1` / direct-cell CIF that preserves artifact geometry | Supported by current `pymatgen` writer behavior in the local env | Avoids serializer-side lattice rewriting. |
| CSLLM symmetry/Wyckoff preprocessing as the first material-string target | CrystalTextLLM line-oriented body as the first target | CrystalTextLLM repo/paper 2024; CSLLM released code/README 2025 | Matches the repo’s shipped target name and avoids new symmetry inference work. |
| Training-time random unit-cell translation | Deterministic canonical fractional coordinates | CrystalTextLLM uses randomness only for augmentation, not for a repo audit trail | Repeated exports stay byte-stable. |

**Deprecated/outdated:**

- Notebook-only CIF export for translated candidates: Phase 32 should replace it with repo code.
- Using `build_pymatgen_structure(candidate)` as the exporter boundary: it is a backend helper, not the translation/export contract.
- Treating the CSLLM symmetry string as the default first target: it overreaches the data carried by the shipped Phase 31 artifact.

## Open Questions

1. **Should standalone CIF files mirror fidelity/loss metadata inside CIF comments, or should Phase 32 keep metadata only on the artifact wrapper?**
   - What we know: `TranslatedStructureArtifact` already carries `fidelity_tier`, `loss_reasons`, diagnostics, and source linkage. CrystalTextLLM-style material strings cannot safely take a metadata preamble.
   - What's unclear: Whether future external-model workflows want raw `.cif` files to carry a mirrored comment header in addition to the artifact metadata.
   - Recommendation: Keep Phase 32 `emitted_text` clean and artifact-backed. Decide comment/sidecar mirroring in Phase 33 when the file-backed CLI surface is designed.

2. **Should Phase 32 upgrade `pymatgen` to current PyPI latest before implementation?**
   - What we know: Installed `2025.10.7` already supports `Structure(labels=...)`, partial occupancies, and `CifWriter`.
   - What's unclear: Whether any post-`2025.10.7` CIF writer fixes matter for this exact exporter path.
   - Recommendation: Do not upgrade preemptively. Add exporter tests first; only bump if a concrete writer defect appears.

3. **Do we need a third repo fixture for the `approximate` tier?**
   - What we know: Phase 31 intentionally froze fixture coverage on the exact Al-Cu-Fe and lossy Sc-Zn boundary cases, while `approximate` is already covered in `test_llm_translation_core.py`.
   - What's unclear: Whether export semantics for `approximate` need a dedicated text golden file or only a semantic unit test.
   - Recommendation: Keep repo goldens on the exact and lossy fixture pair. Add one non-golden export test for the existing mixed-origin approximate candidate instead of adding a third fixture file now.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | exporter runtime | ✓ | `3.11.x` | — |
| `uv` | repo package/test execution | ✓ | `0.10.10` | `python -m pytest` only if env is already installed |
| `pytest` | validation lane | ✓ | `9.0.2` | — |
| `pymatgen` | CIF emission and CIF parse verification | ✓ | `2025.10.7` | None recommended |
| `ase` | not required for Phase 32 | ✗ | — | Not needed |

**Missing dependencies with no fallback:**

- None for the recommended Phase 32 approach.

**Missing dependencies with fallback:**

- `ase` is absent locally, but the recommended Phase 32 exporter path does not require it.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest 9.0.2` |
| Config file | `materials-discovery/pyproject.toml` |
| Quick run command | `cd materials-discovery && uv run pytest tests/test_llm_translation_exporters.py tests/test_llm_translation_fixtures.py tests/test_llm_translation_core.py -x` |
| Full suite command | `cd materials-discovery && uv run pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LLM-28 | Exporting the periodic Al-Cu-Fe fixture as CIF is byte-stable across repeated runs and reparses into the expected lattice/species/fractional positions. | unit + fixture regression | `cd materials-discovery && uv run pytest tests/test_llm_translation_exporters.py::test_cif_export_is_stable_and_semantic_for_periodic_fixture -x` | ❌ Wave 0 |
| LLM-28 | Exporting the lossy Sc-Zn fixture as CIF preserves `lossy` metadata on the artifact while still emitting parseable periodic-proxy CIF text. | unit + fixture regression | `cd materials-discovery && uv run pytest tests/test_llm_translation_exporters.py::test_cif_export_keeps_lossy_metadata_for_qc_proxy_fixture -x` | ❌ Wave 0 |
| LLM-29 | Exporting the periodic Al-Cu-Fe fixture as a CrystalTextLLM material string is byte-stable and reparses with the same line grammar CrystalTextLLM uses. | unit + fixture regression | `cd materials-discovery && uv run pytest tests/test_llm_translation_exporters.py::test_material_string_export_matches_crystaltextllm_line_grammar -x` | ❌ Wave 0 |
| LLM-29 | Exporting the lossy Sc-Zn fixture as a material string keeps fidelity/loss semantics on the artifact and does not inject metadata lines that break parsing. | unit + fixture regression | `cd materials-discovery && uv run pytest tests/test_llm_translation_exporters.py::test_material_string_export_stays_parseable_for_lossy_proxy_fixture -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `cd materials-discovery && uv run pytest tests/test_llm_translation_exporters.py -x`
- **Per wave merge:** `cd materials-discovery && uv run pytest tests/test_llm_translation_schema.py tests/test_llm_translation_core.py tests/test_llm_translation_fixtures.py tests/test_llm_translation_exporters.py -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `materials-discovery/tests/test_llm_translation_exporters.py` — exporter dispatch, CIF semantics, material-string semantics, byte-stability, and failure-path coverage for `LLM-28` / `LLM-29`
- [ ] `materials-discovery/tests/fixtures/llm_translation_exports/al_cu_fe_periodic.cif` — representative exact CIF golden
- [ ] `materials-discovery/tests/fixtures/llm_translation_exports/al_cu_fe_periodic.material.txt` — representative exact CrystalTextLLM-body golden
- [ ] `materials-discovery/tests/fixtures/llm_translation_exports/sc_zn_qc_proxy.cif` — representative lossy periodic-proxy CIF golden
- [ ] `materials-discovery/tests/fixtures/llm_translation_exports/sc_zn_qc_proxy.material.txt` — representative lossy periodic-proxy material-string golden

## Sources

### Primary (HIGH confidence)

- Local repo: `materials-discovery/src/materials_discovery/llm/schema.py` — built-in translation target names, `emitted_text`, fidelity/loss contract
- Local repo: `materials-discovery/src/materials_discovery/llm/translation.py` — normalized artifact seam and fidelity classification
- Local repo: `materials-discovery/src/materials_discovery/backends/structure_realization.py` — current coordinate and structure-realization helpers
- Local repo: `materials-discovery/developers-docs/llm-translation-contract.md` — explicit Phase 32 handoff guidance
- Local repo: `materials-discovery/tests/test_llm_translation_schema.py`, `test_llm_translation_core.py`, `test_llm_translation_fixtures.py` — current regression boundaries
- Local repo: `materials-discovery/pyproject.toml` and `materials-discovery/uv.lock` — existing dependency surface and pytest config
- CrystalTextLLM official repo: `https://raw.githubusercontent.com/facebookresearch/crystal-text-llm/main/llama_finetune.py` — `get_crystal_string` line grammar and training-time random translation
- CrystalTextLLM official repo: `https://raw.githubusercontent.com/facebookresearch/crystal-text-llm/main/llama_sample.py` — `parse_fn` showing the expected material-string parse contract
- CSLLM official repo: `https://raw.githubusercontent.com/szl666/CSLLM/main/material_str.py` — symmetry/Wyckoff-based structure string that would require new inference
- CSLLM official repo: `https://raw.githubusercontent.com/szl666/CSLLM/main/README.md` — current project scope around CIF/POSCAR ingestion and synthesizability tasks
- `pymatgen` official source: `https://raw.githubusercontent.com/materialsproject/pymatgen/master/src/pymatgen/io/cif.py` — CIF file comments/parsing behavior
- PyPI registry: `https://pypi.org/pypi/pymatgen/json`, `https://pypi.org/pypi/pytest/json`, `https://pypi.org/pypi/pydantic/json` — current package versions and publish dates

### Secondary (MEDIUM confidence)

- None needed. The key claims above were verified directly from repo code, official upstream code, local environment inspection, and the package registry.

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - driven by current repo modules, installed environment checks, and official upstream formatter/writer code.
- Architecture: HIGH - the Phase 31 contract already freezes the exporter seam, and the remaining design choice is a narrow serialization layer.
- Pitfalls: MEDIUM-HIGH - symmetry-refined CIF drift and CrystalTextLLM augmentation risks were reproduced locally, but future `pymatgen` behavior can still move between releases.

**Research date:** 2026-04-06
**Valid until:** 2026-05-06
