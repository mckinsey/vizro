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
        --bundle=llms-full.txt \
        --bundle-exclude-prefix=pages/API-reference \
        --split-models-page=pages/API-reference/models/index.html \
        --split-models-namespace=vizro.models \
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
    r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>",
    flags=re.IGNORECASE,
)
FENCE_START_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n\n", flags=re.DOTALL)
MODEL_ID_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
RTD_BASE_URL_RE = re.compile(r"https://[^/\s]+(?:/projects/[^/\s]+)?/en/[^/\s]+/")
MIN_MODEL_MARKDOWN_CHARS = 100
MAX_FENCE_INDENT = 3


@dataclass(frozen=True)
class Config:
    """Project-specific settings for generation and validation."""

    site_dir: Path
    excluded_pages: frozenset[Path] = frozenset()
    canary_page: Path | None = None
    canary_min_chars: int = 10_000
    agent_docs: str | None = None
    bundle_filename: Path | None = None
    bundle_excluded_prefixes: tuple[Path, ...] = ()
    split_models_page: Path | None = None
    split_models_namespace: str | None = None


class AgentMarkdownConverter(MarkdownConverter):
    """Markdown converter that retains fenced-code language markers."""

    def convert_pre(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        """Convert highlighted ``pre`` elements to explicitly typed code fences."""
        code = el.find("code", recursive=False)
        candidates = (el.parent, el, code)
        classes = [
            class_name
            for candidate in candidates
            if isinstance(candidate, Tag)
            for class_name in candidate.get("class", [])
        ]
        if "mermaid" in classes:
            return f"\n```mermaid\n{el.get_text().strip()}\n```\n"
        language_class = next((class_name for class_name in classes if class_name.startswith("language-")), None)
        if language_class:
            language = language_class.removeprefix("language-")
            return f"\n```{language}\n{el.get_text().strip()}\n```\n"
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
        title = str(element["title"])
        if "<" in title or ">" in title:
            del element["title"]
    for element, attribute in (
        *((element, "href") for element in article.select("[href]")),
        *((element, "src") for element in article.select("[src]")),
    ):
        value = element.get(attribute)
        if value and not value.startswith(("data:", "mailto:", "tel:")):
            element[attribute] = urljoin(source_url, value)


def _convert_tag(tag: Tag, source_url: str) -> str:
    for selector in REMOVE_SELECTORS:
        for element in tag.select(selector):
            element.decompose()
    _canonicalize_links(tag, source_url)
    return AgentMarkdownConverter(heading_style=ATX, bullets="-").convert_soup(tag).strip()


def _frontmatter(title: str, description: str, source_url: str, agent_docs: str | None) -> str:
    frontmatter = (
        "---\n"
        f"title: {json.dumps(title, ensure_ascii=False)}\n"
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        f"source_url: {json.dumps(source_url)}\n"
    )
    if agent_docs:
        frontmatter += f"agent_docs: {json.dumps(agent_docs)}\n"
    return f"{frontmatter}---"


def html_to_markdown(html_path: Path, agent_docs: str | None = None) -> str:
    """Convert one built HTML documentation page to agent-facing Markdown."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    title, description, source_url = _metadata(soup, html_path)
    article = soup.select_one(ARTICLE_SELECTOR)
    if not isinstance(article, Tag):  # Kept separate from _metadata for type narrowing.
        raise ValueError(f"{html_path}: expected exactly one documentation article")

    body = _convert_tag(article, source_url)
    frontmatter = _frontmatter(title, description, source_url, agent_docs)
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


def _page_source_url(html_path: Path) -> str:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    canonical = soup.select_one('link[rel="canonical"]')
    if not canonical or not canonical.get("href"):
        raise ValueError(f"{html_path}: expected a canonical URL")
    return str(canonical["href"])


def _is_excluded_from_bundle(relative_path: Path, prefixes: tuple[Path, ...]) -> bool:
    return any(relative_path.is_relative_to(prefix) for prefix in prefixes)


def emit_bundle(config: Config, pages: list[Path]) -> Path | None:
    """Concatenate selected generated pages into an ``llms-full.txt``-style bundle."""
    if not config.bundle_filename:
        return None

    bundled_pages = []
    for html_path in pages:
        relative_path = html_path.relative_to(config.site_dir)
        if _is_excluded_from_bundle(relative_path, config.bundle_excluded_prefixes):
            continue
        markdown_path = markdown_paths(html_path, config.site_dir)[0]
        markdown = FRONTMATTER_RE.sub("", markdown_path.read_text(encoding="utf-8"), count=1).strip()
        heading, separator, remainder = markdown.partition("\n")
        source_url = _page_source_url(html_path)
        bundled_pages.append(f"{heading}\n\nSource: {source_url}{separator}{remainder}".strip())

    if not bundled_pages:
        raise ValueError("No documentation pages remain after applying bundle exclusions")

    output_path = config.site_dir / config.bundle_filename
    header = (
        "# Full documentation\n\n"
        "> Consolidated documentation content. See llms.txt for the curated index and API reference links."
    )
    output_path.write_text(f"{header}\n\n---\n\n" + "\n\n---\n\n".join(bundled_pages) + "\n", encoding="utf-8")
    return output_path


def _model_slug(name: str) -> str:
    first_pass = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", first_pass).lower()


def _model_sections(html_path: Path, namespace: str) -> list[tuple[str, str, Tag]]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    sections = []
    for section in soup.select("div.doc.doc-object.doc-class"):
        heading = section.find(["h2", "h3"], class_="doc-heading", recursive=False)
        anchor = str(heading.get("id", "")) if isinstance(heading, Tag) else ""
        prefix = f"{namespace}."
        qualified_name = anchor.removeprefix(prefix)
        if not anchor.startswith(prefix) or "." in qualified_name or not MODEL_ID_RE.fullmatch(qualified_name):
            continue
        sections.append((qualified_name, anchor, section))
    if not sections:
        raise ValueError(f"{html_path}: no top-level {namespace} classes found")
    return sections


def emit_model_markdown(config: Config) -> list[Path]:
    """Split the rendered Models API page into one Markdown file per model."""
    if not config.split_models_page:
        return []
    if not config.split_models_namespace:
        raise ValueError("split_models_namespace is required when split_models_page is configured")

    html_path = config.site_dir / config.split_models_page
    page_url = _page_source_url(html_path)
    output_dir = html_path.parent
    model_sections = _model_sections(html_path, config.split_models_namespace)
    slugs = [_model_slug(model_name) for model_name, _, _ in model_sections]
    if "index" in slugs:
        raise ValueError(f"{html_path}: model filename 'index.md' is reserved for the combined page")
    if len(slugs) != len(set(slugs)):
        raise ValueError(f"{html_path}: duplicate model filename after slug conversion")

    written = []
    for (model_name, anchor, section), slug in zip(model_sections, slugs, strict=True):
        heading = section.find(["h2", "h3"], class_="doc-heading", recursive=False)
        if not isinstance(heading, Tag):
            raise ValueError(f"{html_path}: model {model_name} has no heading")
        heading.name = "h1"
        for label in heading.select(".doc-labels"):
            label.decompose()
        source_url = f"{page_url}#{anchor}"
        body = _convert_tag(section, source_url)
        first_paragraph = section.find("p")
        description = first_paragraph.get_text(" ", strip=True) if isinstance(first_paragraph, Tag) else ""
        markdown = f"{_frontmatter(model_name, description, source_url, config.agent_docs)}\n\n{body}\n"
        output_path = output_dir / f"{slug}.md"
        output_path.write_text(markdown, encoding="utf-8")
        written.append(output_path)
    return written


def _content_without_code(markdown: str) -> str:
    prose_lines = []
    fence_character = ""
    fence_length = 0
    for line in markdown.splitlines():
        if fence_character:
            closing_fence = line.lstrip(" ")
            indentation = len(line) - len(closing_fence)
            closing_candidate = closing_fence.strip()
            if (
                indentation <= MAX_FENCE_INDENT
                and len(closing_candidate) >= fence_length
                and set(closing_candidate) == {fence_character}
            ):
                fence_character = ""
                fence_length = 0
            continue

        match = FENCE_START_RE.match(line)
        if match:
            fence_character = match.group(1)[0]
            fence_length = len(match.group(1))
            continue
        prose_lines.append(line)
    return INLINE_CODE_RE.sub("", "\n".join(prose_lines))


def _check_page_twins(config: Config, documentation: list[Path]) -> list[str]:
    failures = []
    for html_path in documentation:
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
    return failures


def _check_canary(config: Config) -> list[str]:
    if not config.canary_page:
        return []
    canary_markdown = config.site_dir / config.canary_page.with_suffix(".md")
    if not canary_markdown.is_file() or len(canary_markdown.read_text(encoding="utf-8")) < config.canary_min_chars:
        return [f"Canary page is missing or unexpectedly empty: {canary_markdown}"]
    return []


def _check_bundle(config: Config, documentation: list[Path]) -> list[str]:
    if not config.bundle_filename:
        return []
    bundle_path = config.site_dir / config.bundle_filename
    if not bundle_path.is_file():
        return [f"missing documentation bundle: {bundle_path}"]

    failures = []
    bundle = bundle_path.read_text(encoding="utf-8")
    normalized_bundle = RTD_BASE_URL_RE.sub("{docs-base}/", bundle)
    bundle_source_markers = {line for line in normalized_bundle.splitlines() if line.startswith("Source: ")}
    if RAW_HTML_RE.search(_content_without_code(bundle)):
        failures.append(f"raw HTML outside code: {bundle_path}")
    for html_path in documentation:
        relative_path = html_path.relative_to(config.site_dir)
        source_url = _page_source_url(html_path)
        source_marker = RTD_BASE_URL_RE.sub("{docs-base}/", f"Source: {source_url}")
        is_excluded = _is_excluded_from_bundle(relative_path, config.bundle_excluded_prefixes)
        if is_excluded and source_marker in bundle_source_markers:
            failures.append(f"excluded page leaked into bundle: {source_url}")
        elif not is_excluded and source_marker not in bundle_source_markers:
            failures.append(f"page missing from bundle: {source_url}")
    return failures


def _check_model_markdown(config: Config) -> list[str]:
    if not config.split_models_page:
        return []
    if not config.split_models_namespace:
        return ["split_models_namespace is required when split_models_page is configured"]

    failures = []
    models_html = config.site_dir / config.split_models_page
    expected = {
        models_html.parent / f"{_model_slug(model_name)}.md": anchor
        for model_name, anchor, _ in _model_sections(models_html, config.split_models_namespace)
    }
    combined_page = models_html.with_suffix(".md")
    if combined_page in expected:
        return [f"per-model filename is reserved for the combined page: {combined_page}"]
    actual = set(models_html.parent.glob("*.md")) - {combined_page}
    failures.extend(
        f"unexpected stale per-model Markdown: {unexpected_path}"
        for unexpected_path in sorted(actual - expected.keys())
    )
    for model_path, anchor in expected.items():
        if not model_path.is_file():
            failures.append(f"missing per-model Markdown: {model_path}")
            continue
        model_markdown = model_path.read_text(encoding="utf-8")
        if len(model_markdown) < MIN_MODEL_MARKDOWN_CHARS:
            failures.append(f"per-model Markdown is unexpectedly empty: {model_path}")
        if f"#{anchor}" not in model_markdown:
            failures.append(f"source anchor missing from per-model Markdown: {model_path}")
        if RAW_HTML_RE.search(_content_without_code(model_markdown)):
            failures.append(f"raw HTML outside code: {model_path}")
    return failures


def check_markdown(config: Config, pages: list[Path] | None = None) -> list[str]:
    """Return validation failures for all generated agent-facing files."""
    documentation = pages if pages is not None else documentation_pages(config)
    return [
        *_check_page_twins(config, documentation),
        *_check_canary(config),
        *_check_bundle(config, documentation),
        *_check_model_markdown(config),
    ]


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
    parser.add_argument("--bundle", type=Path, help="Write selected pages to this bundle path relative to site-dir.")
    parser.add_argument(
        "--bundle-exclude-prefix",
        action="append",
        default=[],
        type=Path,
        help="Exclude this site-relative HTML path prefix from the bundle; repeat for multiple prefixes.",
    )
    parser.add_argument(
        "--split-models-page",
        type=Path,
        help="Split top-level classes from this site-relative HTML page into sibling Markdown files.",
    )
    parser.add_argument("--split-models-namespace", help="Python namespace rendered by --split-models-page.")
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
        bundle_filename=args.bundle,
        bundle_excluded_prefixes=tuple(args.bundle_exclude_prefix),
        split_models_page=args.split_models_page,
        split_models_namespace=args.split_models_namespace,
    )
    pages = documentation_pages(config)
    if not args.check:
        written = emit_markdown(config, pages)
        print(f"Generated {len(written)} Markdown files from {len(pages)} HTML pages.")
        bundle_path = emit_bundle(config, pages)
        if bundle_path:
            print(f"Generated documentation bundle: {bundle_path}.")
        model_paths = emit_model_markdown(config)
        if model_paths:
            print(f"Generated {len(model_paths)} per-model Markdown files.")

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
