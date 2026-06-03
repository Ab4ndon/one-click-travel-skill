#!/usr/bin/env python3
"""Build default route data from normalized hotel and attraction coordinates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from generate_html import build_default_routes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Normalized trip JSON.")
    parser.add_argument("--output", required=True, help="Trip JSON with routes added.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing routes.")
    args = parser.parse_args()

    input_path = Path(args.input)
    data: dict[str, Any] = json.loads(input_path.read_text(encoding="utf-8-sig"))
    if args.overwrite or not data.get("routes"):
        data["routes"] = build_default_routes(data)
    Path(args.output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
