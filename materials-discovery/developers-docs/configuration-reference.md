# Configuration Reference

## Overview

Each materials-discovery pipeline run is driven by a single YAML configuration file. These files live in `configs/systems/` and are deserialized into a `SystemConfig` Pydantic model defined in `src/materials_discovery/common/schema.py`. The config controls which chemical system to explore, how candidate structures are generated, and which backend adapters perform validation work.

The repository ships seven config files that form a progression from minimal mock-mode testing through full native-provider execution plus Zomic-authored generation:

| File | Purpose | Backend mode |
|---|---|---|
| `al_cu_fe.yaml` | Minimal mock config for Al-Cu-Fe | mock |
| `al_cu_fe_real.yaml` | Fixture-backed real mode | real |
| `al_cu_fe_exec.yaml` | Exec adapter real mode with subprocess commands | real |
| `al_cu_fe_native.yaml` | Native provider real mode with in-process MLIP | real |
| `al_pd_mn.yaml` | Alternative ternary system (decagonal) | mock |
| `sc_zn.yaml` | Binary system (cubic) | mock |
| `sc_zn_zomic.yaml` | Binary system generated from a Zomic-authored prototype bridge | mock |

---

## SystemConfig Reference

`SystemConfig` is the top-level model. All fields except `backend` are required.

| Field | Type | Default | Description |
|---|---|---|---|
| `system_name` | `str` | *required* | Chemical system identifier (e.g. `"Al-Cu-Fe"`). Used as a label throughout the pipeline and in output filenames. |
| `template_family` | `str` | *required* | Which approximant template drives structure generation. Valid values: `"icosahedral_approximant_1_1"`, `"decagonal_proxy_2_1"`, `"cubic_proxy_1_0"`. See [zphi-geometry.md](zphi-geometry.md) for the geometry behind each template. |
| `species` | `list[str]` | *required* | Element symbols that define the system (e.g. `["Al", "Cu", "Fe"]`). |
| `composition_bounds` | `dict[str, CompositionBound]` | *required* | Per-element min/max mole-fraction bounds. Must include an entry for every element in `species`; validation rejects missing entries. Each `CompositionBound` has `min` and `max` floats in [0, 1] with `min <= max`. |
| `coeff_bounds` | `CoeffBounds` | *required* | Integer bounds on Z[phi] lattice coefficients used during candidate generation. Has `min` and `max` fields; `min` must be `<= max`. Wider bounds produce a larger search space. |
| `seed` | `int` | *required* | Random seed for reproducibility across generation and screening. |
| `default_count` | `int` | *required* | Number of candidate structures to generate per run. |
| `prototype_library` | `str \| None` | `None` | Optional workspace-root-relative path to an orbit-library JSON file. When set, generation uses this file instead of anchored template resolution. |
| `zomic_design` | `str \| None` | `None` | Optional workspace-root-relative path to a `ZomicDesignConfig` YAML file. When set, `generate` exports the design and then loads the resulting orbit library automatically. |
| `backend` | `BackendConfig` | mock-mode defaults | Backend configuration block. When omitted, defaults to mock mode with fixture adapters. See the BackendConfig section below. |

### Validation rules

- **composition_bounds coverage**: Every element listed in `species` must have a corresponding key in `composition_bounds`. The validator raises `ValueError` if any species is missing.
- **CompositionBound range**: `min` and `max` must both lie in [0, 1], and `min <= max`.
- **CoeffBounds ordering**: `min` must be `<= max`.
- **Prototype override exclusivity**: `prototype_library` and `zomic_design` are mutually exclusive.

### Path semantics

- `prototype_library` and `zomic_design` are resolved relative to the materials-discovery workspace root.
- Paths inside a Zomic design YAML (`zomic_file`, `export_path`, `raw_export_path`) are resolved relative to the design YAML file itself.

---

## ZomicDesignConfig Reference

`ZomicDesignConfig` is a separate YAML contract used by `mdisc export-zomic` and by
`mdisc generate` when `SystemConfig.zomic_design` is set. It defines how exact Zomic
geometry is embedded into a crystallographic cell and converted into the orbit-library
JSON format consumed by the generator.

