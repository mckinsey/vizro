import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.tables import dash_data_table

iris = px.data.iris()
gapminder_2007 = px.data.gapminder().query("year == 2007")

# HOME ------------------------------------------------------------------------
home = vm.Page(
    title="Vizro Features",
    layout=vm.Layout(grid=[[0, 1], [2, 3]], row_gap="16px", col_gap="24px"),
    components=[
        vm.Card(
            text="""
                ![](assets/images/icons/line-chart.svg#icon-top)

                ### Components

                Main components of vizro include **charts**, **tables**, **cards** and **buttons**.
                """,
            href="/graphs",
        ),
        vm.Card(
            text="""
                ![](assets/images/icons/filters.svg#icon-top)

                ### Controls

                Vizro has two different control types **filters** and **parameters**.

                """,
            href="/filters",
        ),
        vm.Card(
            text="""
                ![](assets/images/icons/download.svg#icon-top)

                ### Actions

                Standard predefined actions are made available including **export data** and **filer interactions**.
                """,
            href="/export-data",
        ),
        vm.Card(
            text="""
                ![](assets/images/icons/use-case.svg#icon-top)

                ### Extensions

                Vizro enables customization of **plotly express** and **graph object charts** as well as
                creating custom components based on Dash.
            """,
            href="/custom-chart",
        ),
    ],
)

# COMPONENTS ------------------------------------------------------------------
graphs = vm.Page(
    title="Graphs",
    components=[
        vm.Graph(
            figure=px.scatter_matrix(
                iris, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"], color="species"
            ),
        ),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)

table = vm.Page(
    title="Table",
    components=[
        vm.Table(title="Dash DataTable", figure=dash_data_table(data_frame=gapminder_2007)),
    ],
    controls=[vm.Filter(column="continent")],
)

cards = vm.Page(
    title="Cards",
    components=[
        vm.Card(
            text="""
                # Header level 1 <h1>

                ## Header level 2 <h2>

                ### Header level 3 <h3>

                #### Header level 4 <h4>
            """,
        ),
        vm.Card(
            text="""
                 ### Paragraphs
                 Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                 Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                 Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                 Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.
            """,
        ),
        vm.Card(
            text="""
                ### Block Quotes

                >
                > A block quote is a long quotation, indented to create a separate block of text.
                >
            """,
        ),
        vm.Card(
            text="""
                ### Lists

                * Item A
                    * Sub Item 1
                    * Sub Item 2
                * Item B
            """,
        ),
        vm.Card(
            text="""
                ### Emphasis

                This word will be *italic*

                This word will be **bold**

                This word will be _**bold and italic**_
            """,
        ),
    ],
)

button = vm.Page(
    title="Button",
    layout=vm.Layout(grid=[[0], [0], [0], [0], [1]]),
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(
                iris,
                x="sepal_width",
                y="sepal_length",
                color="species",
                size="petal_length",
            ),
        ),
        vm.Button(
            text="Export data",
            actions=[vm.Action(function=export_data(targets=["scatter_chart"]))],
        ),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)

# CONTROLS --------------------------------------------------------------------
filters = vm.Page(
    title="Filters",
    components=[
        vm.Graph(id="scatter_chart1", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="scatter_chart2", figure=px.scatter(iris, x="petal_length", y="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
        vm.Filter(column="petal_length", targets=["scatter_chart2"], selector=vm.RangeSlider()),
    ],
)


components = [graphs, table, cards, button]
controls = [filters]

dashboard = vm.Dashboard(
    pages=[home] + components + controls,
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Homepage", pages=["Vizro Features"], icon="Home"),
                vm.NavLink(
                    label="Features",
                    pages={
                        "Components": ["Graphs", "Table", "Cards", "Button"],
                        "Controls": ["Filters"],
                        #  "Actions": ["Export data", "Filter interaction"],
                        #   "Extensions": ["Custom plotly chart", "Custom graph object chart", "Custom range slider", "Custom jumbotron",],
                    },
                    icon="Library Add",
                ),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run(port=8052)
