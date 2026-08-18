r"""TEMPORARY: publishes two probe Markdown files to test how ReadTheDocs serves ``.md``.

Before building a full HTML-to-Markdown pipeline that publishes a ``.md`` twin of
every documentation page, we need to know how ReadTheDocs serves static ``.md``
files from the build output. Two things are unknown:

1. Whether ``.md`` is served at all, or 404s (proxito may only serve known types).
2. What ``Content-Type`` it gets. The published ``llms.txt`` comes back as
   ``text/plain; charset=utf-8``, not ``text/markdown``, and content types cannot
   be configured on ReadTheDocs static output. If ``.md`` is served as
   ``application/octet-stream`` browsers will download it rather than display it.

This writes probes for both candidate URL shapes, because agents guess both:

* ``<site>/agent-md-probe.md``       -> sibling-of-page style
* ``<site>/agent-md-probe/index.md`` -> directory-index style

Check them on the ReadTheDocs PR preview build with::

    curl -sD - -o /dev/null <preview-url>/agent-md-probe.md
    curl -sD - -o /dev/null <preview-url>/agent-md-probe/index.md

Delete this script, its ``docs:build`` step, and the probe files once the
content-type question is answered.

Usage::

    python ../tools/emit_md_probe.py --site-dir=site
"""
# ruff: noqa: T201

import argparse
import sys
from pathlib import Path

PROBE_BODY = """---
title: Markdown serving probe
description: Temporary probe to check how ReadTheDocs serves static .md files.
---

# Markdown serving probe

This file is a temporary build artifact. If you are reading it on a published
Vizro documentation site, it should have been deleted - please open an issue.

Its only purpose is to reveal the `Content-Type` ReadTheDocs returns for a
static `.md` file, so that a future pipeline can publish a Markdown twin of
every documentation page for AI agents to consume.
"""

PROBE_PATHS = ("agent-md-probe.md", "agent-md-probe/index.md")


def emit_md_probe(site_dir: Path) -> int:
    """Write the probe Markdown files into ``site_dir``."""
    if not site_dir.is_dir():
        print(f"ERROR: {site_dir} not found. Run after `zensical build` from the docset directory.")
        return 1

    for relative in PROBE_PATHS:
        path = site_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(PROBE_BODY, encoding="utf-8")
        print(f"Wrote probe {path}.")

    return 0


def main() -> int:
    """Parse CLI arguments and invoke :func:`emit_md_probe`."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--site-dir",
        default="site",
        type=Path,
        help="Built docs directory to write the probe files into (default: site).",
    )
    args = parser.parse_args()
    return emit_md_probe(site_dir=args.site_dir)


if __name__ == "__main__":
    sys.exit(main())
