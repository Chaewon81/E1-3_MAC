"""Interactive mode for comparing a 3x3 pattern with two filters."""

from time import perf_counter

from .judge import decide
from .mac import mac
from .pattern_generator import generate_patterns
from .perf import benchmark_size, print_benchmark_table


def _read_matrix(name, input_fn=input, output_fn=print, size=3):
    while True:
        output_fn(f"{name}의 각 행을 숫자 {size}개로 입력하세요 (공백 또는 쉼표로 구분).")
        matrix = []

        try:
            for row_index in range(size):
                values = input_fn(f"{row_index + 1}행: ").replace(",", " ").split()
                if len(values) != size:
                    raise ValueError(f"한 행에는 숫자 {size}개가 필요합니다.")
                matrix.append([float(value) for value in values])
            return matrix
        except ValueError as error:
            output_fn(f"입력 오류: {error} 다시 입력해 주세요.\n")


def run_input_mode(input_fn=input, output_fn=print):
    """Read two filters and a pattern, then print their MAC scores and decision."""
    output_fn("입력 방식: 1. 직접 입력  2. 생성된 3×3 Cross/X 사용")
    while True:
        source = input_fn("선택: ").strip()
        if source in {"1", "2"}:
            break
        output_fn("1 또는 2를 입력해 주세요.")

    if source == "1":
        filter_a = _read_matrix("필터 A", input_fn, output_fn)
        filter_b = _read_matrix("필터 B", input_fn, output_fn)
        pattern = _read_matrix("비교할 패턴", input_fn, output_fn)
    else:
        filter_a, filter_b = generate_patterns(3)
        output_fn("생성된 Cross 패턴을 필터 A로, X 패턴을 필터 B로 사용합니다.")
        output_fn("비교할 패턴: 1. Cross  2. X")
        while True:
            pattern_choice = input_fn("선택: ").strip()
            if pattern_choice == "1":
                pattern, _ = generate_patterns(3)
                break
            if pattern_choice == "2":
                _, pattern = generate_patterns(3)
                break
            output_fn("1 또는 2를 입력해 주세요.")

    output_fn(f"필터 A 저장 확인: {filter_a}")
    output_fn(f"필터 B 저장 확인: {filter_b}")
    output_fn(f"비교 패턴 저장 확인: {pattern}")

    start = perf_counter()
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    elapsed_ms = (perf_counter() - start) * 1000

    output_fn(f"A 점수: {score_a}")
    output_fn(f"B 점수: {score_b}")
    output_fn(f"연산 시간: {elapsed_ms:.6f} ms (MAC 두 번)")
    result = decide(score_a, score_b)
    if result == "Cross":
        decision = "A"
    elif result == "X":
        decision = "B"
    else:
        decision = "판정 불가 (UNDECIDED)"
    output_fn(f"판정: {decision}")
    print_benchmark_table([benchmark_size(3)], output_fn)
