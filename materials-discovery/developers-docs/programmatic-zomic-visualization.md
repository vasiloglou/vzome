# Programmatic Zomic Visualization

Use this reference when you want the checked Sc-Zn geometry preview in repo-owned
code instead of opening desktop vZome for the normal read-only inspection path.

## Checked Artifact

The Phase 41 preview surface reads the checked raw labeled-geometry export
directly:

- `data/prototypes/generated/sc_zn_tsai_bridge.raw.json`

That file stays tied to the same source geometry used elsewhere in the Sc-Zn
workflow:

- `designs/zomic/sc_zn_tsai_bridge.zomic`
- `designs/zomic/sc_zn_tsai_bridge.yaml`

As of 2026-04-15, the checked raw export contains 52 labeled points and 52
segments.

## Refresh the Export

Refresh the checked raw export and the orbit-library artifact with the existing
bridge command:

```bash
cd materials-discovery
uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
```

`preview-zomic` does not replace `export-zomic`. The export command is still the
official artifact refresh path.

## Programmatic Preview

Render the checked Sc-Zn export without opening desktop vZome:

```bash
cd materials-discovery
uv run mdisc preview-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
```

The default output lands next to the raw export as:

- `data/prototypes/generated/sc_zn_tsai_bridge.viewer.html`

Useful variations:

```bash
uv run mdisc preview-zomic --raw data/prototypes/generated/sc_zn_tsai_bridge.raw.json
uv run mdisc preview-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml --show-labels
uv run mdisc preview-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml --open-browser
```

The generated viewer is a standalone HTML file with inline JavaScript for:

- drag-to-rotate
- wheel zoom
- reset view
- label toggle

## Python Helper

The stable import path is `materials_discovery.visualization`.

```python
from pathlib import Path

from materials_discovery.visualization import (
    build_view_model,
    preview_zomic_design,
    write_raw_export_viewer,
)

summary = preview_zomic_design(
    Path("designs/zomic/sc_zn_tsai_bridge.yaml"),
    show_labels=True,
)

view_model = build_view_model(
    Path("data/prototypes/generated/sc_zn_tsai_bridge.raw.json")
)

html_path = write_raw_export_viewer(
    Path("data/prototypes/generated/sc_zn_tsai_bridge.raw.json")
)
```

Use `preview_zomic_design(...)` when you want one function call that refreshes
through the existing export chain first. Use `write_raw_export_viewer(...)` or
`build_view_model(...)` when you already trust the current raw export artifact.

If you want the richer runnable walkthrough that embeds this helper into the
full Sc-Zn tutorial flow, use the
[Guided Design Tutorial Notebook](../notebooks/guided_design_tutorial.ipynb).

## What This Replaces

The new viewer is for programmatic preview of the checked raw export.

That means:

- the happy-path preview no longer requires opening desktop vZome just to look
  at the current checked geometry
- desktop vZome remains the authoring and deeper inspection tool
- the `.zomic` file remains the editable geometry source

## Future Work

This milestone deliberately stops at the raw-export preview surface.

Deferred work for later phases includes:

- `.vZome` compatibility
- `.shapes.json` compatibility
- broader browser-side feature parity with desktop vZome
