# Phase 37: Deep-Dive Provenance Audit and Tutorial Scope - Research

**Researched:** 2026-04-15
**Domain:** documentation provenance, stale-claim audit, shipped-surface evidence, tutorial scope lock
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

## Implementation Decisions

### Narrative boundary
- **D-01:** The refreshed deep-dive source should remain a high-level external
  narrative, not become a standalone exhaustive operator manual.
- **D-02:** The narrative should cross-link the current runbooks and reference
  docs instead of duplicating their full procedural detail.
- **D-03:** The refresh must explicitly cover the shipped workflow surface
  through `v1.6`, not stop at the earlier seven-stage core pipeline.

### Evidence and freshness policy
- **D-04:** Capability claims in the refreshed deep-dive source should be
  backed by shipped planning artifacts, current docs, or git history.
- **D-05:** Planned or future capabilities must be labeled explicitly as future
  work rather than blended into current-state prose.
- **D-06:** Quantitative claims that drift quickly, such as commit counts or
  module counts, should either be refreshed from the repo or softened so the
  document does not go stale immediately again.

### Tutorial anchor example
- **D-07:** The tutorial should center one reproducible Sc-Zn Zomic-backed
  example because it connects design authoring, pipeline execution, and
  vZome/Zomic visualization in one path.
- **D-08:** The default tutorial path should optimize for reproducibility and
  operator learning first, using the checked example config and design assets
  before any optional real/native follow-on notes.
- **D-09:** Broader chemistry coverage should be deferred rather than packing
  multiple worked examples into the first tutorial.

### Tutorial walkthrough shape
- **D-10:** The tutorial should be a step-by-step operator walkthrough with
  concrete commands, expected artifact locations, and interpretation checkpoints
  after each major stage.
- **D-11:** The tutorial must explain how to read screening, validation,
  ranking, and report artifacts, not just how to run commands.
- **D-12:** The visualization section should point to the exact Zomic design and
  export artifacts that remain the geometry authority for the worked example.

### the agent's Discretion
- Exact document naming and where the tutorial lives within
  `materials-discovery/developers-docs/`
- Whether tables, diagrams, or screenshots are worth adding if they clarify the
  shipped workflow without requiring new product work
- Exact balance of prose, callouts, and command blocks in the tutorial

### Claude's Discretion

- Exact document naming and where the tutorial lives within
  `materials-discovery/developers-docs/`
- Whether tables, diagrams, or screenshots are worth adding if they clarify the
  shipped workflow without requiring new product work
- Exact balance of prose, callouts, and command blocks in the tutorial

### Deferred Ideas (OUT OF SCOPE)

- Additional worked tutorials for Al-Cu-Fe reference-aware flow or the external
  benchmark surface
- Broader podcast or website packaging beyond the repo documentation set
- Multi-example chemistry coverage in the first tutorial
</user_constraints>

## Project Constraints (from CLAUDE.md)

- `materials-discovery/` changes require updating `materials-discovery/Progress.md`.
- The required progress update has two parts: add a Changelog table row, and append a timestamped Diary entry under today's date heading.
- The rule applies to all `materials-discovery/` changes: code, configs, experiments, fixes, refactors, docs, and new systems.
- Phase 37 research writes under `.planning/`, so it does not itself require a `materials-discovery/Progress.md` update.
- `AGENTS.md` also says to push only to the `fork` remote, not to push `origin` unless explicitly requested, and not to open pull requests unless explicitly requested.
- No project-local `.claude/skills/` or `.agents/skills/` SKILL.md files were found.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOC-01 | Operator can see when `materials-discovery/developers-docs/podcast-deep-dive-source.md` was created, how it moved in the repo, and which shipped milestones and workflow capabilities landed after its first draft so refresh work has a concrete evidence base. | Use `git log --follow --name-status` for creation and renames; use milestone audits and verification reports for shipped post-draft surfaces; use current CLI/docs/code for stale claim and tutorial-scope evidence. |
</phase_requirements>

