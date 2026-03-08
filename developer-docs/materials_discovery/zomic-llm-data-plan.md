# Zomic LLM Data Collection & Conversion Plan

This document details the strategy for building a training corpus to fine-tune an LLM
on the Zomic language for quasicrystal-compatible structure generation.

---

## 1. Existing Zomic Data Inventory

### 1.1 Regression Test Scripts

**Location:** `core/src/regression/files/Zomic/`

~100 directories, each containing one or more `.zomic` files. These cover a wide range
of geometric constructions:

| Category | Examples | Count (est.) |
|---|---|---|
| Polyhedral shells | 121zoneBall, 600cell, buckyball, icosidodecahedron | ~20 |
| Fullerene / molecular | C240, C60, nanotube, buckyTube | ~10 |
| Lattice / crystal-like | diamond, diamondLattice, bodycenteredcubic | ~10 |
| Symmetry demonstrations | blueSymmetry, fiveSymmetry, rotationalPenta | ~15 |
| Spiral / helical | archimedesSpiral, DNA_double_helix | ~5 |
| Complex constructions | zonoBall, rhombicTriacontahedron, stellatedDodecahedron | ~15 |
| Miscellaneous | greenLines, halfBlue, purpleStruts, labels | ~25 |

**Quality:** High. These are curated test cases that exercise all Zomic language
features. Each has been validated by the ANTLR4 parser and vZome compiler.

**Limitations:** Most describe geometric objects, not crystallographic structures with
labeled atomic sites. They teach Zomic syntax and geometry but not materials-specific
patterns.

### 1.2 Part Definition Scripts

**Location:** `core/src/main/resources/com/vzome/core/parts/`

`.zomic` files defining strut geometries for the Zometool system. These are simple,
repetitive constructions but demonstrate correct axis/size usage patterns.

**Count:** ~30 files
**Quality:** Production code — guaranteed correct.

### 1.3 Materials Discovery Designs

**Location:** `materials-discovery/designs/zomic/`

Currently one example:

- `sc_zn_tsai_bridge.zomic` — Tsai-inspired cluster sketch with labeled atomic sites
  (pent, frustum, joint orbits)

**Quality:** This is the gold standard for what LLM-generated Zomic should look like.
It demonstrates the label convention and the design-YAML embedding workflow.

**Count:** 1 (will grow as more systems get Zomic designs)

### Total Existing Zomic: ~130-150 scripts

---

## 2. Data Sources Requiring Conversion

### 2.1 Pipeline-Generated Candidates → Zomic (`record2zomic`)

**Source:** CandidateRecord JSONL files from `mdisc generate` runs.

Each CandidateRecord contains:
- `sites`: list of `SiteRecord` with `qphi_coord` (three (a,b) pairs in Z[phi])
- `species`: element assignment per site
- `orbit`: orbit grouping per site
- `composition`: overall composition dict

**Conversion strategy:**

Given a set of QPhiCoord sites, reverse-engineer a Zomic construction sequence:

1. Start at origin
2. For each site (sorted by orbit, then by distance from origin):
   a. Compute the displacement vector from current position to target site
   b. Decompose the displacement into a sequence of Zomic strut moves
   c. The decomposition uses the 31 icosahedral axis directions (6 red, 10 yellow,
      15 blue) plus green/orange/purple
   d. Add a `label` statement for the site
   e. Use `branch` to return to origin between orbits

**Challenges:**
- Not every Z[phi]³ vector decomposes cleanly into a short sequence of struts
- Some coordinates may require `move` sequences (no struts, just position changes)
- The resulting Zomic may be verbose compared to hand-authored designs

**Mitigation:**
- Accept longer scripts (LLM training can handle verbosity)
- Implement a greedy decomposition: find the largest single strut that gets closest,
  then recurse on the remainder
- Post-process to simplify: merge consecutive struts on the same axis, wrap repeated
  patterns in `repeat` or `symmetry` blocks

