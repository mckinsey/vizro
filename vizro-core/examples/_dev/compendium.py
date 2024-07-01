"""Example to show dashboard configuration specified as pydantic models."""

from datetime import datetime
from typing import Callable, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm  # This is fine because we define __all__ in hyphen.models.

# ruff: noqa: F403, F405
# Alternatively you could do `import hyphen.models as hm` and then use the `hm` namespace for all models
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture


def retrieve_empty_dataframe():
    """This function returns an empty dataframe."""
    return pd.DataFrame()


def retrieve_slope_data():
    """This function returns data for slope chart."""
    data = [
        ["A", 17743, 25032],
        ["B", 10216, 15672],
        ["C", 3953, 4821],
        ["D", 12568, 8734],
        ["E", 5601, 4350],
    ]

    df = pd.DataFrame(data, columns=["cats", "start", "end"])
    return df


@capture("graph")
def slope(data_frame):
    fig = go.Figure()

    for idx, cat in enumerate(data_frame["cats"].to_list()):
        fig.add_trace(
            go.Scatter(
                x=["Year 2022", "Year 2023"],
                y=[
                    int(data_frame.loc[data_frame["cats"] == cat]["start"]),
                    int(data_frame.loc[data_frame["cats"] == cat]["end"]),
                ],
                name=f"Trace {cat}",
                mode="lines+markers+text",
                text=[
                    int(data_frame.loc[data_frame["cats"] == cat]["start"]),
                    int(data_frame.loc[data_frame["cats"] == cat]["end"]),
                ],
                textposition=["middle left", "middle right"],
                line_color=px.colors.sequential.Blues[::-1][idx],
            )
        )

    return fig


@capture("graph")
def barcode(data_frame):
    fig = go.Figure()

    for idx, species in enumerate(data_frame["species"].unique().tolist()):
        fig.add_trace(
            go.Scatter(
                x=data_frame.loc[data_frame["species"] == species]["sepal_width"],
                y=[species.capitalize()] * len(data_frame.loc[data_frame["species"] == species]["sepal_width"]),
                mode="markers",
                name=species.capitalize(),
                legendgroup=species.capitalize(),
                showlegend=True,
                marker=dict(color=px.colors.sequential.Blues[::-1][idx], symbol="line-ns-open"),
            )
        )

    fig.update_layout(
        xaxis_title="Sepal Width",
        yaxis_title="Species",
    )

    return fig


def retrieve_waterfall_data():
    """This function returns data for slope chart."""
    measure = ["relative", "relative", "total", "relative", "relative", "total"]
    x = ["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"]
    y = [60, 80, 0, -40, -20, 0]

    df = pd.DataFrame({"measure": measure, "x": x, "y": y})
    return df


@capture("graph")
def waterfall(data_frame):

    text_list = [str(val) if val != 0 else "Total" for val in data_frame["y"].to_list()]

    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=data_frame["measure"].to_list(),
            x=data_frame["x"].to_list(),
            textposition="outside",
            text=text_list,
            y=data_frame["y"].to_list(),
            decreasing={"marker": {"color": px.colors.sequential.Blues[::-1][1]}},
            increasing={"marker": {"color": px.colors.sequential.Blues[::-1][2]}},
            totals={"marker": {"color": px.colors.sequential.Blues[::-1][0]}},
        )
    )

    return fig


def retrieve_venn_data():
    """This function returns data for slope chart."""
    circle = ["1", "2", "3"]
    x0 = [0, 1.5, 0.75]
    y0 = [0, 0, 1.25]
    x1 = [2, 3.5, 2.75]
    y1 = [2, 2, 3.25]

    df = pd.DataFrame({"circle": circle, "x0": x0, "y0": y0, "x1": x1, "y1": y1})
    return df


@capture("graph")
def venn(data_frame):

    fig = go.Figure()

    for idx, circle in enumerate(data_frame["circle"].to_list()):
        fig.add_shape(
            type="circle",
            line_color=px.colors.sequential.Blues[::-1][idx],
            fillcolor=px.colors.sequential.Blues[::-1][idx],
            x0=float(data_frame.loc[data_frame["circle"] == circle]["x0"]),
            y0=float(data_frame.loc[data_frame["circle"] == circle]["y0"]),
            x1=float(data_frame.loc[data_frame["circle"] == circle]["x1"]),
            y1=float(data_frame.loc[data_frame["circle"] == circle]["y1"]),
        )

    fig.update_shapes(opacity=0.3, xref="x", yref="y")

    fig.update_layout(
        xaxis_range=[-0.7, 4.2],
        yaxis_range=[-0.2, 3.7],
        xaxis_visible=False,
        xaxis_showticklabels=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        margin=dict(l=20, r=20, b=100),
    )

    fig.update_layout(
        margin=dict(l=20, r=20, b=100),
    )

    return fig


def retrieve_lollipop_data():
    """This function returns data for slope chart."""
    x = ["A", "B", "C", "D", "E", "F"]
    y = [15, -25, -10, 30, 20, 5]

    df = pd.DataFrame({"x": x, "y": y})
    return df


@capture("graph")
def lollipop(data_frame):

    fig = go.Figure()

    for i in range(0, len(data_frame["x"])):
        fig.add_trace(
            go.Scatter(
                x=[data_frame["x"].to_list()[i], data_frame["x"].to_list()[i]],
                y=[0, data_frame["y"].to_list()[i]],
                name=f"Customer Segment {data_frame['x'].to_list()[i]}",
                mode="markers+lines",
                marker=dict(size=10, color=px.colors.sequential.Blues[::-1][i], angleref="previous"),
                line=dict(width=2, color=px.colors.sequential.Blues[::-1][i]),
            )
        )

    fig.update_layout(
        xaxis_title="Customer Segment",
        yaxis_title="Development last month",
        xaxis=dict(showline=False),
    )

    return fig


def retrieve_dot_data():
    """This function returns data for slope chart."""
    x0 = [25000, 20000, 45000, 8000, 12000]
    x1 = [46000, 30000, 57000, 60000, 29000]
    y = ["Accessories", "Bookcase", "Chairs", "Copiers", "Furnishing"]

    df = pd.DataFrame({"x0": x0, "x1": x1, "y": y})
    return df


@capture("graph")
def dot_pot(data_frame):

    fig = go.Figure()

    for i in range(0, len(data_frame["y"])):
        fig.add_trace(
            go.Scatter(
                x=[data_frame["x0"].to_list()[i], data_frame["x1"].to_list()[i]],
                y=[data_frame["y"].to_list()[i], data_frame["y"].to_list()[i]],
                name=data_frame["y"].to_list()[i],
                mode="markers+lines",
                marker=dict(size=10, color=px.colors.sequential.Blues[::-1][i]),
                line=dict(width=2, color=px.colors.sequential.Blues[::-1][i]),
            )
        )

    fig.update_layout(
        yaxis_title="Office Material",
        xaxis_title="Cost range",
        xaxis=dict(showline=False),
    )

    return fig


