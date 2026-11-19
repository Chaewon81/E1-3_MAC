"""Entry point for the Mini NPU Simulator."""

from src.mode_input import run_input_mode
from src.mode_json import analyze_json_file
from src.pattern_generator import run_generator_mode
from src.perf import run_optimization_comparison


def main():
    print("Mini NPU Simulator")
    print("1. 사용자 입력으로 패턴 비교")
    print("2. data.json 패턴 분석")
    print("3. 보너스: Cross/X 패턴 생성")
    print("4. 보너스: 2차원/1차원 MAC 성능 비교")
    choice = input("모드를 선택하세요: ").strip()

    if choice == "1":
        run_input_mode()
    elif choice == "2":
        analyze_json_file()
    elif choice == "3":
        run_generator_mode()
    elif choice == "4":
        run_optimization_comparison()
    else:
        print("아직 지원하지 않는 모드입니다.")


if __name__ == "__main__":
    main()
