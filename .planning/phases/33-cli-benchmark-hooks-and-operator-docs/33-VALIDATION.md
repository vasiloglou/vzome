---
phase: 33
slug: cli-benchmark-hooks-and-operator-docs
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-06
last_updated: "2026-04-06T00:00:00Z"
---

# Phase 33 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | `pytest` via `uv run pytest` |
| Config file | `materials-discovery/pyproject.toml` |
| Quick run command | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_bundle.py tests/test_llm_translation_cli.py -x -v` |
| Full phase command | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_bundle.py tests/test_llm_translation_cli.py tests/test_cli.py tests/test_llm_translation_export.py tests/test_llm_translation_cif.py tests/test_llm_translation_material_string.py tests/test_llm_translation_export_fixtures.py tests/test_llm_translation_schema.py tests/test_llm_translation_core.py tests/test_llm_translation_fixtures.py -x -v` |
| Estimated runtime | ~20 seconds |

## Sampling Rate

- After every task commit: run the focused suite for the touched plan
- After every plan wave: run the quick phase command
- Before verification: run the full phase command

## Per-Task Verification Map

| Task ID | Plan | Requirement | Automated Command | Status |
|---------|------|-------------|-------------------|--------|
| 33-01-01 | 01 | OPS-15 | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_bundle.py -x -v` | ⬜ pending |
| 33-01-02 | 01 | OPS-15 | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_bundle.py -x -v` | ⬜ pending |
| 33-02-01 | 02 | OPS-15 | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_cli.py -x -v` | ⬜ pending |
| 33-02-02 | 02 | OPS-15 | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_cli.py -x -v` | ⬜ pending |
| 33-03-01 | 03 | OPS-16 | documentation-only; verify via doc review plus phase full command | ⬜ pending |
| 33-03-02 | 03 | OPS-15, OPS-16 | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_cli.py -x -v` | ⬜ pending |

## Wave 0 Requirements

- Existing `pytest` infrastructure is already sufficient.
- No new harness/bootstrap work is required before execution.

## Manual-Only Verifications

- Review the new runbook wording to ensure it states the fidelity/loss boundary
  plainly and does not imply CIF/material-string replace Zomic as the source of
  truth.

## Validation Sign-Off

- [x] Every execution task has an automated verification command or explicit doc-only review
- [x] Wave 0 is complete
- [x] `nyquist_compliant: true` set in frontmatter

