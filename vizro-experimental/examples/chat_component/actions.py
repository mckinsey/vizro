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
            Generated text response.

        """
        if Anthropic is None:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
        client = Anthropic()
        api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=api_messages,
        )
        return "".join(block.text for block in response.content if getattr(block, "type", None) == "text")


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
    ) -> html.Div | html.P:
        """Generate data visualization using VizroAI.

        Args:
            messages: Parsed history (``role`` and ``content`` per item).
            uploaded_files: List of uploaded file dicts with 'content' and 'filename' keys.

        Returns:
            Dash component containing the generated visualization or error message.

        """
        if chart_agent is None:
            return html.P(
                "vizro-ai not installed. Install with: pip install vizro-ai",
                style={"color": "red"},
            )

        prompt = messages[-1]["content"] if messages else ""

        if not uploaded_files:
            return html.P("Please upload a data file first!", style={"color": "#1890ff"})

        # Get the first uploaded file
        uploaded_data = uploaded_files[0]["content"]
        uploaded_filename = uploaded_files[0]["filename"]

        # Parse the raw file contents (base64 encoded from dcc.Upload)
        try:
            _content_type, content_string = uploaded_data.split(",")
            decoded = base64.b64decode(content_string)

            if uploaded_filename and uploaded_filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(decoded))
            elif uploaded_filename and uploaded_filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return html.P(
                    f"Unsupported file type: {uploaded_filename}. Please upload CSV or Excel files.",
                    style={"color": "red"},
                )
        except Exception:
            logger.exception("Error parsing uploaded file")
            return html.P("Error parsing file. Please check the file format and try again.", style={"color": "red"})

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
            return html.P("Error generating visualization. Please try a different prompt.", style={"color": "red"})


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
    ) -> str | html.P:
        """Generate response using OpenAI Vision API with images.

        Args:
            messages: Parsed history (``role`` and ``content`` per item).
            uploaded_files: List of uploaded file dicts with 'content' and 'filename' keys.

        Returns:
            Generated text response or error message component.

        """
        raw_prompt = messages[-1]["content"] if messages else ""
        prompt = raw_prompt if isinstance(raw_prompt, str) else str(raw_prompt)

        content = [{"type": "input_text", "text": prompt}]

        if uploaded_files:
            for file_info in uploaded_files:
                data = file_info["content"]
                filename = file_info["filename"]

                # supported image file types: https://platform.openai.com/docs/guides/images-vision#analyze-images
                is_image = any(filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"])

                if is_image:
                    # data is already base64 encoded from dcc.Upload (format: "data:image/png;base64,...")
                    content.append(
                        {
                            "type": "input_image",
                            "image_url": data,  # Pass the full data URL
                        }
                    )

        # Build API messages (exclude the last message since we'll add it with images)
        api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages[:-1]]
        api_messages.append({"role": "user", "content": content})

        try:
            response = self.client.responses.create(
                model=self.model,
                input=api_messages,
                instructions="You are a helpful assistant that can analyze images and answer questions about them.",
                store=False,
            )
            return response.output_text

        except Exception:
            logger.exception("Error calling OpenAI Vision API")
            return html.P("Error processing your request. Please try again.", style={"color": "red"})


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

        Args:
            messages: Parsed history (``role`` and ``content`` per item).
            uploaded_files: List of uploaded file dicts with 'content' and 'filename' keys.

        Yields:
            Text chunks from the streaming response.

        """
        raw_prompt = messages[-1]["content"] if messages else ""
        prompt = raw_prompt if isinstance(raw_prompt, str) else str(raw_prompt)

        content = [{"type": "input_text", "text": prompt}]

        if uploaded_files:
            for file_info in uploaded_files:
                data = file_info["content"]
                filename = file_info["filename"]

                is_image = any(filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"])

                if is_image:
                    content.append(
                        {
                            "type": "input_image",
                            "image_url": data,
                        }
                    )

        # Build API messages (exclude the last message since we'll add it with images)
        api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages[:-1]]
        api_messages.append({"role": "user", "content": content})

        try:
            response = self.client.responses.create(
                model=self.model,
                input=api_messages,
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
