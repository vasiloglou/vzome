# Research Summary: v1.1 Closed-Loop LLM Campaign MVP

## Milestone direction

The strongest next milestone for Project 3 is to turn the shipped Phase 9
acceptance-pack plus dry-run suggestion surface into an operator-governed,
replayable closed-loop campaign workflow.

## Stack additions

- No new platform stack is required.
- Stay with Python 3.11, Typer, Pydantic, and file-backed manifests.
- Add typed campaign contracts and a thin runtime around existing `llm-generate`
  and benchmark artifacts.

## Feature table stakes

- executable campaign proposals
- explicit operator approval
- reproducible campaign specs
- launch through existing `llm-generate`
- replay and comparison against prior acceptance and benchmark artifacts

## Architecture guidance

- Put the contract first, execution bridge second, replay/comparison third.
- Reuse `llm/`, `active_learning/`, `common/schema.py`, and `cli.py`.
- Keep campaign logic additive to the existing no-DFT pipeline.

## Watch out for

- proposals that remain too vague to execute
- hidden state mutation
- acceptance-pack bypass
- weak replay fidelity
- scope creep into local serving or fine-tuning

## Recommended scope boundary

Ship the closed-loop campaign MVP now. Defer local or fine-tuned inference
serving until the campaign surface and acceptance workflow are stable.
