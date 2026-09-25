"""Scratch app."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_sparkline_card

df = px.data.iris()
stocks = px.data.stocks()
SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}

kpi_sparkline_page = vm.Page(
    id="kpi-sparkline-cards",
    title="KPI sparkline cards",
    layout=vm.Grid(grid=[[0, 1, 2, 3], [4, 4, 5, 5], [4, 4, 5, 5], [4, 4, 5, 5]]),
    components=[
        vm.Figure(
            figure=kpi_sparkline_card(
                stocks,
                value_column="GOOG",
                x_column="date",
                title="Google",
                icon="trending_up",
                value_format="{value:.2f}",
                units="MWh",
            )
        ),
        vm.Figure(
            figure=kpi_sparkline_card(
                stocks,
                value_column="AAPL",
                x_column="date",
                title="Apple",
                chart_type="line",
                value_format="{value:.2f} ({delta_relative:+.1%})",
            )
        ),
        vm.Figure(
            figure=kpi_sparkline_card(
                stocks,
                value_column="MSFT",
                x_column="date",
                title="Microsoft",
                reverse_color=True,
                value_format="{value:.2f}",
            )
        ),
        vm.Figure(
            figure=kpi_sparkline_card(
                stocks,
                value_column="FB",
                x_column="date",
                title="Meta",
                icon="show_chart",
                agg_func="mean",
                value_format="${value:.2f}",
            )
        ),
        vm.Graph(
            figure=px.line(
                stocks,
                x="date",
                y=["GOOG", "AAPL", "AMZN"],
                title="Stock Prices Over Time",
                labels={"date": "Date", "value": "Price", "variable": "Company"},
            )
        ),
        vm.Graph(
            figure=px.scatter(
                stocks,
                x="AAPL",
                y="MSFT",
                title="Apple vs Microsoft Stock Prices",
                labels={"AAPL": "Apple", "MSFT": "Microsoft"},
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[kpi_sparkline_page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
