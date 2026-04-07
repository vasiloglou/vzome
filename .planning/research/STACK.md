# Technology Stack: v1.6 Translator-Backed External Materials-LLM Benchmark MVP

**Project:** Materials Design Program
**Milestone:** v1.6
**Researched:** 2026-04-07
**Scope:** Only stack additions or changes needed for external downloaded-model benchmarking. Existing internal pipeline, campaign flow, checkpoint lifecycle, serving lanes, and v1.5 translation/export surfaces stay in place.
**Overall confidence:** HIGH for the runtime/reproducibility stack, MEDIUM for the exact first external model shortlist because upstream packaging quality varies.

## Recommended Stack

### Core Runtime

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.11 | Keep one repo-wide runtime baseline | Already matches `materials-discovery`; do not split the milestone across Conda-only side environments. |
| `uv` + `uv.lock` | repo current | Install, lock, and reproduce benchmark environments | The repo is already `uv`-first; v1.6 should add one optional extra instead of a parallel package manager story. |
| `torch` | exact pinned build per benchmark environment | Local inference backend for downloaded models | External materials LLMs are PyTorch-first; pin exact wheel/build in the environment manifest instead of using loose semver. |
| `transformers` | `>=4.57,<5` | Canonical model/tokenizer loading and generation | Best fit for HF-style downloadable checkpoints, local path loading, revision pinning, `use_safetensors`, and generation config control. |
| `huggingface_hub` | `>=1.0,<2` | Snapshot download, cache control, and offline execution | Needed to prefetch exact model revisions, stage them locally, then run benchmarks with network access disabled. |
| `safetensors` | `>=0.5,<1` | Safe model weight loading | Prefer `safetensors`-backed checkpoints over pickle-heavy or project-specific weight formats. |
| `accelerate` | `>=1.4,<2` | Device mapping and CPU/disk offload for larger local models | Lets one runner handle both modest models and larger checkpoints without introducing a distributed serving stack. |
| `peft` | `>=0.18,<1` optional | Adapter-backed inference only when a curated target requires it | CrystalTextLLM-style models may arrive as PEFT adapters; support this as an explicit runner type, not the default path. |

### Reuse Instead of Replacing

| Existing Stack | v1.6 Change | Why |
|----------------|-------------|-----|
| `typer` CLI + existing `mdisc` command style | Add one external benchmark command family under the existing CLI | Keeps the workflow operator-governed and consistent with shipped benchmark/translation commands. |
| `pydantic` schemas | Add typed external-model manifest, benchmark-pack manifest, and environment manifest | The repo already depends on typed file-backed contracts; v1.6 should extend that pattern, not bypass it. |
| Translation bundle artifacts from v1.5 | Use them as benchmark dataset sources | This is the whole point of the milestone: benchmark external models against the shipped translation artifacts, not ad hoc notebooks. |
| Existing `pymatgen` / `ase` optional stack | Reuse for CIF parsing and normalization checks | Do not add a second crystal-structure validation stack for CIF scoring. |

## Required Additions

### 1. Downloaded Model Packaging Layer

Add a file-backed external model registration contract. Each curated external target should resolve into one normalized local snapshot before benchmarking starts.

Required manifest fields:

| Field | Required | Notes |
|-------|----------|-------|
| `model_id` | Yes | Stable repo-local identifier, not just the upstream repo name. |
| `source_kind` | Yes | Start with `huggingface_model` and `local_snapshot`; defer arbitrary repo runners. |
| `repo_id` / `local_path` | Yes | One authoritative download source. |
| `revision` | Yes | Full upstream commit or immutable revision, never "main" or floating tags. |
| `snapshot_path` | Yes | Local resolved directory used at benchmark time. |
| `license` | Yes | Needed because upstream licenses differ materially across projects. |
| `task_family` | Yes | Start with `cif_generation` and `material_string_generation`; do not overload one prompt contract across both. |
| `runner_kind` | Yes | Restrict to `transformers_causal_lm` and `peft_causal_lm` in v1.6. |
| `base_model` | Optional, typed | Required when `runner_kind=peft_causal_lm`. |
| `tokenizer_source` | Yes | Explicit tokenizer path/revision so tokenization drift is visible. |
| `dtype` / `device_map` / `offload_policy` | Yes | Must be part of the reproducible execution contract, not hidden in operator memory. |
| `quantization` | Optional, typed | Allowed only when explicitly pinned and benchmarked as a separate lane. |
| `prompt_template_id` | Yes | Different external models will not share the same prompt framing. |
| `generation_defaults` | Yes | Temperature, top-p, max tokens, stop tokens, repetition penalties, etc. |

Recommended packaging rule:

- Download with `huggingface_hub.snapshot_download(...)` into a controlled cache root.
- Benchmark only from the resolved local snapshot path.
- During execution, force offline mode and local-file loading.

This should be a two-step workflow:

1. `download/resolve` step: fetch, fingerprint, and register the model snapshot.
2. `benchmark` step: run only against already-resolved local artifacts.

