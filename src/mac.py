"""Multiply-Accumulate (MAC) operations implemented with Python loops."""

from .matrix import same_shape


def mac(pattern, filter_):
    """Multiply matching cells, add each product to a running score, and return it.

    The two loops visit every row and column once. A shape check runs first,
    then each same-position pair is multiplied and accumulated into ``score``.
    """
    if not same_shape(pattern, filter_):
        raise ValueError("두 배열은 비어 있지 않은 같은 크기의 직사각형이어야 합니다.")

    score = 0.0
    for row in range(len(pattern)):
        for col in range(len(pattern[0])):
            score += pattern[row][col] * filter_[row][col]

    return score


def mac_flat(pattern, filter_):
    """MAC two equal-length flattened arrays using one loop."""
    if not isinstance(pattern, list) or not isinstance(filter_, list):
        raise ValueError("1차원 배열 두 개가 필요합니다.")
    if not pattern or len(pattern) != len(filter_):
        raise ValueError("두 1차원 배열은 비어 있지 않고 길이가 같아야 합니다.")

    score = 0.0
    for index in range(len(pattern)):
        score += pattern[index] * filter_[index]
    return score
