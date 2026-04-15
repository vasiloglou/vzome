# Progress

## Changelog

| Date | Change | Details |
|------|--------|---------|
| 2026-04-15 | Phase 39 guided tutorial | Added `developers-docs/guided-design-tutorial.md`, linked it from the docs index, and documented the Sc-Zn Zomic-backed design -> evaluate -> visualize path with concrete artifact interpretation and vZome handoff guidance |
| 2026-04-15 | Phase 38 narrative refresh | Refreshed `developers-docs/podcast-deep-dive-source.md` so it describes the shipped workflow through `v1.6`, links to the current runbooks and reference docs, and removes stale command-count, capability, and quantitative claims from the older deep-dive draft |
| 2026-04-07 | Phase 36 Plan 03 comparative benchmark docs and example spec | Added a committed `al_cu_fe_external_benchmark.yaml`, shipped an operator runbook for benchmark execute or inspect plus artifact interpretation, and refreshed the configuration reference, pipeline stages guide, and docs index so the Phase 36 workflow is discoverable beside the Phase 34 and Phase 35 handoff docs |
| 2026-04-07 | Phase 36 Plan 03 comparative benchmark CLI workflow | Added `mdisc llm-external-benchmark` and `mdisc llm-inspect-external-benchmark`, kept the repo-standard exit-code-2 failure posture for missing or invalid benchmark specs and summaries, and locked the new operator surface with focused CLI plus root-help coverage |
| 2026-04-07 | Phase 36 Plan 02 fidelity-aware benchmark scorecards | Tightened `build_external_benchmark_summary(...)` so recommendation lines privilege the periodic-safe exact or anchored slice even when overall shared-slice deltas look better on lossy cases, and added typed benchmark-summary coverage that proves weak periodic-safe performance cannot hide behind diagnostic-only wins |
| 2026-04-07 | Phase 36 Plan 02 comparative benchmark execution core | Added `llm/external_benchmark.py` with spec loading, frozen benchmark-set replay, prompt rendering, response parsing, external-target and internal-control execution, deterministic per-target artifact writing, and focused benchmark-core tests that lock explicit exclusions plus smoke-failure handling without requiring real model weights |
| 2026-04-07 | Phase 36 Plan 01 comparative benchmark storage helpers | Added deterministic `llm_external` benchmark storage helpers in `llm/storage.py` for benchmark-level and per-target artifacts including `benchmark_summary.json`, `scorecard_by_case.jsonl`, `run_manifest.json`, `case_results.jsonl`, and `raw_responses.jsonl`, and locked the new artifact family in focused schema/storage coverage so it stays isolated from benchmark-set and external-target roots |
| 2026-04-07 | Phase 36 Plan 01 comparative benchmark contract | Added typed Phase 36 benchmark-spec, target-variant, case-result, run-manifest, slice-summary, control-delta, and benchmark-summary models to `llm/schema.py`, re-exported the new public surface plus storage helpers from `materials_discovery.llm`, and added focused schema tests that lock the family-aware and fidelity-aware contract before benchmark execution lands |
| 2026-04-07 | Phase 35 Plan 03 external-target docs and example specs | Added committed CIF and material-string external-target example specs, shipped an operator runbook for registration or inspect or smoke plus artifact layout and Phase 36 boundary notes, and refreshed the docs map plus configuration and pipeline references so the new workflow is discoverable beside translated benchmark and checkpoint docs |
| 2026-04-07 | Phase 35 Plan 03 external-target CLI workflow | Added `mdisc llm-register-external-target`, `mdisc llm-inspect-external-target`, and `mdisc llm-smoke-external-target`, wired them to the Phase 35 registry core with repo-standard exit-code-2 failures, and locked the new command surface with focused CLI plus root-help coverage |
| 2026-04-07 | Phase 35 Plan 02 external-target environment and smoke persistence | Added `llm/external_targets.py` with typed registration reload, package-version and platform capture, fail-closed smoke persistence tied to the registration fingerprint, public `materials_discovery.llm` exports for the Phase 35 core, and focused registry tests that validate passed and failed smoke artifacts without requiring real third-party weights |
| 2026-04-07 | Phase 35 Plan 02 external-target registration core | Added `register_external_target(...)`, `load_registered_external_target(...)`, and spec loading plus fingerprint conflict checks for immutable benchmark-target registrations, normalized repo-relative snapshot paths into `registration.json`, and locked the registry behavior with focused tmp-path coverage in `test_llm_external_target_registry.py` |
| 2026-04-07 | Phase 35 Plan 01 external-target storage helpers | Added deterministic `llm_external_models` storage helpers in `llm/storage.py` for the external-target root plus `registration.json`, `environment.json`, and `smoke_check.json`, re-exported the new helpers from `materials_discovery.llm`, and extended the focused schema tests so this artifact family stays isolated from checkpoint directories |
| 2026-04-07 | Phase 35 Plan 01 external-target contract | Added typed external-target registration, environment-manifest, smoke-check, and registration-summary models to `llm/schema.py`, re-exported the new public surface from `materials_discovery.llm`, and kept the new schema slice focused on immutable benchmark-target identity plus reproducibility metadata |
| 2026-04-07 | Phase 34 Plan 03 translated benchmark runbook, example spec, and demo bundles | Added a committed `configs/llm/al_cu_fe_translated_benchmark_freeze.yaml`, shipped two repo-backed Phase 34 demo translation bundles under `data/llm_translation_exports/`, taught the freeze loader to accept YAML specs, and added a dedicated translated-benchmark runbook plus docs-map and pipeline-reference updates that keep Phase 35 runtime registration and Phase 36 scorecards explicitly deferred |
| 2026-04-07 | Phase 34 Plan 03 translated benchmark CLI commands | Added `mdisc llm-translated-benchmark-freeze` and `mdisc llm-translated-benchmark-inspect` to `cli.py`, kept the repo’s exit-code-2 error pattern for missing specs or manifests plus invalid contract requests, and added a human-readable inspect trace for benchmark-set metadata, included rows, excluded rows, and `--show` or `--candidate-id` filtering |
| 2026-04-07 | Phase 34 Plan 03 RED translated benchmark CLI tests | Added failing `test_llm_translated_benchmark_cli.py` coverage for the new freeze and inspect commands, including JSON summary output, clear exit-code-2 failures, human-readable inspect traces with `--show included|excluded|all` plus `--candidate-id`, and top-level CLI help discoverability before wiring the commands into `cli.py` |
| 2026-04-07 | Phase 34 Plan 02 acceptance artifact-name follow-up | Added explicit artifact-name assertions in the freeze persistence tests and a matching module note in `llm/translated_benchmark.py` so the fixed `freeze_contract.json`, `manifest.json`, `included.jsonl`, and `excluded.jsonl` contract remains visible in the code surface while still flowing through the storage helpers |
| 2026-04-07 | Phase 34 Plan 02 persisted freeze artifacts and public exports | Extended `llm/translated_benchmark.py` to write normalized `freeze_contract.json`, `included.jsonl`, `excluded.jsonl`, and `manifest.json` with source bundle lineage plus exclusion-reason tallies, added the tally field to the benchmark-pack manifest schema, re-exported the freeze helpers from `materials_discovery.llm`, and turned the focused persistence suite green |
| 2026-04-07 | Phase 34 Plan 02 RED persisted freeze-artifact tests | Extended `test_llm_translated_benchmark_freeze.py` with failing coverage that requires `freeze_contract.json` and `manifest.json` writes, typed manifest lineage plus exclusion-reason tallies, repeat-run byte stability for all freeze artifacts, and public `materials_discovery.llm` exports for the freeze helpers before the persistence pass lands |
| 2026-04-07 | Phase 34 Plan 02 freeze engine core | Added `llm/translated_benchmark.py` with the first benchmark-pack freeze engine pass: spec loading, shipped bundle inventory loading, explicit system or target-family or fidelity-tier or loss-posture filtering, deterministic duplicate handling, conflicting-payload failure, and included or excluded inventory writing |
| 2026-04-07 | Phase 34 Plan 02 RED freeze-engine tests | Added failing `test_llm_translated_benchmark_freeze.py` coverage that drives the future freeze engine through real shipped translation bundles and locks eligibility filtering, typed exclusions, exact duplicate handling, conflicting-duplicate failure, and deterministic row ordering before `llm/translated_benchmark.py` exists |
| 2026-04-07 | Phase 34 Plan 01 benchmark-pack storage helpers | Added deterministic `llm_external_sets` storage helpers in `llm/storage.py` for the benchmark-pack root plus `freeze_contract.json`, `manifest.json`, `included.jsonl`, and `excluded.jsonl`, keeping this artifact family isolated from translation-export and serving-benchmark roots and turning the focused schema/storage slice green |
| 2026-04-07 | Phase 34 Plan 01 RED benchmark-pack storage tests | Extended `test_llm_translated_benchmark_schema.py` with failing storage-layout coverage for `data/benchmarks/llm_external_sets/{benchmark_set_id}/`, dedicated `freeze_contract.json` and inventory filenames, blank-ID rejection, and proof that the new artifact family stays separate from translation-export and serving-benchmark roots |
| 2026-04-07 | Phase 34 Plan 01 translated benchmark-pack contract | Added typed translated benchmark-set spec, included/excluded row, manifest, and summary models to `llm/schema.py`, re-exported the new public surface from `materials_discovery.llm`, and kept the new benchmark-pack schema slice green against the focused validator tests |
| 2026-04-07 | Phase 34 Plan 01 RED benchmark-pack contract tests | Added failing `test_llm_translated_benchmark_schema.py` coverage that locks the translated benchmark freeze contract shape, typed loss-posture and exclusion vocabularies, included/excluded row lineage, and manifest path/count expectations before implementing the new schema surface |
| 2026-04-07 | Phase 33 Plan 03 translation operator docs and help coverage | Added `developers-docs/llm-translation-runbook.md`, refreshed README and docs entry points for the new translation workflow, updated the pipeline command reference and developer contract note to point operators at the runbook, and locked CLI help discoverability for `llm-translate` plus `llm-translate-inspect` |
| 2026-04-07 | Phase 33 Plan 02 translation export CLI | Added `mdisc llm-translate` and `mdisc llm-translate-inspect`, wired translation bundle creation into standard stage-manifest writing plus campaign-lineage and benchmark-context passthrough, and added operator-readable bundle inspection with clear exit-code-2 failures for missing inputs or manifests |
| 2026-04-06 | Phase 33 Plan 02 RED translation CLI tests | Added failing `test_llm_translation_cli.py` coverage for the new `llm-translate` and `llm-translate-inspect` commands, including stage-manifest writing, campaign-lineage and benchmark-context passthrough, bundle-summary inspection, candidate-level tracing, and clear exit-code-2 failures on missing inputs or manifests |
| 2026-04-06 | Phase 33 Plan 01 translation bundle core | Added translation-bundle schema models, dedicated `data/llm_translation_exports/{export_id}/` storage helpers, a deterministic bundle writer that emits raw payload files plus inline-text inventory rows and bundle manifests for both CIF and CrystalTextLLM-compatible material-string targets, and public `materials_discovery.llm` exports for the new Phase 33 artifact layer |
| 2026-04-06 | Phase 33 Plan 01 RED translation bundle tests | Added failing `test_llm_translation_bundle.py` coverage that locks the new translation-bundle path layout, schema validators, manifest/inventory shape, raw payload file expectations, explicit lossy material-string sidecar semantics, and byte-stable repeated bundle writing before implementing the Phase 33 artifact layer |
| 2026-04-06 | Phase 32 Plan 03 Task 2 parser and malformed-artifact regressions | Extended CIF and shared-export coverage so repo-local `parse_cif()` is explicitly exercised against the checked-in periodic golden and the stripped lossy payload, while malformed periodic artifacts fail through `emit_translated_structure(...)` and legitimate lossy exports continue to serialize |
| 2026-04-06 | Phase 32 Plan 03 Task 1 checked-in exporter goldens | Added four repo-backed expected-output files that freeze the shipped CIF preamble contract and the bare CrystalTextLLM-compatible material-string body for the exact Al-Cu-Fe and lossy Sc-Zn boundary fixtures |
| 2026-04-06 | Phase 32 Plan 03 Task 1 RED golden regression tests | Added failing `test_llm_translation_export_fixtures.py` coverage that requires four checked-in golden exporter outputs, exact byte matches for both boundary candidates across CIF and material-string targets, and explicit lossy periodic-proxy semantics without reintroducing repo-only metadata into the raw CrystalTextLLM-compatible body |
| 2026-04-06 | Phase 32 Plan 02 Task 2 cross-target dispatch | Finished `emit_translated_structure(...)` for both built-in target families so CIF and CrystalTextLLM-compatible material-string payloads now share the same validation gate, copy-not-mutate artifact return shape, preserved provenance/fidelity/loss metadata, and explicit unsupported-family failure |
| 2026-04-06 | Phase 32 Plan 02 Task 2 RED cross-target dispatch tests | Replaced the temporary `material_string` NotImplemented expectation with failing dispatch coverage that requires byte-stable emission for both target families, preserved artifact identity across CIF and material-string exports, parseable dispatched material-string output, and a clear unsupported-family failure path |
| 2026-04-06 | Phase 32 Plan 02 Task 1 CrystalTextLLM material-string emitter | Added `emit_material_string_text(...)` and public `materials_discovery.llm` exports for the first concrete material-string target, keeping the emitted body parser-compatible with CrystalTextLLM lengths/angles/species/coordinate lines while preserving provenance and loss metadata on the translated artifact itself |
| 2026-04-06 | Phase 32 Plan 02 Task 1 RED CrystalTextLLM material-string tests | Added failing `test_llm_translation_material_string.py` coverage for a real CrystalTextLLM-compatible body layout, parser-style line decoding, preserved site order, explicit loss metadata staying on the artifact contract, and byte-stable repeated emission before implementing the first material-string exporter |
| 2026-04-06 | Phase 32 Plan 01 Task 2 CIF site-order test fix | Corrected the new CIF site-order assertion to ignore the `loop_` control line after the first green run showed the serializer was preserving site order and the test was counting the CIF loop marker as data |
| 2026-04-06 | Phase 32 Plan 01 Task 2 deterministic CIF serializer | Tightened `emit_cif_text(...)` to emit the fixed CIF comment preamble with source and fidelity metadata while preserving the shared scalar formatting, fixed cell-field order, parser-compatible atom loop, and explicit lossy periodic-proxy labeling |
| 2026-04-06 | Phase 32 Plan 01 Task 2 RED CIF serializer tests | Added failing `test_llm_translation_cif.py` coverage for the deterministic CIF comment preamble, fixed scalar and loop-header order, parser compatibility after comment stripping, preserved site order, and explicit lossy periodic-proxy metadata before tightening the serializer |
| 2026-04-06 | Phase 32 Plan 01 Task 1 shared export seam | Added `llm/translation_export.py` with deterministic export validation, a shared six-decimal float formatter, copy-not-mutate dispatch, a narrow pure-text CIF emitter, and public `llm` exports for the new Phase 32 seam |
| 2026-04-06 | Phase 32 Plan 01 Task 1 RED export-seam tests | Added failing `test_llm_translation_export.py` coverage for shared export validation, deterministic dispatch, copy-not-mutate behavior, and the explicit `material_string` not-yet-implemented boundary before adding the new exporter module |
| 2026-04-06 | Phase 31 Plan 03 Task 2 developer translation contract note | Added `developers-docs/llm-translation-contract.md` as an implementation-facing handoff for Phase 32, documented the source-of-truth boundary, the built-in target registry, all four fidelity states, and why the exact/lossy fixture pair anchors the exporter boundary while `approximate` remains covered in core tests |
| 2026-04-06 | Phase 31 Plan 03 Task 1 translation fixtures | Added repo-backed Al-Cu-Fe periodic-safe and Sc-Zn QC-native candidate fixtures under `tests/fixtures/llm_translation/`, made the new regression suite green across both built-in translation targets, and kept the contract anchored on explicit fixture data-shape differences rather than prose alone |
| 2026-04-06 | Phase 31 Plan 03 Task 1 RED fixture regression tests | Added failing `test_llm_translation_fixtures.py` coverage that loads repo-backed periodic-safe and QC-native candidate fixtures, locks exact versus lossy expectations for both built-in translation targets, and proves the new regression suite is file-based rather than inline-only |
| 2026-04-06 | Phase 31 Plan 02 Task 2 translation fidelity classification | Implemented conservative translation-fidelity assessment in `llm/translation.py`, made mixed-origin candidates top out at `approximate`, required explicit lossy reasons for QC-native periodic exports, and kept the focused translation/realization slice green at 10 passing tests |
| 2026-04-06 | Phase 31 Plan 02 Task 2 RED fidelity tests | Added failing translation-core coverage for conservative exact/anchored/approximate/lossy classification, explicit lossy reasons for QC-native periodic exports, and a clear unsupported-exactness failure path before implementing fidelity assessment |
| 2026-04-06 | Phase 31 Plan 02 Task 1 translation normalization seam | Added `llm/translation.py` with deterministic normalized-artifact construction, exported translation-core helpers, introduced an explicit per-site coordinate-origin helper in structure realization, and kept the focused translation/realization slice green at 7 passing tests |
| 2026-04-06 | Phase 31 Plan 02 Task 1 RED normalization tests | Added failing translation-core coverage for deterministic normalized artifacts, explicit coordinate-source reporting, and byte-stable output expectations, plus a structure-realization regression that locks per-site origin reporting before implementing the normalization seam |
| 2026-04-06 | Phase 31 Plan 01 Task 2 translation target registry | Added the built-in CIF and CrystalTextLLM-style material-string target registry, exported explicit `list_translation_targets()` and `resolve_translation_target(...)` APIs, surfaced periodic-cell and QC-semantics flags on descriptors, and kept the schema slice green at 10 passing tests |
| 2026-04-06 | Phase 31 Plan 01 Task 2 RED target-registry tests | Added failing registry coverage for explicit CIF and material-string target discovery, stable target resolution, periodic-cell requirement flags, and clear unknown-family failures before implementing the built-in registry |
| 2026-04-06 | Phase 31 Plan 01 Task 1 translation artifact contract | Added the additive translated-structure schema models, a separate export-facing fidelity tier with `lossy`, typed source linkage and diagnostics, public imports for the new contract, and green schema coverage including missing-source-linkage rejection |
| 2026-04-06 | Phase 31 Plan 01 Task 1 RED translation schema tests | Added failing schema coverage for translated-structure source linkage, export fidelity separation, lossy-reason validation, and diagnostic-only artifacts before implementing the additive translation contract |
| 2026-04-05 | Phase 30 Task 3 lifecycle operator docs and help coverage | Documented the candidate benchmark, promotion, rollback, and retirement workflow with the committed lifecycle configs/specs, clarified serving-benchmark role semantics in the developer docs, and expanded CLI help coverage for the lifecycle command surface |
| 2026-04-05 | Phase 30 Task 2 committed lifecycle benchmark proof | Added committed candidate and lifecycle benchmark example configs, proved the promoted-vs-candidate-vs-baseline benchmark workflow offline, and validated that benchmark summaries can recommend checkpoint promotion while keeping rollback explicit |
| 2026-04-05 | Phase 30 Task 1 lifecycle benchmark roles and recommendations | Added typed lifecycle benchmark target roles, taught benchmark summaries to recommend promote/keep/rollback from structured target intent, and expanded serving-benchmark schema/core coverage around lifecycle benchmark semantics |
| 2026-04-05 | Phase 29 Task 3 promoted-default config and workflow proof | Switched the committed adapted Al-Cu-Fe lane to promoted-family default resolution, added an explicit pinned companion config, documented replay-safe promotion semantics and rollback guidance, and extended the real-mode proof to exercise the promoted-default benchmark path |
| 2026-04-05 | Phase 29 Task 2 replay-safe promotion drift handling | Kept replay pinned to the recorded family checkpoint after later promotions change, surfaced checkpoint selection metadata in compare and serving-benchmark summaries, and added focused replay/output coverage for promotion-aware lifecycle identity |
| 2026-04-05 | Phase 29 Task 1 promoted-family runtime resolution | Added promoted-default checkpoint-family resolution for new execution, recorded lifecycle selection metadata on serving identity, updated manual and campaign launch paths to reuse that resolver, and locked the first promotion-aware workflow regressions in checkpoint, launch, and generate tests |
| 2026-04-05 | Phase 28 Task 6 lifecycle contract docs and phase boundary | Documented `checkpoint_family`, hybrid lifecycle state, lifecycle CLI JSON/action semantics, replay-safe retirement, demotion-by-promotion, and the explicit Phase 29 boundary for promoted-default execution plus workflow-integrated RUNBOOK guidance |
| 2026-04-05 | Phase 28 Task 5 lifecycle example specs and replay-proof retirement | Added committed promotion/retirement action examples, proved retired checkpoints remain replay-safe by fingerprint, and kept the lifecycle CLI fixtures operational with placeholder evidence paths |
| 2026-04-05 | Phase 28 Task 4 checkpoint lifecycle CLI surface | Added `llm-list-checkpoints`, `llm-promote-checkpoint`, and `llm-retire-checkpoint` with structured JSON, clear stale-write remediation, and repo-level CLI coverage for lifecycle command discovery |
| 2026-04-05 | Phase 28 Task 3 checkpoint lifecycle registry actions | Added family lifecycle loading, auto-enrollment, promotion/retirement mutation guards, and focused registry coverage for stale-write protection plus replay-safe retirement history |
| 2026-04-05 | Phase 28 Task 2 checkpoint lifecycle storage helpers | Added deterministic checkpoint-family lifecycle paths under `data/llm_checkpoints/families/`, revision-based promotion/retirement artifact naming, and focused registry storage coverage without changing legacy registration paths |
| 2026-04-05 | Phase 28 Task 1 checkpoint lifecycle schema contract | Added the additive `checkpoint_family` lane selector, shipped the lifecycle/promotion/retirement/pin-selection schema contract, and locked the Wave 1 schema surface in focused LLM checkpoint tests |
| 2026-04-05 | Phase 27 adapted checkpoint operator workflow docs | Documented `mdisc llm-register-checkpoint`, adapted-lane registration rules, the committed adapted Al-Cu-Fe config and benchmark spec, rollback guidance, and replay-safe checkpoint drift behavior across `RUNBOOK.md`, `configuration-reference.md`, `llm-integration.md`, and `pipeline-stages.md` |
| 2026-04-05 | Phase 26 adapted checkpoint workflow integration | Added file-backed checkpoint resolution to serving identity, hardened replay against checkpoint fingerprint drift, added the committed adapted Al-Cu-Fe system and benchmark configs, and proved the offline adapted-vs-baseline benchmark path in `test_real_mode_pipeline.py` |
| 2026-04-05 | Phase 25 checkpoint registration and lineage contracts | Added typed checkpoint registration models, storage helpers, `llm/checkpoints.py`, the `mdisc llm-register-checkpoint` CLI, and focused registry/CLI coverage for auditable adapted-checkpoint lineage |
| 2026-04-05 | Phase 21 Plan 03 serving benchmark operator docs | Added the serving-benchmark workflow to the runbook and developer docs, documented benchmark-spec fields plus strict smoke/no-silent-fallback behavior, added shared CLI coverage for missing benchmark specs, and kept the Wave 3 docs/CLI slice green at `31 passed` |
| 2026-04-05 | Phase 21 Plan 03 committed benchmark examples | Added the hosted Al-Cu-Fe LLM config plus committed Al-Cu-Fe and Sc-Zn serving-benchmark specs, kept the specialized target evaluation-primary with an aligned `top1` slice, and re-verified the shared CLI/real-mode benchmark slice at `16 passed` |
| 2026-04-05 | Phase 21 Plan 03 Task 1 RED benchmark example-config tests | Added failing `test_real_mode_pipeline.py` coverage that locks the committed hosted config plus Al-Cu-Fe and Sc-Zn serving-benchmark example specs before adding the operator-facing benchmark files |
| 2026-04-05 | Phase 21 Plan 02 serving benchmark execution proof | Reused the shipped launch and evaluation flows inside `llm-serving-benchmark`, recorded standard launch/comparison and evaluation summary artifacts per target, rejected misaligned evaluation batches before execution, and kept the combined Wave 2 verification green at `15 passed` |
| 2026-04-05 | Phase 21 Plan 02 Task 2 RED benchmark integration proof | Added failing offline `test_real_mode_pipeline.py` coverage for one shared-context serving benchmark spanning hosted launch, local launch, and specialized evaluation targets while preserving on-disk campaign specs |
| 2026-04-05 | Phase 21 Plan 02 benchmark CLI and strict smoke orchestration | Added the `llm-serving-benchmark` CLI command, wrote typed smoke artifacts before benchmark continuation, enforced exit code 2 on strict smoke failures, and supported summary-path overrides for operator benchmarks |
| 2026-04-05 | Phase 21 Plan 02 Task 1 RED benchmark CLI tests | Added failing `test_llm_serving_benchmark_cli.py` coverage for smoke-only output, strict smoke failure exit code 2, recommendation printing, and `--out` summary override behavior |
| 2026-04-05 | Phase 21 Plan 01 serving benchmark smoke and summary helpers | Added offline serving-benchmark core helpers that reuse lane resolution and readiness probes, surface explicit no-fallback smoke failures, and build per-target summaries with fastest/cheapest/lowest-friction recommendations |
| 2026-04-05 | Phase 21 Plan 01 Task 2 RED benchmark-core tests | Added failing `test_llm_serving_benchmark_core.py` coverage for offline launch and evaluation smoke checks, explicit no-fallback failures, and summary recommendations that keep missing metrics explicit |
| 2026-04-05 | Phase 21 Plan 01 serving benchmark schema and loader contract | Added typed serving-benchmark models, benchmark storage helpers under `data/benchmarks/llm_serving/`, and a shared-context `load_serving_benchmark_spec(...)` loader that rejects mixed-system benchmark targets before execution |
| 2026-04-05 | Phase 21 Plan 01 Task 1 RED benchmark schema tests | Added failing `test_llm_serving_benchmark_schema.py` coverage for the shared-context benchmark contract, mixed-system loader rejection, nested serving identity serialization, and new benchmark storage paths before implementing the Phase 21 schema/core layer |
| 2026-04-05 | Phase 20 full-suite projection metadata normalization | Rounded `projection2zomic` composition metadata deterministically so the inherited PyQCstrc projection regression stays exact-value stable under the expanded full-suite run |
| 2026-04-05 | Phase 20 Plan 03 Sc-Zn compatibility proof and specialized-lane docs | Added `llm_evaluate` specialized-lane config to `sc_zn_llm_local.yaml`, proved offline `Sc-Zn` launch/replay/compare compatibility with injected specialized evaluation lineage, documented `llm_evaluate.model_lane` plus a concrete OpenAI-compatible specialist endpoint recipe, and kept the Wave 3 real-mode/CLI regressions green |
| 2026-04-05 | Phase 20 Plan 02 specialized evaluation workflow compatibility | Added `llm-evaluate --model-lane`, turned `al_cu_fe_llm_local.yaml` into the real specialized evaluation proof config, propagated additive evaluation-lane lineage into campaign outcome snapshots and compare output, and kept focused Wave 2 regressions green at `4 passed` plus `32 passed` |
| 2026-04-05 | Phase 20 Plan 01 specialized evaluation lane foundation | Added additive `llm_evaluate.model_lane` support, typed evaluation serving identity on assessments and run manifests, a new `llm/specialist.py` payload seam, lane-aware `llm-evaluate` core reuse of shared serving resolution, and focused schema coverage that passed at `5 passed` |
| 2026-04-05 | Phase 19 Plan 01 local-serving schema and runtime foundation | Added additive local-serving backend and lane config fields, typed `LlmServingIdentity` support for run/launch artifacts, an `openai_compat_v1` runtime adapter with readiness probes, and focused schema/runtime regressions that passed at `20 passed` |
| 2026-04-05 | Phase 19 Plan 02 lane-aware local serving integration | Added shared serving-lane resolution for manual generation and campaign launch, threaded additive serving identity into run and launch artifacts, added `llm-generate --model-lane` plus local-serving preflight diagnostics, and kept focused generate/launch CLI regressions green at `40 passed` |
| 2026-04-05 | Phase 19 Plan 03 replay-safe local serving docs and configs | Added replay-safe handling for richer local serving identity, committed local OpenAI-compatible example configs for Al-Cu-Fe and Sc-Zn, documented the Phase 19 serving contract, and kept focused replay/runtime/CLI regressions green at `38 passed` |
| 2026-04-04 | Phase 12 Plan 03 replay and compare workflow closeout | Added an offline full closed-loop regression for `llm-suggest -> llm-approve -> llm-launch -> llm-replay -> llm-compare`, extended campaign-lineage tests for replay fields, documented the strict replay/compare operator flow, and re-verified the full suite at 374 passed, 3 skipped |
| 2026-04-04 | Phase 12 Plan 02 replay and compare CLI | Added strict `mdisc llm-replay --launch-summary ...`, `mdisc llm-compare --launch-summary ...`, replay-aware `llm-generate` lineage, and focused replay/compare CLI coverage while keeping the shared CLI suite green |
| 2026-04-04 | Phase 12 Plan 01 replay and comparison foundation | Added strict replay bundle loading, replay-config reconstruction helpers, typed outcome/comparison artifacts, deterministic campaign comparison paths, and focused replay/compare core regression coverage |
| 2026-04-04 | Phase 11 Plan 03 launch continuation docs | Documented `mdisc llm-launch`, launch wrapper artifacts, manual downstream continuation, failure posture, and a lineage-audit path in the LLM and pipeline developer docs |
| 2026-04-04 | Phase 11 Plan 03 campaign lineage propagation | Threaded additive `llm_campaign` lineage into launched `llm_generate` manifests, downstream stage manifests, and pipeline manifests, with focused downstream-lineage and mock continuation regression coverage |
| 2026-04-04 | Phase 11 Plan 03 RED tests | Added failing downstream-lineage and mock end-to-end launch regressions in `test_llm_campaign_lineage.py`, `test_report.py`, and `test_real_mode_pipeline.py` before wiring campaign lineage through later pipeline stages |
| 2026-04-04 | Phase 11 Plan 02 Task 2 llm-launch CLI | Added the new `mdisc llm-launch --campaign-spec ...` command, wrote resolved/summary launch artifacts, validated config-hash drift before runtime execution, and preserved partial-failure auditability |
| 2026-04-04 | Phase 11 Plan 02 Task 2 RED tests | Added `tests/test_llm_launch_cli.py` and a shared `test_cli.py` smoke case to lock `llm-launch` success and config-drift failure behavior before wiring the CLI |
| 2026-04-04 | Phase 11 Plan 02 Task 1 campaign-aware llm-generate | Added prompt instruction deltas and campaign launch metadata to the LLM generation request/run-manifest flow while keeping manual `llm-generate` behavior unchanged |
| 2026-04-04 | Phase 11 Plan 02 Task 1 RED tests | Extended `tests/test_llm_generate_core.py` to lock prompt instruction deltas and campaign-aware run/provenance metadata before modifying `llm-generate` |
| 2026-04-04 | Phase 11 Plan 01 Task 2 launch resolution | Added `llm/launch.py` with deterministic lane selection, prompt/composition overlays, eval-set seed materialization, and exported campaign launch helpers |
| 2026-04-04 | Phase 11 Plan 01 Task 2 RED tests | Added `tests/test_llm_launch_core.py` to lock deterministic lane, prompt, composition, and seed resolution behavior before implementing `llm/launch.py` |
| 2026-04-04 | Phase 11 Plan 01 Task 1 launch contracts | Added lane-aware `llm_generate.model_lanes`, typed launch summary models, and deterministic campaign launch storage helpers |
| 2026-04-04 | Phase 11 Plan 01 Task 1 RED tests | Added `tests/test_llm_launch_schema.py` to lock lane-aware config validation, launch summary contracts, and campaign launch storage paths before implementation |
| 2026-03-22 | Initial Progress.md created | Tracking document for experiments and actions |
| 2026-03-22 | Added Ti-Zr-Ni system | New ternary icosahedral quasicrystal target; element priors, pair enthalpies, mock config, template path, execution plan updated |
| 2026-03-23 | Added LLM-quasicrystal landscape doc | New developer doc covering how LLMs and AI models interact with quasicrystals: challenges, workflows, MLIP simulation, diffusion models, TSAI, and LLM-QC analogy |
| 2026-03-23 | Ran ingest for Ti-Zr-Ni | 3 reference phases ingested (i-phase, approximant, C14-Laves); QA passed; fixture updated with Ti-Zr-Ni rows |
| 2026-03-23 | Executed Ti-Zr-Ni export-zomic | Zomic design compiled to orbit library: 22 sites (10 icosa, 8 shell, 4 bridge) across 3 orbits |
| 2026-04-02 | Moved materials discovery docs into workspace | Relocated `developer-docs/materials_discovery` to `materials-discovery/developers-docs` and updated links/references |
| 2026-04-03 | Added source staging runtime foundation | Created `materials_discovery.data_sources` core modules, source manifest/QA models, storage/runtime helpers, and ingestion optional dependencies for Phase 2 |
| 2026-04-03 | Added additive ingestion config seam | Extended `SystemConfig` with `ingestion`, reserved the `source_registry_v1` bridge adapter key, and kept the current ingest path unchanged |
| 2026-04-03 | Added source runtime contract tests | Introduced focused pytest coverage for canonical raw-source schema validation, source adapter registry behavior, and QA aggregation edge cases |
| 2026-04-03 | Hardened native provider optional-dependency test | Relaxed the MD-provider missing-dependency assertion so the full suite stays valid whether `ase` or an ASE-compatible calculator is the first unavailable optional component |
| 2026-04-03 | Refreshed ingestion dependency lockfile | Updated `uv.lock` so the new `ingestion` extra resolves `httpx` and its transitive dependencies alongside the existing workspace extras |
| 2026-04-03 | Added HYPOD-X and COD source adapters | Implemented the first offline provider adapters on the new source runtime, including HYPOD-X fixture/pinned staging, CIF conversion, COD staging, and deterministic adapter tests |
| 2026-04-03 | Added API and OPTIMADE source adapters | Implemented shared OPTIMADE normalization plus offline Materials Project, OQMD, and JARVIS adapters, with compatibility tests proving legacy CLI configs still work without `ingestion` |
| 2026-04-03 | Added canonical source projection bridge core | Implemented `data_sources/projection.py`, deterministic system/phase/dedupe rules, a reusable `ProjectionSummary`, and focused tests proving projected rows remain consumable by downstream reference-phase logic |
| 2026-04-03 | Wired source-registry ingest into the CLI | Turned `source_registry_v1` into a real `mdisc ingest` path with staged snapshot reuse, additive ingest-manifest lineage, and offline bridge/CLI regression coverage |
| 2026-04-03 | Added source-backed pipeline compatibility coverage | Extended real-mode, hull, and report regressions for the new bridge, added an explicit no-DFT ingest guard, and hardened `active_learn` test setup against stale validated artifacts |
| 2026-04-03 | Phase 4: reference-pack assembly layer | Added `ReferencePackConfig`/`ReferencePackMemberConfig` schema models to `common/schema.py`, `ReferencePackManifest`/`ReferencePackMemberResult` to `data_sources/schema.py`, pack storage helpers to `storage.py`, and the full `data_sources/reference_packs.py` assembly module with deduplication, priority ordering, caching, and deterministic fingerprinting; covered by `tests/test_reference_packs.py` (15 tests) |
| 2026-04-03 | Phase 4: benchmark-ready reference-aware configs for Al-Cu-Fe and Sc-Zn | Added `al_cu_fe_reference_aware.yaml` and `sc_zn_reference_aware.yaml` with `source_registry_v1`, multi-source `reference_pack` blocks (HYPOD-X + MP for Al-Cu-Fe; HYPOD-X + COD for Sc-Zn), explicit priority ordering, benchmark corpus/validation snapshot hooks; staged thin second-source canonical fixtures; extended CLI to route `source_registry_v1` + `reference_pack` through `_ingest_via_reference_pack`; 31 deterministic benchmark/fixture tests |
| 2026-04-03 | Phase 4 Plan 02: comparable benchmark outputs across pipeline lanes | Added `BenchmarkRunContext` and `build_benchmark_run_context()` to `common/benchmarking.py`; `write_benchmark_pack()` emits a dedicated `benchmark_pack.json` artifact; additive `benchmark_context` field added to `ArtifactManifest`; `hifi-rank` and `report` CLI commands thread context into manifests and ranked/report outputs; `rank_validated_candidates()` embeds `calibration_provenance` and optional `benchmark_context` in candidate provenance; `compile_experiment_report()` surfaces context in evidence blocks and top-level report; 164 tests pass |

