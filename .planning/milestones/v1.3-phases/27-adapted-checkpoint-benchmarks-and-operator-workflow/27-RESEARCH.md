# Phase 27 Research

## Existing Surfaces

- Phase 21 already shipped `mdisc llm-serving-benchmark`.
- Phase 26 already proved the adapted lane can pass through launch, replay,
  compare, and benchmark compatibility.

## Remaining Gap

Operators still needed explicit answers to:

- how to register the checkpoint before using the adapted lane
- what files the adapted workflow writes
- how to compare adapted vs baseline honestly
- how to roll back cleanly if the adapted lane underperforms
