# Domain Pitfalls

**Domain:** `v1.6` Translator-Backed External Materials-LLM Benchmark MVP  
**Researched:** 2026-04-07  
**Confidence:** HIGH for repo-specific architecture risks, MEDIUM for external-model runtime behavior

## Milestone Phase Assumptions

To keep the warnings actionable, this file assumes `v1.6` is split into three
phases:

| Proposed Phase | Purpose |
|---|---|
| Phase 34: Benchmark Pack Contract and Controls | Freeze the benchmark set, inclusion rules, control arm, and fidelity-aware scoring slices. |
| Phase 35: External Model Execution Lanes | Add downloaded-model execution with reproducible environment capture and operator-safe invocation. |
| Phase 36: Comparative Workflow and Scorecards | Run the shared benchmark, compare against promoted/pinned internal controls, and publish operator decision guidance. |

## Critical Pitfalls

### Pitfall 1: Misleading benchmark packs

**What goes wrong:**  
The benchmark set is curated from whatever exported cleanly, whatever fits one
model's tokenizer, or whatever looks good in early smoke runs. Exact periodic
exports, approximate proxies, and explicitly lossy QC-to-periodic translations
get mixed into one headline number. Dev fixtures or exporter goldens quietly
become part of the "real" benchmark because they are convenient and already
checked in.

**Why it happens here:**  
`v1.5` intentionally made CIF and material-string outputs additive interop
artifacts, not replacements for Zomic. That means the translated surface is
already heterogeneous by design. `v1.6` also wants a small curated set, which
raises the risk that convenience and coverage get confused.

**Consequences:**  
The benchmark measures curation choices more than model capability. A model can
look strong because it only saw easy periodic-safe slices, or weak because it
was judged on lossy periodic proxies that were never QC-faithful to begin with.
Roadmap decisions then rest on noise.

**Prevention:**  
- Freeze a typed benchmark-pack manifest that references translation bundle
  manifests and explicit inventory rows, not ad hoc file globs.
- Require inclusion and exclusion rules by `target_family`, `fidelity_tier`,
  system, and intended task.
- Keep `exact`/`anchored` slices separate from `approximate`/`lossy` slices in
  both execution and reporting.
- Record excluded candidates and the reason they were excluded.
- Do not use repo regression fixtures or golden exporter payloads as headline
  benchmark items.

**Address in milestone:**  
Phase 34 first. Phase 36 should refuse to collapse mixed-fidelity packs into
one headline score.

### Pitfall 2: Apples-to-oranges comparisons against internal controls

**What goes wrong:**  
External models get benchmarked on translated CIF or material-string payloads,
while internal controls are judged on native Zomic generation, different input
subsets, different prompt wrappers, or different evaluation metrics. The final
summary still names a "winner."

**Why it happens here:**  
The shipped internal controls are promoted or pinned Zomic-first lanes. The new
external lanes will consume periodic/material-string views of the same
candidates. Those are related surfaces, but they are not automatically the same
task. The risk gets worse if the external shortlist mixes generators,
evaluators, and task-specific materials models under the same benchmark label.

**Consequences:**  
The comparison stops being scientifically meaningful. A score difference may
reflect representation choice, prompt scaffolding, or task mismatch rather than
actual model quality. The product team can incorrectly conclude that external
models are better, worse, or "ready for automation."

**Prevention:**  
- Define benchmark families by task type before choosing models:
  generation, evaluation, ranking, or question-answering.
- Compare external models and internal controls only on a shared input surface
  with a shared slice definition.
- Pin the exact promoted or explicit-pinned internal control IDs in the
  benchmark spec.
- If an internal control remains Zomic-native while the external model consumes
  translated text, report that as a control-purpose distinction, not as a
  direct like-for-like ranking.
- Ban one overall "best model" score across different task families.

**Address in milestone:**  
Phase 34 defines the comparison contract. Phase 36 enforces it in the scorecard
and CLI summaries.

### Pitfall 3: Environment drift disguised as model improvement

**What goes wrong:**  
Benchmark reruns change because the downloaded model revision moved, a new
tokenizer was pulled, quantization settings changed, the runtime package set
shifted, or GPU/platform differences altered generation behavior. The team then
attributes the change to the model or the translation pack.

**Why it happens here:**  
Downloaded external models sit outside the repo's existing controlled serving
ladder. Hugging Face downloads are revision-aware and cache-aware, but floating
branches/tags remain easy to use accidentally. PyTorch explicitly warns that
fully reproducible results are not guaranteed across releases, commits, or
platforms, and not necessarily between CPU and GPU even with the same seeds.

**Consequences:**  
The benchmark is not replayable. Two operators can "run the same benchmark" and
produce materially different outputs. That makes later training, source-QA, or
runtime investment decisions hard to trust.

