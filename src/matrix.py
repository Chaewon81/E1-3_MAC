"""Helpers for validating small numeric matrices."""


def is_valid_matrix(matrix):
    """Return True when matrix is a non-empty rectangular list of lists."""
    if not isinstance(matrix, list) or not matrix:
        return False

    if not all(isinstance(row, list) for row in matrix):
        return False

    column_count = len(matrix[0])
    if column_count == 0:
        return False

    if not all(len(row) == column_count for row in matrix):
        return False

    return all(
        isinstance(value, (int, float)) and not isinstance(value, bool)
        for row in matrix
        for value in row
    )


def same_shape(a, b):
    """Return True when both valid matrices have the same row/column counts."""
    return (
        is_valid_matrix(a)
        and is_valid_matrix(b)
        and len(a) == len(b)
        and len(a[0]) == len(b[0])
    )


def flatten_matrix(matrix):
    """Convert a valid matrix to a row-major one-dimensional list."""
    if not is_valid_matrix(matrix):
        raise ValueError("올바른 2차원 숫자 배열이 필요합니다.")

    flat = []
    for row in matrix:
        for value in row:
            flat.append(value)
    return flat
