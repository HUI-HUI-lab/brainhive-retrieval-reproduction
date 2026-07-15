#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 OUTPUT_ROOT" >&2
  exit 2
fi

ROOT="$(realpath "$1")"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

for setting in b32 b32_vae; do
  python3 "${REPO_ROOT}/build_average.py" \
    --exp_root "${ROOT}/${setting}" \
    --metrics eval_top1_acc eval_top5_acc \
    --out_json "${ROOT}/${setting}_summary.json" \
    --out_csv "${ROOT}/${setting}_summary.csv"
done