def retrieve_surplus_data():
    """This function returns data for surplus chart."""
    start_date = "2023-06-01"
    forecasting = "2023-06-15"
    df = pd.DataFrame(
        {
            "date": pd.date_range(start_date, forecasting, freq="D"),
            "positive": [
                0,
                0,
                162783,
                226389,
                0,
                0,
                0,
                0,
                0,
                129987,
                180954,
                246098,
                0,
                0,
                0,
            ],
            "negative": [
                -175287,
                0,
                0,
                0,
                0,
                -173940,
                -137233,
                -183940,
                0,
                0,
                0,
                0,
                0,
                -103940,
                -137233,
            ],
        }
    )

    return df


@capture("graph")
def surplus(data_frame):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data_frame["date"].to_list(),
            y=data_frame["positive"].to_list(),
            fill=None,
            mode="lines",
            showlegend=False,
            line_color=px.colors.sequential.Blues[::-1][2],
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_frame["date"].to_list(),
            y=[0] * len(data_frame["date"].to_list()),
            fill="tonexty",
            mode="lines",
            name="Positive Sentiment",
            line_color=px.colors.sequential.Blues[::-1][2],
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_frame["date"].to_list(),
            y=data_frame["negative"].to_list(),
            fill="tonexty",
            mode="lines",
            name="Negative Sentiment",
            line_color=px.colors.sequential.Blues[::-1][0],
        )
    )

    return fig


def retrieve_butterfly_data():
    """This function returns data for gant chart."""
    cat = ["Art", "Chair", "Outdoor"]
    a = [8, 6, 2]
    b = [-4, -8, -1]

    df = pd.DataFrame({"Category": cat, "A": a, "B": b})

    return df


@capture("graph")
def butterfly(data_frame):
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data_frame["A"].to_list(),
            y=data_frame["Category"].to_list(),
            orientation="h",
            name="A",
            marker=dict(color=px.colors.sequential.Blues[::-1][2]),
        )
    )

    fig.add_trace(
        go.Bar(
            x=data_frame["B"].to_list(),
            y=data_frame["Category"].to_list(),
            orientation="h",
            name="B",
            marker=dict(color=px.colors.sequential.Blues[::-1][0]),
        )
    )

    fig.update_layout(
        xaxis_title="Value",
        yaxis_title="Categories",
        barmode="relative",
        xaxis_tickvals=[-8, -6, -4, -2, 0, 2, 4, 6, 8],
        xaxis_ticktext=[8, 6, 4, 2, 0, 2, 4, 6, 8],
    )

    return fig


def retrieve_marimekko_data():
    """This function returns data for marimekko chart."""
    cats = ["Technology", "Office Supplies", "Furniture"]
    state = ["California", "Florida", "New York", "Texas"]
    widths = [35, 25, 30, 10] * 3
    sales = [34.8, 52.49, 41, 38.25, 31.1, 21.81, 28.69, 26.15, 34.1, 25.7, 30.31, 35.60]

    cats, state = pd.core.reshape.util.cartesian_product([cats, state])
    df = pd.DataFrame({"state": state, "category": cats, "sales": sales, "width": widths})

    state_total_sales = df.groupby("state")["sales"].sum().reset_index()

    df = df.merge(state_total_sales, on="state", suffixes=("", "_total"))
    df["category_sales_proportion"] = df["sales"] / df["sales_total"]
    df["cumulative_sales_proportion"] = df.groupby("state")["category_sales_proportion"].cumsum()

    return df


@capture("graph")
def marimekko(data_frame):
    color_map = {
        "Technology": px.colors.sequential.Blues[::-1][0],
        "Office Supplies": px.colors.sequential.Blues[::-1][1],
        "Furniture": px.colors.sequential.Blues[::-1][2],
    }

    fig = go.Figure()
    for key in data_frame["category"].unique():
        dff = data_frame.loc[data_frame["category"] == key]
        fig.add_trace(
            go.Bar(
                name=key,
                y=dff["sales"].to_list(),
                x=np.cumsum(np.array(dff["width"])) - np.array(dff["width"]),
                width=dff["width"].to_list(),
                offset=0,
                marker_color=color_map[key],
                text=["{:.2f}$".format(x) for x in dff["sales"].to_list()],
            )
        )

    fig.update_xaxes(range=[0, 100])
    fig.update_yaxes(range=[0, 100])

    fig.update_layout(
        barmode="stack",
        xaxis_title="State",
        yaxis_title="Cumulative Sales Proportion",
        showlegend=True,
        legend_title="Category",
        uniformtext_mode="hide",
    )

    return fig


def retrieve_line_col_data():
    """This function returns data for line column chart."""
    dates = ["Q3/2022", "Q4/2022", "Q1/2023", "Q2/2023", "Q3/2023"]
    quantity = [1000, 1500, 2100, 2800, 1100]
    quantity_last_year = [1200, 1340, 2300, 3000, 1150]

    df = pd.DataFrame({"dates": dates, "quantity": quantity, "quantity_last_year": quantity_last_year})

    return df


@capture("graph")
def line_column(data_frame):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data_frame["dates"].tolist(),
            y=data_frame["quantity_last_year"].tolist(),
            mode="lines",
            name="Last Year",
            line=dict(color=px.colors.sequential.Blues[::-1][4]),
        )
    )

    fig.add_trace(
        go.Bar(
            x=data_frame["dates"].tolist(),
            y=data_frame["quantity"].tolist(),
            name="This Year",
            marker_color=px.colors.sequential.Blues[::-1][0],
        )
    )

    fig.update_layout(
        xaxis=dict(title="Quarter of Order Dates"),
        yaxis=dict(title="Quantity"),
        legend=dict(title="Time Period"),
    )

    return fig


def retrieve_stepped_line():
    """This function returns data for stepped line chart."""
    data = [
        [0, 0.5, "A"],
        [1, 0.5, "A"],
        [1, 1, "A"],
        [2, 1, "A"],
        [2, 2, "A"],
        [4, 2, "A"],
        [4, 2, "A"],
        [4, 1.5, "A"],
        [5, 1.5, "A"],
        [6, 1.5, "A"],
        [0, 2, "B"],
        [1, 2, "B"],
        [1, 1, "B"],
        [2, 1, "B"],
        [3, 1, "B"],
        [3, 0.5, "B"],
        [4, 0.5, "B"],
        [5, 0.5, "B"],
        [5, 1, "B"],
        [6, 1, "B"],
    ]
    df = pd.DataFrame(data, columns=["count", "value", "cat"])
    return df