| Field | Type | Default | Description |
|---|---|---|---|
| `zomic_file` | `str` | *required* | Path to the `.zomic` source file, relative to the design YAML unless absolute. |
| `prototype_key` | `str` | *required* | Stable key written into candidate provenance and the exported orbit-library JSON. |
| `system_name` | `str` | *required* | Chemical system name the design targets. |
| `template_family` | `str` | *required* | Generator family the design belongs to. |
| `base_cell` | `dict[str, float]` | *required* | Unit cell used for embedding labeled Zomic points. Must include `a`, `b`, `c`, `alpha`, `beta`, `gamma`. |
| `reference` | `str` | *required* | Human-readable provenance string for the design. |
| `reference_url` | `str \| None` | `None` | Optional provenance URL. |
| `motif_center` | `tuple[float, float, float]` | `(0.5, 0.5, 0.5)` | Fractional center used when embedding the exported points. Must lie strictly inside the unit cell. |
| `translation_divisor` | `float` | *required* | Candidate-generation displacement divisor reused by the downstream site-position logic. Must be > 0. |
| `radial_scale` | `float` | *required* | Radial perturbation scale for candidate generation. Must be > 0. |
| `tangential_scale` | `float` | *required* | Tangential perturbation scale for candidate generation. Must be > 0. |
| `reference_axes` | `tuple[Position3D, Position3D, Position3D]` | *required* | Local frame axes used by downstream site placement. |
| `minimum_site_separation` | `float` | *required* | Minimum allowed site separation in fractional coordinates. Must be > 0. |
| `preferred_species_by_orbit` | `dict[str, list[str]]` | `{}` | Optional chemistry preference hints keyed by inferred orbit name. |
| `orbit_config` | `dict[str, ZomicOrbitConfig]` | `{}` | Optional per-orbit overrides for preferred species and Wyckoff labels. |
| `cartesian_scale` | `float \| None` | `None` | Optional explicit scale factor from Zomic units into the target cell. If omitted, the bridge chooses a deterministic scale from `embedding_fraction`. |
| `embedding_fraction` | `float` | `0.72` | Fraction of the available half-cell span that the embedded motif may occupy. Must lie in `(0, 1)`. |
| `export_path` | `str \| None` | `None` | Optional output path for the generated orbit-library JSON. |
| `raw_export_path` | `str \| None` | `None` | Optional output path for the raw labeled-geometry export from `vZome core`. |
| `space_group` | `str \| None` | `None` | Optional space-group tag carried through to the orbit-library JSON and candidate provenance. |

### Zomic labeling convention

The bridge only turns labeled VM locations into atomic sites. Orbit names are inferred
from labels:

- `orbit.site_name` -> orbit `orbit`
- `orbit_01` -> orbit `orbit`
- otherwise -> full label

This makes labels the stable authoring boundary between `Zomic` geometry and the
materials generator.

---

## BackendConfig Reference

`BackendConfig` controls adapter selection, provider dispatch, subprocess commands, and simulation parameters. When the entire `backend` block is omitted from the YAML, the model defaults to mock mode with automatic adapter selection.

### Adapter and provider fields

| Field | Type | Default | Auto-default (mock) | Auto-default (real) |
|---|---|---|---|---|
| `mode` | `"mock"` \| `"real"` | `"mock"` | -- | -- |
| `ingest_adapter` | `str \| None` | `None` | `"hypodx_fixture"` | `"hypodx_pinned_v2026_03_09"` |
| `committee_adapter` | `str \| None` | `None` | *unchanged (None)* | `"committee_fixture_fallback_v2026_03_09"` |
| `phonon_adapter` | `str \| None` | `None` | *unchanged (None)* | `"phonon_fixture_fallback_v2026_03_09"` |
| `md_adapter` | `str \| None` | `None` | *unchanged (None)* | `"md_fixture_fallback_v2026_03_09"` |
| `xrd_adapter` | `str \| None` | `None` | *unchanged (None)* | `"xrd_fixture_fallback_v2026_03_09"` |
| `committee_provider` | `str \| None` | `None` | *unchanged (None)* | `"pinned"` |
| `phonon_provider` | `str \| None` | `None` | *unchanged (None)* | `"pinned"` |
| `md_provider` | `str \| None` | `None` | *unchanged (None)* | `"pinned"` |
| `xrd_provider` | `str \| None` | `None` | *unchanged (None)* | `"pinned"` |

