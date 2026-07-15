#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: $0 DATA_ROOT OUTPUT_ROOT SUBJECT SETTING [SEED]" >&2
  echo "SETTING: b32 or b32_vae" >&2
  exit 2
fi

DATA_ROOT="$(realpath "$1")"
OUTPUT_ROOT="$(realpath -m "$2")"
SUBJECT="$3"
SETTING="$4"
SEED="${5:-2025}"
TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-1024}"
PRECISION="${PRECISION:-bf16}"
NUM_EPOCHS="${NUM_EPOCHS:-25}"

case "$SETTING" in
  b32)
    PROJ_META='{"CLIP-ViT-B-32-laion2B-s34B-b79K":512}'
    ;;
  b32_vae)
    PROJ_META='{"CLIP-ViT-B-32-laion2B-s34B-b79K":512,"vae":1024}'
    ;;
  *)
    echo "Unknown setting: $SETTING (expected b32 or b32_vae)" >&2
    exit 2
    ;;
esac

if [[ "$PRECISION" == "bf16" ]]; then
  BF16=true
  FP16=false
elif [[ "$PRECISION" == "fp16" ]]; then
  BF16=false
  FP16=true
else
  echo "PRECISION must be bf16 or fp16" >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_DIR="${OUTPUT_ROOT}/${SETTING}/subj-${SUBJECT}/rep-01"
RESOLVED_CONFIG="${RUN_DIR}/resolved_config.yaml"
METADATA_FILE="${RUN_DIR}/run_metadata.txt"
mkdir -p "$RUN_DIR"

START_EPOCH="$(date +%s)"
finalize_run() {
  status=$?
  trap - EXIT
  end_epoch="$(date +%s)"
  {
    echo "finished_at=$(date --iso-8601=seconds)"
    echo "runtime_seconds=$((end_epoch - START_EPOCH))"
    echo "exit_status=${status}"
  } | tee -a "$METADATA_FILE"
  exit "$status"
}
trap finalize_run EXIT

python3 "${REPO_ROOT}/build_config.py" \
  --config_file "${REPO_ROOT}/reproduction/configs/retrieval.yaml" \
  --output_file "$RESOLVED_CONFIG" \
  "subject_ids=[${SUBJECT}]" \
  "eval_subject_ids=[${SUBJECT}]" \
  "proj_meta=${PROJ_META}" \
  "seed=${SEED}" \
  "run_name=${SETTING}/subj-${SUBJECT}/rep-01" \
  "output_dir=${RUN_DIR}" \
  "data_directory=${DATA_ROOT}/things-eeg/Preprocessed_data_250Hz_whiten" \
  "embedding_directory=${DATA_ROOT}/visual-embeddings/things-eeg" \
  "per_device_train_batch_size=${TRAIN_BATCH_SIZE}" \
  "num_train_epochs=${NUM_EPOCHS}" \
  "bf16=${BF16}" \
  "fp16=${FP16}"

{
  echo "started_at=$(date --iso-8601=seconds)"
  echo "hostname=$(hostname)"
  echo "git_commit=$(git -C "$REPO_ROOT" rev-parse HEAD)"
  echo "subject=${SUBJECT}"
  echo "setting=${SETTING}"
  echo "seed=${SEED}"
  echo "train_batch_size=${TRAIN_BATCH_SIZE}"
  echo "precision=${PRECISION}"
  echo "cuda_visible_devices=${CUDA_VISIBLE_DEVICES:-all}"
  python3 --version
  python3 -c 'import torch, transformers; print(f"torch={torch.__version__}"); print(f"transformers={transformers.__version__}")'
  nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader
} | tee "$METADATA_FILE"

cd "$REPO_ROOT"
python3 train_clip.py "$RESOLVED_CONFIG" 2>&1 | tee "${RUN_DIR}/train.log"
