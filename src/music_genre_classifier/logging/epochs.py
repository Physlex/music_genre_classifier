"""
This module writes the training epochs of the models to their epoch logs.
"""

import logging

from keras import callbacks

from .system import SystemLogger


class EpochLogger(callbacks.Callback):
    """
    Hands out the loggers that write to the epoch log of each model, <model>_epochs.log.

    An instance is also a keras callback that writes the metrics of every training epoch
    of a keras model to its epoch log.
    """

    def __init__(self, model: str) -> None:
        super().__init__()

        self._model_name = model

        pass

    @classmethod
    def get_logger(cls, model: str) -> logging.Logger:
        """
        Returns the logger for the per-epoch training information of a model.
        """

        return logging.getLogger(f"{SystemLogger.ROOT}.epochs.{model}")

    def on_train_begin(self, logs=None):
        self.get_logger(self._model_name).info("Training run started")

    def on_epoch_end(self, epoch, logs=None):
        metrics = ", ".join(f"{key}={val:.4f}" for key, val in (logs or {}).items())
        self.get_logger(self._model_name).info("Epoch %d: %s", epoch + 1, metrics)

    _model_name: str
