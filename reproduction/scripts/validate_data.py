#!/usr/bin/env python3
"""Validate THINGS-EEG shapes and image/embedding alignment before training."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def parse_subjects(value: str) -> list[int]:
    subjects = sorted({int(item) for item in value.split(",") if item.strip()})
    if not subjects or any(subject < 1 or subject > 10 for subject in subjects):
        raise argparse.ArgumentTypeError("subjects must be comma-separated IDs from 1 to 10")
    return subjects


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--subjects", type=parse_subjects, default=parse_subjects("1"))
    parser.add_argument(
        "--models",
        nargs="+",
        default=["CLIP-ViT-B-32-laion2B-s34B-b79K", "vae"],
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root))

    from main.data import (  # pylint: disable=import-outside-toplevel
        build_brain_with_emb_dataset,
        load_embedding_datasets,
        load_things_brain_dataset,
    )

    data_root = args.data_root.expanduser().resolve()
    summary: dict[str, object] = {
        "data_root": str(data_root),
        "subjects": args.subjects,
        "models": args.models,
        "splits": {},
    }

    for split in ("train", "test"):
        brain_ds = load_things_brain_dataset(
            data_directory=str(
                data_root / "things-eeg" / "Preprocessed_data_250Hz_whiten"
            ),
            split=split,
            subject_ids=args.subjects,
            brain_key="eeg",
            avg_trials=True,
            selected_channels="O1,O2,Oz,PO3,PO4,PO7,PO8,POz,P1,P2,P3,P4,P5,P6,P7,P8,Pz",
        )
        emb_dss = load_embedding_datasets(
            embedding_directory=str(data_root / "visual-embeddings" / "things-eeg"),
            dataset_key="things",
            split=split,
            model_keys=args.models,
            cache_dir=str(data_root / ".datasets-cache"),
        )
        paired = build_brain_with_emb_dataset(brain_ds=brain_ds, emb_dss=emb_dss)
        first = paired[0]
        last = paired[len(paired) - 1]
        emb_dims = {
            model: len(first[f"emb_{model}"])
            for model in args.models
        }
        summary["splits"][split] = {
            "examples": len(paired),
            "eeg_shape": list(np.asarray(first["eeg"]).shape),
            "embedding_dims": emb_dims,
            "first_image_id": first["image_id"],
            "last_image_id": last["image_id"],
            "subject_ids": sorted(set(paired["subject_id"])),
        }

    rendered = json.dumps(summary, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
