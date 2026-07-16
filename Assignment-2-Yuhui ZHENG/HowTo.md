# BrainHIVE Retrieval Reproduction: How To Run

This repository reproduces the THINGS-EEG intra-subject 200-way retrieval
ablation from *Learning Brain Representation with Hierarchical Visual Embeddings*.
The comparison is LAION CLIP ViT-B/32 (`B32`) versus `B32 + SDXL VAE`.

## Final reproduced result

| Setting | Paper Table 7 Top-1 / Top-5 | Reproduction Top-1 / Top-5 |
|---|---:|---:|
| B32 | 51.2 / 83.0 | **48.8 / 81.0** |
| B32+VAE | 73.7 / 94.1 | **69.7 / 92.95** |

The reproduced VAE gain is +20.9/+11.95 points, close to the paper's
+22.5/+11.1 points. All values are ten-subject means.

## AI models and tools

- Codex was used for repository inspection, implementation, SSH diagnostics,
  cache forensics, experiment monitoring, aggregation, documentation, and PDF
  generation.
- Git, GitHub CLI, SSH/tmux, PyTorch, Hugging Face Datasets, NumPy, PyArrow,
  ReportLab, pypdf, and Poppler were used in the workflow.
- Representative prompting strategy: inspect before editing; validate shapes and
  IDs before training; reproduce one subject first; compare input features when
  metrics diverge; retain machine-readable logs for every formal run.

No API keys, passwords, private keys, or private server addresses belong in this
repository.

## Environment

Create an isolated Linux environment and install a CUDA-compatible PyTorch build
separately. CPU FP32 is also supported.

```bash
conda create -n brainhive-retrieval python=3.12 -y
conda activate brainhive-retrieval
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install -r reproduction/requirements.txt
```

On the research server the isolated environment was created with:

```bash
bash reproduction/scripts/setup_server_env.sh \
  /data0/$USER/brainhive-retrieval/envs/brainhive-retrieval
```

## Data layout

```text
DATA_ROOT/
├── things-eeg/
│   └── Preprocessed_data_250Hz_whiten/
│       ├── sub-01/{train,test}.pt
│       └── ... sub-10/{train,test}.pt
└── visual-embeddings/
    └── things-eeg/
        ├── things_{train,test}_CLIP-ViT-B-32-laion2B-s34B-b79K-part-*.parquet
        └── things_{train,test}_vae-part-*.parquet
```

Download EEG and the VAE cache:

```bash
python reproduction/scripts/download_subset.py \
  --data-root "$DATA_ROOT" \
  --subjects 1,2,3,4,5,6,7,8,9,10
```

The downloader intentionally excludes the public B32 cache by default. The cache
snapshot tested during this assignment was collapsed and produced misleadingly
low scores. If downloaded with `--include-unverified-b32`, it must be treated as
untrusted until the health check passes.

## Generate or supply canonical B32

Use the official model
`laion/CLIP-ViT-B-32-laion2B-s34B-b79K`, its canonical image processor, and the
original THINGS training/test images. The upstream `build_embeddings.py` supports
this model through `CLIPVisionModelWithProjection`.

Example environment variables for each train/test split:

```bash
export DATASET_NAME=things
export IMAGE_DIR=/path/to/things-eeg-images
export MODEL_PATH=laion/CLIP-ViT-B-32-laion2B-s34B-b79K
export OUTPUT_DIR="$DATA_ROOT/visual-embeddings/things-eeg"
export SPLIT=train
accelerate launch --config_file configs/gpu_cfg_single.yaml \
  build_embeddings.py --config_file configs/build_embeddings.yaml
```

Repeat with `SPLIT=test`. The corrected assignment run reused a trusted read-only
canonical cache and verified one image against a fresh official-model extraction:
cosine similarity was 0.99992.

## Mandatory preflight checks

First detect collapsed B32 features:

```bash
python reproduction/scripts/validate_embeddings.py \
  --data-root "$DATA_ROOT" \
  --output "$RESULTS_ROOT/b32-health.json"
```

A healthy canonical cache in this experiment had random-pair cosine median
approximately 0.3264. The rejected public cache had median 0.9943 and fails the
default 0.95 threshold.

Then verify EEG shapes, dimensions, counts, and image-ID alignment:

```bash
python reproduction/scripts/validate_data.py \
  --data-root "$DATA_ROOT" \
  --subjects 1 \
  --models CLIP-ViT-B-32-laion2B-s34B-b79K vae \
  --output "$RESULTS_ROOT/data-validation.json"
```

Expected: 16,540 train examples, 200 test examples, EEG shape 17x250,
B32 dimension 512, VAE dimension 1024.

## Smoke test

GPU BF16:

```bash
NUM_EPOCHS=1 TRAIN_BATCH_SIZE=1024 PRECISION=bf16 \
  bash reproduction/scripts/run_retrieval.sh \
  "$DATA_ROOT" "$RESULTS_ROOT/smoke" 1 b32_vae 2025
```

CPU FP32:

```bash
NUM_EPOCHS=1 PRECISION=fp32 USE_CPU=true \
  bash reproduction/scripts/run_retrieval.sh \
  "$DATA_ROOT" "$RESULTS_ROOT/smoke" 1 b32_vae 2025
```

## Formal experiment

GPU, sequential:

```bash
PRECISION=bf16 MAX_PARALLEL=1 \
  bash reproduction/scripts/run_matrix.sh \
  "$DATA_ROOT" "$RESULTS_ROOT/formal" \
  1,2,3,4,5,6,7,8,9,10 2025
```

CPU FP32, four parallel workers (the final corrected run):

```bash
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 \
PRECISION=fp32 USE_CPU=true MAX_PARALLEL=4 \
  bash reproduction/scripts/run_matrix.sh \
  "$DATA_ROOT" "$RESULTS_ROOT/formal" \
  1,2,3,4,5,6,7,8,9,10 2025
```

Keep evaluation batch size at 200 because the metric expects all candidates in a
single similarity matrix. Reducing the training batch changes the number of
in-batch negatives and should be reported as an experimental modification.

## Aggregate and expected outputs

```bash
bash reproduction/scripts/aggregate.sh "$RESULTS_ROOT/formal"
```

Each run contains:

- `resolved_config.yaml`
- `run_metadata.txt`
- `train.log`
- `eval_results.json`
- model checkpoint files (kept off GitHub)

The aggregate command creates `b32_summary.{csv,json}` and
`b32_vae_summary.{csv,json}`. Compact final results are committed under
[`report/data`](report/data/).

## Modifications and limitations

- One seed (2025) was used instead of multiple repeated runs.
- The corrected matrix used CPU FP32 with four concurrent workers because both
  shared GPUs were occupied by other users.
- Canonical cached B32 features replaced on-the-fly visual encoding, after direct
  verification against the official model.
- Public VAE shards were reused after health and alignment checks.
- The released repository and paper contain minor configuration/version drift;
  this reproduction explicitly uses 10 warmup steps and the MBP/BrainMLP setup.
