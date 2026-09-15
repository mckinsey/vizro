"""Reports documentation links still hardcoded to the fixed version placeholder.

The agent-facing ``llms.txt`` / ``llms-full.txt`` files are version-stamped
after the build (see ``tools/stamp_llms_txt.py``), but absolute links authored
directly into pages are not. On a non-stable build (e.g. ``latest`` or a pinned
version) such links send readers to the wrong version of the docs.

This scans the built ``site/`` tree for ``<a>`` links whose ``href`` starts with
the placeholder base URL, ignoring the ``<link rel="canonical">`` tag (which is
intentionally pinned to ``stable`` for search engines) and ``<meta>`` tags such
as ``og:url``.

Report-only by default: it prints a per-file summary and exits 0, so it never
breaks a build. Pass ``--fail`` to exit 1 when offenders are found; that is the
intended enforcement mode once the existing absolute links have been migrated to
relative links. See ``docs/pages/for-llms.md`` for the pattern to follow.
"""
# ruff: noqa: T201

import argparse
import re
import sys
from pathlib import Path

# Matches an <a ...> open tag whose href points at the placeholder base URL.
# <link>/<meta> tags are never matched because we anchor on "<a ".
_ANCHOR_RE_TEMPLATE = r'<a\b[^>]*\bhref="{placeholder}[^"]*"'


def find_stable_links(site_dir: Path, placeholder: str) -> dict[Path, int]:
    """Return a mapping of HTML file -> count of anchor links to the placeholder."""
    anchor_re = re.compile(_ANCHOR_RE_TEMPLATE.format(placeholder=re.escape(placeholder)))
    offenders: dict[Path, int] = {}
    for html_path in sorted(site_dir.rglob("*.html")):
        count = len(anchor_re.findall(html_path.read_text(encoding="utf-8")))
        if count:
            offenders[html_path] = count
    return offenders


def check_stable_links(site_dir: Path, placeholder: str, fail: bool = False) -> int:
    """Report anchor links hardcoded to ``placeholder``; exit non-zero only with ``fail``."""
    if not site_dir.is_dir():
        print(f"ERROR: {site_dir} not found. Run after `zensical build` from the docset directory.")
        return 1

    offenders = find_stable_links(site_dir, placeholder)
    if not offenders:
        print(f"OK: no <a> links hardcoded to '{placeholder}' found in {site_dir}.")
        return 0

    total = sum(offenders.values())
    label = "ERROR" if fail else "NOTE"
    print(f"{label}: {total} <a> link(s) hardcoded to '{placeholder}' (would point at the wrong version on a")
    print("non-stable build). Convert these to relative links; see docs/pages/for-llms.md for the pattern.")
    for html_path, count in offenders.items():
        print(f"  {count:>3}  {html_path}")

    return 1 if fail else 0


def main() -> int:
    """Parse CLI arguments and invoke :func:`check_stable_links`."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--placeholder",
        required=True,
        help="Placeholder base URL to flag in anchor hrefs (e.g. https://vizro.readthedocs.io/en/stable/).",
    )
    parser.add_argument(
        "--site-dir",
        default="site",
        type=Path,
        help="Built docs directory to scan (default: site).",
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit 1 when offenders are found (enforcement mode). Off by default (report-only).",
    )
    args = parser.parse_args()
    return check_stable_links(site_dir=args.site_dir, placeholder=args.placeholder, fail=args.fail)


if __name__ == "__main__":
    sys.exit(main())
