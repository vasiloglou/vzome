# LLM Integration for Quasicrystal Discovery

This document describes how Large Language Models (LLMs) can be integrated into the
materials discovery pipeline to generate and evaluate quasicrystal-compatible
structures using the Zomic language as the native representation format.

---

## 1. Motivation

### The CIF Barrier

Most crystal-generating LLMs — CrystaLLM, CrystalTextLLM, MatLLMSearch — are trained
to read and generate Crystallographic Information Files (CIFs). CIF fundamentally
relies on periodic boundary conditions: a repeating 3D unit cell described by one of
the 230 space groups. Quasicrystals exhibit long-range order but strictly lack
translational periodicity. They cannot be accurately described by standard 3D unit
cells. To properly represent a quasicrystal, lattice math must be scaled up to 4, 5,
or 6 dimensions and projected into 3D. No standard CIF dictionary covers this fully
(the IUCr `msCIF` dictionary handles modulated structures but not quasicrystals in
5D/6D superspace).

**Result**: Current text-based crystal LLMs cannot natively generate true quasicrystal
structures.

### Why Zomic Is the Right Representation

The Zomic language solves this problem:

| Property | CIF | Zomic |
|---|---|---|
| Coordinate system | Standard 3D lattice + space group | Golden field Z[phi]³ (exact algebraic) |
| Periodicity assumption | Required (unit cell) | None (aperiodic by construction) |
| Geometry | Cartesian/fractional coordinates | Procedural turtle graphics in icosahedral directions |
| Symmetry | Space group number | Explicit symmetry operators (rotational, mirror, icosahedral) |
| Compositionality | Flat list of atom positions | Nested, hierarchical construction (branch, repeat, symmetry) |
| Size | Typically 50-500 lines per structure | Compact: 5-50 lines for complex motifs |
| LLM compatibility | Proven (CrystaLLM, CrystalTextLLM) | Untested but structurally ideal |

Key advantages of Zomic for LLMs:

1. **Native aperiodicity.** Zomic operates in the golden field where phi-scaled
   struts naturally generate quasicrystal-compatible geometry without periodic
   boundary conditions.

2. **Compositional structure.** Zomic scripts are hierarchical programs with
   nesting (branch, repeat, symmetry) — structurally parallel to natural language.
   An LLM can learn to compose geometric motifs the same way it composes sentences.

3. **Compact representation.** A 100-atom quasicrystal motif can be described in
   20 lines of Zomic, compared to 100+ lines of CIF coordinates. This fits easily
   within transformer context windows.

4. **Built-in validation.** Generated Zomic can be parsed by the ANTLR4 grammar,
   compiled by the vZome core, and geometrically validated — all before expensive
   MLIP screening.

5. **The LLM-quasicrystal analogy.** Research has drawn a formal analogy between
   how LLMs produce coherent non-repeating text from local token prediction and how
   quasicrystals produce coherent non-repeating structure from local geometric rules
   (Penrose tile matching). Both systems create structured, complex emergent patterns
   without a centralized repeating blueprint.

---

## 2. Literature & Reference Compendium

### 2.1 Crystal-Generating LLMs

