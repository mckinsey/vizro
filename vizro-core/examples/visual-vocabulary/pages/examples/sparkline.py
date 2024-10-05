import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

stocks = px.data.stocks()

def sparkline(df, x, y):
    fig=px.area(df, x, y, facet_row="variable", height=100)
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    return fig

page = vm.Page(
    title="Sparkline",
    components=[vm.Graph(figure=sparkline(stocks, x="date", y=["GOOG", "AMZN"]))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
