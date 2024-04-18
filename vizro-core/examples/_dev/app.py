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
def heatmap(data_frame: pd.DataFrame = None, title: str = None):
    fig = go.Figure(data=go.Heatmap(
        z=[[1, None, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, -10, 20]],
        x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        y=['Morning', 'Afternoon', 'Evening']))

    fig.update_layout(title=title)
    return fig


df = create_sales_df()
df_tips= px.data.tips()


tabs_section = vm.Tabs(
            tabs=[
                vm.Container(
                    title="Revenue",
                    components=[
                        vm.Graph(figure=px.bar(df, x="Month", y="Revenue", color="Period", barmode="group", title="Total Revenue")),
                    ],
                ),
                vm.Container(
                    title="Sales",
                    components=[
                        vm.Graph(figure=px.bar(df, x="Month", y="Sales", color="Period", barmode="group",
                                               title="Total Sales")),
                    ],
                ),
                vm.Container(
                    title="Profit",
                    components=[
                        vm.Graph(figure=px.bar(df, x="Month", y="Profit", color="Period", barmode="group",
                                               title="Total Profit")),
                    ],
                ),
                vm.Container(
                    title="Customers",
                    components=[
                        vm.Graph(figure=px.bar(df, x="Month", y="Customers", color="Period", barmode="group",
                                               title="Total Customers")),
                    ],
                ),
                vm.Container(
                    title="Products",
                    components=[
                        vm.Graph(figure=px.bar(df, x="Month", y="Products", color="Period", barmode="group",
                                               title="Total Products")),
                    ],
                ),
            ],
        )




page_exec = vm.Page(
    title="Executive View",
    layout=vm.Layout(grid=[[0, 1, 2, 3, 4],
                           [5, 5, 6, 6, 6],
                           [5, 5, 6, 6, 6],
                           [7, 7, 7, 8, 8],
                           [7, 7, 7, 8, 8]],
                     row_min_height="120px",
                     col_gap="32px", row_gap="32px"),
    components=[
        KPI(title="Revenue", value="$10.5 M", icon="arrow_circle_up", sign="up", ref_value="5.5% vs. Last Year"),
        KPI(title="Sales", value="$5.4 M", icon="arrow_circle_up", sign="up", ref_value="10.5% vs. Last Year"),
        KPI(title="Profit", value="$1.3 M", icon="arrow_circle_down", sign="down", ref_value="-4.5% vs. Last Year"),
        KPI(title="Customers", value="24.759", icon="arrow_circle_down", sign="down", ref_value="-8.5% vs. Last Year"),
        KPI(title="Products", value="100.490", icon="arrow_circle_down", sign="down", ref_value="-3.5% vs. Last Year"),
        tabs_section,
        vm.Graph(figure=heatmap(df, title="Traffic Channels")),
        vm.Container(
            title="Sales Breakdown",
            layout=vm.Layout(grid=[[0, 1, 2]]),
            components=[
                vm.Graph(figure=px.bar(df, x=[1, 2, 3, 4], y=["North", "West", "South", "East"], orientation='h', title="Sales by Region")),
                vm.Graph(figure=px.bar(df, x=[1, 2, 3, 4], y=["Cust A", "Cust B", "Cust C", "Cust D"], orientation='h',  title="Sales by Customer")),
                vm.Graph(figure=px.bar(df, x=[1, 2, 3, 4], y=["Prod A", "Prod B", "Prod C", "Prod D"], orientation='h',  title="Sales by Product"))
            ]
        ),
        vm.Graph(figure=px.area(df, x=[1, 2, 3, 4], y=[0, 2, 3, 5],  title="Sales by Product"))
    ],
)

page_reg = vm.Page(
    title="Regional View",
    components=[vm.Card(text="# Placeholder")],
)

page_cust = vm.Page(
    title="Customer View",
    components=[vm.Card(text="# Placeholder")],
)

page_prod = vm.Page(
    title="Product View",
    components=[vm.Card(text="# Placeholder")],
)

dashboard = vm.Dashboard(
    pages=[page_exec, page_reg, page_cust, page_prod],
    title="Vizro - Sales Dashboard",
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Executive View", icon="Leaderboard", pages=["Executive View"]),
                vm.NavLink(label="Regional View", icon="South America", pages=["Regional View"]),
                vm.NavLink(label="Customer View", icon="Account Circle", pages=["Customer View"]),
                vm.NavLink(label="Product View", icon="Qr code", pages=["Product View"]),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
