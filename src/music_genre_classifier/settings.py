"""
This module provides the settings, configuration, and other interpreter-time attributes to
run the application.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    """
    Command line settings for a run of the application.
    """

    # Directory of audio clips, with one subdirectory per genre
    clips: Path

    # Directory the per-genre feature tables are extracted to and read from
    features: Path

    # Seed for the data split and model training. None leaves runs unseeded
    seed: int | None

    # Extracts the audio clips into feature tables before training, replacing any tables
    # already serialized
    extract: bool

    @staticmethod
    def from_args() -> "Settings":
        """
        Parses the command line arguments into the settings for a run of the application.
        """

        parser = argparse.ArgumentParser(
            prog="mgc",
            description="Classify music clips into genres from audio features.",
        )
        parser.add_argument(
            "--clips",
            type=Path,
            default=Path("assets/clips"),
            help="directory of audio clips, by genre (default: %(default)s)",
        )
        parser.add_argument(
            "--features",
            type=Path,
            default=Path("build/features"),
            help="directory of the extracted feature tables (default: %(default)s)",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="seed for the data split and model training (default: unseeded)",
        )
        parser.add_argument(
            "--extract",
            action="store_true",
            help="extract the feature tables from the audio clips before training",
        )
        args = parser.parse_args()

        return Settings(
            clips=args.clips, features=args.features, seed=args.seed, extract=args.extract
        )


# A list of genres that are known to the ML model to extract features from.
GENRES = [
    "blues",
    "classical",
    "country",
    "disco",
    "hiphop",
    "jazz",
    "metal",
    "pop",
    "reggae",
    "rock",
]
