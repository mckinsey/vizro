"""Floating chat popup subpackage for Vizro dashboards.

Provides a self-contained, data-aware chat popup that can be added to any Vizro dashboard.
When called without a custom ``generate_response``, the popup auto-discovers datasets
from ``data_manager`` and uses an LLM agent to answer questions.

Example usage::

    from vizro_experimental.chat.popup import add_chat_popup

    app = Vizro()
    app.build(dashboard)

    add_chat_popup(app, title="Analytics Assistant")
    app.run()
"""


def __getattr__(name):
    if name == "add_chat_popup":
        from vizro_experimental.chat.popup.popup import add_chat_popup

        return add_chat_popup
    if name == "create_dashboard_agent":
        from vizro_experimental.chat.popup.dashboard_agent import create_dashboard_agent

        return create_dashboard_agent
    if name == "make_generate_response":
        from vizro_experimental.chat.popup.dashboard_agent import make_generate_response

        return make_generate_response
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "add_chat_popup",
    "create_dashboard_agent",
    "make_generate_response",
]
