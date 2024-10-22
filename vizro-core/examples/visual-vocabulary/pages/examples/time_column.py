import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

gapminder = px.data.gapminder()


@capture("graph")
def categorical_column(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    """Creates a column chart where the x-axis values are converted to category type."""
    fig = px.bar(data_frame, **kwargs)
    # So ticks are aligned with bars when xaxes values are numbers (e.g. years)
    fig.update_xaxes(type="category")
    return fig


page = vm.Page(
    title="Column",
    components=[
        vm.Graph(
            figure=categorical_column(
                gapminder.query("country == 'Nigeria' and year > 1970"),
                x="year",
                y="lifeExp",
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