Auto-defaulting is applied by a `model_validator` on `BackendConfig`. When a field is explicitly set in the YAML, the explicit value takes precedence over the auto-default. In mock mode only `ingest_adapter` is auto-defaulted; the four validation adapters and providers remain `None`. In real mode all nine fields are auto-defaulted if not explicitly provided.

For a detailed explanation of adapters, providers, and the dispatch logic, see [backend-system.md](backend-system.md).

### Snapshot and cache fields

| Field | Type | Default | Description |
|---|---|---|---|
| `pinned_snapshot` | `str \| None` | `None` | Path to the ingest snapshot JSON file (relative to project root). Required by pinned ingest adapters. |
| `validation_snapshot` | `str \| None` | `None` | Path to the validation snapshot JSON file. Required by pinned validation providers. |
| `validation_cache_dir` | `str \| None` | `None` | Directory for exec adapter on-disk caching. Enables cache reuse across runs when using `*_exec_cache_v1` adapters. |
| `benchmark_corpus` | `str \| None` | `None` | Path to a benchmark JSON file for regression testing against known results. |
| `versions` | `dict[str, str]` | `{}` | Arbitrary key-value pairs for version tracking (e.g. snapshot dates, backend versions). Propagated into `ArtifactManifest` records. |

### Command templates (exec adapters)

| Field | Type | Default | Description |
|---|---|---|---|
| `committee_command` | `list[str] \| None` | `None` | Subprocess command template for committee validation. |
| `phonon_command` | `list[str] \| None` | `None` | Subprocess command template for phonon validation. |
| `md_command` | `list[str] \| None` | `None` | Subprocess command template for MD validation. |
| `xrd_command` | `list[str] \| None` | `None` | Subprocess command template for XRD validation. |

Command lists support the following placeholder tokens, substituted at runtime:

| Placeholder | Expanded to |
|---|---|
| `{python}` | Path to the current Python interpreter |
| `{input}` | Path to the input JSON file for the subprocess |
| `{output}` | Path where the subprocess must write its output JSON |
| `{workspace_root}` | Absolute path to the project root directory |
| `{stage}` | Current pipeline stage name |

When set, command lists must be non-empty; an empty list raises `ValueError`.

### Simulation parameters

| Field | Type | Default | Validation | Description |
|---|---|---|---|---|
| `committee_device` | `str \| None` | `None` | -- | Device for ML inference (e.g. `"cpu"`, `"cuda"`). Only relevant when using native providers. |
| `md_temperature_k` | `float` | `600.0` | must be > 0 | Molecular dynamics simulation temperature in Kelvin. |
| `md_timestep_fs` | `float` | `0.5` | must be > 0 | MD integration timestep in femtoseconds. |
| `md_steps` | `int` | `50` | must be > 0 | Number of MD simulation steps. |
| `xrd_wavelength` | `str` | `"CuKa"` | -- | X-ray wavelength identifier for diffraction pattern simulation. |

---

## Config Progression

The four Al-Cu-Fe config files demonstrate a layered progression from mock testing through production-grade native execution. Each layer adds backend capabilities on top of the same core system definition.

### Layer 1: Mock mode (`al_cu_fe.yaml`)

The minimal config. No `backend` block means the model defaults to `mode: "mock"` with `ingest_adapter: "hypodx_fixture"`. All validation stages use synthetic fixture data. Suitable for unit tests, CI, and rapid iteration on pipeline logic.

```yaml
system_name: Al-Cu-Fe
template_family: icosahedral_approximant_1_1
species:
  - Al
  - Cu
  - Fe
composition_bounds:
  Al:
    min: 0.60
    max: 0.80
  Cu:
    min: 0.10
    max: 0.25
  Fe:
    min: 0.05
    max: 0.20
coeff_bounds:
  min: -3
  max: 3
seed: 17
default_count: 100
```

### Parallel authoring path: Zomic-backed mock mode (`sc_zn_zomic.yaml`)

This config keeps the pipeline in mock mode but changes how generation gets its
prototype. Instead of relying on `SYSTEM_TEMPLATE_PATHS`, it points at a Zomic
design YAML:

