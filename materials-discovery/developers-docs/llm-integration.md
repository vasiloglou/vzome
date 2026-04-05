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

The pipeline gains LLM-powered stages that sit alongside (not replacing) the
existing generation and evaluation paths. Phase 7 implements the first
`mdisc llm-generate` MVP with mock coverage plus one hosted-provider seam.
Phase 8 adds `mdisc llm-evaluate`, additive report integration, and an offline
downstream benchmark lane. Phase 9 adds typed eval sets, acceptance packs, and
a dry-run `mdisc llm-suggest` surface.

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
- Stage calibration + manifest output
- Run-level audit artifacts (`prompt.json`, `attempts.jsonl`,
  `compile_results.jsonl`, `run_manifest.json`) under `data/llm_runs/`

**Key design choice:** The LLM generates Zomic text, not coordinates. The Zomic
compiler handles the geometry exactly. This means even an imperfect LLM output is
either valid Zomic (and geometrically exact) or invalid (caught by the parser). There
is no "approximately right" failure mode that could poison the pipeline.

#### `mdisc llm-evaluate` — LLM-Powered Candidate Assessment

**Input:**
- Ranked CandidateRecord JSONL by default (`data/ranked/{system}_ranked.jsonl`)
- Validation results already embedded in each candidate (committee energies,
  phonon, MD, XRD)

**Process:**
1. Serialize candidate structure and validation data as a structured prompt
2. LLM assesses:
   - **Synthesizability score** (inspired by CSLLM: can this actually be made?)
   - **Precursor suggestions** (what starting materials are needed?)
   - **Anomaly detection** (are validation results internally consistent?)
   - **Literature context** (does this composition/structure match known QC families?)
3. LLM assessment is attached to the CandidateRecord

**Output:**
- Enriched CandidateRecord JSONL under `data/llm_evaluated/`
- Run-level audit artifacts (`requests.jsonl`, `assessments.jsonl`,
  `run_manifest.json`) under `data/llm_evaluations/`
- Can be used by `mdisc report` for experiment-facing summaries

**Key design choice:** The default evaluation lane is still a general-purpose
LLM with prompt engineering, but Phase 20 adds an honest
`specialized_materials` evaluation lane. That specialized lane is
evaluation-primary: it can add synthesis-aware or structure-aware assessment
without claiming mature direct Zomic generation.

#### `mdisc llm-suggest` — LLM-Guided Acceptance Suggestions (Phase 9 Dry Run)

The current Phase 9 surface is intentionally lightweight and operator-facing:
- `run_llm_acceptance_benchmarks.sh` computes a typed acceptance pack from the
  Phase 7 and Phase 8 benchmark artifacts
- `mdisc llm-suggest --acceptance-pack ...` reads that pack and emits structured
  next-step proposal bundles without executing a new search loop
- Suggestions are aligned to existing workflow concepts: prompt validity,
  composition-conditioned example quality, downstream pass-through, and release
  readiness

This is a dry-run decision aid, not yet a fully autonomous closed loop.

#### `mdisc llm-approve` — Campaign Approval and Spec Materialization (Phase 10)

Phase 10 adds the governance boundary that sits between dry-run suggestions and
any future closed-loop launch path:
- `mdisc llm-approve --proposal ... --decision approved|rejected --operator ...`
  writes a separate typed approval artifact under the acceptance-pack root
- approved proposals require a system config and materialize a self-contained
  `campaign_spec.json` under `data/llm_campaigns/{campaign_id}/`
- rejected proposals stop at the approval artifact and do not produce a launch
  spec
- the command does not call `llm-generate`, does not write candidate JSONL, and
  does not mutate active-learning state

This keeps the workflow file-backed and operator-governed while still giving
Phase 11 a durable contract to launch and replay later.

#### `mdisc llm-launch` — Campaign Execution Bridge (Phase 11)

Phase 11 turns approved campaign specs into a real launch path without adding a
second candidate-generation engine:
- `mdisc llm-launch --campaign-spec ...` validates the pinned system-config hash
  before any provider execution begins
