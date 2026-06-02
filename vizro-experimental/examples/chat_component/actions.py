"""Reference chat-action implementations for the Vizro Chat component.

These are *examples*, not part of the supported library API: copy a class into your
own project and adapt it. They live under ``examples/chat_component/`` rather than
the package source for that reason — they pull in optional LLM-provider SDKs that
shouldn't be on the package import path.
"""

from __future__ import annotations

import base64
import io
import logging
from collections.abc import Iterator
from typing import Any

import dash_mantine_components as dmc
import pandas as pd
import vizro.plotly.express as px
from dash import dcc, html
from pydantic import Field

# Optional dependencies - only imported when needed
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment, misc]

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None  # type: ignore[assignment, misc]

try:
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider
    from vizro_ai.agents import chart_agent
except ImportError:
    OpenAIChatModel = None  # type: ignore[assignment, misc]
    OpenAIProvider = None  # type: ignore[assignment, misc]
    chart_agent = None  # type: ignore[assignment, misc]

from vizro_experimental.chat import ChatAction, Message, StreamingChatAction
from vizro_experimental.chat._constants import COLOR_TEXT_SECONDARY, PLOT_HEIGHT, PLOT_WIDTH

logger = logging.getLogger(__name__)

# Supported by https://platform.openai.com/docs/guides/images-vision#analyze-images
_VISION_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def _is_vision_image(filename: str) -> bool:
    return filename.lower().endswith(_VISION_IMAGE_EXTS)


def _most_recent_user_attachments(messages: list[Message]) -> list[dict[str, str]]:
    """Walk history newest-first and return the most recent user turn's attachments.

    Use this when the upload is a *singleton parameter* (e.g. the CSV for a chart
    agent that takes one ``deps=df``): latest upload wins, earlier uploads are
    intentionally ignored. For *cumulative context* (e.g. vision conversations that
    reference earlier images), use :func:`_build_vision_api_messages` instead.
    """
    for msg in reversed(messages[:-1]):
        if msg["role"] == "user" and msg.get("attachments"):
            return msg["attachments"]
    return []


def _vision_user_content(text: str, attachments: list[dict[str, str]] | None) -> list[dict[str, Any]]:
    """Build the OpenAI vision content blocks for one user turn.

    Always returns a list (a single ``input_text`` block when no images, plus one
    ``input_image`` block per supported image). Used for both the current turn
    (images from the file-store) and historical turns (images snapshotted onto each
    user message's ``attachments`` at send time).
    """
    return [
        {"type": "input_text", "text": text},
        *(
            {"type": "input_image", "image_url": f["content"]}
            for f in (attachments or [])
            if _is_vision_image(f.get("filename", ""))
        ),
    ]


def _build_vision_api_messages(
    messages: list[Message],
    current_uploaded_files: list[dict[str, str]] | None,
) -> list[dict[str, Any]]:
    """Reconstruct the full conversation as OpenAI vision messages.

    Treats uploads as *cumulative context*: every historical user turn re-emits its
    own snapshotted ``attachments`` alongside its original text, so a follow-up like
    "compare the two earlier images" still sees both. The current turn's images come
    from the ``uploaded_files`` kwarg, since they haven't been snapshotted onto
    ``messages[-1]`` by the framework yet. For *singleton-parameter* uploads (e.g.
    a chart agent that only uses the latest CSV), use
    :func:`_most_recent_user_attachments` instead.
    """
    api_messages: list[dict[str, Any]] = []
    for msg in messages[:-1]:
        text = msg["content"] if isinstance(msg["content"], str) else str(msg["content"])
        if msg["role"] == "user":
            api_messages.append({"role": "user", "content": _vision_user_content(text, msg.get("attachments"))})
        else:
            api_messages.append({"role": msg["role"], "content": text})

    last = messages[-1]
    last_text = last["content"] if isinstance(last["content"], str) else str(last["content"])
    api_messages.append({"role": "user", "content": _vision_user_content(last_text, current_uploaded_files)})
    return api_messages