| 2026-04-03 | Phase 5 Plan 01: data lake metadata layer | Added `lake` package with `catalog.py` (CatalogEntry, DirectoryCatalog, ARTIFACT_DIRECTORIES with 17 entries, build_directory_catalog, write_catalog), `staleness.py` (hash-based + mtime-hint staleness detection), and `index.py` (LakeIndex, build_lake_index, write_lake_index, lake_stats); wired `mdisc lake index` and `mdisc lake stats` CLI subcommands; 15 new tests pass, 187 total |
| 2026-04-03 | Phase 5 Plan 02: cross-lane comparison engine | Added `lake/compare.py` with lane-centric model (LaneSnapshot, MetricDistribution, GateDelta, MetricDelta, ComparisonResult); dereferences benchmark-pack report paths to compute metric distributions (mean/min/max/std for 8 key metrics); wired `mdisc lake compare` CLI command with dual-format output (JSON + table); graceful fallback for missing report files; 10 new tests, 197 total |
| 2026-04-03 | Phase 5 Plan 03 Task 1: analytics notebooks and smoke tests | Three starter notebooks (source_contribution_analysis, cross_run_drift_detection, metric_distribution_deep_dive) under `notebooks/`; each uses workspace_root() and degrades gracefully when data is absent; `tests/test_notebooks.py` with 3 static + 3 conditional execution smoke tests |
| 2026-04-03 | Phase 5 Plan 03 Task 2: unified operator RUNBOOK.md | 8-section runbook covering prerequisites, ingestion, reference-pack assembly, pipeline execution, benchmarking, data lake operations, analytics notebooks, and troubleshooting; 53+ code blocks; full mdisc command quick-reference table |
| 2026-04-03 | Phase 5 complete: data lake and analysis layer | All 3 plans executed across 3 waves; verification passed 15/15 must-haves; 200 tests passing; all 6 cross-AI review concerns addressed; PIPE-04 and PIPE-05 satisfied |
| 2026-04-03 | Phase 6 Plan 01 Task 1: LLM corpus contracts and config | Added the new `materials_discovery.llm` schema package, committed `configs/llm/corpus_v1.yaml`, and introduced schema-focused pytest coverage for corpus config, provenance, inventory rows, validation state, and build summaries |
| 2026-04-03 | Phase 6 Plan 01 Task 2: LLM corpus storage and manifest helpers | Added deterministic `data/llm_corpus/{build_id}` path helpers, corpus fingerprint/manifest builders, and focused pytest coverage for workspace-relative manifest paths and persisted manifest JSON |
| 2026-04-03 | Phase 6 Plan 02 Task 1: LLM corpus inventory layer | Added offline inventory collectors for repo Zomic scripts, candidate JSONL records, generated raw exports, canonical source/reference-pack records, and a committed PyQCstrc projection fixture, with deterministic sorting and focused pytest coverage |
| 2026-04-03 | Phase 6 Plan 02 Task 2: LLM corpus QA grading and dedupe | Added typed gold/silver/reject grading, deterministic duplicate resolution, QA summaries, and focused pytest coverage for release-tier promotion, label validation, and issue tallies |
| 2026-04-03 | Phase 6 Plan 03 Task 1: deterministic record2zomic conversion | Added the shared axis-walk decomposition helper, deterministic `CandidateRecord -> Zomic` serialization with conversion traces, and focused pytest coverage for ordering, label preservation, and duplicate-label disambiguation |
| 2026-04-03 | Phase 6 Plan 03 Task 2: compile helper and projection2zomic | Added a bridge-backed temporary compile helper, a PyQCstrc projection payload conversion path, and focused pytest coverage for compile success/failure reporting and deterministic cell scaling |
| 2026-04-03 | Phase 6 Plan 04 Task 1: CIF/open approximant conversion | Added CIF-driven corpus conversion for COD and HYPOD-X-style fixtures, plus canonical-record fallback handling and focused pytest coverage that stays green with the existing prototype/COD tests |
| 2026-04-03 | Phase 6 Plan 04 Task 2: native and generated source loaders | Added explicit loaders for repo-native `.zomic` files and generated raw export artifacts, with exact vs anchored fidelity handling and focused pytest coverage for loader-hint alignment |
| 2026-04-03 | Phase 6 Plan 04 Task 3: end-to-end corpus builder | Added the inventory-driven corpus builder that routes all loader hints, validates/grades/dedupes examples, and writes syntax/materials/rejects/inventory/QA/manifest artifacts under `data/llm_corpus/{build_id}` |
| 2026-04-03 | Phase 6 Plan 04 Task 4: llm-corpus CLI command | Added the `mdisc llm-corpus build` sub-application/command, JSON summary output, and focused CLI tests for success, invalid configs, and workspace-relative config paths |
| 2026-04-03 | Phase 7 Plan 01: llm-generate contracts and runtime seam | Added additive `llm_generate` config/schema contracts, Phase 7 runtime request/attempt/run-manifest models, the `llm_fixture_v1` / `anthropic_api_v1` adapter seam, configuration docs, and focused schema/runtime pytest coverage |
| 2026-04-03 | Phase 7 Plan 02: llm-generate core path | Added config-driven prompt assembly, bounded retry generation, compile-backed candidate conversion, the `mdisc llm-generate` CLI command, committed mock configs, and focused core/CLI pytest coverage |
| 2026-04-03 | Phase 7 Plan 03: llm benchmark and docs layer | Added the offline deterministic-vs-LLM comparison helper, benchmark runner script, docs refresh, pytest marker, and two-system benchmark regression coverage for Al-Cu-Fe and Sc-Zn |
| 2026-04-03 | Phase 8 Plan 01: llm-evaluate contracts and CLI path | Added additive `llm_evaluate` config/summary contracts, typed evaluation request/assessment/run-manifest models, the `llm/evaluate.py` engine, the `mdisc llm-evaluate` CLI command, and focused schema/CLI pytest coverage |
| 2026-04-03 | Phase 8 Plan 02: report and rank LLM-assessment integration | Taught `report` to prefer `*_all_llm_evaluated.jsonl`, surfaced additive `llm_assessment` context in report entries/calibration, and added regressions proving `hifi-rank` preserves but does not reweight that context |
| 2026-04-03 | Phase 8 Plan 03: downstream LLM pipeline benchmarks | Added the downstream deterministic-vs-LLM benchmark helper, the `run_llm_pipeline_benchmarks.sh` operator script, refreshed LLM docs, and added offline Al-Cu-Fe/Sc-Zn benchmark regression coverage |
| 2026-04-03 | Phase 9 Plan 01: eval-set and acceptance-pack contracts | Added typed eval-set and acceptance-pack models, new storage/helpers for exporting eval sets from the Phase 6 corpus, and focused acceptance-schema pytest coverage |
| 2026-04-03 | Phase 9 Plan 02: conditioned llm-generate prompts | Added optional eval-set-backed example conditioning for `llm-generate`, prompt/run-manifest lineage for selected examples, and focused core/CLI regressions proving the path remains optional |
| 2026-04-03 | Phase 9 Plan 03: acceptance benchmark and llm-suggest | Added the operator acceptance benchmark script, the dry-run `mdisc llm-suggest` command, refreshed LLM docs, and closed the full suite at 297 passed |
| 2026-04-04 | Phase 10 Plan 01 Task 1 RED: campaign schema tests | Added failing pytest coverage for typed campaign proposals, action-family payload validation, separate approvals, and campaign-spec lineage before implementing the new governance contract |
| 2026-04-04 | Phase 10 Plan 01 Task 1 GREEN: campaign governance schema | Added the additive Phase 10 proposal, approval, launch-baseline, lineage, and campaign-spec models in `llm/schema.py`, exported them from `llm/__init__.py`, and aligned them with the new focused schema tests |
| 2026-04-04 | Phase 10 Plan 01 Task 2 RED: campaign storage tests | Added failing pytest coverage for deterministic suggestion, proposal, approval, and campaign-spec artifact paths plus blank-ID rejection before implementing the new storage helpers |
| 2026-04-04 | Phase 10 Plan 01 Task 2 GREEN: campaign storage helpers | Added deterministic acceptance-pack and campaign artifact path helpers in `llm/storage.py`, exported them from `llm/__init__.py`, and made blank artifact IDs fail fast instead of producing malformed paths |
| 2026-04-04 | Phase 10 Plan 02 Task 1 RED: typed llm-suggest core tests | Added failing pytest coverage for acceptance-pack to typed campaign-proposal mapping, deterministic action IDs, release-gate handling, and proposal-summary path emission before migrating `llm-suggest` off the legacy suggestion model |
| 2026-04-04 | Phase 10 Plan 02 Task 1 GREEN: typed proposal mapping and writer | Added `llm/campaigns.py`, migrated `llm-suggest` to typed campaign suggestions plus per-proposal artifact writing, exported the new helpers, and updated the acceptance-benchmark caller to the new contract |
| 2026-04-04 | Phase 10 Plan 02 Task 2 RED: llm-suggest CLI bundle tests | Added failing CLI coverage for typed stdout, default `suggestions.json`, per-system `proposals/` writing, invalid-input exit handling, and the shared `test_cli.py` migration to the new bundle contract |
| 2026-04-04 | Phase 10 Plan 02 Task 2 GREEN: llm-suggest typed CLI contract | Updated `mdisc llm-suggest` to write the typed suggestion bundle plus proposal artifacts through `suggest.py`, print the persisted typed JSON contract, and pass the focused CLI regression slice |
| 2026-04-04 | Phase 10 Plan 03: campaign approval and spec materialization | Added deterministic approval/spec helpers, acceptance-pack-root artifact-root derivation, and focused pytest coverage for approved, rejected, and re-approval campaign flows |
| 2026-04-04 | Phase 10 Plan 03: llm-approve CLI governance boundary | Added the non-launching `mdisc llm-approve` command, refreshed LLM developer docs, updated shared CLI coverage, and closed the full `materials-discovery` suite at 332 passed, 3 skipped |