## Summary

Phase 37 should produce an evidence packet, not a rewrite. The established pattern in this repo is CLI-first, file-backed, and artifact-oriented: claims should point to git history, milestone audits, verification reports, current docs, or current source. The planner should create one Phase 37 audit artifact in the phase directory, with tables for provenance, shipped deltas, stale claims, missing shipped surfaces, and the chosen tutorial path.

The deep-dive source was first added at `359cef57777479fb15652f1f4c702c43a25c4bc6` on 2026-03-06 at `developer-docs/podcast-deep-dive-source.md`, moved the same day to `developer-docs/materials_discovery/podcast-deep-dive-source.md`, and moved again on 2026-04-02 to `materials-discovery/developers-docs/podcast-deep-dive-source.md`. Since then, the project shipped milestones `v1.0` through `v1.6`, including the LLM campaign workflow, serving lanes, adapted checkpoint lifecycle, translation bridge, and external benchmark scorecards. The current document still frames the product as a seven-command core pipeline and carries stale fast-moving numbers.

**Primary recommendation:** Create `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md` as the handoff artifact for Phases 38 and 39, with no `materials-discovery/` edits in Phase 37 unless explicitly added to the plan.

## Standard Stack

### Core

| Tool/Source | Version | Purpose | Why Standard |
|-------------|---------|---------|--------------|
| Git CLI | 2.53.0 | Follow file creation, renames, and post-draft commits | `git log --follow --name-status` is the source of truth for file provenance. |
| ripgrep | 15.1.0 | Find stale claims and shipped-surface references quickly | Fast enough for whole-repo claim scans and already available. |
| Markdown tables | n/a | Store the audit packet and tutorial scope lock | Existing GSD artifacts and docs use Markdown tables for traceability. |
| GSD milestone artifacts | local | Shipped-surface evidence | Milestone audits and phase verification reports encode what is actually shipped. |
| `mdisc` CLI | materials-discovery 0.1.0 | Verify current operator command surface | Root help and `cli.py` expose the real shipped command list. |

### Supporting

| Tool/Source | Version | Purpose | When to Use |
|-------------|---------|---------|-------------|
| uv | 0.10.10 | Run project Python and CLI checks | Use for `uv run mdisc --help`, focused pytest, and project Python. |
| Python via uv | 3.11.15 | Project runtime for optional helper checks | Use only through `uv run`; system `python3` is 3.9.6 and below the project requirement. |
| pytest | 9.0.2 | Existing validation framework | Use if Phase 37 touches code or needs CLI help regression checks. |
| Java runtime | OpenJDK 21.0.10 | Zomic export path availability | Needed later for `mdisc export-zomic` or `generate` with `zomic_design`. |
| Gradle wrapper | 8.13 | vZome core Zomic export | The checked `./gradlew` wrapper is available for the Zomic bridge. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `git log --follow` | Manual commit-subject reconstruction | Misses renames and produces weak provenance. Do not use. |
| Current docs only | `mdisc --help` plus `cli.py` plus docs | Docs can be stale. Verify command surface against code/help. |
| One broad tutorial survey | One Sc-Zn Zomic-backed path | Broad surveys drift across systems. One checked path supports reproducibility. |
| Updating fast counts in prose | Softening/removing fast-drifting counts | Fresh counts go stale again; soften unless a count matters. |

**Installation:**

No new dependencies are needed. If validation needs the project environment:

```bash
cd materials-discovery
uv sync --extra dev
```

**Version verification performed:**

```bash
git --version
rg --version
uv --version
cd materials-discovery && uv run python --version
cd materials-discovery && uv run pytest --version
java -version
./gradlew --version
cd materials-discovery && uv run mdisc --help
```

## Architecture Patterns

### Recommended Project Structure

