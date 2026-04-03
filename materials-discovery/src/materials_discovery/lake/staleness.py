"""Hash-based and mtime-hint staleness detection for artifact directories."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _hash_output_hashes(output_hashes: dict[str, str]) -> str:
    """Compute a stable SHA256 over sorted output_hashes dict."""
    payload = json.dumps(output_hashes, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def check_staleness(directory: Path, catalog_path: Path | None) -> bool:
    """Determine whether the artifact directory is stale relative to its catalog.

    Staleness rules (in priority order):
    1. If catalog_path is None or does not exist: stale (no catalog).
    2. Hash check: if a manifest JSON exists in the directory, compare its
       ``output_hashes`` against the ``content_hash`` recorded in the catalog.
       If they differ: stale.
    3. Mtime hint: if the newest file mtime in the directory is newer than the
       catalog file mtime: stale.
    4. Otherwise: not stale.

    Args:
        directory: Path to the artifact directory to check.
        catalog_path: Path to the existing ``_catalog.json``, or None.

    Returns:
        True if the directory is stale, False otherwise.
    """
    if catalog_path is None or not catalog_path.exists():
        return True

    # --- Hash-based check (authoritative) ---
    manifest_path = _find_manifest(directory)
    if manifest_path is not None:
        try:
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            output_hashes = manifest_data.get("output_hashes")
            if isinstance(output_hashes, dict):
                current_content_hash = _hash_output_hashes(output_hashes)
                # Load the catalog to read its recorded content_hash
                catalog_data = json.loads(catalog_path.read_text(encoding="utf-8"))
                entries = catalog_data.get("entries", [])
                if entries:
                    recorded_hash = entries[0].get("content_hash")
                    if recorded_hash is not None and recorded_hash != current_content_hash:
                        return True
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    # --- Mtime hint (secondary) ---
    newest_dir_mtime = _newest_file_mtime(directory)
    catalog_mtime = catalog_path.stat().st_mtime
    if newest_dir_mtime is not None and newest_dir_mtime > catalog_mtime:
        return True

    return False


def _find_manifest(directory: Path) -> Path | None:
    """Return the first manifest JSON file found in the directory, or None."""
    for candidate in ("manifest.json", "snapshot_manifest.json", "pack_manifest.json"):
        path = directory / candidate
        if path.exists():
            return path
    # Fallback: any .json file that looks like a manifest
    for path in directory.glob("*manifest*.json"):
        return path
    return None


def _newest_file_mtime(directory: Path) -> float | None:
    """Return the mtime of the newest file in the directory (non-recursive), or None."""
    newest: float | None = None
    try:
        for child in directory.iterdir():
            if child.is_file() and child.name != "_catalog.json":
                mtime = child.stat().st_mtime
                if newest is None or mtime > newest:
                    newest = mtime
    except OSError:
        pass
    return newest
