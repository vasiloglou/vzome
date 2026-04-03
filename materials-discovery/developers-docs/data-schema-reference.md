# Data Schema Reference

This document describes the Pydantic models and dataclasses that define the data
schema for the materials discovery pipeline. All models are defined in
`materials-discovery/src/materials_discovery/common/schema.py` unless otherwise
noted. Chemistry descriptors are defined in
`materials-discovery/src/materials_discovery/common/chemistry.py`.

---

## Type Aliases

Defined at module level in `schema.py`:

| Alias | Type | Description |
|---|---|---|
| `QPhiPair` | `tuple[int, int]` | A single (q, phi) integer pair. |
| `QPhiCoord` | `tuple[QPhiPair, QPhiPair, QPhiPair]` | Three-dimensional q-phi coordinate (one pair per axis). |
| `Position3D` | `tuple[float, float, float]` | A 3D coordinate (fractional or Cartesian). |

---

## Core Models

### CompositionBound

Constrains the allowed mole-fraction range for a single species.

| Field | Type | Default | Description |
|---|---|---|---|
| `min` | `float` | *(required)* | Lower bound of the composition fraction. |
| `max` | `float` | *(required)* | Upper bound of the composition fraction. |

**Validators:**
- `min` must be less than or equal to `max`.
- Both `min` and `max` must be in the range [0, 1].

---

### CoeffBounds

Integer coefficient range used during candidate generation.

| Field | Type | Default | Description |
|---|---|---|---|
| `min` | `int` | *(required)* | Minimum coefficient value. |
| `max` | `int` | *(required)* | Maximum coefficient value. |

**Validators:**
- `min` must be less than or equal to `max`.

---

### SiteRecord

Describes a single crystallographic site within a candidate structure.

| Field | Type | Default | Description |
|---|---|---|---|
| `label` | `str` | *(required)* | Site label (e.g., Wyckoff identifier). |
| `qphi` | `QPhiCoord` | *(required)* | Q-phi coordinates for the site. |
| `species` | `str` | *(required)* | Chemical element symbol occupying the site. |
| `occ` | `float` | *(required)* | Site occupancy fraction. |
| `fractional_position` | `Position3D \| None` | `None` | Fractional coordinates within the unit cell. |
| `cartesian_position` | `Position3D \| None` | `None` | Cartesian coordinates. |

**Validators:**
- `occ` must be in the range [0, 1].
- Each component of `fractional_position` (when present) must be in the range [0, 1).

---

### DigitalValidationRecord

Tracks the results of the multi-model digital validation pipeline for a
candidate structure.

| Field | Type | Default | Description |
|---|---|---|---|
| `status` | `str` | `"pending"` | Current validation status. |
| `committee` | `list[str]` | `["MACE", "CHGNet", "MatterSim"]` | Names of committee models used for energy evaluation. |
| `uncertainty_ev_per_atom` | `float \| None` | `None` | Uncertainty estimate (eV/atom). |
| `committee_energy_ev_per_atom` | `dict[str, float] \| None` | `None` | Per-model energy predictions (eV/atom). |
| `committee_std_ev_per_atom` | `float \| None` | `None` | Standard deviation across committee models (eV/atom). |
| `delta_e_proxy_hull_ev_per_atom` | `float \| None` | `None` | Energy above the proxy convex hull (eV/atom). |
| `proxy_hull_baseline_ev_per_atom` | `float \| None` | `None` | Baseline energy of the proxy hull (eV/atom). |
| `proxy_hull_reference_distance` | `float \| None` | `None` | Distance to the nearest reference phase on the proxy hull. |
| `proxy_hull_reference_phases` | `list[str] \| None` | `None` | Reference phases used for hull construction. |
| `phonon_imaginary_modes` | `int \| None` | `None` | Number of imaginary phonon modes found. |
| `phonon_pass` | `bool \| None` | `None` | Whether the phonon stability check passed. |
| `md_stability_score` | `float \| None` | `None` | Molecular dynamics stability score. |
| `md_pass` | `bool \| None` | `None` | Whether the MD stability check passed. |
| `xrd_confidence` | `float \| None` | `None` | XRD pattern confidence score. |
| `xrd_pass` | `bool \| None` | `None` | Whether the XRD validation check passed. |
| `passed_checks` | `bool \| None` | `None` | Overall pass/fail result across all checks. |
| `batch` | `str \| None` | `None` | Batch identifier for this validation run. |

