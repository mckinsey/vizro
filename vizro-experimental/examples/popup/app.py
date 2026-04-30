"""Example: Chat popup floating over a Vizro dashboard.

Run with:
    hatch run example popup

The dashboard shows normal pages with charts.
A floating chat button appears in the bottom-right corner.
Click it to open a data-aware chatbot powered by OpenAI with streaming responses.

Requires OPENAI_API_KEY environment variable.
"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

# --- Dashboard pages with sample content ---
iris = px.data.iris()
gapminder = px.data.gapminder()

page1 = vm.Page(
    title="Iris Scatter Plot",
    components=[
        vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species", title="Iris Dataset")),
    ],
)

page2 = vm.Page(
    title="Gapminder",
    components=[
        vm.Graph(
            figure=px.scatter(
                gapminder.query("year == 2007"),
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
                hover_name="country",
                log_x=True,
                size_max=60,
                title="Life Expectancy vs GDP per Capita (2007)",
            )
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[page1, page2],
    theme="vizro_light",
    title="Dashboard with Chat Popup",
)

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    from vizro_experimental.chat.popup import add_chat_popup

    app = Vizro()
    app.build(dashboard)

    add_chat_popup(
        app,
        title="Chat Assistant",
        placeholder="Ask me anything about the data...",
    )

    # debug=False so Dash's debug menu doesn't overlap the popup toggle in the
    # bottom-right corner (it intercepts clicks in the integration tests).
    app.run(debug=False)
