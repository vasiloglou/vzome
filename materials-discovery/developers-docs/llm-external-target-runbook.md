# External Target Runbook

This runbook explains how to register one curated external benchmark target,
inspect its immutable identity, run the Phase 35 smoke path, and understand the
artifact layout that Phase 36 will consume later.

Phase 35 is deliberately narrow. It does not download models, launch generic
servers, execute comparative benchmarks, or emit scorecards yet.

---

## When to register an external target

Register an external target after:

- Phase 34 has already frozen the translated benchmark pack you plan to reuse
- you have downloaded one local model snapshot for a curated external runtime
- you want one immutable registration artifact before any Phase 36 benchmark
  execution begins

Use this workflow when you need:

- one stable `model_id` and fingerprint for later benchmark bookkeeping
- explicit snapshot-lineage and prompt/parser contract metadata
- a typed smoke artifact that proves the target can still resolve its local
  snapshot and current environment

---

## Required inputs

You need:

1. one typed external-target spec YAML file
2. one local snapshot directory for the target model
3. an optional snapshot-manifest file when you maintain one beside the snapshot
4. the normal repo workspace so CLI commands can resolve relative artifact
   paths

The repo ships two example specs:

- `configs/llm/al_cu_fe_external_cif_target.yaml`
- `configs/llm/al_cu_fe_external_material_string_target.yaml`

Those example files are templates, not fully runnable snapshots. Replace the
placeholder `local_snapshot_path`, `snapshot_manifest_path`, and pinned revision
fields with your downloaded model before running registration.

---

## Register an external target

```bash
cd materials-discovery
uv run mdisc llm-register-external-target \
  --spec configs/llm/al_cu_fe_external_cif_target.yaml
```

The command prints a JSON summary with:

- `model_id`
- `fingerprint`
- `registration_path`

Registration fails closed if:

- the spec file is missing
- the spec does not validate
- the referenced snapshot path does not exist
- the same `model_id` already exists with a different fingerprint

---

## Inspect a registered target

```bash
uv run mdisc llm-inspect-external-target \
  --model-id al_cu_fe_external_cif_demo
```

The inspect command prints a concise human-readable trace of:

- immutable registration facts such as model family, provider/model, runner,
  target families, fingerprint, and prompt/parser contracts
- the persisted registration artifact path
- the latest environment artifact path and capture metadata when
  `environment.json` exists
- the latest smoke artifact path and smoke status when `smoke_check.json`
  exists

If environment or smoke artifacts do not exist yet, the inspect output keeps
that absence explicit instead of pretending the target was already prepared.

---

## Run the external-target smoke path

```bash
uv run mdisc llm-smoke-external-target \
  --model-id al_cu_fe_external_cif_demo
```

The command prints the typed `LlmExternalTargetSmokeCheck` JSON summary. It also
persists:

- `environment.json`
- `smoke_check.json`

The smoke path is intentionally conservative. It captures the current Python,
platform, optional package-version, and CUDA visibility context, then fails
closed if the registered snapshot lineage no longer resolves.

---

## Artifact layout

Each registered target writes one directory under:

```text
data/llm_external_models/{model_id}/
```

Files inside that directory:

- `registration.json` -- immutable target identity, snapshot lineage, prompt
  contract, parser key, and conflict-detecting fingerprint
- `environment.json` -- mutable reproducibility capture for the current Python,
  platform, package versions, and visibility context
- `smoke_check.json` -- latest typed smoke result tied back to the registration
  fingerprint

Phase 35 ends with this artifact family. These files are the handoff boundary
for Phase 36 comparative benchmark execution and scorecards.

---

## Immutable identity versus mutable readiness

Treat the three files differently:

- `registration.json` is the source of truth for immutable target identity
- `environment.json` is one observation of the runtime context that was present
  when the target was prepared
- `smoke_check.json` is the latest readiness result and may change between runs

If you need to change model family, provider/model, snapshot lineage, prompt
contract, or other immutable fields, write a new registration spec and register
that target intentionally. Do not patch `registration.json` by hand.

---

## Scope boundary

Phase 35 ends here:

- register one external target from a file-backed spec
- inspect immutable identity plus latest environment/smoke artifacts
- persist typed reproducibility and smoke files under
  `data/llm_external_models/{model_id}/`

Deferred work:

- Phase 36 executes comparative benchmark runs against frozen translated packs
- Phase 36 emits fidelity-aware scorecards and recommendation guidance

So this runbook does not cover comparative benchmark execution, scorecard
interpretation, server orchestration, or model download automation yet.
