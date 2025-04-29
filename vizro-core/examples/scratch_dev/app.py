# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.models.types import capture


@capture("action")
def action_function_output_list(button_number_of_clicks, _controls):
    return f"Button clicked {button_number_of_clicks} times.", f"Controls: {str(_controls)}"


@capture("action")
def action_function_output_dict(button_number_of_clicks, _controls):
    return {
        "card-id-2": f"Controls: {str(_controls)}.",
        "card-id-1": f"Button clicked {button_number_of_clicks} times.",
    }


# TODO: Enable all three cases
action_output_list = vm.Action(
    function=action_function_output_list("button-id.n_clicks"),
    outputs=["card-id-1.children", "card-id-2.children"],
)
action_output_dict = vm.Action(
    function=action_function_output_dict("button-id.n_clicks"),
    outputs={
        "card-id-1": "card-id-1.children",
        "card-id-2": "card-id-2.children",
    },
)
action_output_dict_legacy = vm.Action(
    function=action_function_output_dict(),
    inputs=["button-id.n_clicks"],
    outputs={
        "card-id-1": "card-id-1.children",
        "card-id-2": "card-id-2.children",
    },
)


page = vm.Page(
    title="Title",
    layout=vm.Flex(),
    components=[
        vm.Graph(figure=px.scatter(px.data.iris(), x="sepal_length", y="petal_width", color="species")),
        vm.Button(
            id="button-id",
            text="Click me",
            actions=[
                # action_output_list,
                # action_output_dict,
                action_output_dict_legacy,
            ],
        ),
        vm.Card(
            id="card-id-1",
            text="Click button to update me",
        ),
        vm.Card(id="card-id-2", text="Click button to update me"),
    ],
    controls=[vm.Filter(column="species", selector=vm.RadioItems())],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
