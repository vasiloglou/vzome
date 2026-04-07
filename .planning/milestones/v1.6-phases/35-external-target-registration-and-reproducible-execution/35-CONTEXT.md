# Phase 35: External Target Registration and Reproducible Execution - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning
**Mode:** Autonomous defaults from roadmap + milestone research

<domain>
## Phase Boundary

Phase 35 should turn the frozen translated benchmark pack from Phase 34 into a
benchmark-ready runtime boundary for curated downloaded external materials
models. The phase should deliver:

- immutable, file-backed registration artifacts for a small curated set of
  external benchmark targets
- deterministic target resolution back to the same local snapshot and runtime
  contract on later runs
- explicit smoke-check and environment-lineage artifacts that operators can
  inspect before Phase 36 benchmark execution
- a narrow benchmark-only execution seam for these external targets without
  polluting the normal `SystemConfig` or `llm-generate` path

This phase should not build a general model zoo, downloader, background serving
platform, or the full comparative benchmark/scorecard workflow. It is the
reproducibility gate before Phase 36, not the comparison phase itself.

</domain>

<decisions>
## Implementation Decisions

### Scope and artifact posture

- **D-01:** Keep external target registration benchmark-specific and
  intentionally small. Support only a curated handful of already-downloaded
  targets instead of a generic registry or marketplace.
- **D-02:** Use a dedicated artifact family for external targets under
  `materials-discovery/data/llm_external_models/` rather than reusing checkpoint
  or campaign directories.
- **D-03:** Internal controls remain on the shipped promoted/pinned checkpoint
  machinery. Phase 35 should register only external targets and prepare them
  for later comparison.

### Registration contract

- **D-04:** External targets should mirror the checkpoint-registration
  discipline: immutable registration facts first, later execution from those
  facts. The MVP should not introduce lifecycle promotion or retirement for
  external models.
- **D-05:** Each registration must capture benchmark-relevant identity and
  compatibility explicitly: stable target ID, model family or label, supported
  translation target families, runner or adapter choice, model or tokenizer
  revision, local snapshot location, prompt or parser contract hooks, and
  operator notes.
- **D-06:** Registration must fail closed on fingerprint conflicts so the same
  target ID cannot silently drift to different model bits or runtime facts.

### Reproducibility and smoke posture

- **D-07:** Reproducibility artifacts must be first-class files, not only CLI
  stdout. Operators should be able to inspect snapshot lineage, package or
  runtime versions, hardware envelope, tokenizer identity, and smoke status
  before a benchmark run starts.
- **D-08:** Environment capture should fail closed when required lineage is
  missing. A registered external target is not benchmark-ready if its snapshot
  or runtime contract cannot be reconstructed later.
- **D-09:** Smoke checks should be explicit and separate from decision-grade
  benchmark runs. Phase 35 proves target readiness and reproducibility, not
  comparative quality.

### Runtime seam posture

- **D-10:** Keep the external runtime surface benchmark-only and additive. Do
  not push downloaded external-model configuration into `SystemConfig`.
- **D-11:** Prefer one repo-owned, reproducible local-snapshot execution seam
  over bespoke upstream project scripts. The phase may use thin fixture or demo
  runners for committed examples, but the contract must model real local
  snapshot-backed execution honestly.
- **D-12:** Treat prompt-template and parser selection as explicit contract
  fields so later Phase 36 results can explain which rendering path was used
  for each external target family.

### Example and documentation posture

- **D-13:** Ship committed example specs and docs that exercise the registration
  and inspect flow without requiring private model weights in the repo. Fixture
  snapshots or manifests are acceptable for the example surface as long as the
  real contract still points at explicit local snapshot facts.
- **D-14:** Keep the operator surface CLI-first and file-backed, with the same
  early validation and exit-code-2 posture used by translation bundles,
  checkpoint registration, and serving benchmarks.

### the agent's Discretion

- Exact schema field names as long as the contract stays typed, immutable, and
  benchmark-oriented
- Whether smoke checks persist inside the registration artifact family or a
  closely related benchmark-runtime subdirectory
