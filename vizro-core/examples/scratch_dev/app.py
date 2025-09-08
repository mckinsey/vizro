import warnings
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Literal
from pydantic import model_validator

import vizro.models as vm
from vizro import Vizro
from vizro.models._models_utils import make_actions_chain
from vizro.models.types import capture, ActionsType
import dash_mantine_components as dmc
from pprint import pprint


@capture("action")
def f(a):
    print(a)
    pass


vm.Page.add_type("components", vm.RadioItems)

if __name__ == "__main__":
    actions = vm.Action(function=f(2))
    vm.Layout(grid=[[0]])

    page = vm.Page(
        title="Custom component",
        layout=vm.Flex(direction="row"),
        components=[vm.RadioItems(options=list("abc"), actions=actions)],
    )
    # print(actions.inputs)
    # pprint(vm.Action.model_json_schema()["propertie])


dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
