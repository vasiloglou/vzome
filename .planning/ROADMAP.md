# Roadmap: Materials Design Program

**Milestone:** `v1.5`
**Focus:** Project 3 expansion - External Materials-LLM Translation Bridge MVP
**Numbering mode:** continue after `v1.4` (`Phase 31+`)

## Milestone Summary

This milestone extends the shipped `v1.4` checkpoint lifecycle workflow.

`v1.4` proved that the platform can:
- generate and evaluate candidates through a Zomic-native LLM workflow
- manage adapted checkpoint families with promoted-default and explicit-pin
  execution
- benchmark candidate checkpoints, preserve rollback baselines, and keep replay
  auditable

`v1.5` turns that internal Zomic-first workflow into an external
materials-LLM interoperability surface:
- compiled Zomic candidates can be translated into explicit downstream
  structure artifacts
- supported candidates can be exported as CIF for CIF-native materials models
- the same candidates can be formatted into model-oriented crystal/material
  string encodings for CrystalTextLLM- or CSLLM-style workflows
- representational loss stays explicit whenever QC-native Zomic cannot map
  cleanly into a periodic/material-string target

## Phase Roadmap

## Phase 31: Translation Contracts and Representation Loss Semantics

**Goal:** define the supported downstream representation targets and the typed
contract that explains when a Zomic candidate can be translated exactly,
approximately, or only lossily.

**Deliverables**

- additive translation models for deterministic structure-interoperability
  artifacts derived from compiled Zomic candidates
- explicit fidelity/loss metadata and diagnostics for unsupported or lossy
  target representations
- a target-format registry covering CIF and at least one
  crystal/material-string family
- regression fixtures that anchor the contract on real candidate records rather
  than notebook-only assumptions

**Primary requirements**

- `LLM-27`, `LLM-30`

**Success criteria**

1. A translated candidate has one auditable source of truth tying the export
   back to the original Zomic/candidate artifact.
2. Exact versus lossy translation is encoded in the artifact contract rather
   than implied by docs alone.
3. Unsupported target exports fail clearly before operators confuse them for
   native QC-safe structure representations.
4. The contract stays additive to the existing Zomic-first workflow instead of
   replacing it.

## Phase 32: CIF and Material-String Exporters

**Goal:** implement deterministic exporters that turn supported translated
candidates into concrete payloads external materials LLMs can ingest.

**Deliverables**

- candidate-to-CIF export for supported approximant/periodic translations
- at least one model-oriented crystal/material string formatter for
  CrystalTextLLM- or CSLLM-style downstream workflows
- shared normalization logic so CIF and material-string payloads come from the
  same translated candidate identity
- regression coverage for representative Al-Cu-Fe and Sc-Zn examples plus clear
  failure cases

**Primary requirements**

- `LLM-28`, `LLM-29`

**Success criteria**

1. The same translated candidate yields stable downstream text artifacts across
   repeated runs.
2. CIF and material-string outputs preserve composition, cell, and site intent
   as far as the target format allows.
3. Exporters document when they are emitting a periodic proxy rather than a
   QC-native exact representation.
4. External-format translation no longer depends on one-off notebooks or manual
   scripts.

## Phase 33: CLI, Benchmark Hooks, and Operator Docs

**Goal:** make the translation bridge operator-usable through the shipped CLI
and documentation surface.

**Deliverables**

- file-backed CLI workflow for writing and inspecting translation artifacts
- benchmark/eval-set hooks so exported payloads can be reused in later external
  model experiments
- runbook and developer-doc guidance for CIF versus material-string exports and
  the fidelity boundary between them
- manifests and provenance coverage that keep the translation workflow auditable

**Primary requirements**

- `OPS-15`, `OPS-16`

**Success criteria**

1. Operators can generate translation artifacts without dropping into custom
   Python or notebooks.
2. The docs explain which exports are safe periodic approximants, which are
   lossy, and when Zomic must remain the authoritative representation.
3. Translation artifacts are stored under the existing file-backed workflow with
   provenance and manifest coverage.
4. The milestone ends with a reusable interop layer, not just a prototype
   serializer.

## Scope Boundaries

- This milestone does **not** claim that CIF is a lossless target for true
  quasicrystal-native Zomic structures.
- This milestone does **not** add a full new serving/runtime stack for external
  downloadable models.
- This milestone does **not** replace Zomic as the platform's core generative
  representation.
- This milestone does **not** automate fine-tuning or checkpoint training jobs.

## Previous Milestones

- `v1.4` archive: `.planning/milestones/v1.4-ROADMAP.md`
- `v1.3` archive: `.planning/milestones/v1.3-ROADMAP.md`
- `v1.2` archive: `.planning/milestones/v1.2-ROADMAP.md`
- `v1.1` archive: `.planning/milestones/v1.1-ROADMAP.md`
- `v1.0` archive: `.planning/milestones/v1.0-ROADMAP.md`