def retrieve_gapminder_country(country):
    """This function returns gapminder data for a list of countries."""
    df = px.data.gapminder()
    subset = df[(df["country"].isin(country))].copy()
    return subset


def retrieve_gapminder_year(year):
    """This is function returns gapminder data for a specific year."""
    df = px.data.gapminder()
    subset = df.loc[df["year"] == year].copy()
    return subset


def retrieve_continent_data():
    """This is function returns gapminder data grouped by continent."""
    df = px.data.gapminder()
    grouped = (
        df.groupby(by=["continent", "year"]).agg({"lifeExp": "mean", "pop": "sum", "gdpPercap": "mean"}).reset_index()
    )
    return grouped


def retrieve_order_data():
    """This function returns data for gant chart."""
    df = pd.DataFrame(
        [
            {"order_id": "CA-103387", "start": "2023-06-01", "finish": "2023-06-01", "ship_mode": "Standard"},
            {"order_id": "CA-103400", "start": "2023-06-03", "finish": "2023-06-04", "ship_mode": "First Class"},
            {"order_id": "CA-103402", "start": "2023-06-03", "finish": "2023-06-05", "ship_mode": "First Class"},
            {"order_id": "CA-103435", "start": "2023-06-04", "finish": "2023-06-08", "ship_mode": "Second Class"},
            {"order_id": "CA-103466", "start": "2023-06-09", "finish": "2023-06-16", "ship_mode": "Standard"},
            {"order_id": "CA-103484", "start": "2023-06-11", "finish": "2023-06-17", "ship_mode": "Standard"},
            {"order_id": "CA-103510", "start": "2023-06-15", "finish": "2023-06-17", "ship_mode": "First Class"},
        ]
    )
    return df


def retrieve_superstore_data():
    """This function returns superstore data."""
    cats = ["Technology", "Office Supplies", "Furniture"]
    year = [2019, 2020, 2021, 2022]
    sales = [175287, 162783, 226389, 271372, 151776, 137233, 183940, 246098, 157193, 170518, 198901, 215387]

    cats, year = pd.core.reshape.util.cartesian_product([cats, year])
    df = pd.DataFrame({"year": year, "category": cats, "sales": sales})

    return df


def retrieve_superstore_grouped():
    """This function returns superstore data for one year."""
    cats = ["Technology", "Furniture", "Food", "Office Supplies", "Clothes"]
    sales = [271372, 226389, 175287, 162783, 151776]

    df = pd.DataFrame({"category": cats, "sales": sales})

    return df


def retrieve_diverging_bar():
    """This function returns superstore data for one year."""
    cats = ["Art", "Bookcases", "Chairs", "Furnishings", "Phones", "Storage", "Tables"]
    profit_ratio = [0.25, 0.17, 0.23, -0.13, 0.08, 0.3, -0.09]
    col = ["Positive", "Positive", "Positive", "Negative", "Positive", "Positive", "Negative"]

    df = pd.DataFrame({"category": cats, "profit_ratio": profit_ratio, "col": col})

    return df


def retrieve_flow_map():
    """This function returns data for flow map chart."""
    # source: https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv
    data = [
        ["Niagara Falls", "New York", 49468, 43.0962143, -79.03773879999999, "Trace 1"],
        ["Rochester", "New York", 210358, 43.16103, -77.61092190000001, "Trace 1"],
        ["New York", "New York", 8405837, 40.7127837, -74.00594129999999, "Trace 1"],
        ["Fort Wayne", "Indiana", 256496, 41.079273, -85.13935129999999, "Trace 2"],
        ["Toledo", "Ohio", 282313, 41.6639383, -83.555212, "Trace 2"],
        ["Cleveland", "Ohio", 390113, 41.499320000000004, -81.6943605, "Trace 2"],
        ["Erie", "Pennsylvania", 100671, 42.1292241, -80.085059, "Trace 2"],
        ["Philadelphia", "Pennsylvania", 1553165, 39.9525839, -75.1652215, "Trace 2"],
        ["Cincinnati", "Ohio", 297517, 39.103118200000004, -84.5120196, "Trace 3"],
        ["Dayton", "Ohio", 143355, 39.758947799999994, -84.1916069, "Trace 3"],
        ["Columbus", "Ohio", 822553, 39.9611755, -82.9987942, "Trace 3"],
        ["Pittsburgh", "Pennsylvania", 305841, 40.440624799999995, -79.9958864, "Trace 3"],
        ["Nashville", "Tennessee", 634464, 36.1626638, -86.78160159999999, "Trace 4"],
        ["Raleigh", "North Carolina", 431746, 35.7795897, -78.6381787, "Trace 4"],
        ["Norfolk", "Virginia", 246139, 36.8507689, -76.28587259999999, "Trace 4"],
        ["Washington", "District of Columbia", 646449, 38.9071923, -77.03687070000001, "Trace 4"],
    ]
    df = pd.DataFrame(data, columns=["City", "State", "Population", "lat", "lon", "trace"])

    return df


def retrieve_election():
    """This function returns election data."""
    return px.data.election()


def retrieve_carshare():
    """This function returns carshare data."""
    return px.data.carshare()


def retrieve_gapminder():
    """This is function returns gapminder data."""
    df = px.data.gapminder()
    return df


def retrieve_forecasting_data():
    """This is function creates synthetic sales forecasting data."""
    # Create dataframe for date range
    start_date = "2020-01-01"
    forecasting = "2025-12-31"
    df_dates = pd.DataFrame({"date": pd.date_range(start_date, forecasting, freq="D")})

    # Create category country combinations
    categories = ["Bakery", "Fruits", "Vegetables", "Fresh Meat", "Fresh Fish"]
    countries = ["Germany", "Austria", "Spain", "Italy", "France"]
    lambda_cat_country = [
        520,
        60,
        190,
        265,
        450,
        1300,
        150,
        475,
        662,
        1125,
        780,
        90,
        285,
        397,
        675,
        1560,
        180,
        570,
        795,
        1350,
        1040,
        120,
        380,
        530,
        900,
    ]
    lambda_list = [lam * 1000 for lam in lambda_cat_country]
    cats, country = pd.core.reshape.util.cartesian_product([categories, countries])
    df_ml = pd.DataFrame({"country": country, "category": cats, "lambda_col": lambda_list})

    # Merge dataframes
    df = pd.merge(df_dates, df_ml, how="cross")

    # create fake data using poisson distribution
    for name, group in df.groupby(["country", "category"]):
        lam = group["lambda_col"].unique().item()
        size = len(group)
        rand_list = [np.random.uniform(0.75, 1.25) for i in range(size)]
        trend = np.arange(1, 11, 10 / size)

        # sales
        np.random.seed(143)
        sales = np.random.poisson(lam=lam, size=size) * trend * rand_list

        # forecasting
        np.random.seed(105)
        forecast = np.random.poisson(lam=lam, size=size) * trend * rand_list

        df.loc[group.index, "sales"] = sales
        df.loc[group.index, "forecast"] = forecast

    df["year"] = df["date"].apply(lambda x: x.strftime("%Y"))

    # Set sales to 0  for future and forecasting to 0 before val period
    today = datetime.now()
    # val_period = datetime.now() - timedelta(days=90)
    val_period = datetime.now()
    df.loc[df["date"] >= today, "sales"] = None
    df.loc[df["date"] < val_period, "forecast"] = None

    df.drop(columns=["lambda_col"], inplace=True)

    df["value"] = "sales"
    df["value_number"] = df["sales"]
    df.loc[~df["forecast"].isna(), "value"] = "forecast"
    df.loc[~df["forecast"].isna(), "value_number"] = df["forecast"]
    df = df[["date", "value", "value_number", "category", "country"]]

    # df = df.loc[df['country']=='Germany']
    df["year"] = df.date.dt.year
    df = df.loc[df["year"] == 2023]

    return df