class simple_echo(ChatAction):
    """Simple echo chat that returns the user's message."""

    def generate_response(self, messages: list[Message]) -> str:
        """Echo the user's last message.

        Args:
            messages: Parsed history (``role`` and ``content`` per item).

        Returns:
            Echo of the user's last message.

        """
        last_message = messages[-1]["content"] if messages else ""
        return f"You said: {last_message}"


class openai_streaming_chat(StreamingChatAction):
    """OpenAI streaming chat implementation.

    Args:
        model (str): OpenAI model name. Defaults to `"gpt-4.1-nano"`.

    """

    model: str = Field(default="gpt-4.1-nano", description="OpenAI model name.")

    @property
    def client(self):  # noqa: D102
        if OpenAI is None:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        return OpenAI()

    def generate_response(self, messages: list[Message]) -> Iterator[str]:
        """Generate streaming response from OpenAI.

        Args:
            messages: Parsed history (``role`` and ``content`` per item).

        Yields:
            Text chunks from OpenAI's response.

        """
        api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
        try:
            response = self.client.responses.create(
                model=self.model,
                input=api_messages,
                instructions="Be polite and creative.",
                store=False,
                stream=True,
            )
            for event in response:
                if event.type == "response.output_text.delta":
                    yield event.delta
        except Exception:
            logger.exception("Error calling OpenAI API")
            yield "Error processing your request. Please try again."


class anthropic_non_streaming_chat(ChatAction):
    """Non-streaming implementation for Anthropic Claude chat.

    Args:
        model (str): Anthropic model name. Defaults to `"claude-haiku-4-5-20251001"`.

    """

    model: str = Field(default="claude-haiku-4-5-20251001", description="Anthropic model name.")

    def generate_response(self, messages: list[Message]) -> str:
        """Generate non-streaming response from Anthropic Claude.

        Args:
            messages: Parsed history (``role`` and ``content`` per item).

        Returns:
            Generated text response, or a plain-text error message on failure
            (renders in the normal assistant bubble; matches how ChatGPT / Claude
            surface backend errors in-chat).

        """
        if Anthropic is None:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
        client = Anthropic()
        api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=api_messages,
            )
            return "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
        except Exception:
            logger.exception("Error calling Anthropic API")
            return "Error processing your request. Please try again."


class mixed_content(ChatAction):
    """Example showing different content types: text, chart, and image."""

    def generate_response(self, messages: list[Message]) -> html.Div:
        """Generate a response with mixed content types.

        Args:
            messages: Parsed history (``role`` and ``content`` per item).

        Returns:
            Dash HTML Div containing various Dash components to showcase rendering capabilities.

        """
        prompt = messages[-1]["content"] if messages else ""

        # Sample data for table
        table_data = [
            {"feature": "Streaming", "status": "Supported", "description": "Real-time text generation"},
            {"feature": "File Upload", "status": "Supported", "description": "Images, CSV, Excel files"},
            {"feature": "Code Highlight", "status": "Supported", "description": "Syntax highlighting"},
        ]

        # Create a scatter plot
        fig = px.scatter(
            px.data.iris(),
            x="sepal_width",
            y="sepal_length",
            color="species",
            title="Interactive Plotly Chart",
        )

        # Sample code for CodeHighlight
        sample_code = '''def generate_response(self, messages):
    """Your custom chat logic here."""
    return "Hello, World!"'''

        return html.Div(
            [
                # Introduction
                dcc.Markdown(f'**You said:** "{prompt}"'),
                dmc.Alert(
                    "This demo showcases various Dash components that can be rendered in chat responses!",
                    title="Component Showcase",
                    color="blue",
                    style={"marginTop": "15px", "marginBottom": "15px"},
                ),
                dmc.Table(
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=True,
                    withColumnBorders=True,
                    data={
                        "head": ["Feature", "Status", "Description"],
                        "body": [[row["feature"], row["status"], row["description"]] for row in table_data],
                    },
                    style={"marginBottom": "15px"},
                ),
                # Accordion with expandable sections
                dmc.Accordion(
                    children=[
                        dmc.AccordionItem(
                            value="chart",
                            children=[
                                dmc.AccordionControl("Interactive Chart"),
                                dmc.AccordionPanel(
                                    dcc.Graph(figure=fig, style={"height": PLOT_HEIGHT, "width": PLOT_WIDTH})
                                ),
                            ],
                        ),
                        dmc.AccordionItem(
                            value="code",
                            children=[
                                dmc.AccordionControl("Code Example"),
                                dmc.AccordionPanel(
                                    dmc.CodeHighlight(code=sample_code, language="python", withCopyButton=True)
                                ),
                            ],
                        ),
                        dmc.AccordionItem(
                            value="image",
                            children=[
                                dmc.AccordionControl("Image"),
                                dmc.AccordionPanel(
                                    dmc.Image(
                                        radius="md",
                                        h=200,
                                        w="auto",
                                        fit="contain",
                                        src="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-9.png",
                                    )
                                ),
                            ],
                        ),
                    ],
                    style={"marginBottom": "15px"},
                ),
                # Blockquote
                dmc.Blockquote(
                    "Any Dash component can be rendered in chat responses!",
                    cite="- Vizro Chat Component",
                    color="blue",
                    style={"marginBottom": "15px"},
                ),
            ]
        )


