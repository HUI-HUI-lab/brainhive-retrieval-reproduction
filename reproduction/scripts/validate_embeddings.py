#!/usr/bin/env python3
"""Detect collapsed or malformed visual-embedding caches before training."""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq


DEFAULT_MODEL = "CLIP-ViT-B-32-laion2B-s34B-b79K"


def load_embeddings(directory: Path, split: str, model: str) -> tuple[list[str], np.ndarray]:
    pattern = directory / f"things_{split}_{model}-part-*-of-*.parquet"
    files = sorted(glob.glob(str(pattern)))
    if not files:
        raise FileNotFoundError(f"No embedding shards match {pattern}")

    ids: list[str] = []
    chunks: list[np.ndarray] = []
    for file in files:
        table = pq.read_table(file, columns=["image_id", "emb"])
        ids.extend(str(value) for value in table["image_id"].to_pylist())
        chunks.append(np.asarray(table["emb"].to_pylist(), dtype=np.float32))
    return ids, np.concatenate(chunks, axis=0)


def summarize(matrix: np.ndarray, sample_size: int, pair_count: int, seed: int) -> dict[str, object]:
    if matrix.ndim != 2 or not np.isfinite(matrix).all():
        raise ValueError("Embedding matrix must be finite and two-dimensional")
    norms = np.linalg.norm(matrix, axis=1)
    if np.any(norms == 0):
        raise ValueError("Embedding matrix contains zero-norm rows")

    rng = np.random.default_rng(seed)
    chosen = rng.choice(len(matrix), size=min(sample_size, len(matrix)), replace=False)
    sample = matrix[chosen] / norms[chosen, None]
    left = rng.integers(0, len(sample), size=pair_count)
    right = rng.integers(0, len(sample), size=pair_count)
    keep = left != right
    cosine = np.sum(sample[left[keep]] * sample[right[keep]], axis=1)
    mean_vector_norm = float(np.linalg.norm(sample.mean(axis=0)))

    return {
        "rows": int(matrix.shape[0]),
        "dimension": int(matrix.shape[1]),
        "norm_median": float(np.median(norms)),
        "random_pair_cosine_q01": float(np.quantile(cosine, 0.01)),
        "random_pair_cosine_median": float(np.median(cosine)),
        "random_pair_cosine_mean": float(np.mean(cosine)),
        "random_pair_cosine_q99": float(np.quantile(cosine, 0.99)),
        "normalized_mean_vector_norm": mean_vector_norm,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--split", choices=("train", "test"), default="train")
    parser.add_argument("--expected-dim", type=int, default=512)
    parser.add_argument("--sample-size", type=int, default=1000)
    parser.add_argument("--pair-count", type=int, default=20000)
    parser.add_argument("--collapse-threshold", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    directory = args.data_root.expanduser().resolve() / "visual-embeddings" / "things-eeg"
    image_ids, matrix = load_embeddings(directory, args.split, args.model)
    result = summarize(matrix, args.sample_size, args.pair_count, args.seed)
    result.update(
        {
            "model": args.model,
            "split": args.split,
            "unique_image_ids": len(set(image_ids)),
            "collapse_threshold": args.collapse_threshold,
        }
    )

    if result["rows"] != len(set(image_ids)):
        raise ValueError("Embedding image IDs are not unique")
    if result["dimension"] != args.expected_dim:
        raise ValueError(
            f"Expected dimension {args.expected_dim}, got {result['dimension']}"
        )

    collapsed = result["random_pair_cosine_median"] >= args.collapse_threshold
    result["status"] = "collapsed" if collapsed else "pass"
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if collapsed:
        raise SystemExit(
            "Embedding cache appears collapsed: median random-pair cosine is "
            f"{result['random_pair_cosine_median']:.4f}"
        )


if __name__ == "__main__":
    main()
