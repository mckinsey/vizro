"""Example to show dashboard configuration."""

from typing import List, Literal, Optional

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from utils._helper import clean_data_and_add_columns
from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

# DATA --------------------------------------------------------------------------------------------
df_complaints = pd.read_csv("data/Financial Consumer Complaints.csv")
df_complaints = clean_data_and_add_columns(df_complaints)
print(df_complaints.head(10))

# TODO: Overall - Do everything vs. last year
# TODO: Overall - Consolidate colors and gaps

# TODO: Bar - How to enable drill-downs for Issue/Sub-issue and Product/Sub-product?
# TODO: Bar - Reformat numbers with commas in bar chart
# TODO: Bar - Left-align y-axis labels
# TODO: Bar - Shorten labels
# TODO: Line - Customise function to always show selected year vs. past year
# TODO: Pie - Manipulate data to show sub-categories of closed company responses

# TODO: Table-view - Check why date format does not work
# TODO: Table-view - Check how to specify different % column widths while still using 100% of available screen width
# TODO: Table-view - Replace with appropriate icons
# TODO: Table-view - Find better color sequences for last column


def create_sales_df():
    # Define months and years
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = ["Last Year"] * 12 + ["Current"] * 12

    # Create DataFrame
    df = pd.DataFrame(
        {
            "Month": months * 2,
            "Revenue": np.concatenate(
                [np.random.randint(8000000, 13000000, size=12), np.random.randint(8000000, 13000000, size=12)]
            ),
            "Sales": np.concatenate(
                [np.random.randint(3000000, 6000000, size=12), np.random.randint(3000000, 6000000, size=12)]
            ),
            "Profit": np.concatenate(
                [np.random.randint(800000, 1300000, size=12), np.random.randint(800000, 1300000, size=12)]
            ),
            "Customers": np.concatenate(
                [np.random.randint(20000, 28000, size=12), np.random.randint(20000, 28000, size=12)]
            ),
            "Products": np.concatenate(
                [np.random.randint(95000, 130000, size=12), np.random.randint(95000, 130000, size=12)]
            ),
            "Period": pd.Categorical(years, categories=["Last Year", "Current"], ordered=True),
        }
    )
    return df


df = create_sales_df()
df_tips = px.data.tips()


# TODO: Think more about potential API - this is just a quick mock-up. Types will likely change.
class KPI(vm.VizroBaseModel):
    """New custom component `KPI`."""

    type: Literal["kpi"] = "kpi"
    title: str
    value: str
    icon: str
    sign: Literal["up", "down"]
    ref_value: str

    def build(self):
        return dbc.Card(
            [
                html.H4(self.title, className="card-title"),
                html.P(self.value, className="card-value"),
                html.Span(
                    [
                        html.Span(self.icon, className=f"material-symbols-outlined {self.sign}"),
                        html.Span(self.ref_value, className=self.sign),
                    ],
                    className="card-ref-value",
                ),
            ],
            className=f"card-border-{self.sign}",
        )


vm.Page.add_type("components", KPI)
vm.Container.add_type("components", KPI)


@capture("graph")
def kpi_card(data_frame: pd.DataFrame = None, value: int = None, ref_value: int = None):
    fig = go.Figure(
        go.Indicator(
            mode="number+delta",
            value=value,
            number={"prefix": "$", "suffix": "m"},
            title={"text": "Accounts<br><span style='font-size:0.8em;color:gray'>vs. last year</span><br>"},
            delta={"reference": ref_value, "relative": True},
        )
    )
    fig.update_layout()
    return fig


