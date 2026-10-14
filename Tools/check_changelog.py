#!/usr/bin/env python3
"""Changelog integrity and sprint tracker gate.

Validates:
1. Existence of CHANGELOG.md in repository root.
2. Compliance with Keep a Changelog standard format.
3. Verification that Sprints 1 to 4 are recorded.
4. Output structured TBS probe json for ACC6 Aggregator.
"""

import argparse
import json
import os
import re
import sys

CHANGELOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CHANGELOG.md")


def validate_changelog(path: str = CHANGELOG_PATH) -> tuple[bool, list[str], dict]:
    errors = []
    data = {"entries": [], "sprints_found": []}

    if not os.path.isfile(path):
        errors.append(f"CHANGELOG.md not found at {path}")
        return False, errors, data

    with open(path, encoding="utf-8") as fh:
        content = fh.read()

    if "# Changelog" not in content and "# CHANGELOG" not in content:
        errors.append("CHANGELOG.md missing top-level # Changelog header")

    # Look for sprint headings
    sprint_pattern = re.compile(r"##\s*\[?(Sprint\s*[1-4][^\]\n]*)\]?", re.I)
    matches = sprint_pattern.findall(content)
    data["sprints_found"] = matches

    for s_num in [1, 2, 3, 4]:
        found = any(f"Sprint {s_num}" in m or f"sprint {s_num}" in m.lower() for m in matches)
        if not found:
            errors.append(f"Missing documentation for Sprint {s_num}")

    ok = len(errors) == 0
    return ok, errors, data


def main():
    parser = argparse.ArgumentParser(description="Changelog Validator")
    parser.add_argument("--path", default=CHANGELOG_PATH, help="Path to CHANGELOG.md")
    args = parser.parse_args()

    print("=== Changelog & Sprint Tracking Gate ===")
    ok, errors, data = validate_changelog(args.path)

    if ok:
        print(f"✅ CHANGELOG.md is valid. Sprints documented: {', '.join(data['sprints_found'])}")
    else:
        print(f"❌ CHANGELOG.md validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")

    print("##TBS##" + json.dumps({
        "probe": "check_changelog",
        "status": "pass" if ok else "fail",
        "v": 1,
        "data": {
            "sprints": data["sprints_found"],
            "errors": errors,
        }
    }))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
