---
phase: 37-deep-dive-provenance-audit-and-tutorial-scope
requirement: DOC-01
status: evidence-packet
created: 2026-04-15
---

# Phase 37 Provenance Audit and Tutorial Scope

## Scope Boundary

- Phase 37 does not rewrite materials-discovery/developers-docs/podcast-deep-dive-source.md.
- Phase 37 does not author the guided tutorial.
- Phase 37 does not edit materials-discovery/, so materials-discovery/Progress.md is intentionally unchanged.
- Refresh claims must be backed by git history, shipped milestone audits, current docs, or current source code.

## Source Document Provenance

`materials-discovery/developers-docs/podcast-deep-dive-source.md` was created before the current `materials-discovery/` documentation layout and moved twice before landing at its current path. The ledger below is backed by `git log --follow --date=iso-strict --format='%H%x09%ad%x09%an%x09%s' --name-status -- materials-discovery/developers-docs/podcast-deep-dive-source.md`.

| Event | Commit | Date | Evidence |
|-------|--------|------|----------|
| Created | `359cef57777479fb15652f1f4c702c43a25c4bc6` | `2026-03-06T19:53:04-05:00` | `A developer-docs/podcast-deep-dive-source.md` |
| First move | `9d7e7bc8189b067155a147ce2dd1e180688ef96f` | `2026-03-06T20:01:04-05:00` | `R099 developer-docs/podcast-deep-dive-source.md -> developer-docs/materials_discovery/podcast-deep-dive-source.md` |
| Current move | `f21c17e3c1a246349d0d0171cfa0b9390bcc8c1d` | `2026-04-02T20:48:12-04:00` | `R098 developer-docs/materials_discovery/podcast-deep-dive-source.md -> materials-discovery/developers-docs/podcast-deep-dive-source.md` |

## Post-Draft Shipped Workflow Deltas

The first source draft landed on 2026-03-06. The shipped milestone audits below show the workflow surface that Phase 38 must consider when refreshing the narrative.

| Milestone | Milestone audit path | Shipped-surface summary |
|-----------|----------------------|-------------------------|
| `v1.0` | `.planning/milestones/v1.0-MILESTONE-AUDIT.md` | Multi-source ingestion, reference-aware workflow, LLM corpus/generate/evaluate/suggest surfaces. |
| `v1.1` | `.planning/milestones/v1.1-MILESTONE-AUDIT.md` | Proposal, approval, launch, replay, and compare campaign workflow. |
| `v1.2` | `.planning/milestones/v1.2-MILESTONE-AUDIT.md` | Hosted/local/specialized serving lanes and serving benchmark workflow. |
| `v1.3` | `.planning/milestones/v1.3-MILESTONE-AUDIT.md` | Adapted checkpoint registration, strict lane resolution, adapted-vs-baseline benchmarks, rollback guidance. |
| `v1.4` | `.planning/milestones/v1.4-MILESTONE-AUDIT.md` | Checkpoint-family lifecycle, promoted default, explicit pin, promotion, and retirement. |
| `v1.5` | `.planning/v1.5-MILESTONE-AUDIT.md` | CIF/material-string translation bundles with fidelity/loss semantics. |
| `v1.6` | `.planning/v1.6-MILESTONE-AUDIT.md` | Translated benchmark freeze, external target registration, comparative external benchmark, and fidelity-aware scorecards. |

## Stale Quantitative Claims

Quantitative claims in `podcast-deep-dive-source.md` are fast-moving and must not be refreshed from memory. D-04 and D-06 require dated command-backed evidence or softer prose.