```text
.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/
|-- 37-CONTEXT.md              # User decisions and phase boundary
|-- 37-RESEARCH.md             # This research artifact
`-- 37-PROVENANCE-AUDIT.md     # Recommended Phase 37 deliverable
```

Do not put the Phase 37 audit inside `materials-discovery/` unless the plan intentionally edits operator docs and also updates `materials-discovery/Progress.md`.

### Pattern 1: Evidence Packet, Not Narrative Rewrite

**What:** Produce one audit handoff document with these sections:

- File provenance ledger
- Post-draft shipped milestone delta table
- Stale quantitative claims
- Stale capability descriptions
- Missing shipped surfaces
- Tutorial anchor path and artifact set
- Phase 38 correction checklist
- Phase 39 tutorial scope lock

**When to use:** Use for Phase 37. Phase 38 can then rewrite the narrative using this packet; Phase 39 can author the tutorial from the locked path.

**Example:**

```markdown
| Claim Location | Current Claim | Evidence Source | Audit Result | Phase 38 Action |
|----------------|---------------|-----------------|--------------|-----------------|
| podcast-deep-dive-source.md:220 | Seven commands, ~60 modules, 7,200 LOC | `mdisc --help`; `find src -name '*.py'`; `wc -l` | Stale | Replace with softer/current shipped-surface wording |
```

### Pattern 2: Provenance Ledger

**What:** Use git history as a ledger, preserving commit hashes, dates, paths, and rename scores.

**When to use:** Any claim about when the podcast source was written or moved.

**Verified findings:**

| Event | Commit | Date | Path Evidence |
|-------|--------|------|---------------|
| Created | `359cef57777479fb15652f1f4c702c43a25c4bc6` | 2026-03-06T19:53:04-05:00 | `A developer-docs/podcast-deep-dive-source.md` |
| First move | `9d7e7bc8189b067155a147ce2dd1e180688ef96f` | 2026-03-06T20:01:04-05:00 | `R099 developer-docs/podcast-deep-dive-source.md -> developer-docs/materials_discovery/podcast-deep-dive-source.md` |
| Current move | `f21c17e3c1a246349d0d0171cfa0b9390bcc8c1d` | 2026-04-02T20:48:12-04:00 | `R098 developer-docs/materials_discovery/podcast-deep-dive-source.md -> materials-discovery/developers-docs/podcast-deep-dive-source.md` |

### Pattern 3: Shipped Surface Delta Matrix

**What:** Compare the source document's current claims against shipped milestones after the first draft.

**When to use:** Any capability sentence that says "now", "currently", "implemented", "future", or implies workflow completeness.

**Required rows:**

| Milestone | Shipped Evidence | Why It Matters For Refresh |
|-----------|------------------|----------------------------|
| `v1.0` | `.planning/milestones/v1.0-MILESTONE-AUDIT.md` | Multi-source ingestion, reference-aware workflow, LLM corpus/generate/evaluate/suggest surfaces shipped. |
| `v1.1` | `.planning/milestones/v1.1-MILESTONE-AUDIT.md` | Closed-loop campaign proposal, approval, launch, replay, and compare shipped. |
| `v1.2` | `.planning/milestones/v1.2-MILESTONE-AUDIT.md` | Hosted/local/specialized serving lanes and serving benchmark workflow shipped. |
| `v1.3` | `.planning/milestones/v1.3-MILESTONE-AUDIT.md` | Adapted-checkpoint registration, strict lane resolution, and rollback guidance shipped. |
| `v1.4` | `.planning/milestones/v1.4-MILESTONE-AUDIT.md` | Checkpoint-family lifecycle, promoted default, explicit pin, promotion, retirement shipped. |
| `v1.5` | `.planning/v1.5-MILESTONE-AUDIT.md` | CIF/material-string translation bundle workflow and fidelity/loss semantics shipped. |
| `v1.6` | `.planning/v1.6-MILESTONE-AUDIT.md` | Translated benchmark freeze, external target registration, comparative external benchmark, and scorecards shipped. |

### Pattern 4: Tutorial Scope Lock

**What:** Lock one reproducible Sc-Zn Zomic-backed path and name the exact authority artifacts.

**When to use:** Phase 37 should choose scope. Phase 39 should implement tutorial content from that scope without broadening examples.

**Anchor path:**

| Role | Artifact |
|------|----------|
| System config | `materials-discovery/configs/systems/sc_zn_zomic.yaml` |
| Zomic design YAML | `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml` |
| Zomic source | `materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic` |
| Raw exported geometry | `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json` |
| Orbit-library generator input | `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json` |
| Anchor prototype | `materials-discovery/data/prototypes/sc_zn_tsai_sczn6.json` |
| Current bridge docs | `materials-discovery/developers-docs/zomic-design-workflow.md` |
| Visualization context | `materials-discovery/developers-docs/vzome-geometry-tutorial.md` |

Verified artifact facts: the generated orbit library currently contains 5 selected anchor orbits and 100 sites; the raw export contains 52 labeled points and 52 segments. Use these as audit evidence, but avoid baking them into long-lived tutorial prose unless the tutorial explains how to re-check them.

### Anti-Patterns to Avoid

- **Rewriting the deep-dive in Phase 37:** This phase establishes evidence and scope. Phase 38 owns the actual narrative refresh.
- **Using docs as sole truth:** `RUNBOOK.md` quick reference currently omits newer v1.5/v1.6 command rows, while `mdisc --help`, `pipeline-stages.md`, and `index.md` expose them. Verify through multiple sources.
- **Treating "fixture mode" as a top-level backend mode:** Current `BackendConfig.mode` is only `"mock"` or `"real"`; fixture, exec, and native are adapter/provider layers under that mode.
- **Expanding tutorial scope:** Do not add Al-Cu-Fe, external benchmark, or native MLIP worked examples to the first tutorial. Mention only as optional follow-on context if needed.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File provenance | A manual history timeline from memory | `git log --follow --name-status --date=iso-strict` | Handles renames and gives commit hashes/dates. |
| Shipped capability evidence | A prose summary from the agent's memory | Milestone audits, phase verification reports, current docs, and current CLI help | Prevents blending planned and shipped work. |
| Command surface inventory | A hand-maintained command list | `uv run mdisc --help` and `rg '@app.command' cli.py` | Existing docs can lag the real CLI. |
| Stale quantitative claim detection | Manual eyeballing only | `rg` claim scans plus deterministic count commands | Reduces missed numeric claims. |
| Tutorial data path | New configs or generated assets | Existing `sc_zn_zomic` config and checked Zomic assets | Keeps tutorial reproducible and inside phase scope. |
| Visualization bridge | New export or reverse-import tooling | Existing Zomic design/export artifacts and docs | Phase 37-39 must teach current toolchain, not expand it. |

**Key insight:** The main risk is not missing a library. It is creating an attractive narrative that is not traceable to shipped artifacts. Every audit row should answer: "What exact source proves this?"

## Common Pitfalls

### Pitfall 1: Missing File Moves

**What goes wrong:** The audit says the source was created at the current path.
**Why it happens:** Plain `git log` without `--follow` stops at the latest rename.
**How to avoid:** Use `git log --follow --name-status` on `materials-discovery/developers-docs/podcast-deep-dive-source.md`.
**Warning signs:** The history starts at 2026-04-02 instead of 2026-03-06.

### Pitfall 2: Treating Current Docs As Always Current

**What goes wrong:** The audit repeats stale command or artifact claims from docs.
**Why it happens:** The docs are extensive and mostly reliable, but some quick-reference rows lag v1.5/v1.6.
**How to avoid:** Cross-check `developers-docs/index.md`, `pipeline-stages.md`, `RUNBOOK.md`, `mdisc --help`, and `cli.py`.
**Warning signs:** The claimed command surface stops before `llm-translate`, `llm-translated-benchmark-*`, or `llm-external-benchmark`.

### Pitfall 3: Quantitative Drift

**What goes wrong:** The refresh updates counts once and they become stale again.
**Why it happens:** Commit counts, module counts, LOC, and test-file counts move quickly.
**How to avoid:** Either soften them or document the exact command/date used.
**Warning signs:** Claims like `4,238 commits`, `60 modules`, `7,200 LOC`, or `21 test files` appear without date and command.

### Pitfall 4: Planned/Shipped Blur

**What goes wrong:** Planned LLM training, reverse import, autonomous campaigns, or broader chemistry support reads as shipped.
**Why it happens:** Several docs include planned sections beside shipped sections.
**How to avoid:** Use milestone audits and verification reports for "shipped"; label the rest as future.
**Warning signs:** "will gain", "planned", "future", or v2 requirements appear in current-state prose.

### Pitfall 5: Mutating `materials-discovery/data` During Research

**What goes wrong:** Running export or tutorial commands creates/modifies data artifacts during a docs audit.
**Why it happens:** `mdisc export-zomic` and `mdisc generate` write under `materials-discovery/data`.
**How to avoid:** In Phase 37, inspect existing checked artifacts unless the plan explicitly includes a run and the required Progress.md update.
**Warning signs:** `git status --short` shows `materials-discovery/` changes after a provenance-only task.

### Pitfall 6: Tutorial Scope Creep

**What goes wrong:** The tutorial tries to cover Sc-Zn, Al-Cu-Fe, external benchmarks, native MLIPs, and LLM campaign workflows at once.
**Why it happens:** The shipped surface is now large.
**How to avoid:** Lock the required path to Sc-Zn Zomic-backed design -> generate -> screen -> validate -> rank -> report -> visualization references.
**Warning signs:** More than one worked chemical system appears in the tutorial plan.

## Code Examples

Verified patterns from local authoritative sources:

### File Provenance

```bash
git log --follow --date=iso-strict \
  --format='%H%x09%ad%x09%an%x09%s' \
  --name-status -- \
  materials-discovery/developers-docs/podcast-deep-dive-source.md