@capture("graph")
def stacked_bar(data_frame=None):
    fig = go.Figure(
        go.Bar(
            y=["Products", "Customers", "Profit", "Sales", "Revenue"],
            x=[28, 22, 30, 15, 27],
            text=["28%", "22%", "30%", "15%", "27%"],
            textposition="inside",
            name="North",
            marker_color="#1A85FF",
            orientation="h",
        )
    )
    fig.add_trace(
        go.Bar(
            y=["Products", "Customers", "Profit", "Sales", "Revenue"],
            x=[26, 25, 25, 20, 23],
            text=["26%", "25%", "25%", "20%", "23%"],
            textposition="inside",
            name="West",
            marker_color="#749ff9",
            orientation="h",
        )
    )
    fig.add_trace(
        go.Bar(
            y=["Products", "Customers", "Profit", "Sales", "Revenue"],
            x=[19, 28, 25, 35, 30],
            text=["19%", "28%", "25%", "35%", "30%"],
            textposition="inside",
            name="South",
            marker_color="#a3baf3",
            orientation="h",
        )
    )
    fig.add_trace(
        go.Bar(
            y=["Products", "Customers", "Profit", "Sales", "Revenue"],
            x=[27, 25, 20, 30, 20],
            text=["27%", "25%", "20%", "30%", "20%"],
            textposition="inside",
            name="East",
            marker_color="#c9d6eb",
            orientation="h",
        )
    )
    fig.update_layout(
        title="Regional distribution", barmode="relative", title_pad_l=0, title_pad_t=4, margin=dict(l=0, r=0, t=32)
    )
    return fig


@capture("graph")
def bar(x: str, y: str, data_frame: pd.DataFrame = None, top_n: int = 15, color_discrete_sequence: List[str] = None):
    df_agg = data_frame.groupby([y]).aggregate({x: "count"}).sort_values(by=x, ascending=False).reset_index()

    fig = px.bar(
        data_frame=df_agg.head(top_n),
        x=x,
        y=y,
        orientation="h",
        text=x,
        color_discrete_sequence=color_discrete_sequence,
    )
    fig.update_layout(xaxis_title="# of Complaints", yaxis=dict(title="", autorange="reversed"))
    return fig


@capture("graph")
def line(x: str, y: str, data_frame: pd.DataFrame = None, color_discrete_sequence: List[str] = None):
    df_agg = data_frame.groupby([x]).aggregate({y: "count"}).reset_index()
    fig = px.area(
        data_frame=df_agg,
        x=x,
        y=y,
        color_discrete_sequence=color_discrete_sequence,
        title="Complaints over time - monthly",
    )
    fig.update_layout(xaxis_title="Date Received", yaxis_title="# of Complaints", title_pad_t=4)
    return fig


@capture("graph")
def pie(
    names: str,
    values: str,
    data_frame: pd.DataFrame = None,
    color_discrete_sequence: List[str] = None,
    title: Optional[str] = None,
):
    df_agg = data_frame.groupby([names]).aggregate({values: "count"}).reset_index()

    fig = px.pie(
        data_frame=df_agg,
        names=names,
        values=values,
        color_discrete_sequence=color_discrete_sequence,
        title=title,
        hole=0.4,
    )

    fig.update_layout(legend_x=1, legend_y=1, title_pad_t=4, margin=dict(l=0, r=24, t=40, b=16))
    return fig


@capture("graph")
def chloropleth(data_frame: pd.DataFrame = None):
    import json
    from urllib.request import urlopen

    with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as response:
        counties = json.load(response)

    import pandas as pd

    data_frame = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv", dtype={"fips": str}
    )
    data_frame["unemp"] = data_frame["unemp"] / 4
    data_frame.loc[1::5, "unemp"] *= -1
    fig = px.choropleth(
        data_frame,
        geojson=counties,
        locations="fips",
        color="unemp",
        color_continuous_scale=["#d41159", "#d41159", "#d41159", "#d3d3d3", "#1a85ff", "#1a85ff", "#1a85ff"],
        color_continuous_midpoint=0,
        scope="usa",
        labels={"unemp": "% change"},
    )
    fig.update_layout(title_text="Change in revenue by ZIP code", margin=dict(l=0, r=0, t=0), title_pad_t=20)
    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "right"}})
    return fig


