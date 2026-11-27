#!/usr/bin/env python3
"""Set GitHub "blocked by" dependencies between roadmap issues (idempotent).

Usage:  python3 scripts/set-dependencies.py [--repo endodod/Primordia] [--dry-run]
Issue numbers refer to the issues created by seed-issues.py in endodod/Primordia.
Uses REST only, so it also works from Claude Code cloud sessions.
"""

import argparse
import json
import subprocess
import sys

# issue: [issues it is blocked by]
BLOCKED_BY = {
    # Phase 1 — everything in the engine waits for the numeric strategy (ADR-0002)
    11: [10], 12: [11], 13: [12], 14: [13], 15: [12], 16: [12], 17: [10], 18: [12],
    19: [13], 21: [13], 22: [12], 23: [13], 24: [16], 25: [24], 26: [19], 27: [14, 15],
    # Phase 2
    28: [23], 29: [30, 31], 30: [11], 31: [11], 32: [15], 33: [11], 34: [14], 35: [34],
    36: [14], 37: [12], 38: [37], 39: [19], 40: [16, 19], 41: [24], 42: [19], 43: [16],
    44: [19, 37, 39, 42],
    # Phase 3
    46: [44], 47: [44], 48: [46], 49: [16], 50: [34], 51: [44], 52: [46, 47, 48],
    # Phase 4
    53: [52], 54: [44], 55: [54], 56: [17, 53, 54, 55], 57: [56], 58: [55, 57], 59: [56],
    60: [55], 61: [57], 62: [56],
    # Phase 5
    63: [65], 64: [63], 68: [63], 70: [63], 71: [63, 68, 69, 70],
    # Phase 6
    72: [15], 73: [72], 74: [72], 75: [72], 76: [30], 77: [12],
}


def gh(*args):
    res = subprocess.run(["gh", *args], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:4])}: {res.stderr.strip()}")
    return res.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="endodod/Primordia")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    repo = args.repo

    ids = {}

    def issue_id(number):
        if number not in ids:
            ids[number] = gh("api", f"repos/{repo}/issues/{number}", "-q", ".id").strip()
        return ids[number]

    added = 0
    for issue, blockers in BLOCKED_BY.items():
        existing = set(json.loads(gh("api", f"repos/{repo}/issues/{issue}/dependencies/blocked_by",
                                     "-q", "[.[].number]")))
        for blocker in blockers:
            if blocker in existing:
                continue
            print(f"  #{issue} blocked by #{blocker}")
            if not args.dry_run:
                gh("api", "-X", "POST", f"repos/{repo}/issues/{issue}/dependencies/blocked_by",
                   "-F", f"issue_id={issue_id(blocker)}", "--silent")
            added += 1
    print(f"{added} dependencies {'would be ' if args.dry_run else ''}added")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))