**Estimated yield:** 1,000-10,000 examples from existing pipeline runs across
Al-Cu-Fe, Al-Pd-Mn, and Sc-Zn systems.

### 2.2 HYPOD-X Approximant Structures → Zomic (`cif2zomic`)

**Source:** [HYPOD-X dataset](https://figshare.com/articles/dataset/HYPOD_comprehensive_experimental_datasets_of_quasicrystals_and_their_approximants/25650705)

Contains compositions and phase data for ~1000 quasicrystals and their approximants.
Many approximant entries include CIF files or crystallographic coordinates.

**Conversion strategy:**

1. Download HYPOD-X dataset from Figshare
2. Extract CIF files for approximant phases (true QCs lack CIFs)
3. For each CIF:
   a. Parse with pymatgen to get atomic positions in Cartesian coordinates
   b. Identify the closest Z[phi]³ lattice points for each atom position
   c. Group atoms into orbits (by Wyckoff site or symmetry equivalence)
   d. Generate Zomic script using the `record2zomic` converter
   e. Annotate with composition and known properties

**Challenges:**
- Approximant coordinates are periodic Cartesian → mapping to Z[phi]³ is approximate
- Large unit cells (100+ atoms) may produce unwieldy Zomic scripts
- Some CIFs may have partial occupancy or disorder

**Mitigation:**
- Filter for structures with <50 unique sites (manageable Zomic length)
- Use the existing `anchor_prototype` snapping to find nearest Z[phi] positions
- Treat partial occupancy as composition variance in the training data

**Estimated yield:** ~200-500 examples (after filtering for quality and size).

### 2.3 ICSD Approximant Structures → Zomic

**Source:** [ICSD](https://icsd.products.fiz-karlsruhe.de/) (licensed database)

Contains periodic approximant crystals for known QC families:
- Al-Cu-Fe (i-phase approximants)
- Al-Pd-Mn (xi-prime and related)
- Sc-Zn (Tsai-type approximants)
- Al-Mn-Si, Al-Co-Ni, etc.

**Conversion:** Same `cif2zomic` pipeline as HYPOD-X.

**Estimated yield:** ~100-200 examples.

**Note:** ICSD requires institutional license. Use Materials Project or COD (Crystallography Open Database) for open-access alternatives.

### 2.4 PyQCstrc 6D → 3D Projections → Zomic

**Source:** [PyQCstrc](https://pmc.ncbi.nlm.nih.gov/articles/PMC8366420/) output

PyQCstrc can generate 3D atomic positions by projecting from 6D superspace models
of icosahedral quasicrystals. These are true quasicrystal positions, not periodic
approximants.

**Conversion strategy:**

1. Use PyQCstrc to generate 3D positions for known QC structure models
2. The positions are already in a coordinate system compatible with Z[phi]
3. Convert to Zomic using the `record2zomic` converter
4. These examples are especially valuable because they represent true QC geometry

**Estimated yield:** ~50-100 examples (limited by available PyQCstrc models).

### 2.5 vZome Model Files → Zomic

**Source:** `.vZome` files (XML format) from the vZome desktop application

vZome saves models as XML containing construction history. Some models were originally
built via Zomic; others were constructed interactively.

**Conversion strategy:**
- For models with Zomic history: extract the embedded Zomic script directly
- For interactive models: export labeled geometry and reverse-engineer via `record2zomic`

**Estimated yield:** ~50-100 examples.

---

## 3. Data Augmentation

Each source example can be augmented to increase the training corpus:

### 3.1 Symmetry Variants

Apply icosahedral symmetry operations to generate equivalent Zomic scripts:
- 60 orientations × 2 (with/without inversion) = 120 variants per structure
- Not all are meaningfully different for training — sample 5-10 per structure

### 3.2 Scale Variants

Adjust Zomic `scale` statements:
- Each structure can be inflated/deflated by powers of phi
- 3-5 scale variants per structure

### 3.3 Composition Variants

For materials-conditioned training:
- Vary element assignments while keeping geometry fixed
- E.g., Sc-Zn structure → try Al-Cu, Al-Mn, Ti-Ni assignments
- 3-10 composition variants per structure

### 3.4 Partial Constructions

Generate prefix sequences of Zomic scripts:
- For a 20-line Zomic script, create training examples from lines 1-5, 1-10, 1-15
- Teaches the LLM to complete partial structures
- 3-5 prefix variants per structure

### Augmentation Multiplier

Conservative estimate: **10x** augmentation over raw examples.

---

## 4. Corpus Size Estimates

| Source | Raw | After Augmentation |
|---|---|---|
| Existing Zomic scripts | 150 | 1,500 |
| Pipeline-generated candidates | 3,000 | 30,000 |
| HYPOD-X approximants | 300 | 3,000 |
| ICSD approximants | 150 | 1,500 |
| PyQCstrc projections | 75 | 750 |
| vZome exports | 75 | 750 |
| **Total** | **~3,750** | **~37,500** |

This is comparable to CrystalTextLLM's training set size (~45k CIF entries from
Materials Project). The key difference is that Zomic scripts are more compact and
structurally richer per example.

---

## 5. Quality Metrics for Training Data

Each training example must pass:

| Check | Tool | Threshold |
|---|---|---|
| Zomic syntax validity | ANTLR4 parser | Must parse without errors |
| Geometric validity | vZome compiler | Must compile without runtime errors |
| No atom collisions | `minimum_site_separation` check | Distance > 0.1 Å between any pair |
| Label consistency | Orbit extraction | All labeled sites have valid orbit prefixes |
| Reasonable structure size | Site count | 4-200 labeled sites |
| Composition validity | Element check | All species are supported elements |

Examples failing any check are excluded from training but logged for debugging.

---

## 6. Converter Specifications

### 6.1 `record2zomic` — CandidateRecord → Zomic Script

**Input:** CandidateRecord (from JSONL)
**Output:** Zomic script text

```python
def record_to_zomic(record: CandidateRecord) -> str:
    """Convert a CandidateRecord to a Zomic script.

    Strategy:
    1. Group sites by orbit
    2. For each orbit, compute displacement vectors from origin
    3. Decompose each displacement into strut sequences
    4. Wrap in branch/label statements
    """
```

**Decomposition algorithm:**

Given a target QPhiCoord `(a1+b1*phi, a2+b2*phi, a3+b3*phi)`:

1. Map the target to the nearest point reachable by a sequence of Zomic struts
2. Use a greedy search over the 62 axis directions (31 axes × 2 signs):
   - For each axis, compute the strut vector at each size (-3 to +7)
   - Select the strut that minimizes remaining distance to target
   - Subtract the strut vector, recurse on remainder
3. Terminate when remaining distance is below `minimum_site_separation`
4. Output the strut sequence as Zomic text

### 6.2 `cif2zomic` — CIF → Zomic Script

**Input:** CIF file path
**Output:** Zomic script text + design YAML

```python
def cif_to_zomic(cif_path: str) -> tuple[str, dict]:
    """Convert a CIF file to Zomic script and design YAML.

    Strategy:
    1. Parse CIF with pymatgen
    2. Extract unique Wyckoff sites
    3. Map Cartesian positions to nearest Z[phi] coordinates
    4. Generate Zomic via record2zomic
    5. Generate design YAML with cell parameters
    """
```

**Coordinate mapping:**

CIF positions are in fractional coordinates relative to a periodic cell. To map to
Z[phi]:

1. Convert fractional → Cartesian using cell parameters
2. For each Cartesian position `(x, y, z)`:
   a. Find the Z[phi] point `(a+b*phi)` closest to each coordinate
   b. Use continued-fraction expansion in phi to find best `(a, b)` pairs
   c. Accept if the error `|x - (a + b*phi)|` < tolerance (0.05 Å)
3. Positions that don't map cleanly to Z[phi] get the nearest approximation

### 6.3 `projection2zomic` — PyQCstrc 3D Projection → Zomic

**Input:** PyQCstrc output (list of 3D positions from 6D projection)
**Output:** Zomic script text

This is a variant of `record2zomic` where positions are already in a phi-compatible
coordinate system, so the Z[phi] mapping step is more reliable.

---

## 7. Training Infrastructure

### 7.1 Hardware Requirements

| Phase | GPU | Time (est.) |
|---|---|---|
| Phase 1: Zomic proficiency (150 examples, 10 epochs) | 1× A100 40GB | ~2 hours |
| Phase 1: Zomic proficiency (1,500 augmented, 5 epochs) | 1× A100 40GB | ~8 hours |
| Phase 2: Materials conditioning (37,500 examples, 3 epochs) | 1× A100 80GB or 2× A100 40GB | ~24 hours |

QLoRA reduces memory requirements significantly — the base LLaMA-3 8B fits in 16GB
with 4-bit quantization, leaving room for the training batch.

### 7.2 Training Framework

- **HuggingFace Transformers + PEFT** for QLoRA fine-tuning
- **Weights & Biases** for experiment tracking
- **Custom evaluation harness** that:
  1. Generates N samples from the model
  2. Parses each with ANTLR4
  3. Compiles valid ones with vZome
  4. Runs through the screening pipeline
  5. Reports parse rate, compile rate, screen pass rate

### 7.3 Evaluation Pipeline

```
LLM generates N Zomic scripts
    |
    v
ANTLR4 parse check ──[fail]──> log & discard
    |
    [pass]
    v
vZome compile ──[fail]──> log & discard
    |
    [pass]
    v
Collision check ──[fail]──> log & discard
    |
    [pass]
    v
Zomic bridge → CandidateRecord
    |
    v
mdisc screen (fast MLIP)
    |
    ├── [fail] → log
    └── [pass] → mdisc hifi-validate → report metrics
```

---

## 8. Data Pipeline Implementation Order

### Step 1: Inventory existing Zomic (1 day)
- Glob all `.zomic` files in the repository
- Parse each with ANTLR4 to verify syntax
- Categorize by type (geometric, crystallographic, part)
- Write manifest of usable training data

### Step 2: Build `record2zomic` converter (3-5 days)
- Implement QPhiCoord → strut sequence decomposition
- Implement orbit grouping → Zomic branch/label structure
- Test with Sc-Zn pipeline candidates (round-trip: generate → record2zomic → parse)
- Validate round-trip fidelity (does the regenerated structure match?)

### Step 3: Generate pipeline training data (2-3 days)
- Run `mdisc generate --count 10000` for all three systems
- Run `mdisc screen` and `mdisc hifi-validate` on top candidates
- Convert all CandidateRecords to Zomic via `record2zomic`
- Pair with validation results for materials-conditioned examples

### Step 4: Build `cif2zomic` converter (3-5 days)
- Implement CIF → Cartesian → Z[phi] coordinate mapping
- Implement Wyckoff site → orbit label mapping
- Test with known approximant CIFs (Al-Cu-Fe, Sc-Zn)
- Validate by comparing against hand-authored Zomic designs

### Step 5: Ingest external datasets (2-3 days)
- Download HYPOD-X from Figshare
- Extract approximant CIFs
- Convert via `cif2zomic`
- Quality-check and filter

### Step 6: Implement augmentation pipeline (2-3 days)
- Symmetry variant generation
- Scale variant generation
- Composition variant generation
- Partial construction generation

### Step 7: Assemble training corpus (1 day)
- Combine all sources
- Apply quality filters
- Split into train/validation/test (80/10/10)
- Write final training JSONL

**Total estimated timeline: 2-3 weeks** for data preparation before model training begins.
