"""Example to show dashboard configuration."""

import pandas as pd
import vizro.models as vm
from utils._charts import COLUMN_DEFS, FlexContainer, area, bar, choropleth, pie
from utils._helper import clean_data_and_add_columns, create_data_for_kpi_cards
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.figures import kpi_card_reference
from vizro.tables import dash_ag_grid

# DATA --------------------------------------------------------------------------------------------
df_complaints = pd.read_csv("https://query.data.world/s/glbdstahsuw3hjgunz3zssggk7dsfu?dws=00000")
df_complaints = clean_data_and_add_columns(df_complaints)
df_kpi_cards = create_data_for_kpi_cards(df_complaints)
vm.Page.add_type("components", FlexContainer)


# SUB-SECTIONS ------------------------------------------------------------------------------------
kpi_banner = FlexContainer(
    components=[
        vm.Figure(
            id="kpi-reverse-coloring",
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Total Complaints_2019",
                reference_column="Total Complaints_2018",
                title="Total Complaints",
                value_format="{value:.0f}",
                reference_format="{delta_relative:+.1%} vs. 2018 ({reference:.0f})",
                icon="person",
            ),
        ),
        vm.Figure(
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Closed Complaints_2019",
                reference_column="Closed Complaints_2018",
                title="Closed Complaints",
                value_format="{value:.1f}%",
                reference_format="{delta:+.1f}pp  vs. 2018 ({reference:.1f}%)",
                icon="inventory",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Timely response_2019",
                reference_column="Timely response_2018",
                title="Timely Response",
                value_format="{value:.1f}%",
                reference_format="{delta:+.1f}pp  vs. 2018 ({reference:.1f}%)",
                icon="timer",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Closed w/o cost_2019",
                reference_column="Closed w/o cost_2018",
                title="Closed w/o cost",
                value_format="{value:.1f}%",
                reference_format="{delta:.1f}pp vs. 2018 ({reference:.1f}%)",
                icon="payments",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                df_kpi_cards,
                value_column="Consumer disputed_2019",
                reference_column="Consumer disputed_2018",
                title="Consumer disputed",
                value_format="{value:.1f}%",
                reference_format="{delta:+.1f}pp vs. 2018 ({reference:.1f}%)",
                icon="sentiment_dissatisfied",
            )
        ),
    ],
    classname="kpi-banner",
)

bar_charts_tabbed = vm.Tabs(
    tabs=[
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
    ],
)

# PAGES --------------------------------------------------------------------------------------
page_exec = vm.Page(
    title="Executive View",
    layout=vm.Layout(
        grid=[
            [0, 0],
            [0, 0],
            [1, 2],
            [1, 2],
            [1, 2],
            [1, 3],
            [1, 3],
            [1, 3],
        ],
    ),
    components=[
        kpi_banner,
        bar_charts_tabbed,
        vm.Graph(figure=area(data_frame=df_complaints, y="Complaint ID", x="Month")),
        vm.Graph(
            figure=pie(
                data_frame=df_complaints[df_complaints["Company response - Closed"] != "Not closed"],
                values="Complaint ID",
                names="Company response - Closed",
                title="Closed company responses",
            )
        ),
    ],
)

page_region = vm.Page(
    title="Regional View",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Graph(
            figure=choropleth(
                data_frame=df_complaints,
                locations="State",
                color="Complaint ID",
                title="Complaints by State <br><sup> ⤵ Click on a state to filter the "
                "charts on the right. Refresh the page to deselect.</sup>",
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
    title="Cumulus Financial Corp. - Fiscal Year 2019",
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