| Source location | Exact source string | Current evidence command from `37-RESEARCH.md` | Audit result | Phase 38 action | Decision controls |
|-----------------|---------------------|-----------------------------------------------|--------------|-----------------|-------------------|
| `materials-discovery/developers-docs/podcast-deep-dive-source.md:78` and `:269` | `4,238 commits` | `git rev-list --count HEAD`; `git rev-list --count 359cef57777479fb15652f1f4c702c43a25c4bc6` | Stale | Refresh from a dated command only if the count matters; otherwise soften or remove. | D-04, D-06 |
| `materials-discovery/developers-docs/podcast-deep-dive-source.md:220` | `seven commands` | `cd materials-discovery && uv run mdisc --help`; `rg -n '@(?:app\|lake_app\|llm_corpus_app)\.command' src/materials_discovery/cli.py` | Stale | Refresh from a dated command only if the count matters; otherwise soften or remove. | D-03, D-04, D-06 |
| `materials-discovery/developers-docs/podcast-deep-dive-source.md:220` | `60 modules` | `find materials-discovery/src/materials_discovery -type f -name '*.py' \| wc -l` | Stale | Refresh from a dated command only if the count matters; otherwise soften or remove. | D-04, D-06 |
| `materials-discovery/developers-docs/podcast-deep-dive-source.md:220` | `7,200 lines of code` | `find materials-discovery/src/materials_discovery -type f -name '*.py' -print0 \| xargs -0 wc -l \| tail -1` | Stale | Refresh from a dated command only if the count matters; otherwise soften or remove. | D-04, D-06 |
| `materials-discovery/developers-docs/podcast-deep-dive-source.md:289` | `21 test files` | `find materials-discovery/tests -type f -name 'test_*.py' \| wc -l` | Stale | Refresh from a dated command only if the count matters; otherwise soften or remove. | D-04, D-06 |

## Stale Capability Descriptions

| Source string or heading | Current evidence source path | Audit result | Required Phase 38 correction | Decision controls |
|--------------------------|------------------------------|--------------|------------------------------|-------------------|
| `Seven Pipeline Stages` | `materials-discovery/developers-docs/index.md:27-45`; `materials-discovery/src/materials_discovery/cli.py:796-2687`; `.planning/milestones/v1.0-MILESTONE-AUDIT.md`; `.planning/v1.6-MILESTONE-AUDIT.md` | Stale | Reframe as a core design/evaluation pipeline plus shipped additive surfaces for Zomic export, LLM generation/evaluation/suggestion, campaigns, serving, checkpoint lifecycle, translation, and external benchmarking. | D-01, D-02, D-03, D-04 |
| `four execution layers` | `materials-discovery/src/materials_discovery/common/schema.py:115-176`; `materials-discovery/developers-docs/backend-system.md:125-302`; `materials-discovery/developers-docs/podcast-deep-dive-source.md:248` | Stale | Describe backend modes as `mock` and `real`, with fixture-backed, exec-cache, and native provider layers under the real-mode adapter system. | D-03, D-04 |
| `targets three real alloy systems` | `materials-discovery/developers-docs/index.md:118-142`; `materials-discovery/RUNBOOK.md:33-47`; `materials-discovery/developers-docs/podcast-deep-dive-source.md:285` | Stale | Avoid a narrow system count; describe checked configs and example lanes, including Sc-Zn Zomic-backed and reference-aware variants, with a link to the current docs map. | D-01, D-02, D-04, D-06 |
| `full seven-stage pipeline` | `materials-discovery/developers-docs/pipeline-stages.md:1-13`; `materials-discovery/developers-docs/pipeline-stages.md:1586-1608`; `materials-discovery/RUNBOOK.md:646-875` | Stale | Keep the seven-stage path as the core operator loop but explicitly state that the shipped workflow now extends through campaign, serving, checkpoint, translation, and external benchmark surfaces. | D-01, D-02, D-03, D-04 |

## Missing Shipped Surfaces For Phase 38

Phase 38 should not turn the deep dive into a command manual, per D-01 and D-02. It must, however, acknowledge the shipped workflow surface through v1.6, per D-03, and cross-link current references rather than duplicating every operator step.