def retrieve_sparkline_data():
    """This is a function that returns forecasting data for country and category."""
    df = retrieve_forecasting_data()
    subset = df.loc[
        (df["category"].isin(["Bakery"]))
        & (df["country"].isin(["Spain", "Italy", "Austria", "France", "Germany"]) & (df["date"] < "2023-02-01"))
    ]
    return subset


def retrieve_iris():
    """This is a function that returns iris dataframe."""
    return px.data.iris()


def create_chart_page(
    chart_name: str,
    retrieve_data_func: Callable,
    fig_type: str,
    description_text: str,
    usage_text: str,
    note_text: Optional[str] = "",
    **kwargs,
):
    """This is a function that creates a chart page."""
    ref_chart_name = chart_name.lower().replace(" ", "_")
    data_manager[ref_chart_name + "_data"] = retrieve_data_func

    if fig_type == "scatter":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.scatter(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )

    elif fig_type == "bar":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.bar(ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]),
        )

    elif fig_type == "timeline":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.timeline(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )

    elif fig_type == "histogram":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.histogram(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "line":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.line(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "area":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.area(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "pie":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.pie(ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]),
        )
    elif fig_type == "violin":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.violin(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "treemap":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.treemap(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "ecdf":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.ecdf(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "strip":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.strip(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "box":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.box(ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]),
        )
    elif fig_type == "choropleth_mapbox":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.choropleth_mapbox(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "scatter_mapbox":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.scatter_mapbox(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "line_mapbox":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=px.line_mapbox(
                ref_chart_name + "_data", **kwargs, color_discrete_sequence=px.colors.sequential.Blues[::-1]
            ),
        )
    elif fig_type == "marimekko":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=marimekko(ref_chart_name + "_data"),
        )
    elif fig_type == "line_column":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=line_column(ref_chart_name + "_data"),
        )
    elif fig_type == "surplus":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=surplus(ref_chart_name + "_data"),
        )
    elif fig_type == "butterfly":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=butterfly(ref_chart_name + "_data"),
        )
    elif fig_type == "slope":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=slope(ref_chart_name + "_data"),
        )
    elif fig_type == "lollipop":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=lollipop(ref_chart_name + "_data"),
        )
    elif fig_type == "waterfall":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=waterfall(ref_chart_name + "_data"),
        )
    elif fig_type == "venn":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=venn(ref_chart_name + "_data"),
        )
    elif fig_type == "barcode":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=barcode(ref_chart_name + "_data"),
        )
    elif fig_type == "dot_pot":
        graph = vm.Graph(
            id=ref_chart_name + "_fig",
            figure=dot_pot(ref_chart_name + "_data"),
        )

    ref_chart_name = vm.Page(
        title=chart_name,
        path=ref_chart_name,
        layout=vm.Layout(grid=[[0, 1, 1], [0, 1, 1], [0, 1, 1]]),
        components=[
            vm.Card(
                text=f"""
                    # {chart_name}

                    &nbsp;
                    ## What is a {chart_name}?

                    {description_text}

                    &nbsp;
                    ## When to use it?

                    {usage_text}

                    &nbsp;

                     &nbsp;
                    > {note_text}
                """,
            ),
            graph,
        ],
    )

    return ref_chart_name


