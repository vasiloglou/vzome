# Phase 38: Narrative Refresh and Cross-Linked Deep Dive - Research

**Researched:** 2026-04-15
**Domain:** Repository documentation refresh for the shipped `materials-discovery/` workflow through `v1.6`
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
## Implementation Decisions

### Narrative shape
- **D-01:** Preserve roughly half of the existing history/math-heavy story and
  reshape the other half around the current shipped workflow. The refresh
  should feel like a balanced rewrite, not a total replacement and not a light
  touch polish pass.
- **D-02:** Keep the deep dive as a high-level external narrative rather than
  turning it into a standalone operator manual.
- **D-03:** The narrative should cross-link the current runbooks and reference
  docs instead of duplicating their procedural detail inline.

### Shipped-surface emphasis
- **D-04:** Post-`v1.0` shipped surfaces should be folded in prominently, with
  somewhat more emphasis than the legacy seven-stage framing. A good target is
  roughly a 60/40 split in favor of the current shipped workflow surface over
  the older origin-story-only framing.
- **D-05:** The refresh must explicitly cover the shipped workflow surface
  through `v1.6`, including campaigns, serving, checkpoint lifecycle,
  translation, and external benchmarking.
- **D-06:** Planned or future capabilities must be labeled explicitly as future
  work rather than blended into current-state prose.

### Quantitative claims and freshness
- **D-07:** Try refreshed numeric snapshots rather than dropping all numbers,
  but only keep numbers that are regenerated from current repo commands and are
  clearly time-bound rather than presented as timeless facts.
- **D-08:** If a number does not materially help the reader understand the
  system, soften or remove it instead of preserving it just because it can be
  counted.

### Documentation workflow
- **D-09:** Phase 38 will edit files under `materials-discovery/`, so it must
  update `materials-discovery/Progress.md` in the same change set with both a
  Changelog row and a Diary entry.

### Claude's Discretion
- Exact heading structure and paragraph flow of the refreshed deep dive
- Exact placement and phrasing of cross-links inside the document
- Which refreshed command-derived numeric snapshots are worth keeping after the
  rewrite
- Whether to add a compact summary table or callout block if it helps the
  document stay readable without turning it into a runbook

### Deferred Ideas (OUT OF SCOPE)
- Authoring the full worked tutorial itself — Phase 39
- Additional worked examples beyond the checked Sc-Zn path
- Broader website, podcast packaging, or marketing refresh outside the repo
  documentation set
</user_constraints>

## Summary

Phase 38 is a documentation rewrite, not a software expansion. The existing
deep-dive source is still valuable for its geometric origin story, but its
implementation section is stale: it frames the system as a seven-command
pipeline with fixed counts and a simplified backend story, while the shipped
surface now includes Zomic export, LLM generation/evaluation, operator-governed
campaigns, serving benchmarks, checkpoint registration/lifecycle, translation
bundles, translated benchmark packs, external target registration, and
fidelity-aware external benchmark scorecards.

The plan should treat Phase 37's provenance audit as the correction checklist,
then rewrite `materials-discovery/developers-docs/podcast-deep-dive-source.md`
around workflow families rather than command enumeration. Keep enough
Zometool/vZome/math story for the document to remain externally readable, but
make the current shipped system carry slightly more weight than the origin
story. Procedural details belong in cross-links to `RUNBOOK.md`,
`pipeline-stages.md`, `backend-system.md`, the Zomic workflow, and the LLM
runbooks.

