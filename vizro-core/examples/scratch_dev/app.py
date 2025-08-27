"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
import time

df = px.data.iris()


@capture("action")
def fast_action(x):
    return f"Fast action triggered {x} times"


@capture("action")
def slow_action(x):
    time.sleep(2)
    return f"Slow action triggered {x} times"


page_1 = vm.Page(
    title="Test Page",
    layout=vm.Flex(),
    components=[
        vm.Button(
            id="fast_action_button",
            text="Trigger Fast Action",
            actions=vm.Action(
                function=fast_action("fast_action_button.n_clicks"),
                outputs=["output_text"]
            )
        ),
        vm.Button(
            id="slow_action_button",
            text="Trigger Slow Action",
            actions=vm.Action(
                function=slow_action("slow_action_button.n_clicks"),
                outputs=["output_text"]
            )
        ),
        vm.Text(
            id="output_text",
            text="Trigger an action to see the result here.",
        )
    ],
)

page_2 = vm.Page(
    title="Standard Vizro Page",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[vm.Filter(column="species")]
)

dashboard = vm.Dashboard(
    # It works fine with and without a dashboard title.
    title="Dashboard Title",
    pages=[page_1, page_2],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
