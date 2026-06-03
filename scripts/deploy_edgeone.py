#!/usr/bin/env python3
"""Deploy an HTML file only when an EdgeOne workflow is already configured."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def detect_workflow(repo: Path) -> list[Path]:
    workflows = repo / ".github" / "workflows"
    if not workflows.exists():
        return []
    return [path for path in workflows.glob("*.*") if "edgeone" in path.read_text(encoding="utf-8", errors="ignore").lower()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", required=True)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--publish-dir", default="")
    parser.add_argument("--deploy-command", default="", help="Explicit local deploy command, if the repo already defines one.")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    html_path = Path(args.html).resolve()
    result = {"deployed": False, "url": "", "local_path": str(html_path), "message": ""}

    if args.publish_dir:
        publish_dir = (repo / args.publish_dir).resolve()
        publish_dir.mkdir(parents=True, exist_ok=True)
        target = publish_dir / html_path.name
        shutil.copy2(html_path, target)
        result["local_path"] = str(target)

    if args.deploy_command:
        completed = subprocess.run(args.deploy_command, cwd=repo, shell=True, text=True, capture_output=True, timeout=300)
        result["deployed"] = completed.returncode == 0
        result["message"] = completed.stdout if completed.returncode == 0 else completed.stderr
    elif detect_workflow(repo):
        result["message"] = "EdgeOne GitHub Actions workflow detected. Commit/push is still required by the caller."
    else:
        result["message"] = "No EdgeOne deployment workflow or command detected; returned local file path only."

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