```

### Current Command Surface

```bash
cd materials-discovery
uv run mdisc --help
rg -n '@(?:app|lake_app|llm_corpus_app)\.command' src/materials_discovery/cli.py
```

Current local result: 29 root `@app.command` entries plus 4 nested group commands under `lake` and `llm-corpus`.

### Quantitative Claim Refresh

```bash
git rev-list --count HEAD
git rev-list --count 359cef57777479fb15652f1f4c702c43a25c4bc6
find materials-discovery/src/materials_discovery -type f -name '*.py' | wc -l
find materials-discovery/src/materials_discovery -type f -name '*.py' -print0 | xargs -0 wc -l | tail -1
find materials-discovery/tests -type f -name 'test_*.py' | wc -l
```

Current local results as of 2026-04-15: 4,629 total commits at `HEAD`, 4,278 at the creation commit, 122 Python source files under `src/materials_discovery`, 27,857 Python source LOC by `wc -l`, and 96 test files. Treat these as audit evidence, not necessarily prose that should be copied into Phase 38.

### Stale Claim Scan

```bash
rg -n "seven commands|60 modules|7,200|21 test files|4,238|future|planned|will" \
  materials-discovery/developers-docs/podcast-deep-dive-source.md \
  materials-discovery/developers-docs/index.md \
  materials-discovery/RUNBOOK.md