class vizro_ai_chat(ChatAction):
    """Generate data visualizations using natural language with VizroAI.

    File uploads are read from the parent chat's file store when ``uploaded_files`` is declared on
    ``generate_response``; no extra model field is required.

    Args:
        model (str): OpenAI model name. Defaults to `"gpt-4.1-nano"`.

    """

    model: str = Field(default="gpt-4.1-nano", description="OpenAI model name.")

    def generate_response(
        self,
        messages: list[Message],
        uploaded_files: list[dict[str, str]] | None = None,
    ) -> html.Div | str:
        """Generate data visualization using VizroAI.

        Args:
            messages: Parsed history (``role`` and ``content`` per item).
            uploaded_files: List of uploaded file dicts with 'content' and 'filename' keys.

        Returns:
            Dash component containing the generated visualization, or a plain-text
            message that renders in the normal assistant bubble for error / info paths.

        """
        if chart_agent is None:
            return "vizro-ai not installed. Install with: pip install vizro-ai"

        prompt = messages[-1]["content"] if messages else ""

        # Reuse the most recent prior-turn upload on follow-ups so users can ask
        # several chart questions about the same CSV without re-uploading each time
        # (see docs/pages/chat/file-upload.md "Re-attach files on follow-ups").
        files = uploaded_files or _most_recent_user_attachments(messages)
        if not files:
            return "Please upload a data file first!"

        uploaded_data = files[0]["content"]
        uploaded_filename = files[0]["filename"]

        # Parse the raw file contents (base64 encoded from dcc.Upload)
        try:
            _content_type, content_string = uploaded_data.split(",")
            decoded = base64.b64decode(content_string)

            if uploaded_filename and uploaded_filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(decoded))
            elif uploaded_filename and uploaded_filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return f"Unsupported file type: {uploaded_filename}. Please upload CSV or Excel files."
        except Exception:
            logger.exception("Error parsing uploaded file")
            return "Error parsing file. Please check the file format and try again."

        # Generate plot with VizroAI chart_agent
        try:
            # Set up the model using pydantic-ai (reads OPENAI_API_KEY and OPENAI_BASE_URL from env)
            llm_model = OpenAIChatModel(self.model, provider=OpenAIProvider())
            result = chart_agent.run_sync(model=llm_model, user_prompt=prompt, deps=df)
            figure = result.output.chart_function(df)

            return html.Div(
                [
                    dcc.Graph(figure=figure, style={"height": PLOT_HEIGHT, "width": PLOT_WIDTH}),
                    html.Details(
                        [
                            html.Summary(
                                "View generated code", style={"cursor": "pointer", "color": COLOR_TEXT_SECONDARY}
                            ),
                            dmc.CodeHighlight(
                                code=result.output.code,
                                language="python",
                                withCopyButton=True,
                            ),
                        ],
                        style={"marginTop": "10px", "width": PLOT_WIDTH},
                    ),
                ],
                style={"width": PLOT_WIDTH},
            )

        except Exception:
            logger.exception("Error generating visualization")
            return "Error generating visualization. Please try a different prompt."


