"""Dev app to try things out."""

from typing import Optional

import dash_bootstrap_components as dbc
import pandas as pd
import vizro.models as vm
from dash import dcc, html
from vizro import Vizro
from vizro.models.types import capture

text = [
    "Lorem ipsum dolor sit amet, consetetur sadipscing no sea elitr sed diam nonumy.",
    "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
    "Sed diam voluptua. At vero eos et accusam et justo no duo dolores et ea rebum.",
    "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
    "Lorem ipsum dolor sit amet, consetetur sadipscing no sea est elitr dolor sit amet.",
    "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
]

df = pd.DataFrame({"text": text * 2})


@capture("figure")  # (1)!
def multiple_cards(data_frame: pd.DataFrame, n_rows: Optional[int] = 1) -> html.Div:  # (2)!
    """Creates a list with a variable number of `vm.Card` components from the provided data_frame.

    Args:
        data_frame: Data frame containing the data.
        n_rows: Number of rows to use from the data_frame. Defaults to 1.

    Returns:
        html.Div with a list of dbc.Card objects generated from the data.

    """
    texts = data_frame.head(n_rows)["text"]
    return html.Div(
        [dbc.Card(dcc.Markdown(f"### Card #{i}\n{text}")) for i, text in enumerate(texts, 1)],
        className="multiple-cards-container",
    )


page = vm.Page(
    title="Page with variable number of cards",
    components=[vm.Figure(id="my-figure", figure=multiple_cards(data_frame=df))],  # (3)!
    controls=[
        vm.Parameter(
            targets=["my-figure.n_rows"],  # (4)!
            selector=vm.Slider(min=2, max=12, step=2, value=8, title="Number of cards to display"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
