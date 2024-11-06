"""Dev app to try things out."""
import time
import yaml

import dash
import pandas as pd
from flask_caching import Cache

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager

print("INITIALIZING")

# FILTER_COLUMN = "species"
FILTER_COLUMN = "sepal_length"


def slow_load(sample_size=3):
    # time.sleep(2)
    df = px.data.iris().sample(sample_size)
    print(f'SLOW LOAD - {sorted(df["species"].unique().tolist())} - sample_size = {sample_size}')
    return df


def load_from_file():
    with open('data.yaml', 'r') as file:
        data = yaml.safe_load(file)
        data = data or pd.DataFrame()

    # Load the full iris dataset
    df = px.data.iris()

    # Load the first N rows of each species. N per species is defined in the data.yaml file.
    if FILTER_COLUMN == "species":
        final_df = pd.concat(objs=[
            df[df[FILTER_COLUMN] == 'setosa'].head(data.get("setosa", 0)),
            df[df[FILTER_COLUMN] == 'versicolor'].head(data.get("versicolor", 0)),
            df[df[FILTER_COLUMN] == 'virginica'].head(data.get("virginica", 0)),
        ], ignore_index=True)
    elif FILTER_COLUMN == "sepal_length":
        final_df = df[
            df[FILTER_COLUMN].between(data.get("min", 0), data.get("max", 0), inclusive="both")
        ]
    else:
        raise ValueError("Invalid FILTER_COLUMN")

    return final_df


data_manager["dynamic_df"] = load_from_file

# # TODO-DEV: Turn on/off caching to see how it affects the app.
# data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
# data_manager["dynamic_df"] = slow_load
# data_manager["dynamic_df"].timeout = 5


homepage = vm.Page(
    title="Homepage",
    components=[
        vm.Card(text="This is the homepage."),
    ],
)

another_page = vm.Page(
    title="Test update control options",
    components=[
        vm.Graph(
            id="graph_1_id",
            figure=px.bar(
                data_frame="dynamic_df",
                x="species",
                color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
            )
        ),
        # vm.Graph(
        #     id="graph_2_id",
        #     figure=px.scatter(
        #         data_frame="dynamic_df",
        #         x="sepal_length",
        #         y="petal_width",
        #         color="species",
        #     )
        # ),

    ],
    controls=[
        vm.Filter(
            id="filter_container_id",
            column=FILTER_COLUMN,

            # selector=vm.Dropdown(id="filter_id"),
            # selector=vm.Dropdown(id="filter_id", value=["setosa"]),

            # selector=vm.Checklist(id="filter_id"),
            # selector=vm.Checklist(id="filter_id", value=["setosa"]),

            # selector=vm.Dropdown(id="filter_id", multi=False),
            # selector=vm.Dropdown(id="filter_id", multi=False, value="setosa"),

            # selector=vm.RadioItems(id="filter_id"),
            # selector=vm.RadioItems(id="filter_id", value="setosa"),

            selector=vm.Slider(id="filter_id"),
            # selector=vm.Slider(id="filter_id", value=6),

            # selector=vm.RangeSlider(id="filter_id"),
            # selector=vm.RangeSlider(id="filter_id", value=[5, 7]),

            # TEST CASES:
            #   no selector
            #           WORKS
            #   multi=True
            #       default
            #           WORKS
            # selector=vm.Slider(id="filter_id", step=0.5),
            #       options: list
            #           WORKS - but options doesn't mean anything because options are dynamically overwritten.
            # selector=vm.Dropdown(options=["setosa", "versicolor"]),
            #       options: empty list
            #           WORKS
            # selector=vm.Dropdown(options=[]),
            #       options: dict
            #           WORKS - but "label" is always overwritten.
            # selector=vm.Dropdown(options=[{"label": "Setosa", "value": "setosa"}, {"label": "Versicolor", "value": "versicolor"}]),
            #       options list; value
            #           WORKS
            # selector=vm.Dropdown(options=["setosa", "versicolor"], value=["setosa"]),
            #       options list; empty value
            #           WORKS
            # selector=vm.Dropdown(options=["setosa", "versicolor"], value=[]),
            #       strange options
            #           WORKS
            # selector=vm.Dropdown(options=["A", "B", "C"]),
            #       strange options with strange value
            #           WORKS - works even for the dynamic False, and this is OK.
            # selector=vm.Dropdown(options=["A", "B", "C"], value=["XYZ"]),
            #
            #
            #   multi=False -> TLDR: Doesn't work if value is cleared. Other combinations are same as multi=True.
            #       default
            #           DOES NOT WORK - Doesn't work if value is cleared. Then persistence storage become "null" and our
            #           placeholder component dmc.DateRangePicker can't process null value. It expects a value or a list
            #           of values. SOLUTION -> Create the "universal Vizro placeholder component"
            # selector=vm.Dropdown(multi=False),
            #       options: list - because options are dynamically overwritten.
            #           WORKS - but options doesn't mean anything because options are dynamically overwritten.
            # selector=vm.Dropdown(multi=False, options=["setosa", "versicolor"]),
            #       options: empty list
            #           WORKS
            # selector=vm.Dropdown(multi=False, options=[]),
            #       options: dict
            # selector=vm.Dropdown(multi=False, options=[{"label": "Setosa", "value": "setosa"}, {"label": "Versicolor", "value": "versicolor"}]),
            #       options list; value
            #           WORKS
            # selector=vm.Dropdown(multi=False, options=["setosa", "versicolor"], value="setosa"),
            #       options list; None value
            #           WORKS
            # selector=vm.Dropdown(multi=False, options=["setosa", "versicolor"], value=None),
            #       strange options
            #           WORKS
            # selector=vm.Dropdown(multi=False, options=["A", "B", "C"]),
            #       strange options with strange value
            #           WORKS
            # selector=vm.Dropdown(multi=False, options=["A", "B", "C"], value="XYZ"),
        ),
        vm.Parameter(
            id="parameter_x",
            targets=["graph_1_id.x",],
            selector=vm.Dropdown(
                options=["species", "sepal_width"],
                value="species",
                multi=False,
            )
        )
        # vm.Parameter(
        #     id="parameter_container_id",
        #     targets=[
        #         "graph_1_id.data_frame.sample_size",
        #         # "graph_2_id.data_frame.sample_size",
        #     ],
        #     selector=vm.Slider(
        #         id="parameter_id",
        #         min=1,
        #         max=10,
        #         step=1,
        #         value=10,
        #     )
        # ),
    ],
)

dashboard = vm.Dashboard(pages=[homepage, another_page])

if __name__ == "__main__":
    app = Vizro().build(dashboard)

    print("RUNNING\n")

    app.run(dev_tools_hot_reload=False)
