"""Example to show dashboard configuration specified as a YAML file."""

from datetime import datetime
from pathlib import Path

import vizro.models as vm
import yaml
from vizro import Vizro
from vizro.models.types import capture


@capture("action")
def current_time_text(use_24_hour_clock):
    """Return the current time as a formatted string."""
    time_format = "%H:%M:%S" if use_24_hour_clock else "%I:%M:%S %p"
    time = datetime.now().strftime(time_format)
    return f"The time is {time}"


# This line doesn't affect the example, so it raises the ValidationError exception.
vm.Page.add_type("components", vm.Switch)

dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = vm.Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
