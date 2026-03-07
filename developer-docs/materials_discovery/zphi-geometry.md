# Z[phi] Geometry for Candidate Generation

This document describes the Z[phi] (integers adjoined with the golden ratio) geometry
system used by the materials discovery pipeline to generate quasicrystalline
approximant candidate structures. For broader context on how the golden ratio
appears in icosahedral geometry, see section 10.8 of the
[vZome geometry tutorial](vzome-geometry-tutorial.md).

## Mathematical Foundation

### QPhiPair: Algebraic Numbers in Z[phi]

The ring Z[phi] consists of all numbers of the form `a + b * phi`, where `a` and `b`
are integers and `phi = (1 + sqrt(5)) / 2` is the golden ratio. In the codebase this
is represented by the type alias

```python
QPhiPair = tuple[int, int]
```

defined in `materials_discovery/common/schema.py`. A pair `(a, b)` encodes the value
`a + b * phi`. The constant `PHI` is computed as:

```python
PHI = (1.0 + 5.0**0.5) / 2.0
```

Conversion to a floating-point number is provided by `qphi_pair_to_float` in
`materials_discovery/common/coordinates.py`:

```python
def qphi_pair_to_float(pair: QPhiPair) -> float:
    return float(pair[0]) + float(pair[1]) * PHI
```

### QPhiCoord: 3D Points in Z[phi]^3

A three-dimensional point whose coordinates each lie in Z[phi] is represented as:

```python
QPhiCoord = tuple[QPhiPair, QPhiPair, QPhiPair]
```

Each component is an independent QPhiPair. Conversion to a floating-point 3-vector
is handled by `qphi_coord_to_float`, which applies `qphi_pair_to_float` to each
component.

### Multiplication by Powers of phi

The key algebraic identity is `phi^2 = phi + 1`. This means multiplying a Z[phi]
element by phi is a linear map on the integer coefficients:

```
(a + b * phi) * phi = b + (a + b) * phi
```

So the pair `(a, b)` maps to `(b, a + b)`. This is the forward step of the Fibonacci
recurrence. Division by phi (i.e., multiplication by `1/phi = phi - 1`) reverses it:

```
(a + b * phi) / phi = (b - a) + a * phi
```

The pair `(a, b)` maps to `(b - a, a)`.

The function `phi_scale_pair` in `zphi_geometry.py` implements this for an arbitrary
integer number of steps:

```python
def phi_scale_pair(pair: QPhiPair, steps: int) -> QPhiPair:
    a, b = pair
    if steps >= 0:
        for _ in range(steps):
            a, b = b, a + b
    else:
        for _ in range(-steps):
            a, b = b - a, a
    return (a, b)
```

`phi_scale_coord` applies this to all three pairs of a QPhiCoord.

## The Template System

### Generic Templates

Three built-in approximant templates are defined in
`materials_discovery/generator/approximant_templates.py`, stored in the module-level
dictionary `FAMILY_TEMPLATES`:

| Template name | Sites | Geometry | Cell parameters |
|---|---|---|---|
| `icosahedral_approximant_1_1` | 12 | Icosahedral shell vertices `(0, +/-1, +/-phi)` and cyclic permutations, normalized, at radius 0.235 from center | a = b = c = 14.2 angstrom |
| `decagonal_proxy_2_1` | 10 | Two pentagonal rings of 5 sites each (z=0.34 and z=0.66, second ring phase-offset by pi/5), radius 0.24 | a = b = 11.8, c = 16.0 angstrom |
| `cubic_proxy_1_0` | 8 | Cube corners at fractional position 0.29 from edges (i.e., coordinates at 0.29 and 0.71) | a = b = c = 10.0 angstrom |

All generic templates use motif center `(0.5, 0.5, 0.5)` and orthogonal cell angles
(alpha = beta = gamma = 90 degrees).

### System-Anchored Orbit Libraries

For specific alloy systems, experimentally-grounded orbit libraries are loaded from
JSON files. The mapping is stored in `SYSTEM_TEMPLATE_PATHS`:

| System | Template family | Prototype file | Description |
|---|---|---|---|
| Al-Cu-Fe | `icosahedral_approximant_1_1` | `data/prototypes/al_cu_fe_mackay_1_1.json` | Mackay 1/1 approximant |
| Al-Pd-Mn | `decagonal_proxy_2_1` | `data/prototypes/al_pd_mn_xi_prime.json` | Xi-prime pseudo-Mackay |
| Sc-Zn | `cubic_proxy_1_0` | `data/prototypes/sc_zn_tsai_sczn6.json` | Tsai ScZn6 (COD CIF 4344182) |

### Zomic-Authored Orbit Libraries

The generator can also consume orbit libraries produced from `.zomic` scripts. In that
path, `materials_discovery.generator.zomic_bridge`:

