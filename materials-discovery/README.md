# Materials Discovery Workspace

This workspace implements a full M1-M6 runnable slice of the no-DFT materials discovery pipeline documented in:

- `developer-docs/materials-discovery-software-scaffold.md`
- `developer-docs/vzome-geometry-tutorial.md` (Section 10.8)

## What is implemented

- `mdisc ingest`: fixture-based ingestion, normalization, deduplication, and JSONL output.
- Ingest backend switch: `backend.mode=mock|real` with pluggable ingest adapter registry.
- Ingest artifact manifests: `data/manifests/*_ingest_manifest.json` with config/backend/output hashes.
- Snapshot-backed RM1 integration test target: `uv run pytest -m integration`.
- `mdisc generate`: deterministic Z[phi]-aware candidate generation with schema validation and JSONL output.
- `mdisc screen`: proxy relax, thresholding, and shortlist ranking.
- `mdisc hifi-validate`: no-DFT digital validation (committee, uncertainty, proxy hull, phonon, short MD, XRD checks).
- `mdisc active-learn`: risk-aware surrogate fitting + next-batch acquisition from validated candidates.
- `mdisc hifi-rank`: deterministic uncertainty-aware ranking of validated candidates.
- `mdisc report`: experiment-facing report generation with chemistry-driven powder-XRD proxy signatures.
- Stage manifests are emitted for every command under `data/manifests/`.
- Calibration artifacts are emitted under `data/calibration/`.
- Model/feature registry artifacts are emitted under `data/registry/models` and `data/registry/features`.
- Backend capability matrix is tracked in `data/registry/backend_capabilities.yaml`.
- Pinned benchmark corpora live under `data/benchmarks/`.

## Real-mode scientific gates

- Real mode now uses composition/descriptor-based no-DFT scoring for `screen` and `hifi-validate` stages (not hash-jitter scoring).
- Real mode enforces element/property and pair-mixing prior coverage for configured systems.
- Real mode now computes `DeltaE_proxy_hull` against ingested competing phases using exact-reference or convex-mixture baselines instead of batch-relative best-candidate scoring.
- `mdisc hifi-rank` now emits calibrated `stability_probability`, `ood_score`, `novelty_score`, and `decision_score` components in candidate provenance.
- `mdisc active-learn` now trains on descriptor/screen features and selects candidates by predicted success, boundary uncertainty, novelty, and OOD risk.
- `mdisc report` now emits chemistry-driven XRD proxy fingerprints, recommendation tiers, risk flags, and release-gate calibration artifacts.
- Real-mode validation stages now run through fixture-backed adapters for committee, phonon, MD, and XRD, with analytic fallback when a pinned result is absent.
- Real-mode ranking, active learning, and report release gates now load thresholds from pinned benchmark corpora instead of fixed constants.
- Candidate geometry generation now applies Z[phi] scaling, permutation, and translation rules rather than pairwise random jitter.
- Generated candidates now store explicit `fractional_position` and `cartesian_position` site coordinates in addition to symbolic `qphi`.
- Real-mode validation now also supports executable adapters (`*_exec_cache_v1`) that run external commands against a JSON input/output contract and reuse results from `data/execution_cache/`.
- Concrete pinned runner modules are available for command-backed validation:
  - `materials_discovery.backends.run_committee_backend`
  - `materials_discovery.backends.run_phonon_backend`
  - `materials_discovery.backends.run_md_backend`
  - `materials_discovery.backends.run_xrd_backend`
- Native provider mode is available through `configs/systems/al_cu_fe_native.yaml` with:
  - `ase_committee_v1`
  - `mace_hessian_v1`
  - `ase_langevin_v1`
  - `pymatgen_xrd_v1`
- Real-mode XRD validation now requires ingested reference phases in `data/processed/*_reference_phases.jsonl` (run `mdisc ingest` first).
- Mock mode remains deterministic for CI reproducibility and fast local checks.

## Executable Validation Adapters

Real mode can now run command-backed validation adapters for committee, phonon, MD, and XRD stages.

Set the adapter names and commands under `backend` in a system config:

```yaml
backend:
  mode: real
  committee_adapter: committee_exec_cache_v1
  phonon_adapter: phonon_exec_cache_v1
  md_adapter: md_exec_cache_v1
  xrd_adapter: xrd_exec_cache_v1
  validation_cache_dir: data/execution_cache/al_cu_fe
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
```

Command placeholders:

- `{input}`: JSON payload path for the candidate and stage metadata
- `{output}`: JSON result path the command must write
- `{stage}`: stage label (`committee`, `phonon`, `md`, `xrd`)
- `{system}`: configured system name
- `{candidate_id}`: candidate identifier
- `{python}`: active interpreter path used by `mdisc`
- `{workspace_root}`: absolute path to the `materials-discovery/` workspace

Output contract:

- `committee`: `{"energies": {"MACE": ..., "CHGNet": ..., "MatterSim": ...}}`
- `phonon`: `{"imaginary_modes": 0}`
- `md`: `{"stability_score": 0.81}`
- `xrd`: `{"confidence": 0.77}`

If a cache entry exists for the same candidate/stage/config digest, the command is skipped and the cached result is reused. If no cache entry exists and the configured command is missing, the stage fails explicitly.

## Native Provider Path

`configs/systems/al_cu_fe_native.yaml` preserves the same exec command/cache contract but switches the runner internals to optional provider-specific backends.

- `committee_provider: ase_committee_v1`
- `phonon_provider: mace_hessian_v1`
- `md_provider: ase_langevin_v1`
- `xrd_provider: pymatgen_xrd_v1`

This path requires the MLIP extra:

```bash
cd materials-discovery
uv sync --extra dev --extra mlip
./scripts/run_native_pipeline.sh
```

Current limitation: the native path now consumes stored site coordinates directly, but those coordinates are still generated heuristically from the current Z[phi] template realization rather than from a full crystallographic construction.

## Quickstart

```bash
cd materials-discovery
uv sync --extra dev
uv run mdisc ingest --config configs/systems/al_cu_fe.yaml
uv run mdisc ingest --config configs/systems/al_cu_fe_real.yaml
uv run mdisc ingest --config configs/systems/al_cu_fe_exec.yaml
uv sync --extra dev --extra mlip
uv run mdisc generate --config configs/systems/al_cu_fe.yaml --count 50
uv run mdisc screen --config configs/systems/al_cu_fe.yaml
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch all
uv run mdisc hifi-rank --config configs/systems/al_cu_fe.yaml
uv run mdisc active-learn --config configs/systems/al_cu_fe.yaml
uv run mdisc report --config configs/systems/al_cu_fe.yaml
./scripts/run_real_pipeline.sh
./scripts/run_exec_pipeline.sh
./scripts/run_native_pipeline.sh
uv run pytest
uv run pytest -m integration
uv run ruff check .
uv run mypy src
```

## Exit codes

- `0`: success
- `2`: input/config/path validation error