That split is important. It prevents "the benchmark also changed the model" drift.

### 2. External Runner Surface

Use one canonical in-process runner built on `transformers` + `torch`, not a mix of project-specific launch scripts.

Recommended runner types:

| Runner | Use | Why |
|--------|-----|-----|
| `transformers_causal_lm` | Default for HF-native checkpoints | Lowest-friction, most reproducible path for a small curated benchmark set. |
| `peft_causal_lm` | Only when a chosen model is adapter-backed | Covers CrystalTextLLM-style artifacts without forcing PEFT complexity onto every target. |

Do not make these v1.6 requirements:

| Avoid | Why |
|-------|-----|
| `vllm` as the required benchmark runtime | Useful later for throughput lanes, but its online serving path is not the right canonical reproducibility surface. |
| Project-specific repo runners (`source install.sh`, custom Conda envs, bespoke scripts) | CrystaLLM and CrystalTextLLM both ship their own repo workflows; vendoring those directly would make the benchmark harder to reproduce and compare honestly. |
| DeepSpeed / LMFlow / distributed inference | Too heavy for a curated MVP and more aligned with training or large-scale fine-tuning than benchmark execution. |

### 3. Fidelity-Aware Benchmark Dataset Pack

Do not add `datasets` or a separate benchmark DB. Build a typed benchmark pack on top of the existing translation bundle manifests and inventories.

Recommended dataset artifact family:

| Artifact | Format | Purpose |
|---------|--------|---------|
| `benchmark_pack.json` | JSON | Bundle-level spec: benchmark id, source translation bundles, control configs, prompt templates, scoring rules, and sample roster. |
| `samples.jsonl` | JSONL | One row per benchmark sample, referencing the translation payload and its fidelity metadata. |
| `prompt_templates/` | text or Jinja-like templates | Family-specific prompts for CIF vs material-string models. |
| `results/` | JSON per target + summary JSON | Reproducible per-target outputs and aggregate scores. |

Each sample row should carry:

- `sample_id`
- `system`
- `candidate_id`
- `target_family`
- `payload_path`
- `payload_hash`
- `translation_manifest_path`
- `fidelity_tier`
- `loss_reasons`
- `diagnostic_codes`
- `control_arm` flag or grouping
- `prompt_template_id`
- `expected_validator`

Recommended scoring split:

| Area | Stack | Notes |
|------|-------|-------|
| Format validity | existing translation/export validators + `pymatgen` for CIF | Make parser success a first-class metric. |
| Fidelity posture | translation bundle metadata | Do not pretend a lossy periodic proxy is equivalent to an exact export. |
| Reproducible prompting | typed template ids + stored rendered prompt text | Keep prompt drift visible in artifacts. |
| Internal control comparison | existing promoted/pinned Zomic checkpoint configs | The control arm is already shipped; v1.6 should reuse it, not redefine it. |

Dataset scope guidance for the MVP:

- Keep the benchmark set small and explicit.
- Include both `cif` and `material_string` families.
- Include an intentional mix of `exact`, `anchored`, `approximate`, and `lossy` cases so fidelity-aware scoring is real, not decorative.
- Prefer 2 systems x 2 target families x a handful of curated samples over a broad leaderboard.

### 4. Benchmark Orchestration

Reuse the existing benchmark philosophy: typed specs, smoke-first checks, explicit artifacts, no silent fallback.

Recommended additions:

| Component | Stack | Why |
|-----------|-------|-----|
| External benchmark spec | `pydantic` + YAML/JSON | Same contract style as serving benchmarks and checkpoint lifecycle specs. |
| Benchmark CLI | `typer` | Keeps the workflow CLI-first and scriptable. |
| Worker isolation | `subprocess` + per-target temp/run dirs | Frees model memory cleanly and prevents one model’s runtime state from contaminating the next. |
| Timing | `time.perf_counter()` | Enough for wall-clock latency in a local MVP. |
| Result summaries | JSON first, optional tabular export later | Avoid premature dashboard/reporting stack growth. |

Suggested command split:

```bash
uv run mdisc llm-register-external-model --spec configs/llm_external/<model>.yaml
uv run mdisc llm-benchmark-external --spec configs/llm_external/<benchmark>.yaml
uv run mdisc llm-benchmark-external-inspect --summary data/benchmarks/llm_external/<benchmark_id>/summary.json
```

### 5. Environment Capture

Environment capture is a schema requirement more than a dependency requirement. Keep it file-backed.

Every benchmark run should write an environment manifest with:

- Python version
- `uv.lock` hash or lock snapshot reference
- `torch`, `transformers`, `huggingface_hub`, `accelerate`, `peft`, `safetensors` versions
- OS and kernel
- CUDA/ROCm availability
- GPU model, count, driver version, and visible devices
- exact external model snapshot path and hash
- tokenizer source and hash
- runner kind, dtype, device map, offload config, quantization config
- benchmark spec hash
- rendered prompt template hash
- random seed
- control checkpoint ids / lifecycle revisions used for the internal arm

