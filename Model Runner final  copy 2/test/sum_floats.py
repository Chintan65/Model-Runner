# sum_floats.py
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Sums three floating-point numbers.")
    parser.add_argument("--number1", type=float, required=True, help="The first number")
    parser.add_argument("--number2", type=float, required=True, help="The second number")
    parser.add_argument("--number3", type=float, required=True, help="The third number")
    args = parser.parse_args()

    sum_result = args.number1 + args.number2 + args.number3

    output_data = {
        "sum": sum_result,
        "input_numbers": [args.number1, args.number2, args.number3]
    }

    print(json.dumps(output_data, indent=4))

if __name__ == "__main__":
    main()