**Primary recommendation:** Rewrite the deep dive as a high-level, source-linked
narrative with dated or softened quantitative claims, explicit shipped/future
labels, and a required same-change update to `materials-discovery/Progress.md`.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOC-02 | The refreshed `materials-discovery/developers-docs/podcast-deep-dive-source.md` accurately describes the currently shipped `materials-discovery/` workflow through `v1.6`, including the design, evaluation, serving/checkpoint, translation, and comparative benchmarking surfaces at the right level of fidelity. | Use the Phase 37 stale-surface inventory plus current `mdisc --help`, `developers-docs/index.md`, `pipeline-stages.md`, `RUNBOOK.md`, and milestone audits `v1.0` through `v1.6` as the source-of-truth set. |
| DOC-03 | The refreshed narrative clearly distinguishes shipped capabilities from planned or future work and points readers to the current source-of-truth runbooks and references for deeper technical detail. | Use future-work controls from Phase 37, preserve high-level prose, and add cross-links to current runbooks instead of copying command procedures inline. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- `materials-discovery/` changes must update `materials-discovery/Progress.md`.
- The `Progress.md` update must add a Changelog row with date, short title, and details.
- The `Progress.md` update must append a timestamped Diary entry under today's date heading, reusing the heading if it exists.
- This applies to all `materials-discovery/` changes, including docs.

## Project Constraints (from AGENTS.md)

- Push changes only to the `fork` remote unless explicitly told otherwise.
- Do not push to `origin` unless explicitly requested.
- Do not open pull requests unless explicitly requested.
- If upstream sync is needed, merge or rebase from `origin/main` locally, then push to `fork/main`.
- `materials-discovery/Progress.md` must be updated for all `materials-discovery/` edits with both Changelog and Diary entries.

## Standard Stack

### Core

| Tool or Source | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Markdown files under `materials-discovery/developers-docs/` | repo-native | Long-form narrative and reference documentation | Existing documentation surface is Markdown and link-based. |
| `materials-discovery/developers-docs/podcast-deep-dive-source.md` | current file: 314 lines before Phase 38 | Primary rewrite target | This is the requirement-bound artifact for DOC-02 and DOC-03. |
| `materials-discovery/Progress.md` | current file: 709 lines before Phase 38 | Mandatory progress log for any `materials-discovery/` edit | Required by both `AGENTS.md` and `CLAUDE.md`. |
| Phase 37 provenance audit | `37-PROVENANCE-AUDIT.md`, verified 2026-04-15 | Source-backed stale-claim inventory | Already verified creation history, stale strings, missing shipped surfaces, and tutorial boundary. |
| `mdisc` CLI | local `uv run mdisc --help` succeeded | Current command-surface discovery | Avoids relying on the stale seven-command narrative. |
| `git` | 2.53.0 | Provenance and commit-count snapshots | Phase 37 evidence and D-07 numeric snapshots depend on git commands. |
| `rg` | 15.1.0 | Stale-claim and cross-link verification | Fast repo-native grep for docs verification. |
| `uv` | 0.10.10 | Python environment and command execution | Project-managed runner; `uv run python` provides Python 3.11.15. |

### Supporting

| Tool or Source | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| `pytest` | 9.0.2 via `uv run pytest --version` | Regression smoke for referenced CLI/help surfaces | Use focused CLI tests if implementation changes command references or wants extra confidence. |
| `ruff` | 0.15.5 | Formatting/lint availability | Not normally required for Markdown-only edits, but available. |
| `mypy` | 1.19.1 | Type-check availability | Not normally required for Markdown-only edits, but available. |
| Java | OpenJDK 21.0.10 | Zomic export runtime | Only needed if the implementation chooses to execute `export-zomic` or regenerate Sc-Zn Zomic artifacts; not required for narrative-only validation. |
| `node` | v25.8.1 | GSD tooling | Available for phase metadata and commit tooling. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Command-count prose | Workflow-family prose | Workflow families stay accurate longer and match the external narrative goal. |
| Copying runbook procedures inline | Cross-link current runbooks | Links preserve one technical source of truth and avoid another stale operator manual. |
| Keeping all old numeric claims | Dated snapshots or softened prose | Dated snapshots are honest; softened prose avoids meaningless churn. |
| Editing only the deep-dive file | Deep-dive plus `Progress.md` | `Progress.md` is mandatory whenever `materials-discovery/` changes. |

