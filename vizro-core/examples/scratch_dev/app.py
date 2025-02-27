"""Test app"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.models.types import capture
from vizro.figures import kpi_card

tips = px.data.tips()


@capture("graph")
def bar_mean(data_frame, x, y):
    df_agg = data_frame.groupby(x).agg({y: "mean"}).reset_index()
    fig = px.bar(df_agg, x=x, y=y, labels={"tip": "Average Tip ($)"})
    fig.update_traces(width=0.6)
    return fig


first_page = vm.Page(
    title="Data",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(tips),
            footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
            Practical Data Analysis: Case Studies in Business Statistics.
            Homewood, IL: Richard D. Irwin Publishing.""",
        ),
    ],
)

second_page = vm.Page(
    title="Summary",
    layout=vm.Layout(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
    components=[
        vm.Figure(
            figure=kpi_card(
                data_frame=tips,
                value_column="total_bill",
                agg_func="mean",
                value_format="${value:.2f}",
                title="Average Bill",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=tips, value_column="tip", agg_func="mean", value_format="${value:.2f}", title="Average Tips"
            )
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Total Bill ($)",
                    components=[
                        vm.Graph(figure=px.histogram(tips, x="total_bill")),
                    ],
                ),
                vm.Container(
                    title="Total Tips ($)",
                    components=[
                        vm.Graph(figure=px.histogram(tips, x="tip")),
                    ],
                ),
            ],
        ),
    ],
    controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")],
)

third_page = vm.Page(
    title="Analysis",
    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Graph(
            title="Where do we get more tips?",
            figure=bar_mean(tips, y="tip", x="day"),
        ),
        vm.Graph(
            title="Is the average driven by a few outliers?",
            figure=px.violin(tips, y="tip", x="day", color="day", box=True),
        ),
        vm.Graph(
            title="Which group size is more profitable?",
            figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[first_page, second_page, third_page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
