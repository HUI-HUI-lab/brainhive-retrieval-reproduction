#!/usr/bin/env python3
"""Download selected THINGS-EEG subjects and visual-embedding artifacts.

The public B32 cache is excluded by default because the snapshot inspected for this
reproduction was severely collapsed. Regenerate B32 from the canonical LAION model,
or opt in explicitly and validate it before training.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


def parse_subjects(value: str) -> list[int]:
    subjects = sorted({int(item) for item in value.split(",") if item.strip()})
    if not subjects or any(subject < 1 or subject > 10 for subject in subjects):
        raise argparse.ArgumentTypeError("subjects must be comma-separated IDs from 1 to 10")
    return subjects


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--subjects", type=parse_subjects, default=parse_subjects("1"))
    parser.add_argument("--skip-eeg", action="store_true")
    parser.add_argument("--skip-embeddings", action="store_true")
    parser.add_argument(
        "--include-unverified-b32",
        action="store_true",
        help="also download the public B32 cache; validate it before training",
    )
    args = parser.parse_args()

    if args.skip_eeg and args.skip_embeddings:
        parser.error("--skip-eeg and --skip-embeddings cannot be used together")

    root = args.data_root.expanduser().resolve()
    eeg_root = root / "things-eeg"
    embedding_root = root / "visual-embeddings"

    eeg_patterns = [
        f"Preprocessed_data_250Hz_whiten/sub-{subject:02d}/{split}.pt"
        for subject in args.subjects
        for split in ("train", "test")
    ]
    if not args.skip_eeg:
        snapshot_download(
            repo_id="Haitao999/things-eeg",
            repo_type="dataset",
            allow_patterns=eeg_patterns,
            local_dir=eeg_root,
        )

    models = ["vae"]
    if args.include_unverified_b32:
        models.insert(0, "CLIP-ViT-B-32-laion2B-s34B-b79K")

    embedding_patterns = [
        f"things-eeg/things_{split}_{model}-*.parquet"
        for split in ("train", "test")
        for model in models
    ]
    if not args.skip_embeddings:
        snapshot_download(
            repo_id="fakekungfu/Brain-HIVE_Visual_Embeddings",
            repo_type="dataset",
            allow_patterns=embedding_patterns,
            local_dir=embedding_root,
        )

    print(f"EEG directory: {eeg_root / 'Preprocessed_data_250Hz_whiten'}")
    print(f"Embedding directory: {embedding_root / 'things-eeg'}")
    if args.include_unverified_b32:
        print(
            "WARNING: the downloaded B32 cache is unverified. Run "
            "reproduction/scripts/validate_embeddings.py before training."
        )
    elif not args.skip_embeddings:
        print("Downloaded VAE only. Regenerate canonical B32 before the experiment.")


if __name__ == "__main__":
    main()