**Prevention:**  
- Require every external run manifest to capture model repo ID, explicit
  revision or commit hash, weight file hashes, tokenizer revision, runtime
  package versions, hardware info, dtype, quantization choice, seeds, and
  prompt-template revision.
- Prefer local snapshots pinned to explicit revisions over floating `main` or
  latest tags.
- Separate smoke runs from decision-grade runs.
- For stochastic models, run multiple trials or explicitly mark the benchmark as
  non-deterministic rather than pretending one pass is definitive.
- Fail closed when environment capture is incomplete.

**Address in milestone:**  
Phase 35 is where this has to be solved. Phase 36 should only consume runs that
meet the Phase 35 reproducibility contract.

### Pitfall 4: Silent fidelity misuse

**What goes wrong:**  
Lossy periodic proxies are sent into external materials LLMs and the resulting
scores get interpreted as if the models were operating on QC-faithful
structure truth. Because raw material strings intentionally stay parser-ready
and bare, operators may inspect only payload text and miss the sidecar fidelity
warnings.

**Why it happens here:**  
`v1.5` made the source-of-truth boundary explicit: compiled Zomic candidates
remain authoritative, while CIF and material-string payloads are additive
views. `v1.6` sits directly on top of that seam, so any reporting shortcut can
turn a known fidelity boundary into a silent misuse boundary.

**Consequences:**  
The team may conclude that an external model is bad at materials reasoning when
it is actually reacting to a lossy proxy, or conclude that the translation
bridge is "good enough" because a model happened to perform well on a degraded
slice. Both are false confidence.

**Prevention:**  
- Carry `fidelity_tier`, `loss_reasons`, `diagnostic_codes`, and
  `target_family` into every benchmark request row, result row, and scorecard.
- Keep periodic-safe (`exact`, `anchored`) and proxy (`approximate`, `lossy`)
  slices separate in reporting.
- Refuse to emit a single overall score if proxy slices are mixed into the same
  headline metric without stratification.
- Keep operator docs blunt: if QC-native fidelity matters, stop at the
  candidate JSONL/Zomic boundary.

**Address in milestone:**  
Phase 34 defines the slice rules. Phase 36 enforces them in reporting and
operator guidance.

### Pitfall 5: Uncontrolled model scope

**What goes wrong:**  
The milestone quietly expands from "benchmark a few downloaded external
materials LLMs" into "build a reusable external serving platform" with generic
model registries, hot-swappable runtimes, background daemons, autopull/update
logic, or broad provider abstractions.

**Why it happens here:**  
Once local execution for external models exists, infrastructure gravity pushes
toward generalization. The repo already has rich internal serving and lifecycle
machinery, so it is easy to over-apply that instinct to a milestone whose real
question is still "which external models are worth deeper investment?"

**Consequences:**  
`v1.6` slips, complexity rises, and the architecture drifts away from the
benchmark-first goal. The program absorbs operational cost before it has
evidence that any external lane deserves to persist.

**Prevention:**  
- Use a hard allowlist of a few explicitly named benchmark targets with declared
  task type, license posture, hardware envelope, and accepted input family.
- Keep model registration benchmark-specific, not global and open-ended.
- Do not add autonomous downloading, scheduling, or generic long-running
  serving in this milestone.
- Treat any reusable runtime abstraction as suspect unless two or more approved
  benchmark lanes genuinely need it.

**Address in milestone:**  
Phase 35, with the boundary called out in the roadmap and operator docs from
day one.

### Pitfall 6: Parallel architecture drift

**What goes wrong:**  
External benchmarking gets implemented as side scripts or notebooks that write
their own JSON, CSV, and prompt logs under a new directory tree. The workflow
bypasses translation bundles, stage manifests, benchmark context, promoted/pin
selection, and compare-style summaries because that feels faster.

**Why it happens here:**  
The repo already has an operator-governed, file-backed workflow. That is a
strength, but it also means an impatient benchmark prototype can accidentally
fork the architecture instead of extending it.

**Consequences:**  
Lineage becomes incomplete, replay becomes manual, and later phases have to
retrofit provenance onto a pile of experiment files. The benchmark then proves
less than the repo standard already expects.

**Prevention:**  
- Make external benchmark specs point to translation bundle manifests and
  inventory rows, not raw payload directories.
- Reuse the existing stage-manifest, source-lineage, and benchmark-context
  patterns.
- Put external run outputs under one dedicated artifact family, but keep the
  schema style aligned with the existing `llm` storage/manifests.
- Extend the shipped CLI instead of normalizing a notebook-first workflow.

**Address in milestone:**  
Phase 35 for artifact shape, Phase 36 for compare/scorecard integration.

## Moderate Pitfalls

### Pitfall 7: Prompt-wrapper instability

