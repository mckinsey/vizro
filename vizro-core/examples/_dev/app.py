"""Example to show dashboard configuration."""

import random
import string

import numpy as np
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
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
            title="AG Grid - Default",
            figure=dash_ag_grid(
                # id="dash_ag_grid_2",
                data_frame=df2,
            ),
        ),
    ],
)

grid_custom = vm.Page(
    title="AG Grid Custom",
    components=[
        vm.AgGrid(
            title="Custom AG Grid",
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
                defaultColDef={"editable": True},
                # dashGridOptions = {"pagination": False},
            ),
        ),
    ],
)

num_rows = 100
num_columns = 20
column_names = ["Column_" + str(i) for i in range(num_columns)]
data = {}
for column in column_names:
    data[column] = ["".join(random.choices(string.ascii_letters, k=random.randint(5, 15))) for _ in range(num_rows)]
df_long = pd.DataFrame(data)

grid_long = vm.Page(
    title="AG Grid Long",
    components=[
        vm.AgGrid(figure=dash_ag_grid(id="dash_ag_grid_4", data_frame=df_long), title="AG Grid - long"),
    ],
)

table_long = vm.Page(
    title="Table Long",
    components=[
        vm.Table(figure=dash_data_table(id="dash_table_5", data_frame=df_long)),
    ],
)


dashboard = vm.Dashboard(
    pages=[grid_interaction, grid_standard, grid_custom, grid_long, table_long],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