---

### CandidateRecord

The central data object representing a single candidate crystal structure.

| Field | Type | Default | Description |
|---|---|---|---|
| `candidate_id` | `str` | *(required)* | Unique identifier for the candidate. |
| `system` | `str` | *(required)* | System name (e.g., `"Al-Cu-Fe"`). |
| `template_family` | `str` | *(required)* | Prototype family the candidate was generated from. |
| `cell` | `dict[str, float]` | *(required)* | Unit cell parameters (e.g., `a`, `b`, `c`, `alpha`, `beta`, `gamma`). |
| `sites` | `list[SiteRecord]` | *(required)* | Crystallographic sites in the structure. |
| `composition` | `dict[str, float]` | *(required)* | Normalized composition (element symbol to mole fraction). |
| `screen` | `dict[str, Any] \| None` | `None` | Screening results and metrics. |
| `digital_validation` | `DigitalValidationRecord` | `DigitalValidationRecord()` | Digital validation state and results. |
| `provenance` | `dict[str, Any]` | *(required)* | Generation provenance metadata. |

**Validators:**
- `composition` must not be empty.
- `composition` values must sum to 1.0 +/- 1e-6.

**Utility function:** `validate_unique_candidate_ids(candidates)` checks that all
`candidate_id` values in a sequence of `CandidateRecord` objects are unique.

#### JSON Example

```json
{
  "candidate_id": "alcufe-001",
  "system": "Al-Cu-Fe",
  "template_family": "icosahedral",
  "cell": {"a": 12.56, "b": 12.56, "c": 7.85, "alpha": 90.0, "beta": 90.0, "gamma": 120.0},
  "sites": [
    {
      "label": "M0",
      "qphi": [[1, 0], [0, 1], [1, 1]],
      "species": "Al",
      "occ": 1.0,
      "fractional_position": [0.123, 0.456, 0.789],
      "cartesian_position": null
    },
    {
      "label": "M1",
      "qphi": [[2, 1], [1, 0], [0, 1]],
      "species": "Cu",
      "occ": 0.85,
      "fractional_position": [0.5, 0.25, 0.0],
      "cartesian_position": null
    }
  ],
  "composition": {"Al": 0.65, "Cu": 0.23, "Fe": 0.12},
  "screen": null,
  "digital_validation": {
    "status": "pending",
    "committee": ["MACE", "CHGNet", "MatterSim"],
    "uncertainty_ev_per_atom": null,
    "committee_energy_ev_per_atom": null,
    "committee_std_ev_per_atom": null,
    "delta_e_proxy_hull_ev_per_atom": null,
    "proxy_hull_baseline_ev_per_atom": null,
    "proxy_hull_reference_distance": null,
    "proxy_hull_reference_phases": null,
    "phonon_imaginary_modes": null,
    "phonon_pass": null,
    "md_stability_score": null,
    "md_pass": null,
    "xrd_confidence": null,
    "xrd_pass": null,
    "passed_checks": null,
    "batch": null
  },
  "provenance": {
    "generator": "qphi_enumerator",
    "template": "icosahedral_v2",
    "seed": 42
  }
}
```

---

## Configuration Models

### BackendConfig

