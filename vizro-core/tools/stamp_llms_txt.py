"""Stamps the built site/llms.txt with the correct ReadTheDocs version.

The source docs/llms.txt uses `stable` as a placeholder in all URLs. When
ReadTheDocs builds the docs, this script replaces `stable` with the actual
version slug (e.g. `0.1.55`, `stable`, `latest`) so that links in the built
llms.txt are self-consistent with the version that serves them.

Intended to run from the vizro-core/ directory after `zensical build`, as part
of the docs build step on ReadTheDocs. If READTHEDOCS_VERSION is not set (e.g.
during a local build), the file is left unchanged.
"""

import os
import sys
from pathlib import Path

SITE_LLMS_TXT = Path("site/llms.txt")
PLACEHOLDER = "https://vizro.readthedocs.io/en/stable/"


def stamp_llms_txt() -> int:
    version = os.environ.get("READTHEDOCS_VERSION")

    if not version:
        print("READTHEDOCS_VERSION not set, leaving site/llms.txt unchanged.")
        return 0

    if not SITE_LLMS_TXT.exists():
        print(f"ERROR: {SITE_LLMS_TXT} not found. Run from the vizro-core/ directory after zensical build.")
        return 1

    versioned_url = f"https://vizro.readthedocs.io/en/{version}/"

    if versioned_url == PLACEHOLDER:
        print(f"READTHEDOCS_VERSION='{version}' matches placeholder, no stamping needed.")
        return 0

    content = SITE_LLMS_TXT.read_text(encoding="utf-8")

    if PLACEHOLDER not in content:
        print(f"Placeholder '{PLACEHOLDER}' not found in {SITE_LLMS_TXT}, nothing to replace.")
        return 0

    stamped = content.replace(PLACEHOLDER, versioned_url)
    SITE_LLMS_TXT.write_text(stamped, encoding="utf-8")
    print(f"Stamped {SITE_LLMS_TXT}: replaced '{PLACEHOLDER}' with '{versioned_url}'.")
    return 0


if __name__ == "__main__":
    sys.exit(stamp_llms_txt())
