"""Run offline metrics against a JSON file of reviewed provider predictions.

Usage from the backend directory:
  python -m apps.writing.evaluate_cli --predictions /path/to/predictions.json

The prediction JSON is an object keyed by evaluation case id. Each value contains
at least corrected_text and errors. Do not commit real learner submissions.
"""
import argparse
import json
from pathlib import Path

from .evaluation import evaluate_predictions


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        default=str(Path(__file__).with_name("evaluation_cases.json")),
        help="Path to the synthetic evaluation cases JSON.",
    )
    parser.add_argument("--predictions", required=True, help="JSON object keyed by case id.")
    args = parser.parse_args(argv)

    with open(args.dataset, encoding="utf-8") as handle:
        cases = json.load(handle)
    with open(args.predictions, encoding="utf-8") as handle:
        predictions = json.load(handle)
    metrics = evaluate_predictions(cases, predictions)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return metrics


if __name__ == "__main__":
    main()