Configures which execution adapters and providers are used for each validation
stage. Embedded within `SystemConfig`.

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | `Literal["mock", "real"]` | `"mock"` | Execution mode. `"mock"` uses fixture data; `"real"` uses pinned or live backends. |
| `ingest_adapter` | `str \| None` | `None` | Adapter name for the ingest stage. Auto-defaults to `"hypodx_fixture"` in mock mode, `"hypodx_pinned_v2026_03_09"` in real mode. |
| `committee_adapter` | `str \| None` | `None` | Adapter name for committee energy evaluation. |
| `phonon_adapter` | `str \| None` | `None` | Adapter name for phonon calculations. |
| `md_adapter` | `str \| None` | `None` | Adapter name for molecular dynamics. |
| `xrd_adapter` | `str \| None` | `None` | Adapter name for XRD validation. |
| `committee_provider` | `str \| None` | `None` | Provider backend for committee evaluation. |
| `phonon_provider` | `str \| None` | `None` | Provider backend for phonon calculations. |
| `md_provider` | `str \| None` | `None` | Provider backend for molecular dynamics. |
| `xrd_provider` | `str \| None` | `None` | Provider backend for XRD validation. |
| `pinned_snapshot` | `str \| None` | `None` | Path or identifier for pinned snapshot data. |
| `validation_snapshot` | `str \| None` | `None` | Path or identifier for validation snapshot data. |
| `validation_cache_dir` | `str \| None` | `None` | Directory for cached validation results. |
| `committee_command` | `list[str] \| None` | `None` | External command for committee evaluation. |
| `phonon_command` | `list[str] \| None` | `None` | External command for phonon calculations. |
| `md_command` | `list[str] \| None` | `None` | External command for molecular dynamics. |
| `xrd_command` | `list[str] \| None` | `None` | External command for XRD validation. |
| `committee_device` | `str \| None` | `None` | Device for committee model inference (e.g., `"cpu"`, `"cuda"`). |
| `md_temperature_k` | `float` | `600.0` | MD simulation temperature in Kelvin. |
| `md_timestep_fs` | `float` | `0.5` | MD simulation timestep in femtoseconds. |
| `md_steps` | `int` | `50` | Number of MD simulation steps. |
| `xrd_wavelength` | `str` | `"CuKa"` | X-ray wavelength for XRD simulation. |
| `benchmark_corpus` | `str \| None` | `None` | Path to a benchmark corpus for evaluation. |
| `versions` | `dict[str, str]` | `{}` | Version tags for backend components. |

**Validators:**
- In `"real"` mode, adapters and providers for committee, phonon, MD, and XRD
  stages auto-default to pinned fixture fallback values and `"pinned"` providers
  if not explicitly set.
- Command lists, when configured, must be non-empty.
- `md_temperature_k`, `md_timestep_fs`, and `md_steps` must all be greater than zero.

---

### SystemConfig

Top-level configuration for a materials discovery run targeting a specific
chemical system.

| Field | Type | Default | Description |
|---|---|---|---|
| `system_name` | `str` | *(required)* | Name of the chemical system (e.g., `"Al-Cu-Fe"`). |
| `template_family` | `str` | *(required)* | Prototype family to use for generation. |
| `species` | `list[str]` | *(required)* | Chemical element symbols in the system. |
| `composition_bounds` | `dict[str, CompositionBound]` | *(required)* | Per-species composition bounds. |
| `coeff_bounds` | `CoeffBounds` | *(required)* | Integer coefficient bounds for generation. |
| `seed` | `int` | *(required)* | Random seed for reproducibility. |
| `default_count` | `int` | *(required)* | Default number of candidates to generate. |
| `prototype_library` | `str \| None` | `None` | Optional workspace-root-relative orbit-library override used by generation. |
| `zomic_design` | `str \| None` | `None` | Optional workspace-root-relative path to a `ZomicDesignConfig` file. |
| `backend` | `BackendConfig` | `BackendConfig()` | Backend configuration. |

**Validators:**
- Every element in `species` must have a corresponding key in `composition_bounds`.
- `prototype_library` and `zomic_design` cannot both be set.

---

### ZomicOrbitConfig

Optional per-orbit overrides used inside `ZomicDesignConfig`.

| Field | Type | Default | Description |
|---|---|---|---|
| `preferred_species` | `list[str] \| None` | `None` | Preferred species ordering for the orbit. |
| `wyckoff` | `str \| None` | `None` | Optional Wyckoff-style label to attach to the exported orbit. |

---

### ZomicDesignConfig

Design-time schema for Zomic-authored prototype export.

