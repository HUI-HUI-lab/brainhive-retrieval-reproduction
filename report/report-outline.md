# Mini Assignment #2 Report Source Outline

## Target

- Paper: *Learning Brain Representation with Hierarchical Visual Embeddings* (ICLR 2026).
- Target: THINGS-EEG intra-subject 200-way retrieval, B32 versus B32+VAE.
- Main question: does adding low-level VAE information improve retrieval over B32?

## Settings

| Item | Paper | Corrected reproduction |
|---|---|---|
| Subjects | 10 | 10 |
| EEG | 17 O+P channels, trial average, 0-1000 ms | Same, 17x250 samples |
| Targets | LAION B32; B32+SDXL VAE | Canonical B32 (512-D); verified VAE (1024-D) |
| Training | 25 epochs, batch 1024, AdamW, 5e-4, cosine, 10 warmup | Same, seed 2025 |
| Numeric/device | Paper GPU precision not fully specified | CPU FP32, four concurrent workers |
| Metric | 200-way Top-1/Top-5 | Same, evaluation batch 200 |

## Cache audit

- Initial public-cache run: B32 21.6/53.05; B32+VAE 50.2/82.55.
- Public B32 random-pair cosine median: 0.9943 (collapsed).
- Canonical B32 random-pair cosine median: 0.3264.
- Fresh official-model extraction versus trusted canonical cache: cosine 0.99992.
- Fresh extraction versus public cache for the same image: cosine 0.20091.

## Corrected result

| Source/setting | Top-1 (%) | Top-5 (%) |
|---|---:|---:|
| Paper Table 7, B32 | 51.2 | 83.0 |
| Corrected reproduction, B32 | 48.8 | 81.0 |
| Paper Table 7, B32+VAE | 73.7 | 94.1 |
| Corrected reproduction, B32+VAE | 69.7 | 92.95 |

The reproduced VAE gain is +20.9/+11.95 points, close to the paper's
+22.5/+11.1. The conclusion is supported across all ten subjects.

## Resources

- 20/20 formal runs succeeded.
- Mean runtime 193.35 seconds/run; summed runtime 3,867 seconds.
- Four CPU FP32 workers; matrix wall time about 17 minutes 47 seconds.
- Repository: https://github.com/HUI-HUI-lab/brainhive-retrieval-reproduction
