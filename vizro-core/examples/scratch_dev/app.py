from datetime import datetime

import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture


@capture("action")
def update_text(use_24_hour_clock):
    time_format = "%H:%M:%S %Z" if use_24_hour_clock else "%I:%M:%S %p %Z"
    switch_title = "24-hour clock" if use_24_hour_clock else "12-hour clock"
    time = datetime.now().strftime(time_format)
    return f"The time is {time}", switch_title


vm.Page.add_type("components", vm.Switch)  # (1)!

page = vm.Page(
    title="Action attached to button",
    layout=vm.Flex(),
    components=[
        vm.Switch(
            id="clock_switch",
            title="24-hour clock",
            value=True,
            actions=vm.Action(
                function=update_text(use_24_hour_clock="clock_switch"),
                outputs=["time_text", "clock_switch.title"],
            ),
        ),
        vm.Text(id="time_text", text="Toggle the switch"),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
