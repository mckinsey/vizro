import e2e.vizro.constants as cnst
import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_control
from vizro.tables import dash_ag_grid

_gapminder = px.data.gapminder().query("year == 2007").copy()
_regions = {
    "North": {
        "Canada",
        "United States",
        "Denmark",
        "Finland",
        "Norway",
        "Sweden",
        "Iceland",
        "Ireland",
        "United Kingdom",
    },
    "South": {
        "Argentina",
        "Brazil",
        "Australia",
        "New Zealand",
        "India",
        "China",
        "Japan",
    },
    "West": {
        "Mexico",
        "Germany",
        "France",
        "Spain",
        "Italy",
        "Nigeria",
        "Egypt",
    },
    "East": {
        "Poland",
        "Ethiopia",
        "Kenya",
        "Korea, Rep.",
        "Thailand",
        "Indonesia",
    },
}
_gapminder["region"] = _gapminder["country"].map({c: r for r, cs in _regions.items() for c in cs})

# "Portland" appears under both Oregon and Maine; "Springfield" under Oregon and Illinois.
_cities = pd.DataFrame(
    {
        "state": ["Oregon", "Oregon", "Oregon", "Maine", "Maine", "Illinois", "Illinois"],
        "city": ["Portland", "Salem", "Springfield", "Portland", "Augusta", "Chicago", "Springfield"],
        "population": [652503, 175535, 62607, 66215, 18899, 2716000, 114230],
    }
)

cascader_leaf_page = vm.Page(
    title=cnst.CASCADER_LEAF_PAGE,
    components=[
        vm.AgGrid(
            id=cnst.CASCADER_LEAF_AG_GRID_ID,
            figure=dash_ag_grid(data_frame=_gapminder),
        ),
        vm.AgGrid(
            id=cnst.CASCADER_LEAF_MULTI_AG_GRID_ID,
            figure=dash_ag_grid(data_frame=_gapminder),
        ),
        vm.AgGrid(
            id=cnst.CASCADER_LEAF_SET_CONTROL_AG_GRID_SOURCE_ID,
            title="set_control source",
            figure=dash_ag_grid(data_frame=_gapminder),
            actions=set_control(control=cnst.CASCADER_LEAF_FILTER_CONTROL_ID, value="country"),
        ),
        vm.Button(
            id=cnst.CASCADER_LEAF_SET_CONTROL_BUTTON_ID,
            text="Show China",
            actions=set_control(control=cnst.CASCADER_LEAF_FILTER_CONTROL_ID, value="China"),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.CASCADER_LEAF_FILTER_CONTROL_ID,
            column=["continent", "region", "country"],
            targets=[cnst.CASCADER_LEAF_AG_GRID_ID],
            selector=vm.Cascader(
                id=cnst.CASCADER_LEAF_ID,
                multi=False,
                full_path=False,
                value="United States",
                title="Country (single, leaf mode)",
            ),
        ),
        vm.Filter(
            id=cnst.CASCADER_LEAF_MULTI_FILTER_CONTROL_ID,
            column=["continent", "region", "country"],
            targets=[cnst.CASCADER_LEAF_MULTI_AG_GRID_ID],
            show_in_url=True,
            selector=vm.Cascader(
                id=cnst.CASCADER_LEAF_MULTI_ID,
                multi=True,
                full_path=False,
                value=["United States", "China"],
                title="Countries (multi, leaf mode)",
            ),
        ),
    ],
)

cascader_path_page = vm.Page(
    title=cnst.CASCADER_PATH_PAGE,
    components=[
        vm.AgGrid(
            id=cnst.CASCADER_PATH_AG_GRID_ID,
            figure=dash_ag_grid(data_frame=_cities),
        ),
        vm.AgGrid(
            id=cnst.CASCADER_PATH_MULTI_AG_GRID_ID,
            figure=dash_ag_grid(data_frame=_cities),
        ),
        vm.AgGrid(
            id=cnst.CASCADER_PATH_SET_CONTROL_AG_GRID_SOURCE_ID,
            title="set_control source",
            figure=dash_ag_grid(data_frame=_cities),
            actions=set_control(control=cnst.CASCADER_PATH_SET_CONTROL_FILTER_CONTROL_ID, value="city"),
        ),
        vm.AgGrid(
            id=cnst.CASCADER_PATH_SET_CONTROL_AG_GRID_ID,
            figure=dash_ag_grid(data_frame=_cities),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.CASCADER_PATH_FILTER_CONTROL_ID,
            column=["state", "city"],
            targets=[cnst.CASCADER_PATH_AG_GRID_ID],
            selector=vm.Cascader(
                id=cnst.CASCADER_PATH_ID,
                multi=False,
                full_path=True,
                value=["Oregon", "Portland"],
                title="City (single, path mode)",
            ),
        ),
        vm.Filter(
            id=cnst.CASCADER_PATH_MULTI_FILTER_CONTROL_ID,
            column=["state", "city"],
            targets=[cnst.CASCADER_PATH_MULTI_AG_GRID_ID],
            show_in_url=True,
            selector=vm.Cascader(
                id=cnst.CASCADER_PATH_MULTI_ID,
                multi=True,
                full_path=True,
                value=[["Illinois", "Chicago"], ["Maine", "Augusta"]],
                title="Cities (multi, path mode)",
            ),
        ),
        # Path-mode Cascader cannot be a set_control target; leaf mode with unique leaves is used here instead.
        vm.Filter(
            id=cnst.CASCADER_PATH_SET_CONTROL_FILTER_CONTROL_ID,
            column=["state", "city"],
            targets=[cnst.CASCADER_PATH_SET_CONTROL_AG_GRID_ID],
            selector=vm.Cascader(
                id=cnst.CASCADER_PATH_SET_CONTROL_ID,
                multi=False,
                full_path=False,
                options={
                    "Maine": ["Augusta"],
                    "Illinois": ["Chicago"],
                    "Oregon": ["Salem"],
                },
                value="Chicago",
                title="City (single, leaf mode, set_control target)",
            ),
        ),
    ],
)
