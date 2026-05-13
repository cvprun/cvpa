# -*- coding: utf-8 -*-

from os import makedirs
from os.path import join
from typing import Optional

from cvpa.apps.train import _imports  # noqa: F401  # Gate ML dependencies
from cvpa.apps.train.dataset import build_dataset
from cvpa.apps.train.device import resolve_device
from cvpa.apps.train.model import build_model, build_processor
from cvpa.logging.loggers import train_logger as logger

_LOG_EVERY_N_STEPS = 10


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
        import torch
        from torch.optim import AdamW
        from torch.utils.data import DataLoader

        device = resolve_device(self._device)
        source = self._resume or self._model
        logger.info(f"Loading source: {source} (device={device})")

        processor = build_processor(source)
        dataset, labels = build_dataset(self._data_dir, processor)
        logger.info(f"Dataset: {len(dataset)} samples, {len(labels)} classes")

        model = build_model(source, labels).to(device)
        model.train()

        loader = DataLoader(
            dataset,
            batch_size=self._batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=device.startswith("cuda"),
        )

        optimizer = AdamW(model.parameters(), lr=self._lr)

        makedirs(self._output_dir, exist_ok=True)

        total_steps = len(loader)
        for epoch in range(1, self._epochs + 1):
            running_loss = 0.0
            for step, (pixel_values, target) in enumerate(loader, start=1):
                pixel_values = pixel_values.to(device)
                target = target.to(device)

                outputs = model(pixel_values=pixel_values, labels=target)
                loss = outputs.loss

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                running_loss += float(loss.item())

                if step % _LOG_EVERY_N_STEPS == 0 or step == total_steps:
                    logger.info(
                        f"[epoch {epoch}/{self._epochs}] "
                        f"step {step}/{total_steps} loss={loss.item():.4f}"
                    )

            mean_loss = running_loss / max(total_steps, 1)
            ckpt_dir = join(self._output_dir, f"checkpoint-{epoch}")
            model.save_pretrained(ckpt_dir)
            processor.save_pretrained(ckpt_dir)
            logger.info(
                f"[epoch {epoch}/{self._epochs}] "
                f"mean_loss={mean_loss:.4f} saved={ckpt_dir}"
            )

        torch.cuda.empty_cache() if device.startswith("cuda") else None