**Installation:** No new package installation is recommended for Phase 38.
Use the existing workspace:

```bash
cd materials-discovery
uv sync --extra dev
```

**Version verification:** Local versions were verified with:

```bash
uv --version
uv run python --version
uv run pytest --version
uv run ruff --version
uv run mypy --version
git --version
rg --version
java -version
```

## Architecture Patterns

### Recommended Documentation Structure

```text
materials-discovery/
├── developers-docs/
│   ├── podcast-deep-dive-source.md    # primary rewritten narrative
│   ├── index.md                       # docs map and shipped command table
│   ├── pipeline-stages.md             # per-command behavior and artifacts
│   ├── backend-system.md              # backend mode/adapter details
│   ├── zomic-design-workflow.md       # Zomic authoring/export path
│   ├── llm-translation-runbook.md     # translation operator details
│   ├── llm-translated-benchmark-runbook.md
│   ├── llm-external-target-runbook.md
│   └── llm-external-benchmark-runbook.md
└── Progress.md                        # mandatory same-change progress log
```

### Pattern 1: Balanced Narrative Rewrite

**What:** Preserve the first half's story arc around Zometool, vZome, exact
geometry, quasicrystals, and the golden field, then rewrite the implementation
half around the shipped workflow through `v1.6`.

**When to use:** Use for the full target document; avoid a surgical patch that
only inserts a few missing command names.

**Example:**

```markdown
The current system still starts with the same Z[phi] insight, but it no longer
ends at a seven-stage screening loop. The shipped workflow now has a core
design/evaluate/report spine plus file-backed LLM and interoperability branches:
Zomic export, LLM generation and assessment, operator-approved campaigns,
serving and checkpoint comparisons, translation bundles, and external
benchmark scorecards. For command-level details, see
[Pipeline Stages](pipeline-stages.md) and the [Operator Runbook](../RUNBOOK.md).
```

### Pattern 2: Workflow Families, Not Command Enumeration

**What:** Describe capabilities by current product surface:
core design/evaluation; Zomic design/export; LLM generation/evaluation;
campaign governance; serving benchmarks; checkpoint lifecycle; translation;
translated benchmark freeze; external target/benchmark scorecards.

**When to use:** Use whenever replacing "seven pipeline stages" or command
count prose.

**Example:**

```markdown
Think of `mdisc` as a file-backed workflow surface rather than a single linear
script. The core loop still generates, screens, validates, ranks, and reports
candidates; the newer shipped branches add Zomic-authored design input,
LLM-assisted candidate and assessment artifacts, operator-approved campaign
replay, serving/checkpoint comparison, and translated external benchmarks.
```

### Pattern 3: Cross-Link Instead of Procedure Duplication

**What:** Link to current references at the first point where a reader would
need procedural detail.

**When to use:** Use for command syntax, artifact paths, backend adapter details,
translation fidelity, and external benchmark inspection.

**Example:**

```markdown
The narrative should explain why translation exists, not copy the full export
procedure. Link to [LLM Translation Runbook](llm-translation-runbook.md) for
commands and to [LLM Translation Contract](llm-translation-contract.md) for
loss/fidelity semantics.
```

### Pattern 4: Dated Numeric Snapshots

**What:** Keep exact numbers only when they were regenerated from current repo
commands and written as time-bound snapshots.

**When to use:** Use only when the number improves reader understanding.

**Current snapshot commands run during research:**

```bash
git rev-list --count HEAD                                      # 4641
git rev-list --count 359cef57777479fb15652f1f4c702c43a25c4bc6  # 4278
find materials-discovery/src/materials_discovery -type f -name '*.py' | wc -l  # 122
find materials-discovery/src/materials_discovery -type f -name '*.py' -print0 | xargs -0 wc -l | tail -1  # 27857 total
find materials-discovery/tests -type f -name 'test_*.py' | wc -l  # 96
rg -n '@(?:app|lake_app|llm_corpus_app)\.command' materials-discovery/src/materials_discovery/cli.py | wc -l  # 33 decorators
```

