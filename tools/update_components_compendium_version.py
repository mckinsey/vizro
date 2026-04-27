"""Set components compendium Vizro version from RELEASE_VERSION (release workflow)."""

import os
import re
import sys
from pathlib import Path

_INDEX_HTML = (
    Path(__file__).resolve().parent.parent / "vizro-core" / "docs" / "pages" / "components_compendium" / "index.html"
)
_BADGE_PATTERN = re.compile(r'(<span class="version-badge">)([^<]*)(</span>)')


def main() -> None:
    """Update Vizro version in the components compendium."""
    raw = os.environ.get("RELEASE_VERSION", "").strip()
    if not raw:
        sys.exit("RELEASE_VERSION must be set")
    display = f"v{raw.removeprefix('v')}"
    text = _INDEX_HTML.read_text(encoding="utf-8")
    new_text, count = _BADGE_PATTERN.subn(rf"\g<1>{display}\g<3>", text, count=1)
    if count != 1:
        sys.exit(f"Expected exactly one version-badge span, replaced {count}")
    _INDEX_HTML.write_text(new_text, encoding="utf-8")


if __name__ == "__main__":
    main()
