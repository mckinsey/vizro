import importlib.util
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).parents[4] / "tools" / "emit_agent_markdown.py"
SPEC = importlib.util.spec_from_file_location("emit_agent_markdown", SCRIPT_PATH)
assert SPEC and SPEC.loader
emit_agent_markdown = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(emit_agent_markdown)


def make_html(
    title="Test page",
    description="Test description",
    body="<p>Useful content.</p>",
    canonical="https://vizro.readthedocs.io/en/stable/pages/test/",
):
    return f"""<!doctype html>
<html>
  <head>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canonical}">
  </head>
  <body>
    <nav>Navigation must not leak</nav>
    <article class="md-content__inner md-typeset"><h1>{title}</h1>{body}</article>
  </body>
</html>
"""


def test_html_to_markdown(tmp_path):
    html_path = tmp_path / "index.html"
    html_path.write_text(
        make_html(
            body="""
<p><a href="../other/" title="<span>tooltip</span>">Other page</a></p>
<p><a href="../normal/" title="Useful title">Normal link</a></p>
<a class="PyCafe-launch-button" href="https://py.cafe/">Run in PyCafe</a>
<pre class="mermaid"><code>graph TD
  A --&gt; B</code></pre>
<div class="language-python highlight"><pre><code>print("Hello")</code></pre></div>
""",
        ),
        encoding="utf-8",
    )

    markdown = emit_agent_markdown.html_to_markdown(html_path, agent_docs="Index: https://example.com/llms.txt")

    assert 'title: "Test page"' in markdown
    assert 'description: "Test description"' in markdown
    assert 'source_url: "https://vizro.readthedocs.io/en/stable/pages/test/"' in markdown
    assert 'agent_docs: "Index: https://example.com/llms.txt"' in markdown
    assert "[Other page](https://vizro.readthedocs.io/en/stable/pages/other/)" in markdown
    assert "Useful title" in markdown
    assert "```mermaid\ngraph TD\n  A --> B\n```" in markdown
    assert '```python\nprint("Hello")\n```' in markdown
    assert "Navigation must not leak" not in markdown
    assert "Run in PyCafe" not in markdown
    assert "<span>" not in markdown


@pytest.mark.parametrize(
    "published_base_url",
    [
        "https://vizro--1857.org.readthedocs.build/en/1857/",
        "https://vizro.readthedocs.io/en/latest/",
        "https://vizro.readthedocs.io/en/0.2.0/",
    ],
)
def test_html_to_markdown_uses_active_published_base_url(tmp_path, published_base_url):
    html_path = tmp_path / "index.html"
    html_path.write_text(
        make_html(
            body=(
                '<a href="../relative/">Relative</a>'
                '<a href="https://vizro.readthedocs.io/en/stable/pages/absolute/">Absolute</a>'
            )
        ),
        encoding="utf-8",
    )
    placeholder = "https://vizro.readthedocs.io/en/stable/"

    markdown = emit_agent_markdown.html_to_markdown(
        html_path,
        agent_docs=f"Index: {placeholder}llms.txt",
        url_placeholder=placeholder,
        published_base_url=published_base_url,
    )

    assert f'source_url: "{published_base_url}pages/test/"' in markdown
    assert f'agent_docs: "Index: {published_base_url}llms.txt"' in markdown
    assert f"[Relative]({published_base_url}pages/relative/)" in markdown
    assert f"[Absolute]({published_base_url}pages/absolute/)" in markdown


def test_emit_and_check_markdown(tmp_path):
    root_page = tmp_path / "index.html"
    root_page.write_text(make_html(), encoding="utf-8")
    canary_page = Path("pages/API-reference/models/index.html")
    models_page = tmp_path / canary_page
    models_page.parent.mkdir(parents=True)
    models_page.write_text(make_html(title="Models", body=f"<p>{'model reference ' * 1000}</p>"), encoding="utf-8")
    excluded_page = Path("pages/visual/index.html")
    visual_page = tmp_path / excluded_page
    visual_page.parent.mkdir(parents=True)
    visual_page.write_text(make_html(title="Visual only"), encoding="utf-8")
    config = emit_agent_markdown.Config(
        site_dir=tmp_path, excluded_pages=frozenset({excluded_page}), canary_page=canary_page
    )

    written = emit_agent_markdown.emit_markdown(config)

    assert written == [
        tmp_path / "index.md",
        tmp_path / "pages/API-reference/models/index.md",
        tmp_path / "pages/API-reference/models.md",
    ]
    assert not visual_page.with_suffix(".md").exists()
    assert "agent_docs:" not in root_page.with_suffix(".md").read_text(encoding="utf-8")
    assert emit_agent_markdown.check_markdown(config) == []


def test_emit_fails_if_documentation_dom_changes(tmp_path):
    html_path = tmp_path / "index.html"
    html_path.write_text(
        '<html><head><link rel="canonical" href="https://example.com/"></head><body>No article</body></html>',
        encoding="utf-8",
    )
    config = emit_agent_markdown.Config(site_dir=tmp_path)

    assert emit_agent_markdown.documentation_pages(config) == [html_path]
    with pytest.raises(ValueError, match="expected an article heading and canonical URL"):
        emit_agent_markdown.emit_markdown(config)


