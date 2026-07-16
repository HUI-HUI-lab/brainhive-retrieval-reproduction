---
name: research-gpu-ssh
description: Safely connect to a shared research GPU server over SSH, inspect resources, synchronize an experiment repository, launch and monitor reproducible jobs, and collect compact results. Use for remote GPU experiments, server diagnostics, data transfer, job monitoring, or resuming a server-side run.
---

# Research GPU SSH

## Protect credentials and shared resources

- Use an SSH config alias supplied by the user or administrator.
- Never place passwords, private keys, tokens, host addresses, or API keys in a repository, command argument, log, or answer.
- Ask the user to complete interactive password authentication when key authentication is unavailable.
- Verify a new host key with the administrator. Never disable host-key checking.
- Treat existing files, environments, datasets, processes, and GPUs as belonging to other users.
- Do not stop unrelated jobs, modify system CUDA, or delete shared files.

## Inspect before changing state

Connect using the configured alias and inspect the environment:

```bash
hostname
whoami
pwd
nvidia-smi
df -h
free -h
python3 --version
git --version
```

Inspect `git status` before synchronizing code. Put large datasets, caches, environments,
checkpoints, and logs on the server's designated data volume rather than the root disk.

## Prepare a reproducible run

1. Create a project-specific virtual environment without changing system Python.
2. Clone or fast-forward the approved Git repository without embedding credentials in its URL.
3. Download only the required dataset subset and cached features.
4. Reuse a trusted, read-only shared public dataset cache only when permissions allow; link or copy it into the documented project layout without modifying the source.
5. Validate sample counts, tensor shapes, feature dimensions, and ID alignment on CPU.
6. Audit embedding health before training. For contrastive features, sample unrelated
   image pairs and inspect cosine statistics; an unexpectedly near-one median can reveal
   a collapsed or duplicated cache even when IDs and dimensions look correct.
7. If a trusted cache exists, verify at least one row against a fresh canonical-model
   extraction and record the model identifier, preprocessing, similarity, and file origin.
8. Check GPU memory, utilization, and compute processes immediately before launch.
9. Run a one-epoch smoke test before a formal experiment.

## Launch and monitor

Pin the job to an idle GPU with `CUDA_VISIBLE_DEVICES`. Use `tmux` for long runs or
`nohup` for short unattended runs, and always redirect output to a persistent log.
If all shared GPUs are occupied, prefer a documented CPU FP32 run when the model is
small enough; cap BLAS/OpenMP threads and concurrent workers to avoid oversubscription.

Record:

- Git commit, resolved configuration, random seed, and command;
- host, GPU, driver, Python, PyTorch, and key dependency versions;
- start/end timestamps, runtime, exit status, and output directory;
- final metrics and any deviations from the source experiment.

Monitor with `nvidia-smi`, process inspection, and log tails. A process that exits is not
necessarily successful; verify the recorded exit status and expected result files.

## Collect and hand off

Copy compact JSON/CSV metrics, resolved configs, and metadata back to the local repository.
Keep large data and checkpoints on the server unless explicitly requested. Report the remote
project path, active PID or `tmux` session, log path, completed/failed runs, GPU state, and the
exact resume command. Never include credentials or private infrastructure details in public
artifacts.
