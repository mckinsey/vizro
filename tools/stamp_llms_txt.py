r"""Stamps a built ``site/llms.txt`` with the correct ReadTheDocs version slug.

Each Vizro docset's source ``docs/llms.txt`` uses a fixed placeholder URL for
all of its own page links (e.g. ``https://vizro.readthedocs.io/en/stable/`` for
``vizro-core``, ``https://vizro.readthedocs.io/projects/vizro-mcp/en/latest/``
for ``vizro-mcp``). When ReadTheDocs builds the docs, this script replaces the
placeholder's trailing version segment with the actual build version
(``READTHEDOCS_VERSION``) so that links in the built ``llms.txt`` are
self-consistent with the version that serves them.

Intended to run from a docset directory (e.g. ``vizro-mcp/``) immediately after
``zensical build``, as part of the docs build step on ReadTheDocs.

If ``READTHEDOCS_VERSION`` is not set (e.g. during a local build), the file is
left unchanged. If the computed versioned URL is identical to the placeholder
(e.g. ``stable`` build of vizro-core, ``latest`` build of vizro-mcp), the file
is also left unchanged.

Usage::

    python ../tools/stamp_llms_txt.py \
        --placeholder=https://vizro.readthedocs.io/projects/vizro-mcp/en/latest/ \
        --site-dir=site
"""
# ruff: noqa: T201

import argparse
import os
import sys
from pathlib import Path


def compute_versioned_url(placeholder: str, version: str) -> str:
    """Swap the placeholder's trailing version segment with ``version``.

    Assumes the placeholder is a ReadTheDocs-shaped URL whose last
    path segment is the version slug, e.g.:

    * ``https://vizro.readthedocs.io/en/stable/`` (segments: ``en``, ``stable``)
    * ``https://vizro.readthedocs.io/projects/vizro-mcp/en/latest/``
      (segments: ``projects``, ``vizro-mcp``, ``en``, ``latest``)

    The trailing slash is normalized away, the last segment is dropped,
    ``version`` is appended, and a trailing slash is added back so the
    result is directly substitutable for the placeholder in the file.

    Example::

        compute_versioned_url(
            "https://vizro.readthedocs.io/projects/vizro-mcp/en/latest/",
            "vizro-mcp-0.1.4",
        )
        # -> "https://vizro.readthedocs.io/projects/vizro-mcp/en/vizro-mcp-0.1.4/"
    """
    stem = placeholder.rstrip("/").rsplit("/", 1)[0]
    return f"{stem}/{version}/"


def stamp_llms_txt(placeholder: str, site_dir: Path) -> int:
    """Replace ``placeholder`` in ``<site_dir>/llms.txt`` with the versioned URL."""
    version = os.environ.get("READTHEDOCS_VERSION")
    site_llms_txt = site_dir / "llms.txt"

    if not version:
        print(f"READTHEDOCS_VERSION not set, leaving {site_llms_txt} unchanged.")
        return 0

    if not site_llms_txt.exists():
        print(f"ERROR: {site_llms_txt} not found. Run after `zensical build` from the docset directory.")
        return 1

    versioned_url = compute_versioned_url(placeholder, version)

    if versioned_url == placeholder:
        print(f"READTHEDOCS_VERSION='{version}' matches placeholder, no stamping needed.")
        return 0

    content = site_llms_txt.read_text(encoding="utf-8")

    if placeholder not in content:
        print(f"Placeholder '{placeholder}' not found in {site_llms_txt}, nothing to replace.")
        return 0

    stamped = content.replace(placeholder, versioned_url)
    site_llms_txt.write_text(stamped, encoding="utf-8")
    print(f"Stamped {site_llms_txt}: replaced '{placeholder}' with '{versioned_url}'.")
    return 0


def main() -> int:
    """Parse CLI arguments and invoke :func:`stamp_llms_txt`."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--placeholder",
        required=True,
        help="The full placeholder URL used in the source llms.txt (e.g. https://vizro.readthedocs.io/en/stable/).",
    )
    parser.add_argument(
        "--site-dir",
        default="site",
        type=Path,
        help="Built docs directory containing llms.txt (default: site).",
    )
    args = parser.parse_args()

    if not args.placeholder.endswith("/"):
        parser.error("--placeholder must end with a trailing slash")

    return stamp_llms_txt(placeholder=args.placeholder, site_dir=args.site_dir)


if __name__ == "__main__":
    sys.exit(main())
