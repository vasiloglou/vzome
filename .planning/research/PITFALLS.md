# Pitfalls Research: v1.2 Local and Specialized LLM Serving MVP

## Common failure modes

- **Config drift:** local endpoint or checkpoint configuration changes after
  approval, but operators only notice once generation starts.
- **Silent fallback:** a specialized lane request quietly runs on a generic
  hosted path.
- **Weak lineage:** manifests record a lane name but not the actual local model
  identity, endpoint, or checkpoint.
- **Unfair comparisons:** hosted and local benchmarks are compared without the
  same acceptance or benchmark context.
- **Scope creep:** serving expansion drifts into training automation or
  autonomous execution before the operator workflow is ready.

## Prevention strategy

- fail fast on missing local serving prerequisites
- record both requested lane and resolved runtime identity
- benchmark all lanes against the same saved context
- keep replay strict so local/specialized runs stay reproducible
- defer autonomy and training work explicitly in the milestone scope
