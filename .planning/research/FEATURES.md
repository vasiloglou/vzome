# Feature Research: v1.2 Local and Specialized LLM Serving MVP

## Table stakes

- local serving for constrained Zomic generation
- lane-aware campaign launch and replay
- explicit hosted vs local vs specialized comparison outputs
- operator smoke tests and failure guidance

## Differentiators

- keeping local and specialized serving inside the same governed campaign
  workflow rather than off to the side
- retaining full provenance from acceptance pack through launch, replay, and
  comparison even when serving mode changes
- using specialized materials models where they fit best instead of forcing
  them into every task equally

## Likely high-value specialized roles

- synthesis-aware assessment inspired by materials-domain models such as
  CSLLM-style systems
- QC-conditioned suggestion or evaluation support where domain knowledge helps
  more than generic prompting
- generation only where the specialized lane can be validated honestly against
  the existing Zomic compile and pipeline contracts

## Anti-features

- implicit fallback that hides which lane actually ran
- adding autonomous execution at the same time as serving expansion
- treating benchmark comparison as optional documentation instead of part of
  the milestone outcome
