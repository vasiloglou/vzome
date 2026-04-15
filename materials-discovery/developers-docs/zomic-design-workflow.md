# Zomic Design Workflow

This workflow lets you author candidate motifs in vZome's `Zomic` language and feed
them directly into the `materials-discovery` generator.

The bridge has three layers:

1. A `Zomic` script defines the exact geometric construction in the golden field.
2. `vZome core` compiles and executes the script, then exports labeled site positions.
3. `materials-discovery` embeds those labeled sites into a crystallographic cell and
   writes the same orbit-library JSON format used by anchored prototypes.

## When to Use It

Use the Zomic path when you want:

- author-controlled motif geometry rather than a built-in prototype library
- exact vZome construction semantics for visualization and design iteration
- a design language that can later be rendered in the native vZome toolchain

Use the existing orbit-library JSON path when you already have a fixed CIF-derived
prototype and do not need procedural construction.

## CLI Entry Points

Two commands now support the Zomic-authored path:

```bash
cd materials-discovery
uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
uv run mdisc generate --config configs/systems/sc_zn_zomic.yaml --count 32
```

`export-zomic` writes an orbit-library JSON file. `generate` can call the same bridge
automatically when the system config sets `zomic_design`.

For the repo-owned preview path over the checked raw export, see
[Programmatic Zomic Visualization](programmatic-zomic-visualization.md). That
surface adds `uv run mdisc preview-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml`
without changing the existing export contract.

## Design Contract

### 1. Labels define atomic sites

Only labeled VM locations become candidate sites. Struts and unlabeled path points are
exported for visualization, but they are not converted into atomic sites.

That means the script author controls site selection explicitly:

```zomic
label pent.top.center
short blue -12
label pent.top.left
```

### 2. Label prefixes define orbit names

Orbit grouping is derived from the label string:

- `pent.top.center` -> orbit `pent`
- `joint.bottom.left` -> orbit `joint`
- `green_0` -> orbit `green`

If a label contains `.` the prefix before the first dot is used.
If a label ends in `_<digits>`, the prefix before the numeric suffix is used.
Otherwise the full label becomes the orbit name.

### 3. The design YAML provides the crystallographic embedding

Zomic coordinates are exact, but they are not a crystal cell by themselves. The design
YAML provides:

- `base_cell`
- `motif_center`
- `translation_divisor`, `radial_scale`, `tangential_scale`
- `reference_axes`
- `minimum_site_separation`
- optional `preferred_species_by_orbit`

The bridge centers the labeled Zomic points, scales them into the specified cell, and
writes fractional positions to an orbit-library JSON file.

If `anchor_prototype` is set, the bridge then snaps the embedded Zomic points onto the
nearest unique sites from that crystallographic orbit library. This is the recommended
path for real/native execution because it keeps the Zomic-authored orbit intent while
starting from physically anchored positions.

If `anchor_orbit_strategy: seed_orbit_expand` is also set, those snapped seed sites are
used to choose a fuller set of anchor orbits. The bridge then emits the full anchor
orbit sites, not just the reduced labeled subset from the original Zomic script.

## Example Design YAML

The repository ships a working example at
`materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml`.

```yaml
zomic_file: sc_zn_tsai_bridge.zomic
prototype_key: sc_zn_tsai_bridge
system_name: Sc-Zn
template_family: cubic_proxy_1_0
reference: Zomic-authored Tsai-inspired cluster sketch
base_cell:
  a: 13.7923
  b: 13.7923
  c: 13.7923
  alpha: 90.0
  beta: 90.0
  gamma: 90.0
motif_center: [0.5, 0.5, 0.5]
translation_divisor: 10.0
radial_scale: 0.012
tangential_scale: 0.026
reference_axes:
  - [1.0, 0.0, 0.0]
  - [0.0, 1.0, 0.0]
  - [0.0, 0.0, 1.0]
minimum_site_separation: 0.1
preferred_species_by_orbit:
  pent: [Sc, Zn]
  frustum: [Zn, Sc]
  joint: [Zn]
embedding_fraction: 0.68
anchor_prototype: ../../data/prototypes/sc_zn_tsai_sczn6.json
anchor_orbit_strategy: seed_orbit_expand
anchor_site_target: 100
anchor_orbit_min_votes: 2
export_path: ../../data/prototypes/generated/sc_zn_tsai_bridge.json
raw_export_path: ../../data/prototypes/generated/sc_zn_tsai_bridge.raw.json
```

## System Config Integration

The system YAML can point at the design directly:

```yaml
system_name: Sc-Zn
template_family: cubic_proxy_1_0
species: [Sc, Zn]
composition_bounds:
  Sc: {min: 0.15, max: 0.40}
  Zn: {min: 0.60, max: 0.85}
coeff_bounds: {min: -2, max: 2}
seed: 31
default_count: 64
zomic_design: designs/zomic/sc_zn_tsai_bridge.yaml
```

