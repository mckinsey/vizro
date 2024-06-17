"""Example to show dashboard configuration."""

import pandas as pd
import vizro.models as vm
from utils._charts import COLUMN_DEFS, KPI, bar, choropleth, line, pie
from utils._helper import clean_data_and_add_columns
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.tables import dash_ag_grid

# DATA --------------------------------------------------------------------------------------------
df_complaints = pd.read_csv("https://query.data.world/s/glbdstahsuw3hjgunz3zssggk7dsfu?dws=00000")
df_complaints = clean_data_and_add_columns(df_complaints)
vm.Container.add_type("components", KPI)

# SUB-SECTIONS ------------------------------------------------------------------------------------
kpi_banner = vm.Container(
    id="kpi-banner",
    title="",
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
    ],
)

bar_charts_tabbed = vm.Tabs(
    tabs=[
        vm.Container(
            title="By Issue",
            components=[
                vm.Graph(
                    figure=bar(
                        data_frame=df_complaints,
                        y="Issue",
                        x="Complaint ID",
                    ),
                )
            ],
        ),
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
        vm.Container(
            title="By Channel",
            components=[
                vm.Graph(
                    figure=bar(
                        data_frame=df_complaints,
                        y="Channel",
                        x="Complaint ID",
                    ),
                )
            ],
        ),
        vm.Container(
            title="By Region",
            components=[
                vm.Graph(
                    figure=bar(
                        data_frame=df_complaints,
                        y="Region",
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
    layout=vm.Layout(
        grid=[
            [0, 0],
            [1, 2],
            [1, 2],
            [1, 3],
            [1, 3],
        ],
    ),
    components=[
        kpi_banner,
        bar_charts_tabbed,
        vm.Graph(figure=line(data_frame=df_complaints, y="Complaint ID", x="Year-Month Received")),
        vm.Graph(
            figure=pie(
                data_frame=df_complaints[df_complaints["Company response - Closed"] != "Not closed"],
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

page_region = vm.Page(
    title="Regional View",
    layout=vm.Layout(grid=[[0, 0]] + [[1, 2]] * 4),
    components=[
        vm.Card(
            text="""
        ##### Click on a state inside the map to filter the bar charts on the right.

        - Which state has the most complaints?
        - What are the three biggest issues in California?
        - What is the product with the most complaints in Texas?
        """
        ),
        vm.Graph(
            figure=choropleth(
                data_frame=df_complaints,
                locations="State",
                color="Complaint ID",
                title="Complaints by State",
                custom_data=["State"],
            ),
            actions=[
                vm.Action(
                    function=filter_interaction(targets=["regional-issue", "regional-product"]),
                )
            ],
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="By Issue",
                    components=[
                        vm.Graph(
                            id="regional-issue",
                            figure=bar(
                                data_frame=df_complaints,
                                y="Issue",
                                x="Complaint ID",
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
                            ),
                        )
                    ],
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(column="Region", selector=vm.Checklist()),
        vm.Filter(column="State"),
        vm.Filter(column="Product"),
        vm.Filter(column="Issue"),
    ],
)

page_table = vm.Page(
    title="List of complaints",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(
                data_frame=df_complaints,
                columnDefs=COLUMN_DEFS,
                dashGridOptions={"pagination": True},
            )
        )
    ],
)

dashboard = vm.Dashboard(
    pages=[page_exec, page_region, page_table],
    title="Cumulus Financial Corporation",
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
