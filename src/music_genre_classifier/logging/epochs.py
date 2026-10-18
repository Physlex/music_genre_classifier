"""
This module provides the loggers for the training epochs of the models, written to their
epoch logs.
"""

import logging

from .system import SystemLogger


class EpochLogger:
    """
    Hands out the loggers that write to the epoch log of each model, <model>_epochs.log.
    """

    @classmethod
    def get_logger(cls, model: str) -> logging.Logger:
        """
        Returns the logger for the per-epoch training information of a model.
        """

        return logging.getLogger(f"{SystemLogger.ROOT}.epochs.{model}")
