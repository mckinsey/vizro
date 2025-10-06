"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from vizro import Vizro

SELECTED_COUNTRIES = [
    "Singapore",
    "Malaysia",
    "Thailand",
    "Indonesia",
    "Philippines",
    "Vietnam",
    "Cambodia",
    "Myanmar",
    "NONE",  # (1)!
]

gapminder = px.data.gapminder().query("country.isin(@SELECTED_COUNTRIES)")


@capture("graph")
def bump_chart(data_frame, highlight_country=None):  # (1)!
    data_with_rank = data_frame.copy()
    data_with_rank["rank"] = data_frame.groupby("year")["lifeExp"].rank(method="dense", ascending=False)

    fig = px.line(data_with_rank, x="year", y="rank", color="country", markers=True)  # (2)!
    fig.update_layout(
        legend_title="",
        xaxis_title="",
        yaxis=dict(autorange="reversed"),
        yaxis_title="Rank (1 = Highest lifeExp)",
    )

    fig.update_traces(opacity=0.3, line=dict(width=2))  # (3)!

    if highlight_country:  # (4)!
        for trace in fig.data:
            if trace.name == highlight_country:
                trace.opacity = 1.0
                trace.line.width = 3

    return fig


@capture("graph")
def bar_chart(data_frame):
    fig = px.bar(data_frame[data_frame["year"] == 2007], y="country", x="lifeExp")
    fig.update_layout(yaxis_title="", xaxis_title="lifeExp (2007)")
    return fig


page = vm.Page(
    title="Cross-highlighting example",
    components=[
        vm.Graph(
            figure=bar_chart(data_frame=gapminder),
            header="💡 Click any bar to highlight that country in the bump chart",
            actions=[va.set_control(control="highlight_parameter", value="y")],  # (5)!
        ),
        vm.Graph(
            id="bump_chart",  # (6)!
            figure=bump_chart(data_frame=gapminder),
        ),
    ],
    controls=[
        vm.Parameter(
            id="highlight_parameter",  # (7)!
            targets=["bump_chart.highlight_country"],  # (8)!
            selector=vm.Dropdown(multi=False, options=SELECTED_COUNTRIES, value="NONE"),  # (9)!
            visible=False,  # (10)!
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
