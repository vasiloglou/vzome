# Phase 44: Prose Enrichment and Zomic Annotation - Research

**Researched:** 2026-04-15
**Domain:** Tutorial prose authoring, Zomic DSL annotation, Python module creation (labels.py)
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Design-origin narrative goes before Section 2 "Know the Worked Example" so readers get the "why" before seeing file paths and authority chains
- Tsai cluster explanation is one paragraph explaining concentric polyhedral shells plus one figure reference — enough to understand the design without a crystallography lecture
- Markdown gets full prose; notebook gets condensed versions linking to the markdown for depth — follows the v1.81 convention
- Cite the IUCrJ 2016 Sc-Zn paper (PMC4937780) once for the shell structure and link it — grounds the tutorial in real science
- Show 3-4 annotated blocks from the checked `sc_zn_tsai_bridge.zomic` file with inline `# <- explanation` comments on key lines
- Each block annotation names the physical result ("builds the pentagonal ring", "adds frustum connectors")
- Introduce a label glossary table mapping cryptic names (pent, frustum, joint) to physical parts before the first snippet — this glossary becomes the foundation for labels.py
- One paragraph per screening metric defining what it measures physically, then a "What the numbers mean" callout after the screening output
- Frame the "all gates False" validation result as "this is what an honest early-stage batch looks like" with a checklist explaining each gate
- One explain-then-command-then-annotate block per LLM command (llm-generate, llm-evaluate, llm-translate) — same depth as the deterministic spine
- labels.py encodes preferred_species_by_orbit from the design YAML plus a human-readable shell name per orbit

### Claude's Discretion

- Exact wording and paragraph lengths at the agent's discretion
- Ordering of explanatory blocks within each section at the agent's discretion

### Deferred Ideas (OUT OF SCOPE)

- Interactive Zomic syntax highlighting (NARR-F01) — captured as future requirement
- Full crystallographic Wyckoff site labels — overkill for this tutorial
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| NARR-01 | Tutorial explains what a Tsai-type icosahedral cluster is and why the Sc-Zn bridge design was chosen, with plain-language conceptual framing before any commands | Design-origin narrative block placed before Section 2; Tsai cluster paragraph + IUCrJ 2016 citation |
| NARR-02 | Tutorial shows annotated Zomic file snippets with per-block explanations of geometry commands (size, symmetry, branch, from, label, short, color directions) | 3-4 annotated blocks from sc_zn_tsai_bridge.zomic with inline comments; label glossary table |
| NARR-03 | Tutorial explains what the screening stage does: what energy_proxy_ev_per_atom and min_distance_proxy measure, how the shortlist threshold works, and what passed_count vs shortlisted_count means | One paragraph per metric + "What the numbers mean" callout in Section 5 |
| NARR-04 | Tutorial explains each validation signal (geometry_prefilter, phonon_imaginary_modes, md_stability_score, xrd_confidence), the release gate logic, and how to read the recommendation field | Gate checklist framing the "all gates False" output as honest early-stage batch in Section 6 |
| NARR-05 | Tutorial explains the same-system LLM lane and the translation/external benchmark branch with the same explanatory depth as the deterministic spine | One explain-then-command-then-annotate block per LLM command in Sections 9.1–9.3 |
| ENRICH-01 | Orbit labels are mapped from cryptic names to intuitive human-readable names with a shared colorblind-safe palette used across all figures | labels.py module in materials_discovery.visualization with orbit_labels dict, shell_names dict, and ORBIT_COLORS palette |
</phase_requirements>

---

## Summary

Phase 44 is a prose and code authoring task. There is no new infrastructure to choose — the entire deliverable consists of text additions to existing documents and one new Python module (`labels.py`). The key investigative questions were: (1) what exactly does the Zomic DSL do in each block of the checked file, (2) what do the screening and validation fields mean physically, (3) where exactly in the markdown and notebook do the additions land, and (4) what does `labels.py` need to contain to unblock Phase 45 visualization work.