**Planning instruction:** Regenerate these at implementation time if any are
kept. Prefer "as of 2026-04-15" language; otherwise soften the claim.

### Anti-Patterns to Avoid

- **Retaining "seven commands" as the main frame:** The CLI now has many more
  surfaces; use workflow families.
- **Turning the deep dive into a runbook:** Keep commands sparse and link to
  source-of-truth docs.
- **Blending future work into current capability:** Label autonomous campaigns,
  checkpoint training automation, reverse import, new exporters, and broad
  chemistry expansion as future work.
- **Copying volatile counts without dates:** D-07 requires regenerated,
  time-bound snapshots.
- **Using old backend vocabulary as the main truth:** Describe `mock` and
  `real` modes with fixture/exec/native adapter layers underneath.
- **Forgetting `Progress.md`:** Any `materials-discovery/` edit without a
  matching progress update violates repo instructions.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Current command inventory | A manually maintained command count in prose | `uv run mdisc --help`, `developers-docs/index.md`, `pipeline-stages.md` | The command surface changes; current docs and CLI are authoritative. |
| Operator workflow details | Inline command walkthroughs in the deep dive | `materials-discovery/RUNBOOK.md` | Keeps the narrative readable and avoids duplicate procedures. |
| Per-command artifact contracts | New tables in the deep dive | `developers-docs/pipeline-stages.md` | This file already lists syntax, inputs, outputs, artifacts, and failure rules. |
| Backend semantics | New simplified layer taxonomy | `developers-docs/backend-system.md` | Existing doc defines modes, registry, fixture, exec, and native provider behavior. |
| Zomic authoring explanation | Re-explaining the design/export contract | `developers-docs/zomic-design-workflow.md` and `vzome-geometry-tutorial.md` | Existing docs separate authoring procedure from mathematical context. |
| Translation fidelity taxonomy | Ad hoc "lossless/lossy" prose | `llm-translation-contract.md` and translation runbooks | v1.5/v1.6 depend on explicit exact/anchored/approximate/lossy semantics. |
| Future roadmap claims | Guessing from intent | `.planning/REQUIREMENTS.md`, `.planning/PROJECT.md`, `.planning/STATE.md` | These files define what is shipped, active, deferred, and future. |

**Key insight:** The deep dive should become an indexable narrative over current
source-of-truth docs, not a second source of truth.

## Common Pitfalls

### Pitfall 1: Legacy Seven-Stage Framing

**What goes wrong:** The document still reads as if the shipped system is only
`ingest` through `report`.

**Why it happens:** The original source predates major post-`v1.0` surfaces.

**How to avoid:** Reframe the implementation section around workflow families
and explicitly include campaigns, serving, checkpoint lifecycle, translation,
and external benchmarking.

**Warning signs:** Phrases like "seven commands", "full seven-stage pipeline",
or no mention of `llm-external-benchmark`.

### Pitfall 2: Stale Numeric Authority

**What goes wrong:** Counts like commits, modules, lines, tests, or commands are
updated once but written as timeless facts.

**Why it happens:** Counts are easy to regenerate but immediately start aging.

**How to avoid:** Keep only useful snapshots, regenerate them during
implementation, and date them in prose.

**Warning signs:** Bare numbers without "as of YYYY-MM-DD" or a nearby source
command.

### Pitfall 3: Future Work Sounds Shipped

**What goes wrong:** Broader autonomous campaigns, checkpoint training,
reverse-import, or chemistry expansion reads like current functionality.

**Why it happens:** Some existing docs include roadmap material adjacent to
implemented sections.

**How to avoid:** Use explicit labels such as "future work", "not shipped in
`v1.6`", or "planned beyond this milestone".

**Warning signs:** "will" or "fully autonomous" language not tied to a future
section.

