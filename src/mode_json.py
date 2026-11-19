"""Analyze the pattern cases stored in data.json."""

import json
from pathlib import Path
import re
from collections import Counter

from .judge import EPSILON, decide, normalize_label
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
                raise ValueError(
                    f"케이스 키 {case_name!r}의 형식이 잘못됐습니다. "
                    "size_{N}_{idx} 형식이어야 합니다."
                )
            size = int(key_match.group(1))
            if len(pattern) != size or len(pattern[0]) != size:
                raise ValueError(f"키는 {size}×{size}를 가리키지만 패턴 크기가 다릅니다.")
            filter_key = f"size_{size}"
            if filter_key not in filters:
                raise ValueError(
                    f"필터 묶음 '{filter_key}'을 찾을 수 없습니다. "
                    "filters에 해당 크기의 Cross와 X 필터를 추가하세요."
                )
            filter_set = filters[filter_key]
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
                "failure_type": (
                    None
                    if passed
                    else "동점/수치 비교"
                    if predicted == "UNDECIDED"
                    else "예측/expected 불일치"
                ),
            }
        except (KeyError, TypeError, ValueError) as error:
            reason = str(error)
            failure_type = "라벨/스키마" if "라벨" in reason or "필터 키" in reason else "데이터/스키마"
            result = {
                "case": case_name,
                "expected": expected,
                "predicted": "ERROR",
                "cross_score": None,
                "x_score": None,
                "passed": False,
                "reason": reason,
                "failure_type": failure_type,
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
    undecided_count = sum(result["predicted"] == "UNDECIDED" for result in results)
    failure_counts = Counter(result["failure_type"] for result in failures)
    benchmarks = [benchmark_size(size) for size in (3, 5, 13, 25)]
    print_benchmark_table(benchmarks, output_fn)

    output_fn("\n결과 요약")
    output_fn(f"동점 기준 epsilon: {EPSILON:g}")
    output_fn(f"전체: {len(results)} | 통과: {len(results) - len(failures)} | 실패: {len(failures)}")
    output_fn(f"판정 불가(UNDECIDED): {undecided_count}")
    if failures:
        output_fn("실패 원인별 집계:")
        for failure_type, count in sorted(failure_counts.items()):
            output_fn(f"- {failure_type}: {count}건")
        output_fn("실패 케이스:")
        for result in failures:
            output_fn(f"- {result['case']}: {result['reason']}")

    return results