1. invokes `./gradlew :core:zomicExport`
2. reads labeled VM locations exported by `vZome core`
3. embeds those labeled points into the specified crystal cell
4. writes a generated orbit-library JSON under `data/prototypes/generated/`

### Template Resolution

`resolve_template(system_name, template_family)` checks whether a system-specific
orbit library exists on disk for the given `(system_name, template_family)` pair. If
it does, the orbit library is loaded (and cached via `@functools.cache`). Otherwise
the generic template from `FAMILY_TEMPLATES` is returned.

When the config provides `prototype_library` or `zomic_design`, generation bypasses
`SYSTEM_TEMPLATE_PATHS` and loads the resolved orbit library directly with
`template_from_path(path)`.

### Template Data Structures

**`TemplateSite`** (frozen dataclass):
- `label` -- site identifier string
- `base_qphi` -- the site's position as a QPhiCoord
- `base_fractional_position` -- the same position as fractional coordinates
- `orbit` -- orbit group name
- `preferred_species` -- optional tuple of preferred element symbols
- `wyckoff` -- optional Wyckoff position label

**`ApproximantTemplate`** (frozen dataclass):
- `name`, `prototype_key`, `anchor_system` -- identification fields
- `reference`, `reference_url` -- literature provenance
- `base_cell` -- dictionary with keys `a`, `b`, `c`, `alpha`, `beta`, `gamma`
- `sites` -- tuple of `TemplateSite` instances
- `motif_center` -- fractional coordinate of the motif center (typically `(0.5, 0.5, 0.5)`)
- `translation_divisor` -- divisor used when reducing QPhiCoord to displacement
- `radial_scale`, `tangential_scale` -- displacement magnitudes along local frame axes
- `reference_axes` -- three reference directions for building local coordinate frames
- `minimum_site_separation` -- minimum allowed fractional distance between sites
- `space_group` -- optional space group symbol
- `source_kind` -- `"generic"`, `"orbit_library"`, `"cif_export"`, or `"zomic_export"`

### Fractional-to-QPhiCoord Conversion

`_position_to_qphi(position, site_index)` converts a fractional coordinate to a
QPhiCoord. The algorithm:

1. Center the position by subtracting 0.5 from each component.
2. For each axis, compute the rational part as `int(round(6 * centered))`.
3. Compute the phi part as `int(round(3 * centered * phi)) + ((site_index + axis_index) % 3) - 1`.

The `(site_index + axis_index) % 3 - 1` term adds a site-dependent offset of -1, 0,
or +1 to the phi coefficient, breaking degeneracies between sites that would otherwise
map to the same QPhiCoord.

## Coordinate Construction Pipeline

The main construction function is `construct_site_qphi` in `zphi_geometry.py`. It
transforms a template site's base QPhiCoord into a candidate-specific QPhiCoord
through a sequence of deterministic, seed-controlled operations.

### Step 1: Compute family_shift

A per-family integer offset:

```python
family_shift = {
    "icosahedral_approximant_1_1": 2,
    "decagonal_proxy_2_1": 1,
    "cubic_proxy_1_0": 0,
}.get(template_family, 0)
```

This ensures different template families produce distinct permutation/scaling
sequences even for the same seed.

### Step 2: Compute inflation_steps

```python
inflation_steps = ((seed + candidate_index + site_index + family_shift) % 3) - 1
```

This yields a value in `{-1, 0, 1}`, selecting whether to deflate by phi, leave
unchanged, or inflate by phi.

### Step 3: Permute

```python
rotated = _permute_coord(base_qphi, seed + candidate_index + site_index + family_shift)
```

The permutation is selected from six variants:

```python
_PERMUTATIONS = (
    (0, 1, 2),  # identity
    (1, 2, 0),  # cyclic
    (2, 0, 1),  # cyclic
    (0, 2, 1),  # swap y,z
    (1, 0, 2),  # swap x,y
    (2, 1, 0),  # swap x,z
)
```

The variant index is `(seed + candidate_index + site_index + family_shift) % 6`.
Even-numbered variants keep signs unchanged. Odd-numbered variants negate the phi
component of each pair (i.e., `(a, b)` becomes `(a, -b)`), which geometrically
reflects through the rational subspace.

### Step 4: Phi-scale

```python
scaled = phi_scale_coord(rotated, inflation_steps)
```

Applies `phi_scale_pair` to each of the three QPhiPair components using the
`inflation_steps` computed in step 2.

### Step 5: Translate

A translation vector is constructed from three phi-scaled pairs whose integer inputs
depend on `candidate_index`, `site_index`, and `family_shift`:

