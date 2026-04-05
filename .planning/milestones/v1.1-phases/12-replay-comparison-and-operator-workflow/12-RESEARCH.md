# Phase 12: Replay, Comparison, and Operator Workflow - Research

**Date:** 2026-04-04  
**Status:** Complete  
**Requirements:** `LLM-09`, `LLM-11`, `OPS-07`

## Goal

Make the closed-loop campaign workflow replayable, comparable, and safe for
regular operator use without weakening the approval and launch boundaries that
Phases 10 and 11 already established.

Phase 12 must:

- replay a saved campaign launch from the recorded launch artifacts rather than
  reinterpreting approval-time intent
- compare current launch outcomes against both the originating acceptance pack
  and the most recent prior launch when available
- preserve additive lineage and campaign-root audit artifacts
- ship a real operator runbook for suggest, approve, launch, replay, compare,
  and interpretation

Phase 12 must not:

- add replay-time behavioral overrides
- auto-chain the downstream pipeline
- weaken the approval boundary or fold replay/compare back into launch
- introduce autonomous execution or local fine-tuned serving

## Current Surface

### Phase 11 already created the execution bridge

The repo already has:

- `mdisc llm-suggest` for dry-run proposals
- `mdisc llm-approve` for approval artifacts and `campaign_spec.json`
- `mdisc llm-launch --campaign-spec ...` for execution
- additive `source_lineage.llm_campaign` propagation into downstream manifests

The current launch artifact family is:

- `data/llm_campaigns/{campaign_id}/campaign_spec.json`
- `data/llm_campaigns/{campaign_id}/launches/{launch_id}/resolved_launch.json`
- `data/llm_campaigns/{campaign_id}/launches/{launch_id}/launch_summary.json`
- standard run artifacts under `data/llm_runs/...`
- standard candidate/manifests/calibration outputs under `data/`

What does **not** exist yet:

- a replay command
- a comparison command
- an immutable per-launch outcome snapshot
- a campaign-level comparison artifact
- a runbook that covers the full Phase 10-12 loop end to end

### Launch artifacts are close to replay-ready, but not sufficient alone

`resolved_launch.json` already freezes:

- resolved model lane
- adapter/provider/model
- prompt instruction deltas
- resolved composition bounds
- resolved example-pack and seed paths

But strict replay also needs values that currently live outside
`resolved_launch.json`, especially in:

- `run_manifest.json`
- `prompt.json`

Those files carry the actual prompt template, request count, temperature,
max_tokens, prompt text, and conditioning-example IDs. Phase 12 replay should
therefore treat the launch bundle as:

- `launch_summary.json`
- `resolved_launch.json`
- `campaign_spec.json`
- `run_manifest.json`
- `prompt.json`

not as `resolved_launch.json` alone.

## Key Design Findings

### 1. Replay should create a new launch record, not a parallel replay tree

The cleanest Phase 12 behavior is:

- replay is a new execution
- it gets a new `launch_id`
- it still writes `resolved_launch.json` and `launch_summary.json` under
  `data/llm_campaigns/{campaign_id}/launches/{launch_id}/`
- it carries additive replay lineage such as:
  - `replay_of_launch_id`
  - `replay_of_launch_summary_path`

Why this is better than a separate `replays/` tree:

- it keeps one canonical execution history under `launches/`
- prior-launch lookup becomes simpler and deterministic
- downstream lineage can keep using the existing `llm_campaign` block rather
  than branching into a second wrapper shape

### 2. Strict replay should be authority-driven, not hash-gated

Phase 11 launch correctly fails when the current config hash drifts from the
approved campaign spec. Phase 12 replay is different. If replay is driven by
the recorded launch artifact, then a pure config-hash mismatch should not
automatically block replay.

Recommended replay posture:

1. Load the current system config as a structural scaffold.
2. Require the scaffold to match the same system and template family.
3. Overwrite the launch-relevant fields with the recorded launch bundle:
   - composition bounds
   - prompt template
   - temperature
   - max_tokens
   - max_attempts
   - example-pack path
   - max_conditioning_examples
   - seed path
   - adapter/provider/model/api_base
4. Record both the source hash and the current hash in replay metadata.
5. Fail only when the replay cannot reconstruct the same effective launch
   inputs, not merely because the config file changed textually.

This matches the Phase 12 user decision that replay is authority-driven by the
recorded launch artifacts.

### 3. Comparison needs an immutable per-launch outcome snapshot

