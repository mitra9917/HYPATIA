#!/usr/bin/env python3
"""Add all playbook issues to GitHub Project 4 with Playbook # and Status."""
from __future__ import annotations

import json
import subprocess
import time

OWNER = "mitra9917"
PROJECT = 4
REPO = "HYPATIA"
PLAYBOOK_FIELD = "Playbook #"
STATUS_FIELD = "Status"
STATUS_UP_NEXT = "Up next"

ORDER = [
    44, 2, 3, 5, 48, 4, 45, 46, 6, 7, 8, 9,
    10, 11, 50, 56, 12, 13, 51, 14, 55, 15, 18,
    52, 16, 53, 54, 17,
    19, 20, 21, 22, 58, 23, 57, 59, 24, 25,
    26, 27, 28, 29, 30, 31, 32, 33, 60, 62, 61,
    47, 49, 34, 35, 36, 37, 64, 39, 66, 63, 40, 67, 65, 41, 42, 43, 38, 68,
]


def run(*args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        check=check,
        capture_output=True,
        text=True,
    )


def existing_issue_numbers() -> set[int]:
    proc = run(
        "gh", "project", "item-list", str(PROJECT),
        "--owner", OWNER, "--format", "json", "--limit", "200",
    )
    if proc.returncode != 0:
        return set()
    data = json.loads(proc.stdout)
    nums: set[int] = set()
    for item in data.get("items", []):
        content = item.get("content") or {}
        if content.get("number"):
            nums.add(int(content["number"]))
    return nums


def main() -> None:
    have = existing_issue_numbers()
    for step, num in enumerate(ORDER, start=1):
        url = f"https://github.com/{OWNER}/{REPO}/issues/{num}"
        if num in have:
            print(f"[{step:02d}] #{num} skip (already on board)")
            continue
        print(f"[{step:02d}] #{num}")
        run(
            "gh", "project", "item-add", str(PROJECT),
            "--owner", OWNER, "--url", url,
        )
        time.sleep(2.0)
        run(
            "gh", "project", "item-edit", str(PROJECT),
            "--owner", OWNER, "--url", url,
            "--field", PLAYBOOK_FIELD, "--number", str(float(step)),
        )
        time.sleep(1.0)
        run(
            "gh", "project", "item-edit", str(PROJECT),
            "--owner", OWNER, "--url", url,
            "--field", STATUS_FIELD, "--value", STATUS_UP_NEXT,
        )
        time.sleep(1.5)
        have.add(num)
    print(f"\nProject: https://github.com/users/{OWNER}/projects/{PROJECT}")
    print("Board view: group by Status; table view: sort by Playbook # ascending.")


if __name__ == "__main__":
    main()
