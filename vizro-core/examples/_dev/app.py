"""Example to show dashboard configuration."""

from typing import Optional

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture


page = vm.Page(
    title="Autocolorscale",
    components=[
vm.Card(
            text="""
                # This is an <h1> tag
                ## This is an <h2> tag
                ###### This is an <h6> tag
                \n
                >
                > Block quotes are used to highlight text.
                >
                \n
                * Item 1
                * Item 2
                \n
                 *This text will be italic*
                _This will also be italic_
                **This text will be bold**
                _You **can** combine them_
            """,
        ),
    ],
)
dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
