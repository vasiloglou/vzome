# Phase 6: Zomic Training Corpus Pipeline - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the data foundation for the LLM workstream by creating deterministic
conversion and corpus-building infrastructure for Zomic-centered training data.
This phase should produce:

- a `record2zomic` path for pipeline-generated `CandidateRecord` data
- a `cif2zomic` path for open approximant structures where feasible
- a corpus builder that combines repo-native Zomic, converted records, converted
  open structures, and existing vZome/Zomic exports
- explicit corpus QA and release-tier rules

This phase does not train models, add `llm-generate`, or add live inference.
Those belong to later phases.

</domain>

<decisions>
## Implementation Decisions

### Corpus source coverage
- **D-01:** Phase 6 must satisfy `LLM-01` as a corpus-construction phase, not a
  model-training or inference phase.
- **D-02:** Required v1 corpus sources are:
  - repo-native Zomic scripts from `core/src/regression/files/Zomic/`
  - repo-native Zomic part definitions from
    `core/src/main/resources/com/vzome/core/parts/`
  - materials-authored Zomic designs from `materials-discovery/designs/zomic/`
  - pipeline-generated candidates converted through `record2zomic`
  - open approximant conversions from `HYPOD-X` and `COD`
  - existing vZome/Zomic export artifacts already produced in
    `materials-discovery/data/prototypes/generated/`
  - `PyQCstrc`-derived projections as a required v1 input family
- **D-03:** Licensed or restricted sources such as `ICSD` remain explicitly out
  of required v1 scope, even if accessible later.
- **D-04:** Phase 6 should prefer sources that are already staged or reproducibly
  derivable inside the current repo and data-lake layout before depending on new
  one-off acquisition flows.

### Training example contract
- **D-05:** Phase 6 should ship one shared corpus builder that emits two related
  corpora from the same source inventory:
  - a syntax-first Zomic corpus focused on language validity and structure
  - a materials-conditioned corpus carrying system, composition, and available
    property/context metadata
- **D-06:** Both corpora should be JSONL-based, file-backed artifacts with
  manifests and deterministic lineage, following the same artifact posture as
  earlier phases.
- **D-07:** The syntax-first corpus should be allowed to include examples that
  are valuable for Zomic grammar and construction patterns even when they are
  not crystallographic materials examples.
- **D-08:** The materials-conditioned corpus should preserve enough metadata to
  support later composition-conditioned training and evaluation without forcing
  Phase 6 to define the final inference prompt format.

### Conversion fidelity policy
- **D-09:** `record2zomic` and `cif2zomic` must prioritize deterministic,
  auditable, reproducible conversion over compact or hand-pretty Zomic output.
- **D-10:** Approximate mappings are allowed in v1, but every converted example
  must carry explicit fidelity/provenance metadata so downstream work can
  distinguish exact, anchored, and heuristic conversions.
- **D-11:** The conversion pipeline should preserve enough intermediate evidence
  to explain how a training example was derived, rather than collapsing all
  examples into an opaque final script.
- **D-12:** Phase 6 should avoid a permissive “parse/compile is enough” posture;
  conversion confidence must remain visible as part of the corpus contract.

### Corpus QA and release tiers
- **D-13:** Phase 6 should use tiered corpus releases rather than a single
  undifferentiated dataset.
- **D-14:** `gold` examples must satisfy all of:
  - parseable Zomic
  - successful vZome compile path
  - valid/consistent labels
  - collision-safe geometry under the chosen threshold
  - higher-confidence conversion fidelity
- **D-15:** `silver` examples must still satisfy parse + compile + basic QA, but
  may include lower-confidence mappings or weaker conversion fidelity than
  `gold`.
- **D-16:** QA output should make it easy to answer:
  - which examples failed parse vs compile vs collision checks
  - which examples were downgraded from `gold` to `silver`
  - which source family or converter produced a given issue

### Project-level inheritance from earlier phases
- **D-17:** The no-DFT boundary remains explicit. Phase 6 may reuse pipeline,
  benchmark, and source artifacts, but it must not require DFT or redefine the
  current physically grounded no-DFT validation stack.
- **D-18:** Phase 6 should build on the existing file-backed lakehouse and
  manifest patterns rather than introducing a database or separate storage
  service for corpora.
- **D-19:** Phase 6 should respect the long-term architecture where Zomic is the
  core generation representation and later LLM stages reuse the existing Zomic
  bridge plus downstream pipeline.

### the agent's Discretion
- The exact package split between corpus builders, converters, and QA helpers
- The exact artifact directory names and manifest schema, so long as they follow
  existing file-backed conventions and preserve deterministic lineage
- The exact fidelity-tier vocabulary beyond the locked `gold` / `silver` release
  distinction
- The exact conversion algorithm details for `record2zomic`, `cif2zomic`, and
  `PyQCstrc` import, provided they preserve auditability and explicit fidelity
  tagging

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Program controls
- `.planning/PROJECT.md` — overall program framing, core value, and the rule
  that LLM work should reinforce rather than outrun the trusted data and no-DFT
  pipeline
- `.planning/ROADMAP.md` — Phase 6 goal, deliverables, and the sequencing into
  later LLM inference/evaluation phases
- `.planning/REQUIREMENTS.md` — `LLM-01` and the neighboring `LLM-02` to
  `LLM-05` boundaries that Phase 6 should not prematurely absorb
- `.planning/STATE.md` — current milestone state and recent inherited decisions

### Prior-phase authority
- `.planning/phases/04-reference-aware-no-dft-materials-discovery-v1/04-CONTEXT.md`
  — locked reference-pack, benchmark-pack, and benchmark-system decisions
- `.planning/phases/05-candidate-reference-data-lake-and-analysis-layer/05-CONTEXT.md`
  — lakehouse/catalog/runbook decisions and the current artifact-discovery
  posture
