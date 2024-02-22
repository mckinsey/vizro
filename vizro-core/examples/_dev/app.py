"""Example to show dashboard configuration."""

import numpy as np
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
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


grid_interaction = vm.Page(
    title="AG Grid and Table Interaction",
    components=[
        vm.AgGrid(
            id="table_country_new",
            title="Click on a cell",
            figure=dash_ag_grid(
                id="dash_ag_grid_1",
                data_frame=px.data.gapminder(),
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


df2 = px.data.stocks()
df2["date_as_datetime"] = pd.to_datetime(df2["date"])
df2["date_str"] = df2["date"].astype("str")
df2["perc_from_float"] = np.random.rand(len(df2))
df2["random"] = np.random.uniform(-100000.000, 100000.000, len(df2))

grid_standard = vm.Page(
    title="AG Grid Default",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(
                id="dash_ag_grid_2",
                data_frame=df2,
            ),
        ),
    ],
)

grid_custom = vm.Page(
    title="AG Grid Custom",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(
                id="dash_ag_grid_3",
                data_frame=df2,
                columnDefs=[
                    {"field": "AAPL", "headerName": "Format Dollar", "cellDataType": "dollar"},
                    {"field": "AAPL", "headerName": "Format Euro", "cellDataType": "euro"},
                    {"field": "random", "headerName": "Format Numeric", "cellDataType": "numeric"},
                    {"field": "perc_from_float", "headerName": "Format Percent", "cellDataType": "percent"},
                    {
                        "field": "perc_from_float",
                        "headerName": "custom format",
                        "valueFormatter": {"function": "d3.format('.^30')(params.value)"},
                    },
                ],
            ),
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[grid_interaction, grid_standard, grid_custom],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
