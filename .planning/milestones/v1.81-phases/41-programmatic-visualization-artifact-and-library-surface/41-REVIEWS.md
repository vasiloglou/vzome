---
phase: 41
requested_reviewers: [gemini, claude, codex]
completed_reviewers: [gemini, claude]
skipped_reviewers: [codex]
reviewed_at: 2026-04-15T15:56:28Z
plans_reviewed:
  - 41-01-PLAN.md
---

# Cross-AI Plan Review — Phase 41

`codex` was intentionally skipped for this review because the current runtime is
already Codex, and the review workflow prefers independent external feedback.

## Gemini Review

This review evaluates implementation plan **41-01-PLAN.md** for Phase 41 of the Materials Design Program.

### 1. Summary
The plan is exceptionally well-aligned with the milestone goals and architectural constraints. It correctly identifies the existing `*.raw.json` as the stable input contract and focuses on building a Python-first visualization library (`materials_discovery.visualization`) that generates standalone, interactive HTML viewers. By avoiding a dependency on the full `online/` stack or a long-running service, the plan delivers a lightweight, tutorial-ready solution that is easy to embed in notebooks and document in Markdown.

### 2. Strengths
*   **Contract Alignment:** Correctly reuses the existing `mdisc export-zomic` and `ExportZomicLabeledGeometry.java` artifacts, ensuring no duplication of export logic.
*   **Minimalist Architecture:** The decision to produce a self-contained HTML/Canvas viewer with inline JavaScript avoids introducing Node/Yarn/Three.js build complexities into the Python-centric `materials-discovery` package.
*   **API Design:** The library-first approach (`preview_zomic_design` helper) ensures that both the CLI and future Notebook integration share a single, stable code path.
*   **Scope Discipline:** Explicitly deferring `.vZome` and `.shapes.json` parity keeps the implementation focused on the "tutorial-first" requirement.
*   **Validation Rigor:** Includes specific regression tests to ensure the new viewer doesn't break the existing contracts relied upon by LLM tooling.

### 3. Concerns
*   **Vanilla JS Implementation (LOW):** Implementing 3D rotation, zoom, and projection from scratch in Vanilla JS (to avoid remote CDN assets or Node build steps) is non-trivial. While suitable for simple points and segments, it requires careful handling of the projection matrix and interaction events.
*   **Centroid vs. Origin (LOW):** The plan calls for recentering around the labeled-point centroid. While excellent for "auto-framing" the tutorial design, the viewer should also include a visual indicator of the original Zomic origin `(0,0,0)` if available, as that helps designers understand the motif's anchoring.
*   **Missing Sites/Segments (LOW):** The loader should gracefully handle "empty" designs (e.g., zero segments but many points) without crashing the normalization or bounds calculation.

### 4. Suggestions
*   **Viewer Metadata:** Ensure the `RawExportViewModel` and the rendered HTML include the `source_zomic` path and symmetry name in a header or tooltip to provide context during programmatic previews.
*   **Coordinate Precision:** When serializing the `VIEW_MODEL` into the HTML, use a stable precision (e.g., 6 decimal places) to keep the file size small while maintaining geometric fidelity.
*   **Style Parity:** In Task 1, define the "fixed local palette" for orbits to match the standard vZome desktop colors (e.g., blue, yellow, red, green) to ensure visual consistency for users transitioning between tools.

### 5. Risk Assessment: LOW
The risk is low because the plan is additive and surgical. It introduces a new package and a new CLI command without modifying core generator or evaluation logic. The "standalone HTML" strategy provides a robust fallback that works in any browser or notebook environment without requiring additional system-level services.

**The plan is approved for execution.**

---

## Claude Review

# Phase 41 Plan Review: Programmatic Visualization Artifact and Library Surface

## Plan 41-01

### Summary

This is a well-scoped, tightly aligned single-plan phase that adds a self-contained raw-export visualization library, a thin CLI wrapper, and a narrow reference doc. The plan correctly inherits every locked decision from the context and research phases, avoids scope creep into `.vZome`/`.shapes.json` parity, and reuses the existing export contract rather than replacing it. The three-task decomposition is clean: core library, CLI integration, docs. The main risks are minor — a few implicit assumptions about the raw export schema and one missing validation edge case — but nothing that threatens the phase goal.

