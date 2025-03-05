"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


iris = px.data.iris()

page = vm.Page(
    title="Fix empty dropdown as parameter",
    components=[vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"))],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(
    pages=[page],
    title=vm.Title(
        title="Test dev dashboard with icon",
        icon=True,
        tooltip_text="""

            # Tooltip title <h1> tag

            ## Lorem ipsum <h2> tag

            ###### "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum." <h6> tag
        """,
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
