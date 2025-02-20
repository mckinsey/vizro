"""Test app"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.models.types import capture
from vizro.figures import kpi_card
from vizro.actions import export_data

tips = px.data.tips()


@capture("graph")
def bar_mean(data_frame, x, y):
    df_agg = data_frame.groupby(x).agg({y: "mean"}).reset_index()
    fig = px.bar(df_agg, x=x, y=y, labels={"tip": "Average Tip ($)"})
    fig.update_traces(width=0.6)
    return fig

page_data = vm.Page(
    title="Data",
    layout=vm.Layout(grid=[[0], [1], [1], [1], [2]]),
    components=[
        vm.Card(
            text="""

            ### Description
            One waiter recorded information about each tip he received over a period of a few months working in
            one restaurant. In all he recorded 244 tips. He collected several variables:

            * tip in dollars,
            * bill in dollars,
            * sex of the bill payer,
            * whether there were smokers in the party,
            * day of the week,
            * time of day,
            * size of the party.
        """
        ),
        vm.AgGrid(
            figure=dash_ag_grid(tips, columnSize="responsiveSizeToFit"),
            footer="""**Data Source:** Bryant, P. G. and Smith, M (1995) Practical Data Analysis: Case Studies in Business Statistics. Homewood, IL: Richard D. Irwin Publishing.""",
        ),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(function=export_data()),
            ],
        ),
    ],
)


page_charts = vm.Page(
    title="Summary",
    layout=vm.Layout(grid=[[0, 1, 2, 3]] + [[4, 4, 4, 4]] * 4),
    components=[
        vm.Figure(
            figure=kpi_card(data_frame=tips, value_column="total_bill", value_format="${value:.2f}", title="Total Bill")
        ),
        vm.Figure(
            figure=kpi_card(data_frame=tips, value_column="tip", value_format="${value:.2f}", title="Total Tips")
        ),
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
                        vm.Graph(figure=px.histogram(tips, x="total_bill", labels={"total_bill": "Total Bill ($)"})),
                    ],
                ),
                vm.Container(
                    title="Total Tips ($)",
                    components=[
                        vm.Graph(figure=px.histogram(tips, x="tip", labels={"tip": "Total Tips ($)"})),
                    ],
                ),
            ],
        ),
    ],
    controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")],
)

page_analysis = vm.Page(
    title="Analysis",
    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Graph(
            title="Where do we get more tips on average?",
            id="bar",
            figure=bar_mean(tips, y="tip", x="day"),
        ),
        vm.Graph(
            title="Is the average driven by a few outliers?",
            id="violin",
            figure=px.violin(tips, y="tip", x="day", color="day", box=True, labels={"tip": "Tip ($)"}),
        ),
        vm.Graph(
            id="heatmap",
            title="Which shift is more profitable?",
            figure=px.density_heatmap(tips, x="day", y="time", z="tip", histfunc="avg"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["violin.x", "violin.color", "heatmap.x", "bar.x"],
            selector=vm.RadioItems(
                options=["day", "time", "sex", "smoker", "size"], value="day", title="Change x-axis inside charts:"
            ),
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[page_data, page_charts, page_analysis],
    title="Analyzing tips",
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Data", pages=["Data"], icon="database"),
                vm.NavLink(label="Charts", pages=["Summary", "Analysis"], icon="bar_chart"),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
