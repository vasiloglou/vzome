#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

CONFIG="configs/systems/al_cu_fe_exec.yaml"

uv run mdisc ingest --config "$CONFIG"
uv run mdisc generate --config "$CONFIG" --count 200 --seed 20260306
uv run mdisc screen --config "$CONFIG"
uv run mdisc hifi-validate --config "$CONFIG" --batch all
uv run mdisc hifi-rank --config "$CONFIG"
uv run mdisc active-learn --config "$CONFIG"
uv run mdisc report --config "$CONFIG"