### Pitfall 4: Runbook Duplication

**What goes wrong:** The deep dive becomes a long command tutorial, competing
with Phase 39 and the runbooks.

**Why it happens:** The current workflow is rich, and copying command examples
feels safer than summarizing.

**How to avoid:** Put one compact current-surface map in the narrative and link
to runbooks for exact commands and artifacts.

**Warning signs:** Multi-step command blocks for campaign, serving, checkpoint,
translation, or external benchmark workflows.

### Pitfall 5: Backend Layer Drift

**What goes wrong:** The document preserves "four execution layers" as though
all four are equivalent user-facing modes.

**Why it happens:** `backend-system.md` still explains four adapter layers, but
the operator vocabulary is `mock` and `real` with fixture/exec/native behavior
under real-mode adapters.

**How to avoid:** Say the workflow has `mock` and `real` modes, then link to
`backend-system.md` for the adapter-layer details.

**Warning signs:** A standalone "Four Layers of Execution" heading in the
refreshed document.

### Pitfall 6: Progress Log Omission

**What goes wrong:** Implementation edits `materials-discovery/` docs but leaves
`Progress.md` unchanged.

**Why it happens:** Phase research and planning artifacts live under
`.planning/`, but Phase 38 implementation does not.

**How to avoid:** Make `Progress.md` update an explicit task in the plan and a
verification item.

**Warning signs:** Diff includes `materials-discovery/developers-docs/...` but
not `materials-discovery/Progress.md`.

## Code Examples

Verified patterns from repo sources:

### Cross-Link Pattern

```markdown
For the command-by-command contract, see
[Pipeline Stages](pipeline-stages.md). For operator sequences and artifact
locations, see the [Operator Runbook](../RUNBOOK.md).
```

### Dated Snapshot Pattern

```markdown
As of 2026-04-15, a local repository snapshot counted 122 Python modules under
`materials-discovery/src/materials_discovery` and 96 `test_*.py` files under
`materials-discovery/tests`. These are orientation numbers, not part of the
system contract.
```

### Future-Work Label Pattern

```markdown
The shipped checkpoint surface can register, benchmark, promote, pin, roll back,
and retire adapted checkpoint family members. Automated checkpoint training is
future work; the current workflow keeps adaptation decisions file-backed and
operator-governed.
```

### Progress Update Pattern

