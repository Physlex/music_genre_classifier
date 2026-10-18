"""
This module provides the settings, configuration, and other interpreter-time attributes to
run the application.
"""

from pathlib import Path

# Folder where static assets are held, next to this module. All datasets are taken from here.
ASSET_ROOT = Path(__file__).parent / "public"

# Forces the program to re-serialize the feature set. Set to 'False' if features have
# already been serialized.
EXTRACT_FEATURES = False

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
