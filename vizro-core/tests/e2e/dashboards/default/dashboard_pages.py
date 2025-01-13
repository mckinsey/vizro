from flask_caching import Cache

import vizro.models as vm
import e2e_constants as cnst
import vizro.plotly.express as px
import pandas as pd
from vizro.actions import export_data
from vizro.figures import kpi_card, kpi_card_reference
from vizro.tables import dash_data_table, dash_ag_grid
from vizro.managers import data_manager

iris = px.data.iris()
gapminder = px.data.gapminder()
kpi_df = pd.DataFrame(
    [[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]],
    columns=["Actual", "Reference", "Category"],
)
datepicker_df = pd.DataFrame(
    [
        ["2016-05-16 20:42:31", "Male", 35, "$30,000 to $39,999", "Employed for wages", "mechanical drafter", "Associate degree", None],
        ["2016-05-16", "Male", 21, "$1 to $10,000", "Out of work and looking for work", "-", "Some college, no degree", "join clubs/socual clubs/meet ups"],
        ["2016-05-17", "Male", 22, "$0", "Out of work but not currently looking for work", "unemployed, Some college", "no degree", "Other exercise"],
        ["2016-05-18", "Male", 19, "$1 to $10,000", "A student", "student", "Some college, no degree", "Joined a gym/go to the gym"],
        ["2016-05-18", "Male", 23, "$30,000 to $39,999", "Employed for wages", "Factory worker", "High school graduate, diploma or the equivalent (for example: GED)", None],
        ["2016-05-19", "Male", 23, "$30,000 to $39,999", "Employed for wages", "Factory worker", "High school graduate, diploma or the equivalent (for example: GED)", None]],
    columns=["time", "gender", "age", "income", "employment", "job_title", "edu_level", "improve_yourself_how"],
)


def load_datepicker_data():
    datepicker_df["time"] = pd.to_datetime(datepicker_df["time"], format="mixed")
    return datepicker_df


data_manager.cache = Cache(
    config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"}
)
data_manager["datepicker_df"] = load_datepicker_data
data_manager["datepicker_df"].timeout = 10

