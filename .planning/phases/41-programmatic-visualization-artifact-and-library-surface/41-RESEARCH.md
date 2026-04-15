# Phase 41 Research: Programmatic Visualization Artifact and Library Surface

**Phase:** 41  
**Date:** 2026-04-15  
**Goal:** Plan one repo-owned programmatic visualization path for the checked
Sc-Zn Zomic design without turning the milestone into a browser-parity or
service project.

## Research Question

What do we need to know to plan Phase 41 well so the repo can:

- refresh the checked Sc-Zn visualization artifact without a manual desktop
  export step
- render that checked artifact programmatically through one stable library
  surface
- keep the implementation tutorial-first, local, and reusable by later docs and
  notebook work
- avoid drifting into full `.vZome` / `.shapes.json` compatibility or a new
  always-on visualization backend

## Key Findings

### 1. `mdisc export-zomic` already provides almost all of the refresh contract

The checked refresh path already exists in
`materials-discovery/src/materials_discovery/cli.py` and
`materials-discovery/src/materials_discovery/generator/zomic_bridge.py`.

Important details:

- `export-zomic` calls `export_zomic_design(...)`
- `export_zomic_design(...)` refreshes the raw export and orbit-library JSON
- the summary contract in `ZomicExportSummary` already returns:
  - `design_path`
  - `zomic_file`
  - `raw_export_path`
  - `orbit_library_path`
  - `labeled_site_count`
  - `orbit_count`

Planning implication: Phase 41 does **not** need a replacement for the export
bridge. It needs a clearer rendering surface on top of the existing raw export,
plus only a paper-thin ergonomic wrapper where that actually helps.

### 2. The checked raw export is rich enough to drive the MVP renderer directly

`core/src/main/java/com/vzome/core/apps/ExportZomicLabeledGeometry.java`
exports:

- `labeled_points[]` with `label`, `source_label`, `occurrence`, `position`,
  and `cartesian`
- `segments[]` with `signature`, `start`, and `end`
- parser and symmetry metadata

The committed Sc-Zn example at
`materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json`
currently contains:

- 52 labeled points
- 52 segments
- evaluated cartesian coordinates for both points and segment endpoints

Planning implication: the renderer can take `*.raw.json` as its **public
input**, with no need to invent a separate checked artifact first.

### 3. The repo already treats `*.raw.json` as a first-class artifact outside docs

The raw export is not just a tutorial side file. It is already consumed by the
LLM-facing code:

- `materials-discovery/src/materials_discovery/llm/inventory.py`
- `materials-discovery/src/materials_discovery/llm/converters/generated_export.py`
- `materials-discovery/tests/test_llm_native_sources.py`

Those paths already assume:

- the `*.raw.json` suffix is stable
- `labeled_points` exists
- `parser`, `symmetry`, and `zomic_file` metadata are useful downstream

Planning implication: choosing `*.raw.json` as the MVP viewer input aligns with
an existing repo contract instead of creating a docs-only side path.

### 4. The existing `online/` viewer stack is capable, but too heavy to be the MVP base

The `online/` app already has:

- a reusable `vzome-viewer` web component
- Three.js geometry rendering
- labels, image capture, and export hooks
- support for `.vZome` and `.shapes.json`

But the same codebase also carries Phase 41 risks:

- its documented input formats are `.vZome` and `.shapes.json`, not the raw
  labeled-geometry export
- `online/README.md` still expects Node/Yarn or Docker for normal development
- `online/developer-docs/testing-strategy.md` explicitly says there are no
  automated tests yet
- the worker/viewer architecture is broader than the tutorial-first MVP needs

Planning implication: Phase 41 should treat `online/` as **reference
material**, not as the required runtime foundation for the new programmatic
path. Borrowing ideas is fine; making the tutorial depend on the full online
stack is not.

### 5. The lowest-risk stable API lives inside `materials_discovery`

`materials-discovery/pyproject.toml` keeps the runtime intentionally small:

- `typer`
- `pydantic`
- `pyyaml`
- `numpy`

There is no existing JS build step, package-data workflow, or notebook widget
dependency in that Python package. That argues for a local additive module such
as:

```text
materials-discovery/src/materials_discovery/visualization/
  __init__.py
  raw_export.py
  viewer.py
```

Planning implication: the stable public API should be Python-first and live in
`materials_discovery.visualization`, because that is the surface later notebook
and docs work will actually call.

### 6. A self-contained HTML/canvas viewer is a better fit than a new service

The user accepted these planning constraints:

- Python-first helper
- thin JavaScript layer
- no default long-running service
- readability over desktop parity

That points to a self-contained viewer shape:

- Python loads and normalizes `*.raw.json`
- Python emits standalone HTML with embedded JSON
- inline JavaScript draws points and segments and supports drag-to-rotate,
  wheel zoom, and optional labels
