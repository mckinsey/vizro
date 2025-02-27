"""Example of a chat assistant using VizroChatComponent."""

import os
from dotenv import load_dotenv
import vizro.plotly.express as px


import vizro.models as vm
from vizro import Vizro
from vizro_chat import EchoProcessor, VizroChatComponent

from vizro_chat import VizroChatComponent
from custom_processor import SQLAgentProcessor
from vizro_chat import OpenAIProcessor

# Load environment variables from .env file
# env_path = Path(__file__).parent / ".env"
# load_dotenv(env_path)
load_dotenv()
from langsmith import traceable

# Initialize Vizro with assets folder
assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
vizro_app = Vizro(assets_folder=assets_path)

# Register the chat component
vm.Page.add_type("components", VizroChatComponent)

# Create chat component with OpenAI processor and settings
chat_component = VizroChatComponent(
    id="chat",
    input_placeholder="Ask about the Chinook database...",
    button_text="Send",
    vizro_app=vizro_app,
    # processor=OpenAIProcessor(model="gpt-4o-mini", temperature=0.7),
    processor=EchoProcessor(),
    show_settings=True  # Enable settings icon
)

# Create chat pages
chat_page = vm.Page(
    title="SQL Chat Assistant",
    components=[
        chat_component,
        vm.Card(
            text="""
                ### Components

                Main components of Vizro include **charts**, **tables**, **cards**, **figures**, **containers**,
                **buttons** and **tabs**.
                """,
            href="/graphs",
        ),
        ],
    layout=vm.Layout(grid=[[0, 0, 1], [0, 0, 1]]),
)

iris = px.data.iris()
iris_page = vm.Page(
    title="Graphs",
    components=[
        vm.Graph(
            figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
            title="Relationships between Sepal Width and Sepal Length",
            header="""
                Each point in the scatter plot represents one of the 150 iris flowers, with colors indicating their
                types. The Setosa type is easily identifiable by its short and wide sepals.

                However, there is still overlap between the Versicolor and Virginica types when considering only sepal
                width and length.
                """,
            footer="""SOURCE: **Plotly iris data set, 2024**""",
        ),
    ],
)

# Build and run
dashboard = vm.Dashboard(
    pages=[chat_page, iris_page],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(
                    label="Chat",
                    icon="Chat",
                    pages=["SQL Chat Assistant"],
                ),
                vm.NavLink(
                    label="Data",
                    icon="Scatter Plot",
                    pages=["Graphs"],
                ),
            ]
        )
    ),
)
vizro_app.build(dashboard)
vizro_app.run(debug=False)