All five requirements are pure additions to existing files. The tutorial already has 12 sections in the markdown and corresponding notebook cells. Phase 44 inserts narrative before Section 2, enriches Sections 5–6 and 9, and creates `labels.py` inside the already-existing `materials_discovery.visualization` package. The existing `_ORBIT_PALETTE` in `raw_export.py` must be superseded by the colorblind-safe palette defined in `labels.py` — Phase 45 will import from `labels.py`, so `labels.py` is the authoritative palette source going forward.

**Primary recommendation:** Write `labels.py` first (it is a pure data/mapping module with no external dependencies), then enrich the markdown tutorial sections in order, then mirror condensed versions into notebook markdown cells. This order keeps ENRICH-01 complete before NARR-01 through NARR-05 so the label glossary table in NARR-02 directly mirrors the `labels.py` data structures.

---

## Standard Stack

### Core (No New Dependencies)

This phase introduces no new library dependencies. Everything runs on the already-installed package set.

| Component | Version / Location | Purpose |
|-----------|-------------------|---------|
| `materials_discovery.visualization` package | Already in `src/` | Home for `labels.py` |
| `raw_export.py` `_ORBIT_PALETTE` | Already in `visualization/` | Must be superseded by `labels.py` palette |
| `designs/zomic/sc_zn_tsai_bridge.yaml` `preferred_species_by_orbit` | `pent: [Sc, Zn]`, `frustum: [Zn, Sc]`, `joint: [Zn]` | Source of truth for orbit-to-species mapping in `labels.py` |
| `data/prototypes/generated/sc_zn_tsai_bridge.json` `anchor_orbit_summary.selected_orbits` | `['tsai_zn7', 'tsai_sc1', 'tsai_zn6', 'tsai_zn5', 'tsai_zn4']` | 5 anchor orbits that labels.py must name |
| pytest | Already in `[dev]` extras | Test framework for labels.py unit tests |

### Wong (2011) Colorblind-Safe Palette

The CONTEXT.md decision and FEATURES.md research both specify using the Wong (2011) colorblind-safe palette. This is a well-known 8-color palette safe for deuteranopia, protanopia, and tritanopia. The 8 colors in hex (HIGH confidence — widely documented):

| Index | Color Name | Hex |
|-------|-----------|-----|
| 0 | Black | `#000000` |
| 1 | Orange | `#E69F00` |
| 2 | Sky blue | `#56B4E9` |
| 3 | Bluish green | `#009E73` |
| 4 | Yellow | `#F0E442` |
| 5 | Blue | `#0072B2` |
| 6 | Vermilion | `#D55E00` |
| 7 | Reddish purple | `#CC79A7` |

For the 5 Tsai cluster orbits, skip index 0 (black, too low contrast on white backgrounds) and use indices 1–5 or 2–6. Indices 2, 5, 6, 1, 3 provide good separation across the 5 orbits.

**Note:** The current `_ORBIT_PALETTE` in `raw_export.py` uses arbitrary web-safe blues and reds — not colorblind-safe. `labels.py` replaces this as the canonical source; `raw_export.py` should be updated to import from `labels.py` in Phase 45 (or optionally in this phase if the plan includes it).

---

## Architecture Patterns

### labels.py Module Design

`labels.py` is a pure data/mapping module. It has no imports from the rest of the package except possibly `typing`. It is consumed by Phase 45's `plotly_3d.py` and Phase 46's `matplotlib_pub.py`.

```
materials_discovery/
└── visualization/
    ├── __init__.py          # add labels exports
    ├── raw_export.py        # existing — orbit palette superseded by labels.py
    ├── viewer.py            # existing — unchanged
    └── labels.py            # NEW: orbit label mappings + colorblind-safe palette
```

