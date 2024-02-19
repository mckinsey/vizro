"""Rough example used by developers."""

from datetime import datetime

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models._components.form._text_area import TextArea
from vizro.models._components.form._user_input import UserInput
from vizro.tables import dash_data_table

iris = px.data.iris()

# Only added to container.components directly for dev example
vm.Container.add_type("components", UserInput)
vm.Container.add_type("components", TextArea)

page = vm.Page(
    title="User Text Inputs",
    layout=vm.Layout(grid=[[0, 1]], col_gap="40px"),
    components=[
        vm.Container(
            title="Input Components",
            components=[
                UserInput(title="Input - Text (single-line)", placeholder="Enter text here"),
                TextArea(title="Input - Text (multi-line)", placeholder="Enter multi-line text here"),
            ],
        ),
        vm.Graph(
            id="for_custom_chart",
            figure=px.scatter(iris, title="Iris Dataset", x="sepal_length", y="petal_width", color="sepal_width"),
        ),
    ],
)

# CREATE FAKE DATA
column = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4]
row = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
value = [1, 7, 3, 5, 2, 10, 9, 1, 3, 7, 5, 8, 2, 9, 1, 2, 7, 5, 3, 2]
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

date_time_new = [datetime.strptime(date, "%Y-%m-%d").date() for date in date_time]

data["COLUMN1"] = column
data["ROW1"] = row
data["VALUE"] = value
data["GROUP"] = group
data["DATE_TIME"] = date_time_new

page_1 = vm.Page(
    title="Datepicker page",
    components=[vm.Table(id="table", figure=dash_data_table(data_frame=data))],
    controls=[
        vm.Filter(
            column="DATE_TIME",
            selector=vm.DateRangePicker(
                title="Pick a date",
                min="2023-01-01",
                value=["2024-01-01", "2024-03-01"],
                max="2024-07-07",
            ),
            # selector=vm.DatePicker(title="Pick a date", min_date='2023-01-01', value=['2024-01-01']),
        )
    ],
)

dashboard = vm.Dashboard(pages=[page, page_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
