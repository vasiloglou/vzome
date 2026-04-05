# Feature Research: v1.3 Zomic-Native Local Checkpoint MVP

## Table Stakes

- register an adapted local checkpoint as a serving lane
- preserve base-model, adaptation, corpus, and eval lineage
- execute adapted checkpoints through generation and campaign launch
- replay and compare adapted-checkpoint runs without forking artifact shapes
- benchmark adapted checkpoints against baseline local lanes on shared context

## Differentiators

- honest Zomic-native acceptance criteria rather than vague “model seems better”
- rollback guidance that keeps baseline local lanes easy to recover
- checkpoint-aware operator workflow integrated into the existing serving
  benchmark ladder

## Anti-Features

- training-farm orchestration
- many-checkpoint fleet management
- automatic campaign execution triggered by checkpoint results