```python
translation = (
    phi_scale_pair(((candidate_index + site_index + family_shift) % 2, 0), inflation_steps),
    phi_scale_pair((0, ((candidate_index + family_shift) % 2)), max(0, inflation_steps)),
    phi_scale_pair(
        ((site_index + family_shift) % 2, -((candidate_index + site_index) % 2)),
        0,
    ),
)
translated = _translate_coord(scaled, translation)
```

Translation is performed by pairwise addition of QPhiPairs (rational parts add,
phi parts add).

### Step 6: Bound

```python
return _bound_coord(translated, min_coeff=min_coeff, max_coeff=max_coeff)
```

All integer coefficients (both rational and phi parts, across all three axes) are
clamped to `[min_coeff, max_coeff]`. The bounds come from the pipeline configuration
(`config.coeff_bounds`).

### Cell Scaling

`cell_scale_multiplier(seed, candidate_index)` computes a per-candidate cell scale
factor:

```python
variant = (seed + 5 * candidate_index) % 3 - 1   # yields -1, 0, or 1
return round(PHI**variant, 6)
```

This produces one of three values: `1/phi ~ 0.618034`, `1.0`, or `phi ~ 1.618034`.
The multiplier is applied to the lattice parameters `a`, `b`, `c` of the template's
base cell (angles are unchanged).

## From QPhiCoord to Final Positions

After `construct_site_qphi` produces a QPhiCoord for each site, the
`site_positions_from_template` function in `site_positions.py` converts these to
fractional and Cartesian coordinates.

### Displacement from Base Position

For each site, the pipeline computes a displacement from the template site's
`base_fractional_position`:

1. **Reduce**: Convert the QPhiCoord to floats via `qphi_coord_to_float`, then
   reduce by `template.translation_divisor` to get a bounded displacement vector
   in `(-0.5, 0.5]`.

2. **Build local frame**: Construct a radial/tangential coordinate frame centered at
   the motif center, using the template's `reference_axes` and cross products to
   ensure orthogonality.

3. **Apply displacement**: Scale the reduced components by `radial_scale` (first
   component) and `tangential_scale` (second and third components) along the local
   frame axes.

4. **Wrap**: Wrap the displaced position into `[0, 1)` on each axis.

### Collision Avoidance

After displacement, `_resolve_collision` checks the new position against all
previously placed sites. If any pair is closer than `minimum_site_separation`
(measured as periodic fractional distance), the position is shifted along the
tangential axes by multiples of `0.48 * minimum_site_separation` until a
non-colliding placement is found, trying 13 offset combinations.

### Cartesian Conversion

`cell_matrix_from_cell` builds a 3x3 matrix from the six cell parameters
`(a, b, c, alpha, beta, gamma)` using the standard crystallographic convention:

- **a** lies along the x-axis.
- **b** lies in the xy-plane at angle gamma from a.
- **c** is determined by angles alpha and beta.

`fractional_to_cartesian` multiplies fractional coordinates by this matrix.

## Candidate Generation: End-to-End

The `generate_candidates` function in `candidate_factory.py` ties everything together.
For each candidate index:

1. **Resolve template**: `resolve_template(system_name, template_family)` returns
   the appropriate `ApproximantTemplate` unless the config specifies
   `prototype_library` or `zomic_design`, in which case the override path is loaded
   with `template_from_path(...)`.

2. **Assign species**: `assign_species` from `decorate_sites` maps element types to
   sites using `composition_bounds` and site preferences from the template.

3. **Construct QPhiCoords**: For each template site, call `construct_site_qphi` with
   the site's `base_qphi`, the current `candidate_index`, `site_index`, `seed`, and
   coefficient bounds.

4. **Compute positions**: `site_positions_from_template` converts QPhiCoords to
   fractional and Cartesian positions using the displacement/collision pipeline.

5. **Scale cell**: `cell_scale_multiplier(seed, candidate_index)` produces a
   phi-power multiplier applied to the template's lattice parameters.

6. **Build record**: A `CandidateRecord` is assembled with the cell, sites,
   composition, screening placeholder, and provenance metadata (including
   `prototype_key`, `reference`, and `source_kind`).

7. **Validate and write**: After all candidates are generated,
   `validate_unique_candidate_ids` checks for duplicates, and the batch is written
   to JSONL via `write_jsonl`.

## Source Files

| File | Path |
|---|---|
| Z[phi] geometry | `materials-discovery/src/materials_discovery/generator/zphi_geometry.py` |
| Approximant templates | `materials-discovery/src/materials_discovery/generator/approximant_templates.py` |
| Candidate factory | `materials-discovery/src/materials_discovery/generator/candidate_factory.py` |
| Coordinate utilities | `materials-discovery/src/materials_discovery/common/coordinates.py` |
| Site position computation | `materials-discovery/src/materials_discovery/generator/site_positions.py` |
| Type definitions | `materials-discovery/src/materials_discovery/common/schema.py` |