- the command writes `resolved_launch.json` and `launch_summary.json` under
  `data/llm_campaigns/{campaign_id}/launches/{launch_id}/`
- launch resolution stays additive: prompt deltas, composition-window changes,
  seed handling, and lane selection are resolved in memory and then passed into
  the existing `generate_llm_candidates()` runtime
- launched runs still write the standard candidate JSONL, standard
  `llm_generate` manifest, and standard run-level artifacts under
  `data/llm_runs/`

Phase 11 deliberately keeps later stages manual:
- `llm-launch` produces standard candidates and launch wrapper artifacts
- operators then continue with the existing commands such as `mdisc screen`,
  `mdisc hifi-validate`, `mdisc hifi-rank`, and `mdisc report`
- downstream stage manifests now preserve additive `source_lineage.llm_campaign`
  data so launched runs remain traceable after they enter the normal pipeline

Failure posture in Phase 11:
- partial launch artifacts are preserved
- failed launches still write `launch_summary.json` with status `failed`
- there is no resume path yet; retries are explicit fresh launches

**Lineage Audit**

For any launched run, the trace path is:
1. downstream manifest or pipeline manifest `source_lineage.llm_campaign`
2. `launch_summary_path`
3. `resolved_launch_path`
4. `campaign_spec_path`
5. approval artifact and acceptance-pack lineage referenced by the campaign spec

This gives operators a file-backed audit chain from a later pipeline stage back
to the approved proposal and benchmark context that triggered the launch.

#### `mdisc llm-replay` and `mdisc llm-compare` — Replay and Comparison Workflow (Phase 12)

Phase 12 adds the reproducibility and operator-interpretation layer on top of
the Phase 11 launch bridge:
- `mdisc llm-replay --launch-summary ...` uses the recorded launch bundle as the
  primary authority, not the approval artifact alone
- replay reads the original `launch_summary.json`, `resolved_launch.json`,
  `run_manifest.json`, and `prompt.json`, reconstructs the same effective
  request, and then launches a fresh run with a new `launch_id`
- the command records the current config hash alongside the source launch
  identity so operators can detect drift, but it deliberately exposes no
  override knobs in Phase 12
- replay writes a new launch wrapper under
  `data/llm_campaigns/{campaign_id}/launches/{launch_id}/` and keeps the
  existing standard `llm_generate` artifacts under `data/llm_runs/`

The strict replay posture is deliberate:
- the workflow is meant to answer "what happens if we rerun this exact launch
  contract?" rather than "what nearby launch should we try next?"
- if the recorded launch bundle is missing or inconsistent, replay fails
  instead of silently substituting new behavior

`mdisc llm-compare --launch-summary ...` then turns a launch or replay into a
stable comparison unit:
- it always builds or reuses an immutable `outcome_snapshot.json` for the
  targeted launch
- it always compares against the originating acceptance-pack baseline for the
  system
- it also compares against the most recent prior launch for the same campaign
  and system when one exists
- missing downstream metrics stay explicit in `missing_metrics`; they are not
  coerced to zero just to make comparisons easier

Why the outcome snapshot matters:
- later stages may evolve, but the snapshot freezes the specific parse,
  compile, generation, and available downstream metrics that belonged to one
  launch at one point in time
- comparison artifacts can then reference those frozen snapshots without
  recomputing history or depending on mutable notebook logic

Phase 12 still keeps the workflow additive:
- `llm-suggest` stays dry-run
- `llm-approve` stays governance-only
- `llm-launch` and `llm-replay` stop at candidate generation plus audit
  artifacts
- downstream stages such as `screen`, `hifi-validate`, `hifi-rank`, and
  `report` remain manual/operator-driven

#### Phase 19: Local Serving Runtime and Lane Contracts

Phase 19 extends the shipped LLM workflow with a lane-aware serving seam rather
than a second generation engine:

