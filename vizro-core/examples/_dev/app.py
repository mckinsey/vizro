"""Example to show dashboard configuration."""

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
import numpy as np
import dash_bootstrap_components as dbc
from dash import html
from typing import Literal
from vizro.tables import dash_ag_grid

# DATA --------------------------------------------------------------------------------------------
df_complaints = pd.read_csv("data/Financial Consumer Complaints.csv")
df_complaints['Date Received'] = pd.to_datetime(df_complaints['Date Received'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
df_complaints['Date Sumbited'] = pd.to_datetime(df_complaints['Date Sumbited'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
df_complaints.rename(columns={"Date Sumbited": "Date Submitted"}, inplace=True)
print(df_complaints)

def create_sales_df():
    # Define months and years
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = ['Last Year'] * 12 + ['Current'] * 12

    # Create DataFrame
    df = pd.DataFrame({
        'Month': months * 2,
        'Revenue': np.concatenate([np.random.randint(8000000, 13000000, size=12), np.random.randint(8000000, 13000000, size=12)]),
        'Sales': np.concatenate([np.random.randint(3000000, 6000000, size=12), np.random.randint(3000000, 6000000, size=12)]),
        'Profit': np.concatenate([np.random.randint(800000, 1300000, size=12), np.random.randint(800000, 1300000, size=12)]),
        'Customers': np.concatenate([np.random.randint(20000, 28000, size=12), np.random.randint(20000, 28000, size=12)]),
        'Products': np.concatenate([np.random.randint(95000, 130000, size=12), np.random.randint(95000, 130000, size=12)]),
        'Period': pd.Categorical(years, categories=['Last Year', 'Current'], ordered=True)
    })
    return df


df = create_sales_df()
df_tips= px.data.tips()



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
        return dbc.Card([
                html.H3(self.title, className="card-title"),
                html.P(self.value, className="card-value"),
                html.Span([
                    html.Span(self.icon, className=f"material-symbols-outlined {self.sign}"),
                    html.Span(self.ref_value, className=self.sign)
            ], className="card-ref-value"),
        ], className=f"card-border-{self.sign}")

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
    fig = go.Figure(go.Bar(
        y=['Products', 'Customers', 'Profit', 'Sales', 'Revenue'],
        x=[28, 22, 30, 15, 27],
        text=["28%", "22%", "30%", "15%", "27%"],
        textposition="inside",
        name='North', marker_color='#1A85FF', orientation="h"))
    fig.add_trace(go.Bar(
        y=['Products', 'Customers', 'Profit', 'Sales', 'Revenue'],
        x=[26, 25, 25, 20, 23],
        text=["26%", "25%", "25%", "20%", "23%"],
        textposition="inside",
        name='West', marker_color='#749ff9', orientation="h"))
    fig.add_trace(go.Bar(
        y=['Products', 'Customers', 'Profit', 'Sales', 'Revenue'],
        x=[19, 28, 25, 35, 30],
        text=["19%", "28%", "25%", "35%", "30%"],
        textposition="inside",
        name='South', marker_color='#a3baf3', orientation="h"))
    fig.add_trace(go.Bar(
        y=['Products', 'Customers', 'Profit', 'Sales', 'Revenue'],
        x=[27, 25, 20, 30, 20],
        text=["27%", "25%", "20%", "30%", "20%"],
        textposition="inside",
        name='East', marker_color='#c9d6eb', orientation="h"))
    fig.update_layout(title="Regional distribution", barmode='relative', title_pad_l=0, title_pad_t=4, margin=dict(l=0, r=0, t=32))
    return fig

@capture("graph")
def heatmap(data_frame: pd.DataFrame = None, title: str = None):
    fig = go.Figure(data=go.Heatmap(
        z=[[1, None, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, -10, 20]],
        x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        y=['Morning', 'Afternoon', 'Evening']))

    fig.update_layout(title=title)
    return fig


@capture("graph")
def bar(x: str, y: str, color: str, barmode: str, data_frame: pd.DataFrame = None):
    fig = px.bar(data_frame=data_frame, x=x, y=y, color=color, barmode=barmode, color_discrete_sequence=["#a3a5a9", "#1A85FF"])
    fig.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=0, r=0, t=0), title_pad_t=0,
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=-0.6,
                          xanchor="left",
                          x=-0.1
                      )
                      )
    return fig


@capture("graph")
def chloropleth(data_frame: pd.DataFrame = None):
    from urllib.request import urlopen
    import json
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    import pandas as pd
    data_frame = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                     dtype={"fips": str})
    data_frame['unemp'] = data_frame['unemp']/4
    data_frame.loc[1::5, 'unemp'] *= -1
    fig = px.choropleth(data_frame, geojson=counties, locations='fips', color='unemp',
                           color_continuous_scale=['#d41159', '#d41159', '#d41159', '#d3d3d3', '#1a85ff', '#1a85ff', '#1a85ff'],
                           color_continuous_midpoint=0,
                           scope="usa",
                           labels={'unemp':'% change'}
                          )
    fig.update_layout(title_text='Change in revenue by ZIP code', margin=dict(l=0, r=0, t=0), title_pad_t=20)
    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "right"}})
    return fig




