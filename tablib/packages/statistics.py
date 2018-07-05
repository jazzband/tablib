from __future__ import division


def median(data):
    """
    Return the median (middle value) of numeric data, using the common
    "mean of middle two" method. If data is empty, ValueError is raised.

    Mimics the behaviour of Python3's statistics.median

    >>> median([1, 3, 5])
    3
    >>> median([1, 3, 5, 7])
    4.0

    """
    data = sorted(data)
    n = len(data)
    if not n:
        raise ValueError("No median for empty data")
    i = n // 2
    if n % 2:
        return data[i]
    return (data[i - 1] + data[i]) / 2
