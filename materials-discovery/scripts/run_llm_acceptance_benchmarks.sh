#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

SYSTEMS="all"
COUNT="5"
PACK_ID="phase9_acceptance_v1"
EVAL_SET_MANIFEST=""

usage() {
  echo "Usage: $0 [--systems all|al_cu_fe|sc_zn] [--count N] [--pack-id ID] [--eval-set-manifest PATH]" >&2
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
    --pack-id)
      PACK_ID="$2"
      shift 2
      ;;
    --eval-set-manifest)
      EVAL_SET_MANIFEST="$2"
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

./scripts/run_llm_generate_benchmarks.sh --systems "$SYSTEMS" --count "$COUNT"
./scripts/run_llm_pipeline_benchmarks.sh --systems "$SYSTEMS" --count "$COUNT"

case "$SYSTEMS" in
  all)
    SYSTEM_KEYS="al_cu_fe,sc_zn"
    ;;
  al_cu_fe|sc_zn)
    SYSTEM_KEYS="$SYSTEMS"
    ;;
  *)
    usage
    exit 2
    ;;
esac

SYSTEM_KEYS="$SYSTEM_KEYS" PACK_ID="$PACK_ID" EVAL_SET_MANIFEST="$EVAL_SET_MANIFEST" \
uv run python - <<'PY'
import os
from pathlib import Path

from materials_discovery.llm.acceptance import (
    build_llm_acceptance_pack,
    load_acceptance_benchmark_input,
    write_llm_acceptance_pack,
)
from materials_discovery.llm.storage import llm_acceptance_pack_path

system_names = {
    "al_cu_fe": "Al-Cu-Fe",
    "sc_zn": "Sc-Zn",
}
benchmark_root = Path("data/benchmarks")

inputs = []
for key in os.environ["SYSTEM_KEYS"].split(","):
    key = key.strip()
    if not key:
        continue
    inputs.append(
        load_acceptance_benchmark_input(
            system=system_names[key],
            generate_comparison_path=benchmark_root / "llm_generate" / f"{key}_comparison.json",
            pipeline_comparison_path=benchmark_root / "llm_pipeline" / f"{key}_comparison.json",
        )
    )

pack = build_llm_acceptance_pack(
    pack_id=os.environ["PACK_ID"],
    benchmark_inputs=inputs,
    eval_set_manifest_path=os.environ["EVAL_SET_MANIFEST"] or None,
)
path = write_llm_acceptance_pack(pack, llm_acceptance_pack_path(os.environ["PACK_ID"]))
print(path)
PY
