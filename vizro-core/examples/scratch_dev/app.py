"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


iris = px.data.iris()

page = vm.Page(
    title="Fix empty dropdown as parameter",
    components=[vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"))],
    controls=[vm.Filter(column="species")],
)
page_2 = vm.Page(
    title="Test",
    components=[vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"))],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(
    pages=[page, page_2],
    # title=vm.Title(
    #     text="Test dev dashboard with icon",
    #     tooltip="""
    #
    #         ### Tooltip title
    #
    #         #### Lorem ipsum
    #
    #         "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    #     """,
    # ),
    title="This is a plain title"
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
