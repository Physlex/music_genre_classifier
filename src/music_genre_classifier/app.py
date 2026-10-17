"""
This module defines the entry point to the CMPUT 466 mini-project.
"""

import csv
import typing as ty
from pathlib import Path

import keras_tuner as kt
import numpy as np
from keras import layers, metrics, models, optimizers, utils
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from . import settings
from .features import FeatureTable


# Little bit of a rush job, but in a tad bit of a hurry anyway.
def build_model(hp):
    model = models.Sequential()
    model.add(
        layers.Dense(
            hp.Choice("units", [8, 16, 24]), activation="sigmoid", use_bias=True
        )
    )
    model.add(layers.Dense(len(settings.GENRES), activation="sigmoid", use_bias=True))

    model.compile(
        loss=metrics.binary_crossentropy,
        optimizer=optimizers.SGD(0.4),  # HP to consider
        metrics=["accuracy"],
    )

    return model


class App(object):
    """
    Class wrapper for the application. Seperates initialization, state, and other logical
    features from the entry point.
    """

    def __init__(self) -> None:
        """
        Initializes the application structure, allowing imports of public assets via name.
        """

        self.error = False
        self.error_encountered = None
        self.context = {}

        pass

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

        print("\n##### Logistic Regression #####\n")

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

        print(f"Best C: {best_hp}" if best_penalty else "No C Used")
        print("Ridge regression type used: ", best_penalty)
        print("Best Val Acc: ", best_acc)

        test_predictions = model.predict(X_test)
        print("Test Summary: ")
        print(f"Accuracy: {accuracy_score(Y_test, test_predictions)}")
        print(f"Classficiation: \n{classification_report(Y_test, test_predictions)}")
        print(f"Confusion: \n{confusion_matrix(Y_test, test_predictions)}")

        # Decision Tree

        print("\n##### Decision Tree #####\n")

        hp = [0.1, 0.3, 1.0]
        best_mssp = 0
        best_msl = 0
        best_acc = 0
        model = None
        for mssp_hp in range(2, 41):
            for msl_hp in range(2, 24):
                val_model = DecisionTreeClassifier(
                    min_samples_split=mssp_hp, min_samples_leaf=msl_hp
                )
                val_model.fit(X_train, Y_train)
                prediction = val_model.predict(X_val)
                val_accuracy = np.mean(prediction == Y_val)
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

        print(f"Best min sample split: {best_mssp}")
        print("Best min samples leaf: ", best_msl)
        print("Best Val Acc: ", best_acc)

        test_predictions = model.predict(X_test)
        print("Test Summary: ")
        print(f"Accuracy: {accuracy_score(Y_test, test_predictions)}")
        print(f"Classficiation: \n{classification_report(Y_test, test_predictions)}")
        print(f"Confusion: \n{confusion_matrix(Y_test, test_predictions)}")

        ### Neural Network

        print("\n##### Neural Network #####\n")

        Y_train = utils.to_categorical(Y_train, len(settings.GENRES))
        Y_val = utils.to_categorical(Y_val, len(settings.GENRES))
        Y_test = utils.to_categorical(Y_test, len(settings.GENRES))

        tuner = kt.RandomSearch(
            build_model,
            objective="val_accuracy",
            max_trials=5,
        )

        tuner.search(X_train, Y_train, epochs=500, validation_data=(X_val, Y_val))
        model = tuner.get_best_models()[0]
        model.summary()

        Y_test = np.argmax(Y_test, axis=1)
        test_predictions = np.argmax(model.predict(X_test), axis=1)
        print("Test Summary: ")
        print(f"Accuracy: {accuracy_score(Y_test, test_predictions)}")
        print(f"Classficiation: \n{classification_report(Y_test, test_predictions)}")
        print(f"Confusion: \n{confusion_matrix(Y_test, test_predictions)}")

        return False

    def init(self):
        """
        Prep the application as an initial update step to ensure efficient running.
        """

        asset_root = Path.cwd() / Path(settings.ROOT) / Path(settings.ASSET_ROOT)
        self.context["asset-root"] = asset_root

        if settings.EXTRACT_FEATURES:
            # Convert the audio files in the extract asset root into a table of features
            table = FeatureTable.extract(asset_root, settings.GENRES)
            if table is None:
                self.error = (
                    "Failed to extract features into table. See log for details."
                )
                self.error_encountered = True

            # Serialize the features to a set of csv's (to increase speed on second-training attempts)
            table.serialize(to=asset_root, classes=settings.GENRES)

    def _split_features(self) -> ty.Optional[ty.Union[ty.Union[ty.Iterable]]]:
        """
        Splits features into testing, validation, and training sets. Feature selection is
        randomized and augmented as necessary during this process.
        """

        asset_root = self.context["asset-root"]
        if not asset_root:
            self.error_encountered = "Failed to initialize asset root"
            self.error = True
            return None

        # Convert all features (in seperate files) into one big dataset
        dataset = []
        for genre in settings.GENRES:
            with open(asset_root / "features" / f"{genre}.csv", "r") as file:
                reader = csv.reader(file)
                table = [[np.float64(value) for value in row] for row in reader]
                for row in table:
                    row[0] = int(row[0])
                    dataset.append(row)

        if len(dataset) <= 0:
            self.error_encountered = (
                "Dataset is zero-width. Set EXTRACT_FEATURES in settings.py to True"
            )
            self.error = True
            return None

        # Augment and split the features

        labels = [row[0] for row in dataset]
        features = [row[1:] for row in dataset]

        random_state = np.random.RandomState()
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

    error_encountered: ty.Union[str, None]
    error: bool
    context: ty.Dict[str, ty.Any]
