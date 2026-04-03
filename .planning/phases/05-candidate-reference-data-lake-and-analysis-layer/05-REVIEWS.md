---
phase: 5
reviewers: [gemini, codex]
reviewed_at: 2026-04-03T12:50:00Z
plans_reviewed: [05-CONTEXT.md (pre-planning design review)]
---

# Cross-AI Plan Review — Phase 05

## Gemini Review

This review evaluates the Phase 5 design for the **Candidate/Reference Data Lake and Analysis Layer**.

### 1. Summary
The design for Phase 5 is a pragmatic and highly effective evolution of the existing file-backed architecture. By choosing a decentralized catalog approach (`_catalog.json` per directory) rather than a centralized database or a massive directory reorganization, the plan minimizes migration risk while significantly improving data discoverability. The focus on system-vs-system comparisons and a unified operator runbook directly addresses the goal of transitioning the project from a "collection of scripts" to a "usable platform." The strategy for staleness detection and lineage tracking is particularly well-aligned with the needs of a research-oriented materials discovery pipeline.

### 2. Strengths
- **Minimal Disruption:** Retaining the existing directory structure (D-01) prevents breaking existing scripts and paths, which is critical for maintaining velocity.
- **Decentralized Metadata:** Placing `_catalog.json` files alongside the data (D-02) ensures that metadata travels with the artifacts. This makes manual inspection easier and prevents a single "global catalog" from becoming a bottleneck or a point of corruption.
- **On-Demand Indexing:** The `mdisc lake index` command (D-03) is a smart choice to avoid the performance overhead of updating a global index during high-frequency write operations in the pipeline.
- **Actionable Comparison Granularity:** Focusing on gate-level and aggregate metric distributions (D-07) rather than per-candidate details is the correct approach for system-level tuning and benchmarking.
- **Documentation-First Mindset:** The commitment to a copy-pasteable, troubleshooting-heavy `RUNBOOK.md` (D-12 to D-15) is essential for fulfilling PIPE-05 and ensuring team adoption.

### 3. Concerns
- **Catalog Staleness (MEDIUM):** Since indexing is not auto-updated (D-03), there is a high risk that operators will run analytics or comparisons on stale data. The "staleness flag" mentioned in D-04 is a good start, but the heuristic for detecting it needs to be performant (e.g., checking directory `mtime` vs. `_catalog.json` timestamp).
- **Lineage Fragility (MEDIUM):** Lineage pointers (D-04) are notoriously difficult to maintain in file-backed systems if artifacts are moved or deleted manually. If a `_catalog.json` entry points to a missing run config, the "lakehouse" integrity breaks.
- **Notebook Bit-Rot (MEDIUM):** Jupyter notebooks (D-11) often break when underlying schemas or library versions change. There is no mention of how these notebooks will be tested or kept in sync with the CLI's JSON outputs.
- **Comparison Scope Limitation (LOW):** While system-vs-system is the primary axis (D-05), the design may eventually need to support "version-vs-version" (e.g., same system, different code version) to validate algorithmic improvements.
- **Concurrency Risks (LOW):** If multiple operators or automated runners attempt to update the same `_catalog.json` or the top-level `lake_index.json` simultaneously, there may be race conditions, though this is likely mitigated by the "on-demand" nature of indexing.

### 4. Suggestions
- Implement a "Safe-Analysis" Check: Add a `--check-lake` or `--refresh` flag to `mdisc lake stats` and `compare` that performs a quick validation of the index staleness before proceeding.
- Schema Enforcement: Use Pydantic or a JSON Schema validator within the CLI to ensure every `_catalog.json` adheres to the required format.
- Path Relativization: Ensure all lineage pointers and directory paths are stored as relative paths from the project root for portability.
- Automated Notebook Smoke Tests: Consider a CI test that runs notebooks via `nbconvert --execute` with a small dummy dataset.
- Enhanced Staleness Heuristic: Compare last-modified time of directories against the catalog's `last-modified` field for quick staleness identification.

### 5. Risk Assessment
**Overall Risk: LOW**

The design is conservative and builds directly on patterns already proven in Phases 1-4. The most significant risk is "metadata drift" (staleness), but this is an operational risk rather than a structural one.

---

## Codex Review

### 1. Summary
The Phase 5 direction is good: a file-backed catalog/index plus comparison and operator tooling is the right next step, and it fits the repo's existing provenance-heavy architecture instead of forcing a storage rewrite. The main design risk is not the lakehouse idea itself, but unresolved contracts around what exactly gets cataloged, how freshness/staleness is determined, and what data `mdisc lake compare` will actually read to produce the promised analytics. If those contracts are nailed down early, this phase is moderate-risk and likely to land cleanly.

### 2. Strengths
- The design is aligned with the current architecture. Existing provenance hooks in benchmarking.py and benchmark-pack emission in cli.py give a real foundation for a metadata overlay.
- Choosing an additive catalog/index layer instead of reorganizing `data/` is the right call for a live research pipeline.
- Dual-format comparison output is well judged: JSON for downstream tooling, CLI table for operators.
- Explicit benchmark-pack inputs for comparison favor reproducibility and avoid hidden discovery rules.
- A single operator runbook is the right deliverable for PIPE-05.

