r"""Stamps built LLM documentation files with the correct ReadTheDocs version slug.

Each Vizro docset's source ``docs/llms.txt`` uses a fixed placeholder URL for
all of its own page links (e.g. ``https://vizro.readthedocs.io/en/stable/`` for
``vizro-core``, ``https://vizro.readthedocs.io/projects/vizro-mcp/en/latest/``
for ``vizro-mcp``). When ReadTheDocs builds the docs, this script replaces the
placeholder with the build's canonical URL (``READTHEDOCS_CANONICAL_URL``).
This keeps production and pull-request preview links self-consistent with the
version and host that serve them. ``READTHEDOCS_VERSION`` is retained as a
fallback for older Read the Docs environments.

Intended to run from a docset directory (e.g. ``vizro-mcp/``) immediately after
``zensical build``, as part of the docs build step on ReadTheDocs.

If ``READTHEDOCS_VERSION`` is not set (e.g. during a local build), the file is
left unchanged. If the computed versioned URL is identical to the placeholder
(e.g. ``stable`` build of vizro-core, ``latest`` build of vizro-mcp), the file
is also left unchanged.

Usage::

    python ../tools/stamp_llms_txt.py \
        --placeholder=https://vizro.readthedocs.io/projects/vizro-mcp/en/latest/ \
        --site-dir=site \
        --filename=llms.txt \
        --filename=llms-full.txt
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


def stamp_llms_txt(placeholder: str, site_dir: Path, filenames: tuple[str, ...] = ("llms.txt",)) -> int:
    """Replace ``placeholder`` in selected files with the versioned URL."""
    version = os.environ.get("READTHEDOCS_VERSION")
    canonical_url = os.environ.get("READTHEDOCS_CANONICAL_URL")
    site_files = [site_dir / filename for filename in filenames]

    if not version:
        print(f"READTHEDOCS_VERSION not set, leaving {len(site_files)} LLM documentation file(s) unchanged.")
        return 0

    missing = [path for path in site_files if not path.exists()]
    if missing:
        for path in missing:
            print(f"ERROR: {path} not found. Run after `zensical build` from the docset directory.")
        return 1

    versioned_url = canonical_url.rstrip("/") + "/" if canonical_url else compute_versioned_url(placeholder, version)

    if versioned_url == placeholder:
        print(f"READTHEDOCS_VERSION='{version}' matches placeholder, no stamping needed.")
        return 0

    stamped_files = 0
    for site_file in site_files:
        content = site_file.read_text(encoding="utf-8")
        if placeholder not in content:
            print(f"Placeholder '{placeholder}' not found in {site_file}, nothing to replace.")
            continue
        site_file.write_text(content.replace(placeholder, versioned_url), encoding="utf-8")
        stamped_files += 1
    print(f"Stamped {stamped_files} file(s): replaced '{placeholder}' with '{versioned_url}'.")
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
    parser.add_argument(
        "--filename",
        action="append",
        default=None,
        help="Filename under site-dir to stamp; repeat for multiple files (default: llms.txt).",
    )
    args = parser.parse_args()

    if not args.placeholder.endswith("/"):
        parser.error("--placeholder must end with a trailing slash")

    return stamp_llms_txt(
        placeholder=args.placeholder,
        site_dir=args.site_dir,
        filenames=tuple(args.filename or ["llms.txt"]),
    )


if __name__ == "__main__":
    sys.exit(main())
