"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
from dash import html
from vizro import Vizro
from vizro.models.types import capture

df = pd.DataFrame({"names": ["Emma", "Jack", "Sophia", "Ethan", "Mia"]})


@capture("figure")
def dynamic_html_header(data_frame: pd.DataFrame, column: str) -> html.H2:
    """Creates a HTML header that dynamically updates based on controls."""
    return html.H2(f"Good morning, {data_frame[column].iloc[0]}! ☕ ⛅")


page = vm.Page(
    title="Dynamic HTML header",
    components=[vm.Figure(figure=dynamic_html_header(data_frame=df, column="names"))],
    controls=[vm.Filter(column="names", selector=vm.RadioItems(title="Select a name"))],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