```yaml
system_name: Sc-Zn
template_family: cubic_proxy_1_0
species:
  - Sc
  - Zn
composition_bounds:
  Sc:
    min: 0.15
    max: 0.40
  Zn:
    min: 0.60
    max: 0.85
coeff_bounds:
  min: -2
  max: 2
seed: 31
default_count: 64
zomic_design: designs/zomic/sc_zn_tsai_bridge.yaml
```

What this path adds:

- **Design authoring in Zomic**: candidate sites come from labeled VM locations in a `.zomic` script.
- **Generated orbit library cache**: `generate` exports and reuses `data/prototypes/generated/*.json`.
- **vZome runtime dependency**: generation now requires a local Java runtime because the bridge invokes `./gradlew :core:zomicExport`.

### Layer 2: Real mode with fixture fallback (`al_cu_fe_real.yaml`)

Adds a `backend` block with `mode: real`. Uses pinned snapshot files for ingest and fixture-fallback adapters for validation. This mode exercises the real data path and schema validation without requiring MLIP dependencies.

```yaml
system_name: Al-Cu-Fe
template_family: icosahedral_approximant_1_1
species:
  - Al
  - Cu
  - Fe
composition_bounds:
  Al:
    min: 0.60
    max: 0.80
  Cu:
    min: 0.10
    max: 0.25
  Fe:
    min: 0.05
    max: 0.20
coeff_bounds:
  min: -3
  max: 3
seed: 17
default_count: 100
backend:
  mode: real
  ingest_adapter: hypodx_pinned_v2026_03_09
  committee_adapter: committee_fixture_fallback_v2026_03_09
  phonon_adapter: phonon_fixture_fallback_v2026_03_09
  md_adapter: md_fixture_fallback_v2026_03_09
  xrd_adapter: xrd_fixture_fallback_v2026_03_09
  pinned_snapshot: data/external/pinned/hypodx_pinned_2026_03_09.json
  validation_snapshot: data/external/pinned/al_cu_fe_validation_snapshot_2026_03_09.json
  benchmark_corpus: data/benchmarks/al_cu_fe_benchmark.json
  versions:
    hypodx_snapshot: "2026-03-09"
    validation_snapshot: "2026-03-09"
    benchmark_corpus: "2026-03-06"
```

What this layer adds:
- **Pinned ingest**: `pinned_snapshot` points to a frozen HyPoDX export, ensuring deterministic ingest across runs.
- **Fixture-fallback validation adapters**: Each `*_adapter` returns pre-recorded results while conforming to the real adapter interface.
- **Benchmark corpus**: Enables regression assertions against known outputs.
- **Version tracking**: `versions` records snapshot provenance dates for audit trails.

### Layer 3: Exec adapters (`al_cu_fe_exec.yaml`)

Replaces fixture-fallback adapters with exec-cache adapters (`*_exec_cache_v1`) that run validation as subprocesses. Each `*_command` field specifies the command template with `{python}`, `{input}`, and `{output}` placeholders.

```yaml
system_name: Al-Cu-Fe
template_family: icosahedral_approximant_1_1
species:
  - Al
  - Cu
  - Fe
composition_bounds:
  Al:
    min: 0.60
    max: 0.80
  Cu:
    min: 0.10
    max: 0.25
  Fe:
    min: 0.05
    max: 0.20
coeff_bounds:
  min: -3
  max: 3
seed: 17
default_count: 100
backend:
  mode: real
  ingest_adapter: hypodx_pinned_v2026_03_09
  committee_adapter: committee_exec_cache_v1
  phonon_adapter: phonon_exec_cache_v1
  md_adapter: md_exec_cache_v1
  xrd_adapter: xrd_exec_cache_v1
  pinned_snapshot: data/external/pinned/hypodx_pinned_2026_03_09.json
  validation_snapshot: data/external/pinned/al_cu_fe_validation_snapshot_2026_03_09.json
  validation_cache_dir: data/execution_cache/al_cu_fe_exec
  committee_command:
    - "{python}"
    - -m
    - materials_discovery.backends.run_committee_backend
    - --input
    - "{input}"
    - --output
    - "{output}"
  phonon_command:
    - "{python}"
    - -m
    - materials_discovery.backends.run_phonon_backend
    - --input
    - "{input}"
    - --output
    - "{output}"
  md_command:
    - "{python}"
    - -m
    - materials_discovery.backends.run_md_backend
    - --input
    - "{input}"
    - --output
    - "{output}"
  xrd_command:
    - "{python}"
    - -m
    - materials_discovery.backends.run_xrd_backend
    - --input
    - "{input}"
    - --output
    - "{output}"
  benchmark_corpus: data/benchmarks/al_cu_fe_benchmark.json
  versions:
    hypodx_snapshot: "2026-03-09"
    validation_snapshot: "2026-03-09"
    benchmark_corpus: "2026-03-06"
    validation_backend: "pinned-runner-v1"
```

