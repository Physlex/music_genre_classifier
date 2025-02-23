"""
Just a bunch of math utilities for missing implementations of the paper using numpy.
"""

import numpy as np


def gaussian_kernel(size, sigma):
    """
    Creates a gaussian kernel. Apparently required as a means of reducing noise in the
    audio signal.
    """

    start = -(size - 1) / 2
    stop = (size - 1) / 2
    x = np.linspace(start, stop, size)

    kernel = np.exp(-0.5 * np.square(x) / np.square(sigma))
    kernel /= np.sum(kernel)

    return kernel
