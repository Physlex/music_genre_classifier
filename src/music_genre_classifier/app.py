"""
This module trains and evaluates the genre classifiers on the extracted feature table.
"""

import csv
import typing as ty

import keras_tuner as kt
import numpy as np
from keras import layers, metrics, models, optimizers, utils
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from . import settings
from .features import FeatureTable
from .logging import EpochLogger, ResultsLogger
from .logging.callbacks import EpochCallback
from .settings import Settings


def build_model(hp):
    model = models.Sequential()
    model.add(
        layers.Dense(hp.Choice("units", [8, 16, 24]), activation="sigmoid", use_bias=True)
    )
    model.add(layers.Dense(len(settings.GENRES), activation="sigmoid", use_bias=True))

    model.compile(
        loss=metrics.binary_crossentropy,
        optimizer=optimizers.SGD(0.4),  # HP to consider
        metrics=["accuracy"],
    )

    return model


class App:
    """
    Class wrapper for the application. Seperates initialization, state, and other logical
    features from the entry point.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initializes the application structure from the command line settings.
        """

        self.error = False
        self.error_encountered = None
        self.settings = settings

        pass

    @classmethod
    def from_settings(cls) -> "App":
        """
        Creates the application from the settings given on the command line.
        """

        return cls(Settings.from_args())

    def run(self) -> bool:
        """
        Executes an instance of the application main loop.

        ## Returns

        - True if the application can continue running without problem.

        - False if an error has been encountered or the application has been naturally
          terminated through expected means (IE: User Input).
        """

        # HEADER GUARD

        if self.error:
            return False

        features = self._split_features()
        if features is None:
            return False
        ((X_train, Y_train), (X_val, Y_val), (X_test, Y_test)) = features

        # Logistic Regression

        results = ResultsLogger.get_logger("logistic_regression")
        epochs = EpochLogger.get_logger("logistic_regression")
        results.info("##### Logistic Regression #####")

        hp = [0.1, 0.3, 1.0]
        best_hp = 0
        best_penalty = None
        best_acc = 0
        model = None
        for C in hp:
            for penalty in [None, "l2"]:
                val_model = LogisticRegression(C=C, penalty=penalty)
                val_model.fit(X_train, Y_train)
                prediction = val_model.predict(X_val)
                val_accuracy = np.mean(prediction == Y_val)
                epochs.info(
                    "C=%s, penalty=%s: val_accuracy=%.4f", C, penalty, val_accuracy
                )
                if val_accuracy > best_acc:
                    best_hp = C
                    best_acc = val_accuracy
                    best_penalty = penalty
                    model = val_model

        if model is None:
            self.error_encountered = (
                "Model validation step has error. Model never non None"
            )
            self.error = True
            return False

        results.info(f"Best C: {best_hp}" if best_penalty else "No C Used")
        results.info("Ridge regression type used: %s", best_penalty)
        results.info("Best Val Acc: %s", best_acc)

        test_predictions = model.predict(X_test)
        ResultsLogger.log_test_summary("logistic_regression", Y_test, test_predictions)

        # Decision Tree

        results = ResultsLogger.get_logger("decision_tree")
        epochs = EpochLogger.get_logger("decision_tree")
        results.info("##### Decision Tree #####")

        hp = [0.1, 0.3, 1.0]
        best_mssp = 0
        best_msl = 0
        best_acc = 0
        model = None
        for mssp_hp in range(2, 41):
            for msl_hp in range(2, 24):
                val_model = DecisionTreeClassifier(
                    min_samples_split=mssp_hp,
                    min_samples_leaf=msl_hp,
                    random_state=self.settings.seed,
                )
                val_model.fit(X_train, Y_train)
                prediction = val_model.predict(X_val)
                val_accuracy = np.mean(prediction == Y_val)
                epochs.info(
                    "min_samples_split=%d, min_samples_leaf=%d: val_accuracy=%.4f",
                    mssp_hp,
                    msl_hp,
                    val_accuracy,
                )
                if val_accuracy > best_acc:
                    best_mssp = mssp_hp
                    best_msl = msl_hp
                    best_acc = val_accuracy
                    model = val_model

        if model is None:
            self.error_encountered = (
                "Model validation step has error. Model never non None"
            )
            self.error = True
            return False

        results.info("Best min sample split: %s", best_mssp)
        results.info("Best min samples leaf: %s", best_msl)
        results.info("Best Val Acc: %s", best_acc)

        test_predictions = model.predict(X_test)
        ResultsLogger.log_test_summary("decision_tree", Y_test, test_predictions)

        ### Neural Network

        results = ResultsLogger.get_logger("neural_network")
        results.info("##### Neural Network #####")

        Y_train = utils.to_categorical(Y_train, len(settings.GENRES))
        Y_val = utils.to_categorical(Y_val, len(settings.GENRES))
        Y_test = utils.to_categorical(Y_test, len(settings.GENRES))

        if self.settings.seed is not None:
            utils.set_random_seed(self.settings.seed)

        tuner = kt.RandomSearch(
            build_model,
            objective="val_accuracy",
            max_trials=5,
            seed=self.settings.seed,
        )

        tuner.search(
            X_train,
            Y_train,
            epochs=500,
            validation_data=(X_val, Y_val),
            callbacks=[EpochCallback("neural_network")],
            verbose=1 if self.settings.stream else 0,
        )
        results.info(
            "Best hyperparameters: %s", tuner.get_best_hyperparameters()[0].values
        )
        model = tuner.get_best_models()[0]
        model.summary(print_fn=results.info)

        Y_test = np.argmax(Y_test, axis=1)
        test_predictions = np.argmax(
            model.predict(X_test, verbose=1 if self.settings.stream else 0), axis=1
        )
        ResultsLogger.log_test_summary("neural_network", Y_test, test_predictions)

        return False

    def init(self):
        """
        Prep the application as an initial update step to ensure efficient running.
        """

        if self.settings.extract:
            # Convert the audio clips into a table of features
            table = FeatureTable.extract(self.settings.clips, settings.GENRES)
            if table is None:
                self.error_encountered = (
                    "Failed to extract features into table. See log for details."
                )
                self.error = True
                return

            # Serialize the features to a set of csv's (speeds up later training runs)
            table.serialize(to=self.settings.features, classes=settings.GENRES)

    def _split_features(self) -> ty.Iterable | None:
        """
        Splits features into testing, validation, and training sets. Feature selection is
        randomized and augmented as necessary during this process.
        """

        if not self.settings.features.is_dir():
            self.error_encountered = (
                f"Feature directory {self.settings.features} not found. "
                "Run with --extract"
            )
            self.error = True
            return None

        # Convert all features (in seperate files) into one big dataset
        dataset = []
        for genre in settings.GENRES:
            with open(self.settings.features / f"{genre}.csv") as file:
                reader = csv.reader(file)
                for row in reader:
                    dataset.append(
                        [int(row[0]), *(np.float64(value) for value in row[1:])]
                    )

        if len(dataset) <= 0:
            self.error_encountered = "Dataset is zero-width. Run with --extract"
            self.error = True
            return None

        # Augment and split the features

        labels = [row[0] for row in dataset]
        features = [row[1:] for row in dataset]

        random_state = np.random.RandomState(self.settings.seed)
        scalar = StandardScaler()

        X_train, X_temp, Y_train, Y_temp = train_test_split(
            features, labels, test_size=0.4, random_state=random_state
        )

        X_val, X_test, Y_val, Y_test = train_test_split(
            X_temp, Y_temp, test_size=0.5, random_state=random_state
        )

        # Normalize the input features to have 0 mean and unit variance

        X_train = scalar.fit_transform(X_train)
        X_val = scalar.transform(X_val)
        X_test = scalar.transform(X_test)

        return ((X_train, Y_train), (X_val, Y_val), (X_test, Y_test))

    error_encountered: str | None
    error: bool
    settings: Settings
