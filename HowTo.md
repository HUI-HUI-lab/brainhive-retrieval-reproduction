# BrainHIVE Retrieval Reproduction

This repository reproduces one result from *Learning Brain Representation with Hierarchical Visual Embeddings*: the THINGS-EEG intra-subject 200-way retrieval ablation comparing CLIP ViT-B/32 (`B32`) with `B32 + VAE`.

## Reproduction target

The paper reports 52.2%/83.3% Top-1/Top-5 for B32 and 73.6%/94.3% for B32+VAE, averaged across ten subjects. The reproduction tests the paper's main trend that adding low-level VAE features to semantic CLIP features improves retrieval.

## Environment

Create an isolated Linux environment with a CUDA-enabled PyTorch build compatible with the server driver. Then install this repository's dependencies. Do not install or change system CUDA drivers.

```bash
conda create -n brainhive-retrieval python=3.12 -y
conda activate brainhive-retrieval
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install -r reproduction/requirements.txt
```

The exact PyTorch index must be adjusted to the server's supported CUDA version.

On the group server, create the isolated environment on `/data0` with:

```bash
bash reproduction/scripts/setup_server_env.sh \
  /data0/yuhui/brainhive-retrieval/envs/brainhive-retrieval
```

## Data preparation

Download only the selected EEG subjects and the authors' cached B32/VAE embeddings:

```bash
python reproduction/scripts/download_subset.py \
  --data-root "$HOME/project/brainhive-data" \
  --subjects 1
```

If the EEG files already exist in a trusted shared cache, link or copy them into the
documented directory layout and add `--skip-eeg` to fetch only the visual embeddings.

The EEG files are trusted research artifacts serialized with PyTorch/pickle. Do not load similarly formatted files from an untrusted source.

Validate the file shapes and image-ID alignment before using a GPU:

```bash
python reproduction/scripts/validate_data.py \
  --data-root /data0/yuhui/brainhive-retrieval/data \
  --subjects 1 \
  --output /data0/yuhui/brainhive-retrieval/results/data-validation-sub01.json
```

## Smoke test

```bash
NUM_EPOCHS=1 TRAIN_BATCH_SIZE=1024 \
  bash reproduction/scripts/run_retrieval.sh \
  "$HOME/project/brainhive-data" \
  "$HOME/project/brainhive-results" \
  1 b32 2025
```

## Formal experiment

```bash
for subject in 1 2 3 4 5 6 7 8 9 10; do
  for setting in b32 b32_vae; do
    bash reproduction/scripts/run_retrieval.sh \
      "$HOME/project/brainhive-data" \
      "$HOME/project/brainhive-results" \
      "$subject" "$setting" 2025
  done
done
```

Keep `per_device_eval_batch_size=200`: the provided metric implementation expects all 200 candidates in one similarity matrix. If training batch 1024 does not fit, reduce `TRAIN_BATCH_SIZE`; record that modification because gradient accumulation does not restore the same number of in-batch negatives.

## Expected outputs

Each run writes `eval_results.json`, `resolved_config.yaml`, `run_metadata.txt`, and `train.log` under the output root. Aggregate completed runs with:

```bash
bash reproduction/scripts/aggregate.sh "$HOME/project/brainhive-results"
```

The expected conclusion is directional rather than exact numerical agreement: mean Top-1 and Top-5 for B32+VAE should exceed B32.

## Changes from the paper

- The initial reproduction uses fewer random seeds and may use fewer subjects.
- Cached author-provided visual embeddings replace recomputing B32 and VAE features.
- Batch size or numeric precision may change if required by server memory.
- The repository default has zero warmup steps; this reproduction uses the paper's stated 10-step warmup.
- The upstream intra-subject script currently names an RN50 run while selecting SynCLR. This reproduction uses explicit B32 and B32+VAE configurations to avoid that mismatch.
