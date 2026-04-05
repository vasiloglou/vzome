# Stack Research: v1.3 Zomic-Native Local Checkpoint MVP

## Keep

- Python 3.11
- existing `materials-discovery` CLI and schema stack
- local OpenAI-compatible serving seam from `v1.2`
- file-backed manifests, JSON/JSONL artifacts, and deterministic lane
  resolution

## Add

- checkpoint metadata and registration schema
- checkpoint compatibility validation helpers
- checkpoint-aware serving identity and drift checks
- adapted-vs-baseline benchmark configs and storage references

## Avoid

- introducing a separate training platform inside this milestone
- making in-process model execution the headline
- new UI or orchestration layers
