"""Set components compendium Vizro version from RELEASE_VERSION (release workflow)."""

import os
import re
import sys
from pathlib import Path

_DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "vizro-core"
    / "docs"
    / "pages"
    / "components_compendium"
    / "compendium_data.yaml"
)
_VERSION_PATTERN = re.compile(r'^(vizro_version:\s*")[^"]*(")', re.MULTILINE)


def main() -> None:
    """Update vizro_version in compendium_data.yaml."""
    raw = os.environ.get("RELEASE_VERSION", "").strip()
    if not raw:
        sys.exit("RELEASE_VERSION must be set")
    version = raw.removeprefix("v")
    text = _DATA_FILE.read_text(encoding="utf-8")
    new_text, count = _VERSION_PATTERN.subn(rf"\g<1>{version}\g<2>", text, count=1)
    if count != 1:
        sys.exit(f"Expected exactly one vizro_version field in compendium_data.yaml, found {count}")
    _DATA_FILE.write_text(new_text, encoding="utf-8")


if __name__ == "__main__":
    main()
