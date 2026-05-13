# -*- coding: utf-8 -*-

from cvpa.logging.loggers import infer_logger as logger


class InferApplication:
    def __init__(
        self,
        model: str,
        input_path: str,
        device: str,
        batch_size: int,
        top_k: int,
    ):
        self._model = model
        self._input_path = input_path
        self._device = device
        self._batch_size = batch_size
        self._top_k = top_k

    def start(self) -> None:
        logger.info(
            f"Starting inference: model={self._model}, input={self._input_path}"
        )
        logger.warning("InferApplication is not implemented yet")