What this layer adds:
- **Exec-cache adapters**: Validation runs as isolated subprocesses, enabling sandboxing and cache reuse via `validation_cache_dir`.
- **Command templates**: Each `*_command` list defines the subprocess invocation. Placeholders are expanded at runtime.
- **On-disk caching**: Results are cached under `validation_cache_dir` keyed by input hash, so repeated runs skip redundant computation.

### Layer 4: Native providers (`al_cu_fe_native.yaml`)

Adds native in-process MLIP providers on top of exec adapters. The `*_provider` fields select specific implementations, and simulation parameters (`md_temperature_k`, `md_timestep_fs`, `md_steps`, `xrd_wavelength`, `committee_device`) tune execution.

```yaml
system_name: Al-Cu-Fe
template_family: icosahedral_approximant_1_1
species:
  - Al
  - Cu
  - Fe
composition_bounds:
  Al:
    min: 0.60
    max: 0.80
  Cu:
    min: 0.10
    max: 0.25
  Fe:
    min: 0.05
    max: 0.20
coeff_bounds:
  min: -3
  max: 3
seed: 17
default_count: 100
backend:
  mode: real
  ingest_adapter: hypodx_pinned_v2026_03_09
  committee_adapter: committee_exec_cache_v1
  phonon_adapter: phonon_exec_cache_v1
  md_adapter: md_exec_cache_v1
  xrd_adapter: xrd_exec_cache_v1
  committee_provider: ase_committee_v1
  phonon_provider: mace_hessian_v1
  md_provider: ase_langevin_v1
  xrd_provider: pymatgen_xrd_v1
  committee_device: cpu
  md_temperature_k: 600.0
  md_timestep_fs: 0.5
  md_steps: 25
  xrd_wavelength: CuKa
  pinned_snapshot: data/external/pinned/hypodx_pinned_2026_03_09.json
  validation_snapshot: data/external/pinned/al_cu_fe_validation_snapshot_2026_03_09.json
  validation_cache_dir: data/execution_cache/al_cu_fe_native
  committee_command:
    - "{python}"
    - -m
    - materials_discovery.backends.run_committee_backend
    - --input
    - "{input}"
    - --output
    - "{output}"
  phonon_command:
    - "{python}"
    - -m
    - materials_discovery.backends.run_phonon_backend
    - --input
    - "{input}"
    - --output
    - "{output}"
  md_command:
    - "{python}"
    - -m
    - materials_discovery.backends.run_md_backend
    - --input
    - "{input}"
    - --output
    - "{output}"
  xrd_command:
    - "{python}"
    - -m
    - materials_discovery.backends.run_xrd_backend
    - --input
    - "{input}"
    - --output
    - "{output}"
  benchmark_corpus: data/benchmarks/al_cu_fe_benchmark.json
  versions:
    hypodx_snapshot: "2026-03-09"
    validation_snapshot: "2026-03-09"
    benchmark_corpus: "2026-03-06"
    validation_backend: "native-provider-v1"
```

What this layer adds:
- **Native providers**: `committee_provider: ase_committee_v1` runs a MACE/CHGNet/MatterSim committee ensemble via ASE. `phonon_provider: mace_hessian_v1` computes finite-difference phonons. `md_provider: ase_langevin_v1` runs Langevin MD. `xrd_provider: pymatgen_xrd_v1` simulates powder XRD patterns.
- **Device selection**: `committee_device: cpu` pins inference to CPU (use `"cuda"` for GPU).
- **Tuned simulation parameters**: `md_steps: 25` (reduced from the default 50 for faster iteration), explicit temperature and timestep settings.
- **Dependency note**: Native providers require `uv sync --extra dev --extra mlip` to install MLIP dependencies.

