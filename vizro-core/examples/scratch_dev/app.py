# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.
import textwrap

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="Vizro on PyCafe",
    layout=vm.Layout(grid=[[0, 1], [2, 2], [2, 2], [3, 3], [3, 3]], row_min_height="140px"),
    components=[
        vm.Card(
            text="""
                ### What is Vizro?
                An open-source toolkit for creating modular data visualization applications.

                Rapidly self-serve the assembly of customized dashboards in minutes - without the need for advanced coding or design experience - to create flexible and scalable, Python-enabled data visualization applications."""
        ),
        vm.Card(
            text="""
                ### Github

                Checkout Vizro's GitHub page for further information and release notes. Contributions are always 
                welcome!  [Click here](www.google.com) to learn more about flowers.""",
        ),
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                description=vm.Tooltip(
                    text="""
                    Select which species of iris you like.
                    
                    [Click here](www.google.com) to learn more about flowers.""",
                )
            ),
        ),
        vm.Filter(column="petal_length"),
        vm.Filter(column="sepal_width"),
    ],
    description=vm.Tooltip(
        text="""

    At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat


    # something something
    * asdfasdf

    [link](www.google.com)
    """
    ),
)

dashboard = vm.Dashboard(pages=[page], title="blah blah blah", description=vm.Tooltip(text="Hello hello", icon="Help"))

if __name__ == "__main__":
    Vizro().build(dashboard).run()
