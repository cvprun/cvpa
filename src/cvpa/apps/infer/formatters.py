# -*- coding: utf-8 -*-

from typing import Any, Callable, Dict, List, Mapping

TASK_IMAGE_CLASSIFICATION = "image-classification"
TASK_OBJECT_DETECTION = "object-detection"
TASK_IMAGE_SEGMENTATION = "image-segmentation"
TASK_ZERO_SHOT_IMAGE_CLASSIFICATION = "zero-shot-image-classification"


def _format_classification(path: str, result: List[Mapping[str, Any]]) -> str:
    parts = ", ".join(f"{r['label']}({r['score']:.3f})" for r in result)
    return f"{path}: {parts}"


def _format_detection(path: str, result: List[Mapping[str, Any]]) -> str:
    parts = ", ".join(f"{r['label']}({r['score']:.2f})" for r in result)
    return f"{path}: {len(result)} boxes - {parts}"


def _format_segmentation(path: str, result: List[Mapping[str, Any]]) -> str:
    labels = ", ".join(r["label"] for r in result)
    return f"{path}: {len(result)} masks - {labels}"


_FORMATTERS: Dict[str, Callable[[str, List[Mapping[str, Any]]], str]] = {
    TASK_IMAGE_CLASSIFICATION: _format_classification,
    TASK_ZERO_SHOT_IMAGE_CLASSIFICATION: _format_classification,
    TASK_OBJECT_DETECTION: _format_detection,
    TASK_IMAGE_SEGMENTATION: _format_segmentation,
}


def format_result(task: str, path: str, result: Any) -> str:
    fn = _FORMATTERS.get(task)
    if fn is not None and isinstance(result, list):
        return fn(path, result)
    return f"{path}: {result!r}"