homepage = vm.Page(
    title=cnst.HOME_PAGE,
    id=cnst.HOME_PAGE_ID,
    layout=vm.Layout(grid=[[0, 4], [1, 4], [2, 4], [3, 4]]),
    components=[
        vm.Card(
            text="""
                # This is an <h1> tag
                ## This is an <h2> tag
                ###### This is an <h6> tag
                \n
                >
                > Block quotes are used to highlight text.
                >
                \n
                * Item 1
                * Item 2
                \n
                 *This text will be italic*
                _This will also be italic_
                **This text will be bold**
                _You **can** combine them_
            """,
        ),
        vm.Card(
            text="""
            ![icon-top](assets/images/icons/content/hypotheses.svg)

            Leads to the filters page on click.
            """,
            href=cnst.FILTERS_PAGE_PATH,
        ),
        vm.Card(
            text="""
            ![icon-top](assets/images/icons/content/features.svg)

            Leads to the datepicker page on click.
            """,
            href=cnst.DATEPICKER_PAGE_PATH,
        ),
        vm.Card(
            text="""
            ![icon-top](assets/images/icons/content/hypotheses.svg)

            Leads to the 404 page on click.
            """,
            href=cnst.PAGE_404_PATH,
        ),
        vm.Graph(
            id=cnst.AREA_GRAPH_ID,
            figure=px.area(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species", targets=[cnst.AREA_GRAPH_ID]),
    ],
)

filters_page = vm.Page(
    title=cnst.FILTERS_PAGE,
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    id=cnst.FILTERS_TAB_CONTAINER,
                    title=cnst.FILTERS_TAB_CONTAINER,
                    components=[
                        vm.Container(
                            id=cnst.FILTERS_COMPONENTS_CONTAINER,
                            title=cnst.FILTERS_COMPONENTS_CONTAINER,
                            layout=vm.Layout(grid=[[0, 1], [0, 1], [0, 2]]),
                            components=[
                                vm.Graph(
                                    id=cnst.SCATTER_GRAPH_ID,
                                    figure=px.scatter(
                                        iris,
                                        x="sepal_length",
                                        y="petal_width",
                                        color="sepal_width",
                                    ),
                                ),
                                vm.Card(
                                    text="""
                    ![icon-top](assets/images/icons/content/features.svg)

                    Leads to the home page on click.
                    """,
                                    href="/",
                                ),
                                vm.Button(
                                    text="Export data",
                                    actions=[
                                        vm.Action(
                                            function=export_data(
                                                targets=[cnst.SCATTER_GRAPH_ID],
                                                file_format="csv",
                                            )
                                        ),
                                        vm.Action(
                                            function=export_data(
                                                targets=[cnst.SCATTER_GRAPH_ID],
                                                file_format="xlsx",
                                            )
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ]
        ),
        vm.Graph(
            id=cnst.BOX_GRAPH_ID,
            figure=px.box(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=[cnst.SCATTER_GRAPH_ID, cnst.BOX_GRAPH_ID],
        ),
        vm.Filter(
            column="species",
            targets=[cnst.SCATTER_GRAPH_ID, cnst.BOX_GRAPH_ID],
            selector=vm.RadioItems(options=["setosa", "versicolor", "virginica"]),
        ),
        vm.Filter(
            column="species",
            targets=[cnst.SCATTER_GRAPH_ID],
            selector=vm.Checklist(options=["setosa", "versicolor", "virginica"]),
        ),
        vm.Filter(
            column="petal_width",
            targets=[cnst.SCATTER_GRAPH_ID],
            selector=vm.Slider(id=cnst.SLIDER_FILTER_FILTERS_PAGE, step=0.5),
        ),
        vm.Filter(
            column="sepal_length",
            targets=[cnst.SCATTER_GRAPH_ID, cnst.BOX_GRAPH_ID],
            selector=vm.RangeSlider(id=cnst.RANGE_SLIDER_FILTER_FILTERS_PAGE, step=1.0),
        ),
    ],
)


parameters_page = vm.Page(
    title=cnst.PARAMETERS_PAGE,
    path=cnst.PARAMETERS_PAGE_PATH,
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    id=cnst.PARAMETERS_TAB_CONTAINER,
                    title=cnst.PARAMETERS_TAB_CONTAINER,
                    components=[
                        vm.Tabs(
                            tabs=[
                                vm.Container(
                                    id=cnst.PARAMETERS_SUB_TAB_CONTAINER_ONE,
                                    title=cnst.PARAMETERS_SUB_TAB_CONTAINER_ONE,
                                    components=[
                                        vm.Graph(
                                            id=cnst.BAR_GRAPH_ID,
                                            figure=px.bar(
                                                iris,
                                                x="sepal_length",
                                                y="petal_width",
                                                color="species",
                                                color_discrete_map={
                                                    "setosa": "black",
                                                    "versicolor": "pink",
                                                },
                                            ),
                                        )
                                    ],
                                ),
                                vm.Container(
                                    id=cnst.PARAMETERS_SUB_TAB_CONTAINER_TWO,
                                    title=cnst.PARAMETERS_SUB_TAB_CONTAINER_TWO,
                                    components=[
                                        vm.Graph(
                                            id=cnst.HISTOGRAM_GRAPH_ID,
                                            figure=px.histogram(
                                                iris,
                                                x="sepal_length",
                                                y="petal_width",
                                                color="species",
                                                color_discrete_map={
                                                    "setosa": "black",
                                                    "versicolor": "pink",
                                                },
                                            ),
                                        ),
                                    ],
                                ),
                            ]
                        )
                    ],
                )
            ]
        ),
        vm.Container(
            id=cnst.PARAMETERS_CONTAINER,
            title=cnst.PARAMETERS_CONTAINER,
            components=[
                vm.Graph(
                    id=cnst.BAR_GRAPH_ID_CONTAINER,
                    figure=px.bar(
                        iris,
                        x="sepal_length",
                        y="petal_width",
                        color="species",
                        color_discrete_map={
                            "setosa": "black",
                            "versicolor": "pink",
                        },
                    ),
                ),
            ],
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[f"{cnst.HISTOGRAM_GRAPH_ID}.color_discrete_map.setosa"],
            selector=vm.Dropdown(
                options=["NONE", "red", "blue"], multi=False, value="blue"
            ),
        ),
        vm.Parameter(
            targets=[f"{cnst.BAR_GRAPH_ID}.color_discrete_map.virginica"],
            selector=vm.Dropdown(
                options=["NONE", "red", "blue"], multi=False, value="blue"
            ),
        ),
        vm.Parameter(
            targets=[f"{cnst.BAR_GRAPH_ID}.title", f"{cnst.HISTOGRAM_GRAPH_ID}.title"],
            selector=vm.RadioItems(options=["red", "blue"], value="blue"),
        ),
        vm.Parameter(
            targets=[f"{cnst.BAR_GRAPH_ID}.y"],
            selector=vm.RadioItems(
                options=["petal_width", "petal_length"], value="petal_width"
            ),
        ),
        vm.Parameter(
            targets=[f"{cnst.BAR_GRAPH_ID}.opacity"],
            selector=vm.Slider(
                min=0, max=1, value=0.2, step=0.2, title="Bubble opacity"
            ),
        ),
        vm.Parameter(
            targets=[f"{cnst.HISTOGRAM_GRAPH_ID}.range_x"],
            selector=vm.RangeSlider(min=4, max=8, step=1.0, title="Range X Histogram"),
        ),
    ],
)


kpi_indicators_page = vm.Page(
    title=cnst.KPI_INDICATORS_PAGE,
    layout=vm.Layout(grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8]]),
    components=[
        # Style 1: Value Only
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                title="Value I",
                agg_func="sum",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                title="Value II",
                agg_func="mean",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                title="Value III",
                agg_func="median",
            )
        ),
        # Style 2: Value and reference value
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Reference",
                reference_column="Actual",
                title="Ref. Value II",
                agg_func="sum",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Actual",
                reference_column="Reference",
                title="Ref. Value I",
                agg_func="sum",
            )
        ),
        vm.Figure(
            id="kpi-card-reverse-coloring",
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Actual",
                reference_column="Reference",
                title="Ref. Value III",
                agg_func="median",
                icon="shopping_cart",
            ),
        ),
        # Style 3: Value and icon
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                icon="shopping_cart",
                title="Icon I",
                agg_func="sum",
                value_format="${value:.2f}",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                icon="payment",
                title="Icon II",
                agg_func="mean",
                value_format="{value:.0f}€",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                icon="monitoring",
                title="Icon III",
                agg_func="median",
            )
        ),
    ],
    controls=[vm.Filter(column="Category")],
)

