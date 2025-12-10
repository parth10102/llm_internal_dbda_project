import argparse
import json
from pipeline import process_input

def parse_args():
    parser = argparse.ArgumentParser(
        description='LLM-based cleaner: text or URL -> cleaned JSON'
    )

    parser.add_argument(
        'input',
        help='Text to clean OR a URL (starting with http/https). '
        'Wrap text with spaces in quotes.'
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )

    return parser.parse_args()

def main():
    args = parse_args()
    result = process_input(args.input)
    data = result.model_dump()

    if args.pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data, ensure_ascii=False))

if __name__ == "__main__":
    main()