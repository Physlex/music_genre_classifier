"""
This module defines the entry point to the application, run as `mgc` or `python -m
music_genre_classifier`.
"""

from .logging import init_logging, setup_logging
from .settings import Settings

logger = setup_logging(__name__)


def main() -> None:
    settings = Settings.from_args()
    init_logging(settings)

    # Imported only once logging is initialized, so the output TensorFlow writes as it
    # loads is caught by the log instance
    from .app import App

    app = App(settings)

    app.init()
    while app.run():
        continue

    if app.error_encountered:
        logger.error(
            "Application encountered an unexpected error: %s", app.error_encountered
        )


if __name__ == "__main__":
    main()