```

### Tutorial Anchor Artifact Check

```bash
ls -l \
  materials-discovery/configs/systems/sc_zn_zomic.yaml \
  materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml \
  materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic \
  materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json \
  materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json \
  materials-discovery/data/prototypes/sc_zn_tsai_sczn6.json
```

## State of the Art

| Old Approach In Deep Dive | Current Shipped Approach | When Changed | Impact |
|---------------------------|--------------------------|--------------|--------|
| Seven-stage core pipeline only | Core pipeline plus Zomic export, LLM generation/evaluation/suggest, campaign governance, serving, checkpoints, translation, and external benchmarks | `v1.0` through `v1.6`, audited 2026-04-04 to 2026-04-07 | Phase 38 must not stop at the seven-stage description. |
| Static long-form source as current truth | Long-form narrative plus cross-links to runbooks and command references | Current v1.7 decision | Narrative should stay high-level and point to source-of-truth docs. |
| Fast counts in prose | Regenerated or softened counts with command/date evidence | Current v1.7 decision | Avoids immediate re-staleness. |
| Zomic bridge as conceptual/planned path | `mdisc export-zomic` and `generate` with `zomic_design` are shipped | Current docs and CLI | Tutorial can use Sc-Zn Zomic-backed assets today. |
| External materials LLM interop as future | Translation bundle, CIF/material-string exporters, benchmark-pack freeze, external target registration, comparative benchmark scorecards shipped | `v1.5` and `v1.6`, 2026-04-07 | Deep dive needs explicit shipped-vs-future wording. |
| Backend "four modes" phrasing | `BackendConfig.mode` is `mock` or `real`; fixture/exec/native are adapter/provider layers | Current `common/schema.py` and backend docs | Refresh should describe layers carefully. |

**Deprecated/outdated in the source document:**

- `4,238 commits`: current local `HEAD` count is 4,629; the creation commit count was 4,278.
- `seven commands`: current root CLI has many more commands and command groups.
- `60 modules and 7,200 lines of code`: current source tree is substantially larger.
- `21 test files`: current test file count is much higher.
- "The pipeline currently targets three real alloy systems": current docs list additional configs and Sc-Zn variants; avoid over-specific count phrasing.
- "Four execution layers" should be reframed through the current backend docs: mock mode, real mode with fixture fallback, exec adapters, and native providers.

## Open Questions

1. **Exact Phase 37 deliverable filename**
   - What we know: the planner needs one concrete artifact for Phases 38 and 39.
   - What's unclear: no filename was locked in CONTEXT.md.
   - Recommendation: use `37-PROVENANCE-AUDIT.md` in the phase directory.

2. **Whether Phase 37 should edit `materials-discovery/` docs**
   - What we know: Phase 37 boundary says it does not rewrite the deep-dive source itself.
   - What's unclear: the planner could decide to add a tiny cross-link or placeholder, but that would trigger `Progress.md`.
   - Recommendation: keep Phase 37 entirely in `.planning/`; leave materials docs changes to Phase 38/39.

3. **How much of the tutorial path to execute during Phase 37**
   - What we know: Java and Gradle are available, and checked generated artifacts already exist.
   - What's unclear: running commands can mutate data artifacts and expand Phase 37.
   - Recommendation: inspect existing artifacts in Phase 37; require execution only in Phase 39.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Git CLI | Provenance audit | yes | 2.53.0 | None needed |
| ripgrep | Claim scans | yes | 15.1.0 | `grep`, but prefer `rg` |
| uv | Project CLI/test checks | yes | 0.10.10 | None needed |
| Project Python | `mdisc`, pytest | yes | 3.11.15 through `uv run python` | Do not use system Python 3.9.6 for project code |
| pytest | Validation | yes | 9.0.2 through `uv run pytest` | `git diff --check` for docs-only smoke, but pytest is available |
| Java runtime | Sc-Zn Zomic export path | yes | OpenJDK 21.0.10 | Existing checked generated artifacts for Phase 37 audit |
| Gradle wrapper | vZome core Zomic export | yes | Gradle 8.13 | Existing checked generated artifacts for Phase 37 audit |
| `mdisc` CLI | Current command surface | yes | local package 0.1.0 | Inspect `cli.py` if CLI env fails |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 via `uv run pytest` |
| Config file | `materials-discovery/pyproject.toml` |
| Quick run command | `git diff --check` |
| Full suite command | `cd materials-discovery && uv run pytest` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| DOC-01 | Audit records source creation, path moves, and post-draft shipped milestones. | docs/provenance smoke | `git log --follow --name-status -- materials-discovery/developers-docs/podcast-deep-dive-source.md` | yes source doc |
| DOC-01 | Audit identifies stale quantitative claims and stale/missing capability descriptions. | docs content check | `rg -n "4,238|seven commands|60 modules|7,200|21 test files|v1.6|llm-external-benchmark|llm-translate" .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-*.md` | no audit artifact yet |
| DOC-01 | Audit locks one Sc-Zn Zomic-backed tutorial path and artifact set. | docs content check | `rg -n "sc_zn_zomic|sc_zn_tsai_bridge|raw_export|orbit-library|vZome|Zomic" .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-*.md` | no audit artifact yet |

### Sampling Rate

- **Per task commit:** `git diff --check`
- **Per wave merge:** `git diff --check` plus targeted `rg` checks against the Phase 37 audit artifact
- **Phase gate:** Phase 37 audit artifact exists, includes provenance/milestone/stale-claim/tutorial-scope sections, and `git diff --check` is clean

### Wave 0 Gaps

- [ ] `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md` - covers DOC-01 provenance, stale claim inventory, shipped delta matrix, and tutorial scope lock.
- [ ] No new Python test files required for Phase 37 unless implementation chooses to add a helper script.

## Sources

### Primary (HIGH confidence)

- `.planning/REQUIREMENTS.md` - DOC-01 and v1.7 boundaries.
- `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-CONTEXT.md` - locked decisions, tutorial anchor, deferred scope.
- `.planning/STATE.md` - current milestone state and recent project decisions.
- `CLAUDE.md` and `AGENTS.md` - project constraints.
- `git log --follow --name-status -- materials-discovery/developers-docs/podcast-deep-dive-source.md` - creation and move provenance.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` through `.planning/v1.6-MILESTONE-AUDIT.md` - shipped milestone evidence.
- `.planning/milestones/v1.6-phases/*/*-VERIFICATION.md` and `.planning/milestones/v1.5-phases/33-*/33-VERIFICATION.md` - detailed shipped evidence for translation and external benchmark surfaces.
- `materials-discovery/developers-docs/podcast-deep-dive-source.md` - source under audit.
- `materials-discovery/developers-docs/index.md`, `materials-discovery/RUNBOOK.md`, `materials-discovery/developers-docs/pipeline-stages.md`, `materials-discovery/developers-docs/zomic-design-workflow.md`, `materials-discovery/developers-docs/vzome-geometry-tutorial.md` - current docs surface.
- `materials-discovery/src/materials_discovery/cli.py`, `materials-discovery/src/materials_discovery/common/schema.py`, `materials-discovery/src/materials_discovery/generator/zomic_bridge.py` - current command/backend/Zomic implementation truth.
- `materials-discovery/configs/systems/sc_zn_zomic.yaml`, `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml`, `materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic` - tutorial anchor inputs.

### Secondary (MEDIUM confidence)

- Local command outputs from `uv run mdisc --help`, `find`, `wc`, `git rev-list --count`, and `ls -l` - current environment and count snapshots. These are reliable for 2026-04-15 but intentionally time-bound.

### Tertiary (LOW confidence)

- None. No web-only or unverified sources were used.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - all tools and versions were verified locally.
- Architecture: HIGH - based on repo GSD patterns, current docs, current CLI, and milestone audit structure.
- Pitfalls: HIGH - derived from concrete discrepancies between target source, docs, CLI, and git history.
- Tutorial anchor: HIGH - locked in CONTEXT.md and verified against checked config/design/generated artifacts.
- Quantitative current counts: MEDIUM - command outputs are current snapshots and should be regenerated before long-lived publication.

**Research date:** 2026-04-15
**Valid until:** 2026-05-15 for architecture and provenance; 2026-04-22 for fast-moving counts and command inventory.
