# Phase 6 Research: Zomic Training Corpus Pipeline

**Phase:** 06  
**Date:** 2026-04-03  
**Goal:** Plan the data-foundation phase that builds a Zomic-centered corpus for
later LLM training and inference.

## Research Question

What do we need to know to plan Phase 6 well so that the team can:

- build deterministic `record2zomic` and `cif2zomic` conversion paths
- include `PyQCstrc`-style projection data in required v1 scope without adding a
  fragile runtime dependency
- assemble two corpus outputs (syntax-first and materials-conditioned)
- apply explicit `gold` / `silver` QA and fidelity tiering
- prepare for later `llm-generate` and `llm-evaluate` work without prematurely
  locking the inference architecture

## Key Findings

### 1. The repo already contains four meaningful corpus source families

Phase 6 does not start from zero. The current repo already exposes:

- **repo-native Zomic grammar examples**
  - `core/src/regression/files/Zomic/**/*.zomic`
  - `core/src/main/resources/com/vzome/core/parts/**/*.zomic`
- **materials-specific Zomic designs**
  - `materials-discovery/designs/zomic/*.zomic`
- **pipeline artifacts**
  - `materials-discovery/data/candidates/*.jsonl`
  - `materials-discovery/data/prototypes/generated/*.raw.json`
  - `materials-discovery/data/prototypes/generated/*.json`
- **staged open-source materials inputs**
  - `materials-discovery/data/external/sources/...`
  - `materials-discovery/data/external/reference_packs/...`

That strongly supports the user’s choice to split Phase 6 into a syntax-first
corpus and a richer materials-conditioned corpus rather than forcing one
uniform dataset too early.

### 2. Zomic parse/compile authority already exists, but only on the Java side

There is no Python-native Zomic parser or compiler in `materials-discovery/`.
Instead:

- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`
  shells out to `./gradlew :core:zomicExport`
- the real grammar and compiler live in:
  - `core/src/main/antlr/com/vzome/core/grammar/zomic/ZomicLexer.g4`
  - `core/src/main/antlr/com/vzome/core/grammar/zomic/ZomicParser.g4`
  - `core/src/main/java/com/vzome/core/zomic/ZomicASTCompiler.java`

This is a major planning constraint. Phase 6 should not try to invent a second
parser authority in Python. The safest path is:

- treat Java/vZome compile as ground truth for compileability
- use local fixtures and monkeypatched bridge calls in unit tests
- keep any Python-side validation lightweight and additive

### 3. `CandidateRecord` already contains enough structure to support `record2zomic`

`materials-discovery/src/materials_discovery/common/schema.py` already gives
`CandidateRecord`:

- `sites[].label`
- `sites[].qphi`
- `sites[].species`
- optional `fractional_position` and `cartesian_position`
- top-level `composition`, `system`, and `provenance`

That means Phase 6 does not need a new candidate-export format before building
`record2zomic`. The key missing seam is the inverse serializer from
`CandidateRecord` / `SiteRecord` back into deterministic Zomic text plus
conversion trace metadata.

### 4. Existing CIF handling is deeper than it first appears

Phase 6 can reuse two meaningful CIF-related seams:

- `materials-discovery/src/materials_discovery/data_sources/adapters/cif_conversion.py`
  already parses CIFs into canonical source records for `COD`
- `materials-discovery/src/materials_discovery/generator/prototype_import.py`
  already parses CIF symmetry/atom-site loops and exports orbit-library JSON

This matters because `cif2zomic` does not need to start from raw text parsing
from scratch. It can reuse:

- existing CIF parsing and orbit expansion logic
- canonical raw-source structure representations
- existing COD fixture coverage in
  `materials-discovery/tests/test_data_source_cod.py` and
  `materials-discovery/tests/test_prototype_import.py`

The recommended Phase 6 plan should treat `cif2zomic` as an additive layer on
top of those existing seams, not a brand-new CIF subsystem.

### 5. `PyQCstrc` is conceptually important but not yet a runtime dependency

`PyQCstrc` appears in docs and references, but there is no current Python
integration or packaged fixture in the repo.

That suggests a safer v1 implementation posture:

- support a **documented projection payload contract** for `PyQCstrc` exports
- test it with a committed thin JSON fixture
- do not require a live `PyQCstrc` install in Phase 6 verification

This matches the user’s decision to keep `PyQCstrc` in required scope while
still preserving the repo’s offline, deterministic test posture.

### 6. Optional dependency boundaries matter for Phase 6

`materials-discovery/pyproject.toml` shows:

- `pymatgen` is optional, under `ingestion` and `mlip`
- no `transformers`, `peft`, or tokenizer/training packages are installed yet

That has two direct consequences:

1. Phase 6 should keep corpus-building and conversion code import-light and
   avoid making heavy materials or ML dependencies part of the default install.
2. Any `cif2zomic` logic that wants `pymatgen` should keep imports lazy and
   retain fixture-backed fallbacks so unit tests stay green without the
   optional extra.

### 7. The planned long-term package shape already points to `llm/`

`materials-discovery/developers-docs/architecture.md` already documents a
planned package shape:

```text
llm/
  llm_generate.py
  llm_evaluate.py
  llm_suggest.py
  converters/
