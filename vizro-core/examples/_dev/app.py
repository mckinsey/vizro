"""Example to show dashboard configuration."""

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
import numpy as np

def create_sales_df():
    # Generate sample sales data for the last two years
    this_year_sales = np.random.randint(1000, 5000, size=12)
    last_year_sales = np.random.randint(1000, 5000, size=12)

    # Define months and years
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = ['2022'] * 12 + ['2023'] * 12

    # Create DataFrame
    df = pd.DataFrame({
        'Month': months * 2,
        'Sales': np.concatenate([last_year_sales, this_year_sales]),
        'Period': pd.Categorical(years, categories=['2022', '2023'], ordered=True)
    })

    return df

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

page_exec = vm.Page(
    title="Executive View",
    layout=vm.Layout(grid=[[0, 0],
                           [1, 2],
                           [1, 2],
                           [3, 4],
                           [3, 4]]),
    components=[
        vm.Container(
            title="KPI Summary",
            id="kpi-container",
            layout=vm.Layout(grid=[[0, 1, 2, 3]]),
            components=[
                vm.Graph(figure=kpi_card(data_frame=df, value=1000, ref_value=700)),
                vm.Graph(figure=kpi_card(data_frame=df, value=760, ref_value=500)),
                vm.Graph(figure=kpi_card(data_frame=df, value=170, ref_value=200)),
                vm.Graph(figure=kpi_card(data_frame=df, value=90, ref_value=80)),
            ],
        ),
        vm.Graph(figure=px.bar(df, x="Month", y="Sales", color="Period", barmode="group", title="Annual Revenue")),
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
