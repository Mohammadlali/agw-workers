#!/usr/bin/env python3
"""Root wrapper for Tools/check_changelog.py."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "Tools", "check_changelog.py")

if __name__ == "__main__":
    if not os.path.isfile(TOOL):
        print(f"Error: {TOOL} not found", file=sys.stderr)
        sys.exit(1)
    os.execv(sys.executable, [sys.executable, TOOL] + sys.argv[1:])
