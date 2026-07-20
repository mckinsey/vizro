"""Complete final app from the Vizro "Write your own actions" tutorial.

Extracted from the "Handle errors" example at the end of the tutorial. It
combines every incremental step from the tutorial into a single runnable file:

    - a Dropdown that selects between Berlin and Washington, D.C.
    - a Switch that toggles between 12- and 24-hour clock
    - a RadioItems that toggles between DD/MM/YY and MM/DD/YY date formats
    - three Cards that display the current time, date and weather at the
      chosen location
    - four custom actions with try/except handling for the weather HTTP
      request

See: https://vizro.readthedocs.io/en/stable/pages/tutorials/custom-actions-tutorial/
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture


@capture("action")
def update_time_card(use_24_hour_clock, location):
    """Return a Markdown string with the current time at ``location``."""
    time_format = "%H:%M:%S %Z" if use_24_hour_clock else "%I:%M:%S %p %Z"
    timezone_name = "Europe/Berlin" if location == "Berlin" else "America/New_York"
    now = datetime.now(ZoneInfo(timezone_name))
    time = now.strftime(time_format)
    return f"🕰️ The time is {time}"


@capture("action")
def update_date_card(date_format, location):
    """Return a Markdown string with the current date at ``location``."""
    date_format = "%d/%m/%y" if date_format == "DD/MM/YY" else "%m/%d/%y"
    timezone_name = "Europe/Berlin" if location == "Berlin" else "America/New_York"
    now = datetime.now(ZoneInfo(timezone_name))
    date = now.strftime(date_format)
    return f"📅 The date is {date}"


@capture("action")
def fetch_weather(location):
    """Fetch the current temperature at ``location`` from Open-Meteo."""
    berlin_params = {"latitude": 52.5, "longitude": 13.4, "current": "temperature_2m"}
    washington_dc_params = {"latitude": 38.9, "longitude": -77.0, "current": "temperature_2m"}
    params = berlin_params if location == "Berlin" else washington_dc_params
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=5)
        temperature = r.json()["current"]["temperature_2m"]
    except Exception:
        return "❗ Could not fetch weather"
    return f"🌡️ The current temperature in {location} is {temperature}°C"


@capture("action")
def update_time_date_formats(location):
    """Return default clock, date-format and placeholder weather text for ``location``."""
    if location == "Berlin":
        return True, "DD/MM/YY", "Fetching current weather..."
    return False, "MM/DD/YY", "Fetching current weather..."


vm.Container.add_type("components", vm.Switch)
vm.Container.add_type("components", vm.RadioItems)
vm.Container.add_type("components", vm.Dropdown)

page = vm.Page(
    title="My first action",
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
                            outputs=["clock_switch", "date_radio_items", "weather_card"],
                        ),
                        vm.Action(function=fetch_weather("location_dropdown"), outputs="weather_card"),
                    ],
                    extra={"style": {"min-width": "200px"}},
                ),
                vm.Switch(
                    id="clock_switch",
                    title="24-hour clock",
                    value=True,
                    actions=vm.Action(
                        function=update_time_card("clock_switch", "location_dropdown"),
                        outputs="time_card",
                    ),
                ),
                vm.RadioItems(
                    id="date_radio_items",
                    options=["DD/MM/YY", "MM/DD/YY"],
                    actions=vm.Action(
                        function=update_date_card("date_radio_items", "location_dropdown"),
                        outputs="date_card",
                    ),
                ),
            ],
        ),
        vm.Card(id="time_card", text="Select a location to show the current time."),
        vm.Card(id="date_card", text="Select a location to show the current date."),
        vm.Card(id="weather_card", text="Select a location to fetch the current weather."),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
