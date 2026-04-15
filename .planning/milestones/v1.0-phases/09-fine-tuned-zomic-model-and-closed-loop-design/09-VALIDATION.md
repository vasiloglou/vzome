# Phase 9 Validation

## Required checks

### Plan 01

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_acceptance_schema.py -x -v`

### Plan 02

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_generate_cli.py -x -v`

### Plan 03

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_acceptance_benchmarks.py tests/test_cli.py -x -v`
- `bash -n /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/scripts/run_llm_acceptance_benchmarks.sh`

### Phase close

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
- `git diff --check`

## Must-haves

- A typed acceptance/eval-set artifact family exists for Phase 9.
- `llm-generate` can optionally consume composition-conditioned examples without
  changing the candidate output schema.
- An operator-facing acceptance benchmark exists for deterministic vs LLM lanes.
- `materials-discovery/Progress.md` is updated for every Phase 9 change.
