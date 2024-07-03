"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

df_stocks = px.data.stocks(datetimes=True)
df_stocks_long = pd.melt(
    df_stocks,
    id_vars="date",
    value_vars=["GOOG", "AAPL", "AMZN", "FB", "NFLX", "MSFT"],
    var_name="stocks",
    value_name="value",
)


@capture("graph")
def vizro_plot(data_frame, stocks_selected, **kwargs):
    """Custom chart function."""
    return px.line(data_frame[data_frame["stocks"].isin(stocks_selected)], **kwargs)


df_stocks_long["value"] = df_stocks_long["value"].round(3)

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(
            id="my_graph",
            figure=vizro_plot(
                data_frame=df_stocks_long,
                stocks_selected=list(df_stocks_long["stocks"].unique()),
                x="date",
                y="value",
                color="stocks",
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["my_graph.stocks_selected"],
            selector=vm.Dropdown(
                options=[{"label": s, "value": s} for s in df_stocks_long["stocks"].unique()],
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
