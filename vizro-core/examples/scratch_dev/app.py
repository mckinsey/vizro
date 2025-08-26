import base64
import json

import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

df = px.data.gapminder().query("year == 2007")


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

dashboard = vm.Dashboard(pages=[page, page_2, page_3])
Vizro().build(dashboard).run(debug=True)
