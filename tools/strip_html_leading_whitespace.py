r"""Removes leading whitespace before ``<!doctype html>`` in every built HTML page.

Zensical's generated ``base.html`` template imports a partial on its own line
without Jinja whitespace control::

    {#-
      This file was automatically generated - do not edit
    -#}
    {% import "partials/language.html" as lang with context %}
    <!doctype html>

Because ``{% import %}`` has no trailing ``-%}``, the newline after it is
emitted, so every built page starts with ``"\n<!doctype html>"`` instead of
``"<!doctype html>"``.

Browsers tolerate this, but HTML-to-markdown converters do not: a leading text
node means the doctype is parsed as bogus character data rather than a doctype
declaration. Cloudflare's Markdown for Agents (which Read the Docs uses to serve
``Accept: text/markdown`` requests) then emits a literal ``<!doctype html>`` line
into the body of the markdown that AI agents consume.

This script strips that leading whitespace as a post-build step. It is a
workaround for an upstream Zensical template issue; once the generated template
uses ``{% import ... -%}`` (or the build enables ``trim_blocks``), this can go.

Intended to run from a docset directory (e.g. ``vizro-core/``) immediately after
``zensical build``, as part of the docs build step on ReadTheDocs.

Usage::

    python ../tools/strip_html_leading_whitespace.py --site-dir=site
"""
# ruff: noqa: T201

import argparse
import sys
from pathlib import Path

DOCTYPE = "<!doctype html>"


def strip_leading_whitespace(site_dir: Path) -> int:
    """Rewrite HTML files under ``site_dir`` that start with whitespace before the doctype."""
    if not site_dir.is_dir():
        print(f"ERROR: {site_dir} not found. Run after `zensical build` from the docset directory.")
        return 1

    html_files = sorted(site_dir.rglob("*.html"))
    if not html_files:
        print(f"ERROR: no HTML files found under {site_dir}.")
        return 1

    stripped = 0
    for path in html_files:
        content = path.read_text(encoding="utf-8")
        if not content.startswith((" ", "\t", "\n", "\r")):
            continue
        # Only touch pages whose sole problem is whitespace before the doctype, so that a
        # future template change (or an unrelated file) is left alone rather than mangled.
        if content.lstrip()[: len(DOCTYPE)].lower() != DOCTYPE:
            continue
        path.write_text(content.lstrip(), encoding="utf-8")
        stripped += 1

    print(f"Stripped leading whitespace from {stripped} of {len(html_files)} HTML files in {site_dir}.")
    return 0


def main() -> int:
    """Parse CLI arguments and invoke :func:`strip_leading_whitespace`."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--site-dir",
        default="site",
        type=Path,
        help="Built docs directory containing the HTML pages (default: site).",
    )
    args = parser.parse_args()
    return strip_leading_whitespace(site_dir=args.site_dir)


if __name__ == "__main__":
    sys.exit(main())
