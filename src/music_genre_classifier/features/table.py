"""
This module implements feature extraction for audio waveforms
"""

import csv
import typing as ty
from copy import deepcopy
from pathlib import Path

import librosa as lr
import numpy as np
from scipy import stats

from ..logging import SystemLogger
from .generic import FeatureSet

logger = SystemLogger.get_logger(__name__)


class FeatureTable:
    """
    Represents a columnal organization of feature sets. Combined with a feature set of
    more than one feature, this forms a table of input features.
    """

    def __init__(self, featureset_list: list[FeatureSet]):
        """
        Private default constructor. Should only ever be called by the `extract` class.
        """

        self._featureset_list = deepcopy(featureset_list)

        pass

    @classmethod
    def extract(cls, assets_root_pathname, genres) -> ty.Union["FeatureTable", None]:
        """
        Performs feature extraction on the dataset and returns a feature table instance.
        """

        featureset_list: list[FeatureSet] = []
        for genre_class, genre in enumerate(genres):
            logger.info("Extracting features for %s", genre)
            for snippet_idx in range(100):
                if (snippet_idx % 10) == 0:
                    logger.info("%s", snippet_idx / 100)

                ## Create Path for Assets

                curr_pathname = assets_root_pathname
                if snippet_idx < 10:
                    curr_pathname = (
                        assets_root_pathname / f"{genre}/{genre}.0000{snippet_idx}.au"
                    )
                else:
                    curr_pathname = (
                        assets_root_pathname / f"{genre}/{genre}.000{snippet_idx}.au"
                    )

                audio_path = Path(curr_pathname)
                if not audio_path.exists():
                    logger.error("Failed to find path %s", curr_pathname)
                    return None

                ## Extract Stationary Features

                FRAME_SIZE = 1024
                HOP_LENGTH = 512

                # y = waveform, sr = samplerate (lr convention)
                y, sr = lr.load(audio_path)

                tempo_dynamic = lr.feature.tempo(y=y, sr=sr, aggregate=None, std_bpm=4)

                # Rhythm features from the beat-tracked onset times
                _, beats_dynamic = lr.beat.beat_track(
                    y=y, sr=sr, units="time", trim=False, bpm=tempo_dynamic
                )
                mean_beats = np.mean(beats_dynamic)
                var_beats = np.var(beats_dynamic)

                dyn_beat_histogram = beats_dynamic - mean_beats
                dyn_beats_strength = np.sum(dyn_beat_histogram)
                dyn_beats_peak = np.max(dyn_beat_histogram)

                brightness = lr.feature.spectral_centroid(
                    y=y, sr=sr, n_fft=FRAME_SIZE, hop_length=HOP_LENGTH
                )[0]
                mean_brightness = np.mean(brightness)
                std_brightness = np.sqrt(np.var(brightness))
                skew_brightness = stats.skew(brightness)
                kurt_brightness = stats.kurtosis(brightness)

                roll_off_freq = lr.feature.spectral_rolloff(
                    y=y, sr=sr, n_fft=FRAME_SIZE, hop_length=HOP_LENGTH
                )[0]
                mean_rolloff = np.mean(roll_off_freq)
                var_rolloff = np.var(roll_off_freq)

                spectral_flux = lr.onset.onset_strength(y=y, sr=sr)
                mean_flux = np.mean(spectral_flux)
                var_flux = np.var(spectral_flux)

                bandwidth = lr.feature.spectral_bandwidth(y=y, centroid=brightness)[0]
                mean_bandwidth = np.mean(bandwidth)
                var_bandwidth = np.var(bandwidth)

                zcr = lr.feature.zero_crossing_rate(
                    y=y, frame_length=FRAME_SIZE, hop_length=HOP_LENGTH
                )[0]
                mean_zcr = np.mean(zcr)
                var_zcr = np.var(zcr)

                loudness = lr.feature.rms(y=y, hop_length=HOP_LENGTH)[0]
                mean_loudness = np.mean(loudness)
                var_loudness = np.var(loudness)

                mfcc = lr.feature.mfcc(y=y, sr=sr, n_mfcc=6)
                mean_mfcc = np.mean(mfcc[1:6], axis=1)
                var_mfcc = np.var(mfcc[1:6], axis=1)

                featureset_list.append(
                    FeatureSet(
                        label=assets_root_pathname,
                        genre_class=genre_class,
                        # Rythmic features
                        mean_beats=mean_beats,
                        dyn_beats_strength=dyn_beats_strength,
                        dyn_beats_peak=dyn_beats_peak,
                        var_beats=var_beats,
                        # Static Features
                        mean_loudness=mean_loudness,
                        var_loudness=var_loudness,
                        # Spectral Features
                        mean_brightness=mean_brightness,
                        std_brightness=std_brightness,
                        skew_brightness=skew_brightness,
                        kurt_brightness=kurt_brightness,
                        mean_rolloff=mean_rolloff,
                        var_rolloff=var_rolloff,
                        mean_flux=mean_flux,
                        var_flux=var_flux,
                        mean_zcr=mean_zcr,
                        var_zcr=var_zcr,
                        mean_bandwidth=mean_bandwidth,
                        var_bandwidth=var_bandwidth,
                        # MFCC Stuff (Timbral Features)
                        mean_mfcc0=mean_mfcc[0],
                        var_mfcc0=var_mfcc[0],
                        mfcc1=mean_mfcc[1],
                        var_mfcc1=var_mfcc[1],
                        mfcc2=mean_mfcc[2],
                        var_mfcc2=var_mfcc[2],
                        mfcc3=mean_mfcc[3],
                        var_mfcc3=var_mfcc[3],
                        mfcc4=mean_mfcc[4],
                        var_mfcc4=var_mfcc[4],
                    )
                )

        return cls(featureset_list)

    def serialize(self, to, classes) -> bool:
        """
        Serialize the feature sets to a 'features' table.
        """

        logger.info("Serializing features...")

        if len(self._featureset_list) <= 0:
            logger.error("No features extracted from data source")
            return False

        root = Path(to)
        root.mkdir(parents=True, exist_ok=True)

        # Flush any prior serializations, if they exist
        for featureset in self._featureset_list:
            with open(
                root / f"{classes[featureset.genre_class]}.csv",
                mode="w",
                newline="",
            ) as file:
                pass

        # Write any features
        for featureset in self._featureset_list:
            with open(
                root / f"{classes[featureset.genre_class]}.csv",
                mode="a",
                newline="",
            ) as file:
                writer = csv.writer(file)
                writer.writerow(featureset.to_list())

        return True

    _featureset_list: list[FeatureSet]