Recommended controls:

| Control | Recommendation | Why |
|---------|----------------|-----|
| HF cache path | Set `HF_HOME` and `HF_HUB_CACHE` explicitly | Keeps downloads and cache reuse deterministic. |
| Offline execution | Set `HF_HUB_OFFLINE=1` during benchmark runs | Prevents mid-run network drift. |
| Local loading | Use `local_files_only=True` once the snapshot is resolved | Ensures execution uses the staged artifact, not a fresh remote lookup. |
| Safe weights | Use `use_safetensors=True` where available | Prefer safer, more portable weight loading. |
| PyTorch determinism | Enable deterministic algorithms where supported | Makes failures and drift more visible on the same hardware/software stack. |

## Explicit Non-Goals For v1.6

| Do Not Add | Why Not |
|------------|---------|
| Full CSLLM training/inference stack | CSLLM is a broader synthesis workflow family, not the smallest practical translator-backed benchmark target. |
| DeepSpeed, LMFlow, or distributed finetuning infra | Too heavy for a reproducible benchmark MVP. |
| `datasets`, MLflow, W&B, Ray, Airflow, or a benchmark service | The milestone should stay file-backed, CLI-first, and operator-governed. |
| A web UI or dashboard | The current repo conventions are CLI and artifacts first. |
| Automatic model discovery or mass benchmark sweeps | Initial scope should stay curated and explicit. |
| Arbitrary remote-code model execution | Restrict the MVP to HF/Transformers-compatible checkpoints and explicit adapter cases. |
| Quantized variants as the default | Quantization changes fidelity and runtime behavior; treat it as an explicit alternate lane only if needed later. |
| `vllm` as the benchmark source of truth | Keep canonical scoring on the simpler deterministic runner; add throughput-focused vLLM lanes only later if the benchmark surface proves useful. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Model loading | `transformers` local runner | Reusing each upstream repo’s scripts | Too much environment drift and too many hidden assumptions. |
| Download flow | `huggingface_hub` snapshot registration | `git clone` + ad hoc LFS handling | Weaker revision pinning and worse cache/offline ergonomics. |
| Large-model support | `accelerate` offload/device maps | `vllm` or distributed serving as the default | More moving parts than the MVP needs. |
| Dataset representation | repo-local JSON/JSONL benchmark pack | HF `datasets` dataset build | Adds packaging complexity without helping the file-backed workflow. |
| Control arm | existing promoted/pinned internal checkpoints | new external-only baseline | Misses the milestone’s core comparison question. |

## Installation Direction

Add a new optional extra, not a second environment manager:

```bash
# existing repo baseline
cd materials-discovery
uv sync --extra dev

# new v1.6 benchmark runtime
uv sync --extra external-benchmark
```

Likely `external-benchmark` dependency group:

```toml
external-benchmark = [
  "torch==<exact tested build>",
  "transformers>=4.57,<5",
  "huggingface_hub>=1.0,<2",
  "safetensors>=0.5,<1",
  "accelerate>=1.4,<2",
  "peft>=0.18,<1",
]
```

If CIF validation is not already available in the chosen environment, reuse the repo's existing `pymatgen` support rather than adding a different crystal parser.

## Sources

- HIGH: Hugging Face Hub download guide and environment variables
  - https://huggingface.co/docs/huggingface_hub/v1.0.0.rc7/guides/download
  - https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables
- HIGH: Transformers model loading docs
  - https://huggingface.co/docs/transformers/v4.57.1/main_classes/model
- HIGH: PEFT model loading docs
  - https://huggingface.co/docs/peft/v0.6.2/package_reference/peft_model
- HIGH: Accelerate big-model/offload docs
  - https://huggingface.co/docs/accelerate/v1.4.0/en/package_reference/big_modeling
- HIGH: PyTorch deterministic algorithms docs
  - https://docs.pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html
- MEDIUM: vLLM serving and reproducibility docs
  - https://docs.vllm.ai/en/stable/serving/openai_compatible_server/
  - https://docs.vllm.ai/en/stable/usage/reproducibility/
- MEDIUM: CrystaLLM upstream repo
  - https://github.com/lantunes/CrystaLLM
- MEDIUM: CrystalTextLLM upstream repo
  - https://github.com/facebookresearch/crystal-text-llm
- MEDIUM: CSLLM paper
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC12264133/

## Recommended Stack Direction For v1.6

Use one new `external-benchmark` runtime built around exact-pinned `torch` plus `transformers`, `huggingface_hub`, `safetensors`, and `accelerate`, with `peft` only for explicitly curated adapter-backed targets. Register external models as file-backed local snapshots pinned to immutable revisions, benchmark them from small translation-bundle-derived JSON/JSONL packs, and capture every run with an offline cache policy plus a typed environment manifest. Do not add CSLLM-scale training infrastructure, dashboards, or vLLM-as-default execution in this milestone.

**File changed:** `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/STACK.md`
