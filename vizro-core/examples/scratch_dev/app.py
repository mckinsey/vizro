import base64
import json
import dash
from dash import get_relative_path

import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

df = px.data.gapminder()

import plotly.graph_objs as go


@capture("action")
def update_control_same_page(data):
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
def update_control_different_page(data):
    # In future this action will be built-in.
    # In fact, hopefully soon you won't need to do this data["points"][0] stuff even for custom action.
    [continent] = data["points"][0]["customdata"]
    # In future this would just be trigger["customdata"]
    return get_relative_path("/target_page"), f"?target_filter2={encode_to_base64(continent)}"


################################################################################################
# Filter method for doing drill down:
# - two multi-select filters, one for continent and one for country
# - action updates just one of these at a time
# - data_Frame arrives in hierarchical_plot_filter_method already filtered
# - you can set "invalid" combinations manually e.g. by selecting continent="Africa" and country="France"
# - filters could be hidden with CSS (or in future built-in visible=False) and we put in a "reset filters" button
@capture("action")
def hierarchical_action_filter_method(data):
    data = data["points"][0]  # This line won't be needed in future
    # Ugly way to detect whether click was from the graph of px.scatter or px.pie. This tells us which filter to
    # update: continent or country.
    if "customdata" in data:
        [continent] = data["customdata"]
        return continent, dash.no_update
    else:
        country = data["label"]
        return dash.no_update, country


@capture("graph")
def hierarchical_plot_filter_method(data_frame):
    # Base case of plotting all countries and continents.
    if data_frame["continent"].nunique() > 1:
        return px.scatter(
            data_frame.query("year == 2007"),
            x="pop",
            y="lifeExp",
            log_x=True,
            color="continent",
            custom_data="continent",
        )
    # Drill down level 1 to looking at one continent.
    elif data_frame["country"].nunique() > 1:
        return px.pie(data_frame.query("year == 2007"), values="pop", names="country")
    # Drill down level 2 to looking at one country.
    elif data_frame["country"].nunique() == 1:
        return px.line(data_frame, x="year", y="pop")
    else:
        # e.g. when data_frame.empty. Maybe some other cases too since I wrote the above very roughly.
        return go.Figure()


################################################################################################
# Parameter method for doing drill down:
#  - one single-select parameter that switches between all possible charts using "encoded" options like country=France
#  - action a bit simpler because it needs to update only one control
#  - need to do filtering inside hierarchical_plot_parameter_method itself
#  - no possibility of setting invalid continent="Africa" and country="France"
#  - unlike filter method, this won't work for dynamic data
#  - almost definitely want to hide the selector or at least "encoded" options more sensibly using options dictionary
#  in Dash
@capture("graph")
def hierarchical_plot_parameter_method(data_frame, continent_country_filter):
    # Decode e.g. "country=France" string value
    column, value = continent_country_filter.split("=")

    # Base case of plotting all countries and continents.
    if column == "default":
        return px.scatter(
            data_frame.query("year == 2007"),
            x="pop",
            y="lifeExp",
            log_x=True,
            color="continent",
            custom_data="continent",
        )
    # Drill down level 1 to looking at one continent. Note need to do filtering.
    elif column == "continent":
        return px.pie(data_frame.query(f"year == 2007 and continent == '{value}'"), values="pop", names="country")
    # Drill down level 2 to looking at one country. No need to handle empty case here. Note need to do filtering.
    else:
        return px.line(data_frame.query(f"country == '{value}'"), x="year", y="pop")


@capture("action")
def hierarchical_action_parameter_method(data):
    data = data["points"][0]  # This line won't be needed in future
    # Ugly way to detect whether click was from the graph of px.scatter or px.pie. This tells us which filter to
    # update: continent or country.
    if "customdata" in data:
        [continent] = data["customdata"]
        return f"continent={continent}"
    else:
        country = data["label"]
        return f"country={country}"


parameter_method_options = (
    ["default=<all>"]
    + [f"continent={continent}" for continent in set(df["continent"])]
    + [f"country={country}" for country in set(df["country"])]
)
################################################################################################

page = vm.Page(
    title="Action triggered by graph",
    components=[
        vm.Container(
            title="Source graph",
            components=[
                vm.Graph(
                    id="source_graph",
                    figure=px.scatter(df, x="pop", y="lifeExp", log_x=True, color="continent", custom_data="continent"),
                    actions=vm.Action(
                        function=update_control_same_page("source_graph.clickData"), outputs="target_filter"
                    ),
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
                function=update_control_different_page("source_graph2.clickData"),
                outputs=["vizro_url.pathname", "vizro_url.search"],
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
    title="Drill-down graph using filters",
    components=[
        vm.Graph(
            id="graph",
            figure=hierarchical_plot_filter_method(df),
            actions=vm.Action(
                function=hierarchical_action_filter_method("graph.clickData"),
                outputs=["filter_continent", "filter_country"],
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


page_5 = vm.Page(
    title="Drill-down graph using parameter",
    components=[
        vm.Graph(
            id="graph2",
            figure=hierarchical_plot_parameter_method(df, continent_country_filter=parameter_method_options[0]),
            actions=vm.Action(function=hierarchical_action_parameter_method("graph2.clickData"), outputs="parameter"),
            # In future you won't need to label graph and do graph.clickData. You'd use special
            # argument trigger instead.
        ),
    ],
    controls=[
        vm.Parameter(
            id="parameter",
            targets=["graph2.continent_country_filter"],
            selector=vm.Dropdown(options=parameter_method_options, multi=False),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page, page_2, page_3, page_4, page_5])
Vizro().build(dashboard).run(debug=True)
