"""Example to show dashboard configuration."""
from typing import List

import pandas as pd
from dash import State, dash_table

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.gapminder()
df_mean = (
    df.groupby(by=["continent", "year"]).agg({"lifeExp": "mean", "pop": "mean", "gdpPercap": "mean"}).reset_index()
)

df_transformed = df.copy()
df_transformed["lifeExp"] = df.groupby(by=["continent", "year"])["lifeExp"].transform("mean")
df_transformed["gdpPercap"] = df.groupby(by=["continent", "year"])["gdpPercap"].transform("mean")
df_transformed["pop"] = df.groupby(by=["continent", "year"])["pop"].transform("sum")
df_concat = pd.concat([df_transformed.assign(color="Continent Avg."), df.assign(color="Country")], ignore_index=True)


def my_custom_table(data_frame=None, id: str = None, chosen_columns: List[str] = None):
    """Custom table."""
    columns = [{"name": i, "id": i} for i in chosen_columns]
    defaults = {
        "style_as_list_view": True,
        "style_data": {"border_bottom": "1px solid var(--border-subtle-alpha-01)", "height": "40px"},
        "style_header": {
            "border_bottom": "1px solid var(--state-overlays-selected-hover)",
            "border_top": "1px solid var(--main-container-bg-color)",
            "height": "32px",
        },
    }
    return dash_table.DataTable(data=data_frame.to_dict("records"), columns=columns, id=id, **defaults)


my_custom_table.action_info = {
    "filter_interaction_input": lambda x: {
        "active_cell": State(component_id=x._callable_object_id, component_property="active_cell"),
        "derived_viewport_data": State(
            component_id=x._callable_object_id,
            component_property="derived_viewport_data",
        ),
    }
}

my_custom_table = capture("table")(my_custom_table)


def create_benchmark_analysis():
    """Function returns a page to perform analysis on country level."""
    # Apply formatting to table columns
    columns = [
        {"id": "country", "name": "country"},
        {"id": "continent", "name": "continent"},
        {"id": "year", "name": "year"},
        {"id": "lifeExp", "name": "lifeExp", "type": "numeric", "format": {"specifier": ",.1f"}},
        {"id": "gdpPercap", "name": "gdpPercap", "type": "numeric", "format": {"specifier": "$,.2f"}},
        {"id": "pop", "name": "pop", "type": "numeric", "format": {"specifier": ",d"}},
    ]

    page_country = vm.Page(
        title="Benchmark Analysis",
        # description="Discovering how the metrics differ for each country and export data for further investigation",
        # layout=vm.Layout(grid=[[0, 1]] * 5 + [[2, -1]], col_gap="32px", row_gap="60px"),
        components=[
            vm.Table(
                id="table_country_new",
                title="Click on a cell in country column:",
                figure=dash_ag_grid(
                    id="dash_ag_grid_country",
                    data_frame=df,
                ),
                actions=[vm.Action(function=filter_interaction(targets=["line_country"]))],
            ),
            vm.Table(
                id="table_country",
                title="Click on a cell in country column:",
                figure=dash_data_table(
                    id="dash_data_table_country",
                    data_frame=df,
                    columns=columns,
                    style_data_conditional=[
                        {
                            "if": {"filter_query": "{gdpPercap} < 1045", "column_id": "gdpPercap"},
                            "backgroundColor": "#ff9222",
                        },
                        {
                            "if": {
                                "filter_query": "{gdpPercap} >= 1045 && {gdpPercap} <= 4095",
                                "column_id": "gdpPercap",
                            },
                            "backgroundColor": "#de9e75",
                        },
                        {
                            "if": {
                                "filter_query": "{gdpPercap} > 4095 && {gdpPercap} <= 12695",
                                "column_id": "gdpPercap",
                            },
                            "backgroundColor": "#aaa9ba",
                        },
                        {
                            "if": {"filter_query": "{gdpPercap} > 12695", "column_id": "gdpPercap"},
                            "backgroundColor": "#00b4ff",
                        },
                    ],
                    sort_action="native",
                    style_cell={"textAlign": "left"},
                ),
                actions=[vm.Action(function=filter_interaction(targets=["line_country"]))],
            ),
            vm.Graph(
                id="line_country",
                figure=px.line(
                    df_concat,
                    title="Country vs. Continent",
                    x="year",
                    y="gdpPercap",
                    color="color",
                    labels={"year": "Year", "data": "Data", "gdpPercap": "GDP per capita"},
                    color_discrete_map={"Country": "#afe7f9", "Continent": "#003875"},
                    markers=True,
                    hover_name="country",
                ),
            ),
            vm.Button(
                text="Export data",
                actions=[
                    vm.Action(
                        function=export_data(
                            targets=["line_country"],
                        )
                    ),
                ],
            ),
            vm.Table(  # the custom table works with its own set of states defined above
                id="custom_table",
                title="Custom Dash DataTable",
                figure=my_custom_table(
                    id="custom_dash_table_callable_id",
                    data_frame=df,
                    chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"],
                ),
                actions=[vm.Action(function=filter_interaction(targets=["line_country"]))],
            ),
        ],
        controls=[
            vm.Filter(column="continent", selector=vm.Dropdown(value="Europe", multi=False, title="Select continent")),
            vm.Filter(column="year", selector=vm.RangeSlider(title="Select timeframe", step=1, marks=None)),
            vm.Parameter(
                targets=["line_country.y"],
                selector=vm.Dropdown(
                    options=["lifeExp", "gdpPercap", "pop"], multi=False, value="gdpPercap", title="Choose y-axis"
                ),
            ),
        ],
    )
    return page_country


dashboard = vm.Dashboard(
    pages=[
        create_benchmark_analysis(),
    ],
)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()