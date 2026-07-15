# AI-assisted work log

Record actual usage rather than reconstructing estimates at the end of the assignment.

| Date | Tool/model | Task | Representative prompt or action | Human time | AI time/tokens/cost |
|---|---|---|---|---:|---:|
| 2026-07-15 | Codex | Reproduction planning and repository inspection | Inspect Brain-HIVE and design a minimal retrieval reproduction for Table 3. | TBD | TBD |
| 2026-07-15 | Codex | Reproduction scaffolding | Create paper-aligned B32 and B32+VAE data, training, aggregation, and documentation workflows. | TBD | TBD |
| 2026-07-16 | Codex | Server setup and debugging | Inspect GPU/disk state, configure an isolated environment, diagnose Transformers and missing-diffusers compatibility errors, and validate the data pipeline. | TBD | Copy from Codex usage UI |
| 2026-07-16 | Codex | Experiment execution | Run a one-epoch smoke test, launch the 25-epoch B32/B32+VAE comparison, aggregate metrics, and synchronize compact artifacts. | TBD | Copy from Codex usage UI |

Representative debugging prompts/actions included: "check why the downloader is not making
progress", "validate EEG and embedding IDs before using a GPU", and "diagnose the smoke-test
traceback without modifying shared server software".

Before submission, add debugging prompts, total approximate token usage, incremental cost, AI-assisted working time, data preparation time, and experiment runtime. Never include passwords, API keys, SSH keys, or private server details.
