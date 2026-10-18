"""
This module provides the logger for anything that is not a model result or epoch, written
to system.log.
"""

import logging


class SystemLogger:
    """
    Hands out the loggers that write to the system log of the current log instance.
    """

    # Name of the logger every system logger is nested under
    ROOT = "music_genre_classifier"

    @classmethod
    def get_logger(cls, name: str = ROOT) -> logging.Logger:
        """
        Returns the system logger for a module, given its `__name__`. Names outside the
        package (such as `__main__`) are nested under it, so they still reach the system
        log.
        """

        if name != cls.ROOT and not name.startswith(f"{cls.ROOT}."):
            name = f"{cls.ROOT}.{name}"

        return logging.getLogger(name)
