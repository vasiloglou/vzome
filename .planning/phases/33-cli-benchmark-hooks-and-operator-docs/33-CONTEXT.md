# Phase 33: CLI, Benchmark Hooks, and Operator Docs - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning
**Mode:** Autonomous defaults from roadmap + completed Phases 31-32

<domain>
## Phase Boundary

Phase 33 should turn the finished translation/export seam into an operator-usable
workflow. The phase should deliver:

- a shipped CLI surface for creating translation artifacts from file-backed
  candidate inputs
- machine-readable manifests/inventory so exported CIF and material-string
  payloads can be inspected and traced without ad hoc scripts
- additive hooks that make those exported payload sets reusable in later
  external benchmark or eval-set style experiments
- runbook/developer docs that explain format choice, provenance, and where
  representational loss remains unavoidable

This phase should not introduce a new external-model serving stack, redesign the
existing Zomic-first pipeline, or weaken the Phase 31/32 fidelity boundary just
because export now has a CLI.

</domain>

<decisions>
## Default Decisions

### CLI posture

- **D-01:** Translation should ship as a native `mdisc` CLI workflow, not as a
  notebook recipe or a one-off helper script.
- **D-02:** The CLI should stay file-backed and auditable: one export run
  produces raw payload files plus machine-readable metadata rather than only
  printing text to stdout.
- **D-03:** The CLI should preserve the existing repo style of deterministic
  outputs and exit-code-2 validation failures for operator mistakes.

### Artifact and provenance posture

- **D-04:** Raw exported payloads must remain target-compatible. Provenance,
  fidelity tier, loss reasons, and tracing data belong in manifest/inventory
  sidecars rather than being pushed into the material-string body.
- **D-05:** Translation exports should live under a dedicated artifact family
  instead of overwriting candidate, ranked, eval-set, or report artifacts.
- **D-06:** A translation run must remain traceable back to the source
  candidate IDs and input file/manifests that produced it.

### Benchmark/eval-set hook posture

- **D-07:** Phase 33 should add additive hooks for later external experiments,
  but it should not redesign existing Zomic `llm_eval_set` schema or pretend the
  current benchmark commands already consume CIF/material-string payloads.
- **D-08:** The reusable handoff should be a manifest/inventory or bundle that a
  later external-model phase can consume directly, rather than a hidden
  convention inside docs alone.

### Documentation posture

- **D-09:** Keep the existing translation contract note technical and
  implementation-oriented; add a separate operator/runbook surface for how to
  run exports and when to trust or distrust them.
- **D-10:** The docs must say plainly when CIF/material-string exports are safe
  periodic approximants, when they are explicit periodic proxies, and when
  Zomic remains the authoritative representation.

### Inherited constraints

- **D-11:** Zomic remains the QC-native source of truth; translation artifacts
  are additive interop views.
- **D-12:** The Phase 32 compatibility decision is locked: CIF may carry
  comment metadata, but `crystaltextllm_material_string` raw bodies stay bare
  and CrystalTextLLM-compatible.
- **D-13:** New translation workflow artifacts must stay deterministic and
  should reuse the existing `CandidateRecord -> TranslatedStructureArtifact ->
  emitted_text` seam instead of re-normalizing geometry.

</decisions>

<canonical_refs>
## Canonical References

- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/31-translation-contracts-and-representation-loss-semantics/31-VERIFICATION.md`
- `.planning/phases/32-cif-and-material-string-exporters/32-VERIFICATION.md`
- `materials-discovery/developers-docs/llm-translation-contract.md`
- `materials-discovery/developers-docs/pipeline-stages.md`
- `materials-discovery/developers-docs/index.md`
- `materials-discovery/README.md`
- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/src/materials_discovery/llm/translation.py`
- `materials-discovery/src/materials_discovery/llm/translation_export.py`
- `materials-discovery/src/materials_discovery/llm/eval_set.py`
- `materials-discovery/src/materials_discovery/llm/storage.py`

</canonical_refs>

<code_context>
## Existing Code Insights

- `materials_discovery.llm.translation` and `translation_export` already provide
  the normalized export seam this phase should drive from the CLI.
- `cli.py` already has a stable pattern for file-backed commands: validate
  inputs early, write dedicated artifact directories/files, emit a JSON summary,
  and use manifests for traceability.
- `llm/storage.py` already groups LLM-stage artifacts under dedicated
  directories (`data/llm_eval_sets/`, `data/benchmarks/llm_serving/`,
  `data/llm_campaigns/`), which is a strong precedent for a translation export
  artifact root.
- `llm/eval_set.py` already shows the repo’s preferred style for writing a
  reusable set plus a manifest, but its current schema is Zomic/example-pack
  specific and should not be silently repurposed for CIF/material-string text.
- The docs explicitly say Phase 33 owns CLI workflow, artifact storage, and
  operator guidance for translation; Phase 32 intentionally stopped at raw
  serializer APIs.

</code_context>

<specifics>
## Specific Ideas

- Add a first `mdisc llm-translate` workflow that reads candidate JSONL from a
  file-backed path, resolves a target family, emits deterministic files, and
  writes a manifest/inventory bundle under a dedicated translation artifact
  directory.
- Add a lightweight inspect/tracing path so operators can summarize a
  translation export bundle without writing Python.
- Keep benchmark/eval-set reuse additive by emitting a machine-readable bundle
  row per exported payload, with provenance fields that later external-model
  phases can consume.
- Update the docs surface in three places:
  - a new translation runbook
  - pipeline command reference
  - top-level README/docs index pointers

</specifics>

<deferred>
## Deferred Ideas

- Running downloaded external materials LLMs directly from this phase
- Automatic best-target or best-model selection across CIF/material-string
  consumers
- A UI or dashboard for translation export management
- Retrofitting existing `llm_eval_set` rows to inline CIF/material-string
  payloads before later external-model phases prove the right downstream shape

</deferred>

---

*Phase: 33-cli-benchmark-hooks-and-operator-docs*
*Context gathered: 2026-04-06*
