"""Chat Vizro model — renders message history, input, and SSE wiring."""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal

import dash
import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_extensions import SSE
from dash_iconify import DashIconify
from pydantic import BeforeValidator, Field, model_validator
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain

from .._constants import (
    BORDER_RADIUS,
    CSS_BUTTON_ROW,
    CSS_DATA_INFO,
    CSS_EXAMPLE_MENU_DROPDOWN,
    CSS_EXAMPLE_QUESTION_ITEM,
    CSS_HISTORY_CONTAINER,
    CSS_HISTORY_SECTION,
    CSS_INPUT_INNER,
    CSS_INPUT_SECTION,
    CSS_LEFT_BUTTONS,
    CSS_ROOT,
    ICON_BUTTON_SIZE,
)
from ..actions._base_chat_action import _BaseChatAction


def _coerce_chat_actions(value: Any) -> Any:
    """Accept a single action or a list (empty omits validation pass-through for [])."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


class Chat(VizroBaseModel):
    """Chat component for conversational AI interfaces.

    Args:
        type (Literal["chat"]): Defaults to `"chat"`.
        actions (list[_BaseChatAction] | _BaseChatAction): One action or a list of actions. Defaults to `[]`.
        placeholder (str): Placeholder text for the input field. Defaults to `"How can I help you?"`.
        file_upload (bool): Enable file upload functionality. Defaults to `False`.
        example_questions (list[str]): List of example questions to show in a popup menu. Defaults to `[]`.

    """

    type: Literal["chat"] = "chat"
    actions: Annotated[list[_BaseChatAction], BeforeValidator(_coerce_chat_actions)] = Field(
        default_factory=list,
        description="Chat action(s) to handle responses. Pass one action or a list.",
    )
    placeholder: str = Field(default="How can I help you?", description="Placeholder text for the input field.")
    file_upload: bool = Field(default=False, description="Enable file upload functionality.")
    example_questions: list[str] = Field(default=[], description="List of example questions to show in a popup menu.")

    _make_actions_chain = model_validator(mode="after")(make_actions_chain)

    @property
    def _action_triggers(self) -> dict[str, str]:
        """Define action triggers for the chat component.

        Returns:
            Dict mapping trigger names to component property references.

        """
        return {"__default__": f"{self.id}-send-button.n_clicks"}

    @_log_call
    def pre_build(self) -> None:
        """Set up callbacks for example questions during pre-build phase."""
        if self.example_questions:
            self._setup_example_questions_callback()

    def _setup_example_questions_callback(self) -> None:
        """Set up callback to fill chat input when example question is clicked."""
        # Store the questions list for use in the callback
        questions = self.example_questions

        @callback(
            Output(f"{self.id}-chat-input", "value", allow_duplicate=True),
            Input({"type": f"{self.id}-example-question", "index": dash.ALL}, "n_clicks"),
            prevent_initial_call=True,
        )
        def fill_example_question(n_clicks):
            """Fill chat input with the clicked example question."""
            if not n_clicks or not any(n_clicks):
                raise PreventUpdate

            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            # Get the index of the clicked question
            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
            index = json.loads(triggered_id)["index"]

            if 0 <= index < len(questions):
                return questions[index]

            raise PreventUpdate

    def _build_upload_stores(self) -> list[dcc.Store]:
        """Build stores for file upload.

        Returns:
            List of dcc.Store components for file upload state.

        """
        return [dcc.Store(id=f"{self.id}-file-store", storage_type="session")]

    def _build_example_questions_menu(self) -> dmc.Menu:
        """Build the example questions popup menu.

        Returns:
            Dash Mantine Menu component with example questions.

        """
        menu_items = [
            dmc.MenuItem(
                question,
                id={"type": f"{self.id}-example-question", "index": i},
                className=CSS_EXAMPLE_QUESTION_ITEM,
            )
            for i, question in enumerate(self.example_questions)
        ]

        return dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.ActionIcon(
                        [
                            DashIconify(icon="material-symbols-light:chat-outline", width=24, height=24),
                            DashIconify(icon="material-symbols-light:keyboard-arrow-up", width=14, height=14),
                        ],
                        variant="subtle",
                        color="grey",
                        radius=BORDER_RADIUS,
                        style={"width": "48px", "height": ICON_BUTTON_SIZE},
                        id=f"{self.id}-example-questions-button",
                    )
                ),
                dmc.MenuDropdown(
                    menu_items,
                    className=CSS_EXAMPLE_MENU_DROPDOWN,
                ),
            ],
            position="top-start",
            shadow="md",
        )

    def _build_input_area(self) -> html.Div:
        """Build the input area with optional file upload button.

        Returns:
            Dash HTML Div containing the input area components.

        """
        # File upload button
        upload_button = dcc.Upload(
            id=f"{self.id}-upload",
            children=dmc.ActionIcon(
                DashIconify(icon="material-symbols-light:attach-file-add", width=24, height=24),
                variant="subtle",
                color="grey",
                radius=BORDER_RADIUS,
                style={"width": ICON_BUTTON_SIZE, "height": ICON_BUTTON_SIZE},
            ),
            style={"width": "fit-content", "display": "block" if self.file_upload else "none"},
            multiple=True,
        )

        # Example questions menu button
        example_questions_menu = (
            self._build_example_questions_menu() if self.example_questions else html.Div(style={"display": "none"})
        )

        # Build children list explicitly
        inner_children = []

        inner_children.append(html.Div(id=f"{self.id}-data-info", className=CSS_DATA_INFO))

        # Textarea - Mantine components need inline styles for internal styling
        inner_children.append(
            dmc.Textarea(
                id=f"{self.id}-chat-input",
                placeholder=self.placeholder,
                autosize=True,
                size="md",
                minRows=1,
                maxRows=6,
                radius=0,
                styles={
                    "input": {
                        "borderLeft": "none",
                        "borderRight": "none",
                        "borderTop": "none",
                        "borderRadius": "0",
                        "resize": "none",
                        "backgroundColor": "var(--bs-body-bg)",
                        "fontSize": "var(--chat-font-size)",
                        "lineHeight": "var(--chat-line-height)",
                        "color": "var(--text-primary)",
                    }
                },
                style={"width": "100%"},
                value="",
            )
        )

        # Left buttons group (file upload + example questions)
        left_buttons = html.Div(
            [upload_button, example_questions_menu],
            className=CSS_LEFT_BUTTONS,
        )

        # Button row
        inner_children.append(
            html.Div(
                [
                    left_buttons,
                    dmc.ActionIcon(
                        # Send glyph rendered at 32 (vs 24 on peers): the paper-plane only fills
                        # ~75% of its 24-unit viewBox, so equal px reads smaller.
                        DashIconify(
                            icon="material-symbols-light:send-outline",
                            width=32,
                            height=32,
                            id=f"{self.id}-send-icon",
                        ),
                        id=f"{self.id}-send-button",
                        variant="subtle",
                        color="grey",
                        n_clicks=0,
                        radius=BORDER_RADIUS,
                        style={"width": ICON_BUTTON_SIZE, "height": ICON_BUTTON_SIZE},
                    ),
                ],
                className=CSS_BUTTON_ROW,
            )
        )

        return html.Div(
            [
                html.Div(
                    inner_children,
                    className=CSS_INPUT_INNER,
                )
            ],
            className=CSS_INPUT_SECTION,
        )

    @_log_call
    def build(self) -> html.Div:
        """Build the chat component layout.

        Returns:
            Dash HTML Div containing the complete chat interface.

        """
        return html.Div(
            [
                *self._build_upload_stores(),
                # Messages container
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(id=f"{self.id}-hidden-messages", children=[], style={"display": "none"}),
                                html.Div(id=f"{self.id}-rendered-messages", className=CSS_HISTORY_CONTAINER),
                            ],
                            id=f"{self.id}-chat-messages-container",
                        )
                    ],
                    className=CSS_HISTORY_SECTION,
                ),
                # Input area
                self._build_input_area(),
                # Store for conversation history
                dcc.Store(id=f"{self.id}-store", data=[], storage_type="session"),
                # Server-Sent Events for streaming support
                SSE(id=f"{self.id}-sse", concat=True, animate_chunk=10, animate_delay=5),
            ],
            className=CSS_ROOT,
        )
