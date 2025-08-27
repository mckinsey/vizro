""""""

import base64
import json
from typing import Literal

import dash

import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

df = px.data.gapminder()

import plotly.graph_objs as go


@capture("action")
def drill_down(data):
    # In future this action will be built-in.
    # In fact, hopefully soon you won't need to do this data["points"][0] stuff even for custom action.
    [continent] = data["points"][0]["customdata"]
    # In future this would just be trigger["customdata"]
    return continent


def encode_to_base64(value):
    json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
    b64_bytes = base64.urlsafe_b64encode(json_bytes)
    return f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"


@capture("action")
def drill_through(data):
    # In future this action will be built-in.
    # In fact, hopefully soon you won't need to do this data["points"][0] stuff even for custom action.
    [continent] = data["points"][0]["customdata"]
    # In future this would just be trigger["customdata"]
    return "/target_page", f"?target_filter2={encode_to_base64(continent)}"


@capture("action")
def hierarchical_action(data):
    data = data["points"][0]  # This line won't be needed in future
    # Ugly way to detect whether click was from the graph of px.scatter or px.pie. This tells us which filter to
    # update: continent or country.
    if "customdata" in data:
        [continent] = data["customdata"]
        return continent, dash.no_update
    else:
        country = data["label"]
        return dash.no_update, country


# You could definitely do something like this using Parameters (or maybe just one Parameter) instead, but would then
# need to do the filtering operation inside hierarchical_plot itself. It wouldn't work so well with dynamic data either.
@capture("graph")
def hierarchical_plot(data_frame):
    if data_frame["continent"].nunique() > 1:
        return px.scatter(
            data_frame.query("year == 2007"),
            x="pop",
            y="lifeExp",
            log_x=True,
            color="continent",
            custom_data="continent",
        )
    elif data_frame["country"].nunique() > 1:
        return px.pie(data_frame.query("year == 2007"), values="pop", names="country")
    elif data_frame["country"].nunique() == 1:
        return px.line(data_frame, x="year", y="pop")
    else:
        # e.g. when data_frame.empty. Probably some other cases too since I wrote the above very roughly.
        return go.Figure()


page = vm.Page(
    title="Action triggered by graph",
    components=[
        vm.Container(
            title="Source graph",
            components=[
                vm.Graph(
                    id="source_graph",
                    figure=px.scatter(df, x="pop", y="lifeExp", log_x=True, color="continent", custom_data="continent"),
                    actions=vm.Action(function=drill_down("source_graph.clickData"), outputs="target_filter"),
                    # In future you won't need to label source_graph and do source_graph.clickData. You'd use special
                    # argument trigger instead.
                ),
            ],
        ),
        vm.Container(
            title="Target table",
            controls=[vm.Filter(id="target_filter", column="continent")],
            components=[vm.AgGrid(figure=dash_ag_grid(df))],
        ),
    ],
)

page_2 = vm.Page(
    title="Cross-page action triggered by graph source",
    components=[
        vm.Graph(
            id="source_graph2",
            figure=px.scatter(df, x="pop", y="lifeExp", log_x=True, color="continent", custom_data="continent"),
            actions=vm.Action(
                function=drill_through("source_graph2.clickData"), outputs=["vizro_url.pathname", "vizro_url.search"]
            ),
            # In future you won't need to label source_graph and do source_graph.clickData. You'd use special
            # argument trigger instead.
        ),
    ],
)


page_3 = vm.Page(
    id="target_page",
    title="Cross-page action triggered by graph target",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
    controls=[vm.Filter(id="target_filter2", column="continent", show_in_url=True)],
)

page_4 = vm.Page(
    title="Self-interacting graph",
    components=[
        vm.Graph(
            id="graph",
            figure=hierarchical_plot(df),
            actions=vm.Action(
                function=hierarchical_action("graph.clickData"), outputs=["filter_continent", "filter_country"]
            ),
            # In future you won't need to label graph and do graph.clickData. You'd use special
            # argument trigger instead.
        ),
    ],
    controls=[
        vm.Filter(id="filter_continent", column="continent"),
        vm.Filter(id="filter_country", column="country"),
    ],
)

dashboard = vm.Dashboard(pages=[page, page_2, page_3, page_4])
Vizro().build(dashboard).run(debug=True)