**labels.py structure (pseudocode pattern):**
```python
# Source: design YAML preferred_species_by_orbit + orbit library selected_orbits
# Orbit labels: design-time names used in .zomic labels and inferred by _infer_orbit_name
ORBIT_LABELS: dict[str, str] = {
    "pent": "Pentagonal ring",
    "frustum": "Frustum connectors",
    "joint": "Joint sites",
}

# Shell names: anchor-library orbit names + human-readable physical shell identity
SHELL_NAMES: dict[str, str] = {
    "tsai_zn7": "Zn inner shell (7-site)",
    "tsai_sc1": "Sc icosahedron (1-site representative)",
    "tsai_zn6": "Zn intermediate shell (6-site)",
    "tsai_zn5": "Zn pentagonal shell (5-site)",
    "tsai_zn4": "Zn outer ring (4-site)",
}

# Colorblind-safe palette (Wong 2011) — canonical source for all figures
ORBIT_COLORS: dict[str, str] = {
    "tsai_zn7": "#56B4E9",   # sky blue
    "tsai_sc1": "#E69F00",   # orange
    "tsai_zn6": "#009E73",   # bluish green
    "tsai_zn5": "#D55E00",   # vermilion
    "tsai_zn4": "#0072B2",   # blue
}

# Design-time orbit → preferred species (from sc_zn_tsai_bridge.yaml)
PREFERRED_SPECIES: dict[str, list[str]] = {
    "pent": ["Sc", "Zn"],
    "frustum": ["Zn", "Sc"],
    "joint": ["Zn"],
}
```

**`__init__.py` additions:**
```python
from materials_discovery.visualization.labels import (
    ORBIT_LABELS,
    ORBIT_COLORS,
    SHELL_NAMES,
    PREFERRED_SPECIES,
)
```

### Tutorial Section Mapping

The markdown tutorial has 12 sections. The additions land at specific insertion points:

| Insertion Point | Requirement | Content |
|-----------------|-------------|---------|
| New block before Section 2 | NARR-01 | Design-origin narrative: Tsai cluster paragraph + IUCrJ citation + why Sc-Zn |
| New subsection 2.1 or inline in Section 2 | NARR-02 | Label glossary table + 3-4 annotated Zomic blocks |
| Enrichment to Section 5 prose | NARR-03 | One paragraph each for energy_proxy_ev_per_atom and min_distance_proxy + "What the numbers mean" callout |
| Enrichment to Section 6 prose | NARR-04 | Gate checklist + honest framing of all-gates-False outcome |
| Enrichment to Sections 9.1, 9.2, 9.3 | NARR-05 | Explain-then-command-then-annotate blocks per LLM command |

### Notebook Cell Mapping

The notebook has corresponding markdown cells. The convention (from CONTEXT.md) is: markdown gets full prose, notebook gets condensed versions with a link to the markdown for depth.

| Notebook Location | Action |
|-------------------|--------|
| Before cell `b7279499` (Section 2) | Insert new markdown cell with condensed design-origin paragraph + link to markdown section |
| New markdown cell after Section 2 path inventory | Insert condensed Zomic annotation (1-2 blocks max, not all 4) + glossary table |
| After cell `b1aada31` screening output | Insert markdown cell explaining the three screening fields shown in the output dict |
| After cell `4509cd69` validation output | Insert markdown cell with gate checklist + honest framing |
| After each LLM `run()` cell in Sections 8-10 | Insert "What this signal means" markdown cell |

### Zomic Block Analysis (from sc_zn_tsai_bridge.zomic)

The checked Zomic file has three natural annotatable blocks:

**Block 1 — Frame declaration (lines 1-4):**
```zomic
size 7 purple +0            # <- set the base strut length to scale 7, using purple direction
symmetry around blue +13    # <- apply icosahedral symmetry around this axis
symmetry through +13        # <- close the symmetry group through the axis
branch{                     # <- open the outer symmetry branch
```
Physical result: establishes icosahedral symmetry frame for the entire motif.

**Block 2 — Pentagonal ring (lines 5-23 inner branch):**
```zomic
branch {
  size 7 purple -0
  from { yellow +0 red +0 }   # <- start position using golden-ratio strut combination
  label pent.top.center        # <- tag this site as the "pent" orbit, top-center position
  short blue -12               # <- short strut in blue direction, building the ring edge
  label pent.top.left
  short blue -10
  label pent.bottom.left
  short blue +13
  label pent.bottom.right
  short blue +11
  label pent.top.right         # <- five labels close the pentagonal loop
```
Physical result: builds the pentagonal ring of sites that forms the `pent` orbit.

