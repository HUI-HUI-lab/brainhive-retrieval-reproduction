#!/usr/bin/env python3
"""CPU-only import and forward/backward check for the retrieval model."""

from __future__ import annotations

import torch

from main.models_clip import BrainCLIPModel, CLIPConfig


def main() -> None:
    config = CLIPConfig(
        hidden_size=1024,
        intermediate_size=1024,
        brain_backbone="brain_mlp",
        brain_channels=17,
        brain_sequence_length=250,
        proj_meta={
            "CLIP-ViT-B-32-laion2B-s34B-b79K": 512,
            "vae": 1024,
        },
    )
    model = BrainCLIPModel(config).cpu().train()
    batch_size = 4
    output = model(
        brain_signals=torch.randn(batch_size, 17, 250),
        embs={
            "CLIP-ViT-B-32-laion2B-s34B-b79K": torch.randn(batch_size, 512),
            "vae": torch.randn(batch_size, 1024),
        },
        return_loss=True,
    )
    if output.loss is None or output.logits_per_brain.shape != (batch_size, batch_size):
        raise RuntimeError("Unexpected retrieval model output")
    output.loss.backward()
    print(f"loss={output.loss.item():.6f}")
    print(f"logits_shape={tuple(output.logits_per_brain.shape)}")
    print("forward_backward_check=ok")


if __name__ == "__main__":
    main()
