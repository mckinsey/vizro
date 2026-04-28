"""Example of how to use the Vizro Chat Component with action-based architecture.

Run with::

    hatch run example chat_component
"""

import vizro.models as vm
from actions import (
    anthropic_non_streaming_chat,
    mixed_content,
    openai_streaming_chat,
    openai_vision_streaming_chat,
    simple_echo,
    vizro_ai_chat,
)
from dotenv import load_dotenv
from vizro import Vizro

from vizro_experimental.chat import Chat

load_dotenv()

# Register the Chat component with Vizro Page
vm.Page.add_type("components", Chat)

# Page 1: Simple Echo (no API key required)
page_echo = vm.Page(
    title="Simple Echo (No API Key)",
    components=[
        Chat(actions=simple_echo()),
    ],
)

# Page 2: Example Questions Demo
page_example_questions = vm.Page(
    title="Example Questions",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [1]]),
    components=[
        vm.Card(
            text="""
## Example Questions Demo

This page demonstrates the `example_questions` feature which provides a popup menu
of predefined questions that users can click to fill the input field.

**How to use:**
1. Click the chat icon with arrow (left of the input field)
2. Select a question from the popup menu
3. The input field is automatically filled with the selected question
4. Press send or Enter to submit

**Note:** Requires `OPENAI_API_KEY` and `OPENAI_BASE_URL`.
"""
        ),
        Chat(
            # Explicit id gives the integration test (test_chat_component.py) a stable
            # DOM handle; without it Vizro assigns a random uuid prefix per run.
            id="example_chat",
            placeholder="Ask me anything or select an example...",
            actions=openai_streaming_chat(),
            example_questions=[
                "What is the capital of France?",
                "Explain quantum computing in simple terms",
                "Write a haiku about programming",
                "What are the benefits of TypeScript over JavaScript?",
            ],
        ),
    ],
)

# Page 3: Example Questions + File Upload Combined
page_example_with_upload = vm.Page(
    title="Examples + Upload",
    layout=vm.Grid(grid=[[0, 1, 1, 1]]),
    components=[
        vm.Card(
            text="""
## Example Questions + File Upload

This page demonstrates using both `example_questions` and `file_upload` together.

**How to use:**
1. Click the attachment icon (left) to upload a CSV/Excel file
2. Click the chat icon (middle) to see example prompts for data visualization
3. Select an example prompt or type your own
4. Press send to generate a chart

**Note:** Requires `OPENAI_API_KEY` and `OPENAI_BASE_URL`.
"""
        ),
        Chat(
            placeholder="Upload a file and ask questions...",
            actions=vizro_ai_chat(),
            file_upload=True,
            example_questions=[
                "Show a bar chart of the data",
                "Create a scatter plot of price vs quantity",
                "Make a pie chart showing distribution",
                "Plot a line chart over time",
            ],
        ),
    ],
)

# Page 4: OpenAI Chat with Streaming
page = vm.Page(
    title="OpenAI Chat (Streaming)",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [1]]),
    components=[
        vm.Card(
            text="""
## OpenAI Chat - Streaming Example

Chat with OpenAI models with real-time streaming responses.

**Note:** Requires `OPENAI_API_KEY` and `OPENAI_BASE_URL`.
"""
        ),
        Chat(actions=openai_streaming_chat()),
    ],
)

# Page 4: Mixed Content Chat Demo
page_mixed = vm.Page(
    title="Mixed Content Chat (No API Key)",
    layout=vm.Grid(grid=[[0, 1, 1, 1]]),
    components=[
        vm.Card(
            text="""
## Component Showcase Demo

This example demonstrates that chat responses can render **any Dash component**.
The response is fixed to showcase various components:

- **dmc.Alert** - Notification boxes
- **dmc.Table** - Data tables
- **dmc.Accordion** - Expandable sections
- **dmc.CodeHighlight** - Syntax-highlighted code
- **dmc.Blockquote** - Styled quotes
- **dcc.Graph** - Interactive Plotly charts
- **dmc.Image** - Images

Type anything to see the component showcase!
"""
        ),
        Chat(actions=mixed_content()),
    ],
)

# Page 5: Anthropic Claude Chat (Non-Streaming)
page_anthropic = vm.Page(
    title="Claude Chat (Non-Streaming)",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [1]]),
    components=[
        vm.Card(
            text="""
## Anthropic Claude Chat - Non-Streaming Example

Chat with Anthropic Claude. Response appears all at once when complete.

**Note:** Requires `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL`.
"""
        ),
        Chat(actions=anthropic_non_streaming_chat()),
    ],
)

# Page 6: VizroAI Natural Language Charts
page_vizro_ai = vm.Page(
    title="VizroAI Natural Language Charts",
    layout=vm.Grid(grid=[[0, 1, 1, 1]]),
    components=[
        vm.Card(
            text="""
## VizroAI - Natural Language Charts

Generate data visualizations by describing what you want in plain English.

**How to use:**
1. Upload a CSV or Excel file (.csv, .xls, .xlsx)
2. Describe the chart you want (e.g., "Show a bar chart of sales by region")
3. VizroAI generates an interactive Plotly chart

**Example prompts:**
- "Create a scatter plot of price vs quantity"
- "Show a line chart of revenue over time"
- "Make a pie chart of market share by company"
- "Plot a histogram of customer ages"

**Note:** Requires `OPENAI_API_KEY` and `OPENAI_BASE_URL`.
"""
        ),
        Chat(
            file_upload=True,
            placeholder="Describe the chart you want to create...",
            actions=vizro_ai_chat(),
        ),
    ],
)

# Page 7: OpenAI Vision Chat with Streaming
page_vision = vm.Page(
    title="OpenAI Vision Chat (Streaming)",
    layout=vm.Grid(grid=[[0, 1, 1, 1]]),
    components=[
        vm.Card(
            text="""
## OpenAI Vision Chat - Image Analysis (Streaming)

Upload images and ask questions about them using OpenAI's vision capabilities with streaming responses.

**How to use:**
1. Click the attachment icon to upload one or more images
2. Type your question about the image(s)
3. Press send to get AI analysis (streams in real-time!)

**Image requirements:**
- **Supported formats:** PNG, JPEG, WEBP, non-animated GIF
- **Size limits:** Up to 50 MB total per request, up to 500 images per request
- **Other:** No watermarks/logos, no NSFW content, clear enough for humans to understand

**Note:** Requires `OPENAI_API_KEY` and `OPENAI_BASE_URL`.
"""
        ),
        Chat(
            file_upload=True,
            placeholder="Upload images and ask questions about them...",
            actions=openai_vision_streaming_chat(model="gpt-4.1-nano"),
        ),
    ],
)

# Create the dashboard with all pages
dashboard = vm.Dashboard(
    pages=[
        page_echo,
        page_example_questions,
        page_example_with_upload,
        page,
        page_anthropic,
        page_mixed,
        page_vizro_ai,
        page_vision,
    ],
    theme="vizro_light",
    title="Vizro Chat Component Demo",
)

if __name__ == "__main__":
    app = Vizro()
    app.build(dashboard).run(debug=False)
