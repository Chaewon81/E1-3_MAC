"""Label normalization and score comparison."""

EPSILON = 1e-9


def normalize_label(label):
    """Normalize common spellings for cross and X labels."""
    if not isinstance(label, str):
        raise ValueError(f"라벨은 문자열이어야 합니다: {label!r}")

    normalized = label.strip().lower()
    if normalized in {"+", "cross", "십자가", "plus"}:
        return "Cross"
    if normalized in {"x", "×", "엑스"}:
        return "X"
    raise ValueError(f"알 수 없는 라벨입니다: {label!r}")


def decide(score_cross, score_x, epsilon=EPSILON):
    """Return Cross, X, or UNDECIDED when scores are within epsilon."""
    if abs(score_cross - score_x) < epsilon or score_cross == score_x:
        return "UNDECIDED"
    return "Cross" if score_cross > score_x else "X"