def create_first_row():
    """This function creates all pages of the first row."""
    page_column = create_chart_page(
        "Column",
        retrieve_superstore_grouped,
        "bar",
        x="category",
        y="sales",
        labels={"category": "Category", "sales": "Sales"},
        description_text="A Column chart is a vertical Bar chart, with column lengths varying according to the "
        "categorical value they represent. The scale is presented on the y-axis, starting with zero.",
        usage_text="Select a Column chart when you want to help your audience draw size comparisons and identify "
        "patterns between categorical data, i.e., data that presents `how many?` in each category. You can "
        "arrange your columns in any order to fit the message you wish to emphasise. Be mindful of "
        "labelling clearly when you have a large number of columns. You may need to include a legend, "
        "or use abbreviations in the chart with fuller descriptions below of the terms used.",
    )

    page_marimekko = create_chart_page(
        "Marimekko",
        retrieve_marimekko_data,
        "marimekko",
        x="state",
        y="cumulative_sales_proportion",
        color="category",
        labels={"category": "Category", "sales": "Sales", "state": "State"},
        description_text="A Marimekko chart (also known as a Mekko or a Mosaic Plot) is a stacked chart with column "
        "segments that vary in height, as well as the column widths varying according to a second "
        "value. It becomes a 2-dimensional stacked chart.",
        usage_text="A Marimekko chart is useful when you wish to visualise relationships between categories and their "
        "subcategories across two variables, i.e., the two axes. Each axis is variable, with a percentage "
        "scale determining both the width and the height of each segment. Be aware, though, "
        "that they become hard to read when there are many segments. Also, readers may find it difficult "
        "to make accurate comparisons between each segment because they are not arranged next to each "
        "other along the same baseline.",
    )

    page_stacked_column = create_chart_page(
        "Stacked Column",
        retrieve_superstore_data,
        "bar",
        x="year",
        y="sales",
        color="category",
        labels={"category": "Category", "sales": "Sales", "year": "Year"},
        description_text="A Stacked Column chart shows part-to-whole relationships of multiple totals and their "
        "shares. Data series are stacked one on top of each other in vertical columns, starting from "
        "the same baseline.",
        usage_text="You should consider using a Stacked Column chart when you want your audience to focus on totals "
        "and the parts that make them up, and when the total of the parts is crucial. It is best to "
        "arrange your most important value at the bottom of the chart and to use a distinct colour to make "
        "it stand out. This will make it easier for your audience to compare values. This chart works well "
        "when you are displaying multiple totals; if you`re only interested in the parts of one total, "
        "consider instead a Bar chart.",
    )

    page_gant = create_chart_page(
        "Gant",
        retrieve_order_data,
        "timeline",
        x_start="start",
        x_end="finish",
        y="order_id",
        color="ship_mode",
        labels={"order_id": "Order Id", "ship_mode": "Ship Mode"},
        description_text="A Gantt chart is a type of Bar chart for displaying, for example, a project schedule.",
        usage_text="Select a Gantt chart when your audience needs to see how various activities/tasks/events are "
        "scheduled over a period of time. List the activities or tasks along the vertical axis and the "
        "time intervals along the horizontal axis. Plot horizontal bars representing the activities, "
        "with their positions and lengths indicating the start time/date, duration and end time/date. You "
        "might also show the dependency relationships between the activities and the current schedule "
        "status.",
    )

    page_histogram = create_chart_page(
        "Histogram",
        retrieve_gapminder,
        "histogram",
        x="lifeExp",
        labels={"lifeExp": "Life Expectancy", "y": "Count"},
        description_text="A Histogram groups numeric data into columns sized according to how often values fall into "
        "specified ranges. It displays the data over a period of time or over a continuous interval.",
        usage_text="Using a Histogram will help your audience see where particular values are concentrated, what the "
        "extremes are, and whether there are any gaps or unusual values. It may also help you see a rough "
        "probability distribution. You should try to keep the gaps small between your columns so that the "
        "`shape` your data takes is immediately apparent.",
    )

    page_ordered_bubble = create_chart_page(
        "Ordered Bubble",
        lambda: retrieve_gapminder_country(["India"]),
        "scatter",
        x="gdpPercap",
        size="pop",
        labels={"gdpPercap": "GDP per Cap", "pop": "Population"},
        description_text="This chart distributes proportionately-sized circles against two variables presented on "
        "each axis (like a standard Bubble chart), in order of size, e.g., smallest to largest.",
        usage_text="You can select this chart when you are displaying big variations in values and/or it is not so "
        "important for your audience to see minor differences between the data. By presenting your "
        "`bubbles` in size order, you can show at a glance the magnitude of each compared with each other.",
    )

    return page_column, page_marimekko, page_stacked_column, page_gant, page_histogram, page_ordered_bubble


def create_second_row():
    """This function creates all pages of the second row."""
    page_line_column = create_chart_page(
        "Line Column",
        retrieve_line_col_data,
        "line_column",
        description_text="A combined Column and Line chart helps you demonstrate the relationship between an amount ("
        "displayed in columns) and a variable over time (displayed as a line running across the "
        "columns).",
        usage_text="Use this type of chart when you wish to compare quantities of one item with changes in another "
        "item over a period of time.",
    )

    page_surplus_chart = create_chart_page(
        "Surplus Chart",
        retrieve_surplus_data,
        "surplus",
        description_text="In a line-surplus-deficit-filled chart, shaded areas emphasise variation from a fixed "
        "reference point.",
        usage_text="Use this chart when you wish to draw the audience`s attention to the balance between two data "
        "sets or that against a baseline. The chart will help them draw comparisons between the two sets "
        "of data.",
    )

    page_butterfly_chart = create_chart_page(
        "Butterfly Chart",
        retrieve_butterfly_data,
        "butterfly",
        description_text="A Tornado chart (also called a Butterfly chart) is a bar chart for displaying two sets of "
        "data series side by side.",
        usage_text="Use a Tornado chart when you wish to emphasise the comparison between two data sets sharing the "
        "same parameters. Sharing this chart with your audience will help them see at a glance how two "
        "groups differ within the same parameters. You can also `stack` two bars on each side if you wish "
        "to divide your categories, e.g., `trained staff` and `staff-in-training`.",
    )

    page_bar = create_chart_page(
        "Bar",
        retrieve_superstore_grouped,
        "bar",
        x="sales",
        y="category",
        orientation="h",
        labels={"sales": "Sales", "category": "Category"},
        description_text="A Bar chart displays bars in lengths proportional to the values they represent. One axis of "
        "the chart shows the categories to compare and the other axis provides a value scale, "
        "starting with zero.",
        usage_text="Select a Bar chart when you want to help your audience draw size comparisons and identify "
        "patterns between categorical data, i.e., data that presents `how many?` in each category. You can "
        "arrange your bars in any order to fit the message you wish to emphasise. Be mindful of labelling "
        "clearly when you have a large number of bars. You may need to include a legend, "
        "or use abbreviations in the chart with fuller descriptions below of the terms used.",
    )

    page_line = create_chart_page(
        "Line",
        lambda: retrieve_gapminder_country(["India"]),
        "line",
        x="year",
        y="pop",
        labels={"pop": "Population", "year": "Year"},
        description_text="A Line chart presents a series of data points over a continuous interval or time period, "
        "joined together with straight lines.",
        usage_text="You should select a Line chart when you want to show trends and invite analysis of how the data "
        "has changed over time. Usually, your y-axis will show a quantitative value and your x-axis will "
        "be marked as a timescale or a sequence of intervals. You can also display negative values below "
        "the x-axis. If you wish to group several lines (different data series) in the same chart, "
        "try to limit yourself to 3-4 to avoid cluttering up your chart and making it harder for the "
        "audience to read.",
    )

    return page_line_column, page_surplus_chart, page_butterfly_chart, page_bar, page_line


