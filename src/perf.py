"""Timing helpers for the MAC function only."""

from time import perf_counter

from .mac import mac
from .mac import mac_flat
from .matrix import flatten_matrix
from .pattern_generator import generate_patterns
from .judge import EPSILON


def benchmark_size(size, repeats=10, pattern=None, filter_=None):
    """Return average MAC call time and operation count for a square matrix."""
    if repeats < 10:
        raise ValueError("성능 측정은 크기별 최소 10회 반복해야 합니다.")

    if pattern is None:
        pattern, _ = generate_patterns(size)
    if filter_ is None:
        _, filter_ = generate_patterns(size)

    elapsed = 0.0
    for _ in range(repeats):
        start = perf_counter()
        mac(pattern, filter_)
        elapsed += perf_counter() - start

    return {
        "size": size,
        "repeats": repeats,
        "average_ms": elapsed * 1000 / repeats,
        "operations": size * size,
    }


def compare_mac_implementations(size, repeats=10):
    """Compare 2D and flattened one-loop MAC on identical generated data."""
    if repeats < 10:
        raise ValueError("성능 측정은 크기별 최소 10회 반복해야 합니다.")

    pattern, filter_ = generate_patterns(size)
    flat_pattern = flatten_matrix(pattern)
    flat_filter = flatten_matrix(filter_)

    score_2d = mac(pattern, filter_)
    score_1d = mac_flat(flat_pattern, flat_filter)
    if abs(score_2d - score_1d) > EPSILON:
        raise ArithmeticError("2차원과 1차원 MAC 결과가 일치하지 않습니다.")

    elapsed_2d = 0.0
    elapsed_1d = 0.0
    for _ in range(repeats):
        start = perf_counter()
        mac(pattern, filter_)
        elapsed_2d += perf_counter() - start

        start = perf_counter()
        mac_flat(flat_pattern, flat_filter)
        elapsed_1d += perf_counter() - start

    average_2d = elapsed_2d * 1000 / repeats
    average_1d = elapsed_1d * 1000 / repeats
    return {
        "size": size,
        "repeats": repeats,
        "average_2d_ms": average_2d,
        "average_1d_ms": average_1d,
        "operations": size * size,
        "speedup": average_2d / average_1d if average_1d else None,
    }


def run_optimization_comparison(output_fn=print):
    """Print a before/after timing comparison at all project sizes."""
    rows = [compare_mac_implementations(size) for size in (3, 5, 13, 25)]
    output_fn("\n2차원 / 1차원 MAC 최적화 비교 (동일 패턴, 필터, 10회 반복)")
    output_fn(
        f"{'크기':<10}{'연산 횟수':>12}{'2차원(ms)':>16}"
        f"{'1차원(ms)':>16}{'속도비(2D/1D)':>20}"
    )
    for row in rows:
        speedup = f"{row['speedup']:.3f}x" if row["speedup"] is not None else "N/A"
        output_fn(
            f"{row['size']}×{row['size']:<8}{row['operations']:>12}"
            f"{row['average_2d_ms']:>16.6f}{row['average_1d_ms']:>16.6f}"
            f"{speedup:>20}"
        )
    return rows


def print_benchmark_table(rows, output_fn=print):
    """Print size, average time, and N-squared MAC count as a table."""
    output_fn("\n성능 분석 (MAC 함수 호출 시간만 측정)")
    output_fn(f"{'크기(N×N)':<14}{'평균 시간(ms)':>18}{'연산 횟수(N²)':>18}")
    for row in rows:
        output_fn(
            f"{row['size']}×{row['size']:<12}"
            f"{row['average_ms']:>18.6f}{row['operations']:>18}"
        )
