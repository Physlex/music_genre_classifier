"""
A bunch of utility functions that don't yet have a home.
"""

import typing as ty

import numpy as np


def split(array_like: ty.Iterable, fr0=1, fr1=0, fr2=0):
    """
    Allows splitting an audio feature table by a fractional set of lists of that
    feature.

    ## Example

    Given an 100 input feature sets of (x, y, z), the following is true:

    >>> table.split(fr0=1, fr1=1, fr2=1) # the resulting list is split as: 33, 33, 34
    >>> table.split(fr0=3, fr1=2, fr2=1) # the resulting list is split as: 50, 33, 17
    >>> table.split(fr0=98, fr1=1, fr2=1) # the resulting list is split as: 98, 1, 1

    """

    T = fr0 + fr1 + fr2
    (N,) = np.shape(array_like)
    if N < 3:
        return array_like, None, None

    fr0 = int((fr0 / T) * N)
    fr1 = int((fr1 / T) * N + fr0)
    fr2 = N - fr1

    split1 = array_like[:fr0]
    split2 = array_like[fr0:fr1]
    split3 = array_like[fr1:]

    return split1, split2, split3
