from materials_discovery.visualization.raw_export import build_view_model, load_raw_export
from materials_discovery.visualization.viewer import (
    preview_raw_export,
    preview_zomic_design,
    render_raw_export_html,
    write_raw_export_viewer,
)
from materials_discovery.visualization.labels import (
    DEFAULT_ORBIT_COLOR,
    ORBIT_COLORS,
    ORBIT_LABELS,
    PREFERRED_SPECIES,
    SHELL_NAMES,
)

__all__ = [
    "build_view_model",
    "load_raw_export",
    "preview_raw_export",
    "preview_zomic_design",
    "render_raw_export_html",
    "write_raw_export_viewer",
    "DEFAULT_ORBIT_COLOR",
    "ORBIT_COLORS",
    "ORBIT_LABELS",
    "PREFERRED_SPECIES",
    "SHELL_NAMES",
]

# Conditionally export plotly_3d functions when the [viz] extra is installed.
# If plotly or scipy are absent the package is still fully importable.
try:
    from materials_discovery.visualization.plotly_3d import (
        load_orbit_library,
        orbit_figure,
        shell_figure,
    )
except ImportError:
    pass
else:
    __all__ += ["load_orbit_library", "orbit_figure", "shell_figure"]