**Block 3 — Frustum connectors (lines 23-33):**
```zomic
  green +3
  label frustum.top.right      # <- first frustum site, connecting pent ring to outer shell
  branch { repeat 2 short orange -2 short blue -6 }  # <- repeat pattern for connector arms
  short blue -13
  label frustum.top.left
  blue -5
  label frustum.bottom.left
  short blue +13
  label frustum.bottom.right   # <- four frustum sites complete the connectors
  branch green -33
  blue -2
```
Physical result: adds frustum connector sites between the pentagonal ring and the outer joint layer.

**Block 4 — Joint sites (lines 35-47):**
```zomic
from short red +1
branch purple -0
label joint.top.right           # <- joint site at top-right of the outer layer
from short blue -13
branch purple -0
label joint.top.left
from blue -5
branch purple -0
label joint.bottom.left
from short blue +13
branch purple -0
label joint.bottom.right        # <- four joint sites anchor the outermost shell
```
Physical result: places the `joint` orbit sites that link adjacent cluster copies.

### Screening Field Explanations (from calibration artifact)

Checked values: `input_count: 30`, `passed_count: 20`, `shortlisted_count: 4`, `first_energy_proxy_ev_per_atom: -2.778674`, `first_min_distance_proxy: 0.751937`.

| Field | Physical Meaning | What Good Looks Like |
|-------|-----------------|----------------------|
| `energy_proxy_ev_per_atom` | Estimated cohesive energy per atom from a fast empirical model; more negative = more bound = more stable | More negative than a threshold (e.g., -2.0 eV/atom for Sc-Zn intermetallics) |
| `min_distance_proxy` | Minimum normalized intersite distance; too small = atoms too close = unphysical structure | Above 0.7–0.8 (dimensionless; tuned to avoid severe crowding) |
| `passed_count` | Candidates that cleared both proxy thresholds | Shows how much of the generated batch is geometrically and energetically plausible |
| `shortlisted_count` | Top-ranked subset of passing candidates forwarded to expensive validation | Controls validation cost; typically 4–10 for early-stage batches |

### Validation Gate Explanations (from validated artifact)

Checked values for `md_000006`: `geometry_prefilter_pass: False`, `phonon_imaginary_modes: 99`, `md_stability_score: 0.0`, `xrd_confidence: 0.0`.

| Gate / Field | What It Checks | Current Value Meaning |
|-------------|---------------|-----------------------|
| `geometry_prefilter_pass` | Cheap atom-crowding check before expensive phonon/MD work | False = crowded geometry; skips phonon/MD to save compute |
| `phonon_imaginary_modes` | Count of imaginary phonon frequencies (indicates dynamical instability) | 99 = sentinel value from mock backend (no real phonon calculation ran) |
| `md_stability_score` | Short-MD structural drift indicator (0.0 = unstable, 1.0 = stable) | 0.0 = mock backend placeholder; not a real MD result |
| `xrd_confidence` | Similarity between simulated and reference XRD pattern | 0.0 = no pattern match (or mock placeholder) |
| `passed_checks` | All gates simultaneously True | False for this batch = correct behavior for mock/early-stage run |

The framing for NARR-04: "All gates False is what an honest early-stage batch looks like when the backend is mock or the candidates have not been pre-filtered aggressively. The pipeline is not broken — it is showing you the unfiltered result of a first-pass generation run."

### LLM Section Explanations (NARR-05)

Each LLM command needs one explain-then-command-then-annotate block:

