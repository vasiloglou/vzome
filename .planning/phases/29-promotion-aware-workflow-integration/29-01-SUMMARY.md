# Phase 29 Plan 01 Summary

Made new execution promotion-aware across the shared launch path and the manual
`llm-generate` CLI flow.

## Delivered

- Added promoted-family default resolution for `checkpoint_family` lanes while
  preserving explicit family pins and legacy `checkpoint_id`-only behavior.
- Extended `LlmServingIdentity` with checkpoint selection metadata so launch,
  generate, evaluation, and benchmark flows can record how a checkpoint was
  chosen and which lifecycle revision was used.
- Removed the CLI-only serving-identity duplicate so manual generation now
  reuses the same promotion-aware resolver as campaign launch.

## Verification

- `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_registry.py tests/test_llm_launch_core.py tests/test_llm_generate_cli.py -x -v`
  - Result: `34 passed in 0.40s`

## Outcome

New execution now follows the promoted member of a checkpoint family by
default, while still letting operators pin a specific family member
deliberately and audit that choice later.
