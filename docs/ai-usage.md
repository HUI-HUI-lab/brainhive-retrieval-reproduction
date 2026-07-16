# AI-assisted work log

Record actual usage rather than reconstructing estimates at the end of the assignment.

| Date | Tool/model | Task | Representative prompt or action | Human time | AI time/tokens/cost |
|---|---|---|---|---:|---:|
| 2026-07-15 | Codex | Reproduction planning and repository inspection | Inspect Brain-HIVE and design a minimal retrieval reproduction for Table 3. | ~30 min | Included in estimate below |
| 2026-07-15 | Codex | Reproduction scaffolding | Create paper-aligned B32 and B32+VAE data, training, aggregation, and documentation workflows. | ~45 min | Included in estimate below |
| 2026-07-16 | Codex | Server setup and debugging | Inspect GPU/disk state, configure an isolated environment, diagnose Transformers and missing-diffusers compatibility errors, and validate the data pipeline. | ~60 min | Included in estimate below |
| 2026-07-16 | Codex | Experiment execution | Run a one-epoch smoke test, launch the 25-epoch B32/B32+VAE comparison, aggregate metrics, and synchronize compact artifacts. | ~30 min | Included in estimate below |
| 2026-07-16 | Codex | Cache forensics | Compare public and trusted B32 vectors, recompute a canonical image embedding, test row permutation, and measure feature collapse. | ~45 min | Included in estimate below |
| 2026-07-16 | Codex | Corrected experiment | Validate canonical B32 plus VAE, run 20 CPU FP32 jobs with four workers, aggregate results, and update all deliverables. | ~45 min | Included in estimate below |

Representative debugging prompts/actions included: "check why the downloader is not making
progress", "validate EEG and embedding IDs before using a GPU", and "diagnose the smoke-test
traceback without modifying shared server software".

Current transparent estimate: approximately 200k AI tokens, approximately four hours
of AI-assisted working time across planning, debugging, experiment monitoring, analysis,
and document production. Incremental cost was not separately metered because Codex was
used through the account subscription. The corrected formal matrix took approximately
17 minutes 47 seconds wall time; summed per-run runtime was 3,867 seconds. Replace the
token estimate with an account export if one becomes available. Never include passwords,
API keys, SSH keys, private host addresses, or private server details.