**What goes wrong:**  
The prompt template, system instruction, stop-token handling, or unit rendering
changes between runs, and the observed difference gets reported as a model
difference.

**Why it happens here:**  
`v1.6` is benchmarking text-facing models on translated artifacts. Materials
LLMs are sensitive to prompt phrasing and input perturbations; recent materials
LLM robustness work reports degradation under unit mixing, sentence reordering,
and other text changes.

**Prevention:**  
- Version the request template as a first-class artifact.
- Capture the template hash in the run manifest.
- If a model needs a model-specific wrapper, treat that as a separate benchmark
  lane, not the same lane with a hidden tweak.
- Add a small prompt-perturbation check before trusting a result as
  decision-grade.

**Address in milestone:**  
Phase 35 defines the request renderer. Phase 36 decides whether perturbation
checks are required for final scorecards.

### Pitfall 8: Overclaiming from a tiny curated benchmark

**What goes wrong:**  
One external model performs well on a small curated pack and the team treats
that as proof that training automation, broad external runtime work, or new
source-QA investments should be the next milestone.

**Why it happens here:**  
The milestone goal explicitly asks what should come next. That makes narrative
overreach likely unless the benchmark outputs are constrained to the decisions
they can actually support.

**Prevention:**  
- Predefine allowed outcome classes in the scorecard:
  not competitive, competitive only on periodic-safe slices, worthy of deeper
  runtime investment, or blocked by translation/source quality rather than
  model quality.
- Keep evidence references file-backed and explicit.
- Treat the benchmark as a gating experiment, not as proof that the whole
  external-model product direction is validated.

**Address in milestone:**  
Phase 36.

## Minor Pitfalls

### Pitfall 9: Benchmark-set reuse from convenience artifacts

**What goes wrong:**  
The milestone reuses Phase 31/32 exporter fixtures, goldens, or smoke configs
as decision-grade benchmark content because they are already deterministic and
easy to inspect.

**Why it happens here:**  
Those artifacts are excellent regression anchors, but they are intentionally
small and boundary-focused. They are not a representative benchmark pack.

**Prevention:**  
- Keep regression fixtures for tests only.
- Build the benchmark pack from real translated candidate artifacts with their
  own manifest and selection rationale.

**Address in milestone:**  
Phase 34.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|---|---|---|
| Phase 34: Benchmark pack contract | Mixed fidelity, convenience curation, and task-family confusion | Freeze benchmark-pack schema, slice rules, control IDs, and exclusion reasons before running any external model. |
| Phase 34: Internal controls | Using whichever internal lane is easiest to call instead of the promoted/pinned control arm | Require control selection to be explicit and file-backed in the benchmark spec. |
| Phase 35: Downloaded model execution | Floating model revisions, hidden tokenizer/runtime drift, and broad serving abstractions | Pin revisions, snapshot environments, capture runtime metadata, and keep the model list intentionally small. |
| Phase 35: Request rendering | Prompt-wrapper churn changes results | Version prompt templates and treat model-specific wrappers as distinct lanes. |
| Phase 36: Comparative reporting | Collapsing unlike slices into one score | Report by task family and fidelity slice first; refuse a headline aggregate when the comparison contract is violated. |
| Phase 36: Product conclusion | Treating one benchmark win as proof of strategic readiness | Limit outputs to explicit next-step recommendations grounded in evidence paths. |

## Sources

**Repo sources**
- `.planning/PROJECT.md`
- `.planning/milestones/v1.5-ROADMAP.md`
- `.planning/milestones/v1.5-phases/33-cli-benchmark-hooks-and-operator-docs/33-RESEARCH.md`
- `materials-discovery/developers-docs/llm-translation-contract.md`
- `materials-discovery/developers-docs/llm-translation-runbook.md`
- `materials-discovery/src/materials_discovery/llm/translation_bundle.py`
- `materials-discovery/src/materials_discovery/llm/schema.py`

**External sources**
- PyTorch reproducibility note: https://docs.pytorch.org/docs/stable/notes/randomness.html
- Hugging Face Hub file download and revision docs: https://huggingface.co/docs/huggingface_hub/package_reference/file_download
- Wang et al., "Evaluating the performance and robustness of LLMs in materials science Q&A and property predictions" (Digital Discovery, 2025): https://pubs.rsc.org/en/content/articlehtml/2025/dd/d5dd00090d

## Critical Warnings Summary

- Do not let `lossy` translated payloads drive the headline story for `v1.6`.
- Do not compare external models and internal controls on different task
  surfaces and still call it one benchmark.
- Do not trust reruns unless model revision, runtime, hardware, prompt, and
  sampling state are all captured.
- Do not let this milestone turn into a general external serving stack before
  the benchmark proves any external lane is worth that cost.

## File Changed

- `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/PITFALLS.md`
