"""Generate simple Cross and X patterns of any positive square size."""


def generate_patterns(size):
    """Return (cross, x_pattern), each represented as an N by N list."""
    if not isinstance(size, int) or isinstance(size, bool) or size < 1:
        raise ValueError("패턴 크기 N은 1 이상의 정수여야 합니다.")

    middle = size // 2
    cross = []
    x_pattern = []
    for row in range(size):
        cross_row = []
        x_row = []
        for col in range(size):
            cross_row.append(1.0 if row == middle or col == middle else 0.0)
            x_row.append(1.0 if row == col or row + col == size - 1 else 0.0)
        cross.append(cross_row)
        x_pattern.append(x_row)
    return cross, x_pattern


def run_generator_mode(input_fn=input, output_fn=print):
    """Ask for a size and display the generated patterns."""
    while True:
        try:
            size = int(input_fn("패턴 크기 N을 입력하세요: ").strip())
            cross, x_pattern = generate_patterns(size)
            break
        except ValueError as error:
            output_fn(f"입력 오류: {error}")

    output_fn("Cross 패턴:")
    for row in cross:
        output_fn(" ".join(f"{value:g}" for value in row))
    output_fn("X 패턴:")
    for row in x_pattern:
        output_fn(" ".join(f"{value:g}" for value in row))
    return cross, x_pattern
