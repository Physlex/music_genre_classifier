"""
This module configures the per-run log instances. Every run of the application writes to
its own hashed and timestamped directory under the logs root, holding the system log plus
a results log and an epoch log for each model.
"""

import hashlib
import logging
import os
import platform
import sys
import time
from datetime import datetime
from importlib import metadata
from pathlib import Path

from ..settings import Settings
from .epochs import EpochLogger
from .results import ResultsLogger
from .system import SystemLogger

# Models with a results log and an epoch log in every log instance
MODELS = ["logistic_regression", "decision_tree", "neural_network"]

_FORMAT = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Third-party packages whose versions are recorded in the system log
_PACKAGES = [
    "keras",
    "keras-tuner",
    "librosa",
    "numpy",
    "scikit-learn",
    "scipy",
    "tensorflow-cpu",
]


def setup(settings: Settings) -> Path:
    """
    Creates a new log instance under the logs root and routes every application logger
    into it. Returns the instance directory.

    The directory is named `<timestamp>_<hash>`. The timestamp leads and is zero-padded,
    so a name-sorted listing (as in most IDEs) puts the oldest instance at the top and
    the newest at the bottom.
    """

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    digest = hashlib.sha256(
        f"{time.time_ns()}:{os.getpid()}:{settings}".encode()
    ).hexdigest()[:8]
    instance = settings.logs / f"{stamp}_{digest}"
    instance.mkdir(parents=True, exist_ok=True)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("%(message)s"))

    system = SystemLogger.get_logger()
    system.setLevel(logging.INFO)
    system.addHandler(_file_handler(instance / "system.log"))
    if settings.stream:
        system.addHandler(console)

    for model in MODELS:
        results = ResultsLogger.get_logger(model)
        results.propagate = False
        results.addHandler(_file_handler(instance / f"{model}.log"))
        if settings.stream:
            results.addHandler(console)

        # Epochs are too frequent for the console, so they only go to file
        epochs = EpochLogger.get_logger(model)
        epochs.propagate = False
        epochs.addHandler(_file_handler(instance / f"{model}_epochs.log"))

    _log_system_info(system, instance, settings)

    return instance


def _file_handler(path: Path) -> logging.FileHandler:
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(_FORMAT)
    return handler


def _log_system_info(logger: logging.Logger, instance: Path, settings: Settings) -> None:
    """
    Records the run environment at the top of the system log.
    """

    logger.info("Log instance: %s", instance)
    logger.info("Platform: %s", platform.platform())
    logger.info("Python: %s (%s)", platform.python_version(), sys.executable)
    logger.info("Host: %s", platform.node())
    logger.info("CPUs: %s", os.cpu_count())
    logger.info("Working directory: %s", Path.cwd())
    logger.info("Settings: %s", settings)

    for package in _PACKAGES:
        try:
            version = metadata.version(package)
        except metadata.PackageNotFoundError:
            version = "not installed"
        logger.info("Package %s: %s", package, version)
