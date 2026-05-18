"""Checks that all URLs in docs/llms.txt map to existing local documentation files.

Intended to run from the vizro-core/ directory as part of CI. Exits with code 1
and prints a report if any referenced files are missing, renamed, or deleted.

URLs in llms.txt use the stable base URL, for example:
    https://vizro.readthedocs.io/en/stable/pages/user-guides/install/

Mapping to local file:
    https://vizro.readthedocs.io/en/stable/pages/user-guides/install/
    -> strip base URL -> pages/user-guides/install/
    -> strip trailing slash, add .md -> pages/user-guides/install.md
    -> prepend docs/ -> docs/pages/user-guides/install.md
"""
# ruff: noqa: T201

import re
import sys
from pathlib import Path

DOCS_BASE_URL = "https://vizro.readthedocs.io/en/stable/"
LLMS_TXT = Path("docs/llms.txt")
DOCS_DIR = Path("docs")


def url_to_local_path(url: str) -> Path | None:
    """Convert a stable docs URL to a local docs file path.

    Returns None for URLs that don't match the stable base (external links, other packages, etc.).
    """
    if not url.startswith(DOCS_BASE_URL):
        return None

    relative = url[len(DOCS_BASE_URL) :]
    return DOCS_DIR / (relative.rstrip("/") + ".md")


def check_llms_txt() -> int:
    """Check all docs URLs in llms.txt resolve to existing local files.

    Returns the number of broken references found.
    """
    if not LLMS_TXT.exists():
        print(f"ERROR: {LLMS_TXT} not found. Run from the vizro-core/ directory.")
        return 1

    content = LLMS_TXT.read_text(encoding="utf-8")

    # Extract all URLs from markdown links: [text](url)
    urls = re.findall(r"\[.*?\]\(([^)]+)\)", content)

    broken = []
    skipped = []

    for url in urls:
        local_path = url_to_local_path(url)
        if local_path is None:
            skipped.append(url)
            continue
        if not local_path.exists():
            broken.append((url, local_path))

    if skipped:
        print(f"Skipped {len(skipped)} non-docs URL(s) (external links, other packages, etc.)")

    if broken:
        print(f"\nERROR: Found {len(broken)} broken reference(s) in {LLMS_TXT}:\n")
        for url, local_path in broken:
            print(f"  URL:        {url}")
            print(f"  Local path: {local_path}  (file not found)")
            print()
        print("Update docs/llms.txt to fix the references above.")
        return len(broken)

    checked = len(urls) - len(skipped)
    print(f"OK: All {checked} docs URL(s) in {LLMS_TXT} resolve to existing local files.")
    return 0


if __name__ == "__main__":
    sys.exit(check_llms_txt())