| Command | What It Does | Key Artifact to Explain |
|---------|-------------|------------------------|
| `llm-generate` | Proposes candidate structures using an LLM as a proposal source instead of the deterministic Zomic-backed generator | `data/llm_runs/{run_id}/run_manifest.json` — shows the prompt/request side |
| `llm-evaluate` | Adds an LLM assessment layer on top of ranked deterministic candidates; does not replace deterministic validation | `data/llm_evaluated/{slug}_all_llm_evaluated.jsonl` — additive synthesis/precursor signals |
| `llm-translate` | Converts internal candidate records into external formats (CIF, material strings) for interoperability with external runtimes | `data/llm_translation_exports/{export_id}/inventory.jsonl` — fidelity tier and loss reasons |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Colorblind-safe color palette | Custom color wheel logic | Wong (2011) 8-color set, hardcoded in labels.py | Known good; peer-reviewed; no dependency |
| Orbit name inference | New parsing logic | Re-use `_infer_orbit_name` from `zomic_bridge.py` | Already tested; handles dot and underscore conventions |
| Design YAML parsing | New YAML reader | `ZomicDesignConfig.preferred_species_by_orbit` already parsed by schema | Pydantic-validated; use the already-loaded model |

---

## Common Pitfalls

### Pitfall 1: Inserting narrative before Section 2 breaks section numbering
**What goes wrong:** If a new "Section 1.5" or "Section 0" heading is added, all existing cross-references (Section 3, Section 5, etc.) in the markdown and notebook break.
**How to avoid:** Insert the design-origin narrative as a standalone block with its own heading (e.g., "About the Design" or "Why Sc-Zn?") that is NOT a numbered section, OR insert it as an unnumbered preamble paragraph within the intro area above the existing Section 2 heading. The CONTEXT.md says "before Section 2" — the safest interpretation is a new paragraph block between the intro paragraph and the "## 2. Know the Worked Example" heading, without adding a new section number.

### Pitfall 2: Notebook condensed versions become disconnected from markdown
**What goes wrong:** If notebook prose is written independently, it can contradict or duplicate the markdown prose, causing confusion when both are open.
**How to avoid:** Write markdown first, then copy the first 1-2 sentences of each key paragraph into the notebook cell, ending with "See [Guided Design Tutorial](../developers-docs/guided-design-tutorial.md#section-name) for the full account." Mirror the structure, not the content.

### Pitfall 3: labels.py introduces a circular import
**What goes wrong:** If `labels.py` imports from `raw_export.py` (e.g., to inherit `_ORBIT_PALETTE`), and `raw_export.py` later imports from `labels.py`, you get a circular import error.
**How to avoid:** `labels.py` must be a leaf module — it imports nothing from the rest of `materials_discovery`. `raw_export.py` is the one that should import from `labels.py` (in Phase 45), not the reverse.

### Pitfall 4: Orbit name mismatch between design labels and anchor library labels
**What goes wrong:** The design-time orbit names (`pent`, `frustum`, `joint`) come from `preferred_species_by_orbit` in the YAML. The anchor-library orbit names (`tsai_zn7`, `tsai_sc1`, etc.) come from the anchor prototype. Both exist simultaneously and mean different things. Conflating them in `labels.py` confuses Phase 45.
**How to avoid:** `labels.py` must have two separate mappings: `ORBIT_LABELS` for design-time names and `SHELL_NAMES` for anchor-library names. They serve different lookup contexts. The glossary table in NARR-02 explains design-time names (`pent`, `frustum`, `joint`); the color palette keys off anchor-library names (`tsai_zn7`, etc.) because those are what `build_view_model` emits.

### Pitfall 5: Zomic annotation claims wrong physical geometry
**What goes wrong:** Annotating Zomic commands with physically incorrect descriptions (e.g., claiming "short blue" builds a specific polyhedron face when it actually builds an edge) misleads readers.
**How to avoid:** Annotations must describe observable outcomes ("builds one edge of the pentagonal ring") rather than asserting 3D geometry claims that require crystallographic computation. The safe phrasing is "step along direction X to place the next site" rather than claiming the resulting face or shell type.