class openai_vision_chat(ChatAction):
    """OpenAI Vision chat for analyzing images with text prompts.

    Uses the OpenAI responses API with input_image content type for vision capabilities.
    Supports multiple image uploads with a text prompt. Uploaded files are bound automatically
    when ``uploaded_files`` is declared on ``generate_response``.

    Args:
        model (str): OpenAI model name. Defaults to `"gpt-4.1-nano"`.

    """

    model: str = Field(default="gpt-4.1-nano", description="OpenAI model name.")

    @property
    def client(self) -> OpenAI:
        """Get OpenAI client instance.

        Returns:
            OpenAI client.

        """
        if OpenAI is None:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        return OpenAI()

    def generate_response(
        self,
        messages: list[Message],
        uploaded_files: list[dict[str, str]] | None = None,
    ) -> str:
        """Generate response using OpenAI Vision API with images.

        Historical images uploaded in earlier turns are re-sent on every follow-up
        so the model can keep answering questions about them. This matches how
        ChatGPT / Claude / Gemini behave. Each repeated image is billed per turn,
        so very long conversations with images attached can get expensive; trim
        history if cost matters.

        Args:
            messages: Parsed history (``role`` and ``content`` per item; user turns may
                carry ``attachments``).
            uploaded_files: List of uploaded file dicts with 'content' and 'filename' keys.

        Returns:
            Generated text response, or a plain-text error message on failure.

        """
        if not messages:
            return ""
        try:
            response = self.client.responses.create(
                model=self.model,
                input=_build_vision_api_messages(messages, uploaded_files),
                instructions="You are a helpful assistant that can analyze images and answer questions about them.",
                store=False,
            )
            return response.output_text
        except Exception:
            logger.exception("Error calling OpenAI Vision API")
            return "Error processing your request. Please try again."


class openai_vision_streaming_chat(StreamingChatAction):
    """OpenAI Vision chat with streaming for analyzing images with text prompts.

    Uses the OpenAI responses API with input_image content type and streaming.
    Supports multiple image uploads with a text prompt. Uploaded files are bound automatically
    when ``uploaded_files`` is declared on ``generate_response``.

    Args:
        model (str): OpenAI model name. Defaults to `"gpt-4.1-nano"`.

    """

    model: str = Field(default="gpt-4.1-nano", description="OpenAI model name.")

    @property
    def client(self) -> OpenAI:
        """Get OpenAI client instance.

        Returns:
            OpenAI client.

        """
        if OpenAI is None:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        return OpenAI()

    def generate_response(
        self,
        messages: list[Message],
        uploaded_files: list[dict[str, str]] | None = None,
    ) -> Iterator[str]:
        """Generate streaming response using OpenAI Vision API with images.

        Historical images uploaded in earlier turns are re-sent on every follow-up
        so the model can keep answering questions about them. This matches how
        ChatGPT / Claude / Gemini behave. Each repeated image is billed per turn,
        so very long conversations with images attached can get expensive; trim
        history if cost matters.

        Args:
            messages: Parsed history (``role`` and ``content`` per item; user turns may
                carry ``attachments``).
            uploaded_files: List of uploaded file dicts with 'content' and 'filename' keys.

        Yields:
            Text chunks from the streaming response.

        """
        if not messages:
            return
        try:
            response = self.client.responses.create(
                model=self.model,
                input=_build_vision_api_messages(messages, uploaded_files),
                instructions="You are a helpful assistant that can analyze images and answer questions about them.",
                store=False,
                stream=True,
            )
            for event in response:
                if event.type == "response.output_text.delta":
                    yield event.delta
        except Exception:
            logger.exception("Error calling OpenAI Vision API (streaming)")
            yield "Error processing your request. Please try again."
