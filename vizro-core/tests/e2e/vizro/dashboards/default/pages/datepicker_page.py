import time

import e2e.vizro.constants as cnst
import pandas as pd
from flask_caching import Cache

import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager
from vizro.tables import dash_data_table

datepicker_df = pd.DataFrame(
    [
        [
            "2016-05-16 20:42:31",
            "Male",
            35,
            "$30,000 to $39,999",
            "Employed for wages",
            "mechanical drafter",
            "Associate degree",
            None,
        ],
        [
            "2016-05-16",
            "Male",
            21,
            "$1 to $10,000",
            "Out of work and looking for work",
            "-",
            "Some college, no degree",
            "join clubs/socual clubs/meet ups",
        ],
        [
            "2016-05-17",
            "Male",
            22,
            "$0",
            "Out of work but not currently looking for work",
            "unemployed, Some college",
            "no degree",
            "Other exercise",
        ],
        [
            "2016-05-18",
            "Male",
            19,
            "$1 to $10,000",
            "A student",
            "student",
            "Some college, no degree",
            "Joined a gym/go to the gym",
        ],
        [
            "2016-05-18",
            "Male",
            23,
            "$30,000 to $39,999",
            "Employed for wages",
            "Factory worker",
            "High school graduate, diploma or the equivalent (for example: GED)",
            None,
        ],
        [
            "2016-05-19",
            "Male",
            23,
            "$30,000 to $39,999",
            "Employed for wages",
            "Factory worker",
            "High school graduate, diploma or the equivalent (for example: GED)",
            None,
        ],
    ],
    columns=["time", "gender", "age", "income", "employment", "job_title", "edu_level", "improve_yourself_how"],
)


def load_datepicker_data():
    datepicker_df["time"] = pd.to_datetime(datepicker_df["time"], format="mixed")
    time.sleep(0.25)  # for testing, to catch reloading of the chart
    return datepicker_df


data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})
data_manager["datepicker_df"] = load_datepicker_data
data_manager["datepicker_df"].timeout = 10


datepicker_page = vm.Page(
    title=cnst.DATEPICKER_PAGE,
    id=cnst.DATEPICKER_PAGE,
    layout=vm.Grid(grid=[[0, 1], [0, 1], [2, 3], [2, 3]]),
    components=[
        vm.Graph(
            id=cnst.BAR_POP_RANGE_ID,
            figure=px.bar(
                "datepicker_df",
                x="time",
                y="age",
                color="age",
            ),
        ),
        vm.Graph(
            id=cnst.BAR_POP_DATE_ID,
            figure=px.bar(
                "datepicker_df",
                x="time",
                y="age",
                color="age",
            ),
        ),
        vm.Table(
            id=cnst.TABLE_POP_RANGE_ID,
            title="Table Pop Range",
            figure=dash_data_table(
                data_frame="datepicker_df",
            ),
        ),
        vm.Table(
            id=cnst.TABLE_POP_DATE_ID,
            title="Table Pop Date",
            figure=dash_data_table(
                data_frame="datepicker_df",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="time",
            selector=vm.DatePicker(
                id=cnst.DATEPICKER_RANGE_ID,
                title="Pick a date range",
                value=["2016-05-16", "2016-05-19"],
                max="2016-06-01",
            ),
            targets=[cnst.TABLE_POP_RANGE_ID, cnst.BAR_POP_RANGE_ID],
        ),
        vm.Filter(
            column="time",
            selector=vm.DatePicker(id=cnst.DATEPICKER_SINGLE_ID, title="Pick a date", range=False),
            targets=[cnst.TABLE_POP_DATE_ID, cnst.BAR_POP_DATE_ID],
        ),
    ],
)