- The minimal example target shortlist, as long as it stays curated and
  representation-aware

</decisions>

<specifics>
## Specific Ideas

- Mirror the checkpoint workflow shape: `--spec` driven registration, typed
  JSON artifact output, deterministic storage helpers, and focused CLI tests.
- Use one CIF-oriented example target and one CrystalTextLLM-style
  material-string example target so the registration contract stays honest
  about target-family compatibility.
- Capture enough environment metadata for later benchmark trust: Python,
  package versions, hardware visibility, snapshot path, and hashable model or
  tokenizer lineage.
- Keep any committed demo surface lightweight and repo-backed; do not require
  shipping actual third-party model weights with the repository.

</specifics>

<canonical_refs>
## Canonical References

### Milestone scope
- `.planning/ROADMAP.md` — Phase 35 goal, requirement mapping, and success criteria
- `.planning/REQUIREMENTS.md` — `OPS-17` benchmark-ready registration requirement
- `.planning/STATE.md` — Current milestone position and inherited decisions
- `.planning/research/FEATURES.md` — benchmark-first scope and anti-features
- `.planning/research/SUMMARY.md` — Phase 35 rationale and research flags
- `.planning/research/STACK.md` — recommended runner and environment-capture posture
- `.planning/research/ARCHITECTURE.md` — external registration and runtime seam boundaries
- `.planning/research/PITFALLS.md` — reproducibility, scope-control, and architecture-drift risks

### Existing repo patterns
- `materials-discovery/src/materials_discovery/llm/schema.py` — checkpoint, serving-identity, and translated-benchmark schema patterns
- `materials-discovery/src/materials_discovery/llm/storage.py` — dedicated artifact-root helper conventions
- `materials-discovery/src/materials_discovery/llm/checkpoints.py` — immutable registration, fingerprinting, and lifecycle-enrollment precedent
- `materials-discovery/src/materials_discovery/cli.py` — CLI command style, validation posture, and JSON summary output
- `materials-discovery/developers-docs/pipeline-stages.md` — operator-facing command and artifact documentation style
- `materials-discovery/developers-docs/configuration-reference.md` — committed config contract surface and Phase 34/35 boundary note
- `materials-discovery/developers-docs/llm-translated-benchmark-runbook.md` — Phase 34 handoff boundary for later benchmark work

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials_discovery.llm.checkpoints` already shows the repo's preferred
  immutable-registration pattern, including spec loading, fingerprint conflict
  rejection, deterministic storage, and JSON summary return values.
- `materials_discovery.llm.storage` already isolates artifact families cleanly,
  including recent `llm_external_sets` helpers from Phase 34.
- `materials_discovery.llm.schema.LlmServingIdentity` already models the kind of
  runtime lineage that later benchmark artifacts will need to expose.

### Established Patterns
- New LLM workflow surfaces are typed first in `schema.py`, then wired through
- dedicated storage helpers, CLI commands, focused unit tests, and developer docs.
- Benchmark and checkpoint commands validate inputs early, fail with exit code 2
  on operator mistakes, and write machine-readable artifacts instead of relying
  on ad hoc notebooks or shell history.
- The repo favors explicit artifact families and immutable manifests over
  implicit conventions hidden in config or logs.

### Integration Points
- Phase 35 should build directly on the frozen translated benchmark handoff from
  `data/benchmarks/llm_external_sets/{benchmark_set_id}/`.
- Phase 36 will consume the registered external targets, so Phase 35 contracts
  need stable IDs, compatibility declarations, smoke artifacts, and environment
  lineage that later benchmark specs can reference without reinterpretation.

</code_context>

<deferred>
## Deferred Ideas

- Comparative benchmark execution and scorecards across external targets and
  internal controls
- Broad model-zoo support, model downloading, or long-lived serving management
- Automated follow-on decisions such as training, promotion, or campaign
  automation for winning external models

</deferred>

---

*Phase: 35-external-target-registration-and-reproducible-execution*
*Context gathered: 2026-04-07*
