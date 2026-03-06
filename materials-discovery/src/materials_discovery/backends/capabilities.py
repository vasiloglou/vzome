from __future__ import annotations

from pathlib import Path
from typing import Any

from materials_discovery.common.io import load_yaml, workspace_root


def capabilities_matrix_path() -> Path:
    return workspace_root() / "data" / "registry" / "backend_capabilities.yaml"


def load_capabilities_matrix() -> dict[str, Any]:
    path = capabilities_matrix_path()
    if not path.exists():
        raise FileNotFoundError(f"Backend capability matrix missing: {path}")
    return load_yaml(path)
