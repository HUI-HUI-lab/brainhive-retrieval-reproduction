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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IFS=',' read -r -a subjects <<< "$SUBJECTS_CSV"
for subject in "${subjects[@]}"; do
  if [[ ! "$subject" =~ ^([1-9]|10)$ ]]; then
    echo "Invalid subject ID: $subject" >&2
    exit 2
  fi
  for setting in b32 b32_vae; do
    echo "matrix_run subject=${subject} setting=${setting} started_at=$(date --iso-8601=seconds)"
    bash "$SCRIPT_DIR/run_retrieval.sh" \
      "$DATA_ROOT" "$OUTPUT_ROOT" "$subject" "$setting" "$SEED"
  done
done

echo "matrix_finished_at=$(date --iso-8601=seconds)"
