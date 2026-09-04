"""This is a test app to test the dashboard layout."""

import vizro.models as vm
from vizro import Vizro
from vizro.figures import kpi_card_reference
from functools import reduce
import numpy as np
from typing import List, Optional
import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture


# CUSTOM CHARTS ----------------------------------------------------------------
@capture("graph")
def bar(
    x: str,
    y: str,
    data_frame: pd.DataFrame,
    top_n: int = 15,
    custom_data: Optional[List[str]] = None,
):
    """Custom bar chart implementation.
    Based on [px.bar](https://plotly.com/python-api-reference/generated/plotly.express.bar).
    """
    df_agg = data_frame.groupby(y).agg({x: "count"}).sort_values(by=x, ascending=False).reset_index()
    fig = px.bar(
        data_frame=df_agg.head(top_n),
        x=x,
        y=y,
        orientation="h",
        text=x,
        color_discrete_sequence=["#1A85FF"],
        custom_data=custom_data,
    )
    fig.update_layout(xaxis_title="# of Complaints", yaxis={"title": "", "autorange": "reversed"})
    return fig


@capture("graph")
def area(x: str, y: str, data_frame: pd.DataFrame):
    """Custom chart to create unstacked area chart.
    Based on [go.Scatter](https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scatter.html).
    """
    df_agg = data_frame.groupby(["Year", "Month"]).agg({y: "count"}).reset_index()
    df_agg_2019 = df_agg[df_agg["Year"] == "2018"]
    df_agg_2020 = df_agg[df_agg["Year"] == "2019"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df_agg_2020[x], y=df_agg_2020[y], fill="tozeroy", name="2019", marker={"color": "#1a85ff"})
    )
    fig.add_trace(go.Scatter(x=df_agg_2019[x], y=df_agg_2019[y], fill="tonexty", name="2018", marker={"color": "grey"}))
    fig.update_layout(
        title="Complaints over time",
        xaxis_title="Date Received",
        yaxis_title="# of Complaints",
        title_pad_t=4,
        xaxis={
            "showgrid": False,
            "tickmode": "array",
            "tickvals": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "ticktext": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        },
    )
    return fig


@capture("graph")
def pie(
    names: str,
    values: str,
    data_frame: pd.DataFrame = None,
    title: Optional[str] = None,
):
    """Custom pie chart implementation.
    Based on [px.pie](https://plotly.com/python-api-reference/generated/plotly.express.pie).
    """
    df_agg = data_frame.groupby(names).agg({values: "count"}).reset_index()
    fig = px.pie(
        data_frame=df_agg,
        names=names,
        values=values,
        color=names,
        color_discrete_map={
            "Closed with explanation": "#1a85ff",
            "Closed with monetary relief": "#d41159",
            "Closed with non-monetary relief": "#adbedc",
            "Closed without relief": "#7ea1ee",
            "Closed with relief": "#df658c",
            "Closed": "#1a85ff",
        },
        title=title,
        hole=0.4,
    )
    fig.update_layout(legend_x=1, legend_y=1, title_pad_t=2, margin={"l": 0, "r": 0, "t": 60, "b": 0})
    return fig


def fill_na_with_random(df, column):
    """Fills missing values in a column with random values from the same column."""
    non_na_values = df[column].dropna().values
    df[column] = df[column].apply(lambda x: np.random.choice(non_na_values) if pd.isna(x) else x)
    return df[column]


def clean_data_and_add_columns(data: pd.DataFrame):
    """Tidies the original data set, adds new columns, and changes cell values for the purpose of this example."""
    data = data.rename(
        columns={
            "Date Sumbited": "Date Submitted",
            "Submitted via": "Channel",
            "Company response to consumer": "Company response - detailed",
        },
    )

    # Clean cell values and/or assign different values for the purpose of this example
    data["Company response - detailed"] = data["Company response - detailed"].replace("Closed", "Closed without relief")
    data["State"] = data["State"].replace("UNITED STATES MINOR OUTLYING ISLANDS", "UM")
    data["State"] = fill_na_with_random(data, "State")
    data["Consumer disputed?"] = data["Consumer disputed?"].fillna("No")

    # Convert to correct data type
    data["Date Received"] = pd.to_datetime(data["Date Received"], format="%m/%d/%y").dt.strftime("%Y-%m-%d")

    # Create additional columns
    data["Month"] = pd.to_datetime(data["Date Received"], format="%Y-%m-%d").dt.strftime("%m")
    data["Year"] = pd.to_datetime(data["Date Received"], format="%Y-%m-%d").dt.strftime("%Y")
    data["Company response"] = np.where(
        data["Company response - detailed"].str.contains("Closed"), "Closed", data["Company response - detailed"]
    )
    data["Company response - Closed"] = np.where(
        data["Company response - detailed"].str.contains("Closed"), data["Company response - detailed"], "Not closed"
    )

    # Filter 2018 and 2019 only
    data = data[(data["Year"].isin(["2018", "2019"]))]
    return data


