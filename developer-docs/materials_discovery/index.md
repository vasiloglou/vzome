# Materials Discovery Documentation

No-DFT materials discovery pipeline for quasicrystal-compatible structures, built on
Z[phi] geometry from [vZome Geometry Tutorial, Section 10.8](vzome-geometry-tutorial.md#108-materials-optimization-over-z%CF%86).

The pipeline generates candidate approximant structures whose atomic sites live in the
ring Z[phi]^3, screens them with ML interatomic potentials (MACE, CHGNet, MatterSim),
validates survivors with phonon, molecular dynamics, and XRD checks, and ranks the
results for experimental follow-up. All stages run without DFT.

## Status

All milestones (M1-M6) and real-mode execution phases (RM0-RM6) are implemented.
The codebase contains ~60 Python modules (7200+ LOC) with 22 test files covering
unit, integration, and end-to-end scenarios.

| Stage | CLI Command | Module |
|-------|-------------|--------|
| Ingest reference phases | `mdisc ingest` | `data/` |
| Export Zomic design | `mdisc export-zomic` | `generator/` + `core/` |
| Generate candidates | `mdisc generate` | `generator/` |
| Fast screening | `mdisc screen` | `screen/` |
| High-fidelity validation | `mdisc hifi-validate` | `hifi_digital/` |
| Ranking | `mdisc hifi-rank` | `hifi_digital/` |
| Active learning | `mdisc active-learn` | `active_learning/` |
| Experiment report | `mdisc report` | `diffraction/` |

## Quickstart

```bash
cd materials-discovery
uv sync --extra dev
uv run pytest                    # unit tests
uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
uv run mdisc generate  --config configs/systems/sc_zn_zomic.yaml --count 32
uv run mdisc ingest    --config configs/systems/al_cu_fe.yaml
uv run mdisc generate  --config configs/systems/al_cu_fe.yaml --count 50
uv run mdisc screen    --config configs/systems/al_cu_fe.yaml
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch all
uv run mdisc hifi-rank --config configs/systems/al_cu_fe.yaml
uv run mdisc active-learn --config configs/systems/al_cu_fe.yaml
uv run mdisc report    --config configs/systems/al_cu_fe.yaml
```

## Documentation Map

| Question | Document |
|----------|----------|
| How is the codebase organized? | [Architecture](architecture.md) |
| How does Z[phi] geometry work? | [Z[phi] Geometry & Candidate Generation](zphi-geometry.md) |
| How do I author designs in Zomic? | [Zomic Design Workflow](zomic-design-workflow.md) |
| What does each CLI command do? | [Pipeline Stages](pipeline-stages.md) |
| How do backend adapters work? | [Backend System](backend-system.md) |
| What are the YAML config options? | [Configuration Reference](configuration-reference.md) |
| What are the Pydantic data models? | [Data Schema Reference](data-schema-reference.md) |
| How do I set up development? | [Contributing](contributing.md) |

## Scope

**Primary goal**: A reproducible pipeline that generates quasicrystal-compatible
candidate structures, screens them with fast surrogate models, validates with
high-fidelity digital checks (no DFT), and ranks candidates for experimental follow-up.

**Non-goals (v0.1)**: Full autonomous lab integration, guaranteed aperiodic bulk
proof, universal potential quality across all chemistries.

## Chemical Systems

Three systems are configured out of the box:

| System | Template Family | Config |
|--------|----------------|--------|
| Al-Cu-Fe | Icosahedral 1/1 approximant | `configs/systems/al_cu_fe.yaml` |
| Al-Pd-Mn | Decagonal 2/1 proxy | `configs/systems/al_pd_mn.yaml` |
| Sc-Zn | Cubic 1/0 proxy | `configs/systems/sc_zn.yaml` |
| Sc-Zn (Zomic-authored) | Cubic 1/0 proxy via Zomic bridge | `configs/systems/sc_zn_zomic.yaml` |

Al-Cu-Fe has additional configs for real-mode progression:
`al_cu_fe_real.yaml` (fixture-backed), `al_cu_fe_exec.yaml` (command-backed),
`al_cu_fe_native.yaml` (native MLIP providers).

The Zomic-authored path depends on `vZome core` and requires a local Java runtime for
`mdisc export-zomic` and for `mdisc generate` when `zomic_design` is set.

## External Resources

- [HYPOD-X datasets](https://www.nature.com/articles/s41597-024-04043-z)
- [Matbench Discovery benchmark](https://www.nature.com/articles/s42256-025-01055-1)
- [CHGNet](https://github.com/CederGroupHub/chgnet) |
  [MACE](https://github.com/ACEsuit/mace) |
  [MatterSim](https://github.com/microsoft/mattersim)
- [Zomic Reference](../../core/docs/ZomicReference.md)
- [Quasicrystal ML discovery](https://doi.org/10.1103/PhysRevMaterials.7.093805)
- [QC structure prediction review](https://euler.phys.cmu.edu/widom/pubs/PDF/IJCR2023.pdf)
- [Deep-learning XRD for QC identification](https://pubmed.ncbi.nlm.nih.gov/37964402/)

## Related Documents

- [vZome Geometry Tutorial, Section 10.8](vzome-geometry-tutorial.md) — Mathematical motivation
- [Software Scaffold](materials-discovery-software-scaffold.md) — Original design blueprint (historical)
- [Real-Mode Execution Plan](../../materials-discovery/REAL_MODE_EXECUTION_PLAN.md) — RM0-RM6 execution plan
