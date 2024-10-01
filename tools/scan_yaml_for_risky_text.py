"""Check for security issues in workflows files."""

import sys
from pathlib import Path

# pull_request_target needs to be used carefully to not be a security concern, so only allow it to be used in specific
# files which use it correctly.
# https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#pull_request_target
# https://nathandavison.com/blog/github-actions-and-the-threat-of-malicious-pull-requests
risky_text = "pull_request_target"
ignore_files = {".github/workflows/labeler.yml"}


def find_risky_files(path: str):
    """Searching for risky text in yml files for given path."""
    return {
        str(file)
        for file in Path(path).rglob("*.yml")
        if risky_text in file.read_text() and str(file) not in ignore_files
    }


if __name__ == "__main__":
    risky_files = find_risky_files(sys.argv[1])
    if risky_files:
        sys.exit(f"{risky_text} found in files {', '.join(risky_files)}.")
