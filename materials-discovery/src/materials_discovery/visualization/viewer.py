from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from materials_discovery.common.io import ensure_parent
from materials_discovery.visualization.raw_export import RawExportViewModel, build_view_model

_VIEWER_TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>__TITLE__</title>
    <style>
      :root {
        color-scheme: light;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        background: #f3f4f6;
        color: #111827;
      }

      main {
        max-width: calc(__WIDTH__px + 48px);
        margin: 0 auto;
        padding: 24px;
      }

      .viewer-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 16px;
      }

      .viewer-header h1 {
        margin: 0 0 8px;
        font-size: 1.5rem;
      }

      .viewer-meta,
      .viewer-help {
        margin: 0;
        color: #4b5563;
        line-height: 1.5;
      }

      .viewer-controls {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }

      button {
        border: 1px solid #d1d5db;
        border-radius: 6px;
        background: #ffffff;
        color: #111827;
        padding: 8px 12px;
        font: inherit;
        cursor: pointer;
      }

      button:hover {
        background: #f9fafb;
      }

      canvas {
        display: block;
        width: 100%;
        height: auto;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        background: #ffffff;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        touch-action: none;
      }
    </style>
  </head>
  <body>
    <main>
      <header class="viewer-header">
        <div>
          <h1>__TITLE__</h1>
          <p class="viewer-meta">Source: __SOURCE_ZOMIC__ | Symmetry: __SYMMETRY__ | Points: __POINT_COUNT__ | Segments: __SEGMENT_COUNT__ | Orbits: __ORBIT_COUNT__</p>
          <p class="viewer-help">Drag to rotate. Use the mouse wheel to zoom.</p>
        </div>
        <div class="viewer-controls">
          <button id="toggle-labels" type="button">Toggle Labels</button>
          <button id="reset-view" type="button">Reset View</button>
        </div>
      </header>
      <canvas id="zomic-viewer" width="__WIDTH__" height="__HEIGHT__"></canvas>
    </main>
    <script>
      const VIEW_MODEL = __VIEW_MODEL__;
      const DEFAULT_SHOW_LABELS = __SHOW_LABELS__;

      (() => {
        const canvas = document.getElementById("zomic-viewer");
        const context = canvas.getContext("2d");
        const toggleLabelsButton = document.getElementById("toggle-labels");
        const resetViewButton = document.getElementById("reset-view");
        const defaultState = {
          rotationX: -0.55,
          rotationY: 0.75,
          zoom: 1.0,
          showLabels: DEFAULT_SHOW_LABELS,
        };
        const state = { ...defaultState };
        const cameraDistance = Math.max(VIEW_MODEL.bounds_radius * 4.0, 8.0);
        const baseScale = Math.min(canvas.width, canvas.height) / Math.max(VIEW_MODEL.bounds_radius * 3.2, 1.0);
        let dragPointerId = null;
        let lastPointerX = 0;
        let lastPointerY = 0;

        function projectCoordinates(coordinates) {
          const [x, y, z] = coordinates;
          const cosY = Math.cos(state.rotationY);
          const sinY = Math.sin(state.rotationY);
          const rotatedX = (x * cosY) + (z * sinY);
          const rotatedZ = (-x * sinY) + (z * cosY);
          const cosX = Math.cos(state.rotationX);
          const sinX = Math.sin(state.rotationX);
          const rotatedY = (y * cosX) - (rotatedZ * sinX);
          const depth = (y * sinX) + (rotatedZ * cosX);
          const perspective = cameraDistance / (cameraDistance - depth);
          const scale = baseScale * state.zoom * perspective;
          return {
            canvasX: (canvas.width / 2) + (rotatedX * scale),
            canvasY: (canvas.height / 2) - (rotatedY * scale),
            depth,
            scale,
          };
        }

        function clearCanvas() {
          context.fillStyle = "#ffffff";
          context.fillRect(0, 0, canvas.width, canvas.height);
          context.strokeStyle = "#e5e7eb";
          context.strokeRect(0.5, 0.5, canvas.width - 1, canvas.height - 1);
        }

        function renderEmptyState() {
          context.fillStyle = "#4b5563";
          context.font = "16px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
          context.textAlign = "center";
          context.fillText("No labeled points or segments available in this raw export.", canvas.width / 2, canvas.height / 2);
        }

        function renderScene() {
          clearCanvas();
          if (!VIEW_MODEL.points.length && !VIEW_MODEL.segments.length) {
            renderEmptyState();
            return;
          }

          const projectedSegments = VIEW_MODEL.segments.map((segment) => {
            const start = projectCoordinates(segment.start);
            const end = projectCoordinates(segment.end);
            return { segment, start, end, depth: (start.depth + end.depth) / 2 };
          }).sort((a, b) => a.depth - b.depth);

          const projectedPoints = VIEW_MODEL.points.map((point) => {
            const projection = projectCoordinates(point.coordinates);
            return { point, projection };
          }).sort((a, b) => a.projection.depth - b.projection.depth);

          context.lineWidth = 1.5;
          for (const entry of projectedSegments) {
            context.beginPath();
            context.strokeStyle = entry.segment.color;
            context.moveTo(entry.start.canvasX, entry.start.canvasY);
            context.lineTo(entry.end.canvasX, entry.end.canvasY);
            context.stroke();
          }

          for (const entry of projectedPoints) {
            const radius = Math.max(3.5, entry.projection.scale * 0.08);
            context.beginPath();
            context.fillStyle = entry.point.color;
            context.arc(entry.projection.canvasX, entry.projection.canvasY, radius, 0, Math.PI * 2);
            context.fill();
            context.lineWidth = 1;
            context.strokeStyle = "#ffffff";
            context.stroke();

            if (state.showLabels) {
              context.fillStyle = "#111827";
              context.font = "12px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
              context.textAlign = "left";
              context.fillText(
                entry.point.label,
                entry.projection.canvasX + radius + 4,
                entry.projection.canvasY - radius - 2
              );
            }
          }

          toggleLabelsButton.textContent = state.showLabels ? "Hide Labels" : "Show Labels";
        }

        canvas.addEventListener("pointerdown", (event) => {
          dragPointerId = event.pointerId;
          lastPointerX = event.clientX;
          lastPointerY = event.clientY;
          canvas.setPointerCapture(event.pointerId);
        });

        canvas.addEventListener("pointermove", (event) => {
          if (dragPointerId !== event.pointerId) {
            return;
          }
          const deltaX = event.clientX - lastPointerX;
          const deltaY = event.clientY - lastPointerY;
          lastPointerX = event.clientX;
          lastPointerY = event.clientY;
          state.rotationY += deltaX * 0.01;
          state.rotationX += deltaY * 0.01;
          renderScene();
        });

        function stopDragging(event) {
          if (dragPointerId === event.pointerId) {
            dragPointerId = null;
          }
        }

        canvas.addEventListener("pointerup", stopDragging);
        canvas.addEventListener("pointercancel", stopDragging);

        canvas.addEventListener("wheel", (event) => {
          event.preventDefault();
          const zoomFactor = event.deltaY > 0 ? 0.92 : 1.08;
          state.zoom = Math.min(6.0, Math.max(0.3, state.zoom * zoomFactor));
          renderScene();
        }, { passive: false });

        toggleLabelsButton.addEventListener("click", () => {
          state.showLabels = !state.showLabels;
          renderScene();
        });

        resetViewButton.addEventListener("click", () => {
          Object.assign(state, defaultState);
          renderScene();
        });

        renderScene();
      })();
    </script>
  </body>