tabs_section = vm.Tabs(
            tabs=[
                vm.Container(
                    title="Revenue",
                    components=[
                        vm.Graph(figure=bar(data_frame=df, x="Month", y="Revenue", color="Period", barmode="group")),
                    ],
                ),
                vm.Container(
                    title="Sales",
                    components=[
                        vm.Graph(figure=bar(data_frame=df, x="Month", y="Sales", color="Period", barmode="group")),
                    ],
                ),
                vm.Container(
                    title="Profit",
                    components=[
                        vm.Graph(figure=bar(data_frame=df, x="Month", y="Profit", color="Period", barmode="group")),
                    ],
                ),
                vm.Container(
                    title="Customers",
                    components=[
                        vm.Graph(figure=bar(data_frame=df, x="Month", y="Customers", color="Period", barmode="group")),
                    ],
                ),
                vm.Container(
                    title="Products",
                    components=[
                        vm.Graph(figure=bar(data_frame=df, x="Month", y="Products", color="Period", barmode="group")),
                    ],
                ),
            ],
        )




page_exec = vm.Page(
    title="Executive View",
    layout=vm.Layout(grid=[[0, 1, 2, 3, 4, 5],
                           [6, 6, 8, 8, 10, 10],
                           [6, 6, 8, 8, 10, 10],
                           [7, 7, 9, 9, 10, 10],
                           [7, 7, 9, 9, 11, 11]],
                     row_min_height="100px",
                     col_gap="32px", row_gap="32px"),
    components=[
        KPI(title="Revenue", value="$10.5 M", icon="arrow_circle_up", sign="up", ref_value="5.5% vs. Last Year"),
        KPI(title="Sales", value="$5.4 M", icon="arrow_circle_up", sign="up", ref_value="10.5% vs. Last Year"),
        KPI(title="Profit", value="$1.3 M", icon="arrow_circle_down", sign="down", ref_value="-4.5% vs. Last Year"),
        KPI(title="Customers", value="24.759", icon="arrow_circle_down", sign="down", ref_value="-8.5% vs. Last Year"),
        KPI(title="Products", value="100.490", icon="arrow_circle_down", sign="down", ref_value="-3.5% vs. Last Year"),
        KPI(title="Products", value="100.490", icon="arrow_circle_down", sign="down", ref_value="-3.5% vs. Last Year"),
        tabs_section,
        vm.Graph(figure=stacked_bar(df)),
        vm.Graph(figure=px.bar(df, x=[1, 2, 3, 4], y=["Cust A", "Cust B", "Cust C", "Cust D"], orientation='h',
                               title="Sales by Customer")),
        vm.Graph(figure=px.bar(df, x=np.random.randint(150000, 900000, size=10), y=["Phones", "Chairs", "Storage", "Tables", "Binders", "Machines", "Accessories", "Copiers", "Bookcases", "Appliances"], orientation='h',
                               title="Sales by Product Categories")),
        vm.Graph(figure=chloropleth(df)),
        vm.Card(text="# Placeholder"),
    ],
)

# TABLE --------------------------------------------------------------------------------------------
# TODO: Check why date format does not work
# TODO: Check how to specify different % column widths while still using 100% of available screen width
# TODO: Replace with appropriate icons
# TODO: Find better color sequences for last column
rain =  "![alt text: rain](https://www.ag-grid.com/example-assets/weather/rain.png)"
sun = "![alt text: sun](https://www.ag-grid.com/example-assets/weather/sun.png)"
df_complaints["Timely response?"] = df_complaints["Timely response?"].apply(lambda x: f"No {rain} " if x == 'No' else f"Yes {sun} ")

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


column_defs = [{"field": "Complaint ID", "cellDataType": "text", "headerName": "ID"},
 {"field": "Date Received", "cellDataType": "text"}, # Why doesn't date work even after reformatting?
 {"field": "Submitted via", "cellDataType": "text", "headerName": "Channel"},
 {"field": "State", "cellDataType": "text"},
 {"field": "Product", "cellDataType": "text"},
 {"field": "Sub-product", "cellDataType": "text"},
 {"field": "Issue", "cellDataType": "text"},
 {"field": "Sub-issue", "cellDataType": "text"},
 {"field": "Timely response?", "cellRenderer": "markdown"},
 {"field": "Company response to consumer", "cellDataType": "text", "cellStyle": cell_style, "headerName": "Company response"},]

page_table = vm.Page(
    title="List of complaints",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(
                data_frame=df_complaints,
                columnDefs=column_defs,
                columnSize="autoSize",
                defaultColDef= {"minWidth": 0, "flex": 1}

        )
        )
    ],
)


dashboard = vm.Dashboard(
    pages=[page_exec, page_table],
    title="Financial Complaints Dashboard",
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Executive View", icon="Leaderboard", pages=["Executive View"]),
                vm.NavLink(label="Table View", icon="Table View", pages=["List of complaints"]),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
