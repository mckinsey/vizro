"""Example to show dashboard configuration."""

import datetime

import numpy as np
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

df = px.data.gapminder()
df_mean = (
    df.groupby(by=["continent", "year"]).agg({"lifeExp": "mean", "pop": "mean", "gdpPercap": "mean"}).reset_index()
)

df_transformed = df.copy()
df_transformed["lifeExp"] = df.groupby(by=["continent", "year"])["lifeExp"].transform("mean")
df_transformed["gdpPercap"] = df.groupby(by=["continent", "year"])["gdpPercap"].transform("mean")
df_transformed["pop"] = df.groupby(by=["continent", "year"])["pop"].transform("sum")
df_concat = pd.concat([df_transformed.assign(color="Continent Avg."), df.assign(color="Country")], ignore_index=True)


df2 = px.data.stocks()
df2["date_as_datetime"] = pd.to_datetime(df2["date"])
df2["date_str"] = df2["date"].astype("str")
df2["perc_from_float"] = np.random.rand(len(df2))
df2["random"] = np.random.uniform(-100000.000, 100000.000, len(df2))


# CREATE FAKE DATA
column = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4]
row = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
value = ["1", "7", "3", "5", "2", "10", "9", "1", "3", "7", "5", "8", "2", "9", "1", "2", "7", "5", "3", "2"]
group = ["A", "B", "C", "D", "E", "E", "D", "C", "B", "A", "A", "E", "C", "B", "D", "A", "D", "B", "C", "E"]
date_time_str = [
    "2023-01-01 20:04:01",
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
    "2024-07-01",
    "2024-07-02",
]
date_time_date = [
    datetime.datetime(2023, 1, 1).date(),
    datetime.datetime(2023, 2, 2).date(),
    datetime.datetime(2023, 3, 3).date(),
    datetime.datetime(2023, 4, 4).date(),
    datetime.datetime(2023, 5, 5).date(),
    datetime.datetime(2023, 6, 6).date(),
    datetime.datetime(2023, 7, 7).date(),
    datetime.datetime(2023, 8, 8).date(),
    datetime.datetime(2023, 9, 9).date(),
    datetime.datetime(2023, 10, 10).date(),
    datetime.datetime(2023, 11, 11).date(),
    datetime.datetime(2023, 12, 12).date(),
    datetime.datetime(2024, 1, 1).date(),
    datetime.datetime(2024, 2, 2).date(),
    datetime.datetime(2024, 3, 3).date(),
    datetime.datetime(2024, 4, 4).date(),
    datetime.datetime(2024, 5, 5).date(),
    datetime.datetime(2024, 6, 6).date(),
    datetime.datetime(2024, 7, 1).date(),
    datetime.datetime(2024, 7, 2).date(),
]
date_time_time = [
    datetime.datetime(2023, 1, 1),
    datetime.datetime(2023, 2, 2),
    datetime.datetime(2023, 3, 3),
    datetime.datetime(2023, 4, 4),
    datetime.datetime(2023, 5, 5),
    datetime.datetime(2023, 6, 6),
    datetime.datetime(2023, 7, 7),
    datetime.datetime(2023, 8, 8),
    datetime.datetime(2023, 9, 9),
    datetime.datetime(2023, 10, 10),
    datetime.datetime(2023, 11, 11),
    datetime.datetime(2023, 12, 12),
    datetime.datetime(2024, 1, 1),
    datetime.datetime(2024, 2, 2),
    datetime.datetime(2024, 3, 3),
    datetime.datetime(2024, 4, 4),
    datetime.datetime(2024, 5, 5),
    datetime.datetime(2024, 6, 6),
    datetime.datetime(2024, 7, 1),
    datetime.datetime(2024, 7, 2),
]

date_time_iso = [
    datetime.date(2023, 1, 1).isoformat(),
    datetime.date(2023, 2, 2).isoformat(),
    datetime.date(2023, 3, 3).isoformat(),
    datetime.date(2023, 4, 4).isoformat(),
    datetime.date(2023, 5, 5).isoformat(),
    datetime.date(2023, 6, 6).isoformat(),
    datetime.date(2023, 7, 7).isoformat(),
    datetime.date(2023, 8, 8).isoformat(),
    datetime.date(2023, 9, 9).isoformat(),
    datetime.date(2023, 10, 10).isoformat(),
    datetime.date(2023, 11, 11).isoformat(),
    datetime.date(2023, 12, 12).isoformat(),
    datetime.date(2024, 1, 1).isoformat(),
    datetime.date(2024, 2, 2).isoformat(),
    datetime.date(2024, 3, 3).isoformat(),
    datetime.date(2024, 4, 4).isoformat(),
    datetime.date(2024, 5, 5).isoformat(),
    datetime.date(2024, 6, 6).isoformat(),
    datetime.date(2024, 7, 1).isoformat(),
    datetime.date(2024, 7, 2).isoformat(),
]

data = pd.DataFrame()

data["COLUMN1"] = column
data["ROW1"] = row
data["VALUE"] = value
data["GROUP"] = group
data["DATE_TIME"] = date_time_str

# data["DATE_TIME"] = pd.to_datetime(data["DATE_TIME"])

date_range_picker = vm.Page(
    title="DateRangePicker",
    components=[vm.AgGrid(id="table", figure=dash_ag_grid(data_frame=data))],
    controls=[
        vm.Filter(
            column="DATE_TIME",
            selector=vm.DatePicker(
                title="Pick a date",
                min="2023-01-01",
                value=["2024-01-01", "2024-03-01"],
                max="2024-07-01",
            ),
        ),
        vm.Filter(
            column="GROUP",
        ),
    ],
)

date_picker = vm.Page(
    title="Datepicker",
    components=[vm.AgGrid(id="table two", figure=dash_ag_grid(data_frame=data))],
    controls=[
        vm.Filter(
            column="DATE_TIME",
            selector=vm.DatePicker(
                range=False,
                title="Pick a date",
                min="2023-01-01",
                value="2024-01-01",
                max="2024-07-01",
            ),
        ),
        vm.Filter(
            column="GROUP",
        ),
    ],
)


dashboard = vm.Dashboard(pages=[date_range_picker, date_picker])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