page_exec = vm.Page(
    title="Executive View",
    layout=vm.Layout(
        grid=[
            [0, 1, 2, 3, 4, 5],
            [0, 1, 2, 3, 4, 5],
            [6, 6, 6, 7, 7, 7],
            [6, 6, 6, 7, 7, 7],
            [6, 6, 6, 7, 7, 7],
            [6, 6, 6, 7, 7, 7],
            [6, 6, 6, 7, 7, 7],
            [6, 6, 6, 8, 8, 8],
            [6, 6, 6, 8, 8, 8],
            [6, 6, 6, 8, 8, 8],
            [6, 6, 6, 8, 8, 8],
        ],
        col_gap="32px",
        row_gap="32px",
    ),
    components=[
        KPI(title="Total Complaints", value="75.513", icon="arrow_circle_up", sign="up", ref_value="5.5% vs. Last Year"),
        KPI(
            title="Closed Complaints", value="75.230 (99.6%)", icon="arrow_circle_down", sign="down", ref_value="-4.5% vs. Last Year"
        ),
        KPI(
            title="Open Complaints", value="283 (0.4%)", icon="arrow_circle_down", sign="down", ref_value="-4.5% vs. Last Year"
        ),
        KPI(title="Timely Response", value="98.1%", icon="arrow_circle_up", sign="up", ref_value="10.5% vs. Last Year"),
        KPI(
            title="Resolved at no cost",
            value="84.5%",
            icon="arrow_circle_down",
            sign="down",
            ref_value="-8.5% vs. Last Year",
        ),
        KPI(title="Consumer disputed", value="9.5%", icon="arrow_circle_up", sign="up", ref_value="10.5% vs. Last Year"),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="By Issue",
                    components=[
                        vm.Graph(
                            id="bar-issue",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Issue",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
                vm.Container(
                    title="By Product",
                    components=[
                        vm.Graph(
                            id="bar-product",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Product",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
                vm.Container(
                    title="By Channel",
                    components=[
                        vm.Graph(
                            id="bar-channel",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Channel",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
                vm.Container(
                    title="By Region",
                    components=[
                        vm.Graph(
                            id="bar-region",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Region",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
            ],
        ),
        vm.Graph(
            id="line-date",
            figure=line(
                data_frame=df_complaints, y="Complaint ID", x="Year-Month Received", color_discrete_sequence=["#1A85FF"]
            ),
        ),
        vm.Graph(
            figure=pie(
                data_frame=df_complaints[df_complaints["Company response - Closed"] != "Not closed"],
                values="Complaint ID",
                names="Company response - Closed",
                title="Resolved Company Responses",
            )
        ),
    ],
)

# TABLE --------------------------------------------------------------------------------------------
rain = "![alt text: rain](https://www.ag-grid.com/example-assets/weather/rain.png)"
sun = "![alt text: sun](https://www.ag-grid.com/example-assets/weather/sun.png)"
df_complaints["Timely response?"] = df_complaints["Timely response?"].apply(
    lambda x: f"No {rain} " if x == "No" else f"Yes {sun} "
)

cell_style = {
    "styleConditions": [
        {
            "condition": "params.value == 'Closed with explanation'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed with monetary relief'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed with non-monetary relief'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed without relief'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed with relief'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'In progress'",
            "style": {"backgroundColor": "orange"},
        },
        {
            "condition": "params.value == 'Untimely response'",
            "style": {"backgroundColor": "#D41159"},
        },
    ]
}


column_defs = [
    {"field": "Complaint ID", "cellDataType": "text", "headerName": "ID"},
    {"field": "Date Received", "cellDataType": "text"},  # Why doesn't date work even after reformatting?
    {"field": "Channel", "cellDataType": "text"},
    {"field": "State", "cellDataType": "text"},
    {"field": "Product", "cellDataType": "text"},
    {"field": "Sub-product", "cellDataType": "text"},
    {"field": "Issue", "cellDataType": "text"},
    {"field": "Sub-issue", "cellDataType": "text"},
    {"field": "Timely response?", "cellRenderer": "markdown"},
    {
        "field": "Company response - detailed",
        "cellDataType": "text",
        "cellStyle": cell_style,
        "headerName": "Company response",
    },
]

page_table = vm.Page(
    title="List of complaints",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(
                data_frame=df_complaints,
                columnDefs=column_defs,
                columnSize="autoSize",
                defaultColDef={"minWidth": 0, "flex": 1},
            )
        )
    ],
)

page_region = vm.Page(
    title="Regional View",
    components=[vm.Graph(figure=stacked_bar(df)), vm.Graph(figure=chloropleth(df))],
)


dashboard = vm.Dashboard(
    pages=[page_exec, page_region, page_table],
    title="Cumulus Financial - Complaints",
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Executive View", icon="Leaderboard", pages=["Executive View"]),
                vm.NavLink(label="Regional View", icon="South America", pages=["Regional View"]),
                vm.NavLink(label="Table View", icon="Table View", pages=["List of complaints"]),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
