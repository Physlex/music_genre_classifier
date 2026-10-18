"""
This module defines the entry point to the application, run as `mgc` or `python -m
music_genre_classifier`.
"""

from .app import App


def main() -> None:
    app = App()

    app.init()
    while app.run():
        continue

    if app.error_encountered:
        print(f"Application encountered an unexpected error: {app.error_encountered}")


if __name__ == "__main__":
    main()
