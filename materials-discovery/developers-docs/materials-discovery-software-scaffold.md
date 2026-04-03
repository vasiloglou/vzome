# Materials Discovery Software Scaffold

> **Historical document.** This was the original design blueprint for the materials
> discovery pipeline. For current documentation derived from the actual implementation,
> see **[Materials Discovery Documentation](index.md)**.

Companion to Chapter 10.8 in [vZome Geometry Tutorial](vzome-geometry-tutorial.md).

---

## Original Scope

Build a reproducible pipeline that can:

1. Generate candidate quasicrystal-compatible structures using Z[phi] geometry.
2. Screen them with fast ML interatomic potentials (MACE, CHGNet, MatterSim).
3. Refine top candidates with high-fidelity digital validation (no DFT required).
4. Rank candidates for experimental follow-up.

## Implementation Status

All milestones (M1-M6) and real-mode execution phases (RM0-RM6) are implemented.
See the [current documentation](index.md) for details.

## Current Documentation

| Topic | Document |
|-------|----------|
| Overview and quickstart | [index.md](index.md) |
| System architecture | [architecture.md](architecture.md) |
| Z[phi] geometry engine | [zphi-geometry.md](zphi-geometry.md) |
| Zomic design workflow | [zomic-design-workflow.md](zomic-design-workflow.md) |
| Pipeline stage reference | [pipeline-stages.md](pipeline-stages.md) |
| Backend adapter system | [backend-system.md](backend-system.md) |
| Configuration reference | [configuration-reference.md](configuration-reference.md) |
| Data schema reference | [data-schema-reference.md](data-schema-reference.md) |
| Developer guide | [contributing.md](contributing.md) |

## External Resources

- [HYPOD-X datasets](https://www.nature.com/articles/s41597-024-04043-z)
- [Matbench Discovery benchmark](https://www.nature.com/articles/s42256-025-01055-1)
- [CHGNet](https://github.com/CederGroupHub/chgnet) |
  [MACE](https://github.com/ACEsuit/mace) |
  [MatterSim](https://github.com/microsoft/mattersim)
- [Quasicrystal ML discovery](https://doi.org/10.1103/PhysRevMaterials.7.093805)
- [QC structure prediction review](https://euler.phys.cmu.edu/widom/pubs/PDF/IJCR2023.pdf)
- [Deep-learning XRD for QC identification](https://pubmed.ncbi.nlm.nih.gov/37964402/)

## Real-Mode Execution Plan

For the RM0-RM6 execution plan (March-August 2026), see:

- `materials-discovery/REAL_MODE_EXECUTION_PLAN.md`