| Field | Type | Default | Description |
|---|---|---|---|
| `zomic_file` | `str` | *(required)* | Path to the `.zomic` source file, resolved relative to the design YAML unless absolute. |
| `prototype_key` | `str` | *(required)* | Stable prototype identifier. |
| `system_name` | `str` | *(required)* | Chemical system name for the design. |
| `template_family` | `str` | *(required)* | Template family that the generated orbit library should advertise. |
| `base_cell` | `dict[str, float]` | *(required)* | Crystallographic cell used for embedding the exported points. |
| `reference` | `str` | *(required)* | Human-readable provenance string. |
| `reference_url` | `str \| None` | `None` | Optional provenance URL. |
| `motif_center` | `Position3D` | `(0.5, 0.5, 0.5)` | Fractional motif center; each component must lie strictly inside `(0, 1)`. |
| `translation_divisor` | `float` | *(required)* | Generation displacement divisor; must be > 0. |
| `radial_scale` | `float` | *(required)* | Radial displacement scale; must be > 0. |
| `tangential_scale` | `float` | *(required)* | Tangential displacement scale; must be > 0. |
| `reference_axes` | `tuple[Position3D, Position3D, Position3D]` | *(required)* | Local reference frame axes for downstream site placement. |
| `minimum_site_separation` | `float` | *(required)* | Minimum site separation; must be > 0. |
| `preferred_species_by_orbit` | `dict[str, list[str]]` | `{}` | Orbit-level chemistry preferences derived from label prefixes. |
| `orbit_config` | `dict[str, ZomicOrbitConfig]` | `{}` | Optional orbit-level overrides for chemistry and Wyckoff labels. |
| `cartesian_scale` | `float \| None` | `None` | Optional explicit Zomic-to-cell scale factor. |
| `embedding_fraction` | `float` | `0.72` | Auto-scaling target in `(0, 1)` used when `cartesian_scale` is omitted. |
| `export_path` | `str \| None` | `None` | Optional orbit-library output path. |
| `raw_export_path` | `str \| None` | `None` | Optional raw labeled-geometry output path. |
| `space_group` | `str \| None` | `None` | Optional space-group tag passed through to the orbit-library JSON. |

**Validators:**
- `base_cell` must contain `a`, `b`, `c`, `alpha`, `beta`, `gamma`.
- `a`, `b`, and `c` must be > 0.
- `alpha`, `beta`, and `gamma` must lie in `(0, 180)`.
- `translation_divisor`, `radial_scale`, `tangential_scale`, and `minimum_site_separation` must be > 0.
- `cartesian_scale`, when present, must be > 0.
- `embedding_fraction` must lie in `(0, 1)`.

---

### IngestRecord

Represents a reference phase ingested from an external database.

| Field | Type | Default | Description |
|---|---|---|---|
| `system` | `str` | *(required)* | System name. |
| `phase_name` | `str` | *(required)* | Name of the reference phase. |
| `composition` | `dict[str, float]` | *(required)* | Composition (auto-normalized to sum to 1.0). |
| `source` | `str` | *(required)* | Data source identifier. |
| `metadata` | `dict[str, Any]` | `{}` | Additional metadata. |

**Validators:**
- Composition total must be positive; values are automatically normalized so they sum to 1.0.

---

## Pipeline Stage Summaries

Each pipeline stage returns a summary model capturing counts and output paths.

### IngestSummary

| Field | Type | Default |
|---|---|---|
| `raw_count` | `int` | *(required)* |
| `matched_count` | `int` | *(required)* |
| `deduped_count` | `int` | *(required)* |
| `output_path` | `str` | *(required)* |
| `invalid_count` | `int` | `0` |
| `backend_mode` | `Literal["mock", "real"]` | `"mock"` |
| `backend_adapter` | `str` | `"hypodx_fixture"` |
| `qa_metrics` | `dict[str, float \| int \| bool]` | `{}` |
| `manifest_path` | `str \| None` | `None` |

### ZomicExportSummary

| Field | Type | Default |
|---|---|---|
| `design_path` | `str` | *(required)* |
| `zomic_file` | `str` | *(required)* |
| `raw_export_path` | `str` | *(required)* |
| `orbit_library_path` | `str` | *(required)* |
| `labeled_site_count` | `int` | *(required)* |
| `orbit_count` | `int` | *(required)* |

### GenerateSummary

| Field | Type | Default |
|---|---|---|
| `requested_count` | `int` | *(required)* |
| `generated_count` | `int` | *(required)* |
| `invalid_filtered_count` | `int` | *(required)* |
| `output_path` | `str` | *(required)* |
| `qa_metrics` | `dict[str, float \| int \| bool]` | `{}` |
| `calibration_path` | `str \| None` | `None` |
| `manifest_path` | `str \| None` | `None` |

### ScreenSummary

| Field | Type | Default |
|---|---|---|
| `input_count` | `int` | *(required)* |
| `relaxed_count` | `int` | *(required)* |
| `passed_count` | `int` | *(required)* |
| `shortlisted_count` | `int` | *(required)* |
| `output_path` | `str` | *(required)* |
| `calibration_path` | `str \| None` | `None` |
| `manifest_path` | `str \| None` | `None` |

