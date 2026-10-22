
<a id='changelog-0.1.1'></a>
# 0.1.1 — 2026-10-21

## Removed

- Drop support for Python 3.10. ([#1888](https://github.com/mckinsey/vizro/pull/1888))

## Added

- Added an `llms.txt` index of the documentation, advertised from the docs home page and via a machine-readable `<link>` tag in every page's `<head>`. ([#1762](https://github.com/mckinsey/vizro/pull/1762))

- Add support for Python 3.15. ([#1888](https://github.com/mckinsey/vizro/pull/1888))

## Changed

- Update component introspection for the Vizro 1.0.0 API: the removed `AgGrid` model is no longer referenced (`Table` covers AG Grid). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

<a id='changelog-0.1.0'></a>
# 0.1.0 — 2026-06-18

## Added

- Initial release of `vizro-experimental` with the `Chat` component, `ChatAction` and `StreamingChatAction` for plugging in response generators, and the built-in chat popup (`add_chat_popup`). ([#1705](https://github.com/mckinsey/vizro/pull/1705))