---

## Alternative Systems

### Al-Pd-Mn (`al_pd_mn.yaml`)

A ternary system using the decagonal proxy template. Demonstrates how `template_family` and `composition_bounds` change for a different quasicrystal symmetry class.

```yaml
system_name: Al-Pd-Mn
template_family: decagonal_proxy_2_1
species:
  - Al
  - Pd
  - Mn
composition_bounds:
  Al:
    min: 0.60
    max: 0.80
  Pd:
    min: 0.10
    max: 0.30
  Mn:
    min: 0.05
    max: 0.20
coeff_bounds:
  min: -3
  max: 3
seed: 23
default_count: 100
```

Key differences from Al-Cu-Fe:
- `template_family: decagonal_proxy_2_1` selects a decagonal approximant geometry instead of icosahedral.
- Pd has a wider composition range (0.10--0.30) than Cu in Al-Cu-Fe (0.10--0.25).
- Different `seed` for independent random exploration.

### Sc-Zn (`sc_zn.yaml`)

A binary system using the cubic proxy template. Demonstrates that the pipeline handles two-element systems with no code changes.

```yaml
system_name: Sc-Zn
template_family: cubic_proxy_1_0
species:
  - Sc
  - Zn
composition_bounds:
  Sc:
    min: 0.15
    max: 0.40
  Zn:
    min: 0.60
    max: 0.85
coeff_bounds:
  min: -2
  max: 2
seed: 31
default_count: 100
```

Key differences:
- `template_family: cubic_proxy_1_0` selects a cubic approximant, the simplest template. See [zphi-geometry.md](zphi-geometry.md) for how template complexity scales.
- Only two species, so `composition_bounds` has two entries.
- Tighter `coeff_bounds` (-2 to 2 vs. -3 to 3) produces a smaller search space appropriate for the simpler template.

---

## How to Create a Config for a New System

1. **Choose a system name.** Use the standard element-dash notation: `"X-Y"` for binaries, `"X-Y-Z"` for ternaries.

2. **Select a template family.** Pick from the three available templates based on the target quasicrystal symmetry:
   - `icosahedral_approximant_1_1` -- icosahedral quasicrystals (most complex geometry)
   - `decagonal_proxy_2_1` -- decagonal quasicrystals
   - `cubic_proxy_1_0` -- cubic approximants (simplest geometry, also useful for initial exploration)

3. **Define species and composition bounds.** List all elements and set physically motivated min/max mole fractions. Bounds must be in [0, 1] with `min <= max`. Every species must have a bounds entry.

4. **Set coefficient bounds.** Start with `{min: -3, max: 3}` for icosahedral/decagonal templates and `{min: -2, max: 2}` for cubic. Wider bounds increase the search space combinatorially.

5. **Pick a seed and count.** Use a unique integer seed for each system to ensure independent exploration. `default_count: 100` is a reasonable starting point.

6. **Start in mock mode.** Create the file without a `backend` block and verify the pipeline runs end-to-end:

   ```yaml
   system_name: X-Y-Z
   template_family: icosahedral_approximant_1_1
   species: [X, Y, Z]
   composition_bounds:
     X: {min: 0.50, max: 0.70}
     Y: {min: 0.15, max: 0.30}
     Z: {min: 0.05, max: 0.25}
   coeff_bounds: {min: -3, max: 3}
   seed: 42
   default_count: 100
   ```

7. **Promote to real mode.** Add a `backend` block with `mode: real` and point to the appropriate pinned snapshots. See the [config progression](#config-progression) above for the layer-by-layer approach.

8. **Place the file in `configs/systems/`.** Use a lowercase, underscore-separated filename matching the system name (e.g. `x_y_z.yaml`).

For details on the data models that the pipeline produces from these configs, see [data-schema-reference.md](data-schema-reference.md). For adapter implementation details, see [backend-system.md](backend-system.md).