## Diary

### 2026-04-15

- 00:11 EDT — Refreshed the long-form narrative in `developers-docs/podcast-deep-dive-source.md` for Phase 38.
- Reframed the stale seven-stage and four-layer story around the shipped `v1.6` workflow families, added cross-links to the current runbooks and reference docs, softened or removed volatile repo-state counts, and made explicit that no new workflow capability was added.
- 00:21 EDT — Added the Phase 39 guided tutorial and wired it into the docs index.
- Documented the locked Sc-Zn Zomic-backed path from `export-zomic` through `report`, added artifact interpretation notes for the current screening, validation, and report snapshots, and made the `.zomic` -> raw export -> orbit-library -> candidate geometry authority chain explicit for vZome iteration.

### 2026-04-07

- 04:23 EDT — Finished the Phase 36 Plan 03 docs and example-spec slice for comparative benchmarks.
- Added a committed `al_cu_fe_external_benchmark.yaml`, shipped a dedicated external-benchmark runbook that covers execute or inspect plus scorecard interpretation and the `data/benchmarks/llm_external/{benchmark_id}/` artifact family, and refreshed the configuration reference, pipeline stages guide, and docs index so the Phase 36 workflow is discoverable without reading code first.
- 04:20 EDT — Implemented the Phase 36 Plan 03 comparative benchmark CLI workflow and inspect surface.
- Added `llm-external-benchmark` and `llm-inspect-external-benchmark` to `cli.py`, kept the repo-standard exit-code-2 behavior for missing or invalid benchmark artifacts, and locked the new run or inspect or root-help surface with focused CLI coverage over typed benchmark summaries.
- 04:13 EDT — Implemented the Phase 36 Plan 02 comparative benchmark execution core in `llm/external_benchmark.py`.
- Added spec loading for frozen translated benchmark manifests, prompt-contract and parser registries, explicit per-case exclusion handling, external-target registration and smoke reuse, internal-control serving-identity resolution, and deterministic writing of benchmark summary plus per-target run manifests and raw-response or case-result artifacts.
- 04:13 EDT — Tightened the Phase 36 Plan 02 scorecard layer so recommendations stay periodic-safe-first.
- Added typed `build_external_benchmark_summary(...)` coverage proving that strong lossy-slice deltas cannot overrule weak exact or anchored performance, while keeping shared eligible control deltas visible in the typed summary for later inspect surfaces.
- 03:51 EDT — Implemented the Phase 36 Plan 01 comparative benchmark contract in `llm/schema.py` and exported it from `materials_discovery.llm`.
- Added typed benchmark specs with explicit external-target and internal-control variants, case-result and run-manifest models that preserve translated-benchmark lineage plus fidelity metadata, and scorecard contracts for overall slices, family or fidelity slices, shared eligible control deltas, and recommendation lines; the new schema slice stays additive to the Phase 34 benchmark-set and Phase 35 external-target artifacts.
- 03:51 EDT — Added the Phase 36 Plan 01 `llm_external` benchmark storage helpers and focused schema coverage.
- Added deterministic helpers for the benchmark root plus per-target `run_manifest.json`, `case_results.jsonl`, and `raw_responses.jsonl` paths, exposed the new helpers through `materials_discovery.llm`, and created focused `test_llm_external_benchmark_schema.py` coverage that locks the new artifact family away from `llm_external_sets` and `llm_external_models`.
- 03:17 EDT — Finished the Phase 35 Plan 03 docs and example-spec slice for external targets.
- Added committed CIF and material-string example target specs, shipped a dedicated external-target runbook that explains register or inspect or smoke plus the `data/llm_external_models/{model_id}/` artifact family, and refreshed the docs map plus configuration and pipeline references so the Phase 35 boundary stays explicit before Phase 36 scorecards.
- 03:17 EDT — Implemented the Phase 35 Plan 03 external-target CLI workflow and coverage.
- Added `llm-register-external-target`, `llm-inspect-external-target`, and `llm-smoke-external-target` to `cli.py`, kept the repo-standard exit-code-2 failure posture for missing specs or unknown model IDs or invalid artifacts, and locked the new command/help surface with focused CLI tests that exercise real registration and smoke persistence in a temporary workspace.
- 02:59 EDT — Finished the Phase 35 Plan 02 environment-capture and smoke persistence pass in `llm/external_targets.py`.
- Added typed environment capture with Python, platform, optional package-version, and snapshot-lineage fields, persisted `environment.json` and `smoke_check.json` under the dedicated external-target root, and kept the smoke path fail-closed on missing snapshot inputs while still writing a typed failed result for later inspect surfaces.
- 02:59 EDT — Implemented the Phase 35 Plan 02 external-target registration core and registry tests.
- Added typed spec loading, immutable registration writing, repo-relative snapshot-path normalization, conflict-detecting fingerprints, and reload helpers in `llm/external_targets.py`, then locked the behavior through tmp-path registration tests that prove idempotent repeats and clear different-fingerprint failures.
- 02:59 EDT — Added the Phase 35 Plan 01 external-target storage helpers in `llm/storage.py` and re-exported them from `materials_discovery.llm`.
- Added deterministic helpers for the `llm_external_models` root plus fixed `registration.json`, `environment.json`, and `smoke_check.json` filenames, and extended the focused schema test file so the new artifact family is locked apart from `llm_checkpoints`.
- 02:59 EDT — Implemented the Phase 35 Plan 01 external-target contract in `llm/schema.py` and exported it from `materials_discovery.llm`.
- Added explicit external-target identity and compatibility fields, typed reproducibility-environment and smoke-result contracts, deterministic path pointers for later inspect flows, and focused schema coverage that keeps the new surface benchmark-specific instead of leaking into checkpoint lifecycle or SystemConfig.
- 02:24 EDT — Finished the Phase 34 Plan 03 operator-doc and example-spec slice.
- Added a committed `al_cu_fe_translated_benchmark_freeze.yaml` that points at two shipped demo translation-bundle manifests, generated those demo bundles from the checked-in Al-Cu-Fe translation fixture so the sample spec resolves to real repo-backed artifacts, updated the freeze loader so YAML specs work end to end, and documented the new freeze or inspect workflow plus the Phase 35 and Phase 36 scope boundary in the docs map, configuration reference, and pipeline command reference.
- 02:15 EDT — Implemented the Phase 34 Plan 03 translated benchmark CLI surface in `cli.py`.
- Added `llm-translated-benchmark-freeze` to call the Phase 34 freeze core and emit the typed JSON summary, added `llm-translated-benchmark-inspect` to read `manifest.json` plus included and excluded inventories and print a concise human-readable trace, and kept the repo-standard exit-code-2 failure path for missing spec or manifest files, invalid `--show` values, and absent `--candidate-id` requests.
- 02:10 EDT — Started Phase 34 Plan 03 in TDD RED mode by adding translated benchmark CLI tests and help coverage.
- The new failing coverage requires `mdisc llm-translated-benchmark-freeze` to emit a JSON summary from a file-backed spec, locks clear exit-code-2 failures for missing specs or invalid freeze contracts, defines the human-readable inspect trace for benchmark-set metadata and included or excluded rows, and extends root help discoverability to the new translated benchmark workflow before `cli.py` exposes those commands.
- 01:58 EDT — Added a small acceptance follow-up for the Phase 34 Plan 02 persistence pass.
- Kept the implementation on storage helpers, but made the fixed artifact-family filenames explicit again through direct test assertions and a brief module note so the plan acceptance greps can see the frozen file contract in-code without changing the runtime path logic.
- 01:57 EDT — Finished the Phase 34 Plan 02 persistence pass across the freeze module, schema, and public `llm` exports.
- `freeze_translated_benchmark_set(...)` now writes the normalized freeze contract and full artifact family under `data/benchmarks/llm_external_sets/{benchmark_set_id}/`, records source bundle manifest paths and export IDs plus exclusion-reason counts in `manifest.json`, keeps all written bytes stable across repeat runs, and exposes the freeze helpers through `materials_discovery.llm`; I also added the missing `exclusion_reason_counts` field to `TranslatedBenchmarkSetManifest` as a direct correctness follow-up for the new lineage contract.
- 01:53 EDT — Started the Phase 34 Plan 02 persistence RED slice by extending `tests/test_llm_translated_benchmark_freeze.py`.
- The new failing cases require `freeze_contract.json` and `manifest.json` to exist beside the written inventories, validate those files through the benchmark-pack schema models, lock stable artifact bytes across repeat runs, require exclusion-reason tallies in the manifest, and force the freeze helpers onto the public `materials_discovery.llm` surface before the persistence implementation.
- 01:51 EDT — Implemented the first Phase 34 Plan 02 freeze-engine pass in `llm/translated_benchmark.py`.
- The new module loads typed freeze specs plus shipped bundle manifests and inventory rows, applies explicit system or target-family or fidelity-tier or loss-posture filters, sorts deterministically by bundle path and candidate and payload hash, excludes exact duplicates after the first kept row, fails closed on conflicting payload hashes for the same candidate ID, and writes included or excluded benchmark inventories for later manifest work.
- 01:48 EDT — Started Phase 34 Plan 02 in TDD RED mode by adding `tests/test_llm_translated_benchmark_freeze.py`.
- The new failing coverage drives the future freeze engine through real translation bundles and locks bundle-manifest loading, explicit system or target-family or fidelity or loss-posture exclusions, deterministic duplicate handling, clear conflicting-payload failures, and spec-order-independent row ordering before `llm/translated_benchmark.py` exists.
- 01:39 EDT — Implemented the Phase 34 Plan 01 benchmark-pack storage helpers in `llm/storage.py`.
- Added deterministic helpers for the `llm_external_sets` root plus `freeze_contract.json`, `manifest.json`, `included.jsonl`, and `excluded.jsonl`, reusing the shared artifact-id guard so blank benchmark-set IDs fail early and the new artifact family stays isolated from translation-export and serving-benchmark directories.
- 01:38 EDT — Started the Phase 34 Plan 01 storage-helper RED slice by extending `tests/test_llm_translated_benchmark_schema.py`.
- The new failing cases lock the `llm_external_sets` artifact root, dedicated freeze-contract and included/excluded inventory filenames, blank benchmark-set rejection through the shared artifact-id guard, and explicit separation from translation-export plus serving-benchmark directories.
- 01:32 EDT — Implemented the Phase 34 Plan 01 translated benchmark-pack contract in `llm/schema.py` and exported it from `materials_discovery.llm`.
- Added explicit benchmark-set filters, typed loss-posture and exclusion vocabularies, included/excluded row lineage models that stay additive to translation inventories, and a file-backed manifest/summary surface; the focused pytest slice turned green for the new contract tests.
- 01:32 EDT — Started Phase 34 Plan 01 in TDD RED mode by adding `tests/test_llm_translated_benchmark_schema.py`.
- The new failing coverage locks the benchmark-set spec filters, typed loss-posture and exclusion vocabularies, included/excluded translation-row lineage, and manifest path/count fields before the translated benchmark-pack contract or storage helpers exist.
- 00:15 EDT — Finished the Phase 33 Plan 03 operator docs slice by adding an `llm-translation` runbook, threading it through the README/docs map and pipeline command reference, tightening the developer contract note so it points operators to the runbook, and verifying CLI help discoverability at `17 passed`.
- 00:09 EDT — Implemented the Phase 33 Plan 02 CLI layer by adding `mdisc llm-translate` and `mdisc llm-translate-inspect`, wiring bundle export into the standard stage-manifest flow with campaign-lineage and benchmark-context passthrough, and verifying the focused CLI slice at `4 passed`.

