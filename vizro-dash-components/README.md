# vizro-dash-components

Custom Dash components for Vizro with enhanced functionality.

## Overview

This package provides custom Dash components for the Vizro framework. The first component is `Markdown`, which renders markdown content with syntax highlighting for code blocks using Mantine's CodeHighlight.

## Installation

```bash
pip install vizro-dash-components
```

## Usage

````python
from dash import Dash
from vizro_dash_components import Markdown

app = Dash(__name__)

app.layout = Markdown(
    id="my-markdown",
    children="""
    # Hello World

    ```python
    print("Hello, World!")
    ```
    """,
)

if __name__ == "__main__":
    app.run(debug=True)
````

## Components

### Markdown

A Markdown component that renders markdown content with syntax highlighting for code blocks using Mantine CodeHighlight.

#### Props

| Prop                     | Type           | Default | Description                                                |
| ------------------------ | -------------- | ------- | ---------------------------------------------------------- |
| `id`                     | string         | -       | The ID used to identify this component in Dash callbacks   |
| `children`               | string or list | -       | A markdown string (or array of strings) to render          |
| `className`              | string         | -       | Class name of the container element                        |
| `style`                  | object         | -       | A style object for the container element                   |
| `dedent`                 | boolean        | `true`  | Remove matching leading whitespace from all lines          |
| `dangerously_allow_html` | boolean        | `false` | Allow raw HTML in markdown                                 |
| `link_target`            | string         | -       | Target attribute for links                                 |
| `mathjax`                | boolean        | `false` | Enable LaTeX math rendering (uses MathJax)                 |
| `highlight_config`       | object         | -       | Config options for syntax highlighting (`{theme: 'dark'}`) |

#### Features

- Full markdown support via react-markdown
- Syntax highlighting for code blocks with copy button (via @mantine/code-highlight)
- LaTeX math rendering with MathJax
- HTML parsing with custom component support (dccLink, dccMarkdown, dashMathjax)
- Client-side navigation for `<dccLink>` in HTML blocks
- Automatic dedent of markdown content
- Theme support for code highlighting

> **Note:** For detailed information about implementation differences from the original Dash Markdown, see [IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md).

---

## Architecture

This component is based on `dcc.Markdown` from Plotly Dash. The only intentional deviation is code highlighting, which uses `@mantine/code-highlight` (with built-in copy button) instead of the original `highlight.js` approach. All other features — MathJax math rendering, HTML parsing, internal link support, theme support — use the same logic as the original.

### Key Differences from dcc.Markdown

| Feature           | dcc.Markdown                            | vizro Markdown                           |
| ----------------- | --------------------------------------- | ---------------------------------------- |
| Code highlighting | highlight.js (DOM manipulation)         | @mantine/code-highlight (React)          |
| Copy button       | None                                    | Built-in with CodeHighlight              |
| Math rendering    | MathJax (lazy-loaded via webpack chunk) | MathJax (bundled synchronously)          |
| react-markdown    | v4.3.1                                  | v4.3.1 (same)                            |
| Internal links    | `<DccLink>` component import            | Inline pushState routing (same behavior) |

For a comprehensive explanation of all deviations and their reasons, see [IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md).

### Project Structure

```
vizro_dash_components/
├── src/ts/
│   ├── components/
│   │   └── Markdown.tsx              # Main Dash component wrapper
│   ├── fragments/
│   │   ├── Markdown.react.js         # Core markdown renderer (modified from dcc)
│   │   ├── Math.react.js             # Math/LaTeX support (from dcc)
│   │   └── markdownPropTypes.js      # Shared propTypes and defaultProps
│   ├── utils/
│   │   ├── LoadingElement.js         # Loading state wrapper (from dcc)
│   │   └── mathjax.js                # MathJax import and loader
│   ├── props.ts                      # Dash props type definitions
│   └── index.ts                      # Entry point
├── vizro_dash_components/            # Generated Python package (after build)
│   ├── __init__.py
│   ├── _imports_.py
│   ├── Markdown.py                   # Auto-generated Python bindings
│   └── vizro_dash_components.js      # Bundled JavaScript
├── package.json
├── webpack.config.js
├── tsconfig.json
├── setup.py
├── usage.py                          # Test script
└── IMPLEMENTATION_NOTES.md           # Deviation documentation
```