</html>
"""


def _round_json_floats(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, list):
        return [_round_json_floats(item) for item in value]
    if isinstance(value, dict):
        return {key: _round_json_floats(item) for key, item in value.items()}
    return value


def _default_title(view_model: RawExportViewModel) -> str:
    if view_model.source_zomic:
        return f"Zomic Preview - {Path(view_model.source_zomic).name}"
    return "Zomic Preview"


def _default_out_path(raw_export_path: Path) -> Path:
    if raw_export_path.name.endswith(".raw.json"):
        return raw_export_path.with_name(
            raw_export_path.name[: -len(".raw.json")] + ".viewer.html"
        )
    return raw_export_path.with_name(f"{raw_export_path.stem}.viewer.html")


def render_raw_export_html(
    view_model: RawExportViewModel,
    *,
    title: str | None = None,
    width: int = 960,
    height: int = 720,
    show_labels: bool = False,
) -> str:
    serialized_view_model = json.dumps(
        _round_json_floats(view_model.model_dump(mode="json")),
        separators=(",", ":"),
        sort_keys=True,
    )
    replacements = {
        "__TITLE__": html.escape(title or _default_title(view_model)),
        "__SOURCE_ZOMIC__": html.escape(
            Path(view_model.source_zomic).name if view_model.source_zomic else "unknown"
        ),
        "__SYMMETRY__": html.escape(view_model.symmetry or "unknown"),
        "__POINT_COUNT__": str(view_model.labeled_point_count),
        "__SEGMENT_COUNT__": str(view_model.segment_count),
        "__ORBIT_COUNT__": str(view_model.orbit_count),
        "__VIEW_MODEL__": serialized_view_model,
        "__SHOW_LABELS__": "true" if show_labels else "false",
        "__WIDTH__": str(width),
        "__HEIGHT__": str(height),
    }
    rendered = _VIEWER_TEMPLATE
    for placeholder, replacement in replacements.items():
        rendered = rendered.replace(placeholder, replacement)
    return rendered


def write_raw_export_viewer(
    raw_export_path: Path,
    out_path: Path | None = None,
    *,
    title: str | None = None,
    show_labels: bool = False,
) -> Path:
    resolved_raw_export_path = raw_export_path.resolve()
    resolved_out_path = (out_path.resolve() if out_path is not None else _default_out_path(resolved_raw_export_path))
    view_model = build_view_model(resolved_raw_export_path)
    html_text = render_raw_export_html(
        view_model,
        title=title,
        show_labels=show_labels,
    )
    ensure_parent(resolved_out_path)
    resolved_out_path.write_text(html_text, encoding="utf-8")
    return resolved_out_path