### HifiValidateSummary

| Field | Type | Default |
|---|---|---|
| `batch` | `str` | *(required)* |
| `input_count` | `int` | *(required)* |
| `validated_count` | `int` | *(required)* |
| `passed_count` | `int` | *(required)* |
| `output_path` | `str` | *(required)* |
| `calibration_path` | `str \| None` | `None` |
| `manifest_path` | `str \| None` | `None` |

### ActiveLearnSummary

| Field | Type | Default |
|---|---|---|
| `validated_count` | `int` | *(required)* |
| `selected_count` | `int` | *(required)* |
| `pass_rate` | `float` | *(required)* |
| `surrogate_path` | `str` | *(required)* |
| `batch_path` | `str` | *(required)* |
| `feature_store_path` | `str \| None` | `None` |
| `model_registry_path` | `str \| None` | `None` |
| `model_id` | `str \| None` | `None` |
| `manifest_path` | `str \| None` | `None` |

### HifiRankSummary

| Field | Type | Default |
|---|---|---|
| `input_count` | `int` | *(required)* |
| `ranked_count` | `int` | *(required)* |
| `passed_count` | `int` | *(required)* |
| `output_path` | `str` | *(required)* |
| `calibration_path` | `str \| None` | `None` |
| `manifest_path` | `str \| None` | `None` |

### ReportSummary

| Field | Type | Default |
|---|---|---|
| `ranked_count` | `int` | *(required)* |
| `reported_count` | `int` | *(required)* |
| `report_path` | `str` | *(required)* |
| `xrd_patterns_path` | `str` | *(required)* |
| `calibration_path` | `str \| None` | `None` |
| `report_fingerprint` | `str \| None` | `None` |
| `manifest_path` | `str \| None` | `None` |
| `pipeline_manifest_path` | `str \| None` | `None` |

---

## ArtifactManifest

Captures provenance and integrity metadata for a single pipeline stage execution.

| Field | Type | Default | Description |
|---|---|---|---|
| `run_id` | `str` | *(required)* | Unique run identifier. |
| `stage` | `str` | *(required)* | Pipeline stage name. |
| `system` | `str` | *(required)* | System name. |
| `config_hash` | `str` | *(required)* | Hash of the configuration used. |
| `backend_mode` | `Literal["mock", "real"]` | *(required)* | Backend mode for this run. |
| `backend_versions` | `dict[str, str]` | *(required)* | Version tags of backend components. |
| `output_hashes` | `dict[str, str]` | *(required)* | Content hashes of output artifacts. |
| `created_at_utc` | `str` | *(required)* | ISO-format UTC timestamp of creation. |

---

## Chemistry Descriptors

Defined in `materials-discovery/src/materials_discovery/common/chemistry.py`.
These are frozen dataclasses (not Pydantic models).

### ElementProperties

Properties for a single chemical element.

| Field | Type | Description |
|---|---|---|
| `atomic_number` | `int` | Atomic number. |
| `covalent_radius_pm` | `float` | Covalent radius in picometers. |
| `pauling_electronegativity` | `float` | Pauling electronegativity. |
| `valence_electrons` | `float` | Number of valence electrons. |

### CompositionDescriptors

Computed descriptors for a composition (element fractions).

| Field | Type | Description |
|---|---|---|
| `vec` | `float` | Valence electron concentration (composition-weighted). |
| `radius_mismatch` | `float` | Atomic-radius mismatch parameter. |
| `electronegativity_spread` | `float` | Composition-weighted electronegativity spread. |
| `pair_mixing_enthalpy_ev_per_atom` | `float` | Pairwise mixing enthalpy estimate (eV/atom). |
| `dominant_fraction` | `float` | Mole fraction of the most abundant element. |
| `avg_atomic_number` | `float` | Composition-weighted average atomic number. |

### CandidateDescriptors

Extends `CompositionDescriptors` with structure-level features.

| Field | Type | Description |
|---|---|---|
| *(all fields from CompositionDescriptors)* | | |
| `qphi_complexity` | `float` | Mean absolute value of all q-phi coefficients across sites. |

### Supported Elements

The `ELEMENT_PROPERTIES` dictionary contains priors for the following elements:

