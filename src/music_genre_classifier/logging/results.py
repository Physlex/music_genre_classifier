"""
This module writes the evaluation of the trained models to their results logs.
"""

import logging

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from .system import SystemLogger


class ResultsLogger:
    """
    Hands out the loggers that write to the results log of each model, <model>.log.
    """

    @classmethod
    def get_logger(cls, model: str) -> logging.Logger:
        """
        Returns the logger for the evaluation results of a model.
        """

        return logging.getLogger(f"{SystemLogger.ROOT}.results.{model}")

    @classmethod
    def log_test_summary(cls, model: str, Y_test, test_predictions) -> None:
        """
        Writes the test set evaluation of a model to its results log.
        """

        results = cls.get_logger(model)
        results.info("Test Summary: ")
        results.info("Accuracy: %s", accuracy_score(Y_test, test_predictions))
        results.info(
            "Classficiation: \n%s", classification_report(Y_test, test_predictions)
        )
        results.info("Confusion: \n%s", confusion_matrix(Y_test, test_predictions))
