# vizro-experimental

## Purpose

`vizro-experimental` is the incubation home for large Vizro features that aren't
ready for `vizro-core` yet. Good fits: features like the chat component, or
alternative app layouts — work that spans multiple models/actions, introduces
new runtime concepts, or needs several releases to stabilise. Poor fit: a single
new chart, form input, or small utility — those belong directly in `vizro-core`.

Every feature here is opt-in, API-unstable, and expected to graduate to
`vizro-core` (or be removed) once it matures. Users install with
`pip install vizro-experimental` and import per-feature:

```python
from vizro_experimental.chat import Chat, ChatAction, StreamingChatAction
from vizro_experimental.chat.popup import add_chat_popup
```

The package follows the same Hatch-based dev workflow as the rest of the
monorepo. See the root `CLAUDE.md` for the common commands (`hatch run lint`,
`hatch run test-unit`, `hatch run changelog:add`, etc.). Feature-specific
scripts:

- `hatch run example` — runs `examples/scratch_dev/app.py` (per-PR sandbox).
- `hatch run example chat_component` — runs the Chat demo.
- `hatch run example popup` — runs the floating-popup demo.

### Test prerequisites

`hatch run test-integration-browser` self-installs the Chromium binary
Playwright needs (`~/.cache/ms-playwright/`, ~150 MB on first run, instant
afterwards). LLM integration tests (`tests/integration/llm/`) and the
benchmark suite (`tests/benchmark/`) need an `OPENAI_API_KEY` (and
optionally `ANTHROPIC_API_KEY` for the Claude action) and skip themselves
otherwise.

## Adding a new feature

Each feature is a self-contained subpackage that mirrors the `vizro-core`
layout in miniature, so graduation is a mechanical move.

1. **Create the feature package** under `src/vizro_experimental/<feature>/`
   with the same internal shape as `chat/`:

   ```
   <feature>/
   ├── __init__.py          # re-exports the public API for `from vizro_experimental.<feature> import …`
   ├── _constants.py        # private constants (mirrors vizro/_constants.py)
   ├── models/              # mirrors vizro/models/
   │   ├── __init__.py
   │   ├── <feature>.py     # the main VizroBaseModel(s)
   │   └── types.py         # feature-local types (mirrors vizro.models.types)
   ├── actions/             # mirrors vizro/actions/ (only if the feature defines actions)
   │   ├── __init__.py
   │   └── …
   └── …                    # feature-specific subpackages (e.g. chat/popup/) as needed
   ```

   Don't leave loose files at `<feature>/` root alongside `models/` / `actions/`;
   put them in `_constants.py` or a feature-local subpackage.

2. **Don't cross-import** between features (`<feature_a>/` must not import from
   `<feature_b>/`). If two features need to share real code, extract it to
   `src/vizro_experimental/_shared/` — or graduate it to `vizro-core` first.

3. **Static assets**: drop CSS/JS into the shared `src/vizro_experimental/static/`
   with a feature prefix (e.g. `static/css/<feature>.css`), and register the
   new paths in `src/vizro_experimental/__init__.py` under `_css_dist` /
   `_js_dist`. There is one Dash `ComponentRegistry` namespace for the whole
   package — don't add another.

4. **Package `__init__.py` stays thin**: it only registers Dash assets and
   declares `__version__`. Do **not** re-export feature symbols at the
   `vizro_experimental` top level; users import per feature.

5. **Heavy / optional dependencies**: add a new extras group in
   `pyproject.toml` (e.g. `[project.optional-dependencies] <feature> = [...]`)
   and wire it into `[envs.default] features = [...]` in `hatch.toml` so the
   dev env installs it by default.

6. **Tests**: add `tests/unit/<feature>/`, and — if applicable —
   `tests/integration/<feature>/browser/` and `tests/integration/<feature>/llm/`.
   Mark LLM tests so they skip without an API key; mark long-running perf
   tests with `@pytest.mark.benchmark` (already configured to skip by default).

7. **Examples**: add `examples/<feature>/app.py` (plus any reference helpers,
   e.g. `examples/chat_component/actions.py`). Leave `examples/scratch_dev/`
   as the shared per-PR sandbox — do *not* create `examples/<feature>/scratch/`.

8. **Docs**: add a sibling top-level group in `zensical.toml`'s `nav` (next to
   `Chat`) — only the feature group becomes a horizontal nav tab. Each feature
   owns its full doc subtree under `docs/pages/<feature>/`: how-to guides as
   individual pages plus an `api-reference.md` (mkdocstrings renders from
   docstrings). Inside the tab, the sidebar should have a `How-to guides`
   group and an `API reference` entry. If the feature has a *sub-feature* with
   meaningfully different concepts (like Chat → "Chat component" vs.
   "Chat popup"), nest one more level: each sub-feature gets its own sidebar
   group with its own how-to(s) and API reference (e.g.
   `popup-api-reference.md`). Don't promote sub-features to top-level tabs —
   keep one tab per feature so the horizontal nav stays scannable. The
   grouping makes `vizro-experimental` scale to many features without one
   section dominating the sidebar — and a feature's whole docs subtree moves
   cleanly when it graduates to `vizro-core`.

9. **Changelog**: `hatch run changelog:add` and write an `### Added` entry.

## Graduating a feature to vizro-core

When a feature stabilises, promote it to `vizro-core`:

- `<feature>/models/*.py` → `vizro-core/src/vizro/models/_components/` (or wherever fits).
- `<feature>/actions/*.py` → `vizro-core/src/vizro/actions/`.
- `<feature>/_constants.py` contents → merge into `vizro-core/src/vizro/_constants.py` or inline at callers.
- Static assets → `vizro-core/src/vizro/static/`.
- Tests, examples, docs → corresponding `vizro-core/` locations.
- Delete the feature folder and its extras group / docs nav / examples folder here, and note the removal under `### Removed` in the changelog.
