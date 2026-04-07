# Project Research Summary

**Project:** Materials Design Program
**Domain:** Translator-backed external materials-LLM benchmark MVP
**Milestone:** `v1.6`
**Researched:** 2026-04-07
**Confidence:** MEDIUM

## Executive Summary

`v1.6` should be a narrow, benchmark-first extension of the existing
`materials-discovery` workflow, not a generic external-model platform. The
research converges on one practical shape: freeze a small benchmark pack from
shipped translation artifacts, register a curated handful of downloaded
external materials LLMs as immutable local artifacts, and compare them against
the current promoted or explicitly pinned internal controls in one typed,
CLI-first workflow.

The recommended build is additive to the repo's current architecture. Reuse the
existing schema, manifest, storage, CLI, translation-bundle, and benchmark
patterns; add a small `external-benchmark` runtime extra; benchmark only from
resolved local snapshots pinned to exact revisions; and write fidelity-aware
scorecards that stay explicit about target family, eligible slice, exclusions,
and control deltas. The MVP succeeds if it can answer a simple roadmap
question: which external models are worth deeper investment, and under what
representation and fidelity constraints?

The main risks are all credibility risks, not feature-volume risks. Mixed
fidelity packs, apples-to-oranges comparisons against internal controls, and
runtime or prompt drift would make the benchmark untrustworthy. Prevent that by
freezing benchmark cases before execution, stratifying results by
`target_family` and `fidelity_tier`, pinning internal control IDs and external
model revisions, capturing prompt and environment hashes, and refusing blended
headline scores when the comparison contract is violated.

## Key Findings

### Recommended Stack

The stack addition is intentionally small. Stay on Python 3.11 and the repo's
`uv`-first workflow, then add one optional `external-benchmark` dependency
group for local external-model execution. Use one repo-owned benchmark runtime
based on exact-pinned `torch` plus `transformers`, `huggingface_hub`,
`safetensors`, and `accelerate`, with `peft` only for explicitly curated
adapter-backed targets. Benchmark from local resolved snapshots with offline
loading enabled and capture environment metadata as a first-class run artifact.

**Core technologies:**
- `Python 3.11` + `uv`/`uv.lock`: keep one runtime baseline and one lock story.
- `torch` with exact pinned build: reproducible local inference backend.
- `transformers`: canonical model/tokenizer loading and generation control.
- `huggingface_hub`: snapshot download, revision pinning, cache control, and offline execution.
- `safetensors`: safe checkpoint loading where supported.
- `accelerate`: device maps and offload for larger local checkpoints without adding serving infrastructure.
- `peft` optional: explicit support for curated adapter-backed models only.
- Existing `typer`, `pydantic`, manifests, translation bundles, and `pymatgen`: extend current repo patterns instead of introducing a parallel platform.

### Expected Features

The minimum credible feature set is a small, honest benchmark that can produce
decision-grade output. That means the workflow must freeze a fidelity-aware
translated benchmark set, run a curated set of external models reproducibly,
compare them against the internal control arm on the same translated slices,
and emit scorecards that say whether a model is competitive enough to justify
deeper follow-on work.

**Must have (table stakes):**
- Freeze one small translated benchmark set with explicit inclusion, exclusion, `target_family`, and `fidelity_tier` rules.
- Register each external model with immutable identity, local snapshot lineage, compatible input families, smoke checks, and environment capture.
- Run a shared benchmark spec that includes curated external targets and the current promoted or explicitly pinned internal controls.
- Score by representation family and fidelity slice, with eligible and excluded counts made explicit.
- Emit typed summaries and CLI scorecards that produce a clear continue, explore, or stop recommendation per external target.

**Should have (competitive):**
- Support both promoted-default and explicit pinned internal controls in the same benchmark when useful.
- Show representation-sensitivity slices for models that can consume both CIF and material-string inputs.
- Add simple rule-based milestone routing in the summary output for next-step decisions.

**Defer (v2+):**
- Broad model-zoo support, auto-discovery, or autonomous downloading.
- Training or fine-tuning automation for external models.
- Autonomous campaign execution based on benchmark winners.
- UI dashboards, benchmark services, or broader workflow orchestration.
- Large benchmark-pack expansion or one blended cross-family leaderboard.

