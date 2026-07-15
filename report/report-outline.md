# Mini Assignment #2 Report Outline

## 1. Paper and reproduction target

- Paper: *Learning Brain Representation with Hierarchical Visual Embeddings* (ICLR 2026).
- Target: Table 3, THINGS-EEG intra-subject 200-way retrieval ablation.
- Hypothesis: B32+VAE improves Top-1 and Top-5 over B32.

## 2. Original and reproduced settings

| Item | Paper | Reproduction |
|---|---|---|
| Dataset/task | THINGS-EEG intra-subject, 200-way retrieval | Same; all 10 subjects |
| EEG input | 17 occipital/parietal channels, repeated trials averaged | Same; validated shape 17 x 250 |
| Visual targets | B32 versus B32+VAE | Authors' cached B32 (512-D) and VAE (1024-D) embeddings |
| Training | 25 epochs, AdamW, LR 5e-4, batch 1024, 10 warmup steps | Same; one seed (2025), BF16 |
| Evaluation | Top-1 and Top-5 over all 200 test candidates | Same; evaluation batch 200 |
| Hardware | Not used as the comparison variable | One NVIDIA RTX 5090 (32 GB), PyTorch 2.9.1+cu130 |

## 3. AI-assisted workflow

Record Codex usage, representative prompts, debugging decisions, approximate tokens/cost, AI-assisted working time, and manual verification.

## 4. Results

| Source/setting | Top-1 (%) | Top-5 (%) |
|---|---:|---:|
| Paper, B32 (10-subject mean) | 52.2 | 83.3 |
| Paper, B32+VAE (10-subject mean) | 73.6 | 94.3 |
| Reproduction, B32 (10-subject mean) | 21.6 | 53.1 |
| Reproduction, B32+VAE (10-subject mean) | 50.2 | 82.6 |

Adding VAE features improves reproduced Top-1 by 28.6 percentage points and Top-5 by
29.5 points. The paper reports gains of 21.4 and 11.0 points respectively. B32+VAE
outperforms B32 for both metrics in every one of the ten reproduced subjects.

## 5. Analysis and limitations

The reproduction strongly supports the directional conclusion: low-level VAE features
substantially improve retrieval over B32 alone, consistently across all subjects. Absolute
scores are lower than the paper: -30.6/-30.3 points for B32 and -23.4/-11.8 points for
B32+VAE (Top-1/Top-5). Likely sources include one seed, BF16, dependency/code-version drift,
and differences between the released training code and the paper settings. Cached visual
embeddings preserve the target representations but avoid recomputing the visual encoders.

## 6. Reproducibility and resources

- Mean B32 end-to-end runtime: 74.9 seconds per subject.
- Mean B32+VAE end-to-end runtime: 93.2 seconds per subject.
- Sum of recorded end-to-end runtimes for 20 runs: 1,681 seconds (28 minutes 1 second).
- Repository: https://github.com/HUI-HUI-lab/brainhive-retrieval-reproduction
- Compact machine-readable results and run metadata are stored under `report/data/`.