| Shipped surface | Evidence source path | Audit result | Required Phase 38 correction | Decision controls |
|-----------------|----------------------|--------------|------------------------------|-------------------|
| `mdisc export-zomic` | `materials-discovery/developers-docs/index.md:27`; `materials-discovery/developers-docs/pipeline-stages.md:78`; `materials-discovery/src/materials_discovery/cli.py:2067` | Missing from source narrative | Add as the shipped Zomic design export bridge that precedes the Sc-Zn tutorial path. | D-02, D-03, D-04 |
| `mdisc llm-generate` | `materials-discovery/developers-docs/index.md:34`; `materials-discovery/developers-docs/pipeline-stages.md:543`; `materials-discovery/src/materials_discovery/cli.py:935` | Missing from source narrative | Mention as a shipped additive candidate-generation lane, not as a replacement for deterministic generation. | D-01, D-03, D-04 |
| `mdisc llm-evaluate` | `materials-discovery/developers-docs/index.md:35`; `materials-discovery/developers-docs/pipeline-stages.md:616`; `materials-discovery/src/materials_discovery/cli.py:1195` | Missing from source narrative | Mention as shipped additive assessment output for ranked candidates. | D-01, D-03, D-04 |
| `mdisc llm-suggest` | `materials-discovery/developers-docs/index.md:36`; `materials-discovery/RUNBOOK.md:646`; `materials-discovery/src/materials_discovery/cli.py:1266` | Missing from source narrative | Mention dry-run suggestion proposals as shipped, operator-governed workflow. | D-01, D-03, D-04, D-05 |
| `mdisc llm-approve` | `materials-discovery/RUNBOOK.md:647`; `materials-discovery/developers-docs/pipeline-stages.md:745`; `materials-discovery/src/materials_discovery/cli.py:1285` | Missing from source narrative | Mention approval artifacts as the boundary between suggestions and executable campaigns. | D-01, D-03, D-04, D-05 |
| `mdisc llm-launch` | `materials-discovery/RUNBOOK.md:648`; `materials-discovery/developers-docs/pipeline-stages.md:795`; `materials-discovery/src/materials_discovery/cli.py:1356` | Missing from source narrative | Mention approved campaign launch as shipped, still operator controlled. | D-01, D-03, D-04, D-05 |
| `mdisc llm-replay` | `materials-discovery/RUNBOOK.md:649`; `materials-discovery/developers-docs/pipeline-stages.md:881`; `materials-discovery/src/materials_discovery/cli.py:1557` | Missing from source narrative | Mention strict replay for provenance and comparison, not autonomous optimization. | D-01, D-03, D-04, D-05 |
| `mdisc llm-compare` | `materials-discovery/RUNBOOK.md:650`; `materials-discovery/developers-docs/pipeline-stages.md:948`; `materials-discovery/src/materials_discovery/cli.py:1760` | Missing from source narrative | Mention launch comparison as shipped evidence for campaign decisions. | D-01, D-03, D-04 |
| `mdisc llm-register-checkpoint` | `materials-discovery/RUNBOOK.md:692`; `materials-discovery/developers-docs/pipeline-stages.md:1003`; `materials-discovery/src/materials_discovery/cli.py:1016` | Missing from source narrative | Mention adapted checkpoint registration with pinned lineage. | D-01, D-03, D-04, D-05 |
| `mdisc llm-list-checkpoints` | `materials-discovery/RUNBOOK.md:765`; `materials-discovery/src/materials_discovery/cli.py:1125` | Missing from source narrative | Mention lifecycle visibility for checkpoint families. | D-01, D-03, D-04 |
| `mdisc llm-promote-checkpoint` | `materials-discovery/RUNBOOK.md:789`; `materials-discovery/src/materials_discovery/cli.py:1148` | Missing from source narrative | Mention benchmark-backed promotion as operator action, not automatic training. | D-01, D-03, D-04, D-05 |
| `mdisc llm-retire-checkpoint` | `materials-discovery/RUNBOOK.md:801`; `materials-discovery/src/materials_discovery/cli.py:1172` | Missing from source narrative | Mention safe retirement for superseded checkpoint family members. | D-01, D-03, D-04 |
| `mdisc llm-serving-benchmark` | `materials-discovery/RUNBOOK.md:723-833`; `materials-discovery/developers-docs/pipeline-stages.md:1055`; `materials-discovery/src/materials_discovery/cli.py:1792` | Missing from source narrative | Mention shared-context serving comparisons across hosted, local, specialized, and adapted lanes. | D-01, D-03, D-04 |
| `mdisc llm-translate` | `materials-discovery/developers-docs/index.md:37`; `materials-discovery/developers-docs/pipeline-stages.md:1122`; `materials-discovery/src/materials_discovery/cli.py:1878` | Missing from source narrative | Mention deterministic CIF/material-string translation bundles with loss posture. | D-01, D-03, D-04, D-05 |
| `mdisc llm-translate-inspect` | `materials-discovery/developers-docs/index.md:38`; `materials-discovery/developers-docs/pipeline-stages.md:1182`; `materials-discovery/src/materials_discovery/cli.py:1936` | Missing from source narrative | Mention inspectable translation traces for operator review. | D-01, D-02, D-03, D-04 |
| `mdisc llm-translated-benchmark-freeze` | `materials-discovery/developers-docs/index.md:39`; `materials-discovery/developers-docs/pipeline-stages.md:1231`; `materials-discovery/src/materials_discovery/cli.py:1981` | Missing from source narrative | Mention frozen translated benchmark packs with explicit inclusion/exclusion semantics. | D-01, D-03, D-04 |
| `mdisc llm-translated-benchmark-inspect` | `materials-discovery/developers-docs/index.md:40`; `materials-discovery/developers-docs/pipeline-stages.md:1285`; `materials-discovery/src/materials_discovery/cli.py:2011` | Missing from source narrative | Mention benchmark-pack inspection as the operator surface for included/excluded rows. | D-01, D-02, D-03, D-04 |
| `mdisc llm-register-external-target` | `materials-discovery/developers-docs/index.md:41`; `materials-discovery/developers-docs/pipeline-stages.md:1338`; `materials-discovery/src/materials_discovery/cli.py:1029` | Missing from source narrative | Mention immutable external target registration with reproducibility-grade identity. | D-01, D-03, D-04, D-05 |
| `mdisc llm-inspect-external-target` | `materials-discovery/developers-docs/index.md:42`; `materials-discovery/developers-docs/pipeline-stages.md:1389`; `materials-discovery/src/materials_discovery/cli.py:1042` | Missing from source narrative | Mention target inspection for registration, environment, and smoke artifacts. | D-01, D-02, D-03, D-04 |
| `mdisc llm-smoke-external-target` | `materials-discovery/developers-docs/index.md:43`; `materials-discovery/developers-docs/pipeline-stages.md:1436`; `materials-discovery/src/materials_discovery/cli.py:1112` | Missing from source narrative | Mention smoke capture as readiness evidence before external comparison. | D-01, D-03, D-04 |
| `mdisc llm-external-benchmark` | `materials-discovery/developers-docs/index.md:44`; `materials-discovery/developers-docs/pipeline-stages.md:1486`; `materials-discovery/src/materials_discovery/cli.py:1823`; `.planning/v1.6-MILESTONE-AUDIT.md` | Missing from source narrative | Mention comparative external-vs-internal benchmark execution on translated case slices. | D-01, D-03, D-04, D-05 |
| `mdisc llm-inspect-external-benchmark` | `materials-discovery/developers-docs/index.md:45`; `materials-discovery/developers-docs/pipeline-stages.md:1547`; `materials-discovery/src/materials_discovery/cli.py:1840`; `.planning/v1.6-MILESTONE-AUDIT.md` | Missing from source narrative | Mention fidelity-aware scorecard inspection and bounded recommendation lines. | D-01, D-02, D-03, D-04 |

