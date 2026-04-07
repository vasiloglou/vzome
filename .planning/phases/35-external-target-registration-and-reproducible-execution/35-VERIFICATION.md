---
phase: 35-external-target-registration-and-reproducible-execution
verified: 2026-04-07T07:26:10Z
status: passed
score: 3/3 must-haves verified
---

# Phase 35: External Target Registration and Reproducible Execution Verification Report

**Phase Goal:** Operators can register each curated downloaded external materials LLM as an immutable benchmark target with pinned revision or snapshot identity, compatible translation families, runtime settings, smoke checks, and reproducibility-grade environment lineage before benchmark execution.
**Verified:** 2026-04-07T07:26:10Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | An operator can register one curated external benchmark target from a file-backed spec and receive one immutable registration artifact with conflict-detecting fingerprinting. | ✓ VERIFIED | `materials-discovery/src/materials_discovery/llm/schema.py:950-1216` defines the typed external-target registration, environment, smoke, and summary contracts; `materials-discovery/src/materials_discovery/llm/external_targets.py:128-216` loads YAML specs, normalizes snapshot paths, fingerprints immutable facts, rejects conflicting `model_id` reuse, and writes `registration.json`; `materials-discovery/src/materials_discovery/cli.py:961-971` exposes `mdisc llm-register-external-target`; focused tests in `materials-discovery/tests/test_llm_external_target_registry.py` and `materials-discovery/tests/test_llm_external_target_cli.py:60-84` passed as part of the phase-wide `41 passed in 0.59s` run. |
| 2 | An operator can inspect a registered target and see immutable identity, environment lineage, and the latest smoke result before Phase 36 benchmark execution begins. | ✓ VERIFIED | `materials-discovery/src/materials_discovery/llm/external_targets.py:219-288` persists `environment.json` and `smoke_check.json`; `materials-discovery/src/materials_discovery/cli.py:974-1054` prints immutable identity plus environment/smoke artifact traces and emits typed smoke JSON; CLI coverage in `materials-discovery/tests/test_llm_external_target_cli.py:87-164` proves register → smoke → inspect behavior, and a direct behavioral spot-check returned `register_exit=0`, `smoke_exit=0`, `inspect_exit=0` with fingerprint, environment artifact, and passed smoke status present in inspect output. |
| 3 | The shipped docs and example configs make the Phase 35 boundary explicit: external target registration and smoke are in scope now, while comparative benchmark runs and scorecards remain Phase 36 work. | ✓ VERIFIED | Example specs live at `materials-discovery/configs/llm/al_cu_fe_external_cif_target.yaml:1-18` and `materials-discovery/configs/llm/al_cu_fe_external_material_string_target.yaml:1-18`; the operator runbook at `materials-discovery/developers-docs/llm-external-target-runbook.md:1-167` documents required inputs, commands, artifact layout, and the deferred Phase 36 boundary; the configuration reference and docs index expose the workflow at `materials-discovery/developers-docs/configuration-reference.md:254-303` and `materials-discovery/developers-docs/index.md:34-43`; the command reference and help discoverability are locked by `materials-discovery/developers-docs/pipeline-stages.md:1335-1459`, `materials-discovery/tests/test_cli.py:290-298`, and `uv run mdisc --help`, which listed all three new commands. |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/schema.py` | Typed external-target spec, registration, environment, smoke, and summary contracts | ✓ VERIFIED | External-target contract models are present at `:950-1216` with typed runner/status vocabularies, required-string validation, package-version normalization, and latency/gpu guards. |
| `materials-discovery/src/materials_discovery/llm/external_targets.py` | Spec loader, registration core, environment capture, and smoke persistence | ✓ VERIFIED | Implements spec loading, path normalization, fingerprint conflict detection, registration persistence, environment capture, and fail-closed smoke persistence at `:128-288`. |
| `materials-discovery/src/materials_discovery/cli.py` | Operator register, inspect, and smoke commands | ✓ VERIFIED | `llm-register-external-target`, `llm-inspect-external-target`, and `llm-smoke-external-target` are implemented at `:961-1054` with repo-standard exit-code-2 error handling. |
| `materials-discovery/configs/llm/al_cu_fe_external_cif_target.yaml` | Runnable contract-shaped CIF-oriented example spec | ✓ VERIFIED | Declares `model_id`, target family, runner, provider/model, pinned revisions, snapshot lineage, prompt contract, parser key, and placeholder note at `:1-18`. |
| `materials-discovery/configs/llm/al_cu_fe_external_material_string_target.yaml` | Runnable contract-shaped material-string example spec | ✓ VERIFIED | Declares the parallel material-string-oriented contract with explicit target-family and parser fields at `:1-18`. |
| `materials-discovery/developers-docs/llm-external-target-runbook.md` | Operator workflow and artifact-layout runbook | ✓ VERIFIED | Documents register, inspect, smoke, artifact layout under `data/llm_external_models/{model_id}/`, and explicit Phase 36 deferrals at `:1-167`. |
| `materials-discovery/tests/test_llm_external_target_schema.py` | Contract and storage validation coverage | ✓ VERIFIED | Covered by the phase-wide external-target test slice, which passed `41` focused tests. |
| `materials-discovery/tests/test_llm_external_target_registry.py` | Registration, reload, environment, and smoke regression coverage | ✓ VERIFIED | Covered by the phase-wide external-target test slice, which passed `41` focused tests. |
| `materials-discovery/tests/test_llm_external_target_cli.py` | CLI workflow coverage | ✓ VERIFIED | Covers register JSON, inspect trace, smoke JSON, missing/invalid inputs, and help surface at `:60-260`. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/external_targets.py` | `materials-discovery/src/materials_discovery/llm/schema.py` | Loads typed specs and writes typed registration/environment/smoke artifacts | WIRED | Imports `LlmExternalTargetRegistrationSpec`, `LlmExternalTargetRegistration`, `LlmExternalTargetEnvironmentManifest`, and `LlmExternalTargetSmokeCheck`, then persists those models at `external_targets.py:19-30` and `:128-288`. |
| `materials-discovery/src/materials_discovery/llm/external_targets.py` | `materials-discovery/src/materials_discovery/llm/storage.py` | Persists registration, environment, and smoke files under deterministic paths | WIRED | Uses `llm_external_target_registration_path`, `llm_external_target_environment_path`, and `llm_external_target_smoke_path` at `external_targets.py:26-30`, `:175-177`, `:250-251`, and `:262-287`. |
| `materials-discovery/src/materials_discovery/cli.py` | `materials-discovery/src/materials_discovery/llm/external_targets.py` | Register, inspect, and smoke command entrypoints | WIRED | CLI commands call `register_external_target`, `load_registered_external_target`, and `smoke_external_target` directly at `cli.py:967`, `:980`, and `:1050`. |
| `materials-discovery/developers-docs/llm-external-target-runbook.md` | `materials-discovery/configs/llm/al_cu_fe_external_cif_target.yaml` | Operator example workflow | WIRED | The runbook points operators at the committed example specs and explains that snapshot paths and revisions must be replaced before live registration at `llm-external-target-runbook.md:40-57`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/external_targets.py` | `registration`, `environment`, `smoke` | Typed YAML spec plus local snapshot directory | Yes. The behavioral spot-check registered `verify_target`, wrote `registration.json`, wrote `environment.json`, and returned a passed smoke result with `fingerprint=25b7958bf30fb502`. | ✓ FLOWING |
| `materials-discovery/src/materials_discovery/cli.py` | inspect trace lines | Registration/environment/smoke artifacts under `data/llm_external_models/{model_id}/` | Yes. Inspect output included `Fingerprint:`, `Environment artifact:`, and `Smoke status: passed` during the direct CLI round-trip verification. | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Full external-target phase slice stays green | `cd materials-discovery && uv run pytest tests/test_llm_external_target_schema.py tests/test_llm_external_target_registry.py tests/test_llm_external_target_cli.py tests/test_cli.py -q` | `41 passed in 0.59s` | ✓ PASS |
| Root CLI help exposes the new workflow | `cd materials-discovery && uv run mdisc --help \| rg "llm-(register|inspect|smoke)-external-target"` | Help output listed all three new commands with descriptions. | ✓ PASS |
| One real register → smoke → inspect round-trip works in a temporary workspace | `cd materials-discovery && uv run python - <<'PY' ... CliRunner register/smoke/inspect spot-check ... PY` | Returned `register_exit=0`, `smoke_exit=0`, `inspect_exit=0`, `smoke_status="passed"`, and inspect output contained fingerprint plus environment/smoke artifact traces. | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| `OPS-17` | `35-01`, `35-02`, `35-03` | Operator can register each curated downloaded external materials LLM as an immutable benchmark target with pinned revision or snapshot identity, compatible translation families, runtime settings, smoke checks, and reproducibility-grade environment lineage before benchmark execution. | ✓ SATISFIED | Typed contracts in `schema.py`, deterministic registration/environment/smoke persistence in `external_targets.py`, CLI surface in `cli.py`, example specs, runbook/docs updates, and the `41 passed` phase-wide external-target suite satisfy the requirement end to end. |

Orphaned requirements for Phase 35: none.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| Phase 35 implementation set | n/a | No TODO/FIXME/stub markers or hollow command wrappers found in the phase files inspected during verification. | Info | No blocker anti-patterns detected. |

### Human Verification Required

None required for phase-goal verification. The delivered surface is CLI-first and file-backed, and the critical operator behaviors were verified through automated tests plus direct CLI spot-checks.

### Gaps Summary

No gaps found. Phase 35 delivers the typed contract, deterministic artifact layout, immutable registration core, reproducibility lineage capture, smoke persistence, operator CLI surface, committed example specs, and documentation required by the roadmap goal and `OPS-17`.

---

_Verified: 2026-04-07T07:26:10Z_
_Verifier: Codex (manual verifier path aligned to gsd-verifier expectations)_
