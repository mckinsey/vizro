import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.figures import kpi_sparkline_card

stocks_kpi_sparkline = px.data.stocks()
stocks_kpi_sparkline["year"] = stocks_kpi_sparkline["date"].str[:4]

kpi_sparkline_page = vm.Page(
    title=cnst.KPI_SPARKLINE_PAGE,
    layout=vm.Grid(grid=[[0, 1, 2], [3, -1, -1]]),
    components=[
        vm.Figure(
            id=cnst.KPI_SPARKLINE_GOOG_CARD_ID,
            figure=kpi_sparkline_card(
                stocks_kpi_sparkline,
                value_column="GOOG",
                x_column="date",
                title="Google",
                icon="trending_up",
                value_format="{value:.2f}",
            ),
        ),
        vm.Figure(
            figure=kpi_sparkline_card(
                stocks_kpi_sparkline,
                value_column="AAPL",
                x_column="date",
                title="Apple",
                chart_type="line",
                value_format="{value:.2f} ({delta_relative:+.1%})",
            )
        ),
        vm.Figure(
            figure=kpi_sparkline_card(
                stocks_kpi_sparkline,
                value_column="MSFT",
                x_column="date",
                title="Microsoft",
                reverse_color=True,
                value_format="{value:.2f}",
            )
        ),
        vm.Figure(
            figure=kpi_sparkline_card(
                stocks_kpi_sparkline,
                value_column="FB",
                x_column="date",
                title="Meta",
                icon="show_chart",
                agg_func="mean",
                value_format="${value:.2f}",
            )
        ),
    ],
    controls=[
        vm.Filter(
            id="kpi_sparkline_filter",
            column="year",
            selector=vm.Dropdown(id=cnst.DROPDOWN_FILTER_KPI_SPARKLINE_PAGE, multi=False),
        )
    ],
)
