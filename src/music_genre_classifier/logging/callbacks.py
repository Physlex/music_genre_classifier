"""
This module writes the training epochs of the keras models to their epoch logs. It is kept
out of the package exports, since importing keras loads TensorFlow, which must only happen
after the log instance is set up.
"""

from keras import callbacks

from .epochs import EpochLogger


class EpochCallback(callbacks.Callback):
    """
    Keras callback that writes the metrics of every training epoch of a keras model to its
    epoch log.
    """

    def __init__(self, model: str) -> None:
        super().__init__()

        self._model_name = model

        pass

    def on_train_begin(self, logs=None):
        EpochLogger.get_logger(self._model_name).info("Training run started")

    def on_epoch_end(self, epoch, logs=None):
        metrics = ", ".join(f"{key}={val:.4f}" for key, val in (logs or {}).items())
        EpochLogger.get_logger(self._model_name).info("Epoch %d: %s", epoch + 1, metrics)

    _model_name: str
