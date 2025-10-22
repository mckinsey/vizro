"""Example to show dashboard configuration specified as a YAML file."""

import yaml
from pathlib import Path
from datetime import datetime

import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture


@capture("action")
def current_time_text(use_24_hour_clock):
    time_format = "%H:%M:%S" if use_24_hour_clock else "%I:%M:%S %p"
    time = datetime.now().strftime(time_format)
    return f"The time is {time}"


# This line doesn't affect the example, so it raises the ValidationError exception.
vm.Page.add_type("components", vm.Switch)

dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = vm.Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