### Architecture Approach

The architecture should be a dedicated sibling workflow, best thought of as
`llm_external_benchmark`, layered on top of the shipped translation bundle
surface. Translation bundles remain the reusable upstream export layer; a new
frozen benchmark-set artifact captures the curated case slice; external models
gain immutable registrations and benchmark-only execution; internal controls
stay on existing promoted or pinned checkpoint lineage; and one scorecard layer
normalizes all targets into per-case results and fidelity-aware summaries.

**Major components:**
1. `TranslatedBenchmarkSet` artifact under `data/benchmarks/llm_external_sets/` — freezes benchmark cases, inclusion rules, and fidelity boundaries.
2. `ExternalModelRegistration` under `data/llm_external_models/` — records immutable external model identity, revision, snapshot path, compatibility, and prompt/runtime contract.
3. Benchmark-only runtime seam — runs curated local external models with smoke checks, prompt rendering, and environment capture without turning into a general serving platform.
4. Shared `ExternalBenchmark` orchestrator under `data/benchmarks/llm_external/` — executes targets, writes run manifests and case results, and references internal controls.
5. `ExternalBenchmarkScorecard` summary — aggregates by `target_family`, `fidelity_tier`, and control delta, then emits roadmap-facing recommendation lines.

### Critical Pitfalls

1. **Misleading benchmark packs** — freeze a typed benchmark pack from translation inventories, stratify exact or anchored versus approximate or lossy slices, and record exclusions explicitly.
2. **Apples-to-oranges internal comparisons** — compare only on shared task families and shared translated slices, pin the internal control IDs in the benchmark spec, and do not emit one overall "best model" score across unlike tasks.
3. **Environment and prompt drift** — pin model and tokenizer revisions, snapshot local artifacts, capture runtime and hardware metadata, version prompt templates, and fail closed when environment capture is incomplete.
4. **Silent fidelity misuse** — carry `fidelity_tier`, `loss_reasons`, and `diagnostic_codes` through requests, results, and summaries so proxy slices cannot masquerade as QC-faithful evidence.
5. **Scope creep into an external serving platform** — keep a hard allowlist of a few curated models, avoid generic provider abstractions, and do not add autonomous serving, scheduling, or training workflows in `v1.6`.

## Implications for Roadmap

Based on the combined research, the milestone should be planned as three
phases. That order matches the actual dependency chain: input credibility
first, reproducible execution second, comparative judgment last.

### Phase 34: Benchmark Pack Contract and Controls
**Rationale:** Freeze the benchmark input and comparison contract before runtime work introduces variability.
**Delivers:** Translated benchmark-set schema, storage helpers, freeze command, explicit inclusion and exclusion rules, fidelity slices, and explicit promoted or pinned internal control selection.
**Addresses:** `LLM-31` and the comparison contract portion of `LLM-32`.
**Avoids:** Misleading benchmark packs, apples-to-oranges comparisons, and silent fidelity misuse.

### Phase 35: External Model Registration and Reproducible Execution
**Rationale:** Prove each curated external target can be resolved, smoke-tested, and run reproducibly before attempting a milestone-grade comparison.
**Delivers:** External model registration schema, local snapshot registration, benchmark runtime extra, smoke checks, environment manifests, prompt-template versioning, and a narrow benchmark-only execution seam.
**Uses:** `torch`, `transformers`, `huggingface_hub`, `safetensors`, `accelerate`, and optional `peft`.
**Implements:** External registration and runtime architecture without polluting `SystemConfig` or the normal `llm-generate` path.
**Avoids:** Environment drift, prompt-wrapper instability, uncontrolled model scope, and side-script architecture drift.

### Phase 36: Comparative Workflow and Fidelity-Aware Scorecards
**Rationale:** Only after the benchmark cases and execution surfaces are stable should the repo produce decision-grade external-versus-internal outputs.
**Delivers:** Shared benchmark spec, per-target run manifests, normalized case-result rows, aggregate summaries by family and fidelity, control deltas, inspect surfaces, and recommendation lines for roadmap follow-up.
**Addresses:** `LLM-32`, `LLM-33`, and `OPS-18`.
**Avoids:** Misleading aggregate scores, overclaiming from a tiny benchmark, and disconnected reporting artifacts.