Current launch-side run artifacts are stable enough for generation metrics:

- `run_manifest.json` gives attempt/generation counts
- `compile_results.jsonl` allows parse/compile pass counts to be recomputed

But downstream stage manifests and calibration files are mostly written to
standard system-level paths and can be overwritten by later runs. That means
historical comparison cannot rely on "whatever is currently in
`data/manifests/`" for older launches.

Phase 12 therefore needs an immutable `outcome_snapshot.json` written under the
campaign launch directory. That snapshot should:

- always include launch-level generation metrics
- include downstream metrics when a matching stage manifest currently exists and
  still points at the same `launch_id`
- be reused on later comparison runs instead of trying to rediscover historical
  state from mutable standard paths

This is the key step that turns comparison from best-effort inspection into a
durable operator workflow.

### 4. Acceptance-pack comparison should reuse Phase 9 metric semantics

Acceptance-pack system metrics already define the comparison language that Phase
12 operators understand:

- `parse_success_rate`
- `compile_success_rate`
- `generation_success_rate`
- `shortlist_pass_rate`
- `validation_pass_rate`
- `novelty_score_mean`
- `synthesizability_mean`
- `report_release_gate_ready`

Phase 12 should not invent a separate metric vocabulary. Instead it should
materialize current launch outcomes into the same metric names, with `None` or
"missing" markers when downstream data is not yet available.

That lets Phase 12 compare:

- current outcome vs acceptance-pack baseline
- current outcome vs most recent prior launch

using the same metric names and threshold semantics that already exist in the
Phase 9 acceptance workflow.

### 5. Prior-launch lookup should be deterministic and campaign-local

The best v1.1 prior-launch rule is:

- same `campaign_id`
- same `system`
- exclude the current launch
- sort by `created_at_utc`, then `launch_id`
- pick the latest prior one

This keeps the rule deterministic, easy to explain, and local to the approved
campaign scope rather than reaching across unrelated campaigns.

### 6. The benchmark compare engine is useful as a formatting reference, not a direct dependency

`materials_discovery/lake/compare.py` already provides:

- typed comparison results
- JSON artifact writing
- terminal-table formatting

That is a useful design precedent for Phase 12. But campaign comparison is not
identical to benchmark-pack comparison because:

- campaign comparisons are launch-centric, not lane-centric
- acceptance-pack baselines are not full benchmark-pack artifacts
- prior-launch baselines may have partial downstream data

So Phase 12 should build its own `llm/compare.py` surface while borrowing the
same dual-output pattern:

- JSON artifact for machines
- concise terminal summary for operators

## Recommended Implementation Split

### Plan 01: replay/comparison contract foundation

Lock the typed artifacts, storage helpers, launch-bundle loader, replay input
freezing, outcome snapshot, and prior-launch lookup before touching the CLI.

### Plan 02: operator replay and compare commands

Once the contracts are stable:

- add `mdisc llm-replay --launch-summary ...`
- add `mdisc llm-compare --launch-summary ...`
- emit JSON artifacts plus operator-readable terminal summaries
- preserve additive campaign lineage for replayed runs

### Plan 03: full workflow docs and regression proof

After commands work:

- update `RUNBOOK.md`
- update `developers-docs/llm-integration.md`
- update `developers-docs/pipeline-stages.md`
- add offline regression coverage for suggest/approve/launch/replay/compare

## Risks and Edge Cases To Lock In Planning

### Historical downstream data may be missing

Older launches can always be compared at the generation layer because the
run-level artifacts are durable. Downstream metrics may be unavailable if a
later run overwrote the standard stage outputs before Phase 12 snapshotting was
introduced. Comparison artifacts should surface missing metrics explicitly
rather than pretending the comparison is complete.

### Replay must not silently change the model lane

If a replay falls back to a different adapter/provider/model than the source
launch, the replay is not strict. Phase 12 should therefore reuse the recorded
resolved lane and backend tuple from the source bundle rather than re-running
lane selection heuristics.

### Replay outputs must not overwrite the original launch outputs

Replay is a new execution and should write to deterministic new paths under the
standard roots. Overwriting the original launch candidates or manifests would
destroy the very evidence the operator is trying to compare.

### CLI summaries must stay useful without a notebook

Phase 12 is explicitly an operator workflow phase. JSON-only output would leave
too much friction for quick decisions. Every compare run should print a concise
summary of:

- the current launch
- the acceptance-pack delta summary
- whether a prior launch baseline was found
- the highest-signal improvements or regressions

