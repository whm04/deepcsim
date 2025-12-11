import os
import argparse
import sys
import json
from deepcsim.core.scanner import scan_directory


def main():
    parser = argparse.ArgumentParser(
        description="DeepCSIM - Code Similarity Analyzer Code Scanner")

    # Default directory = current working directory
    parser.add_argument(
        "directory", help="Directory to scan", nargs="?", default=os.getcwd())
    parser.add_argument("--threshold", type=float,
                        default=80.0, help="Similarity threshold (0-100)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    try:
        results = scan_directory(args.directory, args.threshold)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"DeepCSIM Scan Results for: {args.directory}")
        print(f"Total Similar Pairs Found: {results['count']}")
        print("-" * 50)
        for res in results['results']:
            print(f"File 1: {res['file1']}")
            print(f"File 2: {res['file2']}")
            print(f"Similarity: {res['similarity']}%")
            print(f"Reason: {res['reason']}")
            print("-" * 50)


if __name__ == "__main__":
    main()
