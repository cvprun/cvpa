# -*- coding: utf-8 -*-

from typing import Optional

from cvpa.apps.train import _imports  # noqa: F401  # Gate ML dependencies
from cvpa.logging.loggers import train_logger as logger


class TrainApplication:
    def __init__(
        self,
        model: str,
        data_dir: str,
        output_dir: str,
        epochs: int,
        batch_size: int,
        lr: float,
        device: str,
        resume: Optional[str] = None,
    ):
        self._model = model
        self._data_dir = data_dir
        self._output_dir = output_dir
        self._epochs = epochs
        self._batch_size = batch_size
        self._lr = lr
        self._device = device
        self._resume = resume

    def start(self) -> None:
        logger.info(f"Starting training: model={self._model}, device={self._device}")
        logger.warning("TrainApplication is not implemented yet")
