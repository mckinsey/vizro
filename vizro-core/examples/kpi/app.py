"""Example to show dashboard configuration."""

import pandas as pd
import vizro.models as vm
from utils._charts import COLUMN_DEFS, KPI, bar, chloropleth, line, pie
from utils._helper import clean_data_and_add_columns
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.tables import dash_ag_grid

# DATA --------------------------------------------------------------------------------------------
df_complaints = pd.read_csv("data/Financial Consumer Complaints.csv")
df_complaints = clean_data_and_add_columns(df_complaints)

vm.Page.add_type("components", KPI)
vm.Container.add_type("components", KPI)

# TODO: Enable selection of year filter
# TODO: Enable current year vs. past year comparison
# TODO: Enable dynamic KPI Cards
# TODO: Make KPI Card row horizontally scrollable if no space
# TODO: Bar - How to enable drill-downs for Issue/Sub-issue and Product/Sub-product?
# TODO: Bar - Reformat numbers with commas in bar chart
# TODO: Bar - Left-align y-axis labels
# TODO: Bar - Shorten labels
# TODO: Line - Customize function to always show selected year vs. past year


page_exec = vm.Page(
    title="Executive View",
    layout=vm.Layout(
        grid=[
            [0, 1, 2, 3, 4, 5],
            [0, 1, 2, 3, 4, 5],
            [6, 6, 6, 7, 7, 7],
            [6, 6, 6, 7, 7, 7],
            [6, 6, 6, 7, 7, 7],
            [6, 6, 6, 7, 7, 7],
            [6, 6, 6, 8, 8, 8],
            [6, 6, 6, 8, 8, 8],
            [6, 6, 6, 8, 8, 8],
            [6, 6, 6, 8, 8, 8],
        ],
    ),
    components=[
        # Note: For some KPIs the icon/sign go in opposite directions as an increase e.g. in complaints is negative
        KPI(
            title="Total Complaints",
            value="75.513",
            icon="arrow_circle_up",
            sign="delta-neg",
            ref_value="6.8% vs. LY",
        ),
        KPI(
            title="Closed Complaints",
            value="99.6%",
            icon="arrow_circle_up",
            sign="delta-pos",
            ref_value="+0.2% vs. LY",
        ),
        KPI(
            title="Open Complaints",
            value="0.4%",
            icon="arrow_circle_down",
            sign="delta-pos",
            ref_value="-0.2% vs. LY",
        ),
        KPI(
            title="Timely Response",
            value="98.1%",
            icon="arrow_circle_up",
            sign="delta-pos",
            ref_value="+10.5% vs. LY",
        ),
        KPI(
            title="Closed w/o cost",
            value="84.5%",
            icon="arrow_circle_down",
            sign="delta-neg",
            ref_value="-8.5% vs. LY",
        ),
        KPI(
            title="Consumer disputed",
            value="9.5%",
            icon="arrow_circle_up",
            sign="delta-neg",
            ref_value="+2.3% vs. LY",
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="By Issue",
                    components=[
                        vm.Graph(
                            id="bar-issue",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Issue",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
                vm.Container(
                    title="By Product",
                    components=[
                        vm.Graph(
                            id="bar-product",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Product",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
                vm.Container(
                    title="By Channel",
                    components=[
                        vm.Graph(
                            id="bar-channel",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Channel",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
                vm.Container(
                    title="By Region",
                    components=[
                        vm.Graph(
                            id="bar-region",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Region",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
            ],
        ),
        vm.Graph(
            id="line-date",
            figure=line(
                data_frame=df_complaints, y="Complaint ID", x="Year-Month Received", color_discrete_sequence=["#1A85FF"]
            ),
        ),
        vm.Graph(
            figure=pie(
                data_frame=df_complaints[df_complaints["Company response - Closed"] != "Not closed"],
                color_discrete_sequence=["#1a85ff", "#7ea1ee", "#adbedc", "#df658c", "#d41159"],
                custom_order=[
                    "Closed with explanation",
                    "Closed without relief",
                    "Closed with non-monetary relief",
                    "Closed with relief",
                    "Closed with monetary relief",
                ],
                values="Complaint ID",
                names="Company response - Closed",
                title="Closed company responses",
            )
        ),
    ],
)


# TODO: Table-view - Check why date format does not work on `Date Received`
# TODO: Table-view - Add icons to `Timely` column
page_table = vm.Page(
    title="List of complaints",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(
                data_frame=df_complaints,
                columnDefs=COLUMN_DEFS,
            )
        )
    ],
)

page_region = vm.Page(
    title="Regional View",
    layout=vm.Layout(grid=[[0, 0]] + [[1, 2]] * 5),
    components=[
        vm.Card(text="""Placeholder"""),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="By Region",
                    components=[
                        vm.Graph(
                            id="regional-region",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Region",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                                custom_data=["Region"],
                            ),
                            actions=[vm.Action(function=filter_interaction(targets=["map-region"]))],
                        )
                    ],
                ),
                vm.Container(
                    title="By Issue",
                    components=[
                        vm.Graph(
                            id="regional-issue",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Issue",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
                vm.Container(
                    title="By Product",
                    components=[
                        vm.Graph(
                            id="regional-product",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Product",
                                x="Complaint ID",
                                color_discrete_sequence=["#1A85FF"],
                            ),
                        )
                    ],
                ),
            ],
        ),
        vm.Graph(
            id="map-region",
            figure=chloropleth(
                data_frame=df_complaints,
                locations="State",
                color="Complaint ID",
                title="Complaints by State",
                custom_data=["State"],
            ),
            actions=[
                vm.Action(
                    function=filter_interaction(targets=["regional-product", "regional-issue", "regional-region"])
                )
            ],
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[page_exec, page_region, page_table],
    title="Cumulus Financial",
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Executive View", icon="Leaderboard", pages=["Executive View"]),
                vm.NavLink(label="Regional View", icon="South America", pages=["Regional View"]),
                vm.NavLink(label="Table View", icon="Table View", pages=["List of complaints"]),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
