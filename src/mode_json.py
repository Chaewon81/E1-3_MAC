"""Analyze the pattern cases stored in data.json."""

import json
from pathlib import Path
import re

from .judge import decide, normalize_label
from .mac import mac
from .matrix import is_valid_matrix
from .perf import benchmark_size, print_benchmark_table


def analyze_json_file(path="data.json", output_fn=print):
    """Load cases, classify each pattern, and print a result summary."""
    try:
        with Path(path).open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        output_fn(f"JSON 파일을 읽지 못했습니다: {error}")
        return None

    if not isinstance(data, dict):
        output_fn("JSON 최상위 값은 객체여야 합니다.")
        return None
    filters = data.get("filters", {})
    patterns = data.get("patterns", {})
    if not isinstance(filters, dict) or not isinstance(patterns, dict):
        output_fn("JSON 스키마 오류: filters와 patterns는 객체여야 합니다.")
        return None
    results = []

    for case_name, case in patterns.items():
        expected = case.get("expected") if isinstance(case, dict) else None
        try:
            pattern = case["input"]
            if not is_valid_matrix(pattern):
                raise ValueError("입력 패턴의 배열 모양이나 값이 올바르지 않습니다.")

            key_match = re.fullmatch(r"size_(\d+)_\d+", case_name)
            if not key_match:
                raise ValueError("케이스 키는 size_{N}_{idx} 형식이어야 합니다.")
            size = int(key_match.group(1))
            if len(pattern) != size or len(pattern[0]) != size:
                raise ValueError(f"키는 {size}×{size}를 가리키지만 패턴 크기가 다릅니다.")
            filter_set = filters[f"size_{size}"]
            if not isinstance(filter_set, dict):
                raise ValueError(f"size_{size} 필터 항목은 객체여야 합니다.")
            normalized_filters = {}
            for filter_key, filter_matrix in filter_set.items():
                normalized_filters[normalize_label(filter_key)] = filter_matrix
            if "Cross" not in normalized_filters or "X" not in normalized_filters:
                raise ValueError("필수 Cross/X 필터 키가 없습니다.")
            cross_score = mac(pattern, normalized_filters["Cross"])
            x_score = mac(pattern, normalized_filters["X"])
            predicted = decide(cross_score, x_score)
            expected_label = normalize_label(expected)
            passed = predicted == expected_label

            result = {
                "case": case_name,
                "expected": expected_label,
                "predicted": predicted,
                "cross_score": cross_score,
                "x_score": x_score,
                "passed": passed,
                "reason": (
                    None
                    if passed
                    else (
                        "두 점수가 epsilon 이내라 판정 불가입니다."
                        if predicted == "UNDECIDED"
                        else "예상 라벨과 판정 결과가 다릅니다."
                    )
                ),
            }
        except (KeyError, TypeError, ValueError) as error:
            result = {
                "case": case_name,
                "expected": expected,
                "predicted": "ERROR",
                "cross_score": None,
                "x_score": None,
                "passed": False,
                "reason": str(error),
            }

        results.append(result)
        if result["predicted"] == "ERROR":
            output_fn(f"{case_name}: FAIL (오류: {result['reason']})")
        else:
            status = "PASS" if result["passed"] else "FAIL"
            output_fn(
                f"{case_name}: Cross={result['cross_score']}, X={result['x_score']}, "
                f"판정={result['predicted']} | expected={result['expected']} | {status}"
            )

    failures = [result for result in results if not result["passed"]]
    benchmarks = [benchmark_size(size) for size in (3, 5, 13, 25)]
    print_benchmark_table(benchmarks, output_fn)

    output_fn("\n결과 요약")
    output_fn(f"전체: {len(results)} | 통과: {len(results) - len(failures)} | 실패: {len(failures)}")
    if failures:
        output_fn("실패 케이스:")
        for result in failures:
            output_fn(f"- {result['case']}: {result['reason']}")

    return results
