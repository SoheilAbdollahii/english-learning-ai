"""Generate predictions for the synthetic Writing evaluation set using a live provider.

This command can incur API charges and sends every dataset sentence to the
configured provider. It is intentionally opt-in and never uses learner history.
"""
import argparse
import json
import os
from pathlib import Path

from .services import WritingProviderError, analyze_writing, get_provider


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        default=str(Path(__file__).with_name("evaluation_cases.json")),
        help="Path to synthetic evaluation cases JSON.",
    )
    parser.add_argument("--output", required=True, help="Path to write predictions JSON.")
    parser.add_argument(
        "--confirm-live-provider-calls",
        action="store_true",
        help="Required: explicitly allow live provider calls and possible API charges.",
    )
    parser.add_argument(
        "--allow-draft-dataset",
        action="store_true",
        help="Required while any case is not marked reviewed/adjudicated/approved.",
    )
    args = parser.parse_args(argv)

    if not args.confirm_live_provider_calls:
        parser.error("Live provider calls require --confirm-live-provider-calls.")
    if not os.environ.get("GEMINI_API_KEY", "").strip():
        parser.error("GEMINI_API_KEY is required; demo mode is not a valid provider evaluation.")

    with open(args.dataset, encoding="utf-8") as handle:
        cases = json.load(handle)
    if not isinstance(cases, list) or not cases:
        parser.error("The evaluation dataset must be a non-empty JSON list.")
    unreviewed = [
        case.get("id", "<missing-id>")
        for case in cases
        if case.get("annotation_status") not in {"reviewed", "adjudicated", "approved"}
    ]
    if unreviewed and not args.allow_draft_dataset:
        parser.error(
            "Dataset contains unreviewed cases. Have qualified educators review it first, "
            "or pass --allow-draft-dataset for explicitly non-release diagnostic work."
        )

    provider = get_provider()
    if provider.name == "demo":
        parser.error("Configured provider resolved to demo; refusing to measure demo output.")

    predictions = {}
    try:
        for case in cases:
            _provider_name, result, _usage = analyze_writing(case["original_text"])
            predictions[case["id"]] = {
                "corrected_text": result["corrected_text"],
                "errors": result["errors"],
            }
    except (KeyError, TypeError, WritingProviderError) as exc:
        parser.error(f"Provider evaluation stopped safely: {exc}")

    output_path = Path(args.output)
    output_path.write_text(json.dumps(predictions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(predictions)} predictions to {output_path}")
    print("Review meaning preservation and explanations manually; this file is not a gold-standard judgement.")
    return predictions


if __name__ == "__main__":
    main()