- `openai_compat_v1` is the first local-serving adapter contract
- `mdisc llm-generate --model-lane ...` and `mdisc llm-launch` now resolve
  lanes through the same precedence contract
- run manifests, resolved launch artifacts, and replay bundles can carry richer
  `serving_identity` data including endpoint, checkpoint, revision, and local
  model-path hints

The Phase 19 boundary is intentionally narrow:

- the local server must already be running
- the CLI performs readiness checks and records serving identity
- the CLI does **not** start or supervise the inference process

Specialized lane scope is also explicit:

- a `specialized_materials` lane is first-class in the workflow contract
- off-the-shelf specialized materials models are **not** assumed to understand
  Zomic natively
- in `v1.2`, a specialized lane may prove useful through generation-adjacent
  reasoning or evaluation support instead of direct Zomic generation

#### Phase 20: Specialized Lane Integration and Workflow Compatibility

Phase 20 makes the first specialized lane operational without overstating what
off-the-shelf materials models can do:

- `Al-Cu-Fe` is the deeper proof that a `specialized_materials` lane can take
  a real workflow role through `llm-evaluate`
- `Sc-Zn` is the thinner compatibility proof that launch, replay, compare, and
  lineage still hold when that evaluation lane is present on a second system
- generation, launch, and replay remain compatible with the existing lane-aware
  runtime, but the specialist contribution is intentionally
  **evaluation-primary**
- compare and report now preserve distinct generation-lane and
  evaluation-lane lineage so operators can see which model family generated a
  candidate and which one assessed it

This milestone boundary matters:

- Phase 20 does **not** claim that off-the-shelf specialized materials models
  are already strong direct Zomic generators
- Phase 20 does **not** fork the pipeline into a special-purpose artifact tree
- Zomic-native local generation remains a later milestone once hosted, local,
  and specialized baselines can be compared honestly

#### Phase 21: Comparative Benchmarks and Operator Serving Workflow

Phase 21 turns the hosted/local/specialized lane contract into an operator
benchmark workflow:

- `mdisc llm-serving-benchmark --spec ... --smoke-only` runs explicit per-lane
  readiness checks and writes a typed smoke artifact before any benchmark work
  starts
- `mdisc llm-serving-benchmark --spec ...` reuses the shipped launch/evaluate
  flows and writes a benchmark summary under
  `data/benchmarks/llm_serving/{benchmark_id}/`
- benchmark comparisons are anchored to one shared acceptance-pack context so
  hosted, local, and specialized targets are judged against the same system and
  operator question

The specialized lane remains deliberately honest in this workflow:

- the committed specialist target is still **evaluation-primary**
- the benchmark summary keeps role-specific missing metrics explicit instead of
  pretending launch and evaluation lanes produce identical outputs
- Zomic-native specialized generation remains a later milestone after serving
  baselines and operator tradeoffs are understood

Phase 21 is also strict by design:

- smoke failure stops the benchmark unless fallback is explicitly allowed for
  that target
- no silent fallback is permitted during serving benchmarks
- operators should treat benchmark artifacts as auditable records of what lane
  really ran, not just what was requested

#### Phase 25: Checkpoint Artifact and Lineage Contracts

Phase 25 adds the first file-backed contract for a Zomic-adapted local
checkpoint:

- `mdisc llm-register-checkpoint --spec ...` writes a typed registration under
  `data/llm_checkpoints/{checkpoint_id}/registration.json`
- the registration pins base model, adaptation method, adaptation artifact,
  corpus manifest, eval-set manifest, optional acceptance pack, model revision,
  and local model path
- a lane can still carry `checkpoint_id` as lightweight metadata, but
  `require_checkpoint_registration: true` upgrades that lane into a strict
  adapted-checkpoint lane

This boundary is intentional:

- the milestone does not automate training
- the milestone does make adapted checkpoints auditable, replay-safe, and
  comparable inside the shipped workflow

#### Phase 26: Adapted Local Generation Integration

