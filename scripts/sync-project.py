#!/usr/bin/env python3
"""Add every open issue to the GitHub Project and set Area / Size / Priority from labels.

Usage:  python3 scripts/sync-project.py [--repo endodod/Primordia] [--project 1]
Needs:  gh CLI with the `project` scope (`gh auth refresh -s project`). GitHub Projects only
        has a GraphQL API, which Claude Code cloud sessions can't use — run this locally.
Safe to re-run: issues already on the board are only updated.
"""

import argparse
import json
import subprocess
import sys

FIELDS = {"Area": "area: ", "Size": "size: ", "Priority": ""}
PRIORITIES = {"P0", "P1", "P2"}


def gh(*args):
    res = subprocess.run(["gh", *args], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}...: {res.stderr.strip()}")
    return res.stdout


def label_value(field, labels):
    prefix = FIELDS[field]
    for name in labels:
        if field == "Priority" and name in PRIORITIES:
            return name
        if prefix and name.startswith(prefix):
            return name[len(prefix):]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="endodod/Primordia")
    ap.add_argument("--project", type=int, help="project number (default: the one titled Primordia)")
    args = ap.parse_args()
    owner = args.repo.split("/")[0]

    projects = json.loads(gh("project", "list", "--owner", owner, "--format", "json"))["projects"]
    project = next((p for p in projects if (args.project and p["number"] == args.project)
                    or (not args.project and p["title"] == "Primordia")), None)
    if not project:
        sys.exit("Project not found — run scripts/setup-github.sh first.")
    number, project_id = str(project["number"]), project["id"]

    fields = json.loads(gh("project", "field-list", number, "--owner", owner, "--format", "json"))["fields"]
    options = {f["name"]: (f["id"], {o["name"]: o["id"] for o in f.get("options", [])})
               for f in fields if f["name"] in FIELDS}

    items = json.loads(gh("project", "item-list", number, "--owner", owner, "--limit", "1000",
                          "--format", "json"))["items"]
    on_board = {i["content"].get("url"): i["id"] for i in items if i.get("content")}

    issues = json.loads(gh("issue", "list", "--repo", args.repo, "--state", "open", "--limit", "1000",
                           "--json", "url,title,labels"))
    added = 0
    for issue in issues:
        item_id = on_board.get(issue["url"])
        if not item_id:
            item_id = json.loads(gh("project", "item-add", number, "--owner", owner,
                                    "--url", issue["url"], "--format", "json"))["id"]
            added += 1
        labels = [l["name"] for l in issue["labels"]]
        for field, (field_id, opts) in options.items():
            value = label_value(field, labels)
            if value and value in opts:
                gh("project", "item-edit", "--id", item_id, "--project-id", project_id,
                   "--field-id", field_id, "--single-select-option-id", opts[value])
        print(f"  ✓ {issue['title']}")
    print(f"{added} added, {len(issues) - added} already on the board")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))