def create_third_row():
    """This function creates all pages of the third row."""
    page_scatter = create_chart_page(
        "Scatter",
        retrieve_iris,
        "scatter",
        y="sepal_length",
        x="sepal_width",
        # trendline="ols",
        labels={"sepal_length": "Length", "sepal_width": "W" "idth"},
        description_text="A scatter plot is a two-dimensional data visualisation using dots to represent the values "
        "obtained for two different variables - one plotted along the x-axis and the other plotted "
        "along the y-axis.",
        usage_text="Use Scatter Plots when you want to show the relationship between two variables. Scatter plots are "
        "sometimes called Correlation plots because they show how two variables are correlated. Scatter "
        "plots are ideal when you have paired numerical data and you want to see if one variable impacts "
        "the other. However, do remember that correlation is not causation, and another unnoticed variable "
        "may be influencing results. Make sure your audience does not draw the wrong conclusions.",
    )

    page_pie = create_chart_page(
        "Pie",
        retrieve_superstore_grouped,
        "pie",
        values="sales",
        names="category",
        labels={"sales": "Sales", "category": "Category"},
        description_text="A Pie chart is a circular chart divided into segments to show proportions and percentages "
        "between categories. The circle represents the whole.",
        usage_text="Use the Pie chart when you need to show your audience a quick view of how data is distributed "
        "proportionately, with percentages highlighted. The different values you present must add up to a "
        "total and equal 100%. The downsides are that Pie charts tend to occupy more space than many other "
        "charts, they don`t work well with more than a few values because labelling small segments is "
        "challenging, and it can be difficult to accurately compare the sizes of the segments.",
        note_text="Note: Limited by area chart options of plotly express.",
    )

    page_donut = create_chart_page(
        "Donut",
        retrieve_superstore_grouped,
        "pie",
        values="sales",
        names="category",
        hole=0.6,
        labels={"sales": "Sales", "category": "Category"},
        description_text="A Donut chart looks like a Pie chart, but has a blank space in the centre which may contain "
        "additional information.",
        usage_text="A Donut chart can be used in place of a Pie chart, particularly when you are short of space or "
        "have extra information you would like to share about the data. It may also be more effective if "
        "you wish your audience to focus on the length of the arcs of the sections instead of the "
        "proportions of the segment sizes.",
        note_text="Note: Limited by gant chart options of plotly express.",
    )

    page_violin = create_chart_page(
        "Violin",
        retrieve_gapminder,
        "violin",
        y="lifeExp",
        labels={"lifeExp": "Life Expectancy"},
        description_text="A Violin Plot is similar to a Box Plot, but works better for visualising more complex "
        "distributions and their probability density at different values.",
        usage_text="Use this chart to go beyond the simple Box Plot and show the distribution shape of the data, "
        "the inter-quartile range, the confidence intervals and the median.",
    )

    page_slope = create_chart_page(
        "Slope",
        retrieve_slope_data,
        "slope",
        description_text="A line chart plotting values across two points in time.",
        usage_text="You can use a Slope chart when you wish to invite comparison and identify trends between two "
        "points in time. This chart shows your audience how ranks have changed over time or how they vary "
        "between categories.",
    )

    return page_scatter, page_pie, page_donut, page_violin, page_slope


def create_fourth_row():
    """This function creates all pages of the fourth row."""
    page_lollipop = create_chart_page(
        "Lollipop",
        retrieve_lollipop_data,
        "lollipop",
        description_text="A Lollipop chart is similar to a standard bar chart, but you replace each the bar with a "
        "line and place a dot at the end to mark the value.",
        usage_text="You can use a Lollipop chart in the same situations as a Bar chart. You may find the design "
        "visually more appealing than a standard Bar chart to invite comparison or demonstrate trends over "
        "time. It is claimed that this chart is more effective than a Bar chart at drawing attention to "
        "the data values. But you need to be aware that it may be difficult for the audience to judge the "
        "precise value which lies in the centre of the dot. So make sure your labelling and/or commentary "
        "is clear.",
        # note_text="Note: Currently not available.",
    )

    page_cumulative_curve = create_chart_page(
        "Cumulative Curve",
        retrieve_iris,
        "ecdf",
        x="sepal_length",
        color="species",
        labels={"species": "Species", "sepal_length": "Sepal Length"},
        description_text="The Cumulative Curve (sometimes referred to as an Ogive) represents the cumulative "
        "frequency distribution of grouped data on a graph. The frequency is the number of times an "
        "event occurs within a given scenario, with cumulative frequency being the running total of "
        "frequencies up to the current point.",
        usage_text="The Cumulative Curve is helpful when you wish to discover the popularity of a certain type of "
        "data, or how likely it is that a specified event will fall within a certain frequency "
        "distribution. You can also use it to show how unequal a distribution is: the y-axis is always "
        "cumulative frequency, and the x-axis is always a measure. You can construct a More Than Type or a "
        "Less Than Type Cumulative Frequency Curve. If you plot both curves on the same graph, "
        "the point at which they intersect (the corresponding value on the x-axis) indicates the median of "
        "your data set.",
    )

    page_waterfall = create_chart_page(
        "Waterfall",
        retrieve_waterfall_data,
        "waterfall",
        description_text="A Waterfall chart shows the cumulative effect of a series of positive or negative values on "
        "an initial value.",
        usage_text="You will usually use a Waterfall chart to illustrate a budgetary process, or to show changes in "
        "revenue or profit between two points. Your initial and final values will tend to be represented "
        "by whole columns. In between these you will introduce `floating` columns, starting based on the "
        "value of the previous column. You may wish to colour code the floating columns to help "
        "distinguish between their positive or negative values.",
    )

    page_treemap = create_chart_page(
        "Treemap",
        lambda: retrieve_gapminder_year(2007),
        "treemap",
        values="pop",
        path=[px.Constant("world"), "continent", "country"],
        color="lifeExp",
        width=300,
        labels={"pop": "Population", "lifeExp": "Life Expectancy"},
        description_text="A Treemap shows hierarchical data arranged as a set of `nested` rectangles: rectangles "
        "sized proportionately to the quantity they represent, combining together to form larger "
        "`parent` category rectangles.",
        usage_text="It`s helpful to use a Treemap when you wish to display hierarchical part-to-whole relationships. "
        "You can compare groups and single elements nested within them. Consider using them instead of Pie "
        "charts when you have a higher number of categories. Treemaps are very compact and allow audiences "
        "to get a quick overview of the data.",
    )

    page_venn = create_chart_page(
        "Venn",
        retrieve_venn_data,
        "venn",
        description_text="A Venn Diagram shows all the possible logical relationships between a collection of sets. "
        "These sets tend to be represented with circles.",
        usage_text="Use a Venn diagram to highlight the commonalities between your chosen entities in the overlapping "
        "areas of your circles: the `intersection` areas. You can also draw conclusions about the elements "
        "of the entities that lie outside the overlaps.",
    )

    page_barcode = create_chart_page(
        "Barcode",
        retrieve_iris,
        "barcode",
        # x="sepal_width",
        # y="species",
        # labels={"species": "Species", "sepal_width": "Sepal Width"},
        description_text="A Bar Code chart is a compact means of visualising a distribution. It resembles a bar code "
        "on a purchased item.",
        usage_text="You should use the Bar Code chart when you wish to show audiences several distributions for "
        "comparison, but you are short of space. Use each line segment to represent an individual point "
        "along a single axis.",
        # note_text="Note: Currently only available as strip instead of barcode chart.",
    )

    return page_lollipop, page_cumulative_curve, page_waterfall, page_treemap, page_venn, page_barcode


