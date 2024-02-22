"""Rough example used by developers."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_data_table

iris = px.data.iris()

cards = vm.Page(
    title="Cards",
    components=[
        vm.Card(
            text="""
                # This is an <h1> tag
                ## This is an <h2> tag
                ###### This is an <h6> tag

                >
                > Block quotes are used to highlight text.
                >

                * Item 1
                * Item 2

                *This text will be italic*

                _This will also be italic_

                **This text will be bold**

                _You **can** combine them_
            """
        )
    ],
)

graph = vm.Page(
    title="Graph",
    components=[
        vm.Graph(
            id="scatter_relation",
            figure=px.scatter(data_frame=px.data.gapminder(), x="gdpPercap", y="lifeExp", size="pop"),
        ),
    ],
)

# CREATE FAKE DATA
column = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4]
row = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
value = ["1", "7", "3", "5", "2", "10", "9", "1", "3", "7", "5", "8", "2", "9", "1", "2", "7", "5", "3", "2"]
group = ["A", "B", "C", "D", "E", "E", "D", "C", "B", "A", "A", "E", "C", "B", "D", "A", "D", "B", "C", "E"]
date_time = [
    "2023-01-01",
    "2023-02-02",
    "2023-03-03",
    "2023-04-04",
    "2023-05-05",
    "2023-06-06",
    "2023-07-07",
    "2023-08-08",
    "2023-09-09",
    "2023-10-10",
    "2023-11-11",
    "2023-12-12",
    "2024-01-01",
    "2024-02-02",
    "2024-03-03",
    "2024-04-04",
    "2024-05-05",
    "2024-06-06",
    "2024-07-07",
    "2024-08-08",
]

data = pd.DataFrame()

# date_time_new = [datetime.strptime(date, "%Y-%m-%d") for date in date_time]

data["COLUMN1"] = column
data["ROW1"] = row
data["VALUE"] = value
data["GROUP"] = group
data["DATE_TIME"] = date_time

# data["DATE_TIME"] = pd.to_datetime(data["DATE_TIME"])

page_1 = vm.Page(
    title="Datepicker page",
    components=[vm.Table(id="table", figure=dash_data_table(data_frame=data))],
    controls=[
        vm.Filter(
            column="DATE_TIME",
            selector=vm.DatePicker(
                title="Pick a date",
                min="2023-01-01",
                value=["2024-01-01", "2024-03-01"],
                max="2024-07-07",
            ),
            # selector=vm.DatePicker(title="Pick a date", min_date='2023-01-01', value=['2024-01-01'], multi=False),
        )
    ],
)

# test for DatePicker use in Parameter


@capture("graph")
def bar_with_highlight(data_frame, x, highlight_bar=None):
    """Custom chart to test using DatePicker with Parameter."""
    fig = px.bar(data_frame=data_frame, x=x)

    fig["data"][0]["marker"]["color"] = ["orange" if c == highlight_bar else "blue" for c in fig["data"][0]["x"]]
    return fig


page_2 = vm.Page(
    title="Custom chart",
    components=[
        vm.Graph(
            id="enhanced_bar",
            figure=bar_with_highlight(
                x="date",
                data_frame=px.data.stocks(),
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["enhanced_bar.highlight_bar"],
            selector=vm.DatePicker(min="2018-01-01", max="2023-01-01", value="2018-04-01", multi=False),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_1, page_2])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