```markdown
| 2026-04-15 | Phase 38 narrative refresh | Refreshed the deep-dive source to describe the shipped workflow through v1.6, added current cross-links, and removed or dated stale claims. |

### 2026-04-15

- HH:MM ET — Phase 38 refreshed `developers-docs/podcast-deep-dive-source.md`
  against the Phase 37 provenance audit and current runbooks; no new workflow
  capability was added.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Seven-stage core pipeline only | Core no-DFT workflow plus additive LLM and interoperability branches | `v1.0` through `v1.6` | Deep dive must describe workflow families, not only stages. |
| Dry-run LLM suggestions | Proposal, approval, launch, replay, and compare campaign workflow | `v1.1`, audited 2026-04-05 | Campaigns are shipped but operator-governed, not autonomous. |
| Hosted-only or abstract LLM model use | Hosted/local/specialized serving lanes with shared serving benchmark | `v1.2`, audited 2026-04-05 | Serving deserves prominent current-state coverage. |
| Single adapted checkpoint experiment | Registered adapted checkpoint lanes with benchmark and rollback guidance | `v1.3`, audited 2026-04-05 | Checkpoints are auditable workflow artifacts. |
| No lifecycle family state | Family lifecycle with promotion, explicit pins, rollback, retirement | `v1.4`, audited 2026-04-06 | The narrative should mention lifecycle governance. |
| QC-native candidates only | Additive CIF/material-string translation bundles with fidelity/loss semantics | `v1.5`, audited 2026-04-07 | Translation is shipped but not a lossless replacement for Zomic-native geometry. |
| Internal benchmark only | Frozen translated packs, immutable external target registration, external-vs-internal scorecards | `v1.6`, audited 2026-04-07 | External benchmarking is current, bounded, and evidence-oriented. |

**Deprecated/outdated:**

- "Seven Pipeline Stages" as the whole system: replace with current workflow
  families.
- "Four Layers of Execution" as the operator story: replace with `mock` /
  `real` mode language and link adapter details.
- "Three real alloy systems": use checked configs and example lanes instead of
  a narrow count.
- Bare `4,238 commits`, `60 modules`, `7,200 lines`, `21 test files`: regenerate
  and date if retained.

## Open Questions

1. **Which refreshed numbers are worth keeping?**
   - What we know: Current research snapshots are available, and D-07 allows
     dated command-derived numbers.
   - What's unclear: Whether the narrative benefits from exact counts.
   - Recommendation: Keep at most one compact dated snapshot if it improves
     credibility; otherwise soften all volatile counts.

2. **Should related stale counts in `developers-docs/index.md` be updated?**
   - What we know: `index.md` still has old module/LOC wording but Phase 38 is
     scoped to `podcast-deep-dive-source.md` plus required `Progress.md`.
   - What's unclear: Whether planner wants to expand scope to avoid linking to
     a doc with a stale status sentence.
   - Recommendation: Do not broaden by default. If the deep dive links to
     `index.md`, rely on its command table and docs map, not its count sentence.

3. **How dense should cross-links be?**
   - What we know: D-03 requires links; D-02 rejects a standalone manual.
   - What's unclear: Exact paragraph-level placement.
   - Recommendation: Link once per workflow family and again in Further
     Reading, not after every command mention.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `git` | provenance, numeric snapshots, diff validation | yes | 2.53.0 | none needed |
| `rg` | stale-claim and link checks | yes | 15.1.0 | `grep`, lower quality |
| `uv` | project command runner | yes | 0.10.10 | none recommended |
| Python via `uv` | `mdisc`, pytest, scripts | yes | 3.11.15 | use `uv run`, not system `python3` |
| system `python3` | direct shell checks only | present but too old for project | 3.9.6 | use `uv run python` |
| `mdisc` | command-surface verification | yes | local package | none needed |
| `pytest` | optional focused regression | yes | 9.0.2 | docs grep checks |
| Java | optional Zomic export execution | yes | OpenJDK 21.0.10 | skip export execution for Phase 38 if not needed |
| `node` | GSD tooling | yes | v25.8.1 | none needed |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None for Phase 38. Use `uv run python`
instead of bare `python3` because the system interpreter is 3.9.6.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` 9.0.2 through `uv run pytest`; docs grep checks for narrative requirements |
| Config file | `materials-discovery/pyproject.toml` (`tool.pytest.ini_options`) |
| Quick run command | `git diff --check && rg -n "4,238 commits|seven commands|60 modules|7,200|21 test files|Seven Pipeline Stages|four execution layers|targets three real alloy systems|full seven-stage pipeline" materials-discovery/developers-docs/podcast-deep-dive-source.md` should return no stale hits after implementation |
| Full suite command | `cd materials-discovery && uv run pytest -q` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| DOC-02 | Deep dive mentions shipped design/evaluation, serving/checkpoint, translation, and external benchmark surfaces through `v1.6`. | docs audit | `rg -n "export-zomic|llm-serving-benchmark|llm-list-checkpoints|llm-promote-checkpoint|llm-retire-checkpoint|llm-translate|llm-translated-benchmark-freeze|llm-register-external-target|llm-external-benchmark" materials-discovery/developers-docs/podcast-deep-dive-source.md` | yes |
| DOC-02 | Deep dive no longer preserves known stale source claims. | docs audit | `rg -n "4,238 commits|seven commands|60 modules|7,200|21 test files|Seven Pipeline Stages|four execution layers|targets three real alloy systems|full seven-stage pipeline" materials-discovery/developers-docs/podcast-deep-dive-source.md` should return no hits | yes |
| DOC-03 | Deep dive links source-of-truth docs instead of duplicating procedures. | docs audit | `rg -n "RUNBOOK.md|pipeline-stages.md|backend-system.md|zomic-design-workflow.md|llm-translation-runbook.md|llm-external-benchmark-runbook.md" materials-discovery/developers-docs/podcast-deep-dive-source.md` | yes |
| DOC-03 | Future/planned work is explicitly labeled. | docs audit | `rg -n "future work|not shipped|planned beyond|not yet|operator-governed" materials-discovery/developers-docs/podcast-deep-dive-source.md` | yes |
| DOC-03 | Mandatory progress tracking is updated with the materials docs edit. | docs audit | `git diff --name-only -- materials-discovery | rg "Progress.md|podcast-deep-dive-source.md"` and inspect both Changelog and Diary entries | yes |