def create_fifth_row():
    """This function creates all pages of the fitfth row."""
    page_diverging_bar = create_chart_page(
        "Diverging Bar",
        retrieve_diverging_bar,
        "bar",
        x="profit_ratio",
        y="category",
        color="col",
        orientation="h",
        labels={"profit_ratio": "Profit Ratio", "category": "Category", "col": "Ratio Type"},
        description_text="A Diverging Bar is similar to a standard Bar chart, but differs by displaying both positive "
        "and negative magnitude values.",
        usage_text="You should use a Diverging Bar chart when you wish to emphasise patterns or comparisons in "
        "relation to a fixed reference point. This reference point may or may not equal zero.",
    )

    page_boxplot = create_chart_page(
        "Boxplot",
        retrieve_continent_data,
        "box",
        y="lifeExp",
        color="continent",
        labels={"lifeExp": "Life Expectancy", "continent": "Continent"},
        description_text="A Box Plot (also known as a Box and Whisker Plot) provides a visual display of multiple "
        "datasets, indicating the median (centre) and the range of the data for each.",
        usage_text="Choose a Box Plot when you need to summarise distributions between many groups or datasets. It "
        "takes up less space than many other charts. Create boxes to display the median, and the upper and "
        "lower quartiles. Add `whiskers` to highlight variability outside the upper and lower quartiles. "
        "You can add outliers as dots beyond, but in line with the whiskers.",
    )

    # geojson = px.data.election_geojson()
    # page_choropleth = create_chart_page(
    #     "Choropleth",
    #     retrieve_election,
    #     "choropleth_mapbox",
    #     geojson=geojson,
    #     locations="district",
    #     featureidkey="properties.district",
    #     zoom=9,
    #     opacity=0.7,
    #     color="winner",
    #     center={"lat": 45.5517, "lon": -73.7073},
    #     mapbox_style="carto-positron",
    #     description_text="A Choropleth Map is a map in which geographical areas are coloured, shaded or patterned in "
    #     "relation to a specific data variable.",
    #     usage_text="Use a Chloropleth Map when you wish to show how a measurement varies across a geographic area, "
    #     "or to show variability or patterns within a region. Typically, you will blend one colour into "
    #     "another, take a colour shade from light to dark, or introduce patterns to depict the variation in "
    #     "the data. Be aware that it may be difficult for your audience to accurately read or compare "
    #     "values on the map depicted by colour.",
    # )
    #
    # page_dot_density = create_chart_page(
    #     "Dot Density",
    #     retrieve_carshare,
    #     "scatter_mapbox",
    #     lat="centroid_lat",
    #     lon="centroid_lon",
    #     color="peak_hour",
    #     size="car_hours",
    #     mapbox_style="carto-positron",
    #     zoom=10,
    #     opacity=0.7,
    #     labels={"peak_hour": "Peak Hour"},
    #     description_text="A Dot Density Map uses dots to show concentrations of an entity in a geographical region.",
    #     usage_text="You should use a Dot Density Map when you wish to show the location/s of a phenomenon and its "
    #     "concentration: many dots indicate a high concentration, whilst fewer dots represent lower "
    #     "concentration. Each dot may represent one single count or a given quantity.",
    # )
    #
    # page_flow_map = create_chart_page(
    #     "Flow Map",
    #     retrieve_flow_map,
    #     "line_mapbox",
    #     lat="lat",
    #     lon="lon",
    #     color="trace",
    #     zoom=4.5,
    #     height=300,
    #     mapbox_style="carto-positron",
    #     text="City",
    #     labels={"trace": "Trace"},
    #     description_text="A Flow Map is a map marked with connections or arrows indicating the movement of quantities "
    #     "from one location to another.",
    #     usage_text="Use a Flow Map when you wish to depict the unambiguous movement of an entity across a "
    #     "geographical area, e.g., people or goods. You can adjust the width of the connections to depict "
    #     "the quantity of the item moving. Arrows indicate the direction of movement.",
    # )

    page_bullet = create_chart_page(
        "Bullet",
        retrieve_empty_dataframe,
        "line",
        description_text="A Bullet graph functions similarly to a Bar chart, but contains more information.",
        usage_text="Use the Bullet graph as a more informative and space-efficient alternative to a dashboard gauge. "
        "Often it is used to display performance data. The most important data value is represented in the "
        "length of the main bar in the middle of the chart: the Feature Measure. A line marker running "
        "perpendicular to the graph`s orientation is called the Comparative Measure. It serves as a target "
        "marker to compare against the Feature Measure value. Once the main bar passes the position of "
        "Comparative Measure, you have hit your goal. You can include colours to indicate qualitative "
        "range scores, e.g., performance range ratings.",
        note_text="Note: Currently not available.",
    )

    # return page_diverging_bar, page_boxplot, page_choropleth, page_dot_density, page_flow_map, page_bullet
    return page_diverging_bar, page_boxplot, page_bullet


def create_sixth_row():
    """This function creates all pages of the fifth row."""
    page_dot_plot = create_chart_page(
        "Dot Plot",
        retrieve_dot_data,
        "dot_pot",
        description_text="The Dot Plot positions a group of data points across multiple categories against a simple "
        "scale. Each `dot` (filled circle) represents a minimum and maximum value in a range.",
        usage_text="You can select the Dot Plot when you wish to display the minimum and maximum values (counts) for "
        "each item in a small or moderate data set. Use it to highlight clusters, gaps and outliers in "
        "your data.",
    )

    page_stepped_line = create_chart_page(
        "Stepped Line",
        retrieve_stepped_line,
        "line",
        x="count",
        y="value",
        color="cat",
        labels={"cat": "Category"},
        description_text="A Stepped Line chart is much like a standard Line chart but, instead of connecting two "
        "points with the shortest line, the line forms a series of steps between data points.",
        usage_text="You should use a Stepped Line chart when you wish to draw attention to changes occurring at "
        "specific points. By contrast, a Line chart would suggest that changes occur gradually.",
    )

    page_sparkline = create_chart_page(
        "Sparkline",
        retrieve_sparkline_data,
        "line",
        x="date",
        y="value_number",
        facet_row="country",
        facet_row_spacing=0.05,
        color="country",
        labels={"date": "", "country": "", "value_number": ""},
        description_text="A sparkline is a very small line chart, typically drawn without axes or coordinates. It "
        "presents the general shape of the variation (typically over time) in some measurement, "
        "such as temperature or stock market price, in a simple and highly condensed way.",
        usage_text="Whereas the typical charts are designed to show as much data as possible, and is set off from the "
        "flow of text, sparklines are intended to be succinct, memorable, and located where they are "
        "discussed.",
    )

    return page_dot_plot, page_stepped_line, page_sparkline


