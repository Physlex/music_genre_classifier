"""
This module configures the per-run log instances. Every run of the application writes to
its own hashed and timestamped directory under the logs root, holding the system log plus
a results log and an epoch log for each model.

Logging is configured in two phases. `setup_logging` needs no settings, so modules call it
at import to get their logger. `init_logging` runs once the settings are parsed, creating
the log instance and routing every logger into it.
"""

import hashlib
import logging
import os
import platform
import signal
import sys
import time
from datetime import datetime
from importlib import metadata
from pathlib import Path

from ..settings import Settings
from .epochs import EpochLogger
from .results import ResultsLogger
from .system import SystemLogger


def setup_logging(name: str) -> logging.Logger:
    """
    Applies the settings-independent logging configuration and returns the system logger
    for a module, given its `__name__`. Safe to call from every module at import.
    """

    SystemLogger.get_logger().setLevel(logging.INFO)
    logging.captureWarnings(True)

    return SystemLogger.get_logger(name)


def init_logging(settings: Settings) -> Path:
    """
    Creates a new log instance under the logs root and routes every application logger
    into it. Returns the instance directory.

    The directory is named `<timestamp>_<hash>`. The timestamp leads and is zero-padded,
    so a name-sorted listing (as in most IDEs) puts the oldest instance at the top and
    the newest at the bottom.

    When streaming is disabled, anything written to stderr below python (such as by the
    TensorFlow runtime) is also sent to the system log, so this must run before
    TensorFlow is imported.
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
    system.addHandler(_file_handler(instance / "system.log"))
    if settings.stream:
        system.addHandler(console)

    # Python warnings (such as those of sklearn) are captured into this logger
    warnings = logging.getLogger("py.warnings")
    warnings.propagate = False
    warnings.addHandler(_file_handler(instance / "system.log"))
    if settings.stream:
        warnings.addHandler(console)

    # Models with a results log and an epoch log in every log instance
    for model in ["logistic_regression", "decision_tree", "neural_network"]:
        results = ResultsLogger.get_logger(model)
        results.propagate = False
        results.addHandler(_file_handler(instance / f"{model}.log"))
        if settings.stream:
            results.addHandler(console)

        # Epochs are too frequent for the console, so they only go to file
        epochs = EpochLogger.get_logger(model)
        epochs.propagate = False
        epochs.addHandler(_file_handler(instance / f"{model}_epochs.log"))

    if not settings.stream:
        _redirect_stderr(instance / "system.log")

    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, _log_exit_signal)

    _log_system_info(system, instance, settings)

    return instance


def _log_exit_signal(signum: int, _frame) -> None:
    """
    Logs a terminating signal, then exits with the code shells report for it (128 plus
    the signal number). Exiting through `SystemExit` unwinds without a traceback.
    """

    SystemLogger.get_logger().info(
        "Application exited by signal %s", signal.Signals(signum).name
    )
    sys.exit(128 + signum)


def _file_handler(path: Path) -> logging.FileHandler:
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    return handler


def _redirect_stderr(path: Path) -> None:
    """
    Points the stderr file descriptor at a log file, catching output written below python.
    Python's own `sys.stderr` keeps the terminal, so tracebacks still show.
    """

    sys.stderr.flush()
    terminal = os.dup(2)

    log = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    os.dup2(log, 2)
    os.close(log)

    sys.stderr = os.fdopen(terminal, "w", buffering=1)


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

    # Third-party packages whose versions are recorded
    for package in [
        "keras",
        "keras-tuner",
        "librosa",
        "numpy",
        "scikit-learn",
        "scipy",
        "tensorflow-cpu",
    ]:
        try:
            version = metadata.version(package)
        except metadata.PackageNotFoundError:
            version = "not installed"
        logger.info("Package %s: %s", package, version)
