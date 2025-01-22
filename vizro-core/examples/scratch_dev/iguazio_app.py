"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
from custom_charts import (
    custom_box_chart,
    custom_heatmap,
    custom_map_chart,
    custom_pie_chart_concern,
    custom_pie_chart_upsale,
    custom_polar,
    custom_scatter_chart,
)
from vizro import Vizro
from vizro.figures._kpi_cards import kpi_card

df = pd.read_excel("output.xlsx")


def count_unique_agents(data_frame):
    unique_agents = data_frame["Agent ID"].drop_duplicates()

    return pd.DataFrame(unique_agents)


def count_unique_callers(data_frame):
    unique_callers = data_frame["Caller ID"].drop_duplicates()

    return pd.DataFrame(unique_callers)


def get_percent_upsales(data_frame):
    data = data_frame.loc[df["Upsale Attempted"] == True]
    return data


page = vm.Page(
    title="Call Center Dashboard",
    layout=vm.Layout(
        grid=[
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
            [3, 3, 3, 3],
            [3, 3, 3, 3],
            [4, 4, 4, 4],
            [4, 4, 4, 4],
            [4, 4, 4, 4],
            [5, 5, 5, 5],
            [5, 5, 5, 5],
            [5, 5, 5, 5],
        ],
        row_min_height="140px",
    ),
    components=[
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[0, 1, 2, 3, 4]], col_gap="20px"),
            components=[
                vm.Figure(
                    figure=kpi_card(
                        data_frame=df, agg_func="count", value_column="Caller ID", title="Number of calls", icon="call"
                    )
                ),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=count_unique_agents(data_frame=df),
                        agg_func="count",
                        value_column="Agent ID",
                        title="Number of agents",
                        icon="support_agent",
                    )
                ),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=count_unique_callers(data_frame=df),
                        agg_func="count",
                        value_column="Caller ID",
                        title="Number of callers",
                        icon="person",
                    )
                ),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=df,
                        value_column="Concern Addressed",
                        title="concerns addressed",
                        value_format="{value:.0%}",
                        agg_func="mean",
                        icon="percent",
                    )
                ),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=get_percent_upsales(df),
                        value_column="Upsale Success",
                        title="upsale",
                        value_format="{value:.0%}",
                        icon="percent",
                        agg_func="mean",
                    )
                ),
            ],
        ),
        vm.Container(
            title="Call outcomes",
            layout=vm.Layout(
                grid=[
                    [0, 0, 1, 1],
                ],
            ),
            components=[
                vm.Graph(figure=custom_pie_chart_concern(df)),
                vm.Graph(figure=custom_pie_chart_upsale(df)),
            ],
        ),
        vm.Container(
            title="",
            layout=vm.Layout(
                grid=[
                    [0, 0, 1, 1],
                ]
            ),
            components=[
                vm.Graph(figure=custom_scatter_chart(df), title="Agent Tone vs Client Tone with % Concerns Addressed"),
                vm.Graph(figure=custom_polar(df), title="Agent qualities"),
            ],
        ),
        vm.Graph(figure=custom_box_chart(df)),
        vm.Graph(figure=custom_heatmap(df)),
        vm.Graph(figure=custom_map_chart(df)),
    ],
    controls=[
        vm.Filter(column="Agent ID", selector=vm.Dropdown()),
        vm.Filter(column="Caller ID", selector=vm.Dropdown()),
    ],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
