#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 DATA_ROOT OUTPUT_ROOT SUBJECTS_CSV [SEED]" >&2
  exit 2
fi

DATA_ROOT="$1"
OUTPUT_ROOT="$2"
SUBJECTS_CSV="$3"
SEED="${4:-2025}"
MAX_PARALLEL="${MAX_PARALLEL:-1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pids=()

if [[ ! "$MAX_PARALLEL" =~ ^[1-9][0-9]*$ ]]; then
  echo "MAX_PARALLEL must be a positive integer" >&2
  exit 2
fi

run_one() {
  local subject="$1"
  local setting="$2"
  echo "matrix_run subject=${subject} setting=${setting} started_at=$(date --iso-8601=seconds)"
  bash "$SCRIPT_DIR/run_retrieval.sh" \
    "$DATA_ROOT" "$OUTPUT_ROOT" "$subject" "$setting" "$SEED"
}

IFS=',' read -r -a subjects <<< "$SUBJECTS_CSV"
for subject in "${subjects[@]}"; do
  if [[ ! "$subject" =~ ^([1-9]|10)$ ]]; then
    echo "Invalid subject ID: $subject" >&2
    exit 2
  fi
  for setting in b32 b32_vae; do
    run_one "$subject" "$setting" &
    pids+=("$!")
    if (( ${#pids[@]} >= MAX_PARALLEL )); then
      wait "${pids[0]}"
      pids=("${pids[@]:1}")
    fi
  done
done

for pid in "${pids[@]:-}"; do
  [[ -n "$pid" ]] && wait "$pid"
done

echo "matrix_finished_at=$(date --iso-8601=seconds)"