- the same HTML can be:
  - written to a `.viewer.html` file
  - opened in a browser
  - embedded into a notebook later

Planning implication: Phase 41 can avoid both a service and the full `online/`
toolchain while still delivering a reusable render surface.

### 7. A thin CLI wrapper is worth adding once the library exists

Even though `mdisc export-zomic` already covers refresh, the milestone still
needs one stable render path that operators can run directly.

The clean additive wrapper is:

```text
uv run mdisc preview-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
```

or

```text
uv run mdisc preview-zomic --raw data/prototypes/generated/sc_zn_tsai_bridge.raw.json
```

That wrapper should:

- reuse `export_zomic_design(...)` when `--design` is supplied
- write `*.viewer.html` next to the chosen raw export by default
- optionally open the HTML in a browser
- return a JSON summary like other `mdisc` commands

Planning implication: the CLI should be a convenience layer over the library,
not a second implementation path.

### 8. Phase 41 should ship a narrow reference doc, not the tutorial rewrite

The guided tutorial and notebook changes are already mapped to later phases.
Phase 41 still needs enough documentation to make the new surface reusable.

The right doc shape is a focused reference page that explains:

- the checked raw export path
- the refresh command
- the preview command and Python helper
- the boundary between the new viewer and desktop vZome
- explicit deferrals for `.vZome` / `.shapes.json` parity and editing

Planning implication: Phase 41 should add a small developer reference and let
Phase 42/43 absorb it into the guided tutorial and notebook later.

## Recommended Implementation Shape

### Runtime surface

Add an additive visualization package under `materials_discovery`:

```text
materials-discovery/src/materials_discovery/visualization/
  __init__.py
  raw_export.py
  viewer.py
```

Recommended public API:

- `load_raw_export(path: Path) -> ZomicRawExport`
- `build_view_model(path_or_export) -> RawExportViewModel`
- `render_raw_export_html(path_or_view_model, *, title, width, height, show_labels) -> str`
- `write_raw_export_viewer(raw_export_path, *, out_path=None, title=None) -> Path`
- `preview_zomic_design(design_path, *, out_path=None, force=False, open_browser=False) -> ZomicPreviewSummary`

### CLI surface

Add one additive command:

```text
mdisc preview-zomic
```

Recommended options:

- `--design <design.yaml>`
- `--raw <artifact.raw.json>`
- `--out <viewer.html>`
- `--force`
- `--open-browser/--no-open-browser`

### Documentation surface

Add one focused reference page:

```text
materials-discovery/developers-docs/programmatic-zomic-visualization.md
```

and add one cross-link from:

```text
materials-discovery/developers-docs/zomic-design-workflow.md
```

## Validation Architecture

Phase 41 should use the existing pytest + Typer test stack under
`materials-discovery/`.

### Fast validation loop

Use the phase-focused tests after every task commit:

```bash
cd materials-discovery && uv run pytest \
  tests/test_zomic_visualization.py \
  tests/test_cli.py -q
```

### Compatibility regression loop

Use a slightly broader contract check after the code tasks:

```bash
cd materials-discovery && uv run pytest \
  tests/test_zomic_bridge.py \
  tests/test_llm_native_sources.py \
  tests/test_zomic_visualization.py \
  tests/test_cli.py -q
```

### Full validation loop

Before final phase sign-off:

```bash
cd materials-discovery && uv run pytest -q
```

### Minimum Wave 0 verification expectations

Phase 41 execution should require:

- focused tests for raw export loading, segment normalization, and HTML output
- CLI tests for `preview-zomic` success and exit-code `2` failures
- compatibility checks proving the renderer does not change the existing raw
  export contract relied on by bridge and LLM tooling
- `git diff --check` on the final change set

### Manual checks still worth keeping

- open one generated `.viewer.html` file and confirm the checked Sc-Zn design
  supports rotate, zoom, and label toggling
- inspect the rendered output once with labels off and once with labels on to
  confirm the tutorial-readable default
- confirm the viewer doc states clearly that desktop vZome is still the
  authoring/editing tool

## Planning Implications

Phase 41 should not be planned as “make browser vZome.” It should explicitly:

- keep `*.raw.json` as the public viewer input
- keep `mdisc export-zomic` as the underlying refresh contract
- add one additive Python-first visualization package inside
  `materials_discovery`
- add one thin CLI wrapper for programmatic preview
- add tests and a narrow reference doc
- avoid requiring Node, Yarn, Docker, or a running backend service in the happy
  path

## Recommendation

Phase 41 is ready for planning now.

The highest-confidence planning path is a **single execute plan** with three
tasks:

1. raw export contract and self-contained renderer core
2. public helper and `preview-zomic` CLI wrapper
3. focused reference docs and required `Progress.md` tracking

That decomposition keeps the implementation small, testable, and aligned with
the locked Phase 41 decisions.
