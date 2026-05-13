# -*- coding: utf-8 -*-

from typing import Any, List, Tuple

from torchvision.datasets import ImageFolder


class _ProcessorTransform:
    def __init__(self, processor: Any):
        self._processor = processor

    def __call__(self, image: Any) -> Any:
        return self._processor(image, return_tensors="pt")["pixel_values"].squeeze(0)


def build_dataset(data_dir: str, processor: Any) -> Tuple[ImageFolder, List[str]]:
    dataset = ImageFolder(root=data_dir, transform=_ProcessorTransform(processor))
    return dataset, list(dataset.classes)
