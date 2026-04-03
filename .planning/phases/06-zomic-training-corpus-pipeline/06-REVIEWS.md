---
phase: 6
reviewers: [gemini, claude, codex]
reviewed_at: 2026-04-03T19:58:54Z
plans_reviewed:
  - 06-01-PLAN.md
  - 06-02-PLAN.md
  - 06-03-PLAN.md
  - 06-04-PLAN.md
---

# Cross-AI Plan Review — Phase 6

## Gemini Review

Gemini CLI was invoked twice for Phase 6, once in direct capture mode and once
in TTY mode. In both attempts it exited successfully but returned only the
credential banner:

```text
Loaded cached credentials.
```

No usable review body was produced, so Gemini feedback could not be included in
the plan analysis.

---

## Claude Review

# Phase 6 Plan Review

## Summary

The four plans form a well-sequenced, low-risk decomposition of the corpus
pipeline. The foundation-first approach (schema -> inventory/converters ->
builder/CLI) mirrors established patterns from Phases 1-5. The main concern is
the `record2zomic` axis-walk decomposition: it's the hardest algorithmic piece
and is under-specified relative to its importance.

## Strengths

- Clean wave structure: `06-01` has zero dependencies; `06-02` and `06-03` run
  in parallel; `06-04` joins them.
- Consistent with repo conventions: file-backed JSONL, Pydantic contracts,
  workspace-relative paths, lazy optional imports.
- `PyQCstrc` is handled correctly as a fixture-backed source family, not a live
  dependency.
- Explicit `gold` / `silver` / `reject` tiering with structured fidelity
  metadata directly implements the Phase 6 context decisions.
- CIF conversion reuses `prototype_import.py` and `cif_conversion.py` rather
  than rebuilding.

## Concerns

- `HIGH`: `06-03` Task 1's bounded axis-walk serializer is the core algorithmic
  challenge of the phase, yet the plan describes it too lightly. The
  `QPhiCoord -> Zomic` strut decomposition is non-trivial. If the greedy
  decomposition fails frequently, most converted examples become `heuristic` and
  the materials corpus shrinks sharply.
- `MEDIUM`: `06-03` Task 2's `compile_zomic_script` temp design YAML uses
  placeholder cell values. If the bridge's fractional-position logic rejects
  embedded coordinates, compile validation can false-fail.
- `MEDIUM`: `06-02` Task 1's inventory globs assume a fixed repo layout
  relative to `workspace_root().parent`. No test explicitly verifies that base
  path.
- `LOW`: `CorpusProvenance.release_tier` looks construction-time while later QA
  wants to assign tier after grading. That can create a schema/flow mismatch.
- `LOW`: no plan mentions the repo's `Progress.md` requirement.

## Suggestions

- Add a dedicated unit test in `06-03` for axis-walk decomposition with
  known-good round-trip cases such as the Sc-Zn Tsai bridge sites.
- Make `compile_zomic_script` cell parameters configurable or scale them based
  on input coordinate magnitude.
- Let grading start from a neutral `pending` tier before promoting to `gold` or
  `silver`.
- Add an inventory test that asserts non-empty results against the actual repo
  tree, not only temp fixtures.

## Risk Assessment

`LOW-MEDIUM`. The plans are structurally sound and well-aligned with prior
phases. The only elevated risk is axis-walk decomposition quality: if it
produces mostly heuristic results, the corpus's practical value drops.

---

## Codex Review

### 06-01

**Summary**  
Strong foundation slice. The additive `llm/` package, committed config, and
deterministic storage/manifests fit the repo's existing file-backed style well.
The main weakness is that a few contracts are still looser than the later plans
assume.

**Strengths**
- Clean scope boundary: schema/storage/manifests first, no premature converter
  logic.
- Reuses existing workspace-relative and manifest conventions instead of
  inventing new storage patterns.

**Concerns**
- `HIGH`: the interface note for `write_json_object` is reversed from the
  current code (`record, path`), so the plan can lock in a bad call pattern.
- `MEDIUM`: `validation: dict[str, Any]` is under-typed; later QA/compiler
  plans depend on specific keys but this plan does not lock them.