def test_emit_bundle_and_split_models(tmp_path):
    root_page = tmp_path / "index.html"
    root_page.write_text(make_html(title="Home"), encoding="utf-8")
    models_page = tmp_path / "reference/models/index.html"
    models_page.parent.mkdir(parents=True)
    models_page.write_text(
        make_html(
            title="Models",
            canonical="https://example.com/reference/models/",
            body="""
<div class="doc doc-object doc-class">
  <h3 id="example.models.Graph" class="doc doc-heading">
    <span class="doc doc-object-name doc-class-name">Graph</span>
    <span class="doc doc-labels">pydantic-model</span>
  </h3>
  <div class="doc doc-contents"><p>Graph documentation.</p></div>
</div>
""",
        ),
        encoding="utf-8",
    )
    config = emit_agent_markdown.Config(
        site_dir=tmp_path,
        bundle_filename=Path("llms-full.txt"),
        bundle_excluded_prefixes=(Path("reference"),),
        split_models_page=Path("reference/models/index.html"),
        split_models_namespace="example.models",
    )
    pages = emit_agent_markdown.documentation_pages(config)
    emit_agent_markdown.emit_markdown(config, pages)

    bundle_path = emit_agent_markdown.emit_bundle(config, pages)
    model_paths = emit_agent_markdown.emit_model_markdown(config)

    assert bundle_path == tmp_path / "llms-full.txt"
    bundle = bundle_path.read_text(encoding="utf-8")
    assert "Source: https://vizro.readthedocs.io/en/stable/pages/test/" in bundle
    assert "Models" not in bundle
    assert "source_url:" not in bundle
    assert model_paths == [tmp_path / "reference/models/graph.md"]
    model_markdown = model_paths[0].read_text(encoding="utf-8")
    assert 'source_url: "https://example.com/reference/models/#example.models.Graph"' in model_markdown
    assert "# Graph\n\nGraph documentation." in model_markdown
    assert "pydantic-model" not in model_markdown
    assert emit_agent_markdown.check_markdown(config, pages) == []

    bundle_path.write_text(
        bundle.replace(
            "Source: https://vizro.readthedocs.io/en/stable/pages/test/",
            "Source: https://vizro.readthedocs.io/en/stable/pages/test/child/",
        ),
        encoding="utf-8",
    )
    assert any("page missing from bundle" in failure for failure in emit_agent_markdown.check_markdown(config, pages))

    bundle_path.write_text(
        bundle.replace(
            "https://vizro.readthedocs.io/en/stable/",
            "https://vizro--1857.org.readthedocs.build/en/1857/",
        ),
        encoding="utf-8",
    )
    assert emit_agent_markdown.check_markdown(config, pages) == []

    stale_model = models_page.parent / "removed-model.md"
    stale_model.write_text("# Removed model", encoding="utf-8")
    assert any(
        "unexpected stale per-model Markdown" in failure for failure in emit_agent_markdown.check_markdown(config)
    )


def test_split_models_rejects_reserved_index_filename(tmp_path):
    models_page = tmp_path / "reference/models/index.html"
    models_page.parent.mkdir(parents=True)
    models_page.write_text(
        make_html(
            title="Models",
            canonical="https://example.com/reference/models/",
            body="""
<div class="doc doc-object doc-class">
  <h3 id="example.models.Index" class="doc doc-heading">Index</h3>
  <div class="doc doc-contents"><p>Index documentation.</p></div>
</div>
""",
        ),
        encoding="utf-8",
    )
    config = emit_agent_markdown.Config(
        site_dir=tmp_path,
        split_models_page=Path("reference/models/index.html"),
        split_models_namespace="example.models",
    )
    emit_agent_markdown.emit_markdown(config)
    combined_markdown = models_page.with_suffix(".md").read_text(encoding="utf-8")

    with pytest.raises(ValueError, match=r"'index\.md' is reserved"):
        emit_agent_markdown.emit_model_markdown(config)

    assert models_page.with_suffix(".md").read_text(encoding="utf-8") == combined_markdown
    assert any("reserved for the combined page" in failure for failure in emit_agent_markdown.check_markdown(config))


def test_content_without_code_ignores_backticks_inside_fence():
    markdown = """Before
```
{"description": "Example: ```python"}
<div>HTML inside code</div>
```
<aside>HTML outside code</aside>
"""

    prose = emit_agent_markdown._content_without_code(markdown)

    assert "Before" in prose
    assert "HTML inside code" not in prose
    assert "<aside>HTML outside code</aside>" in prose


@pytest.mark.parametrize(
    "bad_content, expected_failure",
    [
        ("<aside>raw HTML</aside>", "raw HTML outside code"),
        ("[line](#__codelineno-0-1)", "code-line anchor leaked"),
        ("Skip to content", "navigation text leaked"),
    ],
)
def test_check_markdown_rejects_unclean_output(tmp_path, bad_content, expected_failure):
    canary_page = Path("pages/API-reference/models/index.html")
    models_page = tmp_path / canary_page
    models_page.parent.mkdir(parents=True)
    models_page.write_text(make_html(title="Models", body=f"<p>{'model reference ' * 1000}</p>"), encoding="utf-8")
    config = emit_agent_markdown.Config(site_dir=tmp_path, canary_page=canary_page)
    emit_agent_markdown.emit_markdown(config)
    models_page.with_suffix(".md").write_text(bad_content, encoding="utf-8")

    assert any(expected_failure in failure for failure in emit_agent_markdown.check_markdown(config))
