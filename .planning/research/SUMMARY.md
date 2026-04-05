# Research Summary: v1.2 Local and Specialized LLM Serving MVP

## Milestone direction

The strongest next milestone is to expand the shipped closed-loop LLM workflow
from `mock + one hosted seam` into a real serving surface with local execution
and specialized materials-model lanes.

## Stack additions

- No new top-level platform is required.
- Stay with Python 3.11, Typer, Pydantic, and file-backed manifests.
- Add a local serving adapter seam and richer lane-aware runtime metadata under
  `materials_discovery/llm/`.

## Feature table stakes

- local lane execution for `llm-generate`
- deterministic lane resolution for hosted vs local vs specialized paths
- auditable provider/model/checkpoint lineage
- compatibility with `llm-launch`, `llm-replay`, and `llm-compare`
- operator-visible smoke tests and benchmark comparisons

## Architecture guidance

- Extend the existing `llm/runtime.py`, `llm/launch.py`, `llm/replay.py`, and
  `common/schema.py` surfaces rather than creating a parallel inference stack.
- Keep serving mode additive to the current closed-loop workflow.
- Treat specialized materials models as workflow lanes, not as ad hoc one-off
  scripts.

## Watch out for

- hidden fallback from specialized lanes to generic hosted paths
- local dependency or endpoint drift that only fails after long runs start
- weak lineage that loses checkpoint or endpoint identity
- apples-to-oranges comparisons between hosted and local benchmarks
- scope creep into autonomous execution or training orchestration

## Recommended scope boundary

Ship a credible local/specialized serving MVP now. Defer autonomous campaign
execution and training automation until operators can compare the expanded lane
surface confidently.
