from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture


@capture("action")
def update_time_text(use_24_hour_clock, location):
    time_format = "%H:%M:%S %Z" if use_24_hour_clock else "%I:%M:%S %p %Z"
    timezone_name = "Europe/Berlin" if location == "Berlin" else "America/New_York"
    now = datetime.now(ZoneInfo(timezone_name))  # (1)!
    time = now.strftime(time_format)
    return f"The time is {time}"


@capture("action")
def update_date_text(date_format, location):
    date_format = "%d/%m/%y" if date_format == "DD/MM/YY" else "%m/%d/%y"
    timezone_name = "Europe/Berlin" if location == "Berlin" else "America/New_York"
    now = datetime.now(ZoneInfo(timezone_name))
    date = now.strftime(date_format)
    return f"The date is {date}"


@capture("action")
def fetch_weather(location):
    berlin_params = {"latitude": 52.5, "longitude": 13.4, "current": "temperature_2m"}
    washington_dc_params = {"latitude": 38.9, "longitude": -77.0, "current": "temperature_2m"}
    params = berlin_params if location == "Berlin" else washington_dc_params
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
    temperature = r.json()["current"]["temperature_2m"]
    return f"The current temperature in {location} is {temperature}°C"


@capture("action")
def update_time_date_formats(location):
    if location == "Berlin":
        return True, "DD/MM/YY", "Fetching current weather..."  # (1)!
    return False, "MM/DD/YY", "Fetching current weather..."


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
                    options=["Berlin", "Washington, D.C."],
                    multi=False,
                    actions=[
                        vm.Action(
                            function=update_time_date_formats("location_dropdown"),
                            outputs=["clock_switch", "date_radio_items", "weather_text"],
                        ),
                        vm.Action(function=fetch_weather("location_dropdown"), outputs="weather_text"),
                    ],
                    extra={"style": {"min-width": "200px"}},
                ),
                vm.Switch(
                    id="clock_switch",
                    title="24-hour clock",
                    value=True,
                    actions=vm.Action(
                        function=update_time_text("clock_switch", "location_dropdown"), outputs="time_text"
                    ),  # (3)!
                ),
                vm.RadioItems(
                    id="date_radio_items",
                    options=["DD/MM/YY", "MM/DD/YY"],
                    actions=vm.Action(
                        function=update_date_text("date_radio_items", "location_dropdown"), outputs="date_text"
                    ),
                ),
            ],
        ),
        vm.Text(id="time_text", text="Click the button"),
        vm.Text(id="date_text", text="Click the button"),
        vm.Text(id="weather_text", text="Click the button"),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
