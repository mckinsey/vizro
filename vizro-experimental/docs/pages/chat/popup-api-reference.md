# API reference

The public surface of the [Chat popup](chat-popup.md). For the chat component, see the [Chat component API reference](api-reference.md).

The user-facing import path is `from vizro_experimental.chat.popup import …`. The
`popup` subpackage uses lazy `__getattr__` to defer LangChain imports, which
mkdocstrings cannot statically trace, so the entries below point at the
underlying modules where each symbol is actually defined.

::: vizro_experimental.chat.popup.popup.add_chat_popup
    options:
      show_root_heading: true
      show_source: false

::: vizro_experimental.chat.popup.dashboard_agent.create_dashboard_agent
    options:
      show_root_heading: true
      show_source: false

::: vizro_experimental.chat.popup.dashboard_agent.make_generate_response
    options:
      show_root_heading: true
      show_source: false