| Model | Architecture | Key Result | Reference | Code |
|---|---|---|---|---|
| **CrystaLLM** | GPT-2 trained on CIF files | Generates valid crystal structures as text | [Antunes et al., Nature Comms 2024](https://www.nature.com/articles/s41467-024-54639-7) / [arXiv:2307.04340](https://arxiv.org/abs/2307.04340) | [github.com/lantunes/CrystaLLM](https://github.com/lantunes/CrystaLLM) |
| **CrystalTextLLM** | Fine-tuned LLaMA-2 70B | ~49% metastable rate (vs 28% for CDVAE) | [Gruver et al., ICLR 2024](https://arxiv.org/abs/2402.04379) | [github.com/facebookresearch/crystal-text-llm](https://github.com/facebookresearch/crystal-text-llm) |
| **MatLLMSearch** | Evolution-guided LLM (training-free) | 78.4% metastable rate, 31.7% DFT-verified | [Gan et al., 2025](https://arxiv.org/abs/2502.20933) | No public repo |

### 2.2 Synthesizability & Precursor Prediction

| Model | Key Result | Reference | Code |
|---|---|---|---|
| **CSLLM** | 98.6% synthesizability accuracy; predicts precursors | [Song et al., Nature Comms 2025](https://www.nature.com/articles/s41467-025-61778-y) / [arXiv:2407.07016](https://arxiv.org/abs/2407.07016) | [github.com/szl666/CSLLM](https://github.com/szl666/CSLLM) |

### 2.3 Machine-Learned Interatomic Potentials (MLIPs)

Already integrated in our pipeline. Key references:

| Model | Reference | Code |
|---|---|---|
| **MACE** | [Batatia et al., NeurIPS 2022](https://arxiv.org/abs/2206.07697); Foundation model: [arXiv:2401.00096](https://arxiv.org/abs/2401.00096) | [github.com/ACEsuit/mace](https://github.com/ACEsuit/mace) |
| **CHGNet** | [Deng et al., Nature Machine Intelligence 2023](https://www.nature.com/articles/s42256-023-00716-3) | [github.com/CederGroupHub/chgnet](https://github.com/CederGroupHub/chgnet) |
| **MatterSim** | [Yang et al., 2024](https://arxiv.org/abs/2405.04967) | [github.com/microsoft/mattersim](https://github.com/microsoft/mattersim) |

### 2.4 Generative Diffusion Models

| Model | Key Result | Reference | Code |
|---|---|---|---|
| **SCIGEN** | 8M compounds with Archimedean lattice constraints; >10% pass stability | [Okabe et al., Nature Materials 2025](https://www.nature.com/articles/s41563-025-02355-y) / [arXiv:2407.04557](https://arxiv.org/abs/2407.04557) | [github.com/RyotaroOKabe/SCIGEN](https://github.com/RyotaroOKabe/SCIGEN) |

### 2.5 Quasicrystal-Specific ML

| Model | Type | Key Result | Reference | Code |
|---|---|---|---|---|
| **TSAI** | Random Forest classifier | First QCs discovered by ML: Al65Ni20Os15, Al78Ir17Mn5, Al78Ir17Fe5 | [Liu et al., Phys Rev Materials 2023](https://doi.org/10.1103/PhysRevMaterials.7.093805); [Liu et al., Adv Materials 2021](https://advanced.onlinelibrary.wiley.com/doi/abs/10.1002/adma.202102507) | NIMS MDR dataset |
| **Deep-learning PXRD** | CNN for QC identification | >92% accuracy; discovered new Al-Si-Ru icosahedral QC | [Uryu et al., Advanced Science 2024](https://advanced.onlinelibrary.wiley.com/doi/full/10.1002/advs.202304546) | [github.com/SuperspaceLab/ml-qc-pxrd](https://github.com/SuperspaceLab/ml-qc-pxrd) |
| **NN-VMC** | Neural-network variational Monte Carlo | Discovered electronic quasicrystal phase | [Gaggioli et al., 2024](https://arxiv.org/abs/2512.10909) | — |

### 2.6 Theoretical Connections

| Topic | Reference |
|---|---|
| LLM as quasi-crystals analogy | [Guevara-Vela, 2025](https://arxiv.org/abs/2504.11986) |
| Lifshitz-Petrich + graph autoencoder for QC phases | [arXiv:2509.11293](https://arxiv.org/abs/2509.11293) |
| Aperiodic approximants bridging QC and modulated structures | [Nature Comms 2024](https://www.nature.com/articles/s41467-024-49843-4) / [arXiv:2403.16010](https://arxiv.org/abs/2403.16010) |

### 2.7 Databases & Datasets

| Database | Content | Access |
|---|---|---|
| **HYPOD-X** | Comprehensive QC + approximant compositions, phases, properties (~1000 entries) | [Nature Scientific Data 2024](https://www.nature.com/articles/s41597-024-04043-z) / [Figshare](https://figshare.com/articles/dataset/HYPOD_comprehensive_experimental_datasets_of_quasicrystals_and_their_approximants/25650705) |
| **ICSD** | 290k+ periodic inorganic structures (includes QC approximants, not true QCs) | [icsd.products.fiz-karlsruhe.de](https://icsd.products.fiz-karlsruhe.de/) |
| **NIMS MDR** | TSAI model training data, QC-related datasets | [mdr.nims.go.jp](https://mdr.nims.go.jp/) |
| **B-IncStrDB** | Bilbao incommensurate structures (277 entries, superspace formalism) | [cryst.ehu.eus/bincstrdb](https://www.cryst.ehu.eus/bincstrdb/) |
| **Robbin QC cells** | 2,500 quasicrystal cells | [arXiv:1805.11457](https://arxiv.org/abs/1805.11457) |

### 2.8 Computational Tools for Quasicrystals

| Tool | Purpose | Access |
|---|---|---|
| **PyQCstrc** | 6D structure models of icosahedral QCs | [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC8366420/) |
| **Jana2020** | Superspace refinement for aperiodic structures | [jana.fzu.cz](https://jana.fzu.cz/) |
| **QUASI** | QC structure analysis (Fortran) | [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC5099788/) |
| **msCIF dictionary** | CIF extension for modulated structures | [IUCr](https://www.iucr.org/resources/cif/dictionaries/cif_ms) |

---

## 3. LLM Integration Architecture

### 3.1 Two New Pipeline Stages

The pipeline gains two LLM-powered stages that sit alongside (not replacing) the
existing generation and evaluation paths:

#### `mdisc llm-generate` — LLM-Powered Candidate Generation

**Input:**
- Composition constraints (e.g., `Sc: 0.15-0.40, Zn: 0.60-0.85`)
- Target properties (optional: energy range, stability class)
- Seed Zomic script (optional: starting motif to extend/vary)
- Temperature / sampling parameters

**Process:**
1. Format prompt with composition + optional seed Zomic
2. LLM generates one or more Zomic scripts
3. Each script is validated: parsed by ANTLR4 grammar, checked for syntax errors
4. Valid scripts are compiled via vZome core → labeled geometry JSON
5. Zomic bridge converts labeled geometry → orbit library → CandidateRecord
6. Candidates enter the normal `screen → validate → rank` pipeline

**Output:**
- CandidateRecord JSONL (same format as `mdisc generate`)
- Generation provenance includes `source: "llm"`, model ID, prompt, temperature

**Key design choice:** The LLM generates Zomic text, not coordinates. The Zomic
compiler handles the geometry exactly. This means even an imperfect LLM output is
either valid Zomic (and geometrically exact) or invalid (caught by the parser). There
is no "approximately right" failure mode that could poison the pipeline.

#### `mdisc llm-evaluate` — LLM-Powered Candidate Assessment

**Input:**
- CandidateRecord (from any generation source)
- Validation results (committee energies, phonon, MD, XRD)

**Process:**
1. Serialize candidate structure and validation data as a structured prompt
2. LLM assesses:
   - **Synthesizability score** (inspired by CSLLM: can this actually be made?)
   - **Precursor suggestions** (what starting materials are needed?)
   - **Anomaly detection** (are validation results internally consistent?)
   - **Literature context** (does this composition/structure match known QC families?)
3. LLM assessment is attached to the CandidateRecord

**Output:**
- Enriched CandidateRecord with `llm_assessment` block
- Can be used by `mdisc report` for experiment-facing summaries

**Key design choice:** This stage uses a general-purpose LLM (e.g., Claude, GPT-4)
with prompt engineering rather than a fine-tuned model, since it needs broad chemistry
knowledge rather than Zomic-specific generation ability.

#### `mdisc llm-suggest` — LLM-Guided Active Learning (Future)

A third stage that replaces or augments the current `active-learn` surrogate:
- LLM analyzes the full set of validated candidates and their properties
- Proposes new composition regions to explore (outside the current bounds)
- Suggests structural motifs (in Zomic) that might stabilize failing candidates
- Feeds back into `llm-generate` for the next exploration cycle

### 3.2 Backend Adapter for LLM

Following the existing adapter pattern:

```
backends/
  llm_mock.py          Deterministic fixture responses for testing
  llm_api.py           API-based adapter (Claude, GPT-4, local server)
  llm_local.py         Local model adapter (HuggingFace transformers, vLLM)
```

Configuration in system YAML:

```yaml
backend:
  llm_adapter: "api"           # mock | api | local
  llm_provider: "claude"       # claude | openai | local
  llm_model: "claude-sonnet-4-6"
  llm_generate_model: "zomic-llm-v1"   # fine-tuned model for generation
  llm_temperature: 0.7
  llm_max_tokens: 2048
```

### 3.3 Revised Pipeline Data Flow

```
Config YAML
    |
    v
cli.py loads SystemConfig
    |
    ├──────────────────────────────────────────────────────────┐
    v                                                          v
EXISTING PATH                                          LLM PATH
    |                                                          |
    v                                                          v
INGEST                                               LLM-GENERATE
    |                                            (composition → Zomic → candidates)
    v                                                          |
GENERATE (Z[phi] + Zomic bridge)                              |
    |                                                          |
    └────────────────────┬─────────────────────────────────────┘
                         v
                    SCREEN (fast MLIP relaxation, filtering)
                         |
                         v
                    HIFI-VALIDATE (committee, phonon, MD, XRD)
                         |
                    ┌────┴────┐
                    v         v
            LLM-EVALUATE   HIFI-RANK
            (synthesizability,    |
             precursors,          |
             anomalies)           |
                    |             |
                    └──────┬──────┘
                           v
                    ACTIVE-LEARN / LLM-SUGGEST
                           |
                           v
                        REPORT
```

---

## 4. Fine-Tuning Strategy

### 4.1 Base Model Selection

| Option | Pros | Cons |
|---|---|---|
| **LLaMA-3 8B** | Proven for crystal generation (CrystalTextLLM precedent); efficient fine-tuning with LoRA; runs locally | Smaller context window |
| **Mistral 7B** | Strong reasoning; efficient; good for structured output | Less precedent in materials science |
| **Qwen-2.5 7B** | Multilingual; strong code generation | Less community tooling for science fine-tuning |

**Recommendation:** Start with LLaMA-3 8B using QLoRA, following the CrystalTextLLM
methodology but replacing CIF with Zomic.

### 4.2 Training Data Format

Each training example is a structured text record:

```
<system>Sc-Zn</system>
<composition>Sc0.15Zn0.85</composition>
<template>cubic_proxy_1_0</template>
<cell>a=13.79 b=13.79 c=13.79 alpha=90 beta=90 gamma=90</cell>
<zomic>
branch {
  label pent.top.center
  short blue -12
  label pent.top.left
  symmetry around red +0
    branch { size 7 purple +0 label frustum.side }
}
</zomic>
<properties>
energy_ev_per_atom: -3.21
phonon_pass: true
md_pass: true
uncertainty: 0.018
</properties>
```

### 4.3 Two-Phase Training

**Phase 1 — Zomic Language Proficiency:**
- Train on all available Zomic scripts (~150 from regression tests + part definitions)
- Objective: learn Zomic grammar, valid axis combinations, symmetry operators
- Loss: next-token prediction on Zomic text
- Validation: % of generated scripts that parse successfully with ANTLR4
- Target: >95% parse rate

**Phase 2 — Materials-Conditioned Generation:**
- Fine-tune on Zomic + composition + property triplets
- Data from: pipeline-generated candidates with validation results, converted CIF structures
- Objective: given composition → generate Zomic that produces stable structures
- Loss: next-token prediction on Zomic conditioned on composition prefix
- Validation: % of generated candidates that pass screening + % that pass hifi-validate
- Target: >50% screen pass rate (comparable to MatLLMSearch's 78% for periodic)

### 4.4 Zomic-Specific Tokenization

Extend the base tokenizer vocabulary with Zomic-specific tokens:

```
# Direct statement keywords
strut, rotate, scale, build, move, label

# Nested statement keywords
branch, from, repeat, symmetry, save

# Axis names
red, blue, yellow, green, orange, purple

# Size keywords
short, medium, long, size, half

# Symmetry keywords
around, through, center

# Structure tokens
{, }, //, /*

# Special tokens for materials context
<system>, </system>, <composition>, </composition>
<template>, </template>, <cell>, </cell>
<zomic>, </zomic>, <properties>, </properties>
```

This keeps Zomic keywords as single tokens rather than being split across subwords,
improving generation coherence.

---

## 5. Data Sources & Conversion Paths

Detailed in [Zomic LLM Data Plan](zomic-llm-data-plan.md). Summary:

| Source | Est. Examples | Status |
|---|---|---|
| Existing Zomic scripts | ~150 | Ready |
| Pipeline-generated candidates (reverse-engineered) | 1,000-10,000 | Needs `record2zomic` converter |
| HYPOD-X approximant structures | ~500 CIFs | Needs `cif2zomic` converter |
| ICSD approximant structures | ~200 CIFs | Needs `cif2zomic` converter |
| PyQCstrc 6D→3D projections | ~100 structures | Needs `projection2zomic` converter |
| Augmented variants (symmetry, scale, composition) | 10x multiplier | Needs augmentation pipeline |

**Total estimated corpus: 10,000-50,000 training examples** after augmentation.

---

## 6. Evaluation Framework

### 6.1 Syntactic Validation
- Parse generated Zomic with ANTLR4 grammar
- Metric: **Parse success rate** (target >95%)

### 6.2 Geometric Validation
- Compile parsed Zomic via vZome core
- Check for collisions (minimum site separation)
- Metric: **Geometric validity rate** (target >80%)

### 6.3 Physical Validation
- Run valid candidates through the existing screening pipeline
- Metric: **Screen pass rate** (target >30%)
- Metric: **HiFi validation pass rate** (target >10%)

### 6.4 Novelty Assessment
- Compare generated structures against training data (Zomic edit distance)
- Compare against known QC/approximant structures (coordinate RMSD)
- Metric: **Novelty rate** (fraction of candidates not near-duplicates of training)

### 6.5 Diversity Assessment
- Measure structural diversity within a generation batch
- Metric: **Intra-batch diversity** (average pairwise Zomic edit distance)

---

## 7. Implementation Roadmap

### Phase 0 — Data Infrastructure (prerequisites)
- [ ] Build `record2zomic` converter (CandidateRecord → Zomic script)
- [ ] Build `cif2zomic` converter (CIF → Zomic script via coordinate matching)
- [ ] Download and process HYPOD-X dataset
- [ ] Generate pipeline training data: run pipeline for all 3 systems, 10k candidates each

### Phase 1 — Zomic Language Model
- [ ] Prepare Zomic training corpus (combine all sources from Phase 0)
- [ ] Train base Zomic model (LLaMA-3 8B + QLoRA)
- [ ] Evaluate parse success rate on held-out test set
- [ ] Iterate until >95% parse rate

### Phase 2 — Materials-Conditioned Generation
- [ ] Prepare materials training data (Zomic + composition + properties)
- [ ] Fine-tune on materials-conditioned generation
- [ ] Implement `mdisc llm-generate` CLI command
- [ ] Evaluate screen pass rate
- [ ] Iterate until >30% screen pass rate

### Phase 3 — LLM Evaluation
- [ ] Implement `mdisc llm-evaluate` CLI command
- [ ] Design synthesizability prompt (inspired by CSLLM)
- [ ] Design anomaly detection prompt
- [ ] Integrate LLM assessment into report stage

### Phase 4 — Active Learning Loop
- [ ] Implement `mdisc llm-suggest` CLI command
- [ ] Connect LLM suggestions to `llm-generate` for closed-loop exploration
- [ ] Benchmark against traditional `active-learn` surrogate

---

## 8. Risk Analysis

| Risk | Mitigation |
|---|---|
| Insufficient Zomic training data (<1000 examples) | Aggressive augmentation; synthetic data generation via pipeline |
| LLM generates syntactically valid but physically meaningless structures | Physical validation catches this; focus on Phase 2 conditioning |
| Fine-tuned model overfits to known QC families | Track novelty metrics; use temperature sampling; add composition diversity constraints |
| Computational cost of generating + validating LLM candidates | Batch generation; filter at parse stage before expensive MLIP screening |
| Zomic tokenization issues (rare axis combinations) | Custom tokenizer; ensure all axis/size combinations appear in training |

---

## 9. Connections to Existing Pipeline

The LLM integration reuses these existing components without modification:

| Component | Used By |
|---|---|
| `generator/zomic_bridge.py` | `llm-generate` (compiles LLM-generated Zomic to orbits) |
| `generator/candidate_factory.py` | `llm-generate` (wraps orbits into CandidateRecord) |
| `screen/` | Both LLM and traditional candidates flow through screening |
| `hifi_digital/` | Both LLM and traditional candidates flow through validation |
| `backends/` | LLM adapter follows same pattern; existing MLIP adapters unchanged |
| `common/schema.py` | CandidateRecord gains optional `llm_assessment` field |
| `cli.py` | Two new typer commands added |

The design principle is: **LLMs generate Zomic, not structures.** All downstream
processing uses the same validated pipeline, regardless of whether candidates were
generated by Z[phi] geometry, Zomic bridge, or LLM.
