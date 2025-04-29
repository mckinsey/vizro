# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.models.types import capture


# Guidelines:
# - vm.Action.outputs for custom actions could only be defined as list[str].
# See Action.outputs annotation under the _action.py
# - To enable vm.Action.outputs to be a dict[str, str]:
#   - Uncomment the code below the #### Action's output as a dict #### in this file.
#   - Uncomment the usage of the `action_output_dict` under the Button.actions definition.
#   - Run the app and see how it fails.


#   - Enable vm.Action.outputs to be a union[list[str], dict[str, str]] in the _action.py file.
#   - Run the app and see how it fails when the action is triggered.
#   - Add proper outputs dictionary transformation from the dict[str, str] to dict[str, Output] in the
#     `_BaseAction._transformed_outputs` (_action.py file).
#   - Run the app and see how it works. If it does not work then check the `_BaseAction._action_callback_function`.
# - Write just a few unit tests that prove it works. I can help you with this.
# - No docs updates are needed for this change yet.

#### Action's output as a list ####

@capture("action")
def action_function_output_list(button_number_of_clicks, _controls):
    return f"Button clicked {button_number_of_clicks} times.", f"Controls: {str(_controls)}"
# The following also works:
#    return [f"Button clicked {button_number_of_clicks} times.", f"Controls: {str(_controls)}"]


action_output_list = vm.Action(
    function=action_function_output_list("button-id.n_clicks"),
    outputs=["card-id-1.children", "card-id-2.children"],
)


# TODO: Enable so that action output could be a dict:
#### Action's output as a dict ####

@capture("action")
def action_function_output_dict(button_number_of_clicks, _controls):
    return {
         "card-id-2": f"Controls: {str(_controls)}.",
         "card-id-1": f"Button clicked {button_number_of_clicks} times.",
     }
     # TODO: IT'S IRRELEVANT THOUGH:
     #   Consider if vm.Action.outputs are defined as list -> outputs=["card-id-1.children", "card-id-2.children"]
     #   Should we automatically enable action function output to be a dict in the format:
     #   {
     #       "card-id-1.children": "Button clicked {button_number_of_clicks} times.",
     #       "card-id-2.children": "Controls: {str(_controls)}."}
     #   }


action_output_dict = vm.Action(
    function=action_function_output_dict("button-id.n_clicks"),
    outputs={
         "card-id-1": "card-id-1.children",
         "card-id-2": "card-id-2.children",
    },
)


# # TODO: Enable output dict for legacy actions too:
# action_output_dict_legacy = vm.Action(
#     function=action_function_output_dict(),
#     inputs=["button-id.n_clicks"],
#     outputs={
#         "card-1": "card-id-1.children",
#         "card-2": "card-id-2.children",
#     },
# )


page = vm.Page(
    title="Title",
    layout=vm.Flex(),
    components=[
        vm.Graph(figure=px.scatter(px.data.iris(), x="sepal_length", y="petal_width", color="species")),
        vm.Button(
            id="button-id",
            text="Click me",
            actions=[
                #action_output_list,
                 action_output_dict,
                # action_output_dict_legacy,
            ]
        ),
        vm.Card(
            id="card-id-1",
            text="Click button to update me",
        ),
        vm.Card(
            id="card-id-2",
            text="Click button to update me"
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.RadioItems())
    ]
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