### Strengths

- **Tight scope alignment.** The plan explicitly traces back to VIS-01 and VIS-02, names the exact artifacts, and stays within the locked Phase 41 boundary. No general-purpose visualization platform, no service, no Node/Yarn dependency.
- **Correct dependency ordering.** Task 1 builds the library, Task 2 wires it to the CLI, Task 3 writes docs. Each task reads the outputs of the previous one. No circular or out-of-order dependencies.
- **Reuse over invention.** The plan reuses `export_zomic_design()`, `_infer_orbit_name`, `ZomicExportSummary`, and the existing CLI error-handling pattern (`_emit_error` + exit code 2). No parallel implementation paths.
- **TDD discipline.** Tasks 1 and 2 are marked `tdd="true"` with concrete test behaviors listed before the implementation action. The test expectations are specific enough to be falsifiable (e.g., "duplicate segment records collapse to one normalized segment by signature").
- **Self-contained HTML approach.** The inline-JS-in-HTML design avoids a build step, avoids runtime dependencies on the `online/` stack, and produces an artifact that a notebook can embed later. This is the right call for a tutorial-first MVP.
- **Explicit boundary language in docs task.** Task 3 requires the reference doc to state that desktop vZome remains the authoring tool and that `.vZome`/`.shapes.json` parity is deferred. This prevents downstream misunderstanding.
- **Compatibility regression coverage.** The plan-level verify step includes `test_zomic_bridge.py` and `test_llm_native_sources.py` to confirm the new code doesn't break the existing raw export consumers.
- **Progress.md compliance.** Task 3 explicitly includes the mandatory changelog row and diary entry per AGENTS.md and CLAUDE.md.

### Concerns

- **MEDIUM — Segment endpoint extraction is under-specified.** The plan says "fall back to `start.components[].evaluate` and `end.components[].evaluate`" for segment coordinates. Looking at the Java exporter (`ExportZomicLabeledGeometry.java` lines 173-179), segments emit `start` and `end` as `vectorMap()` outputs containing nested `components[].evaluate` but no top-level `cartesian` array like labeled points have. The plan acknowledges this asymmetry but doesn't specify what happens if `components` is missing or malformed. A segment with no extractable coordinates should raise a clear `ValueError`, not silently drop.

- **MEDIUM — No test for the committed checked artifact.** The plan tests against synthetic `tmp_path` fixtures, which is correct for unit tests. But there is no integration-style test or manual verification step that actually loads `data/prototypes/generated/sc_zn_tsai_bridge.raw.json` (the 52-point, 52-segment checked file) through the new library. If the real file has schema surprises not captured by the synthetic fixtures, they'll surface late. Consider adding one test that loads the real committed file (guarded by `Path.exists()` so CI doesn't break if the file is absent).

- **MEDIUM — `--design` and `--raw` mutual exclusivity not specified.** The plan says "Either `--design` or `--raw` must be provided" and "It is valid to provide only one of them." But it doesn't specify what happens when **both** are provided. The most defensive choice is to reject the both-provided case with exit code 2, but the plan is silent. This ambiguity could lead to surprising behavior where `--design` silently wins and `--raw` is ignored.

