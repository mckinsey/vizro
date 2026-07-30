# vizro-experimental

Incubation home for large Vizro features that aren't ready for `vizro-core` yet. Good fits: work spanning multiple models/actions, new runtime concepts, or features needing several releases to stabilise. Every feature here is opt-in, API-unstable, and expected to graduate to `vizro-core` or be removed.

Users install with `pip install vizro-experimental` and import per feature:

```python
from vizro_experimental.chat import Chat, ChatAction, StreamingChatAction
from vizro_experimental.chat.popup import add_chat_popup
```

## Development

Same Hatch workflow as the rest of the monorepo (see root `CLAUDE.md` for `hatch run lint`, `hatch run test-unit`, `hatch run changelog:add`). Feature-specific scripts:

- `hatch run example` runs `examples/scratch_dev/app.py` (per-PR sandbox).
- `hatch run example chat_component` runs the Chat demo.
- `hatch run example popup` runs the floating-popup demo.

`hatch run test-integration-browser` self-installs the Chromium binary Playwright needs (~150 MB on first run). LLM integration tests (`tests/integration/llm/`) and benchmarks (`tests/benchmark/`) skip themselves without `OPENAI_API_KEY` (and optionally `ANTHROPIC_API_KEY`).

## Adding a new feature

Each feature is a self-contained subpackage that mirrors the `vizro-core` layout in miniature, so graduation is a mechanical move.

1. **Create the feature package** under `src/vizro_experimental/<feature>/`, mirroring `chat/`: `__init__.py`, `_constants.py`, `models/`, `actions/` (if any), and feature-specific subpackages. No loose files at the feature root.
2. **Don't cross-import** between features. Shared code goes in `src/vizro_experimental/_shared/`, or graduate it to `vizro-core` first.
3. **Static assets** go in `src/vizro_experimental/static/` with a feature prefix (e.g. `static/css/<feature>.css`). Register paths in `src/vizro_experimental/__init__.py` under `_css_dist` / `_js_dist`. One Dash `ComponentRegistry` namespace for the whole package.
4. **Package `__init__.py` stays thin**: registers Dash assets and declares `__version__` only. Do not re-export feature symbols at the top level.
5. **Optional dependencies**: add an extras group in `pyproject.toml` (`[project.optional-dependencies] <feature> = [...]`) and wire it into `[envs.default] features = [...]` in `hatch.toml`.
6. **Tests**: `tests/unit/<feature>/` and, if applicable, `tests/integration/<feature>/browser/` and `tests/integration/<feature>/llm/`. LLM tests skip without an API key; perf tests use `@pytest.mark.benchmark` (skip by default).
7. **Examples**: `examples/<feature>/app.py` plus any reference helpers. Leave `examples/scratch_dev/` as the shared per-PR sandbox; do not create `examples/<feature>/scratch/`.
8. **Docs**: add a top-level group in `zensical.toml`'s `nav` (one tab per feature). Each feature owns `docs/pages/<feature>/` with a `How-to guides` group and an `API reference` entry. Sub-features (Chat -> "Chat component" vs. "Chat popup") nest one level deeper inside the same tab; do not promote them to top-level tabs.
9. **Changelog**: `hatch run changelog:add` and write an `### Added` entry.

## Graduating a feature to vizro-core

- `<feature>/models/*.py` -> `vizro-core/src/vizro/models/_components/` (or wherever fits).
- `<feature>/actions/*.py` -> `vizro-core/src/vizro/actions/`.
- `<feature>/_constants.py` contents merge into `vizro-core/src/vizro/_constants.py` or inline at callers.
- Static assets -> `vizro-core/src/vizro/static/`.
- Tests, examples, docs -> corresponding `vizro-core/` locations.
- Delete the feature folder, its extras group, the docs nav tab, and the examples folder. Note the removal under `### Removed` in the changelog.
