# Phase 01 Discussion Log

**Phase:** `01-program-charter-and-canonical-data-model`  
**Date:** 2026-04-02

This file is the human audit trail for the `gsd-discuss-phase` conversation.
The locked decisions are captured in
[01-CONTEXT.md](/Users/nikolaosvasiloglou/github-repos/vzome/.planning/phases/01-program-charter-and-canonical-data-model/01-CONTEXT.md).

## Gray Areas Discussed

The following Phase 1 gray areas were presented and selected for discussion:

1. `Package boundary`
2. `Raw record shape`
3. `CLI integration path`
4. `Phase 2 adapter posture`

## Question Log

### 1. Package boundary

**Question**

Where should the new multi-source ingestion layer live?

**Options presented**

1. `materials_discovery/data_sources/` as a new sibling package
2. Extend `materials_discovery/backends/`
3. Extend `materials_discovery/data/`
4. Other

**User choice**

`1`

**Locked outcome**

Create a new sibling package at `materials_discovery/data_sources/`.

### 2. Raw record shape

**Question**

How should the canonical raw-source record be structured?

**Options presented**

1. Strict stable core + nested `source_metadata`
2. Broader flat schema
3. Thin wrapper around source-native data
4. Other

**User choice**

`1`

**Locked outcome**

Use a strict stable core for shared fields and keep provider-specific content
under `source_metadata`.

### 3. CLI integration path

**Question**

What should happen at the operator surface while this project matures?

**Options presented**

1. Keep `mdisc ingest` as the stable entrypoint and integrate the new source
   layer behind it
2. Add a separate primary ingestion CLI now
3. Keep both from the start
4. Other

**User choice**

`1`

**Locked outcome**

Keep `mdisc ingest` as the stable operator-facing entrypoint.

### 4. Phase 2 adapter posture

**Question**

What should the first adapter wave optimize for?

**Options presented**

1. Mixed strategy: snapshot/bulk where that matches the source, direct API or
   `OPTIMADE` where those are mature
2. API-first everywhere possible
3. Snapshot/bulk-first everywhere
4. `OPTIMADE`-first as the default path
5. Other

**User choice**

`1`

**Locked outcome**

Use a mixed adapter strategy in Phase 2.

## Follow-up Clarification

After the initial decisions were captured, the user raised a meta-question:

> have we done a complete deep research to cover all possible repos and data
> sources for the data we need?

The answer was:

- not yet fully
- the first pass was good enough to start Phase 1 contract work
- but Phase 1 should explicitly include a broader source-and-tooling landscape
  review before finalizing the source registry and Phase 2 adapter order

The user then asked whether that work belongs before the phase or inside the
phase. The resulting decision was:

- it belongs inside Phase 1
- Phase 1 should expand its source and tooling inventory before final design
  docs are finalized

## Resulting Context Updates

The discussion directly locked these decisions:

- `D-17`: strict stable core + nested `source_metadata`
- `D-18`: new sibling package `materials_discovery/data_sources/`
- `D-20`: keep `mdisc ingest` as the stable operator-facing entrypoint
- `D-21`: mixed Phase 2 adapter strategy

And it triggered this additional planning change:

- broaden Phase 1 research and context so the source registry is grounded in a
  wider official source-and-tooling inventory
