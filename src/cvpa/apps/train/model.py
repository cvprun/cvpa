# -*- coding: utf-8 -*-

from typing import Any, List

from transformers import AutoImageProcessor, AutoModelForImageClassification


def build_processor(model_id: str) -> Any:
    return AutoImageProcessor.from_pretrained(model_id)


def build_model(model_id: str, labels: List[str]) -> Any:
    id2label = {i: name for i, name in enumerate(labels)}
    label2id = {name: i for i, name in enumerate(labels)}
    return AutoModelForImageClassification.from_pretrained(
        model_id,
        num_labels=len(labels),
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True,
    )
