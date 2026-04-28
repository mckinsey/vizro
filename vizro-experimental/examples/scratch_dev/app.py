"""Per-PR scratch dashboard for vizro-experimental.

Edit this file freely while working on a PR — contents are expected to churn.
The starter wires a single ``Chat`` page backed by an inline echo action so a
fresh clone can ``hatch run example`` with no API keys.

Run with::

    hatch run example
"""

from typing import Any

import vizro.models as vm
from vizro import Vizro

from vizro_experimental.chat import Chat, ChatAction, Message


class EchoAction(ChatAction):
    """Echo the most recent user message back as the assistant reply."""

    def generate_response(self, messages: list[Message], **_: Any) -> str:
        """Return the last user message verbatim, prefixed with 'You said:'."""
        return f"You said: {messages[-1]['content']}"


vm.Page.add_type("components", Chat)

dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Scratch chat",
            components=[Chat(actions=[EchoAction()])],
        ),
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