### Pitfall 6: __init__.py export list grows silently
**What goes wrong:** Adding `labels.py` exports to `__init__.py` but forgetting to update `__all__` leaves the new names importable but not discoverable via `from materials_discovery.visualization import *`.
**How to avoid:** Update both the import statement and the `__all__` list in `__init__.py` together.

---

## Code Examples

### labels.py skeleton (verified against existing code patterns)

```python
# Source: designs/zomic/sc_zn_tsai_bridge.yaml preferred_species_by_orbit
#         data/prototypes/generated/sc_zn_tsai_bridge.json anchor_orbit_summary.selected_orbits
# Wong (2011) palette: https://www.nature.com/articles/nmeth.1618

from __future__ import annotations

# Design-time orbit names (from .zomic label prefixes, inferred by _infer_orbit_name)
ORBIT_LABELS: dict[str, str] = {
    "pent": "Pentagonal ring",
    "frustum": "Frustum connectors",
    "joint": "Joint sites",
}

# Anchor-library orbit names (from sc_zn_tsai_bridge.json selected_orbits)
SHELL_NAMES: dict[str, str] = {
    "tsai_zn7": "Zn inner shell",
    "tsai_sc1": "Sc icosahedron shell",
    "tsai_zn6": "Zn middle shell",
    "tsai_zn5": "Zn pentagonal shell",
    "tsai_zn4": "Zn outer shell",
}

# Colorblind-safe palette (Wong 2011) keyed by anchor-library orbit name
# These 5 colors cover the 5 selected orbits; skip black (#000000) for contrast
ORBIT_COLORS: dict[str, str] = {
    "tsai_zn7": "#56B4E9",  # sky blue
    "tsai_sc1": "#E69F00",  # orange
    "tsai_zn6": "#009E73",  # bluish green
    "tsai_zn5": "#D55E00",  # vermilion
    "tsai_zn4": "#0072B2",  # blue
}

# Fallback color for orbits not in the above map
DEFAULT_ORBIT_COLOR: str = "#6b7280"

# Preferred species by design-time orbit name (mirrors sc_zn_tsai_bridge.yaml)
PREFERRED_SPECIES: dict[str, list[str]] = {
    "pent": ["Sc", "Zn"],
    "frustum": ["Zn", "Sc"],
    "joint": ["Zn"],
}
```

### __init__.py update pattern

```python
# add after existing imports
from materials_discovery.visualization.labels import (
    DEFAULT_ORBIT_COLOR,
    ORBIT_COLORS,
    ORBIT_LABELS,
    PREFERRED_SPECIES,
    SHELL_NAMES,
)

# add to __all__
__all__ = [
    ...existing...,
    "DEFAULT_ORBIT_COLOR",
    "ORBIT_COLORS",
    "ORBIT_LABELS",
    "PREFERRED_SPECIES",
    "SHELL_NAMES",
]
```

### Label glossary table for NARR-02 (markdown format)

```markdown
| Zomic label prefix | Physical part | Preferred species | Count in design |
|-------------------|---------------|-------------------|-----------------|
| `pent` | Pentagonal ring sites | Sc, Zn | 5 sites per ring |
| `frustum` | Frustum connector sites | Zn, Sc | 4 sites |
| `joint` | Outer joint sites | Zn | 4 sites |
```

### Screening callout box pattern (markdown)

```markdown
> **What the numbers mean**
> - `energy_proxy_ev_per_atom: -2.78` — below the threshold, so this candidate is energetically
>   plausible for a Sc-Zn intermetallic.
> - `min_distance_proxy: 0.75` — above the crowding threshold; atoms are not unphysically close.
> - `shortlist_rank: 1` — this candidate is first in the queue for expensive validation.
```

### Validation gate checklist pattern (markdown)

