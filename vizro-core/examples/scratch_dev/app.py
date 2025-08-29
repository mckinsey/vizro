import base64
import json
from typing import Literal

import dash
from dash import get_relative_path

import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

df = px.data.gapminder()


class NewFlexNoType(vm.Flex):
    pass


class NewFlexWithType(vm.Flex):
    type: Literal["anything"] = "anything"


# No add_type needed!

page = vm.Page(title="a", components=[vm.Text(text="a")], layout=NewFlexNoType())
page_2 = vm.Page(title="b", components=[vm.Text(text="b")], layout=NewFlexWithType())

# Coerces to Flex if we don't explicitly specify new type
print(f"{type(page.layout)=}")
print(f"{type(page_2.layout)=}")


dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run(debug=True)