## Future-Work Labeling Risks

| Risk | Why it matters | Required label/control | Decision controls |
|------|----------------|------------------------|-------------------|
| Autonomous campaigns beyond the shipped operator-approved campaign workflow | The shipped surface covers proposal, approval, launch, replay, and compare; unsupervised autonomy remains future work. | Label any broader autonomy as future work and keep the current-state narrative operator-governed. | D-01, D-03, D-05 |
| Checkpoint training automation beyond registration/lifecycle/benchmark-backed promotion | The shipped surface manages adapted checkpoint registration, lifecycle, promotion, retirement, and benchmark evidence, not automatic training. | Label training/fine-tuning automation as future work and cite lifecycle docs for current capability. | D-01, D-03, D-05 |
| Reverse import or new visualization exporters beyond the current Zomic/vZome path | Phase 37-39 should teach the current Zomic design/export artifacts, not imply new reverse import or visualization exporters. | Label reverse import and new exporters as future work; use existing Zomic/vZome authority artifacts for current claims. | D-02, D-04, D-05 |
| Broad chemistry expansion beyond the checked Sc-Zn tutorial anchor | The tutorial scope is one reproducible Sc-Zn Zomic-backed path; broader chemistry examples would dilute the first tutorial and create unverified claims. | Label broad chemistry coverage as future work and keep current tutorial claims tied to checked Sc-Zn artifacts. | D-01, D-04, D-05, D-06 |