- `.planning/phases/03-reference-phase-integration-with-current-pipeline/03-CONTEXT.md`
  — source-registry ingest bridge, processed reference-phase projection, and
  offline deterministic testing rules
- `.planning/phases/02-ingestion-platform-mvp/02-CONTEXT.md` — source adapter
  set and canonical raw-source staging posture
- `.planning/phases/01-program-charter-and-canonical-data-model/01-CONTEXT.md`
  — original raw-source contract and provenance expectations that still matter
  for converted structure inputs

### LLM and Zomic design docs
- `materials-discovery/developers-docs/llm-integration.md` — planned LLM
  architecture, later `llm-generate` / `llm-evaluate` boundaries, and corpus
  strategy overview
- `materials-discovery/developers-docs/zomic-llm-data-plan.md` — detailed
  source inventory, conversion concepts, augmentation ideas, and corpus
  preparation sequence that directly motivates Phase 6
- `materials-discovery/developers-docs/llm-quasicrystal-landscape.md` — why
  Zomic is the representation choice for quasicrystal LLM work
- `materials-discovery/developers-docs/zomic-design-workflow.md` — current
  Zomic authoring path, label/orbit semantics, and the bridge from Zomic text to
  pipeline-ready prototype assets

### Existing subsystem docs
- `materials-discovery/README.md` — current operator entrypoints and the shipped
  Zomic-backed example flows
- `materials-discovery/REAL_MODE_EXECUTION_PLAN.md` — current hardening posture
  and the expectation that new work stays compatible with the existing
  reproducible workflow
- `materials-discovery/developers-docs/architecture.md` — current package
  boundaries and the reserved long-term `llm/` package location
- `materials-discovery/developers-docs/pipeline-stages.md` — implemented stage
  contracts plus the planned `llm-generate` / `llm-evaluate` interfaces that
  Phase 6 should prepare for, not implement
- `materials-discovery/developers-docs/data-schema-reference.md` — current
  schema conventions, `zomic_design` config seam, and persisted record patterns
- `materials-discovery/developers-docs/configuration-reference.md` — current
  config contracts and Zomic design integration
- `materials-discovery/developers-docs/reference-aware-benchmarks.md` — current
  benchmark/reference-pack usage and the preserved Zomic dependency in `Sc-Zn`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`:
  existing vZome/Gradle export seam, labeled-site handling, orbit grouping, and
  anchor-fit logic that later corpus conversion can reuse or mirror
- `materials-discovery/src/materials_discovery/generator/candidate_factory.py`:
  current `CandidateRecord` construction path and provenance patterns
- `materials-discovery/src/materials_discovery/common/schema.py`: existing
  `CandidateRecord`, `SiteRecord`, `QPhiCoord`, `ZomicDesignConfig`,
  `IngestionConfig`, and manifest-summary contracts
- `materials-discovery/src/materials_discovery/data_sources/schema.py`:
  canonical raw-source staging models and manifest/QA patterns that can inform
  corpus-manifest design
- `materials-discovery/src/materials_discovery/data_sources/reference_packs.py`:
  deterministic pack assembly, lineage, fingerprinting, and cached artifact
  reuse patterns
- `materials-discovery/src/materials_discovery/cli.py`: the current CLI home for
  stage orchestration, JSON summary output, and future subcommand integration

### Established Patterns
- File-backed JSON/JSONL artifacts under `materials-discovery/data/`
- Deterministic manifests and sidecar calibration/QA outputs
- Pydantic contracts in `common/schema.py` and stage/domain-specific schema
  modules
- Offline deterministic tests using fixtures, staged payloads, and monkeypatch
  seams instead of live-network dependencies
- Zomic remains an existing implemented bridge path, but there is not yet an
  implemented `materials_discovery/llm/` runtime package

### Integration Points
- Existing candidate artifacts:
  `materials-discovery/data/candidates/*.jsonl`
- Existing staged source/reference-pack artifacts:
  `materials-discovery/data/external/sources/` and
  `materials-discovery/data/external/reference_packs/`
- Existing Zomic and prototype artifacts:
  `materials-discovery/designs/zomic/` and
  `materials-discovery/data/prototypes/generated/`
- Existing tests that should anchor Phase 6 work:
  `materials-discovery/tests/test_zomic_bridge.py`,
  `materials-discovery/tests/test_reference_packs.py`,
  `materials-discovery/tests/test_data_source_projection.py`,
  `materials-discovery/tests/test_cli.py`

</code_context>

<specifics>
## Specific Ideas

- Treat repo-native Zomic scripts as the syntax/training grammar seed set, and
  treat `materials-discovery/designs/zomic/*.zomic` as the higher-value
  materials-specific exemplars.
- Reuse already-generated artifacts before inventing new acquisition flows:
  candidate JSONL, staged source snapshots, reference packs, and generated
  prototype exports should all be first-class corpus inputs.
- Keep approximate conversion outputs useful by tiering them rather than
  discarding them immediately or silently mixing them into one undifferentiated
  corpus.
- Use `PyQCstrc` as a required v1 source family because it is the best explicit
  bridge to true QC geometry rather than only periodic approximants.

</specifics>

<deferred>
## Deferred Ideas

- Licensed or access-restricted sources such as `ICSD` — later phase or
  partner-only path
- Model fine-tuning choices, tokenizer extension details, and training
  infrastructure sizing — later LLM phases
- `mdisc llm-generate`, `mdisc llm-evaluate`, and live/provider-backed inference
  work — later phases
- A permissive “accept anything that parses and compiles” corpus posture — ruled
  out for this phase in favor of explicit fidelity tiers

</deferred>

---

*Phase: 06-zomic-training-corpus-pipeline*
*Context gathered: 2026-04-03*
