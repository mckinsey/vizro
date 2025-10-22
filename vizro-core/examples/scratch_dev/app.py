from datetime import datetime

import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture


@capture("action")
def current_time_text():
    time = datetime.now()
    return f"The time is {time}"


page = vm.Page(
    title="Action triggered by button",
    layout=vm.Flex(),
    components=[
        vm.Button(
            actions=vm.Action(
                function=current_time_text(),
                outputs="time_text",
            )
        ),
        vm.Text(id="time_text", text="Click the button"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
