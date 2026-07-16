#!/usr/bin/env bash
set -euo pipefail

DEFAULT_ENV_PREFIX="/data0/${USER:-user}/brainhive-retrieval/envs/brainhive-retrieval"
ENV_PREFIX="${1:-$DEFAULT_ENV_PREFIX}"
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
TORCH_INDEX_URL="${TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu130}"
TORCH_VERSION="${TORCH_VERSION:-2.9.1}"
TORCHVISION_VERSION="${TORCHVISION_VERSION:-0.24.1}"
export PIP_DEFAULT_TIMEOUT="${PIP_DEFAULT_TIMEOUT:-120}"
export PIP_RETRIES="${PIP_RETRIES:-10}"

CONDA_BASE="$(conda info --base)"
source "${CONDA_BASE}/etc/profile.d/conda.sh"

if [[ ! -x "${ENV_PREFIX}/bin/python" ]]; then
  conda create --prefix "${ENV_PREFIX}" "python=${PYTHON_VERSION}" pip -y
fi

conda activate "${ENV_PREFIX}"
python -m pip install --upgrade pip
python -m pip install \
  "torch==${TORCH_VERSION}" \
  "torchvision==${TORCHVISION_VERSION}" \
  --index-url "${TORCH_INDEX_URL}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python -m pip install -r "${REPO_ROOT}/reproduction/requirements.txt"

python - <<'PY'
import torch
import transformers
import datasets

print("torch", torch.__version__)
print("torch_cuda", torch.version.cuda)
print("cuda_available", torch.cuda.is_available())
print("gpu_count", torch.cuda.device_count())
print("transformers", transformers.__version__)
print("datasets", datasets.__version__)
if not torch.cuda.is_available():
    raise SystemExit("CUDA is not available in the reproduction environment")
PY