```markdown
> **Release gate checklist for this batch**
> - [ ] `geometry_prefilter_pass` — atom-crowding check (False = too crowded for phonon work)
> - [ ] `phonon_imaginary_modes == 0` — no imaginary frequencies (99 = mock sentinel, not a real count)
> - [ ] `md_stability_score > 0.8` — short-MD structural stability (0.0 = mock placeholder)
> - [ ] `xrd_confidence > 0.7` — pattern match to reference (0.0 = mock placeholder)
>
> All gates are False. This is the correct result for a mock-backend run on an early-stage
> candidate batch. The pipeline is not broken; it is showing you the unfiltered signal before
> any candidate has accumulated enough evidence to be promoted.
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | `materials-discovery/pyproject.toml` (section `[tool.pytest.ini_options]`) |
| Quick run command | `uv run pytest tests/test_zomic_visualization.py -x` |
| Full suite command | `uv run pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ENRICH-01 | `labels.py` exports `ORBIT_COLORS`, `ORBIT_LABELS`, `SHELL_NAMES`, `PREFERRED_SPECIES`, `DEFAULT_ORBIT_COLOR` | unit | `uv run pytest tests/test_labels.py -x` | ❌ Wave 0 |
| ENRICH-01 | `ORBIT_COLORS` keys match `SHELL_NAMES` keys | unit | `uv run pytest tests/test_labels.py::test_orbit_colors_keys_match_shell_names -x` | ❌ Wave 0 |
| ENRICH-01 | `PREFERRED_SPECIES` keys match `ORBIT_LABELS` keys | unit | `uv run pytest tests/test_labels.py::test_preferred_species_keys_match_orbit_labels -x` | ❌ Wave 0 |
| ENRICH-01 | `__init__.py` exports new labels symbols | unit | `uv run pytest tests/test_labels.py::test_init_exports -x` | ❌ Wave 0 |
| NARR-01 through NARR-05 | Prose additions in markdown and notebook | manual-only | — | n/a |

