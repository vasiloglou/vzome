---
phase: 42
requested_reviewers: [gemini, claude, codex]
completed_reviewers: [gemini]
failed_reviewers: [claude]
skipped_reviewers: [codex]
reviewed_at: 2026-04-15T16:39:48Z
plans_reviewed:
  - 42-CONTEXT.md (pre-planning design review)
---

# Cross-AI Plan Review — Phase 42

Phase 42 does not have `PLAN.md` files yet, so this review was run as a
pre-planning design review against `42-CONTEXT.md`, the roadmap section, and
the phase requirements.

`codex` was intentionally skipped for this review because the current runtime
is already Codex, and the workflow prefers independent external feedback.

## Gemini Review

This is a pre-planning design review for **Phase 42: Extensive Guided Tutorial Expansion**.

### 1. Summary
Phase 42 represents a critical transition from "cataloging features" to "authoring a narrative workflow." By establishing the deterministic Sc-Zn evidence chain as a "spine" and treating LLM workflows as explicit branches, the design provides a clear mental model for operators. The integration of the Phase 41 programmatic visualization path is a major UX win, reducing the friction of mandatory context-switching to the desktop application for basic verification. The plan is pragmatically grounded, acknowledging where automation ends and where desktop vZome’s specialized authoring still reigns.

### 2. Strengths
*   **Narrative Continuity:** Using a "spine and branch" approach (D-01, D-02) prevents the documentation from feeling like a disconnected list of commands, helping users understand *when* and *why* to pivot to LLM-assisted discovery.
*   **Artifact-Centric Teaching:** The focus on "command -> output path -> signal interpretation" (D-11, D-12) aligns with senior engineering needs for transparency and "evidence-based" discovery.
*   **Visual Integration:** Moving the "happy path" visualization into the repo (D-08, D-09) significantly improves the developer experience by keeping the feedback loop within the terminal/notebook context.
*   **Honest Positioning:** Explicitly labeling future work and defining the boundaries of the repo-owned viewer vs. desktop vZome (D-10, D-15) manages user expectations and prevents "feature parity" frustration.
*   **Pragmatic Reuse:** D-07 (reusing Al-Cu-Fe for external benchmarks) avoids "fixture bloat" while maintaining the pedagogical value of the tutorial.

### 3. Concerns
*   **Chemistry Context Switch (MEDIUM):** Transitioning from Sc-Zn (deterministic) to Al-Cu-Fe (external benchmarks) in one document can be jarring. If not handled with clear visual or structural cues (e.g., a "Context Switch" callout), the reader may lose the "evidence chain" logic the phase aims to preserve.
*   **Visualization "Uncanny Valley" (LOW):** As the repo-owned viewer becomes the "primary" surface (D-09), users may inadvertently expect it to handle complex `.vZome` files or richer rendering features. The tutorial must strictly define the "Preview" vs. "Inspect" boundary to avoid bug reports for missing desktop-level features.
*   **Command Proliferation (LOW):** The sheer number of commands to be demonstrated in the translation branch (D-05) risks "command fatigue." There is a risk that the tutorial becomes a wall of CLI outputs rather than a guided walkthrough.
*   **Branching Complexity (MEDIUM):** If the "same-system LLM branch" and "external benchmark branch" are interleaved too closely, the "deterministic spine" might get lost.

### 4. Suggestions
*   **Visual Branching Diagram:** Include a simple Mermaid or ASCII diagram at the top of the tutorial (and at branch points) to show the reader where they are in the discovery lifecycle (Spine vs. Branch A vs. Branch B).
*   **"Why this Chemistry?" Callouts:** In the translation section (D-07), explicitly add a "Data Availability" note explaining that Al-Cu-Fe is used because it represents a richer external benchmark target, reinforcing the "Reference-Aware" discovery theme.
*   **The "Handoff" Section:** Create a dedicated "When to open Desktop vZome" table or checklist. This reinforces D-10 by providing clear heuristics (e.g., "Use CLI for symmetry verification; use Desktop for manual orbit tuning").
*   **Foldable CLI Output:** If the Markdown allows, or via strategic use of snippets, ensure that long JSON or Zomic outputs don't bury the "Interpretation" text. The "What the signal means" (D-11) should always be the most prominent part of the page.
*   **Cross-Link to Runbooks:** Since campaign/serving workflows are "lighter-weight" (D-06, D-13), ensure every mention ends with a "Deep Dive" link to the relevant full-length runbook to satisfy power users without bloating the tutorial.

### 5. Risk Assessment: LOW
The risk is low because the phase focuses on documentation and existing CLI surfaces rather than new mechanical logic.

**Justification:**
The primary challenges are pedagogical and structural rather than technical. The dependency on Phase 41 is the only technical risk; provided the visualization surface is stable, this phase is essentially a "knowledge-mapping" exercise. The "Chemistry Handoff" is the most likely point of user confusion, but it is easily mitigated with clear labeling. The scope is well-defined and explicitly excludes "parity" traps that usually sink documentation-heavy phases.

---

## Claude Review

Reviewer unavailable. The `claude` CLI is installed on this machine but was not
authenticated at review time and returned:

```text
Not logged in · Please run /login
```

---

## Consensus Summary

Only one independent external review completed successfully for this phase, so
the items below should be treated as single-review guidance rather than
cross-review consensus.

### Agreed Strengths

- The deterministic-spine plus explicit-branches structure looks like the right
  teaching model for Phase 42.
- The repo-owned preview path appears to improve tutorial ergonomics without
  overclaiming parity with desktop vZome.
- Reusing the existing Al-Cu-Fe translation/external benchmark fixtures is a
  reasonable way to avoid fixture sprawl while still demonstrating the shipped
  workflow family.

### Agreed Concerns

1. **Top concern:** the Sc-Zn to Al-Cu-Fe chemistry handoff needs explicit
   narrative framing so readers understand why the tutorial changes context and
   do not lose the evidence-chain story.
2. The tutorial must be disciplined about the preview boundary so the new
   programmatic viewer is understood as a checked preview path, not as desktop
   vZome parity.
3. The translation/external benchmark branch is at risk of becoming a command
   dump unless the plan intentionally emphasizes interpretation over raw output
   volume.
4. Branch ordering matters: if the same-system LLM branch and the external
   benchmark branch are woven together too tightly, the deterministic spine may
   blur.

### Divergent Views

No divergent-view analysis is possible because only one independent reviewer
completed successfully.

### Suggested Planning Follow-Ups

The highest-value changes to fold into `gsd-plan-phase 42 --reviews` are:

1. Add one explicit "context switch" or "why this chemistry" design element
   for the Al-Cu-Fe translation/external benchmark branch.
2. Reserve a small, explicit section for "When to use the repo preview vs.
   when to open desktop vZome."
3. Plan the tutorial around interpretation checkpoints and branch diagrams so
   the extra commands do not collapse into a long, unstructured CLI list.

