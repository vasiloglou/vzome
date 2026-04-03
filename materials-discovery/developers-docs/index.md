# Materials Discovery Documentation

No-DFT materials discovery pipeline for quasicrystal-compatible structures, built on
Z[phi] geometry from [vZome Geometry Tutorial, Section 10.8](vzome-geometry-tutorial.md#108-materials-optimization-over-z%CF%86).

The pipeline generates candidate approximant structures whose atomic sites live in the
ring Z[phi]^3, screens them with ML interatomic potentials (MACE, CHGNet, MatterSim),
validates survivors with phonon, molecular dynamics, and XRD checks, and ranks the
results for experimental follow-up. All stages run without DFT.

Real/native validation now includes a cheap geometry prefilter before phonon so
obviously crowded structures fail quickly instead of consuming most of the
runtime in the native phonon backend.

## Status

All milestones (M1-M6) and real-mode execution phases (RM0-RM6) are implemented.
The codebase contains ~60 Python modules (7200+ LOC) with 22 test files covering
unit, integration, and end-to-end scenarios. LLM integration is in design phase.

| Stage | CLI Command | Module | Status |
|-------|-------------|--------|--------|
| Ingest reference phases | `mdisc ingest` | `data/` | Implemented |
| Export Zomic design | `mdisc export-zomic` | `generator/` + `core/` | Implemented |
| Generate candidates | `mdisc generate` | `generator/` | Implemented |
| Fast screening | `mdisc screen` | `screen/` | Implemented |
| High-fidelity validation | `mdisc hifi-validate` | `hifi_digital/` | Implemented |
| Ranking | `mdisc hifi-rank` | `hifi_digital/` | Implemented |
| Active learning | `mdisc active-learn` | `active_learning/` | Implemented |
| Experiment report | `mdisc report` | `diffraction/` | Implemented |
| LLM-powered generation | `mdisc llm-generate` | `llm/` | Planned |
| LLM-powered evaluation | `mdisc llm-evaluate` | `llm/` | Planned |
| LLM-guided suggestions | `mdisc llm-suggest` | `llm/` | Planned |

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

# Sc-Zn calibrated real mode
uv run mdisc ingest --config configs/systems/sc_zn_real.yaml
uv run mdisc generate --config configs/systems/sc_zn_real.yaml --count 64
uv run mdisc screen --config configs/systems/sc_zn_real.yaml
uv run mdisc hifi-validate --config configs/systems/sc_zn_real.yaml --batch all
uv run mdisc hifi-rank --config configs/systems/sc_zn_real.yaml
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
| How do LLMs and AI interact with quasicrystals? | [LLM & Quasicrystal Landscape](llm-quasicrystal-landscape.md) |
| How will LLMs generate quasicrystals? | [LLM Integration](llm-integration.md) |
| How do we build the Zomic training corpus? | [Zomic LLM Data Plan](zomic-llm-data-plan.md) |

## Scope

**Primary goal**: A reproducible pipeline that generates quasicrystal-compatible
candidate structures, screens them with fast surrogate models, validates with
high-fidelity digital checks (no DFT), and ranks candidates for experimental follow-up.

**Non-goals (v0.1)**: Full autonomous lab integration, guaranteed aperiodic bulk
proof, universal potential quality across all chemistries.

## Chemical Systems

Four systems are configured out of the box:

| System | Template Family | Config |
|--------|----------------|--------|
| Al-Cu-Fe | Icosahedral 1/1 approximant | `configs/systems/al_cu_fe.yaml` |
| Al-Pd-Mn | Decagonal 2/1 proxy | `configs/systems/al_pd_mn.yaml` |
| Sc-Zn | Cubic 1/0 proxy | `configs/systems/sc_zn.yaml` |
| Ti-Zr-Ni | Icosahedral 1/1 approximant | `configs/systems/ti_zr_ni.yaml` |
| Sc-Zn (Zomic-authored) | Cubic 1/0 proxy via Zomic bridge, expanded onto five `ScZn6` anchor orbits | `configs/systems/sc_zn_zomic.yaml` |
| Sc-Zn (real calibrated) | Zomic bridge + pinned Sc-Zn calibration pack | `configs/systems/sc_zn_real.yaml` |
| Sc-Zn (native MLIP) | Zomic bridge + native providers | `configs/systems/sc_zn_native.yaml` |

Additional real-mode configs:
- `al_cu_fe_real.yaml`: fixture-backed real mode
- `al_cu_fe_exec.yaml`: command-backed real mode
- `al_cu_fe_native.yaml`: native MLIP providers
- `sc_zn_real.yaml`: pinned `Sc-Zn` benchmark + validation snapshot
- `sc_zn_native.yaml`: native MLIP providers for `Sc-Zn`

The native MLIP path should be installed into a Python 3.11 `uv` environment:

```bash
uv sync --python 3.11 --extra dev --extra mlip
```

The Zomic-authored path depends on `vZome core` and requires a local Java runtime for
`mdisc export-zomic` and for `mdisc generate` when `zomic_design` is set.

## External Resources

### Databases & Datasets
- [HYPOD-X datasets](https://www.nature.com/articles/s41597-024-04043-z) — Comprehensive QC + approximant data
- [Matbench Discovery benchmark](https://www.nature.com/articles/s42256-025-01055-1)
- [NIMS Materials Data Repository](https://mdr.nims.go.jp/) — TSAI model training data
- [Bilbao Incommensurate Structures DB](https://www.cryst.ehu.eus/bincstrdb/) — Superspace formalism

### ML Interatomic Potentials (integrated)
- [CHGNet](https://github.com/CederGroupHub/chgnet) |
  [MACE](https://github.com/ACEsuit/mace) |
  [MatterSim](https://github.com/microsoft/mattersim)

### Crystal-Generating LLMs
- [CrystaLLM](https://github.com/lantunes/CrystaLLM) — GPT-2 trained on CIF ([Nature Comms 2024](https://www.nature.com/articles/s41467-024-54639-7))
- [CrystalTextLLM](https://github.com/facebookresearch/crystal-text-llm) — Fine-tuned LLaMA-2 ([ICLR 2024](https://arxiv.org/abs/2402.04379))
- [MatLLMSearch](https://arxiv.org/abs/2502.20933) — Evolution-guided, training-free
- [CSLLM](https://github.com/szl666/CSLLM) — 98.6% synthesizability accuracy ([Nature Comms 2025](https://www.nature.com/articles/s41467-025-61778-y))

### Quasicrystal-Specific ML
- [TSAI model — first ML-discovered QCs](https://doi.org/10.1103/PhysRevMaterials.7.093805)
- [Deep-learning PXRD for QC identification](https://github.com/SuperspaceLab/ml-qc-pxrd) ([Advanced Science 2024](https://advanced.onlinelibrary.wiley.com/doi/full/10.1002/advs.202304546))
- [NN-VMC electronic quasicrystals](https://arxiv.org/abs/2512.10909)
- [SCIGEN — diffusion model with geometric constraints](https://github.com/RyotaroOKabe/SCIGEN) ([Nature Materials 2025](https://www.nature.com/articles/s41563-025-02355-y))

### Quasicrystal Tools
- [PyQCstrc — 6D icosahedral QC modeling](https://pmc.ncbi.nlm.nih.gov/articles/PMC8366420/)
- [Jana2020 — superspace refinement](https://jana.fzu.cz/)
- [Zomic Reference](../../core/docs/ZomicReference.md)

### Theoretical
- [LLM as quasi-crystal analogy](https://arxiv.org/abs/2504.11986)
- [Aperiodic approximants bridging QCs and modulated structures](https://www.nature.com/articles/s41467-024-49843-4)

## Related Documents

- [vZome Geometry Tutorial, Section 10.8](vzome-geometry-tutorial.md) — Mathematical motivation
- [Software Scaffold](materials-discovery-software-scaffold.md) — Original design blueprint (historical)
- [Real-Mode Execution Plan](../../materials-discovery/REAL_MODE_EXECUTION_PLAN.md) — RM0-RM6 execution plan
- [LLM Integration Architecture](llm-integration.md) — LLM-powered generation and evaluation
- [Zomic LLM Data Plan](zomic-llm-data-plan.md) — Training corpus construction
