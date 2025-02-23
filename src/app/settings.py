"""
This module provides the settings, configuration, and other interpreter-time attributes to
run the application.
"""

# Root of the application structure, where all the src code is actually held.
ROOT = "src"

# Folder where static assets are held. All datasets are taken from here.
ASSET_ROOT = "public"

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