## Tutorial Anchor Scope Lock

Only worked tutorial system: Sc-Zn.

Default tutorial anchor: reproducible Sc-Zn Zomic-backed path.

Broader chemistry coverage is deferred by D-09.

The tutorial must use checked config and design assets first, per D-07 and D-08.

The tutorial must include commands, artifact locations, and interpretation checkpoints, per D-10 and D-11.

The visualization section must identify the Zomic design and export artifacts as the geometry authority, per D-12.

| Step | Locked command or checkpoint | Evidence basis |
|------|------------------------------|----------------|
| Workspace entry | `cd materials-discovery` | `materials-discovery/RUNBOOK.md` and current command docs assume execution from this directory. |
| Zomic export | `uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml` | `materials-discovery/developers-docs/zomic-design-workflow.md`; `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`; `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml`. |
| Candidate generation | `uv run mdisc generate --config configs/systems/sc_zn_zomic.yaml --count 32` | `materials-discovery/developers-docs/zomic-design-workflow.md`; `materials-discovery/configs/systems/sc_zn_zomic.yaml`. |
| Screening | `uv run mdisc screen --config configs/systems/sc_zn_zomic.yaml` | `materials-discovery/RUNBOOK.md`; `materials-discovery/developers-docs/pipeline-stages.md`. |
| Validation | `uv run mdisc hifi-validate --config configs/systems/sc_zn_zomic.yaml --batch all` | `materials-discovery/RUNBOOK.md`; `materials-discovery/developers-docs/pipeline-stages.md`. |
| Ranking | `uv run mdisc hifi-rank --config configs/systems/sc_zn_zomic.yaml` | `materials-discovery/RUNBOOK.md`; `materials-discovery/developers-docs/pipeline-stages.md`. |
| Report | `uv run mdisc report --config configs/systems/sc_zn_zomic.yaml` | `materials-discovery/RUNBOOK.md`; `materials-discovery/developers-docs/pipeline-stages.md`. |

## Tutorial Artifact Set

Phase 39 should treat the following checked paths and stage outputs as the tutorial's artifact contract. Missing optional outputs should be called out as run-produced artifacts, not invented or silently replaced.