### Source Files

The following files were copied from [plotly/dash](https://github.com/plotly/dash/tree/dev/components/dash-core-components) and modified:

1. **`src/ts/fragments/Markdown.react.js`** (modified from dcc)

    - Replaced `MarkdownHighlighter` / `highlightCode()` with Mantine CodeHighlight
    - Replaced `DccLink` import with inline pushState routing
    - Imports propTypes from shared `markdownPropTypes.js` (see deviation comment)
    - All other logic (dedent, regexMath, componentTransforms, className, renderers) is identical

1. **`src/ts/fragments/Math.react.js`** (from dcc, minor change)

    - Import path updated to `../utils/mathjax` (original: `../utils/LazyLoader/mathjax`)
    - All rendering logic is identical

1. **`src/ts/utils/LoadingElement.js`** (copied from dcc, no changes)

    - Loading state wrapper for Dash components

1. **`src/ts/utils/mathjax.js`** (merged from dcc's two files)

    - Merges original `utils/mathjax.js` and `utils/LazyLoader/mathjax.js`
    - Imports MathJax synchronously instead of lazy-loading (see deviation comment)

1. **`src/ts/fragments/markdownPropTypes.js`** (new, extracted from dcc)

    - Shared propTypes/defaultProps to avoid circular dependency (see deviation comment)

All deviations from the original are marked with `DEVIATION FROM ORIGINAL DCC` comments in the source.

---

## Development

### Prerequisites

- Node.js (see `.nvmrc` for version)
- Python 3.10+
- npm

### Getting Started

1. Create and activate a Python environment:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    ```

1. Install Python dependencies (includes `dash[dev]` for `dash-generate-components`):

    ```bash
    pip install -r requirements.txt
    ```

1. Install npm packages:

    ```bash
    npm install
    ```

1. Build (**venv must be activated** for `dash-generate-components` to work):

    ```bash
    source .venv/bin/activate  # ensure venv is active
    npm run build
    ```

1. Install locally for testing:

    ```bash
    pip install -e .
    ```

1. Test:

    ```bash
    python usage.py
    ```

> **Important:** The `npm run build` command calls `dash-generate-components` which is part of `dash[dev]`. The Python virtual environment must be activated before running the build.

### Build Commands

| Command                  | Description                         |
| ------------------------ | ----------------------------------- |
| `npm run build`          | Build JS + generate Python bindings |
| `npm run build:js`       | JavaScript bundle only              |
| `npm run build:backends` | Python bindings only                |
| `npm run watch`          | Watch mode (rebuild on changes)     |

### Dependencies

#### JavaScript (npm)

- `@mantine/code-highlight` - Syntax highlighting component with copy button
- `@mantine/core` - Mantine core components (provides MantineProvider)
- `@mantine/hooks` - Mantine React hooks
- `react-markdown@4.3.1` - Markdown parser (same version as original dcc)
- `remark-math@3.0.1` - Math syntax parsing (same version as original dcc)
- `mathjax` - MathJax math typesetting
- `react-jsx-parser` - JSX parsing in HTML blocks
- `ramda` - Functional utilities
- `prop-types` - React prop types
- `highlight.js` - Syntax highlighting engine (Mantine peer dependency)
- `path-browserify` (dev) - Webpack 5 polyfill for Node.js `path` module
- `process` (dev) - Webpack 5 polyfill for Node.js `process` global

#### Python

- `dash[dev]>=3.0.0` - Required for building (includes dash-generate-components)

---

## Publishing

### Create a production build

1. Clean up:

    ```bash
    rm -rf dist build
    ```

1. Build:

    ```bash
    npm install
    npm run build
    ```

1. Build source distribution:

    ```bash
    npm run dist
    ```

1. Test locally:

    ```bash
    pip install vizro_dash_components-<version>.tar.gz
    ```

1. Publish to PyPI:

    ```bash
    twine upload dist/*
    ```

---

## License

Apache-2.0
