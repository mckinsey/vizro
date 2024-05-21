"""Dev app to try things out."""

import numpy as np
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_data_table
from vizro.models.types import capture
import pandas as pd
import plotly.graph_objects as go

from typing import Optional

iris_df = px.data.iris()

@capture("graph")
def plt_kpi_card(
    column: str,
    data_frame: pd.DataFrame = None,
    title: Optional[str] = None,
    align: str = "left",
):
    """Custom KPI card."""
    # Do any data aggregation here
    value = data_frame[column].mean()

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=value,
            number={"font": {"size": 32}},
            title={"text": f"<br><span style='font-size:1rem;'>{title}</span><br>", "align": align},
            align=align,
        )
    )
    return fig



page = vm.Page(
    title="Table Page",
    components=[
        vm.Graph(
            id="kpi-total",
            figure=plt_kpi_card(
                data_frame=iris_df,
                column="sepal_width",
                title="Sepal Width AVG",
            ),
        ),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
