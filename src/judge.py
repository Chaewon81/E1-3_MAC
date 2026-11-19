"""Label normalization and score comparison."""

import math
import os

DEFAULT_EPSILON = 1e-9


def _configured_epsilon():
    """Read an optional tolerance from NPU_EPSILON, defaulting to 1e-9."""
    raw_value = os.environ.get("NPU_EPSILON")
    try:
        epsilon = DEFAULT_EPSILON if raw_value is None else float(raw_value)
    except ValueError as error:
        raise ValueError("NPU_EPSILON은 0 이상의 숫자여야 합니다.") from error
    if not math.isfinite(epsilon) or epsilon < 0:
        raise ValueError("NPU_EPSILON은 0 이상의 유한한 숫자여야 합니다.")
    return epsilon


EPSILON = _configured_epsilon()


def normalize_label(label):
    """Normalize labels once so JSON keys and expected answers compare consistently."""
    if not isinstance(label, str):
        raise ValueError(f"라벨은 문자열이어야 합니다: {label!r}")

    normalized = label.strip().lower()
    if normalized in {"+", "cross", "십자가", "plus"}:
        return "Cross"
    if normalized in {"x", "×", "엑스"}:
        return "X"
    raise ValueError(f"알 수 없는 라벨입니다: {label!r}")


def decide(score_cross, score_x, epsilon=None):
    """Return Cross, X, or UNDECIDED when scores are within epsilon."""
    if epsilon is None:
        epsilon = EPSILON
    if not math.isfinite(epsilon) or epsilon < 0:
        raise ValueError("epsilon은 0 이상의 유한한 숫자여야 합니다.")
    if abs(score_cross - score_x) < epsilon or score_cross == score_x:
        return "UNDECIDED"
    return "Cross" if score_cross > score_x else "X"
