# Pitfalls Research: v1.1 Closed-Loop LLM Campaign MVP

## Primary risks

### 1. Advisory output that is still too vague

If campaign proposals are not specific enough to materialize into a deterministic
spec, the milestone will look new but still behave like the Phase 9 dry run.

### 2. Hidden mutation of state

If approval, launch, and replay are not explicit, operators will not be able to
tell what changed or why a new run happened.

### 3. Acceptance-gate bypass

If the system can launch a campaign without referencing an acceptance pack and
recorded approval, the loop will drift away from the measured benchmark surface.

### 4. Irreproducible campaign replays

If campaign specs do not pin the selected proposal, eval-set reference, prompt
inputs, and launch parameters, later comparisons will be noisy or meaningless.

### 5. Over-coupling to local serving or fine-tuning

Trying to land local-model hosting in the same milestone will dilute the core
goal and slow delivery.

## Prevention strategy

- Require typed proposal actions and explicit approval states.
- Treat campaign spec files as the launch authority.
- Preserve dry-run and execute as separate commands or explicit modes.
- Make replay a first-class artifact path, not an afterthought.
- Keep local serving and fine-tuning in a future milestone.