datepicker_page = vm.Page(
    title=cnst.DATEPICKER_PAGE,
    id=cnst.DATEPICKER_PAGE,
    layout=vm.Layout(grid=[[0, 1], [0, 1], [2, 3], [2, 3]]),
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
                title="Pick a date range",
                value=["2016-05-16", "2016-05-19"],
                max="2016-06-01",
            ),
            targets=[cnst.TABLE_POP_RANGE_ID, cnst.BAR_POP_RANGE_ID],
        ),
        vm.Filter(
            column="time",
            selector=vm.DatePicker(title="Pick a date", range=False),
            targets=[cnst.TABLE_POP_DATE_ID, cnst.BAR_POP_DATE_ID],
        ),
    ],
)

ag_grid_page = vm.Page(
    title=cnst.TABLE_AG_GRID_PAGE,
    components=[
        vm.Container(
            id=cnst.TABLE_AG_GRID_CONTAINER,
            title=cnst.TABLE_AG_GRID_CONTAINER,
            layout=vm.Layout(grid=[[0, 1]], col_gap="0px"),
            components=[
                vm.AgGrid(
                    id=cnst.TABLE_AG_GRID_ID,
                    title="Equal Title One",
                    figure=dash_ag_grid(
                        data_frame=gapminder, dashGridOptions={"pagination": True}
                    ),
                ),
                vm.Graph(
                    id=cnst.BOX_AG_GRID_PAGE_ID,
                    figure=px.box(
                        gapminder, x="continent", y="lifeExp", title="Equal Title One"
                    )
                ),
            ],
        )
    ],
    controls=[
        vm.Filter(
            column="year",
            targets=[cnst.TABLE_AG_GRID_ID],
            selector=vm.Dropdown(value=2007),
        ),
        vm.Filter(
            column="continent",
            targets=[cnst.TABLE_AG_GRID_ID],
            selector=vm.RadioItems(options=["Europe", "Africa", "Americas"]),
        ),
        vm.Filter(
            column="continent",
            targets=[cnst.TABLE_AG_GRID_ID],
            selector=vm.Checklist(options=["Asia", "Oceania"]),
        ),
        vm.Filter(
            column="pop",
            targets=[cnst.TABLE_AG_GRID_ID],
            selector=vm.RangeSlider(step=1000000.0, min=1000000, max=10000000),
        ),
    ],
)