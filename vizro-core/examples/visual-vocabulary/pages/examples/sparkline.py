import plotly.express as px
from vizro.models.types import capture

stocks = px.data.stocks()


@capture("graph")
def sparkline(data_frame, **kwargs):
    fig = px.line(data_frame, **kwargs)
    fig.update_xaxes(ticks="", showgrid=False, title="")
    fig.update_yaxes(visible=False)
    fig.update_layout(showlegend=False)
    return fig


fig = sparkline(stocks, x="date", y=["GOOG", "AMZN", "AAPL"], labels={"variable": "stock"}, facet_row="variable")