**Suggestions**
- Correct the helper signature in the plan text.
- Add typed validation/output submodels now, not later.

**Risk Assessment**  
`LOW-MEDIUM` because the scope is right, but contract drift here will ripple
into every later plan.

### 06-02

**Summary**  
Well-sequenced and phase-appropriate. Source inventory plus explicit
`gold` / `silver` / `reject` gating is the right middle layer before converters
and corpus assembly.

**Strengths**
- Offline, fixture-backed posture matches the repo's testing style.
- Makes quality and tiering explicit instead of burying it inside converters.

**Concerns**
- `HIGH`: inventory mostly discovers files, not normalized record-level items,
  so `06-04` will likely need to reopen and reinterpret sources in multiple
  places.
- `MEDIUM`: dedupe keeps "first by sort," but plain string sort is not a real
  tier-priority rule.

**Suggestions**
- Make inventory rows record-addressable, not just file-addressable.
- Encode explicit precedence: `gold > silver > reject`.

**Risk Assessment**  
`MEDIUM` because the architecture is sound, but inventory granularity is too
thin for a clean builder.

### 06-03

**Summary**  
This is the riskiest plan. It addresses the hard conversion core, but the
proposed serialization is too heuristic for corpus data that is supposed to
ground later LLM work.

**Strengths**
- Correctly reuses Java/vZome as compile authority.
- Good call to keep `PyQCstrc` fixture-based and offline.

**Concerns**
- `HIGH`: the bounded axis-walk placeholder can yield compilable but
  geometry-false Zomic, which weakens corpus quality.
- `HIGH`: promoting qphi/projection-derived outputs to `exact` is not justified
  unless equivalence to source coordinates is proven.

**Suggestions**
- Reserve `exact` for native Zomic or export-backed examples.
- Require a geometry-equivalence check before promoting converted outputs above
  `approximate`.

**Risk Assessment**  
`HIGH` because this plan could produce technically valid but scientifically weak
training data.

### 06-04

**Summary**  
Good end-to-end closeout, but it inherits too much ambiguity from the earlier
plans.

**Strengths**
- Completes the operator path through CLI integration.
- Keeps CIF work additive and offline.

**Concerns**
- `HIGH`: there is no explicit loader/converter for raw repo `.zomic` sources
  even though they are required syntax-corpus inputs.
- `MEDIUM`: generated-export handling is vague despite those artifacts already
  containing rich exact/provenance data.

**Suggestions**
- Add a dedicated native-Zomic loader.
- Add a generated-export converter before wiring the final builder.

**Risk Assessment**  
`MEDIUM-HIGH` because the phase is achievable, but only if exact-source
ingestion is made concrete before the final builder.

---

## Consensus Summary

Two reviewers returned substantive feedback. Both see the phase structure as
good overall: additive, well sequenced, and aligned with the repo's existing
file-backed conventions. Both also converge on the same core risk: the Phase 6
conversion layer can easily produce syntactically valid but scientifically weak
training data if fidelity is not locked down more tightly before execution.

### Agreed Strengths

- The wave structure is strong: foundation first, then parallel middle-layer
  work, then final builder/CLI integration.
- The plan stays additive to the existing architecture instead of overloading
  `generator/` or `data_sources/`.
- Fixture-backed offline validation and reuse of existing seams are both good
  design choices.

### Agreed Concerns

- The `06-03` conversion core is the highest-risk part of the phase. Both
  reviewers flagged the current `record2zomic` / projection conversion approach
  as under-specified or too heuristic for corpus-quality guarantees.
- Fidelity promotion rules are not locked tightly enough. "Compiles" is not a
  strong enough proxy for "scientifically faithful."
- `06-04` still needs clearer handling for exact-source ingestion, especially
  native `.zomic` inputs and export-backed artifacts.

### Divergent Views

- Claude views the phase as broadly low-medium risk with one dominant
  algorithmic hotspot.
- Codex rates the overall risk a bit higher because it also sees contract
  looseness in `06-01`, inventory granularity gaps in `06-02`, and exact-source
  ingestion ambiguity in `06-04`.
- Gemini could not be included because the local CLI produced no usable review
  body.