Phase 26 makes the first adapted checkpoint operational:

- `configs/systems/al_cu_fe_llm_adapted.yaml` proves one real adapted lane
  through the existing `llm-generate` and campaign surfaces
- serving identity now carries `checkpoint_lineage` so launch, replay, and
  benchmark artifacts can distinguish the adapted checkpoint from the baseline
  local model
- replay treats checkpoint identity and checkpoint fingerprint as hard drift,
  while endpoint and local-path differences remain transport drift when the
  same checkpoint still resolves cleanly

This is the first milestone that explicitly aims at Zomic-native local
generation rather than only hosted, local, or specialist serving transport.

#### Phase 27: Adapted Checkpoint Benchmarks and Operator Workflow

Phase 27 turns the adapted checkpoint into an operator-usable workflow:

- `configs/llm/al_cu_fe_adapted_serving_benchmark.yaml` compares the adapted
  checkpoint against the unadapted local baseline on one shared acceptance-pack
  context
- benchmark summaries now emit an explicit adapted-vs-baseline recommendation
  line when an adapted checkpoint improves parse, compile, or generation
  success
- the runbook documents checkpoint registration, smoke testing, rollback to the
  baseline local lane, and how to interpret an adapted benchmark result

The milestone remains deliberately narrow:

- one credible adapted checkpoint is enough
- large-scale checkpoint farming or automated promotion is still a later
  milestone
- the workflow stays CLI-first, file-backed, and operator-governed

#### Phase 28: Checkpoint Lifecycle and Promotion Contract

Phase 28 adds the first multi-checkpoint lifecycle layer without yet changing
runtime default resolution:

- immutable checkpoint registration still lives at
  `data/llm_checkpoints/{checkpoint_id}/registration.json`
- mutable family lifecycle state now lives at
  `data/llm_checkpoints/families/{checkpoint_family}/lifecycle.json`
- promotion and retirement actions are written as revision-stamped artifacts
  under `data/llm_checkpoints/families/{checkpoint_family}/actions/`

The operator surface is intentionally small and explicit:

- `mdisc llm-list-checkpoints --checkpoint-family ...`
- `mdisc llm-promote-checkpoint --spec ...`
- `mdisc llm-retire-checkpoint --spec ...`

Those commands make lifecycle state auditable without weakening replay:

- `checkpoint_family` selects the family registry
- `checkpoint_id` can still act as an explicit member pin inside that family
- retired checkpoints are no longer implicitly selectable, but replay still
  resolves by immutable registration plus checkpoint fingerprint identity
- demotion happens by promoting a different checkpoint; there is no separate
  demote command in Phase 28

The committed example action specs under `configs/llm/` use illustrative
repo-relative placeholder evidence paths. They are structural examples and CLI
fixtures, not claimed benchmark results.

The Phase 28 boundary is deliberate:

- promoted-default execution through `llm-generate`, `llm-launch`, and
  `llm-replay` is deferred to Phase 29
- workflow pin resolution from family state is also deferred to Phase 29
- RUNBOOK-level promotion/demotion workflow guidance stays deferred until that
  execution integration exists

This keeps Phase 28 honest: lifecycle state is now real, file-backed, and
operator-usable, but it is not yet a silent runtime default-selection system.

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
            (general-purpose or   |
             specialized lane     |
             assessment)          |
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
- [x] Implement `mdisc llm-evaluate` CLI command
- [x] Design synthesizability prompt (inspired by CSLLM)
- [x] Design anomaly detection prompt
- [x] Integrate LLM assessment into report stage

### Phase 4 — Active Learning Loop
- [x] Implement `mdisc llm-suggest` dry-run CLI command
- [x] Implement `mdisc llm-approve` approval/spec governance command
- [x] Implement `mdisc llm-launch` as the approved-spec execution bridge
- [x] Add strict `mdisc llm-replay` and `mdisc llm-compare` workflow commands
- [x] Connect campaign launches to a fuller closed-loop exploration workflow
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
