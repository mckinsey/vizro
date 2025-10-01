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
    "NONE"
]

gapminder = px.data.gapminder().query("country.isin(@SELECTED_COUNTRIES)")


@capture("graph")
def bump_chart(data_frame, highlight_country=None):
    data_with_rank = data_frame.copy()
    data_with_rank['rank'] = data_frame.groupby('year')['lifeExp'].rank(
        method='dense', ascending=False
    )
    
    fig = px.line(
        data_with_rank,
        x="year",
        y="rank",
        color="country",
        markers=True,
    )
    
    fig.update_layout(
        legend_title="",
        xaxis_title="",
        yaxis=dict(autorange="reversed"),
        yaxis_title="Rank (1 = Highest lifeExp)",
    )
    
    if highlight_country:
        for trace in fig.data:
            if trace.name == highlight_country:
                trace.opacity = 1.0
                trace.line.width = 3
            else:
                trace.opacity = 0.3
                trace.line.width = 2
    
    return fig


@capture("graph")
def bar_chart(data_frame):
    fig = px.bar(
        data_frame[data_frame["year"] == 2007],
        y="country", 
        x="lifeExp",
    )
    fig.update_layout(yaxis_title="", xaxis_title="lifeExp (2007)")
    return fig


page = vm.Page(
    title="Cross-highlighting example",
    components=[
        vm.Graph(
            figure=bar_chart(data_frame=gapminder),
            header="💡 Click on any bar to highlight that country's trace in the bump chart",
            actions=[va.set_control(control="highlight_parameter", value="y")],
        ),
        vm.Graph(id="bump_chart", figure=bump_chart(data_frame=gapminder)),
    ],
    controls=[
        vm.Parameter(
            id="highlight_parameter",
            targets=["bump_chart.highlight_country"],
            selector=vm.Dropdown(multi=False, options=SELECTED_COUNTRIES, value="NONE"),
            visible=False,
        ),
    ]
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()