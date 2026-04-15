# Phase 8 Validation

## Required checks

### Plan 01

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_evaluate_schema.py tests/test_llm_evaluate_cli.py -x -v`

### Plan 02

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_report.py tests/test_hifi_rank.py -x -v`

### Plan 03

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_pipeline_benchmarks.py tests/test_cli.py -x -v`
- `bash -n /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/scripts/run_llm_pipeline_benchmarks.sh`

### Phase close

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
- `git diff --check`

## Must-haves

- `llm-evaluate` writes a typed assessment artifact family plus run manifest.
- `report` surfaces LLM assessment when present and remains backward compatible when absent.
- A two-system downstream benchmark exists for deterministic vs LLM lanes.
- `materials-discovery/Progress.md` is updated for every Phase 8 change.