### 2026-03-22

- Created this progress document to maintain a timestamped record of all experiments and actions across the materials-discovery pipeline.
- Current state: RM0–RM1 complete; RM2–RM6 have runnable software pathways with four phases of scientific hardening applied. CLI/schema contracts are frozen.
- Target systems: Al-Cu-Fe, Al-Pd-Mn, Sc-Zn.

- **Added Ti-Zr-Ni (titanium-zirconium-nickel) as fourth target system.**
  - Rationale: well-known icosahedral quasicrystal former (Tsai-type, e.g. Ti₄₁.₅Zr₄₁.₅Ni₁₇).
  - Element properties added for Ti, Zr, Ni (atomic number, covalent radius, electronegativity, valence electrons).
  - Pairwise mixing-enthalpy proxies: Ni-Ti (−0.35 eV/atom), Ni-Zr (−0.49 eV/atom), Ti-Zr (~0.00 eV/atom).
  - Composition bounds: Ti 30–50%, Zr 25–45%, Ni 10–25% — covers the icosahedral phase region.
  - Template: icosahedral_approximant_1_1 (same family as Al-Cu-Fe).
  - Mock config: `configs/systems/ti_zr_ni.yaml`.
  - Prototype JSON (`data/prototypes/ti_zr_ni_icosahedral_1_1.json`) not yet authored — will fall back to generic icosahedral template until then.
  - Updated REAL_MODE_EXECUTION_PLAN.md and README.md.

### 2026-03-23

- **Added LLM & quasicrystal landscape documentation.**
  - New file: `materials-discovery/developers-docs/llm-quasicrystal-landscape.md`.
  - Covers: the fundamental challenge of LLMs with aperiodic structures (CIF periodicity assumption), how LLMs are used in QC workflows (CSLLM synthesizability, data interpretation), AI models that simulate/generate QCs (MLIPs, SCIGEN diffusion, NN-VMC electronic QCs, TSAI random forest), and the LLM-quasicrystal analogy.
  - Includes a section connecting the landscape to our pipeline's hybrid approach (Zomic representation, MLIP validation, planned LLM stages).
  - Linked from `materials-discovery/developers-docs/index.md` documentation map.
  - Also updated index.md Chemical Systems table to include Ti-Zr-Ni.

- **Executed Stage 1 (ingest) for Ti-Zr-Ni.**
  - Added 3 Ti-Zr-Ni reference phases to `data/external/fixtures/hypodx_sample.json`:
    - i-phase: Ti₄₁.₅Zr₄₁.₅Ni₁₇ (the canonical icosahedral composition)
    - approximant: Ti₃₆Zr₃₆Ni₂₈
    - C14-Laves: Ti₃₃Zr₃₃Ni₃₄ (competing phase for proxy hull)
  - Ran `mdisc ingest --config configs/systems/ti_zr_ni.yaml` successfully.
  - Output: `data/processed/ti_zr_ni_reference_phases.jsonl` (3 deduped rows).
  - Manifest: `data/manifests/ti_zr_ni_ingest_manifest.json`.
  - QA: 0% invalid rate, 0% duplicate rate, passed.
  - Updated `tests/test_ingest.py` assertion (raw_count 5 → 8) to reflect new fixture rows.

- **Executed Stage 2 (export-zomic) for Ti-Zr-Ni.**
  - Created `designs/zomic/ti_zr_ni_tsai_bridge.zomic`: Tsai-type icosahedral cluster motif with icosa (vertex), shell (outer/inner), and bridge (connector) orbits.
  - Created `designs/zomic/ti_zr_ni_tsai_bridge.yaml`: design config with 14.2A cell, preferred species (Ti/Zr on icosa vertices, Ni/Ti on shells, Ni on bridges).
  - Ran `mdisc export-zomic --design designs/zomic/ti_zr_ni_tsai_bridge.yaml` successfully (JDK 21 installed).
  - Output: `data/prototypes/generated/ti_zr_ni_tsai_bridge.json` — 22 sites across 3 orbits:
    - **icosa**: 10 sites (preferred: Ti, Zr) — icosahedral vertex positions
    - **shell**: 8 sites (preferred: Ni, Ti) — outer/inner shell positions
    - **bridge**: 4 sites (preferred: Ni) — connector positions
  - Raw export: `data/prototypes/generated/ti_zr_ni_tsai_bridge.raw.json`.

### 2026-04-02

- 19:10 EDT — Moved the materials discovery developer documentation from `developer-docs/materials_discovery/` to `materials-discovery/developers-docs/`.
- Updated internal references in `materials-discovery/README.md`, the moved documentation set, and this progress log to point at the new location.

### 2026-04-03

- 09:25 EDT — Started Phase 2 execution for the Material Design Data Ingestion project after the GSD executor stalled; switched to direct execution for Wave 1.
- Landed the `materials_discovery.data_sources` foundation package with canonical raw-source models, source adapter protocols, source registry helpers, storage path helpers, QA aggregation, source snapshot manifests, and a staging runtime entrypoint.
- Added the `ingestion` optional dependency group to `pyproject.toml` with `httpx` and `pymatgen` pinned for later API and structure-conversion adapters.
- 09:41 EDT — Extended `SystemConfig` with an additive `ingestion` block (`source_key`, `adapter_key`, `snapshot_id`, `use_cached_snapshot`, `query`, `artifact_root`) and reserved the `source_registry_v1` ingest adapter key in `backends/registry.py` without wiring it into the existing CLI flow yet.
- 10:02 EDT — Added focused Phase 2 contract tests for `CanonicalRawSourceRecord`, the source adapter registry, and QA duplicate/missing-field/schema-drift accounting so later provider adapters have a stable baseline.
- 10:11 EDT — Hardened `tests/test_native_providers.py` so the full-suite optional-dependency check accepts the clean failure path when `ase` itself is absent, not only the later missing-calculator branch.
- 10:16 EDT — Refreshed `uv.lock` after adding the `ingestion` extra so the lockfile now captures `httpx`, `httpcore`, `anyio`, and the updated extra metadata expected by `uv`.
- 10:34 EDT — Added the first concrete `data_sources` adapters: HYPOD-X fixture/pinned staging on the new runtime plus a local CIF-to-canonical conversion path for COD, together with offline pytest coverage and a checked-in `cod_sample.cif` fixture.
- 10:53 EDT — Added the Wave 3 adapter layer: a shared OPTIMADE adapter base, direct offline Materials Project and OQMD adapters, a dedicated `jarvis.py` OPTIMADE bridge, and test coverage that keeps the legacy `mdisc ingest` CLI path green without an `ingestion` block.
- 09:58 EDT — Added the Phase 3 projection seam in `materials_discovery.data_sources.projection`, including deterministic system matching from canonical source hints, explicit phase-name fallback precedence, additive source provenance in processed `metadata`, a reusable `ProjectionSummary`, and focused pytest coverage plus a downstream `hull_proxy` compatibility check.
- 10:08 EDT — Wired `source_registry_v1` into `mdisc ingest` by branching the CLI onto staged canonical source snapshots, adding cached-snapshot reuse rules, extending the standard ingest manifest with additive `source_lineage`, and covering the bridge path with offline source-registry, CLI, and non-ingest-manifest regression tests.
- 10:27 EDT — Closed Phase 3 with source-backed real-mode smoke coverage, projected-row downstream compatibility checks for `hull_proxy` and `report`, an explicit ingest no-DFT guard, and a deterministic `test_active_learn.py` cleanup that removes stale validated outputs before preparing new fixtures.
- Phase 4 Plan 01 Task 1 — Added the explicit reference-pack assembly layer (commit 0ab3bfce):
  - `common/schema.py`: added `ReferencePackMemberConfig` and `ReferencePackConfig` (config-layer models for `ingestion.reference_pack`); made `IngestionConfig.source_key` optional when `reference_pack` is set.
  - `data_sources/schema.py`: added `ReferencePackMemberResult` and `ReferencePackManifest` (disk-artifact models).
  - `data_sources/storage.py`: added `reference_pack_dir`, `reference_pack_canonical_records_path`, `reference_pack_manifest_path` with an optional `pack_root` override.
  - `data_sources/reference_packs.py` (new): `assemble_reference_pack` — loads staged canonical records per member, deduplicates across sources using explicit priority ordering (QC sources win), writes `canonical_records.jsonl` + `pack_manifest.json`, reuses complete cached packs when configured; `assemble_reference_pack_from_config` convenience wrapper; `load_cached_pack_manifest` helper.
  - `tests/test_reference_packs.py` (new): 15 deterministic offline tests covering config validation, single/multi-source assembly, deduplication, manifest field completeness, member lineage, cache reuse, cache bypass, missing-source errors, fingerprint determinism, and explicit priority ordering.