def create_data_for_kpi_cards(data):
    """Formats and aggregates the data for the KPI cards."""
    total_complaints = (
        data.groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Total Complaints"})
        .reset_index()
    )
    closed_complaints = (
        data[data["Company response"] == "Closed"]
        .groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Closed Complaints"})
        .reset_index()
    )
    timely_response = (
        data[data["Timely response?"] == "Yes"]
        .groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Timely response"})
        .reset_index()
    )
    closed_without_cost = (
        data[data["Company response - Closed"] != "Closed with monetary relief"]
        .groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Closed w/o cost"})
        .reset_index()
    )
    consumer_disputed = (
        data[data["Consumer disputed?"] == "Yes"]
        .groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Consumer disputed"})
        .reset_index()
    )

    # Merge all data frames into one
    dfs_to_merge = [total_complaints, closed_complaints, timely_response, closed_without_cost, consumer_disputed]
    df_kpi = reduce(lambda left, right: pd.merge(left, right, on="Year", how="outer"), dfs_to_merge)

    # Calculate percentages
    df_kpi.fillna(0, inplace=True)
    df_kpi["Closed Complaints"] = df_kpi["Closed Complaints"] / df_kpi["Total Complaints"] * 100
    df_kpi["Open Complaints"] = 100 - df_kpi["Closed Complaints"]
    df_kpi["Timely response"] = df_kpi["Timely response"] / df_kpi["Total Complaints"] * 100
    df_kpi["Closed w/o cost"] = df_kpi["Closed w/o cost"] / df_kpi["Total Complaints"] * 100
    df_kpi["Consumer disputed"] = df_kpi["Consumer disputed"] / df_kpi["Total Complaints"] * 100

    # Pivot the dataframe and flatten
    df_kpi["index"] = 0
    df_kpi = df_kpi.pivot(
        index="index",
        columns="Year",
        values=[
            "Total Complaints",
            "Closed Complaints",
            "Open Complaints",
            "Timely response",
            "Closed w/o cost",
            "Consumer disputed",
        ],
    )
    df_kpi.columns = [f"{kpi}_{year}" for kpi, year in df_kpi.columns]
    return df_kpi


# DATA --------------------------------------------------------------------------------------------
df_complaints = pd.read_csv("https://query.data.world/s/glbdstahsuw3hjgunz3zssggk7dsfu?dws=00000")
df_complaints = clean_data_and_add_columns(df_complaints)
df_kpi_cards = create_data_for_kpi_cards(df_complaints)


# SUB-SECTIONS ------------------------------------------------------------------------------------
kpi_banner = vm.Container(
    layout=vm.Flex(direction="row"),
    components=[
        vm.Figure(
            id="kpi-reverse-coloring",
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Total Complaints_2019",
                reference_column="Total Complaints_2018",
                title="Total Complaints",
                value_format="{value:.0f}",
                reference_format="vs. 2018 ({reference:.0f})",
                icon="person",
                size="default",
                reverse_color=True,
            ),
        ),
        vm.Figure(
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Closed Complaints_2019",
                reference_column="Closed Complaints_2018",
                title="Closed Complaints",
                value_format="{value:.1f}%",
                reference_format=" vs. 2018 ({reference:.1f}%)",
                icon="inventory",
                size="default",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Timely response_2019",
                reference_column="Timely response_2018",
                title="Timely Response",
                value_format="{value:.1f}%",
                reference_format="vs. 2018 ({reference:.1f}%)",
                icon="timer",
                size="default",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Closed w/o cost_2019",
                reference_column="Closed w/o cost_2018",
                title="Closed w/o cost",
                value_format="{value:.1f}%",
                reference_format="vs. 2018 ({reference:.1f}%)",
                icon="payments",
                size="default",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Consumer disputed_2019",
                reference_column="Consumer disputed_2018",
                title="Consumer disputed",
                value_format="{value:.1f}%",
                reference_format="vs. 2018 ({reference:.1f}%)",
                icon="sentiment_dissatisfied",
                size="default",
            )
        ),
    ],
)

bar_charts_tabbed = vm.Tabs(
    tabs=[
        vm.Container(
            title="By Product",
            components=[
                vm.Graph(
                    figure=bar(
                        data_frame=df_complaints,
                        y="Product",
                        x="Complaint ID",
                    ),
                )
            ],
        ),
    ],
)

# PAGES --------------------------------------------------------------------------------------
page_exec = vm.Page(
    title="Executive View",
    layout=vm.Grid(
        grid=[
            [0, 0],
            [0, 0],
            [1, 2],
            [1, 2],
            [1, 2],
            [1, 3],
            [1, 3],
            [1, 3],
        ],
    ),
    components=[
        kpi_banner,
        bar_charts_tabbed,
        vm.Graph(figure=area(data_frame=df_complaints, y="Complaint ID", x="Month")),
        vm.Graph(
            figure=pie(
                data_frame=df_complaints[df_complaints["Company response - Closed"] != "Not closed"],
                values="Complaint ID",
                names="Company response - Closed",
                title="Closed company responses",
            )
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[page_exec],
    title="Cumulus Financial Corp. - Fiscal Year 2019",
)

app = Vizro().build(dashboard)
if __name__ == "__main__":
    app.run()
