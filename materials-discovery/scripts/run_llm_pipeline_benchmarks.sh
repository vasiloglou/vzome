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

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

write_eval_config() {
  local source_config="$1"
  local target_config="$2"
  local system_name="$3"

  SOURCE_CONFIG="$source_config" TARGET_CONFIG="$target_config" SYSTEM_NAME="$system_name" \
  uv run python - <<'PY'
import json
import os
from pathlib import Path

import yaml

source = Path(os.environ["SOURCE_CONFIG"])
target = Path(os.environ["TARGET_CONFIG"])
system_name = os.environ["SYSTEM_NAME"]

with source.open("r", encoding="utf-8") as handle:
    data = yaml.safe_load(handle)

payload = {
    "synthesizability_score": 0.71 if system_name == "Al-Cu-Fe" else 0.68,
    "precursor_hints": ["Al powder", "Cu powder", "Fe powder"]
    if system_name == "Al-Cu-Fe"
    else ["Sc granules", "Zn shot"],
    "anomaly_flags": [],
    "literature_context": f"Offline benchmark fixture for {system_name}.",
    "rationale": "Offline regression fixture.",
}

data["llm_evaluate"] = {
    "prompt_template": "materials_assess_v1",
    "temperature": 0.1,
    "max_tokens": 512,
    "fixture_outputs": [json.dumps(payload, sort_keys=True)],
}

target.parent.mkdir(parents=True, exist_ok=True)
with target.open("w", encoding="utf-8") as handle:
    yaml.safe_dump(data, handle, sort_keys=False)
PY
}

save_calibration() {
  local summary_json="$1"
  local destination="$2"

  SUMMARY_JSON="$summary_json" DESTINATION="$destination" \
  uv run python - <<'PY'
import json
import os
from pathlib import Path

from materials_discovery.common.io import load_json_object

summary = json.loads(os.environ["SUMMARY_JSON"])
calibration = load_json_object(Path(summary["calibration_path"]))
destination = Path(os.environ["DESTINATION"])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(calibration, indent=2, sort_keys=True), encoding="utf-8")
PY
}

run_lane() {
  local lane_name="$1"
  local system_key="$2"
  local system_name="$3"
  local config_path="$4"
  local generation_command="$5"
  local lane_dir="$6"

  echo "Running ${lane_name} lane for ${system_name}"

  local generate_json
  generate_json="$(uv run mdisc "$generation_command" --config "$config_path" --count "$COUNT")"

  local screen_json
  screen_json="$(uv run mdisc screen --config "$config_path")"
  save_calibration "$screen_json" "${lane_dir}/screen.json"

  local validate_json
  validate_json="$(uv run mdisc hifi-validate --config "$config_path" --batch all)"
  save_calibration "$validate_json" "${lane_dir}/hifi_validate.json"

  local rank_json
  rank_json="$(uv run mdisc hifi-rank --config "$config_path")"
  save_calibration "$rank_json" "${lane_dir}/hifi_rank.json"

  local evaluate_json
  evaluate_json="$(uv run mdisc llm-evaluate --config "$config_path" --batch all)"
  echo "$evaluate_json" > /dev/null

  local report_json
  report_json="$(uv run mdisc report --config "$config_path")"
  save_calibration "$report_json" "${lane_dir}/report.json"
}

write_comparison() {
  local system_name="$1"
  local deterministic_dir="$2"
  local llm_dir="$3"
  local out_path="$4"

  SYSTEM_NAME="$system_name" \
  DETERMINISTIC_DIR="$deterministic_dir" \
  LLM_DIR="$llm_dir" \
  OUT_PATH="$out_path" \
  uv run python - <<'PY'
import os
from pathlib import Path

from materials_discovery.common.io import load_json_object
from materials_discovery.llm.pipeline_benchmark import (
    build_llm_pipeline_comparison,
    write_llm_pipeline_comparison,
)

deterministic_dir = Path(os.environ["DETERMINISTIC_DIR"])
llm_dir = Path(os.environ["LLM_DIR"])

payload = build_llm_pipeline_comparison(
    os.environ["SYSTEM_NAME"],
    load_json_object(deterministic_dir / "screen.json"),
    load_json_object(deterministic_dir / "hifi_validate.json"),
    load_json_object(deterministic_dir / "hifi_rank.json"),
    load_json_object(deterministic_dir / "report.json"),
    load_json_object(llm_dir / "screen.json"),
    load_json_object(llm_dir / "hifi_validate.json"),
    load_json_object(llm_dir / "hifi_rank.json"),
    load_json_object(llm_dir / "report.json"),
)
path = write_llm_pipeline_comparison(payload, Path(os.environ["OUT_PATH"]))
print(path)
PY
}

run_system() {
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
    echo "Sc-Zn pipeline benchmark requires a Java runtime for llm-generate compilation." >&2
    exit 2
  fi

  local deterministic_eval_config="${TEMP_DIR}/${system_key}_deterministic_eval.yaml"
  local llm_eval_config="${TEMP_DIR}/${system_key}_llm_eval.yaml"
  write_eval_config "$deterministic_config" "$deterministic_eval_config" "$system_name"
  write_eval_config "$llm_config" "$llm_eval_config" "$system_name"

  local deterministic_dir="${TEMP_DIR}/${system_key}/deterministic"
  local llm_dir="${TEMP_DIR}/${system_key}/llm"
  mkdir -p "$deterministic_dir" "$llm_dir"

  run_lane "deterministic" "$system_key" "$system_name" "$deterministic_eval_config" "generate" "$deterministic_dir"
  run_lane "llm" "$system_key" "$system_name" "$llm_eval_config" "llm-generate" "$llm_dir"

  local comparison_path
  comparison_path="$(
    write_comparison \
      "$system_name" \
      "$deterministic_dir" \
      "$llm_dir" \
      "data/benchmarks/llm_pipeline/${system_key}_comparison.json"
  )"
  echo "Wrote comparison to: $comparison_path"
}

case "$SYSTEMS" in
  all)
    run_system "al_cu_fe" "Al-Cu-Fe" "configs/systems/al_cu_fe.yaml" "configs/systems/al_cu_fe_llm_mock.yaml"
    run_system "sc_zn" "Sc-Zn" "configs/systems/sc_zn.yaml" "configs/systems/sc_zn_llm_mock.yaml"
    ;;
  al_cu_fe)
    run_system "al_cu_fe" "Al-Cu-Fe" "configs/systems/al_cu_fe.yaml" "configs/systems/al_cu_fe_llm_mock.yaml"
    ;;
  sc_zn)
    run_system "sc_zn" "Sc-Zn" "configs/systems/sc_zn.yaml" "configs/systems/sc_zn_llm_mock.yaml"
    ;;
  *)
    usage
    exit 2
    ;;
esac