| Symbol | Atomic Number | Covalent Radius (pm) | Electronegativity | Valence Electrons |
|---|---|---|---|---|
| Al | 13 | 121.0 | 1.61 | 3.0 |
| Cu | 29 | 132.0 | 1.90 | 11.0 |
| Fe | 26 | 124.0 | 1.83 | 8.0 |
| Pd | 46 | 139.0 | 2.20 | 10.0 |
| Mn | 25 | 127.0 | 1.55 | 7.0 |
| Sc | 21 | 148.0 | 1.36 | 3.0 |
| Zn | 30 | 122.0 | 1.65 | 12.0 |

### Pair Mixing Enthalpies

The `PAIR_MIXING_ENTHALPY_EV` dictionary provides approximate pairwise
mixing-enthalpy proxies (eV/atom) for these element pairs:

| Pair | Enthalpy (eV/atom) |
|---|---|
| Al-Cu | -0.12 |
| Al-Fe | -0.18 |
| Cu-Fe | 0.04 |
| Al-Pd | -0.35 |
| Al-Mn | -0.20 |
| Mn-Pd | -0.15 |
| Sc-Zn | -0.16 |

---

## Artifact Directory Layout

All pipeline artifacts are stored under the `data/` directory at the workspace
root. The layout is:

```
data/
  external/fixtures/           Mock mode fixture data
  external/pinned/             Pinned snapshots for real mode
  prototypes/                  System-anchored orbit library JSONs
  benchmarks/                  Pinned benchmark corpora
  processed/                   Ingested reference phases (JSONL)
  candidates/                  Generated candidates (JSONL)
  screened/                    Screened shortlists (JSONL)
  hifi_validated/              Validated candidates per batch (JSONL)
  ranked/                      Final ranked candidates (JSONL)
  active_learning/             Surrogate models and next-batch selections
  reports/                     Experiment reports and XRD patterns
  calibration/                 Per-stage calibration artifacts (JSON)
  manifests/                   Stage and pipeline manifests (JSON)
  registry/features/           Feature store per system (JSONL)
  registry/models/             Model registry per system (JSONL)
  execution_cache/             Cached execution adapter results
```

### File Naming Convention

Artifact files follow the pattern:

```
{system_slug}_{artifact}.{ext}
```

where `system_slug` is derived from `system_name` by lowercasing and replacing
hyphens with underscores:

```python
def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")
```

For example, a system named `"Al-Cu-Fe"` produces the slug `al_cu_fe`, yielding
file names such as:

- `al_cu_fe_reference_phases.jsonl` (in `data/processed/`)
- `al_cu_fe_candidates.jsonl` (in `data/candidates/`)
- `al_cu_fe_screened.jsonl` (in `data/screened/`)
- `al_cu_fe_{batch_slug}_validated.jsonl` (in `data/hifi_validated/`)
- `al_cu_fe_ranked.jsonl` (in `data/ranked/`)
- `al_cu_fe_surrogate.json` (in `data/active_learning/`)
- `al_cu_fe_next_batch.jsonl` (in `data/active_learning/`)
- `al_cu_fe_validated_features.jsonl` (in `data/registry/features/`)
- `al_cu_fe_models.jsonl` (in `data/registry/models/`)
- `al_cu_fe_report.json` (in `data/reports/`)
- `al_cu_fe_xrd_patterns.jsonl` (in `data/reports/`)
- `al_cu_fe_generation_metrics.json` (in `data/calibration/`)
- `al_cu_fe_screen_calibration.json` (in `data/calibration/`)
- `al_cu_fe_{batch_slug}_validation_calibration.json` (in `data/calibration/`)
- `al_cu_fe_ranking_calibration.json` (in `data/calibration/`)
- `al_cu_fe_report_calibration.json` (in `data/calibration/`)
- `al_cu_fe_ingest_manifest.json` (in `data/manifests/`)
- `al_cu_fe_generate_manifest.json` (in `data/manifests/`)
- `al_cu_fe_screen_manifest.json` (in `data/manifests/`)
- `al_cu_fe_{batch_slug}_hifi_validate_manifest.json` (in `data/manifests/`)
- `al_cu_fe_hifi_rank_manifest.json` (in `data/manifests/`)
- `al_cu_fe_active_learn_manifest.json` (in `data/manifests/`)
- `al_cu_fe_report_manifest.json` (in `data/manifests/`)
- `al_cu_fe_pipeline_manifest.json` (in `data/manifests/`)
- `al_cu_fe_benchmark.json` (in `data/benchmarks/`)
