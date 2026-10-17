"""
Generic Feature module. Allows declaring custom FeatureSet types with a simple wrapper.
"""

import typing as ty


class FeatureSet(object):
    """
    Generic FeatureSetet class. Represents a row in a table of FeatureSet.
    """

    def __init__(self, label: str, *args, **kwargs):
        """
        Default constructor. Due to the nature of FeatureSet, it is unlikely we know what
        kind of key-value pairings would best represent a feature prior to the specific
        situation it is in.

        Hence, we allow literally anything to be an attribute, assuming it makes sense.
        """

        self.label = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.label is not None:
            raise NameError(
                "attrib 'label' is a protected attribute for a Feature class"
            )
        else:
            self.label = label

        pass

    def to_list(self) -> ty.List[ty.Any]:
        """
        Converts the labeled feature set into a simple-row representation. Useful for
        working with training data.
        """

        features = []
        for key, val in self.__dict__.items():
            if key != "label":
                features.append(val)

        return features

    def pprint(self):
        """
        Simply pretty prints the feature set.
        """

        print(f"Feature {self.label}: ")
        for key, val in self.__dict__.items():
            print(f"- {key}: {val}")

    def __repr__(self) -> str:
        repr_str = ""
        for key, val in self.__dict__.items():
            repr_str += f"- {key}: {val}\n"

        return repr_str
