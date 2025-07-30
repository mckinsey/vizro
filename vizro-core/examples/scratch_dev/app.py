import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

from datetime import datetime


@capture("action")
def update_text(use_24_hour_clock, date_format):
    time_format = "%H:%M:%S" if use_24_hour_clock else "%I:%M:%S %p"
    date_format = "%d/%m/%y" if date_format == "DD/MM/YY" else "%m/%d/%y"
    now = datetime.now()
    time = now.strftime(time_format)
    date = now.strftime(date_format)
    return [f"The time is {time}", f"The date is {date}"]


vm.Container.add_type("components", vm.Switch)  # (1)!
vm.Container.add_type("components", vm.RadioItems)

page = vm.Page(
    title="My first custom action",
    layout=vm.Flex(),
    components=[
        vm.Container(  # (2)!
            layout=vm.Flex(direction="row"),
            variant="outlined",
            components=[
                vm.Switch(id="clock_switch", title="24-hour clock", value=True),  # (3)!
                vm.RadioItems(id="date_selector", options=["DD/MM/YY", "MM/DD/YY"]),
                vm.Button(
                    actions=[
                        vm.Action(
                            function=update_text(use_24_hour_clock="clock_switch", date_format="date_selector"),
                            outputs=["time_text", "date_text"],
                        ),
                    ]
                ),
            ],
        ),
        vm.Text(id="time_text", text="Click the button"),
        vm.Text(id="date_text", text="Click the button"),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