### 3. Concerns
- **Artifact Inventory Gap (HIGH):** D-01's "existing layout" inventory is narrower than the actual artifact surface. The repo uses `processed/`, `candidates/`, `screened/`, `hifi_validated/`, `ranked/`, `active_learning/`, and `prototypes/` in addition to the directories listed. If the lake formalizes only the listed subset, it will miss core operator-visible outputs.
- **Freshness Authority Model (HIGH):** D-02/D-03 do not define the authority model for freshness. If `_catalog.json` files are persistent but `lake_index.json` is on-demand, it is unclear when per-directory catalogs are regenerated and how drift is detected.
- **Comparison Data Depth (HIGH):** D-07 promises gate-level plus aggregate metric distributions, but the current benchmark pack only persists a thin summary slice. `mdisc lake compare` cannot produce mean/min/max/std robustly unless it reads deeper artifacts or the benchmark-pack schema is expanded.
- **Comparison Axis Limitation (MEDIUM):** "System-vs-system" as the primary comparison axis is not enough to fully support PIPE-04. The most diagnostic comparisons for source-aware enrichment are same-system, cross-lane: baseline vs reference-aware, source-pack A vs B.
- **Multi-Batch Under-Modeling (MEDIUM):** Current report-time pipeline manifest assembly only includes the first matched validated batch file, not all batches.
- **Catalog Unit Ambiguity (MEDIUM):** `_catalog.json` at the directory level is ambiguous for flat mixed directories like `data/reports/` and `data/manifests/`. Needs a clear unit of cataloging.
- **Documentation Duplication (MEDIUM):** RUNBOOK.md, existing developer docs, README snippets, and notebooks can easily become four competing sources of truth.
- **Indexer Performance (LOW):** A naive indexer that fully reads every JSONL to count records will get slow as corpora grow.
- **Schema Version Validation (LOW):** Explicit path-based compare inputs should validate schema versions.

### 4. Suggestions
- Define the artifact inventory first. Make an explicit list of all Phase-5-cataloged artifact classes before coding the indexer.
- Decide one freshness contract up front: either catalogs are generated on demand alongside the index, or producing commands refresh local catalogs as part of their write path.
- Make the internal comparison model lane-centric, not system-centric. Keep "system-vs-system" as a preset view, not as the hard-coded abstraction.
- Decide the compare input contract now: either enrich benchmark-pack to carry all aggregate metrics, or make compare dereference benchmark-pack pointers.
- Use manifest hashes and config hashes for staleness where possible; use timestamps only as hints.
- Prefer workspace-relative lineage paths in catalog artifacts.
- Sequence implementation as: catalog schema and inventory, index generation, compare engine, notebooks, then RUNBOOK.md.
- Make RUNBOOK.md the operator source of truth and reduce README/developer docs to links plus brief entry points.

### 5. Risk Assessment
**Overall Risk: MEDIUM**

The architecture choice is sound. The risk comes from contract ambiguity, not technical impossibility: if catalog scope, freshness semantics, and comparison inputs are left fuzzy, Phase 5 will drift into tooling churn and documentation duplication. Fix those three points first.

---

## Consensus Summary

### Agreed Strengths
- **Additive catalog approach is correct** — both reviewers endorsed keeping the existing directory layout (D-01) and adding metadata on top rather than reorganizing. This minimizes migration risk in a live research pipeline.
- **Dual-format comparison output** — JSON for programmatic use plus CLI table for operators is well-judged for the audience.
- **On-demand indexing** — avoids overhead of auto-updating during pipeline writes.
- **Unified RUNBOOK.md** — both agree this is the right deliverable for PIPE-05 and team adoption.
- **Builds on proven patterns** — existing provenance machinery (manifests, benchmark contexts, hashes) provides a solid foundation.

### Agreed Concerns
1. **Staleness/freshness contract is undefined (HIGH)** — Both reviewers flagged that the design does not specify when `_catalog.json` files are regenerated or how drift between catalogs and actual artifacts is detected. This is the top priority to resolve before planning.
2. **Comparison data depth may be insufficient (HIGH/MEDIUM)** — The current benchmark-pack schema may not carry enough aggregate metrics for the promised mean/min/max/std comparison output. The compare command's data source needs explicit definition.
3. **Notebook maintainability (MEDIUM)** — Gemini raised bit-rot risk; Codex raised documentation duplication. Both point to notebooks needing testing and clear ownership relative to CLI commands.
4. **Lineage pointer fragility (MEDIUM)** — File-backed lineage pointers break if artifacts are moved or deleted. Relative paths and hash-based references are preferred over absolute paths.
5. **System-vs-system may be too narrow for PIPE-04 (MEDIUM)** — Both reviewers noted that source-aware enrichment validation needs cross-lane comparisons (baseline vs reference-aware), not just cross-system.

### Divergent Views
- **Overall risk level:** Gemini rated LOW, Codex rated MEDIUM. The difference is that Codex identified three HIGH-severity contract gaps (artifact inventory, freshness model, comparison data depth) while Gemini saw mostly MEDIUM operational risks. Codex's concern about the artifact inventory being narrower than the actual directory surface is worth investigating.
- **Artifact scope:** Codex flagged that D-01's directory list may miss `processed/`, `candidates/`, `screened/`, `hifi_validated/`, `ranked/`, `active_learning/`, and `prototypes/` directories. Gemini did not raise this. This should be verified against the actual codebase.
- **Comparison abstraction:** Codex suggested making the comparison model lane-centric internally (with system-vs-system as a view), while Gemini accepted the system-vs-system scope as sufficient for Phase 5.

---

*Phase: 05-candidate-reference-data-lake-and-analysis-layer*
*Reviewed: 2026-04-03*
