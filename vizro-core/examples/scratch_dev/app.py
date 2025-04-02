# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.
import textwrap

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="Page with lots of extra information",
    # You could also do this with vm.Tooltip(text=...)
    description="""
        At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat


        # something something
        * asdfasdf

        [link](www.google.com)
        """,
    components=[
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                description="""
                    Select which species of iris you like.

                    [Click here](www.google.com) to learn more about flowers.""",
                # You could also do this with vm.Tooltip(text=...)
            ),
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[page],
    title="blah blah blah",
    # Specify a different icon:
    description=vm.Tooltip(text="Hello hello", icon="Help"),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
