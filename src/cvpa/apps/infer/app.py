# -*- coding: utf-8 -*-

from os import makedirs
from os.path import basename, join, splitext
from typing import Any, Dict, List

from PIL import Image

from cvpa.apps.infer import _imports  # noqa: F401  # Gate ML dependencies
from cvpa.apps.infer.device import resolve_device
from cvpa.apps.infer.drawers import draw_result
from cvpa.apps.infer.formatters import TASK_IMAGE_CLASSIFICATION, format_result
from cvpa.apps.infer.inputs import iter_image_paths
from cvpa.logging.loggers import infer_logger as logger


class InferApplication:
    def __init__(
        self,
        model: str,
        input_path: str,
        output_dir: str,
        device: str,
        batch_size: int,
        top_k: int,
    ):
        self._model = model
        self._input_path = input_path
        self._output_dir = output_dir
        self._device = device
        self._batch_size = batch_size
        self._top_k = top_k

    def start(self) -> None:
        from transformers import pipeline

        device = resolve_device(self._device)
        logger.info(f"Loading model: {self._model} (device={device})")

        pipe = pipeline(task=None, model=self._model, device=device)
        logger.info(f"Pipeline ready: task={pipe.task}")

        makedirs(self._output_dir, exist_ok=True)

        call_kwargs: Dict[str, Any] = {}
        if pipe.task == TASK_IMAGE_CLASSIFICATION:
            call_kwargs["top_k"] = self._top_k

        batch: List[str] = []
        for path in iter_image_paths(self._input_path):
            batch.append(path)
            if len(batch) >= self._batch_size:
                self._run_batch(pipe, batch, call_kwargs)
                batch.clear()
        if batch:
            self._run_batch(pipe, batch, call_kwargs)

    def _run_batch(self, pipe, paths: List[str], call_kwargs: Dict[str, Any]) -> None:
        try:
            results = pipe(paths, **call_kwargs)
        except Exception as e:
            logger.error(f"Batch failed ({len(paths)} images): {e}")
            return

        for path, result in zip(paths, results):
            self._save_annotated(pipe.task, path, result)

    def _save_annotated(self, task: str, path: str, result: Any) -> None:
        try:
            with Image.open(path) as src:
                src.load()
                annotated = draw_result(task, src, result)
        except Exception as e:
            logger.error(f"Failed to annotate {path}: {e}")
            return

        out_name = splitext(basename(path))[0] + ".png"
        out_path = join(self._output_dir, out_name)
        annotated.save(out_path, format="PNG")
        logger.info(f"Wrote: {out_path} | {format_result(task, path, result)}")