At generate time the pipeline will:

1. export the Zomic design if the raw export or orbit library is stale
2. anchor-fit the exported geometry if `anchor_prototype` is configured
3. optionally expand the seed-matched anchor orbits if `anchor_orbit_strategy` is set
4. load the generated orbit library
5. decorate the exported orbits with chemistry and candidate-specific `QPhiCoord`
6. continue through the normal screening and validation stages, including the
   cheap real/native geometry prefilter before phonon

## Artifacts

The bridge writes two files:

- `data/prototypes/generated/*.raw.json`
  Raw labeled geometry emitted by `vZome core`
- `data/prototypes/generated/*.json`
  Orbit-library JSON consumed by `materials_discovery.generator.approximant_templates`

The raw JSON includes labeled points and segments. The orbit-library JSON is the stable
input to the generator.

## Runtime Requirements

The export path invokes:

```bash
./gradlew -q :core:zomicExport -PzomicFile=... -PzomicOut=...
```

So a local Java runtime is required for:

- `mdisc export-zomic`
- `mdisc generate` when `zomic_design` is set

If Java is missing, the bridge fails explicitly instead of silently falling back to the
generic templates.

## Current Limitation

This bridge is already better than the old heuristic coordinate placement, but it is
still an embedding step:

- Zomic gives exact geometric construction.
- The design YAML still chooses the crystal cell and embedding scale.

So this is not yet a fully direct `Zomic -> crystallographic symmetry orbit` compiler.
It is a controlled authoring bridge, optionally tightened by snapping onto an anchored
orbit library and optionally expanded into a fuller anchored orbit set.

---

## LLM-Generated Zomic (Planned)

The Zomic bridge will gain a new design source: LLM-generated Zomic scripts. Instead
of hand-authoring `.zomic` files, a fine-tuned LLM generates Zomic conditioned on
composition constraints and target properties.

### How It Connects

```
LLM generates Zomic text
    |
    v
ANTLR4 parse validation (rejects invalid syntax)
    |
    v
vZome core compiles (same as hand-authored Zomic)
    |
    v
Zomic bridge embeds into crystal cell (same pipeline)
    |
    v
CandidateRecord → screen → validate → rank
```

The key insight is that the entire downstream pipeline is unchanged. The only
difference is the origin of the `.zomic` text: human author vs. LLM.

### Why Zomic for LLMs

Standard crystal-generating LLMs (CrystaLLM, CrystalTextLLM) generate CIF text,
which relies on periodic boundary conditions. CIF cannot represent quasicrystals.
Zomic operates natively in the golden field Z[phi]³, making it the first text-based
representation that allows an LLM to generate true quasicrystal-compatible structures.

See [LLM Integration](llm-integration.md) for the full architecture and training plan.

---

## Reverse Engineering Zomic from Candidates (Planned)

To build the LLM training corpus, pipeline-generated CandidateRecords can be
reverse-engineered into Zomic scripts via a `record2zomic` converter:

1. Group sites by orbit label
2. For each site, compute displacement from origin as a Z[phi]³ vector
3. Decompose the displacement into a sequence of Zomic strut moves (greedy search
   over the 62 axis directions × available sizes)
4. Wrap each orbit in `branch { label ... strut ... }` structure
5. Post-process: merge consecutive same-axis struts, identify `repeat`/`symmetry`
   patterns

This produces Zomic scripts that round-trip through the bridge to reproduce the
original candidate geometry (within `minimum_site_separation` tolerance).

---

## CIF-to-Zomic Conversion (Planned)

A `cif2zomic` converter will allow importing approximant crystal structures from
external databases (HYPOD-X, ICSD, Materials Project) into the Zomic training corpus:

1. Parse CIF with pymatgen → Cartesian atomic positions
2. Map each position to the nearest Z[phi]³ point using continued-fraction
   expansion in phi
3. Group by Wyckoff site → orbit labels
4. Generate Zomic via the same strut decomposition as `record2zomic`
5. Generate a companion design YAML with cell parameters from the CIF

This conversion is approximate (periodic Cartesian → Z[phi] mapping introduces small
errors) but sufficient for LLM training data. The trained LLM will learn to generate
structures that are more natively quasicrystal-compatible than their CIF origins.

See [Zomic LLM Data Plan](zomic-llm-data-plan.md) for the full data pipeline.

## Source References

- `core/src/main/java/com/vzome/core/apps/ExportZomicLabeledGeometry.java`
- `core/build.gradle`
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`
- `materials-discovery/src/materials_discovery/generator/candidate_factory.py`
- `materials-discovery/configs/systems/sc_zn_zomic.yaml`
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml`