### Phase Ordering Rationale

- Phase 34 first because benchmark credibility depends on frozen case selection and explicit control-arm definition, not on runtime completeness.
- Phase 35 second because the benchmark cannot be trusted until external targets are revision-pinned, smoke-tested, and reproducibly executable.
- Phase 36 last because scorecards and milestone decisions are only meaningful once per-case lineage and execution contracts are stable.
- This grouping preserves the repo's additive architecture: immutable input artifacts first, execution lineage second, operator-facing summary last.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 35:** Validate the initial external-model shortlist, adapter-backed cases, hardware envelopes, and any model-specific prompt or parser quirks before locking the final benchmark lane list.
- **Phase 36:** Confirm the exact metric and parser contracts for each benchmark family if the milestone expands beyond simple CIF and material-string generation slices.

Phases with standard patterns (skip research-phase):
- **Phase 34:** Strong repo precedent already exists for schema-backed manifests, file-backed inventories, and freeze-style artifact creation.
- **Most of Phase 36:** Summary artifact writing, CLI inspect surfaces, and compare-style aggregation align closely with existing benchmark patterns once the case-result schema is fixed.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Repo fit is strong and the runtime recommendations are grounded in official PyTorch and Hugging Face docs. |
| Features | HIGH | The minimum credible feature set is consistent across all four research documents and tightly scoped to the milestone goal. |
| Architecture | MEDIUM | Storage shape and component boundaries are clear, but the exact prompt and result contract still needs to be frozen during planning. |
| Pitfalls | HIGH | The main failure modes are concrete, repo-specific, and already map cleanly to phase boundaries. |

**Overall confidence:** MEDIUM

### Gaps to Address

- Final external-model shortlist: upstream packaging quality and adapter requirements vary, so the benchmark lane list still needs explicit operator validation.
- Prompt and parser contract: the exact request template and parsed-output schema per benchmark family should be fixed before implementation starts.
- Hardware envelope: the MVP needs one explicit tested device and offload policy so reruns do not silently change behavior.
- Metric granularity: if the benchmark grows beyond basic validity and fidelity-aware comparisons, metric definitions will need a short research pass before phase planning finalizes.

## Sources

### Primary (HIGH confidence)
- Repo research documents: `.planning/research/STACK.md`, `.planning/research/FEATURES.md`, `.planning/research/ARCHITECTURE.md`, `.planning/research/PITFALLS.md`
- Repo implementation references: `materials-discovery/src/materials_discovery/llm/schema.py`, `materials-discovery/src/materials_discovery/llm/storage.py`, `materials-discovery/src/materials_discovery/llm/runtime.py`, `materials-discovery/src/materials_discovery/llm/translation_bundle.py`, `materials-discovery/src/materials_discovery/llm/checkpoints.py`, `materials-discovery/src/materials_discovery/llm/serving_benchmark.py`
- Repo docs: `materials-discovery/developers-docs/llm-translation-contract.md`, `materials-discovery/developers-docs/llm-translation-runbook.md`
- Official docs: PyTorch reproducibility and deterministic algorithms docs; Hugging Face Hub download and environment-variable docs; Transformers model loading docs; Accelerate big-model docs

### Secondary (MEDIUM confidence)
- Hugging Face PEFT docs for adapter-backed model loading
- CrystaLLM upstream repository
- CrystalTextLLM upstream repository
- Materials-LLM robustness paper: Wang et al., Digital Discovery (2025)

## Milestone Recommendation

Plan `v1.6` as a three-phase, benchmark-first milestone and hold scope there.
Success means one frozen fidelity-aware benchmark set, a small allowlisted set
of reproducibly runnable external models, one shared benchmark against promoted
or pinned internal controls, and a scorecard that can support a clear
continue-or-stop decision without hiding fidelity caveats. Do not broaden the
milestone into generic external serving, training automation, or UI work.

**File changed:** `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/SUMMARY.md`

---
*Research completed: 2026-04-07*
*Ready for roadmap: yes*
