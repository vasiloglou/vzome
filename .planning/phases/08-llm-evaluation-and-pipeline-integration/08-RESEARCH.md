# Phase 8 Research

## Local primary sources reviewed

- `.planning/ROADMAP.md` Phase 8 section
- `.planning/REQUIREMENTS.md` (`LLM-03`, `LLM-04`)
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/src/materials_discovery/llm/generate.py`
- `materials-discovery/src/materials_discovery/hifi_digital/rank_candidates.py`
- `materials-discovery/src/materials_discovery/diffraction/compare_patterns.py`
- `materials-discovery/src/materials_discovery/cli.py`

## Key implementation observations

- The codebase already has a stable additive pattern for stage-specific context:
  stage manifest + calibration JSON + richer run-level artifact.
- Ranked candidates already carry provenance blocks; reports already surface
  those provenance details in the `evidence` section.
- That means `llm-evaluate` can attach its assessment block to candidate
  provenance and only needs minimal report changes to become visible.
- A full second scoring system is not required for Phase 8.

## Phase 8 requirement interpretation

- `LLM-03`: deliver a usable LLM-evaluation path that records assessment outputs
  and threads them into downstream human-facing artifacts.
- `LLM-04`: prove LLM-generated candidates can run through the rest of the
  pipeline and produce benchmarkable downstream metrics.

## Risk notes

- Avoid letting assessment fields leak into deterministic ranking weights.
- Keep report integration additive and transparent.
- Keep benchmarks offline and deterministic in tests even if the runtime also
  supports hosted-provider execution.
