"""
This module defines the entry point to the application, run as `mgc` or `python -m
music_genre_classifier`.
"""

from .app import App
from .logging import SystemLogger
from .logging import setup as setup_logging

logger = SystemLogger.get_logger(__name__)


def main() -> None:
    app = App.from_settings()
    setup_logging(app.settings)

    app.init()
    while app.run():
        continue

    if app.error_encountered:
        logger.error(
            "Application encountered an unexpected error: %s", app.error_encountered
        )


if __name__ == "__main__":
    main()