- Phase 4 Plan 02 — Added output-side comparability layer (3 tasks committed):
  - Task 1 (`BenchmarkRunContext` + `benchmark_pack.json`): introduced `BenchmarkRunContext` dataclass, `build_benchmark_run_context()`, and `write_benchmark_pack()` in `common/benchmarking.py`; added additive `benchmark_context` field to `ArtifactManifest`; updated `build_manifest()` signature; added `_load_benchmark_context()` helper in `cli.py` that reads ingest manifest lineage; wired context into `hifi-rank` manifest and `report` manifest + benchmark-pack artifact.
  - Task 2 (provenance in rank and report): `rank_validated_candidates()` now embeds `calibration_provenance` (source, benchmark_corpus, backend_mode) and optional `benchmark_context` in each ranked candidate's `hifi_rank` block; `compile_experiment_report()` surfaces these in per-entry evidence blocks and at the report top level via `_extract_benchmark_context()`.
  - Task 3 (regression coverage): extended all three test files — `test_benchmarking.py` adds `TestBuildBenchmarkRunContext` (8 tests, both Phase 4 systems, cross-lane key alignment); `test_hifi_rank.py` adds 3 provenance assertions; `test_report.py` adds `test_report_emits_benchmark_context_*`, `test_benchmark_pack_written_by_report_command`, and `test_cross_lane_benchmark_context_keys_match`; total 164 tests passing.

- Phase 4 Plan 03 Task 3 — Locked final cross-lane comparison story for Al-Cu-Fe:
  - `tests/test_report.py`: added `test_cross_lane_comparison_al_cu_fe_baseline_vs_reference_aware` comparing the baseline real lane (`al_cu_fe_real.yaml`) against the reference-aware real lane (`al_cu_fe_reference_aware.yaml`); asserts that both produce identical benchmark_context key sets, that lane_ids and reference_pack_ids differ visibly, that the reference-aware lane surfaces both source_keys (hypodx + materials_project) while the baseline carries none, and that per-entry evidence blocks carry calibration_provenance in both lanes.
  - Total test count: 172 passing (was 171).

- Phase 4 Plan 03 Task 2 — Added two-system end-to-end benchmark regression coverage:
  - `tests/test_real_mode_pipeline.py`: added `test_al_cu_fe_reference_aware_benchmark_e2e` and `test_sc_zn_reference_aware_benchmark_e2e` (both `@pytest.mark.integration @pytest.mark.benchmark_lane`); each runs the full ingest→generate→screen→hifi-validate→hifi-rank→active-learn→report pipeline and asserts on ingest pack lineage (pack_id, member_sources), pipeline manifest, and benchmark_pack.json structure (schema_version, system, backend_mode, benchmark_context, stage_manifest_paths, report_metrics); Sc-Zn test gracefully skips generate+ stages when Java is absent.
  - `tests/test_hifi_rank.py`: added `test_sc_zn_reference_aware_rank_embeds_benchmark_context` (Sc-Zn rank embeds sc_zn_v1 benchmark_context in provenance) and `test_both_phase4_benchmark_configs_have_comparable_context_keys` (both Phase 4 configs produce BenchmarkRunContext with identical key sets and distinct lane_ids).
  - `tests/test_report.py`: added `test_al_cu_fe_reference_aware_benchmark_pack_context`, `test_sc_zn_reference_aware_benchmark_pack_context`, and `test_both_phase4_benchmark_configs_report_context_keys_match` covering both systems' report-level benchmark_context embedding.
  - `pyproject.toml`: registered `benchmark_lane` pytest marker for the slower two-system E2E lane.
  - Total test count: 171 passing (was 164).

- Phase 4 Plan 03 Task 1 — Added operator benchmark runner script and runbook docs:
  - `scripts/run_reference_aware_benchmarks.sh` (new): config-driven two-system benchmark runner for the Phase 4 Al-Cu-Fe and Sc-Zn reference-aware lanes; supports `--count`, `--seed`, `--config-filter`, `--no-active-learn`, and `--dry-run` overrides; reports benchmark-pack artifact paths on completion.
  - `developers-docs/reference-aware-benchmarks.md` (new): operator runbook covering prerequisites (Python env, Java/Zomic dependency for Sc-Zn), full and smoke run commands, benchmark config descriptions, reference-pack input paths, benchmark-pack output structure, and regression test commands.
  - `README.md`: added Phase 4 benchmark runner quickstart section with link to runbook.
  - `developers-docs/index.md`: added runbook to Documentation Map and Phase 4 reference-aware configs to Chemical Systems table.