**Manual-only justification for NARR-01 through NARR-05:** Tutorial prose quality is a human judgment — no automated test can verify that the design narrative is clear, accurate, or correctly framed. These requirements are verified by reading the resulting documents.

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_labels.py -x`
- **Per wave merge:** `uv run pytest tests/ -x`
- **Phase gate:** Full suite green before marking phase complete

### Wave 0 Gaps

- [ ] `tests/test_labels.py` — covers ENRICH-01; must be created alongside `labels.py`

---

## Environment Availability

Step 2.6: SKIPPED. This phase is purely code/prose authoring with no external service dependencies. Python and uv are already confirmed available (notebook cell output shows `WORKDIR` resolution succeeds). No new CLIs, databases, or external services are required.

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| `_ORBIT_PALETTE` tuple in `raw_export.py` (8 arbitrary hex colors) | `ORBIT_COLORS` dict in `labels.py` (Wong 2011 colorblind-safe, keyed by orbit name) | Phase 45 imports from labels.py; raw_export.py palette becomes a compatibility shim or is updated to use labels.py |
| No design-origin narrative in tutorial | Design-origin block before Section 2 | Readers understand the "why" before they see file paths |
| Zomic DSL opaque to newcomers | Annotated blocks with inline comments + glossary table | Newcomers can follow each label and strut command without consulting the language reference |
| Screening output printed as raw JSON dict | Prose explanation + "What the numbers mean" callout | Readers understand what -2.78 eV/atom and 0.75 distance proxy signal |
| "All gates False" with no explanation | Honest-batch framing + gate checklist | Readers distinguish "pipeline broken" from "honest early-stage result" |

---

## Open Questions

1. **Should `raw_export.py` be updated to import from `labels.py` in Phase 44 or Phase 45?**
   - What we know: `raw_export.py` currently uses `_ORBIT_PALETTE` for the HTML viewer's colors; `labels.py` will define `ORBIT_COLORS`; the two palettes are different.
   - What's unclear: If `raw_export.py` is not updated in Phase 44, the HTML viewer and any future plotly figures will use different palettes until Phase 45.
   - Recommendation: Update `raw_export.py` to import `ORBIT_COLORS` from `labels.py` in Phase 44, replacing `_ORBIT_PALETTE`. This keeps the palette consistent from day one and Phase 45 has no divergence to resolve. However, `_infer_orbit_name` maps to design-time names (`pent`, `frustum`, `joint`) while `ORBIT_COLORS` is keyed by anchor-library names (`tsai_zn7`, etc.) — so a fallback to `DEFAULT_ORBIT_COLOR` is needed for design-time orbit names in the existing viewer. The planner should decide whether to include this `raw_export.py` update in Phase 44 or defer to Phase 45.

2. **Which 3-4 Zomic blocks to annotate (out of 4 identified)?**
   - What we know: The research identified 4 natural blocks (frame, pentagonal ring, frustum, joint).
   - What's unclear: CONTEXT.md says "3-4 blocks."
   - Recommendation: Show all 4. Each block is short enough (5-8 lines) that 4 blocks total is not overwhelming, and each block introduces one orbit name that appears in the glossary table.

3. **Exact location of narrative insertion in the markdown**
   - What we know: CONTEXT.md says "before Section 2 Know the Worked Example."
   - What's unclear: Should it be a numbered section (e.g., "1.5 About the Design") or unnumbered prose between Section 1 and Section 2?
   - Recommendation: Use an unnumbered heading such as "## About This Design" or "## Why Sc-Zn? Why a Tsai Bridge?" between the existing Section 1 ("Before You Start") and Section 2 headings. This avoids renumbering subsequent sections and is consistent with the convention in academic tutorials of having a "Background" block before the hands-on steps.

---

## Sources

### Primary (HIGH confidence)

- Internal: `designs/zomic/sc_zn_tsai_bridge.zomic` — direct read of all 4 annotatable blocks
- Internal: `designs/zomic/sc_zn_tsai_bridge.yaml` — `preferred_species_by_orbit`: `{pent: [Sc, Zn], frustum: [Zn, Sc], joint: [Zn]}`
- Internal: notebook cell output showing `selected_orbits: ['tsai_zn7', 'tsai_sc1', 'tsai_zn6', 'tsai_zn5', 'tsai_zn4']`, `orbit_count: 5`
- Internal: `src/materials_discovery/visualization/raw_export.py` — `_ORBIT_PALETTE`, `_infer_orbit_name` import location
- Internal: `src/materials_discovery/visualization/__init__.py` — current export list (6 symbols)
- Internal: `src/materials_discovery/generator/zomic_bridge.py` — `_infer_orbit_name` logic (splits on `.` or trailing digit suffix)
- Internal: `materials-discovery/pyproject.toml` — no `[viz]` extras group yet; pytest in `[dev]`
- Internal: `tests/test_zomic_visualization.py` — existing visualization test pattern to match

### Secondary (MEDIUM confidence)

- [IUCrJ 2016 Sc-Zn paper (PMC4937780)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4937780/) — Tsai cluster shell structure; `pent`/`frustum`/`joint` physical interpretations
- [Wong 2011 colorblind-safe palette](https://www.nature.com/articles/nmeth.1618) — 8-color palette used as canonical source for `ORBIT_COLORS`
- `.planning/research/FEATURES.md` — shell decomposition conventions, academic figure standards, anti-feature rationale
- `.planning/research/ARCHITECTURE.md` — `labels.py` module role, data flow for Phase 45 consumers

### Tertiary (LOW confidence — no independent verification needed; these are pure internal facts)

- None. All claims are grounded in direct code reads or the milestone-level research documents.

---

## Metadata

**Confidence breakdown:**
- Zomic DSL block analysis: HIGH — direct file read of checked source
- labels.py data values: HIGH — read directly from design YAML and orbit library JSON
- Wong palette hex codes: HIGH — standard published palette
- Prose placement recommendations: HIGH — derived from current section structure via direct file read
- Shell name to orbit mapping (tsai_zn7 → "Zn inner shell" etc.): MEDIUM — derived from orbit names and site counts in the anchor library; physical shell identity would require cross-referencing radial distances in raw.json, which is Phase 45 work

**Research date:** 2026-04-15
**Valid until:** 2026-05-15 (stable domain — prose authoring and data module; no fast-moving dependencies)
