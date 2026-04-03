#!/usr/bin/env bash
# run_reference_aware_benchmarks.sh
#
# Phase 4 benchmark runner for reference-aware no-DFT materials discovery.
#
# Runs the two required benchmark lanes (Al-Cu-Fe and Sc-Zn) through the full
# mdisc stage pipeline and records where the benchmark-pack artifacts land.
# The script is config-driven: each lane is simply a committed YAML config plus
# a short name.  Operators can filter or adjust without editing the runner.
#
# USAGE
#   ./scripts/run_reference_aware_benchmarks.sh [OPTIONS]
#
# OPTIONS
#   --count N        Override candidate generation count for all lanes
#                    (default: config default_count or 100)
#   --seed N         Override random seed for candidate generation
#   --config-filter  Comma-separated substring filter applied to config names
#                    e.g. "al_cu_fe" runs only the Al-Cu-Fe lane
#   --no-active-learn  Skip the active-learn stage (useful for quick smoke runs)
#   --dry-run        Print commands that would run, but do not execute them
#
# PREREQUISITES
#   - Python 3.11 environment with mdisc installed:
#       uv sync --extra dev
#   - For the Sc-Zn lane the Zomic bridge needs a local Java runtime
#     (vZome core is invoked via ./gradlew :core:zomicExport).
#     If Java is absent the Sc-Zn *ingest* and *generate* stages that rely on
#     Zomic will fall back to the pinned fixture data already shipped in
#     data/external/sources/.  The validation stages are unaffected.
#
# OUTPUTS
#   benchmark_pack.json files are written to:
#     data/reports/<system_slug>_benchmark_pack.json
#   Pipeline manifests land under:
#     data/manifests/<system_slug>_pipeline_manifest.json
#
# EXAMPLES
#   # Full two-system benchmark run (default counts):
#   ./scripts/run_reference_aware_benchmarks.sh
#
#   # Quick smoke run with 30 candidates:
#   ./scripts/run_reference_aware_benchmarks.sh --count 30 --no-active-learn
#
#   # Only Al-Cu-Fe lane:
#   ./scripts/run_reference_aware_benchmarks.sh --config-filter al_cu_fe
#
#   # Dry run to check commands:
#   ./scripts/run_reference_aware_benchmarks.sh --dry-run

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
COUNT=""
SEED=""
CONFIG_FILTER=""
RUN_ACTIVE_LEARN=true
DRY_RUN=false

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --count)
      COUNT="$2"; shift 2 ;;
    --seed)
      SEED="$2"; shift 2 ;;
    --config-filter)
      CONFIG_FILTER="$2"; shift 2 ;;
    --no-active-learn)
      RUN_ACTIVE_LEARN=false; shift ;;
    --dry-run)
      DRY_RUN=true; shift ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--count N] [--seed N] [--config-filter SUBSTR] [--no-active-learn] [--dry-run]" >&2
      exit 2 ;;
  esac
done

# ---------------------------------------------------------------------------
# Phase 4 benchmark lanes
# Each entry is: "<config_path>:<display_name>"
# ---------------------------------------------------------------------------
BENCHMARK_LANES=(
  "configs/systems/al_cu_fe_reference_aware.yaml:Al-Cu-Fe reference-aware"
  "configs/systems/sc_zn_reference_aware.yaml:Sc-Zn reference-aware"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
run_cmd() {
  if [[ "$DRY_RUN" == true ]]; then
    echo "[DRY-RUN] $*"
  else
    "$@"
  fi
}

run_lane() {
  local config="$1"
  local name="$2"

  echo ""
  echo "============================================================"
  echo "  Benchmark lane: $name"
  echo "  Config: $config"
  echo "============================================================"

  # ingest
  run_cmd uv run mdisc ingest --config "$config"

  # generate — apply optional count/seed overrides
  local gen_args=("uv" "run" "mdisc" "generate" "--config" "$config")
  if [[ -n "$COUNT" ]]; then gen_args+=("--count" "$COUNT"); fi
  if [[ -n "$SEED"  ]]; then gen_args+=("--seed"  "$SEED");  fi
  run_cmd "${gen_args[@]}"

  # screen
  run_cmd uv run mdisc screen --config "$config"

  # hifi-validate
  run_cmd uv run mdisc hifi-validate --config "$config" --batch all

  # hifi-rank
  run_cmd uv run mdisc hifi-rank --config "$config"

  # active-learn (optional)
  if [[ "$RUN_ACTIVE_LEARN" == true ]]; then
    run_cmd uv run mdisc active-learn --config "$config"
  fi

  # report — also writes the benchmark_pack.json artifact
  run_cmd uv run mdisc report --config "$config"

  echo ""
  echo "  Lane complete: $name"
}

# ---------------------------------------------------------------------------
# Announce
# ---------------------------------------------------------------------------
echo "Phase 4 reference-aware benchmark runner"
echo "Root: $ROOT_DIR"
if [[ "$DRY_RUN" == true ]]; then
  echo "(DRY-RUN mode — no commands will execute)"
fi

# ---------------------------------------------------------------------------
# Run lanes
# ---------------------------------------------------------------------------
PACK_PATHS=()

for lane in "${BENCHMARK_LANES[@]}"; do
  config="${lane%%:*}"
  name="${lane##*:}"

  # Apply --config-filter if specified
  if [[ -n "$CONFIG_FILTER" ]]; then
    if [[ "$config" != *"$CONFIG_FILTER"* ]]; then
      echo "Skipping $name (filtered out by --config-filter='$CONFIG_FILTER')"
      continue
    fi
  fi

  run_lane "$config" "$name"

  # Record expected benchmark-pack output path for summary
  slug=$(basename "$config" .yaml)
  PACK_PATHS+=("data/reports/${slug}_benchmark_pack.json")
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
echo "  All benchmark lanes complete."
echo ""
echo "  Benchmark-pack artifacts:"
for path in "${PACK_PATHS[@]}"; do
  if [[ "$DRY_RUN" == true ]]; then
    echo "    [DRY-RUN] $path"
  elif [[ -f "$path" ]]; then
    echo "    $path  (exists)"
  else
    echo "    $path  (not found — check run above)"
  fi
done
echo "============================================================"