- Phase 5 Plan 01 — Built data lake metadata layer (Phase 5, Plan 01):
  - `lake/__init__.py` (new): package init.
  - `lake/catalog.py` (new): `CatalogEntry` Pydantic model (artifact_type, directory_path, schema_version, record_count, last_modified_utc, lineage, size_bytes, is_stale, content_hash); `DirectoryCatalog` model; `ARTIFACT_DIRECTORIES` dict with 17 entries covering all artifact subdirectories (addresses review concern #3); `build_directory_catalog()` scanning JSONL lines and JSON files with workspace-relative paths (addresses review concern #5); `write_catalog()` writing `_catalog.json`.
  - `lake/staleness.py` (new): `check_staleness()` with hash-based detection using manifest output_hashes plus mtime hint (addresses review concern #1).
  - `lake/index.py` (new): `LakeIndex` Pydantic model; `build_lake_index()` iterating over all ARTIFACT_DIRECTORIES and building + writing per-directory catalogs; `write_lake_index()` writing `data/lake_index.json`; `lake_stats()` producing summary stats.
  - `cli.py`: added `lake_app` Typer sub-application; `mdisc lake index` command running build+write; `mdisc lake stats` command loading or rebuilding the index and printing a summary table.
  - Tests: `test_lake_catalog.py` (9 tests), `test_lake_index.py` (6 tests). Total: 187 tests passing.

- Phase 4 Plan 01 Task 2 — Added benchmark-ready reference-aware configs and second-source fixtures:
  - `configs/systems/al_cu_fe_reference_aware.yaml` (new): source_registry_v1, real mode, HYPOD-X + Materials Project reference pack (priority order: hypodx > materials_project), benchmark corpus and validation snapshot wired.
  - `configs/systems/sc_zn_reference_aware.yaml` (new): source_registry_v1, real mode, Zomic design path preserved, HYPOD-X + COD reference pack (priority order: hypodx > cod), benchmark corpus and validation snapshot wired.
  - `data/external/sources/materials_project/mp_fixture_v1/canonical_records.jsonl` (new): thin 2-record MP fixture for Al-Cu-Fe multi-source proof.
  - `data/external/sources/cod/cod_fixture_v1/canonical_records.jsonl` (new): thin 1-record COD fixture for Sc-Zn multi-source proof.
  - `data/external/sources/hypodx/hypodx_pinned_2026_03_09/canonical_records.jsonl` (new): staged canonical records from the pinned HYPOD-X snapshot.
  - `data/external/sources/hypodx/hypodx_fixture_local/canonical_records.jsonl` (new): staged canonical records from the local HYPOD-X fixture for Sc-Zn.
  - `cli.py`: added `_ingest_via_reference_pack` function; updated ingest command to detect `ingestion.reference_pack` and route through the reference-pack assembly path.
  - `tests/test_benchmarking.py`: extended with 31 new deterministic tests asserting config validity, pack IDs, member source keys, snapshot IDs, priority ordering, benchmark corpus/validation-snapshot hooks, zomic-design preservation (Sc-Zn), and second-source fixture existence.

### 2026-04-03 (Phase 5 Plan 02)

- Phase 5 Plan 03 Task 2 — Wrote unified operator RUNBOOK.md:
  - `RUNBOOK.md` (new, at materials-discovery root for high visibility per D-13).
  - 8 major sections: Prerequisites, Ingestion (single + reference-pack), Reference Pack Assembly, Pipeline Execution (all 6 stages), Benchmarking (runner + artifact structure), Data Lake Operations (index/stats/compare), Analytics Notebooks (launch + config), Troubleshooting (5 sub-sections).
  - Copy-pasteable command blocks throughout (per D-14); troubleshooting entries each have Symptom/Cause/Resolution structure with commands (per D-15).
  - Section 8 Quick Reference: full mdisc command table (11 commands), key file paths, config file locations, and pointers to deep-dive developer docs.
  - 53 code blocks covering all mdisc commands, config YAML examples, artifact JSON structure, and diagnostic commands.

- Phase 5 Plan 03 Task 1 — Created three analytics notebooks and notebook smoke tests:
  - `notebooks/source_contribution_analysis.ipynb` (new): loads report JSON, groups candidates by source (via benchmark_context.source_keys and evidence.calibration_provenance), renders grouped bar chart by priority (high/medium/watch), top-N candidate table, and summary text.
  - `notebooks/cross_run_drift_detection.ipynb` (new): loads two benchmark packs as LaneSnapshots, runs compare_benchmark_packs, renders gate pass/fail comparison bar chart and metric distribution side-by-side bars with error bars, and delta interpretation table.
  - `notebooks/metric_distribution_deep_dive.ipynb` (new): loads one or more report JSONs, renders histograms for hifi_score/stability_probability/ood_score, scatter for xrd_confidence vs xrd_distinctiveness, and a summary statistics table; supports overlay mode for cross-run comparison.
  - All notebooks use `workspace_root()` for data path construction and degrade gracefully when data files are missing.
  - `tests/test_notebooks.py` (new): 6 tests — 3 static (valid JSON, imports from materials_discovery, uses workspace_root) always run; 3 execution smoke tests (via nbconvert + fixture workspace injection) skip gracefully when nbformat/nbconvert not installed.

- Phase 5 Plan 02 — Built cross-lane comparison engine and wired `mdisc lake compare` CLI command:
- `lake/compare.py` (new): lane-centric internal model with `MetricDistribution` (mean, min, max, std, count), `LaneSnapshot` (loads from benchmark_pack.json, dereferences stage_manifest_paths["report"] to read deeper report entries for per-candidate metric aggregation), `GateDelta` (with status: both_pass/both_fail/regression/improvement), `MetricDelta`, and `ComparisonResult` (schema_version "comparison/v1").
- `compare_benchmark_packs()`: builds LaneSnapshot for each pack, computes gate deltas and metric distribution diffs (8 key metrics: hifi_score, stability_probability, ood_score, xrd_confidence, xrd_distinctiveness, delta_e_proxy_hull_ev_per_atom, uncertainty_ev_per_atom, md_stability_score).

### 2026-04-06

- 00:04 EDT — Started Phase 33 Plan 02 in TDD RED mode by adding `tests/test_llm_translation_cli.py`.
- The new failing CLI coverage requires `llm-translate` to pass source-lineage and benchmark-context hooks through to the bundle writer while writing a standard stage manifest, and requires `llm-translate-inspect` to summarize bundle manifests plus candidate-level payload tracing without custom Python.
- 00:02 EDT — Implemented the Phase 33 Plan 01 translation-bundle layer in `llm/schema.py`, `llm/storage.py`, `llm/translation_bundle.py`, and `materials_discovery.llm`.
- The new core writes dedicated translation bundle directories with raw payload files, inventory rows that keep emitted text inline for later experiment reuse, bundle manifests that preserve input-path and optional lineage/benchmark hooks, and byte-stable reruns for the same export ID across both CIF and material-string targets.
- 23:56 EDT — Started Phase 33 Plan 01 in TDD RED mode by adding `tests/test_llm_translation_bundle.py`.
- The new failing coverage locks a dedicated `data/llm_translation_exports/{export_id}/` artifact family, translation bundle manifest/inventory contracts, raw payload file expectations for exact and lossy fixtures, inline emitted-text experiment hooks, and byte-stable repeated bundle writing before the new Phase 33 writer exists.
- 23:44 EDT — Added the final Phase 32 parser/failure regression coverage in `tests/test_llm_translation_cif.py` and `tests/test_llm_translation_export.py`.
- The new tests pin repo-local CIF parsing against the checked-in periodic golden and the stripped lossy QC payload, assert that malformed periodic artifacts fail through `emit_translated_structure(...)`, and keep legitimate lossy exports distinct from malformed inputs by requiring successful serialization for both built-in target families.
- 23:39 EDT — Implemented Phase 32 Plan 03 Task 1 by checking in four golden exporter outputs under `tests/fixtures/llm_translation/`.
- The new files freeze the shipped contract exactly: CIF keeps the explicit fidelity/loss metadata comment preamble, while the raw `crystaltextllm_material_string` goldens remain bare CrystalTextLLM-compatible bodies and rely on the artifact contract for provenance and lossy semantics.
- 23:35 EDT — Started Phase 32 Plan 03 Task 1 in TDD RED mode by adding `tests/test_llm_translation_export_fixtures.py`.
- The new failing regression suite requires four checked-in golden exporter outputs, exact emitted-byte matches for both Phase 31 boundary fixtures across CIF and CrystalTextLLM-compatible material-string targets, and explicit lossy periodic-proxy semantics while keeping the raw material-string body free of repo-only metadata headers.
- 23:26 EDT — Implemented Phase 32 Plan 02 Task 2 by finishing the `emit_translated_structure(...)` branch for `material_string`.
- CIF and material-string exports now share the same readiness validation and copy-not-mutate dispatch path, emitted artifacts preserve source linkage/fidelity/loss diagnostics/site ordering unchanged, and unsupported target-family values still fail clearly instead of silently falling back.
- 23:23 EDT — Started Phase 32 Plan 02 Task 2 in TDD RED mode by replacing the old `material_string` NotImplemented boundary with real cross-target dispatch expectations.
- The new failing coverage requires `emit_translated_structure(...)` to handle both built-in target families, preserve shared artifact identity across CIF and material-string exports, keep dispatched material-string output parseable, and still fail clearly on unsupported target families.
- 23:20 EDT — Implemented Phase 32 Plan 02 Task 1 by adding `emit_material_string_text(...)` and exporting it from `materials_discovery.llm`.
- The new emitter intentionally follows the autonomous-mode deviation instead of the literal plan body: it writes a bare CrystalTextLLM-compatible body with lengths, angles, and alternating species/fractional-coordinate lines, while source linkage, fidelity tier, and loss reasons remain on the translated artifact fields so the raw text stays parser-compatible.
- 23:18 EDT — Started Phase 32 Plan 02 Task 1 in TDD RED mode by adding `tests/test_llm_translation_material_string.py`.
- The new failing coverage deliberately follows the review-backed deviation: the emitted `crystaltextllm_material_string` body must stay parser-compatible with CrystalTextLLM-style lengths/angles/species/coordinates lines, while source/fidelity/loss metadata remains on the translated artifact contract instead of breaking the first line with repo-only headers.
- 23:08 EDT — Corrected the new CIF site-order assertion in `tests/test_llm_translation_cif.py` after the first Task 2 green run showed the serializer was fine and the test was mistakenly counting the `loop_` marker as a site row.
- 23:07 EDT — Implemented Phase 32 Plan 01 Task 2 by tightening `emit_cif_text(...)` to the fixed CIF contract.
- The serializer now starts with source/fidelity/loss comment lines, keeps the required scalar-field and atom-loop order, stays parser-compatible with the repo-local CIF reader after comment stripping, and makes the lossy periodic-proxy posture visible in the emitted text instead of only on the artifact wrapper.
- 23:05 EDT — Started Phase 32 Plan 01 Task 2 in TDD RED mode by adding `tests/test_llm_translation_cif.py`.
- The new failing CIF coverage locks the deterministic comment preamble, fixed cell-field and atom-loop header order, parser compatibility after comment stripping, preserved translated site order, and explicit lossy periodic-proxy metadata for the QC-native fixture before tightening the serializer.
- 23:09 EDT — Implemented Phase 32 Plan 01 Task 1 by adding `llm/translation_export.py` and exporting the new helpers from `materials_discovery.llm`.
- The new seam validates periodic export readiness up front, shares one deterministic float formatter, returns copied artifacts with `emitted_text` populated, and keeps `material_string` explicitly unimplemented until Plan 02 while the CIF branch stays a narrow pure-text serializer ready for the stricter Task 2 contract.
- 23:01 EDT — Started Phase 32 Plan 01 Task 1 in TDD RED mode by adding `tests/test_llm_translation_export.py`.
- The new failing coverage locks shared export-readiness validation for missing periodic cell data, empty site lists, and missing fractional coordinates; it also requires byte-stable dispatch, copy-not-mutate semantics, and an explicit `NotImplementedError` for `material_string` until Plan 02 lands.

- 20:03 EDT — Wrote `developers-docs/llm-translation-contract.md` as the Phase 31 implementation handoff for Phase 32 exporters.
- The note keeps Zomic as the source of truth, defines `exact`, `anchored`, `approximate`, and `lossy`, documents the built-in CIF/material-string targets, and explicitly defers operator workflow docs to Phase 33.
- 20:01 EDT — Implemented Phase 31 Plan 03 Task 1 by adding repo-backed Al-Cu-Fe and Sc-Zn translation fixtures under `tests/fixtures/llm_translation/`.
- The fixture data makes the boundary explicit in shape: the periodic-safe example stores fractional positions on every site, while the QC-native example is qphi-only and therefore remains an explicit periodic-proxy/lossy case for both built-in targets.
- 20:00 EDT — Started Phase 31 Plan 03 Task 1 in TDD mode by adding failing `test_llm_translation_fixtures.py` coverage that reads planned repo fixtures instead of inline dicts.
- The RED slice locks a periodic-safe Al-Cu-Fe candidate at `exact`, a QC-native Sc-Zn candidate at explicit `lossy`, and checks both built-in translation target families before any fixture JSON is added.
- 19:53 EDT — Implemented Phase 31 Plan 02 Task 2 by replacing the placeholder fidelity stub with conservative exact/anchored/approximate/lossy assessment in `llm/translation.py`.
- The classifier now requires positive periodic-safe evidence for `exact`, caps mixed-origin candidates at `approximate`, marks QC-native periodic exports `lossy` with explicit reasons, and raises a clear error for unsupported `exact` claims; the focused pytest slice passed at `10 passed`.
- 19:51 EDT — Added the Task 2 RED translation-fidelity tests for conservative exact/anchored/approximate/lossy classification, explicit QC-native loss reasons, and a hard failure when callers request unsupported `exact` periodic export.
- The new coverage also locks a mixed-origin approximant candidate at `approximate` so the fidelity tier stays conservative when periodic-safe evidence is incomplete.
- 19:49 EDT — Implemented Phase 31 Plan 02 Task 1 by adding `llm/translation.py`, exporting the translation-core API, and extending `structure_realization.py` with a stable per-site coordinate-origin helper.
- The normalization seam now returns deterministic translated artifacts with stable site ordering, canonical cell fields, coordinate-source diagnostics, and no emitted CIF/material-string text yet; the focused pytest slice passed at `7 passed`.
- 19:47 EDT — Started Phase 31 Plan 02 Task 1 in TDD mode by adding failing translation-core coverage for deterministic normalized artifacts, explicit coordinate-source reporting, and byte-stable repeated normalization.
- Added a companion `test_structure_realization.py` regression that locks a stable per-site coordinate-origin helper so the translation seam can reuse structure realization instead of reimplementing branch logic.
- 19:35 EDT — Started Phase 31 Plan 01 Task 1 in TDD mode by adding failing `test_llm_translation_schema.py` coverage for the additive translated-structure contract.
- The RED slice locks source candidate linkage, the separate `lossy` export-fidelity tier, explicit lossy-reason validation, and diagnostic-carrying artifacts that do not require emitted CIF/material-string text yet.
- 19:39 EDT — Implemented the additive translation contract in `llm/schema.py` with typed source references, target descriptors, normalized artifact payload fields, standardized loss-reason names, and typed diagnostics.
- Exported the Task 1 public surface from `materials_discovery.llm`, kept the older corpus `FidelityTier` unchanged, and verified the focused translation-schema slice at `6 passed`.
- 19:44 EDT — Added the Task 2 RED registry tests to the same translation-schema slice so Phase 32 will inherit explicit target discovery and resolution APIs instead of guessing target-family names.
- The new failing cases lock built-in CIF and material-string descriptors, periodic-cell requirement metadata, and a clear error path for unknown target families.
- 19:47 EDT — Implemented the built-in translation target registry in `llm/schema.py` and exported the new list/resolve helpers from `materials_discovery.llm`.
- The registry now ships stable CIF and CrystalTextLLM-style descriptors with explicit `requires_periodic_cell`, `requires_fractional_coordinates`, `preserves_qc_native_semantics`, and emission-kind metadata; the focused schema slice passed at `10 passed`.
  - `write_comparison()`: writes JSON to `data/comparisons/` with slugified filename (D-06).
  - `format_comparison_table()`: produces dual-format terminal table with header, gate section, and metric section (D-06).
  - Graceful fallback: if report file missing, warns and falls back to report_metrics embedded in benchmark pack (no crash).
  - `cli.py`: added `@lake_app.command("compare")` with explicit pack_a/pack_b positional args (D-08), optional `--output-dir` and `--json-only` flags.
  - `tests/test_lake_compare.py` (new): 10 tests covering all 7 planned behaviors plus CLI integration. 197 total tests passing.
  - Addresses: PIPE-04, D-06, D-07, D-08, review concern #2 (data depth), review concern #6 (lane-centric model).

### 2026-04-03 (Phase 5 Complete)

- **Phase 5 execution complete — platform is analytically useful.**
  - All 3 plans executed across 3 waves: catalog/index layer (Wave 1), comparison engine (Wave 2), notebooks + RUNBOOK (Wave 3).
  - Verification passed: 15/15 must-haves verified, 200 tests passing, 0 regressions.
  - All 6 cross-AI review concerns addressed: hash-based staleness (HIGH), comparison data depth via benchmark-pack dereferencing (HIGH), 17-directory artifact inventory (HIGH), notebook smoke tests (MEDIUM), workspace-relative lineage (MEDIUM), lane-centric comparison model (MEDIUM).
  - Requirements satisfied: PIPE-04 (source-aware reference-phase enrichment analytics), PIPE-05 (unified operator runbook).
  - New CLI commands: `mdisc lake index`, `mdisc lake stats`, `mdisc lake compare`.
  - New artifacts: 3 analytics notebooks, RUNBOOK.md, `lake/` package (catalog.py, index.py, staleness.py, compare.py).
  - Next phase: Phase 6 (Zomic Training Corpus Pipeline).

- Phase 6 Plan 01 Task 1 — Added the foundation corpus contracts and committed starter config:
  - New package: `src/materials_discovery/llm/` with `schema.py` and `__init__.py`.
  - `schema.py` defines `CorpusBuildConfig`, `CorpusInventoryRow`, `CorpusProvenance`, `CorpusValidationState`, `CorpusConversionTrace`, `CorpusExample`, `CorpusQaSummary`, `CorpusManifest`, and `CorpusBuildSummary`.
  - Locked the review-driven contract updates up front: typed validation state, record-addressable inventory rows, and neutral `release_tier="pending"` before QA promotion.
  - Added `configs/llm/corpus_v1.yaml` covering Phase 6 source-family toggles, systems, thresholds, source keys, and reference-pack IDs.
  - Added `tests/test_llm_corpus_schema.py`; focused verification passed with `6 passed`.

- Phase 6 Plan 01 Task 2 — Added deterministic corpus storage and manifest helpers:
  - New modules: `llm/storage.py` and `llm/manifests.py`.
  - Locked the on-disk artifact family under `data/llm_corpus/{build_id}/` with helpers for syntax/materials/rejects/inventory/qa/manifest paths.
  - Added deterministic `corpus_build_fingerprint()`, `build_corpus_manifest()`, and `write_corpus_manifest()` using workspace-relative paths and output hashes.
  - Extended `llm/__init__.py` to export the new helper surface.
  - Added `tests/test_llm_corpus_storage.py` and `tests/test_llm_corpus_manifest.py`; combined `06-01` validation passed with `11 passed`.

- Phase 6 Plan 02 Task 1 — Added the deterministic LLM corpus inventory layer:
  - New module: `llm/inventory.py` with dedicated collectors for repo regression scripts, part scripts, materials-design `.zomic` files, candidate JSONL rows, generated raw exports, canonical source records, reference-pack records, and the committed PyQCstrc projection payload.
  - Added `tests/fixtures/pyqcstrc_projection_sample.json` as the offline fixture backing the required `pyqcstrc_projection` source family.
  - Extended `llm/__init__.py` to export the public inventory helpers so later builder code can reuse them directly.
  - Added `tests/test_llm_corpus_inventory.py`; focused verification passed with `7 passed`.

- Phase 6 Plan 02 Task 2 — Added the QA grading and dedupe layer:
  - New module: `llm/qa.py` with `grade_corpus_example()`, `dedupe_corpus_examples()`, and `summarize_corpus_quality()`.
  - Locked the release policy around pending -> gold/silver/reject promotion, label/orbit validation via `_infer_orbit_name`, and deterministic duplicate precedence on release tier, fidelity tier, source family, and example id.
  - Extended `llm/__init__.py` to export the QA helpers for the later builder flow.
  - Added `tests/test_llm_corpus_qa.py`; focused verification passed with `5 passed`.

- Phase 6 Plan 03 Task 1 — Added deterministic record2zomic conversion:
  - New modules: `llm/converters/axis_walk.py` and `llm/converters/record2zomic.py`, plus the new `llm/converters/` package surface.
  - Added a bounded, auditable qphi axis-walk decomposition strategy with explicit `direct_basis`, `bounded_search`, `anchored_fallback`, and `heuristic_fallback` trace labels.
  - Added deterministic `CandidateRecord -> CorpusExample` serialization with orbit-grouped branch blocks, comment preambles, preserved `source_label_map`, and anchored/approximate/heuristic fidelity visibility through `CorpusConversionTrace`.
  - Added `tests/test_llm_record2zomic.py`; focused verification passed with `12 passed` alongside the companion projection/compiler slice.

- Phase 6 Plan 03 Task 2 — Added the compile helper and PyQCstrc projection path:
  - New module: `llm/compiler.py` for temporary `.zomic` + design-YAML generation and bridge-backed compile validation with deterministic cell scaling from qphi bounds.
  - New module: `llm/converters/projection2zomic.py` for committed PyQCstrc-style projection payload conversion into `CorpusExample` records without a live PyQCstrc dependency.
  - Restored `projection_payload_to_zomic` to the public `llm/converters/__init__.py` exports for later builder dispatch.
  - Added `tests/test_llm_projection2zomic.py`; focused verification passed with `12 passed` alongside the companion record2zomic slice.

- Phase 6 Plan 04 Task 1 — Added CIF/open approximant conversion:
  - New module: `llm/converters/cif2zomic.py` reusing `expand_cif_orbits()` when symmetry metadata is present and falling back to `parse_cif()` on thin offline fixtures without a symmetry loop.
  - Added `tests/fixtures/hypodx_approximant_sample.cif` as the committed HYPOD-X-style approximant sample for offline coverage.
  - Added `canonical_record_to_zomic()` support for CIF-backed canonical source records plus a deterministic composition-only fallback for staged records that do not carry a structure representation.
  - Added `tests/test_llm_cif2zomic.py`; focused verification passed with `9 passed` together with `test_prototype_import.py` and `test_data_source_cod.py`.

- Phase 6 Plan 04 Task 2 — Added native-Zomic and generated-export source loaders:
  - New module: `llm/converters/native_zomic.py` with direct label extraction and exact-fidelity corpus examples for repo-native `.zomic` scripts.
  - New module: `llm/converters/generated_export.py` for raw export artifacts, preserving direct source metadata and choosing `exact` only when a source `.zomic` file is available.
  - Added loader-hint metadata (`native_zomic`, `generated_export`) so the final builder can dispatch from inventory rows without re-inferring source type.
  - Added `tests/test_llm_native_sources.py`; focused verification passed with `5 passed`.

- Phase 6 Plan 04 Task 3 — Added the end-to-end corpus builder:
  - New module: `llm/corpus_builder.py` that starts from `build_inventory()`, dispatches by `loader_hint`, compiles/validates generated examples, grades them, dedupes them, and writes `syntax_corpus.jsonl`, `materials_corpus.jsonl`, `rejects.jsonl`, `inventory.json`, `qa.json`, and `manifest.json`.
  - Tightened the CIF conversion seam so CIF-derived orbit names line up with label-derived orbit validation inside the shared QA rules, preventing valid canonical-source examples from being rejected downstream.
  - Added `tests/test_llm_corpus_builder.py`; focused verification passed with `17 passed` together with the inventory and QA slices.

- Phase 6 Plan 04 Task 4 — Added the operator-facing corpus CLI:
  - `cli.py` now mounts `llm_corpus_app` under `mdisc llm-corpus` and exposes `mdisc llm-corpus build --config ...`.
  - The new command validates the YAML as `CorpusBuildConfig`, calls `build_llm_corpus()`, prints `CorpusBuildSummary` as JSON, and follows the existing CLI error path with exit code 2 on invalid configs.
  - Added `tests/test_llm_corpus_cli.py`; focused verification passed with `11 passed` together with the existing `test_cli.py` contract suite.

### 2026-04-03 (Phase 7 Plan 01)

- Added the Phase 7 llm-generate contract layer:
  - `common/schema.py` now includes additive `BackendConfig.llm_*` fields, optional `LlmGenerateConfig`, and `LlmGenerateSummary` without requiring existing system configs to change.
  - `llm/schema.py` now defines `LlmGenerationRequest`, `LlmGenerationAttempt`, `LlmGenerationResult`, and `LlmRunManifest`, reusing `CompositionBound` and `ValidationStatus` instead of creating a parallel taxonomy.
- 20:01 EDT — Started Phase 8 Plan 01 by adding the first `llm-evaluate` contract and runtime slice.
- Added additive `LlmEvaluateConfig` and `LlmEvaluateSummary` models to `common/schema.py`, keeping the new evaluation path optional in `SystemConfig`.
- Added typed Phase 8 models in `llm/schema.py` for `LlmEvaluationRequest`, `LlmAssessment`, and `LlmEvaluationRunManifest`, plus new schema-version constants.
- Added `llm/evaluate.py` with ranked-candidate loading, structured prompt assembly, mock/real provider reuse, typed request/assessment JSONL artifacts, additive `CandidateRecord.provenance["llm_assessment"]`, and run-manifest persistence under `data/llm_evaluations/`.
- Added `mdisc llm-evaluate` to `cli.py`, including default output under `data/llm_evaluated/` and CLI-written calibration/manifest artifacts.
- Added focused Phase 8 tests in `tests/test_llm_evaluate_schema.py` and `tests/test_llm_evaluate_cli.py` covering schema validation, end-to-end mock evaluation artifacts, CLI success, and the missing-config error path.
- 20:20 EDT — Landed Phase 8 Plan 02 to thread LLM assessment through downstream artifacts without changing ranking weights.
- `cli.py` now prefers `data/llm_evaluated/{system}_all_llm_evaluated.jsonl` during `mdisc report` when that additive artifact exists, while keeping the ranked JSONL fallback unchanged.
- `diffraction/compare_patterns.py` now surfaces `llm_assessment` in report entries/evidence and adds summary-level LLM counts and synthesizability aggregates.
- `common/stage_metrics.py` now records additive LLM-assessment calibration metrics so report calibration captures assessed/failed counts, anomaly flags, and mean synthesizability.
- `hifi_digital/rank_candidates.py` now documents the Phase 8 rule explicitly: existing `llm_assessment` provenance is preserved but never used to reweight scores in this phase.
- Added Plan 02 regressions in `tests/test_report.py` and `tests/test_hifi_rank.py` covering report enrichment, `llm_evaluated` preference, calibration visibility, and score/order invariance when LLM assessment context is present.
- 20:43 EDT — Closed Phase 8 Plan 03 with the downstream deterministic-vs-LLM benchmark lane.
- Added `llm/pipeline_benchmark.py` with a dedicated comparison artifact over `screen`, `hifi-validate`, `hifi-rank`, and `report`, including downstream validity, novelty, top-rank quality, and report acceptance deltas.
- Added `scripts/run_llm_pipeline_benchmarks.sh`, which injects temporary offline `llm_evaluate` configs, runs both deterministic and LLM lanes, snapshots calibration JSON per stage, and writes `data/benchmarks/llm_pipeline/{system}_comparison.json`.
- Added `tests/test_llm_pipeline_benchmarks.py` with helper-level coverage plus offline two-system end-to-end benchmark proofs for `Al-Cu-Fe` and `Sc-Zn`.
- Refreshed `README.md`, `developers-docs/index.md`, `developers-docs/llm-integration.md`, and `developers-docs/pipeline-stages.md` so Phase 8 is documented as implemented and the new pipeline benchmark workflow is discoverable.
- 21:08 EDT — Started Phase 9 by adding the formal eval-set and acceptance-pack artifact layer.
- Added `llm/eval_set.py` and `llm/acceptance.py` so Phase 6 corpus artifacts can be exported into deterministic eval sets and Phase 7/8 benchmark outputs can be summarized into a typed acceptance pack.
- Extended `llm/schema.py`, `llm/storage.py`, and `llm/__init__.py` with Phase 9 eval-set, acceptance-threshold, and suggestion-facing models and artifact paths.
- Added `tests/test_llm_acceptance_schema.py`; focused verification passed with `2 passed`.
- 21:24 EDT — Landed Phase 9 Plan 02 to make `llm-generate` example-conditioned without changing its default path.
- `common/schema.py` now lets `llm_generate` point at an eval-set file plus a deterministic maximum number of conditioning examples.
- `llm/prompting.py` now selects same-system examples by composition distance and injects them into the prompt in a reproducible block.
- `llm/generate.py` now records `example_pack_path` and `conditioning_example_ids` in both `prompt.json` and the run manifest.
- Added Plan 02 regressions in `tests/test_llm_generate_core.py` and `tests/test_llm_generate_cli.py`; focused verification passed with `12 passed`.
- 21:46 EDT — Closed Phase 9 with the operator acceptance benchmark and dry-run suggestion workflow.
- Added `llm/suggest.py` plus the `mdisc llm-suggest --acceptance-pack ...` CLI command so typed acceptance packs now produce structured next-step recommendations without launching an autonomous loop.
- Added `scripts/run_llm_acceptance_benchmarks.sh`, which composes the Phase 7 and Phase 8 benchmark lanes into a typed acceptance pack under `data/benchmarks/llm_acceptance/{pack_id}/acceptance_pack.json`.
- Added `tests/test_llm_acceptance_benchmarks.py` and extended `tests/test_cli.py`; focused verification passed with `11 passed`, and the full `materials-discovery` suite closed at `297 passed, 3 skipped, 1 warning`.
- Refreshed `README.md`, `developers-docs/index.md`, `developers-docs/llm-integration.md`, and `developers-docs/pipeline-stages.md` so the Phase 9 acceptance-pack and dry-run suggestion workflow is documented as implemented.
- `llm/runtime.py` adds the provider-neutral adapter seam with deterministic `llm_fixture_v1` behavior and the first hosted adapter path, `anthropic_api_v1`, via lazy `httpx`.
- `llm/__init__.py` now exports the new Phase 7 runtime/schemas alongside the existing Phase 6 corpus surface.
- `developers-docs/configuration-reference.md` now documents the `llm_generate:` block, mock-only defaulting, and the requirement that real hosted configs set `llm_provider` and `llm_model`.
  - Added focused coverage in `tests/test_llm_generate_schema.py` and `tests/test_llm_runtime.py` for config validation, schema typing, adapter resolution, missing secret handling, lazy imports, and API-base override behavior.

### 2026-04-03 (Phase 7 Plan 02)

- Implemented the first full `mdisc llm-generate` path:
  - Added `llm/prompting.py` for config-driven prompt construction and optional seed-script loading.
  - Added `llm/generate.py` for bounded retries, per-attempt raw completion persistence, compile-result tracking, run-manifest emission, and conversion of valid compiled orbit libraries into standard `CandidateRecord` JSONL.
  - Extended `llm/compiler.py` so compile attempts now return explicit parse/compile status, stable error kinds, and persisted raw-export/orbit-library paths when the caller supplies an artifact root.
  - Extended `generator/candidate_factory.py` with `build_candidate_from_prototype_library(...)` so compiled template geometry can become normal candidates without reusing the Z[phi] perturbation branch.
  - Added `llm_generation_metrics(...)` and wired the new `llm-generate` Typer command into `cli.py`, including calibration JSON and stage-manifest output.
  - Added committed mock configs for `Al-Cu-Fe` and `Sc-Zn`, plus focused tests in `tests/test_llm_generate_core.py`, `tests/test_llm_generate_cli.py`, and `tests/test_cli.py`.

### 2026-04-03 (Phase 7 Plan 03)

- Added the Phase 7 benchmark comparison layer:
  - New `llm/benchmark.py` builds deterministic-vs-LLM comparison payloads and writes comparison JSON under `data/benchmarks/llm_generate/`.
  - Added `scripts/run_llm_generate_benchmarks.sh` as the thin operator wrapper around `mdisc generate`, `mdisc llm-generate`, and `mdisc screen`.
  - Added the `llm_lane` pytest marker plus `tests/test_llm_generate_benchmarks.py` for offline two-system benchmark coverage across `Al-Cu-Fe` and `Sc-Zn`.
- Refreshed docs so the first LLM inference path is described as implemented rather than planned:
  - `README.md`
  - `developers-docs/index.md`
  - `developers-docs/pipeline-stages.md`
  - `developers-docs/llm-integration.md`
- Re-verified the whole `materials-discovery` suite after landing the benchmark layer to keep Phase 7 closed with a project-wide green state.

### 2026-04-05

- 20:55 EDT — Started Phase 30 Task 3 by closing the operator loop in the docs: candidate registration, lifecycle benchmarking, promote-or-keep decisions, rollback to baseline, and retirement of superseded checkpoints.
- This pass is anchored to the committed `al_cu_fe_llm_adapted.yaml`, `al_cu_fe_llm_adapted_candidate.yaml`, and `al_cu_fe_checkpoint_lifecycle_benchmark.yaml` examples so the runbook and developer docs describe the exact files operators can start from.
- Shared CLI coverage is being extended at the help/discoverability layer so the registration, list, promote, retire, and benchmark commands remain visible together as one lifecycle workflow.
- 20:44 EDT — Started Phase 30 Task 2 by committing the candidate-pinned config and the three-way lifecycle benchmark spec, then wiring an offline proof around staged promoted and candidate checkpoints in the same family.
- The new proof keeps the benchmark workflow grounded in one acceptance-pack context and verifies that lifecycle recommendation lines stay tied to structured benchmark roles rather than manual file editing.
- After this benchmark proof lands, the last Phase 30 slice is the operator docs and CLI/help surface for promotion, rollback, and retirement procedure.
- 20:41 EDT — Started Phase 30 Task 1 by adding explicit lifecycle benchmark roles so promotion guidance can come from structured benchmark intent instead of target-name heuristics.
- The serving-benchmark contract now distinguishes baseline, promoted-default, and candidate-checkpoint targets directly, which makes summary recommendations auditable and keeps rollback guidance attached to the shared benchmark output.
- Focused benchmark schema and core coverage is being extended before the committed lifecycle benchmark spec and real-mode proof land.
- 20:34 EDT — Started Phase 29 Task 3 by turning the committed adapted Al-Cu-Fe config into a promoted-family default and adding a pinned companion config for deliberate operator overrides.
- The final Phase 29 proof uses a real promotion artifact before the offline benchmark run, keeps the baseline local config visible as rollback, and updates the docs to explain promoted-default, explicit-pin, and replay-safe lifecycle behavior together.
- The real-mode and shared CLI/docs verification slices are next once the committed configs and docs land.
- 20:29 EDT — Started Phase 29 Task 2 by making replay hold on to the recorded family checkpoint identity even after later promotions move the family's default member.
- The replay path now reuses the recorded checkpoint selector for family-based launches, allows retired historical members during replay-only resolution, and keeps compare plus serving-benchmark output explicit about promoted-default versus explicit-pin execution.
- Focused coverage is being added in `test_llm_replay_core.py`, `test_llm_compare_core.py`, and `test_llm_serving_benchmark_core.py` before the committed config/docs proof in the final Phase 29 wave.
- 20:19 EDT — Started Phase 29 Task 1 by wiring promoted-family runtime resolution into the shared serving identity path.
- Family-only lanes now resolve promoted members for new execution, explicit family pins remain deliberate, retired members are rejected for fresh runs, and serving identity records lifecycle selection metadata for later replay and workflow auditing.
- Focused regressions are being added across `test_llm_checkpoint_registry.py`, `test_llm_launch_core.py`, and `test_llm_generate_cli.py` to lock the first promotion-aware workflow slice before Phase 29 replay work begins.
- 19:56 EDT — Implemented Phase 28 Plan 03 Task 2 by documenting the new checkpoint family selector, the hybrid registration-plus-lifecycle model, and the CLI action surface while keeping promoted-default execution and workflow pin resolution clearly deferred to Phase 29.
- The docs pass stays additive on purpose: it explains lifecycle state on top of the shipped v1.3 workflow, calls out placeholder evidence paths in the committed examples, and avoids implying that Phase 28 already rewired the runbook-driven operator flow.
- 19:51 EDT — Implemented Phase 28 Plan 03 Task 1 by adding committed promotion and retirement specs for the `adapted-al-cu-fe` family and extending replay compatibility coverage so retired checkpoints stay auditable by registration fingerprint.
- The example action specs use illustrative repo-relative evidence paths on purpose, and the tests now treat those files as real CLI fixtures rather than docs-only placeholders.
- 19:46 EDT — Implemented Phase 28 Plan 02 Task 2 by adding the operator-facing lifecycle CLI surface for listing family members, promoting checkpoints from typed specs, and retiring checkpoints with clear stale-write remediation.
- This command layer stays thin over the registry helpers so the lifecycle state logic remains file-backed in one place while the CLI preserves repo-standard JSON success output and exit-code-2 failure behavior.
- 19:40 EDT — Implemented Phase 28 Plan 02 Task 1 by wiring checkpoint-family lifecycle helpers into the registry layer: lifecycle index loading, candidate auto-enrollment on registration, promotion/retirement actions, and stale-write protection.
- This slice keeps promoted-default execution deferred, but it makes lifecycle mutations real and auditable with clear operator-facing failures for stale revisions, mismatched family pins, and unsafe retirement attempts.
- 19:36 EDT — Implemented Phase 28 Plan 01 Task 2 by adding deterministic checkpoint-family storage helpers under `data/llm_checkpoints/families/` plus revision-based promotion and retirement artifact paths.
- Focused registry coverage now locks `lifecycle.json`, the `actions/` directory layout, revision-stamped lifecycle action filenames, and the guarantee that legacy per-checkpoint `registration.json` paths remain unchanged.
- 19:31 EDT — Implemented Phase 28 Plan 01 Task 1 by extending the additive checkpoint lane contract with `checkpoint_family` and shipping the typed lifecycle/promotion/retirement/pin-selection schema pass for multi-checkpoint family management.
- The Wave 1 schema work keeps `checkpoint_id` as an explicit pin when a family is also declared, preserves checkpoint fingerprint identity, and adds focused coverage before any resolver or CLI behavior changes.
- 11:41 EDT — Closed the v1.3 adapted-checkpoint operator docs pass.
- Documented `mdisc llm-register-checkpoint`, strict adapted-lane registration, rollback-to-baseline guidance, and the adapted-vs-baseline benchmark recipe in `RUNBOOK.md`, `developers-docs/configuration-reference.md`, `developers-docs/llm-integration.md`, and `developers-docs/pipeline-stages.md`.
- 11:28 EDT — Completed the adapted checkpoint integration proof.
- Added file-backed checkpoint lineage to serving identity, taught replay to hard-fail on checkpoint fingerprint drift, committed `al_cu_fe_llm_adapted.yaml` plus `al_cu_fe_adapted_serving_benchmark.yaml`, and proved the offline adapted benchmark workflow in `tests/test_real_mode_pipeline.py`.
- Focused verification passed with `12 passed, 28 deselected` across checkpoint, replay, serving-benchmark, and real-mode pipeline coverage.
- 11:12 EDT — Implemented the Phase 25 checkpoint registration contract foundation.
- Added typed checkpoint registration models, storage helpers under `data/llm_checkpoints/`, a new `llm/checkpoints.py` registry layer, and the `mdisc llm-register-checkpoint --spec ...` command with deterministic fingerprinting and lineage validation.
- Focused verification passed with `16 passed` across `tests/test_llm_checkpoint_registry.py`, `tests/test_llm_checkpoint_cli.py`, and `tests/test_llm_replay_core.py`.
- 03:22 EDT — Completed the Phase 21 Plan 03 operator workflow docs pass.
- Added a dedicated serving-benchmark section to `RUNBOOK.md`, documented benchmark-spec fields plus artifact paths in the developer docs, and added shared CLI coverage for missing benchmark specs so the new command is represented in the broad command-surface suite.
- Focused verification passed with `31 passed` across `tests/test_llm_serving_benchmark_cli.py`, `tests/test_cli.py`, and `tests/test_real_mode_pipeline.py`.
- 03:20 EDT — Implemented the Phase 21 Plan 03 committed hosted and benchmark example configs.
- Added `configs/systems/al_cu_fe_llm_hosted.yaml`, plus committed `configs/llm/al_cu_fe_serving_benchmark.yaml` and `configs/llm/sc_zn_serving_benchmark.yaml` specs with placeholder-safe artifact paths and an evaluation-primary `top1` specialized target.
- Focused verification passed with `16 passed` across `tests/test_llm_serving_benchmark_cli.py` and `tests/test_real_mode_pipeline.py`, keeping the full offline benchmark proof green with the new repo-level example coverage.
- 03:19 EDT — Started Phase 21 Plan 03 Task 1 in TDD RED mode with repo-level benchmark example coverage.
- The new failing `test_real_mode_pipeline.py` regression locks the committed hosted config plus the Al-Cu-Fe and Sc-Zn serving-benchmark example specs, including the shared-context evaluation slice and thinner second-system compatibility expectations.
- 03:14 EDT — Closed Phase 21 Plan 02 Task 2 by wiring the real serving-benchmark execution proof through the shipped launch and evaluation paths.
- `llm-serving-benchmark` now reuses `resolve_campaign_launch()` with a benchmark-only lane override for launch targets, writes standard launch/comparison artifacts back into benchmark results, reuses `evaluate_llm_candidates()` for specialized evaluation targets, and rejects misaligned evaluation batches before any target execution begins.
- Focused Wave 2 verification passed with `15 passed` across `tests/test_llm_serving_benchmark_cli.py` and `tests/test_real_mode_pipeline.py`, including the new shared-context misalignment regression.
- 03:18 EDT — Started Phase 21 Plan 02 Task 2 in TDD RED mode with the real offline serving-benchmark proof.
- The new integration coverage now locks one shared-context benchmark run across hosted launch, local launch, and specialized evaluation targets, while also checking that benchmark lane overrides do not mutate the source campaign spec on disk.
- 03:12 EDT — Implemented the first Wave 2 benchmark CLI path and turned the new command tests green.
- `llm-serving-benchmark` now delegates to a typed orchestration entrypoint, always writes the smoke artifact first, stops with exit code 2 on strict smoke failures, and prints concise smoke or recommendation output plus the artifact path operators need next.
- 03:05 EDT — Started Phase 21 Plan 02 Task 1 in TDD RED mode with new benchmark CLI coverage.
- The failing CLI contract now locks `llm-serving-benchmark` smoke-only output, strict smoke failure semantics, recommendation-line printing, and `--out` summary override behavior before the command exists.
- 03:00 EDT — Implemented the Phase 21 serving-benchmark core helpers and turned the new smoke/summary tests green.
- `run_serving_smoke_check(...)` now reuses the shipped serving-lane resolver and readiness probe, records explicit no-fallback failures without dropping operator context, and `build_serving_benchmark_summary(...)` preserves per-target metadata while naming the fastest, cheapest, and lowest-friction targets.
- 02:58 EDT — Started Phase 21 Plan 01 Task 2 in TDD RED mode with new offline benchmark-core tests.
- The new failing coverage locks launch-role and evaluate-role smoke checks, explicit fallback rejection when `allow_fallback` is false, and summary recommendation lines that keep role-specific missing metrics visible.
- 03:01 EDT — Implemented the Phase 21 serving-benchmark schema, storage, and loader contract in the `llm` package.
- The new typed benchmark models now carry shared-context target metadata, nested smoke-check serving identity, deterministic artifact paths under `data/benchmarks/llm_serving/`, and an early mixed-system guard in `load_serving_benchmark_spec(...)`.
- 02:53 EDT — Started Phase 21 Plan 01 Task 1 in TDD RED mode by adding `tests/test_llm_serving_benchmark_schema.py`.
- The new failing coverage locks the shared-context benchmark spec, mixed-system acceptance-pack validation, nested serving-identity serialization, and deterministic benchmark storage paths before the new serving-benchmark schema/core layer is implemented.
- 01:24 EDT — Rounded `projection2zomic` composition metadata deterministically after the Phase 20 full-suite run exposed exact-value float noise in the inherited PyQCstrc regression.
- 01:18 EDT — Closed Phase 20 Plan 03 with the `Sc-Zn` thin compatibility proof, additive specialized-lane docs, and an offline launch/replay/compare regression that preserves distinct generation-vs-evaluation lineage.
- 00:10 EDT — Implemented the Phase 19 Plan 01 local-serving contract foundation.
- Added additive backend transport fields (`llm_request_timeout_s`, `llm_probe_timeout_s`, `llm_probe_path`), lane identity fields (`checkpoint_id`, `model_revision`, `local_model_path`), and optional `default_model_lane` / `fallback_model_lane` support in `common/schema.py`.
- Extended `llm/schema.py` with typed `LlmServingIdentity`, broader lane-source compatibility, and optional nested serving identity on run and launch artifacts while keeping legacy artifacts readable without that field.
- Added `OpenAICompatLlmAdapter` plus `validate_llm_adapter_ready()` in `llm/runtime.py`, including default `/v1/models` probing, supported OpenAI-compatible response parsing, and operator-facing connectivity failures that tell the user to confirm the local server is already running.
- Extended `tests/test_llm_launch_schema.py` and `tests/test_llm_runtime.py` to cover API-base normalization, optional serving identity, legacy artifact reads, default probe behavior, and offline local-adapter parsing.
- Focused verification passed with `20 passed` across `tests/test_llm_launch_schema.py` and `tests/test_llm_runtime.py`.
- 23:25 EDT — Implemented the Phase 19 Plan 02 lane-aware local-serving execution bridge.
- Added shared `resolve_serving_lane(...)` semantics so manual `llm-generate` and campaign `llm-launch` both follow the same precedence order: `CLI requested lane > config default > explicit fallback > backend default`.
- Extended `cli.py` with `llm-generate --model-lane`, early local-serving readiness probes, additive serving-identity construction, and preserved standard summary / manifest output for legacy no-lane configs.
- Updated `generate.py` and `launch.py` so run manifests and resolved launch artifacts record nested `serving_identity` while preserving the existing flat adapter/provider/model fields for compatibility.
- Extended `tests/test_llm_generate_core.py`, `tests/test_llm_launch_core.py`, `tests/test_llm_generate_cli.py`, `tests/test_llm_launch_cli.py`, and `tests/test_cli.py` to cover explicit lane selection, configured fallback behavior, readiness failures, and backward-compatible no-lane execution.
- Focused verification passed with `40 passed` across the Plan 02 generate/launch core and CLI regression slice.
- 23:37 EDT — Implemented the Phase 19 Plan 03 replay-safe local-serving wrap-up.
- Updated `llm/replay.py` and `llm_replay` flow so replay preserves richer serving identity when present, tolerates endpoint/path drift, rejects hard model or checkpoint drift, and still accepts legacy bundles that only carry the old `baseline_fallback` lane-source value.
- Added committed operator-facing local configs in `configs/systems/al_cu_fe_llm_local.yaml` and `configs/systems/sc_zn_llm_local.yaml`, both using placeholder `http://localhost:8000` OpenAI-compatible endpoints and explicit lane definitions without implying that `mdisc` starts the server.
- Extended `tests/test_llm_replay_core.py` for local replay drift classification, committed-config validation, and legacy-bundle compatibility, and tightened `tests/test_cli.py` so the legacy no-lane `llm-generate` path still proves the standard summary shape.
- Updated `developers-docs/configuration-reference.md`, `developers-docs/llm-integration.md`, and `developers-docs/pipeline-stages.md` with the Phase 19 local-serving contract, including `--model-lane`, explicit fallback rules, recorded serving identity, and the note that specialized-materials lanes are not assumed Zomic-native in `v1.2`.
- Focused verification passed with `38 passed` across `tests/test_llm_replay_core.py`, `tests/test_llm_runtime.py`, `tests/test_llm_generate_cli.py`, and `tests/test_cli.py`.
- 01:07 EDT — Implemented the Phase 20 Plan 01 specialized evaluation contract foundation.
- Added additive `llm_evaluate.model_lane` handling in `common/schema.py`, extended evaluation artifacts with requested/resolved lane lineage plus typed `serving_identity`, and rebuilt `LlmEvaluateSummary` typing without breaking legacy manifests.
- Added `llm/specialist.py` with a thin structure-oriented specialized payload seam, then taught `llm/evaluate.py` to reuse the shared serving-lane resolver and readiness validation path from Phase 19 before writing enriched `llm_assessment` provenance.
- Extended `tests/test_llm_evaluate_schema.py` to cover lane config normalization, legacy artifact reads, specialized prompt routing, and backend-default preservation; focused verification passed with `5 passed`.
- 01:12 EDT — Implemented the Phase 20 Plan 02 operator and comparison compatibility layer.
- Added `mdisc llm-evaluate --model-lane ...`, made `configs/systems/al_cu_fe_llm_local.yaml` declare `llm_evaluate.model_lane: specialized_materials`, and proved explicit configured-fallback vs hard-failure behavior fully offline in `tests/test_llm_evaluate_cli.py`.
- Extended `llm/compare.py` and `llm/schema.py` so campaign outcome snapshots now keep generation-lane identity distinct from additive evaluation-lane identity sourced from `llm_assessment` provenance, and updated compare CLI output to surface that distinction clearly for operators.
- Extended compare/report regressions so specialized evaluation serving identity now remains visible through compare snapshots, compare CLI summaries, and report evidence without creating a specialized-only artifact path; focused verification passed with `4 passed` for `tests/test_llm_evaluate_cli.py` plus `32 passed` across compare/report/replay coverage.

### 2026-04-04

- 13:43 EDT — Closed Phase 12 Plan 03 with the full offline operator workflow and docs pass.
- Added an end-to-end regression in `tests/test_real_mode_pipeline.py` for `llm-suggest -> llm-approve -> llm-launch -> llm-replay -> llm-compare`, extended `tests/test_llm_campaign_lineage.py` so replay lineage fields stay normalized, and documented strict replay plus comparison baselines in `RUNBOOK.md`, `developers-docs/llm-integration.md`, and `developers-docs/pipeline-stages.md`.
- Focused Phase 12 verification passed with `4 passed, 7 deselected`, and the full `materials-discovery` suite closed green at `374 passed, 3 skipped, 1 warning`.
- 13:35 EDT — Implemented the Phase 12 Plan 02 replay and compare CLI layer.
- Added strict `mdisc llm-replay --launch-summary ...` and `mdisc llm-compare --launch-summary ...`, updated `llm-generate` so replay lineage flows additively into run manifests and candidate provenance, and kept replay outputs on deterministic standard-root candidate paths.
- Added `tests/test_llm_replay_cli.py`, `tests/test_llm_compare_cli.py`, and extended `tests/test_cli.py`; focused verification passed with `17 passed`.
- 13:29 EDT — Implemented the Phase 12 Plan 01 replay/comparison contract foundation.
- Added `llm/replay.py` and `llm/compare.py`, extended `llm/schema.py` with replay lineage plus typed `LlmCampaignOutcomeSnapshot` and `LlmCampaignComparisonResult` models, added deterministic campaign comparison storage helpers, and exported the new replay/compare surface from `materials_discovery.llm`.
- Added `tests/test_llm_replay_core.py` and `tests/test_llm_compare_core.py`; focused verification passed with `10 passed`.
- 12:47 EDT — Completed the Phase 11 Plan 03 lineage propagation and launch-continuation docs pass.
- Normalized additive `llm_campaign` lineage once, wrote it into launched `llm_generate` manifests, reused it across `screen`, `hifi-validate`, `hifi-rank`, `active-learn`, `report`, and the pipeline manifest, and documented the `llm-launch` wrapper plus manual continuation flow in the developer docs.
- Focused verification passed with `16 passed` across `tests/test_llm_campaign_lineage.py` and `tests/test_report.py`, plus `1 passed` for the offline `tests/test_real_mode_pipeline.py -k "campaign or llm_launch"` slice.
- 12:47 EDT — Started Phase 11 Plan 03 in TDD RED mode by adding downstream lineage and mock launch continuation regressions.
- Added `tests/test_llm_campaign_lineage.py`, extended `tests/test_report.py`, and extended `tests/test_real_mode_pipeline.py` to lock campaign-lineage propagation into downstream manifests plus the offline `llm-launch -> screen` continuation lane.
- Open item: normalize campaign lineage once, thread it into downstream manifests and the pipeline manifest, then update docs for the Phase 11 manual continuation flow.
- 12:47 EDT — Implemented the Phase 11 Plan 02 Task 2 `llm-launch` CLI bridge.
- Added `mdisc llm-launch --campaign-spec ...`, config-hash drift validation with pinned/current hash detail, early `launch_id` visibility, `resolved_launch.json` / `launch_summary.json` writing, and additive execution through the existing `generate_llm_candidates()` path.
- Focused verification passed with `13 passed` across `tests/test_llm_launch_cli.py` and `tests/test_cli.py`.
- 12:52 EDT — Started Phase 11 Plan 02 Task 2 in TDD RED mode by adding `tests/test_llm_launch_cli.py` and a shared `tests/test_cli.py` smoke case.
- The new failing coverage locks successful `llm-launch` artifact writing, config-drift failure messaging, and the requirement that generation must not start when the pinned config hash no longer matches.
- Open item: add the `llm-launch` command, write resolved/summary artifacts, and preserve partial-failure auditability without reusing `llm-approve`.
- 12:47 EDT — Implemented the Phase 11 Plan 02 Task 1 additive `llm-generate` bridge.
- Threaded prompt instruction deltas through `build_generation_prompt()` and `LlmGenerationRequest`, added campaign-aware fields to `LlmRunManifest`, and recorded additive `llm_campaign` provenance on launched candidates.
- Also widened the run hash so campaign launches with different overlays do not silently collide with otherwise identical manual generation runs.
- 12:42 EDT — Started Phase 11 Plan 02 Task 1 in TDD RED mode by extending `tests/test_llm_generate_core.py`.
- The new failing coverage locks prompt instruction-delta placement plus campaign-aware run-manifest and candidate-provenance fields before changing the existing `llm-generate` runtime.
- Open item: thread additive prompt/campaign launch metadata through `llm_generate` without disturbing the manual path.
- 13:12 EDT — Implemented the Phase 11 Plan 01 Task 2 launch resolution layer.
- Added `materials_discovery.llm.launch` with deterministic action ordering, configured-lane vs baseline-fallback resolution, heuristic composition-window shrinking, and eval-set-backed seed materialization into the campaign launch directory.
- Exported `resolve_campaign_launch()`, `resolve_campaign_model_lane()`, and `materialize_campaign_seed()` from `materials_discovery.llm` so later CLI and runtime work can use a single additive launch overlay surface.
- 12:30 EDT — Started Phase 11 Plan 01 Task 2 in TDD RED mode by adding `tests/test_llm_launch_core.py`.
- The new failing coverage locks deterministic lane selection and fallback, ordered prompt deltas, exact vs heuristic composition overlays, seed reuse/materialization, and the requirement that source `SystemConfig` objects stay unmodified.
- Open item: implement `materials_discovery.llm.launch`, export its helpers, and keep all resolution logic file-backed and additive over the existing `llm-generate` path.
- 12:27 EDT — Started Phase 11 Plan 01 Task 1 in TDD RED mode by adding `tests/test_llm_launch_schema.py`.
- The new failing coverage locks the additive `model_lanes` config seam, typed launch-summary/resolved-launch artifacts, and deterministic `data/llm_campaigns/{campaign_id}/launches/{launch_id}/` path helpers before touching the implementation.
- Open item: add the lane-aware schema fields, launch artifact models, storage helpers, and exports without breaking legacy `llm-generate` configs.
- 12:30 EDT — Implemented the Phase 11 Plan 01 Task 1 launch contracts and storage helpers.
- Added `LlmModelLaneConfig` plus `llm_generate.model_lanes`, introduced `CampaignLaunchStatus`, `LlmCampaignResolvedLaunch`, and `LlmCampaignLaunchSummary`, and wired deterministic launch helper paths under `data/llm_campaigns/{campaign_id}/launches/{launch_id}/`.
- Exported the new launch models and storage helpers from `materials_discovery.llm` while keeping legacy manual `llm-generate` configs valid when `model_lanes` is absent.
- 01:28 EDT — Started Phase 10 Plan 01 Task 1 in TDD RED mode by adding `tests/test_llm_campaign_schema.py`.
- The new failing coverage locks the intended governance contract for typed campaign actions, system-scoped proposals, separate approval artifacts, and self-contained campaign specs before touching `llm/schema.py`.
- Open item: implement the additive Phase 10 schema models in `materials_discovery.llm.schema` and export them without disturbing the existing Phase 6-9 contracts.
- 01:29 EDT — Implemented the Phase 10 campaign governance schema in `materials_discovery.llm.schema` and exported the new models and constants from `materials_discovery.llm`.
- Added typed payloads for the three action families, proposal and suggestion contracts, separate approval artifacts, and self-contained campaign specs with pinned launch baselines and lineage.
- Validators now reject blank IDs and paths, require the payload that matches each action family, reject non-matching payloads, normalize evidence/failing-metric lists, and enforce `default_count >= 1` for launch baselines.
- 01:30 EDT — Started Phase 10 Plan 01 Task 2 in TDD RED mode by adding `tests/test_llm_campaign_storage.py`.
- The new failing storage tests lock the deterministic artifact layout for acceptance-pack-rooted suggestions, proposals, approvals, and dedicated `data/llm_campaigns/{campaign_id}/campaign_spec.json` outputs.
- Open item: add the new storage helpers to `materials_discovery.llm.storage`, reject blank artifact IDs, and export the helper surface from `materials_discovery.llm`.
- 01:31 EDT — Implemented the Phase 10 storage helpers in `materials_discovery.llm.storage` and exported them from `materials_discovery.llm`.
- Added deterministic helpers for `suggestions.json`, `proposals/{proposal_id}.json`, `approvals/{approval_id}.json`, and `data/llm_campaigns/{campaign_id}/campaign_spec.json`.
- Blank `pack_id`, `proposal_id`, `approval_id`, and `campaign_id` inputs now raise immediately so the storage layer cannot quietly point at malformed artifact roots.
- 01:42 EDT — Started Phase 10 Plan 02 Task 1 in TDD RED mode by adding `tests/test_llm_suggest_core.py`.
- The new failing coverage locks the acceptance-pack to typed-campaign-proposal mapping rules, deterministic action IDs, release-gate posture, specialized-materials routing, and summary path emission before touching the implementation.
- Open item: add `llm/campaigns.py`, migrate `llm/suggest.py` to the typed campaign bundle, and update in-repo callers away from the legacy `LlmSuggestion` contract.
- 01:47 EDT — Implemented the Phase 10 Plan 02 Task 1 typed suggestion mapping layer.
- Added `llm/campaigns.py` with deterministic system-scoped proposal IDs, stable per-proposal action IDs, heuristic-to-action-family mapping, and acceptance-pack to proposal-summary helpers.
- Migrated `llm/suggest.py` so it now builds `LlmCampaignSuggestion`, writes sibling `proposals/{proposal_id}.json` artifacts under the acceptance-pack root, and keeps directory creation/writing out of the CLI.
- Updated `llm/__init__.py` exports and `tests/test_llm_acceptance_benchmarks.py` so in-repo callers move with the contract instead of silently expecting the legacy `LlmSuggestion` surface.
- 01:48 EDT — Started Phase 10 Plan 02 Task 2 in TDD RED mode by adding `tests/test_llm_suggest_cli.py` and updating the shared `tests/test_cli.py` llm-suggest coverage.
- The new failing CLI tests lock the typed stdout contract, default `suggestions.json` writing, sibling `proposals/{proposal_id}.json` artifact creation, and the requirement that shared CLI callers move with the Wave 2 migration instead of expecting legacy plain-language items.
- Open item: update `cli.py` to call the new typed suggestion writer and keep `mdisc llm-suggest` dry-run with clear exit-2 handling on invalid input.
- 01:50 EDT — Implemented the Phase 10 Plan 02 Task 2 CLI migration.
- `cli.py` now sends `mdisc llm-suggest` through the typed suggestion writer, preserves dry-run behavior, and prints the persisted campaign-bundle JSON instead of the legacy plain-language suggestion surface.
- Added `tests/test_llm_suggest_cli.py`, updated the shared `tests/test_cli.py` contract, and confirmed the focused CLI slice passes with proposal artifacts written under the acceptance-pack root.
- 10:56 EDT — Started Phase 10 Plan 03 in TDD RED mode by adding `tests/test_llm_campaign_spec.py`, `tests/test_llm_approve_cli.py`, and a new shared `test_cli.py` smoke case for `llm-approve`.
- The new failing coverage locked deterministic approval IDs, campaign-spec lineage, approved-vs-rejected behavior, and the requirement that Phase 10 approval must not call `llm-generate` or `llm-evaluate`.
- 10:56 EDT — Implemented the Phase 10 Plan 03 governance boundary.
- Added `create_campaign_approval()` and `materialize_campaign_spec()` to `llm/campaigns.py`, plus artifact-root derivation in `llm/storage.py` so approvals stay under the acceptance-pack root and campaign specs land under `data/llm_campaigns/{campaign_id}/`.
- Added `mdisc llm-approve` to `cli.py`; approved decisions now require `--config`, rejected decisions stop at the approval artifact, and the command emits a JSON summary without launching any downstream run.
- Refreshed `developers-docs/llm-integration.md` and `developers-docs/pipeline-stages.md` to document the new dry-run vs approval/spec boundary.
- Re-verified Phase 10 locally with focused tests plus the full suite: `332 passed, 3 skipped, 1 warning`.