def create_home():
    """This is a function that returns home page."""
    page_dashboard = vm.Page(
        title="Chart Compendium",
        path="compendium",
        layout=vm.Layout(
            grid=[
                [0, 1, 2, 3],
                [4, 5, 6, 7],
                [8, 9, 10, 11],
                [12, 13, 14, 15],
                [16, 17, 18, 19],
                [20, 21, 22, 23],
                [24, 25, 26, 27],
            ],
            row_min_height="230px",
            col_gap="16px",
        ),
        components=[
            # First row
            vm.Card(
                text="""
                ![](assets/images/compendium/12.-Column_details.1.svg#compendium)

                ### Column
                """,
                href="/column",
            ),
            vm.Card(
                text="""
                ![](assets/images/compendium/27.-Marimekko_details.1.svg#compendium)

                ### Marimekko
                """,
                href="/marimekko",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/Stacked_column.1.svg#compendium)

                    ### Stacked
                """,
                href="/stacked_column",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/22.-Gantt_details.1.svg#compendium)

                    ### Gant
                """,
                href="/gant",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/13.-Histogram_details.1.svg#compendium)

                    ### Histogram
                """,
                href="/histogram",
            ),
            vm.Card(
                text="""
                        ![](assets/images/compendium/8.-Ordered-Bubble_details.1.svg#compendium)

                        ### Ordered Bubble
                    """,
                href="/ordered_bubble",
            ),
            # Second row
            vm.Card(
                text="""
                    ![](assets/images/compendium/6.-Colomn-Line_details.1.svg#compendium)

                    ### Line Column
                """,
                href="/line_column",
            ),
            vm.Card(
                text="""
                        ![](assets/images/compendium/3.-Surplus-chart_details.1.svg#compendium)

                        ### Surplus Chart
                    """,
                href="/surplus_chart",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/2.-Butterfly-chart_details.1.svg#compendium)

                    ### Butterfly Chart
                """,
                href="/butterfly_chart",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/11.-Bar_details.1.svg#compendium)

                    ### Bar
                """,
                href="/bar",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/20.-Line_details.1.svg#compendium)

                    ### Line
                """,
                href="/line",
            ),
            # Third row
            vm.Card(
                text="""
                    ![](assets/images/compendium/4.-Scatter-plot_details.1.svg#compendium)

                    ### Scatter
                """,
                href="/scatter",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/24.-Pie_details1.svg#compendium)

                    ### Pie
                """,
                href="/pie",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/25.-Donut_details.1.svg#compendium)

                    ### Donut
                """,
                href="/donut",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/17.-Violin-plot_details.1.svg#compendium)

                    ### Violin
                """,
                href="/violin",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/10.-Slope_details.1.svg#compendium)

                    ### Slope
                """,
                href="/slope",
            ),
            # Fourth row
            vm.Card(
                text="""
                    ![](assets/images/compendium/9.-Lollipop_details.1.svg#compendium)

                    ### Lollipop
                """,
                href="/lollipop",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/18.-Cumulative-curve_details.1.svg#compendium)

                    ### Cumulative Curve
                """,
                href="/cumulative_curve",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/32.-Waterfall_details.1.svg#compendium)

                    ### Waterfall
                """,
                href="/waterfall",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/28.-Tree_details.1.svg#compendium)

                    ### Treemap
                """,
                href="/treemap",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/29.-Venn_details.1.svg#compendium)

                    ### Venn
                """,
                href="/venn",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/15.-Barcode_details.1.svg#compendium)

                    ### Barcode
                """,
                href="/barcode",
            ),
            # Fifth row
            vm.Card(
                text="""
                    ![](assets/images/compendium/1.Diverging-bar_details1.svg#compendium)

                    ### Diverging Bar
                """,
                href="/diverging_bar",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/16.-Boxplot_details.1.svg#compendium)

                    ### Boxplot
                """,
                href="/boxplot",
            ),
            # vm.Card(
            #     text="""
            #       ![](assets/images/compendium/45.-Choropleth1.svg#compendium)
            #
            #       ### Choropleth
            #     """,
            #     href="/choropleth",
            # ),
            # vm.Card(
            #     text="""
            #        ![](assets/images/compendium/47.-Dot-density1.svg#compendium)
            #
            #        ### Dot Density
            #     """,
            #     href="/dot_density",
            # ),
            # vm.Card(
            #     text="""
            #       ![](assets/images/compendium/48.-Flow-map1.svg#compendium)
            #
            #       ### Flow Map
            #     """,
            #     href="/flow_map",
            # ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/34.-Bullet_details.1.svg#compendium)

                    ### Bullet
                """,
                href="/bullet",
            ),
            # Sixth row
            vm.Card(
                text="""
                    ![](assets/images/compendium/14.-Dot-plot_details.1.svg#compendium)

                    ### Dot Plot
                """,
                href="/dot_plot",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/19.-Stepped-line_details..svg#compendium)

                    ### Stepped Line
                """,
                href="/stepped_line",
            ),
            vm.Card(
                text="""
                    ![](assets/images/compendium/36.-Sparkline_details..svg#compendium)

                    ### Sparkline
                """,
                href="/sparkline",
            ),
        ],
    )
    return page_dashboard


def retrieve_compendium_pages():

    page_column, page_marimekko, page_stacked_column, page_gant, page_histogram, page_ordered_bubble = (
        create_first_row()
    )
    (
        page_line_column,
        page_surplus_chart,
        page_butterfly_chart,
        page_bar,
        page_line,
    ) = create_second_row()
    page_scatter, page_pie, page_donut, page_violin, page_slope = create_third_row()
    page_lollipop, page_cumulative_curve, page_waterfall, page_treemap, page_venn, page_barcode = create_fourth_row()
    page_diverging_bar, page_boxplot, page_bullet = create_fifth_row()

    page_dot_plot, page_stepped_line, page_sparkline = create_sixth_row()
    page_dashboard = create_home()

    page_list = [
        page_dashboard,
        page_column,
        page_marimekko,
        page_stacked_column,
        page_gant,
        page_histogram,
        page_ordered_bubble,
        page_line_column,
        page_surplus_chart,
        page_butterfly_chart,
        page_bar,
        page_line,
        page_scatter,
        page_pie,
        page_donut,
        page_violin,
        page_slope,
        page_lollipop,
        page_cumulative_curve,
        page_waterfall,
        page_treemap,
        page_venn,
        page_barcode,
        page_diverging_bar,
        page_boxplot,
        # page_choropleth,
        # page_dot_density,
        # page_flow_map,
        page_bullet,
        page_dot_plot,
        page_stepped_line,
        page_sparkline,
    ]

    return page_list


if __name__ == "__main__":
    dashboard = vm.Dashboard(pages=retrieve_compendium_pages())
    Vizro().build(dashboard).run()
