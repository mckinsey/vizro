
<a id='changelog-0.0.1'></a>
# 0.0.1 — 2026-06-18

## Added

- Initial release of `vizro-experimental` with the `Chat` component, `ChatAction` and `StreamingChatAction` for plugging in response generators, and the built-in chat popup (`add_chat_popup`). ([#1705](https://github.com/mckinsey/vizro/pull/1705))

## Changed

- Tighten browser test coverage for the Chat component and chat popup: streaming round-trip, empty/whitespace prompt rejection, popup clear and restore-on-reopen, popup `streaming=False` variant, multi-turn echo conversation, and session-storage restore after reload. ([#1](https://github.com/mckinsey/vizro/pull/1))
