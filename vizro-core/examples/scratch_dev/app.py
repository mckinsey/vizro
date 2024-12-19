"""
Create a dashboard with 3 pages.

The first page has the title "This year's reading"
The chart is a scatter chart. Plot the date a book was read on the x axis. Plot it at y=1.

The second page has the title "Pages and Book totals over the years" and it shows 1 chart.

The chart shows the cumulative total number of pages read by summing the Number of Pages of each book read in each year, using the Date Read data.
Plot date on the x axis and the number of pages on the y axis using a scale on the left hand side of the chart.

Add a filter so the user can change the x axis to adjust the range of dates by year on the x axis.

Superimpose a bar chart showing the total books read for each year, taking data from the Date Read column.
Show the total books read using the right hand side of the chart which can be a different scale to the y axis shown on the left hand side.

The third page has the title "Ratings over the years" and it has 1 chart.

The chart emphasizes the gap between My Rating and the Average Rating for each row of the dataset.
Eliminate any book where My Rating is 0. Then, for each row of the dataset, plot the My Rating and Average Rating
data points using circles that are connected by a line to show the gap between the two points.
Stack the books vertically on the y axis, ordered alphabetically by Title, and use the x axis to show the rating between 0 and 5. Label each with the Title and Author.

"""


############ Imports ##############
from vizro import Vizro
import vizro.models as vm

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


####### Function definitions ######
@capture("graph")
def scatter_chart(data_frame):
    # Filter the DataFrame to ignore rows where My Rating is 0
    filtered_df = data_frame[(data_frame["My Rating"] > 0) & (data_frame["Date Read"].dt.year == 2024)]

    # Create the figure
    fig = go.Figure()

    # Iterate through the filtered DataFrame to add traces
    for index, row in filtered_df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row["Date Read"], row["Date Read"]],
                y=[1],
                customdata=[[row["Title"], row["Author"], row["My Rating"]]],
                showlegend=False,
                marker=dict(color="#00b4ff", size=20, opacity=0.4),
                hovertemplate='<b>Title:</b> %{customdata[0]}<br>' +
                              '<b>Author:</b> %{customdata[1]}<br>' +
                              '<b>My Rating:</b> %{customdata[2]}<br>' +
                              '<b>Date:</b> %{x}<br>' +
                              '<extra></extra>',
            )
        )

    # Update the layout
    fig.update_layout(
        title="Timeline of My Ratings",
        xaxis_title="Date Read",
        xaxis=dict(type="date"),  # Ensure the x-axis is treated as dates
        yaxis=dict(
           ticks="",  # Hide ticks
           tickmode="linear",
           showticklabels=False,  # Hide y-axis labels
        ),
    )

    return fig


@capture("graph")
def custom_chart(data_frame):
    fig = go.Figure()
    for index, row in data_frame.iterrows():
        if row["My Rating"] > 0:
            fig.add_trace(
                go.Scatter(
                    x=[row["My Rating"], row["Average Rating"]],
                    y=[row["Title"], row["Title"]],
                    mode="markers+lines",
                    line=dict(color="gray", width=2),
                    marker=dict(color=["blue", "orange"], size=10),
                    showlegend=False,
                )
            )
    fig.update_layout(
        title="Dumbbell Chart: My Rating vs Average Rating",
        xaxis_title="Rating",
        yaxis_title="Books",
        xaxis=dict(range=[0, 5]),
        yaxis=dict(
            tickmode="linear",
            showticklabels=False,  # Hide y-axis labels
        ),
        height=600,
    )

    return fig


@capture("graph")
def pages_books_totals_chart(data_frame):
    # Convert 'Date Read' to datetime
    data_frame["Date Read"] = pd.to_datetime(data_frame["Date Read"])

    # Sort data by 'Date Read'
    data_frame = data_frame.sort_values("Date Read")

    # Calculate cumulative sum of 'Number of Pages'
    data_frame["Cumulative Pages"] = data_frame["Number of Pages"].cumsum()

    # Extract year from 'Date Read'
    data_frame["Year"] = data_frame["Date Read"].dt.year

    # Count total books read per year
    books_per_year = data_frame.groupby("Year").size()

    # Create figure
    fig = go.Figure()

    # Add line chart for cumulative pages
    fig.add_trace(
        go.Scatter(
            x=data_frame["Date Read"],
            y=data_frame["Cumulative Pages"],
            mode="lines",
            name="Cumulative Pages",
            zorder=1,  # Ensure the line chart is rendered on top of the bar chart
        )
    )

    # Add bar chart for total books read per year
    fig.add_trace(
        go.Bar(
            x=books_per_year.index,
            y=books_per_year.values,
            name="Total Books Read",
            yaxis="y2",
            opacity=0.5,
        )
    )

    # Update layout
    fig.update_layout(
        title="Cumulative Pages Read and Total Books Read Per Year",
        xaxis_title="Date",
        yaxis=dict(title="Cumulative Pages", rangemode="tozero"),
        yaxis2=dict(title="Total Books Read", overlaying="y", side="right", tickmode="sync", rangemode="tozero"),
    )

    return fig


df = pd.read_csv("filtered_books.csv")
df["Date Read"] = pd.to_datetime(df["Date Read"], dayfirst=True)


########### Model code ############
model = vm.Dashboard(
    pages=[
        vm.Page(
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=scatter_chart(df),
                ),
            ],
            title="This year's reading",
            layout=vm.Layout(grid=[[0]]),
            controls=[],
        ),
        vm.Page(
            components=[
                vm.Graph(
                    id="pages_books_totals_chart",
                    figure=pages_books_totals_chart(df),
                )
            ],
            title="Pages and Book totals over the years",
            layout=vm.Layout(grid=[[0]]),
            controls=[
                vm.Filter(
                    column="Year Published",
                    targets=["pages_books_totals_chart"],
                    selector=vm.RangeSlider(type="range_slider", title="Year Range"),
                )
            ],
        ),
        vm.Page(
            components=[
                vm.Graph(
                    id="custom_chart",
                    figure=custom_chart(df.sort_values(by="Title", ascending=False)),
                ),
            ],
            title="Ratings over the years",
            layout=vm.Layout(grid=[[0]]),
            controls=[],
        ),
    ],
    title="Book Reading Dashboard",
)

if __name__ == "__main__":
    Vizro().build(model).run()