```

No such package exists yet in the source tree. Phase 6 is therefore the right
time to create the additive data/corpus subset of that package:

```text
materials_discovery/llm/
  schema.py
  storage.py
  manifests.py
  inventory.py
  qa.py
  corpus_builder.py
  converters/
```

This keeps corpus work in the same conceptual home that later inference phases
will use, while avoiding premature `llm_generate.py` / `llm_evaluate.py`
implementation.

### 8. Phase 6 needs its own artifact family, not overloaded benchmark or ingest outputs

Existing artifact families already serve other purposes:

- `data/external/...` → staged source and reference-pack inputs
- `data/candidates/...` → generated candidates for screening/validation
- `data/benchmarks/...` → benchmark corpora and lane comparisons

Phase 6 should not overload those. The cleaner additive target is:

```text
data/llm_corpus/{build_id}/
  syntax_corpus.jsonl
  materials_corpus.jsonl
  rejects.jsonl
  inventory.json
  qa.json
  manifest.json
```

This aligns with the repo’s file-backed architecture and keeps later training
and evaluation phases from needing to reverse-engineer corpus provenance.

### 9. The strongest v1 fidelity policy is tiered, not all-or-nothing

Because the user explicitly chose deterministic, auditable conversions with
explicit `gold` / `silver` tiers, the planning consequences are clear:

- conversion outputs need structured fidelity metadata
- corpus QA needs to grade examples, not just accept/reject them
- approximate mappings can remain useful without contaminating the
  highest-trust subset

This is especially important for:

- `cif2zomic` mappings from periodic coordinates into Z[phi]-compatible paths
- `PyQCstrc` projection imports with varying metadata richness
- repo-native Zomic scripts that are syntactically valuable but not
  materials-conditioned

## Recommended Implementation Shape

### Package layout

```text
materials-discovery/src/materials_discovery/llm/
  __init__.py
  schema.py
  storage.py
  manifests.py
  inventory.py
  qa.py
  compiler.py
  corpus_builder.py
  converters/
    __init__.py
    record2zomic.py
    projection2zomic.py
    cif2zomic.py
```

### Artifact and config layout

```text
materials-discovery/
  configs/
    llm/
      corpus_v1.yaml
  data/
    llm_corpus/
      {build_id}/
        syntax_corpus.jsonl
        materials_corpus.jsonl
        rejects.jsonl
        inventory.json
        qa.json
        manifest.json
```

### Recommended plan split

The cleanest execution split is:

1. **Foundation**
   - corpus config and example contracts
   - storage/manifests
2. **Inventory and QA**
   - source harvesting across repo/native/open inputs
   - `gold` / `silver` / reject tiering
3. **Core converters**
   - `record2zomic`
   - `projection2zomic`
   - compile-validation helper
4. **Corpus assembly**
   - `cif2zomic`
   - corpus builder
   - CLI integration and end-to-end build tests

This split matches the repo’s execution style and creates a natural place for
parallel execution in the middle waves.

## Main Risks

### Risk 1: Duplicating parser/compiler authority in Python

**Why it matters:** It would drift from the actual Zomic grammar/compiler used
by vZome.

**Mitigation:** Keep Java/vZome compile as the authoritative compileability
check and use bridge-backed validation helpers.

### Risk 2: Letting future prompt/training format leak into Phase 6 contracts

**Why it matters:** It would overfit corpus artifacts to one later model or one
prompt style.

**Mitigation:** Keep Phase 6 focused on durable source, provenance, fidelity,
and example contracts, not on the final Phase 7/8 prompt surface.

### Risk 3: Making `pymatgen` or other heavy packages mandatory

**Why it matters:** It would weaken the current lightweight developer path and
slow testing.

**Mitigation:** Keep optional imports lazy and design tests around committed CIF
fixtures and existing lightweight parsers first.

### Risk 4: Treating `PyQCstrc` as a live dependency instead of a source family

**Why it matters:** It would create environment fragility and verification
drift.

**Mitigation:** Support a documented projection payload contract and a thin
fixture path for Phase 6.

### Risk 5: Building one undifferentiated corpus

**Why it matters:** It would mix syntax teaching data, materials-conditioned
data, and low-confidence conversions into one blob and make later evaluation
harder.

**Mitigation:** Keep separate syntax and materials corpora plus explicit tier
metadata and rejects.