| Artifact | Tutorial role |
|----------|---------------|
| `materials-discovery/configs/systems/sc_zn_zomic.yaml` | System config that activates the Sc-Zn Zomic generation lane. |
| `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml` | Zomic design metadata, anchor prototype linkage, and export target paths. |
| `materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic` | Source Zomic geometry design. |
| `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json` | Raw vZome Zomic export artifact. |
| `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json` | Orbit-library prototype consumed by generation after export. |
| `materials-discovery/data/prototypes/sc_zn_tsai_sczn6.json` | Anchor prototype used to align the exported Zomic design. |
| `materials-discovery/data/candidates/sc_zn_candidates.jsonl` | Generated candidate structures. |
| `materials-discovery/data/manifests/sc_zn_generate_manifest.json` | Generate-stage provenance and output hashes. |
| `materials-discovery/data/screened/sc_zn_screened.jsonl` | Fast-screened candidates. |
| `materials-discovery/data/calibration/sc_zn_screen_calibration.json` | Screening calibration output. |
| `materials-discovery/data/hifi_validated/sc_zn_all_validated.jsonl` | High-fidelity validation output for the full batch. |
| `materials-discovery/data/ranked/sc_zn_ranked.jsonl` | Ranked candidates with benchmark context. |
| `materials-discovery/data/reports/sc_zn_report.json` | Experiment report for tutorial interpretation. |
| `materials-discovery/data/reports/sc_zn_xrd_patterns.jsonl` | XRD pattern output referenced by report interpretation. |
| `materials-discovery/data/reports/sc_zn_benchmark_pack.json` | Benchmark-pack artifact when the run produces benchmark context. |

## Phase 38 Correction Checklist

- Replace the `seven commands` framing with the shipped through-v1.6 workflow surface: core design/generate/screen/validate/rank/report work plus Zomic export, LLM generation/evaluation/suggestion, campaign governance, serving benchmarks, checkpoint lifecycle, translation, and external benchmark commands.
- Soften or date fast-moving quantitative claims such as commit count, command count, Python module count, line count, and test-file count. Keep exact numbers only when copied from a dated command run.
- Describe backend modes as `mock` and `real` with fixture, exec, and native layers rather than preserving the stale `four execution layers` phrasing.
- Cross-link current runbooks and references instead of duplicating every operator step: `materials-discovery/RUNBOOK.md`, `materials-discovery/developers-docs/index.md`, `materials-discovery/developers-docs/pipeline-stages.md`, `materials-discovery/developers-docs/backend-system.md`, and `materials-discovery/developers-docs/zomic-design-workflow.md`.
- Label future work explicitly when discussing autonomous campaigns, checkpoint training automation, reverse import, new visualization exporters, or chemistry expansion beyond the checked tutorial anchor.

## Phase 39 Tutorial Scope Lock

- Stay on the Sc-Zn Zomic-backed path as the single worked example.
- Teach design, generate, screen, validate, rank, report, and visualize as one reproducible flow.
- Explain screening, validation, ranking, and report interpretation using the stage artifacts in `## Tutorial Artifact Set`.
- Point to exact Zomic design/export artifacts as the geometry authority: `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml`, `materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic`, `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json`, and `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json`.
- Phase 39 must avoid adding Al-Cu-Fe, external benchmark, or native MLIP as second worked examples.

## Evidence Commands

Git provenance:

```bash
git log --follow --date=iso-strict \
  --format='%H%x09%ad%x09%an%x09%s' \
  --name-status -- \
  materials-discovery/developers-docs/podcast-deep-dive-source.md
```

Stale-claim scan:

```bash
rg -n "seven commands|60 modules|7,200|21 test files|4,238|future|planned|will" \
  materials-discovery/developers-docs/podcast-deep-dive-source.md \
  materials-discovery/developers-docs/index.md \
  materials-discovery/RUNBOOK.md
```

Command-surface scan:

```bash
cd materials-discovery
uv run mdisc --help
rg -n '@(?:app|lake_app|llm_corpus_app)\.command' src/materials_discovery/cli.py
```

Quantitative refresh commands:

```bash
git rev-list --count HEAD
git rev-list --count 359cef57777479fb15652f1f4c702c43a25c4bc6
find materials-discovery/src/materials_discovery -type f -name '*.py' | wc -l
find materials-discovery/src/materials_discovery -type f -name '*.py' -print0 | xargs -0 wc -l | tail -1
find materials-discovery/tests -type f -name 'test_*.py' | wc -l
```

Tutorial artifact existence checks:

```bash
ls -l \
  materials-discovery/configs/systems/sc_zn_zomic.yaml \
  materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml \
  materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic \
  materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json \
  materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json \
  materials-discovery/data/prototypes/sc_zn_tsai_sczn6.json
```
