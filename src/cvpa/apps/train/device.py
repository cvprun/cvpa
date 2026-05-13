# -*- coding: utf-8 -*-

DEVICE_AUTO = "auto"


def resolve_device(spec: str) -> str:
    if spec != DEVICE_AUTO:
        return spec

    import torch

    if torch.cuda.is_available():
        return "cuda"

    mps = getattr(torch.backends, "mps", None)
    if mps is not None and mps.is_available():
        return "mps"

    return "cpu"