### Sampling Rate

- **Per task commit:** `git diff --check` plus the DOC-02/DOC-03 grep checks.
- **Per wave merge:** `cd materials-discovery && uv run pytest tests/test_cli.py -q` if command references changed materially; otherwise grep checks are sufficient.
- **Phase gate:** Deep-dive stale-claim grep empty, required shipped-surface/link grep populated, `Progress.md` updated, and human read-through confirms shipped/future distinction.

### Wave 0 Gaps

- [ ] No formal Markdown linter or documentation test exists for this specific narrative. The plan should include explicit grep and human-read verification tasks.
- [ ] No new test file is required for a docs-only refresh unless implementation also edits code or CLI behavior.

## Sources

### Primary (HIGH confidence)

- `.planning/phases/38-narrative-refresh-and-cross-linked-deep-dive/38-CONTEXT.md` - locked decisions, scope, discretion, deferred work.
- `.planning/REQUIREMENTS.md` - DOC-02 and DOC-03 requirement text.
- `.planning/STATE.md` - current milestone state and Phase 37 handoff.
- `.planning/PROJECT.md` - current state, shipped milestone summaries, active constraints.
- `.planning/ROADMAP.md` - Phase 38 goal, dependencies, success criteria.
- `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md` - stale claim inventory, shipped-surface list, correction checklist.
- `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-VERIFICATION.md` - verified evidence packet for Phase 37.
- `materials-discovery/developers-docs/podcast-deep-dive-source.md` - current target document.
- `materials-discovery/developers-docs/index.md` - docs map and shipped command table.
- `materials-discovery/RUNBOOK.md` - operator workflow and artifact references.
- `materials-discovery/developers-docs/pipeline-stages.md` - per-command behavior and workflow data flow.
- `materials-discovery/developers-docs/backend-system.md` - backend mode and adapter details.
- `materials-discovery/developers-docs/zomic-design-workflow.md` - current Zomic authoring/export path.
- `materials-discovery/developers-docs/vzome-geometry-tutorial.md` - preserved geometry/math context.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` through `.planning/v1.6-MILESTONE-AUDIT.md` - shipped milestone evidence.
- `materials-discovery/pyproject.toml` - project runtime and test/lint configuration.
- Local command output from `uv run mdisc --help`, `git rev-list`, `find`, and `rg` snapshot commands.

### Secondary (MEDIUM confidence)

- None. No web search was needed because the phase is constrained to internal
  repository documentation and shipped local workflow evidence.

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - verified from local config, CLI, and installed tools.
- Architecture: HIGH - derived from current docs, Phase 37 audit, and milestone audits.
- Pitfalls: HIGH - directly backed by stale source strings and verified Phase 37 correction checklist.
- Environment: HIGH - probed local tools and versions.
- Validation: MEDIUM - grep checks are reliable for required strings, but final narrative quality still requires human read-through.

**Research date:** 2026-04-15
**Valid until:** 2026-05-15 for documentation patterns; regenerate numeric snapshots at implementation time.
