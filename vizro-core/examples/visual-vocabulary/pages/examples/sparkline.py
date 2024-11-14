import plotly.express as px
from vizro.models.types import capture

stocks = px.data.stocks()
stocks_melt = stocks.melt(id_vars="date", value_vars=["GOOG", "AMZN", "AAPL"], var_name="stock", value_name="value")


@capture("graph")
def sparkline(data_frame, **kwargs):
    fig = px.line(data_frame, **kwargs)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(showlegend=False)
    return fig


fig = sparkline(stocks_melt, x="date", y="value", facet_row="stock", color="stock")
