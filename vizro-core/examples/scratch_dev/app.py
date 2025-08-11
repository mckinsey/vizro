"""Scratch development app."""

import vizro.models as vm
from vizro import Vizro
import vizro.plotly.express as px
from vizro.models.types import capture


# Test action with single string output (instead of list)
@capture("action")
def update_card_text():
    return "Updated text content!"


page = vm.Page(
    title="My first dashboard",
    layout=vm.Flex(),
    components=[
        vm.Text(text="Click the button to update this text", id="text-component"),
        vm.Button(
            text="Test Single Output",
            actions=[
                vm.Action(
                    function=update_card_text(),
                    outputs="text-component",
                )
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
