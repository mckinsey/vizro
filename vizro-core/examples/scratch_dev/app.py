import base64
import json
from typing import Literal, Annotated, Union

import dash
from dash import get_relative_path
from pydantic import Tag

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


class MyPage(vm.Page):
    title: Union[str, int]


page = MyPage(title=1, path="a", id="a", components=[vm.Text(text="a")], layout=NewFlexNoType())
# This works fine:
page_2 = MyPage(title="b", components=[vm.Text(text="b")], layout=NewFlexWithType())

# vm.Dashboard.add_type("pages", MyPage)


class MyDashboard(vm.Dashboard):
    pages: list[MyPage]


# Coerces to Flex if we don't explicitly specify new type
print(f"{type(page.layout)=}")
print(f"{type(page_2.layout)=}")
print("----")
dashboard = MyDashboard(pages=[page, page_2])

print(f"{type(page.title)=}")
print(f"{type(page_2.title)=}")

# Vizro().build(dashboard).run(debug=True)
