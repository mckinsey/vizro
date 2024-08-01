"""Dev app to try things out."""

from typing import Any, Literal

import vizro.models as vm
from dash import dcc
from vizro import Vizro


class PureDashSlider(vm.VizroBaseModel):
    type: Literal["simple_slider"] = "simple_slider"
    kwargs: Any

    def build(self):
        return dcc.Slider(**self.kwargs)


vm.Container.add_type("components", vm.Slider)
vm.Container.add_type("components", PureDashSlider)

# All floats: This works on Vizro, while it does not work in Dash
a = dict(min=0, max=2, step=0.1, marks={0.0: "a", 1.0: "x", 2.0: "y"})  # noqa: C408

# All int: This works in both Vizro and Dash
b = dict(min=0, max=2, step=0.1, marks={0: "a", 1: "x", 2: "y"})  # noqa: C408

# Mixed float and int: This works in Vizro, while it only partially works in Dash
c = dict(min=0, max=1, step=0.1, marks={0: "a", 0.5: "x", 1.0: "y"})  # noqa: C408

# User example
e = dict(min=0, max=1, step=0.01, marks={0: "0%", 0.21: "MARKET", 1.0: "100%"})  # noqa: C408

# Other test example: https://github.com/mckinsey/vizro/pull/266
d = dict(min=2, max=5, step=1, value=3)  # noqa: C408

page = vm.Page(
    title="Vizro on PyCafe",
    components=[
        vm.Container(
            title="vm.Sliders",
            layout=vm.Layout(grid=[[0, 1, 2, 3, 4]]),
            components=[vm.Slider(**a), vm.Slider(**b), vm.Slider(**c), vm.Slider(**d), vm.Slider(**e)],
        ),
        vm.Container(
            title="dcc.Sliders",
            layout=vm.Layout(grid=[[0, 1, 2, 3, 4]]),
            components=[
                PureDashSlider(kwargs=a),
                PureDashSlider(kwargs=b),
                PureDashSlider(kwargs=c),
                PureDashSlider(kwargs=d),
                PureDashSlider(kwargs=e),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
