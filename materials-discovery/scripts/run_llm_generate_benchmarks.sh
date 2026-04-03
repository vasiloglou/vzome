#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

SYSTEMS="all"
COUNT="5"

usage() {
  echo "Usage: $0 [--systems all|al_cu_fe|sc_zn] [--count N]" >&2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --systems)
      SYSTEMS="$2"
      shift 2
      ;;
    --count)
      COUNT="$2"
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

write_comparison() {
  local system_key="$1"
  local system_name="$2"
  local det_generate_json="$3"
  local det_screen_json="$4"
  local llm_generate_json="$5"
  local llm_screen_json="$6"
  local out_path="data/benchmarks/llm_generate/${system_key}_comparison.json"

  SYSTEM_NAME="$system_name" \
  DET_GENERATE_JSON="$det_generate_json" \
  DET_SCREEN_JSON="$det_screen_json" \
  LLM_GENERATE_JSON="$llm_generate_json" \
  LLM_SCREEN_JSON="$llm_screen_json" \
  OUT_PATH="$out_path" \
  uv run python - <<'PY'
import json
import os
from pathlib import Path

from materials_discovery.common.io import load_json_object
from materials_discovery.llm.benchmark import (
    build_llm_generate_comparison,
    write_llm_generate_comparison,
)


def calibration(summary_env: str) -> dict[str, object]:
    summary = json.loads(os.environ[summary_env])
    return load_json_object(Path(summary["calibration_path"]))


payload = build_llm_generate_comparison(
    os.environ["SYSTEM_NAME"],
    calibration("DET_GENERATE_JSON"),
    calibration("DET_SCREEN_JSON"),
    calibration("LLM_GENERATE_JSON"),
    calibration("LLM_SCREEN_JSON"),
)
path = write_llm_generate_comparison(payload, Path(os.environ["OUT_PATH"]))
print(path)
PY
}

run_lane() {
  local system_key="$1"
  local system_name="$2"
  local deterministic_config="$3"
  local llm_config="$4"

  [[ -f "$deterministic_config" ]] || {
    echo "Missing deterministic config: $deterministic_config" >&2
    exit 2
  }
  [[ -f "$llm_config" ]] || {
    echo "Missing LLM config: $llm_config" >&2
    exit 2
  }

  if [[ "$system_key" == "sc_zn" ]] && ! command -v java >/dev/null 2>&1; then
    echo "Sc-Zn benchmark lane requires a Java runtime for Zomic compilation." >&2
    exit 2
  fi

  echo "Running deterministic lane for $system_name"
  local det_generate_json
  det_generate_json="$(uv run mdisc generate --config "$deterministic_config" --count "$COUNT")"
  local det_screen_json
  det_screen_json="$(uv run mdisc screen --config "$deterministic_config")"

  echo "Running llm lane for $system_name"
  local llm_generate_json
  llm_generate_json="$(uv run mdisc llm-generate --config "$llm_config" --count "$COUNT")"
  local llm_screen_json
  llm_screen_json="$(uv run mdisc screen --config "$llm_config")"

  local comparison_path
  comparison_path="$(
    write_comparison \
      "$system_key" \
      "$system_name" \
      "$det_generate_json" \
      "$det_screen_json" \
      "$llm_generate_json" \
      "$llm_screen_json"
  )"
  echo "Wrote comparison to: $comparison_path"
}

case "$SYSTEMS" in
  all)
    run_lane "al_cu_fe" "Al-Cu-Fe" "configs/systems/al_cu_fe.yaml" "configs/systems/al_cu_fe_llm_mock.yaml"
    run_lane "sc_zn" "Sc-Zn" "configs/systems/sc_zn.yaml" "configs/systems/sc_zn_llm_mock.yaml"
    ;;
  al_cu_fe)
    run_lane "al_cu_fe" "Al-Cu-Fe" "configs/systems/al_cu_fe.yaml" "configs/systems/al_cu_fe_llm_mock.yaml"
    ;;
  sc_zn)
    run_lane "sc_zn" "Sc-Zn" "configs/systems/sc_zn.yaml" "configs/systems/sc_zn_llm_mock.yaml"
    ;;
  *)
    usage
    exit 2
    ;;
esac