- **LOW — Orbit color palette is implementation-internal but test-visible.** Task 1 says "Assign orbit colors from a fixed local palette constant." If `RawExportViewModel` exposes colors as a field (it's a `BaseModel`), downstream consumers in Phase 42/43 may depend on the exact palette. The plan doesn't specify whether the palette is a public contract or an internal detail. Marking it clearly as internal (leading underscore on the constant, not on the model field) would prevent accidental coupling.

- **LOW — `webbrowser.open()` in tests.** Task 2 mentions monkeypatching browser opening, which is good. But the behavior spec says "`--open-browser` is optional and defaults to `false` in the JSON summary" without explicitly stating that tests must patch `webbrowser.open` to prevent actual browser launches during CI. The monkeypatch mention in the action section covers this, but the behavior spec should be tighter.

- **LOW — HTML size for notebook embedding.** The self-contained HTML will embed the full normalized JSON model inline. For the checked Sc-Zn file (52 points, 52 segments), this is small. But the plan doesn't cap the inline data size or mention any guard for larger future exports. Not a Phase 41 concern (scope is tutorial-first), but worth noting as a Phase 43 consideration.

- **LOW — No explicit mention of `py.typed` or `__all__`.** The `__init__.py` exports are specified, but the plan doesn't mention whether to add `__all__` for explicit public API control. This is a minor code hygiene item, not a functional risk.

### Suggestions

1. **Add one real-artifact smoke test.** In `test_zomic_visualization.py`, add a test that loads the committed `sc_zn_tsai_bridge.raw.json` if it exists, calls `build_view_model()`, and asserts `labeled_point_count == 52` and `segment_count == 52`. Guard with `pytest.mark.skipif(not path.exists(), ...)` so it doesn't break in CI without the file.

2. **Specify both-provided behavior for `--design` and `--raw`.** Add a sentence: "When both `--design` and `--raw` are provided, `--design` takes precedence and `--raw` is ignored" OR "reject with exit code 2." Either is fine; silence is not.

3. **Add a `ValueError` spec for malformed segments.** In Task 1's action, add: "If a segment's start or end coordinates cannot be extracted, raise `ValueError` with a message naming the segment signature."

4. **Name the palette constant with a leading underscore.** Use `_ORBIT_PALETTE` in `raw_export.py` to signal it is not part of the public API contract.

5. **Consider adding `show_labels` to `ZomicPreviewSummary`.** The CLI wrapper doesn't expose `--show-labels` / `--no-show-labels`. If Phase 42/43 wants the tutorial to default to labels-on, the CLI would need a follow-up change. Adding the flag now (defaulting to `False`) costs nothing and avoids a later additive PR.

### Risk Assessment

**Overall: LOW**

The plan is well-researched, correctly scoped, and aligned with both the phase goals and the locked implementation decisions. The three concerns rated MEDIUM are all edge-case specification gaps rather than architectural risks — they can be resolved in a few sentences of additional spec without changing the plan structure. The dependency ordering is correct, the test coverage is concrete, and the boundary language prevents scope creep. This plan is ready for execution with minor clarifications.

---

## Consensus Summary

Both reviewers agree that Phase 41 is well-scoped, additive, and ready for
execution. Neither reviewer raised a HIGH-severity blocker. The shared message
is that the overall architecture is right, but the plan will execute more
cleanly if a few edge-case contracts are made explicit before or during
implementation.

### Agreed Strengths

- The plan reuses the existing `mdisc export-zomic` and raw-export contract
  instead of inventing a second export path.
- The Python-first library plus thin `preview-zomic` wrapper is the right
  stable surface for later tutorial and notebook work.
- The self-contained HTML approach keeps the MVP local, lightweight, and free
  of `online/` stack, Node, Yarn, or service dependencies.
- The phase stays disciplined about scope and explicitly defers `.vZome` /
  `.shapes.json` parity and broader browser authoring.
- The test strategy is concrete and includes compatibility checks against the
  existing raw-export consumers.

### Agreed Concerns

- **Top concern:** raw export edge cases need tighter specification. Both
  reviews point at malformed or missing point/segment data as a place where the
  implementation should fail clearly rather than silently degrading.
- The viewer implementation is low risk overall, but the standalone canvas /
  inline-JavaScript path still deserves careful handling because basic 3D
  rotation, projection, and interaction logic are easy to underspecify.
- A couple of public-contract details should be made explicit before execution:
  what happens when both `--design` and `--raw` are supplied, and whether the
  orbit palette is a public contract or an internal implementation detail.

### Divergent Views

- Gemini sees the plan as already approved for execution and focuses mostly on
  polish items: viewer metadata, stable coordinate precision, origin cues, and
  color parity with desktop vZome.
- Claude is slightly more conservative and wants a few contract clarifications
  nailed down first: malformed-segment behavior, one smoke test against the
  committed raw artifact, and explicit CLI handling for the both-provided
  `--design` / `--raw` case.

### Suggested Pre-Execution Tightening

If the team wants to incorporate the review feedback before execution, the
highest-value planning edits are:

1. Say explicitly that malformed segment coordinate data raises `ValueError`
   with a segment-specific message.
2. Define whether `preview-zomic` rejects or prioritizes the both-provided
   `--design` / `--raw` case.
3. Add one smoke-test expectation against the committed
   `sc_zn_tsai_bridge.raw.json` artifact when present.
