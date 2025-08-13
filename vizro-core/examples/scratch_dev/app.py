import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

from datetime import datetime


@capture("action")
def update_time_text(use_24_hour_clock):  # (1)!
    time_format = "%H:%M:%S" if use_24_hour_clock else "%I:%M:%S %p"
    now = datetime.now()
    time = now.strftime(time_format)
    return f"The time is {time}"


@capture("action")
def update_date_text(date_format):  # (1)!
    date_format = "%d/%m/%y" if date_format == "DD/MM/YY" else "%m/%d/%y"
    now = datetime.now()
    date = now.strftime(date_format)
    return f"The date is {date}"  # (2)!


@capture("action")
def update_time_date_formats(location):
    if location == "Berlin":
        return True, "DD/MM/YY"
    return False, "MM/DD/YY"


vm.Container.add_type("components", vm.Switch)
vm.Container.add_type("components", vm.RadioItems)
vm.Container.add_type("components", vm.Dropdown)

page = vm.Page(
    title="My first custom action",
    layout=vm.Flex(),
    components=[
        vm.Container(
            layout=vm.Flex(direction="row"),
            variant="outlined",
            components=[
                vm.Dropdown(
                    id="location_dropdown",
                    title="Location",
                    options=["Berlin", "Washington, D.C"],
                    multi=False,
                    actions=[
                        vm.Action(
                            function=update_time_date_formats("location_dropdown.value"),
                            outputs=["clock_switch", "date_selector"],
                        )
                    ],
                ),
                vm.Switch(
                    id="clock_switch",
                    title="24-hour clock",
                    value=True,
                    actions=[
                        vm.Action(function=update_time_text(use_24_hour_clock="clock_switch"), outputs=["time_text"])
                    ],
                ),
                vm.RadioItems(
                    id="date_selector",
                    options=["DD/MM/YY", "MM/DD/YY"],
                    actions=[vm.Action(function=update_date_text(date_format="date_selector"), outputs=["date_text"])],
                ),
            ],
        ),
        vm.Text(id="time_text", text="Click the switch"),
        vm.Text(id="date_text", text="Click the radio item"),
    ],
)

# HERE: Do API request for weather in location as explicit chain. Probably this before implicit chain.
# Put time into timezone as final challenge?
# Note datetime shows system time (?) or UTC rather than fixed timezone.

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
