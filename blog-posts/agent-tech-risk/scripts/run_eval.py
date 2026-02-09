#!/usr/bin/env python3
"""Run full model evaluation against HF dataset.

Usage:
    uv run python scripts/run_eval.py                    # all 4 models, all cases
    uv run python scripts/run_eval.py --max-cases 3      # quick test with 3 cases
    uv run python scripts/run_eval.py --models sonnet-4-5 # single model
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from risk_discovery.eval import MODELS, run_eval


def main():
    parser = argparse.ArgumentParser(description="Run risk discovery evaluation")
    parser.add_argument(
        "--models",
        default="all",
        help="Comma-separated model keys or 'all' (default: all)",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=None,
        help="Max cases to evaluate",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Save results to JSON file",
    )
    args = parser.parse_args()

    if args.models == "all":
        selected = MODELS
    else:
        selected = {k: MODELS[k] for k in args.models.split(",") if k in MODELS}

    results = run_eval(models=selected, max_cases=args.max_cases)

    if args.output:
        out = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "models": list(selected.keys()),
            "results": results,
        }
        Path(args.output).write_text(json.dumps(out, indent=2, default=str))
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
