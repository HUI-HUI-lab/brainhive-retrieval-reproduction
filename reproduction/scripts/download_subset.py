#!/usr/bin/env python3
"""Download only selected THINGS-EEG subjects and cached B32/VAE embeddings."""

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
    args = parser.parse_args()

    root = args.data_root.expanduser().resolve()
    eeg_root = root / "things-eeg"
    embedding_root = root / "visual-embeddings"

    eeg_patterns = [
        f"Preprocessed_data_250Hz_whiten/sub-{subject:02d}/{split}.pt"
        for subject in args.subjects
        for split in ("train", "test")
    ]
    snapshot_download(
        repo_id="Haitao999/things-eeg",
        repo_type="dataset",
        allow_patterns=eeg_patterns,
        local_dir=eeg_root,
    )

    embedding_patterns = [
        f"things-eeg/things_{split}_{model}-*.parquet"
        for split in ("train", "test")
        for model in ("CLIP-ViT-B-32-laion2B-s34B-b79K", "vae")
    ]
    snapshot_download(
        repo_id="fakekungfu/Brain-HIVE_Visual_Embeddings",
        repo_type="dataset",
        allow_patterns=embedding_patterns,
        local_dir=embedding_root,
    )

    print(f"EEG directory: {eeg_root / 'Preprocessed_data_250Hz_whiten'}")
    print(f"Embedding directory: {embedding_root / 'things-eeg'}")


if __name__ == "__main__":
    main()

