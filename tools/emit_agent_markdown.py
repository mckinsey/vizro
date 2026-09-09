"""Emit clean Markdown twins for documentation pages in a built Zensical site.

The source Markdown cannot be published directly because Zensical resolves
includes, custom fences, and mkdocstrings directives while building the HTML.
This post-build step extracts each rendered article and writes both URL shapes
that clients commonly try: ``<path>/index.md`` and ``<path>.md``.

The script is deliberately standalone and project-agnostic so another Zensical
project can adopt it by copying this one file, installing ``beautifulsoup4`` and
``markdownify``, and adding one post-build command. Project-specific exclusions,
frontmatter guidance, and the large-page canary are supplied as CLI options.

Usage::

    python emit_agent_markdown.py --site-dir=site \
        --exclude=pages/visual-only/index.html \
        --canary=pages/API-reference/models/index.html \
        --agent-docs="Index: https://example.com/llms.txt"

    python emit_agent_markdown.py --site-dir=site --check [same options]
"""
# ruff: noqa: T201

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from markdownify import ATX, MarkdownConverter

ARTICLE_SELECTOR = "article.md-content__inner"
REMOVE_SELECTORS = (
    ".headerlink",
    "a[id^=__codelineno]",
    ".md-clipboard",
    ".md-source-file",
    ".md-content__button",
    ".md-feedback",
    ".PyCafe-launch-button",
)
RAW_HTML_RE = re.compile(
    r"</?(?:a|article|aside|blockquote|br|button|code|details|div|em|figure|footer|form|h[1-6]|header|"
    r"hr|i|iframe|img|input|label|li|main|nav|ol|p|pre|script|section|small|span|strong|style|summary|"
    r"table|tbody|td|th|thead|tr|ul)\b[^>]*>",
    flags=re.IGNORECASE,
)
FENCED_CODE_RE = re.compile(r"```.*?```", flags=re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class Config:
    """Project-specific settings for generation and validation."""

    site_dir: Path
    excluded_pages: frozenset[Path] = frozenset()
    canary_page: Path | None = None
    canary_min_chars: int = 10_000
    agent_docs: str | None = None


class AgentMarkdownConverter(MarkdownConverter):
    """Markdown converter that retains Mermaid's language marker."""

    def convert_pre(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        if "mermaid" in el.get("class", []):
            return f"\n```mermaid\n{el.get_text().strip()}\n```\n"
        return super().convert_pre(el, text, parent_tags)


def _metadata(soup: BeautifulSoup, html_path: Path) -> tuple[str, str, str]:
    heading = soup.select_one(f"{ARTICLE_SELECTOR} h1")
    description = soup.select_one('meta[name="description"]')
    canonical = soup.select_one('link[rel="canonical"]')
    if not heading or not canonical or not canonical.get("href"):
        raise ValueError(f"{html_path}: expected an article heading and canonical URL")
    return (
        heading.get_text(" ", strip=True),
        description.get("content", "") if description else "",
        str(canonical["href"]),
    )


def _canonicalize_links(article: Tag, source_url: str) -> None:
    for element in article.select("[title]"):
        # Autorefs stores a large HTML tooltip in ``title``. Markdownify turns
        # that into a Markdown link title, leaking raw HTML into the result.
        del element["title"]
    for element, attribute in (
        *((element, "href") for element in article.select("[href]")),
        *((element, "src") for element in article.select("[src]")),
    ):
        value = element.get(attribute)
        if value and not value.startswith(("data:", "mailto:", "tel:")):
            element[attribute] = urljoin(source_url, value)


def html_to_markdown(html_path: Path, agent_docs: str | None = None) -> str:
    """Convert one built HTML documentation page to agent-facing Markdown."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    title, description, source_url = _metadata(soup, html_path)
    article = soup.select_one(ARTICLE_SELECTOR)
    if not isinstance(article, Tag):  # Kept separate from _metadata for type narrowing.
        raise ValueError(f"{html_path}: expected exactly one documentation article")

    for selector in REMOVE_SELECTORS:
        for element in article.select(selector):
            element.decompose()
    _canonicalize_links(article, source_url)

    body = AgentMarkdownConverter(heading_style=ATX, bullets="-").convert_soup(article).strip()
    frontmatter = (
        "---\n"
        f"title: {json.dumps(title, ensure_ascii=False)}\n"
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        f"source_url: {json.dumps(source_url)}\n"
    )
    if agent_docs:
        frontmatter += f"agent_docs: {json.dumps(agent_docs)}\n"
    frontmatter += "---"
    return f"{frontmatter}\n\n{body}\n"


def markdown_paths(html_path: Path, site_dir: Path) -> tuple[Path, ...]:
    """Return the two candidate Markdown paths for a built index page."""
    directory_shape = html_path.with_suffix(".md")
    if html_path.name != "index.html" or html_path.parent == site_dir:
        return (directory_shape,)
    suffix_shape = html_path.parent.with_suffix(".md")
    return (directory_shape, suffix_shape)


def documentation_pages(config: Config) -> list[Path]:
    """Find built documentation pages by their canonical URL marker."""
    pages = []
    for html_path in sorted(config.site_dir.rglob("*.html")):
        if html_path.relative_to(config.site_dir) in config.excluded_pages:
            continue
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        if soup.select_one('link[rel="canonical"]'):
            pages.append(html_path)
    return pages


def emit_markdown(config: Config, pages: list[Path] | None = None) -> list[Path]:
    """Generate Markdown twins and return all written paths."""
    written = []
    for html_path in pages if pages is not None else documentation_pages(config):
        markdown = html_to_markdown(html_path, agent_docs=config.agent_docs)
        for output_path in markdown_paths(html_path, config.site_dir):
            output_path.write_text(markdown, encoding="utf-8")
            written.append(output_path)
    return written


def _content_without_code(markdown: str) -> str:
    return INLINE_CODE_RE.sub("", FENCED_CODE_RE.sub("", markdown))


def check_markdown(config: Config, pages: list[Path] | None = None) -> list[str]:
    """Return validation failures for generated Markdown twins."""
    failures = []
    for html_path in pages if pages is not None else documentation_pages(config):
        for markdown_path in markdown_paths(html_path, config.site_dir):
            if not markdown_path.is_file():
                failures.append(f"missing Markdown twin: {markdown_path}")
                continue
            markdown = markdown_path.read_text(encoding="utf-8")
            prose = _content_without_code(markdown)
            if RAW_HTML_RE.search(prose):
                failures.append(f"raw HTML outside code: {markdown_path}")
            if "__codelineno" in markdown:
                failures.append(f"code-line anchor leaked into: {markdown_path}")
            if "Skip to content" in prose:
                failures.append(f"navigation text leaked into: {markdown_path}")

    if config.canary_page:
        canary_markdown = config.site_dir / config.canary_page.with_suffix(".md")
        if (
            not canary_markdown.is_file()
            or len(canary_markdown.read_text(encoding="utf-8")) < config.canary_min_chars
        ):
            failures.append(f"Canary page is missing or unexpectedly empty: {canary_markdown}")
    return failures


def main() -> int:
    """Parse arguments, emit Markdown unless checking, and validate the result."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--site-dir", default="site", type=Path, help="Built documentation directory (default: site).")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        type=Path,
        help="HTML path relative to site-dir to exclude; repeat for multiple paths.",
    )
    parser.add_argument(
        "--canary",
        type=Path,
        help="HTML path relative to site-dir whose Markdown twin must exceed --canary-min-chars.",
    )
    parser.add_argument(
        "--canary-min-chars",
        default=10_000,
        type=int,
        help="Minimum generated size for the canary page (default: 10000).",
    )
    parser.add_argument("--agent-docs", help="Optional agent guidance included in each generated file's frontmatter.")
    parser.add_argument("--check", action="store_true", help="Validate existing Markdown without regenerating it.")
    args = parser.parse_args()

    if not args.site_dir.is_dir():
        print(f"ERROR: {args.site_dir} not found. Run after `zensical build` from the docset directory.")
        return 1

    config = Config(
        site_dir=args.site_dir,
        excluded_pages=frozenset(args.exclude),
        canary_page=args.canary,
        canary_min_chars=args.canary_min_chars,
        agent_docs=args.agent_docs,
    )
    pages = documentation_pages(config)
    if not args.check:
        written = emit_markdown(config, pages)
        print(f"Generated {len(written)} Markdown files from {len(pages)} HTML pages.")

    failures = check_markdown(config, pages)
    if failures:
        print("ERROR: agent-facing Markdown validation failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("Agent-facing Markdown validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
