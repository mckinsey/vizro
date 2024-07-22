"""Check for security issues in workflows files."""

import sys
from pathlib import Path

# according to this article: https://nathandavison.com/blog/github-actions-and-the-threat-of-malicious-pull-requests
# we should avoid using `pull_request_target` for security reasons
risky_text = "pull_request_target"


def find_risky_files(path: str):
    """Searching for risky text in yml files for given path."""
    return {str(file) for file in Path(path).rglob("*.yml") if f"{risky_text}" in file.read_text()}


if __name__ == "__main__":
    risky_files = find_risky_files(sys.argv[1])
    if risky_files:
        sys.exit(f"{risky_text} found in files {risky_files}.")
