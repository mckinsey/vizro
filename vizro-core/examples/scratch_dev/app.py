from vizro import Vizro
import vizro.models as vm
import pandas as pd
import vizro.plotly.express as px

from vizro.figures import kpi_card, kpi_card_reference

iris = px.data.iris()
tips = px.data.tips()
gapminder = px.data.gapminder()
gapminder_europe = gapminder[gapminder["continent"] == "Europe"]


df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})
df_bar = pd.DataFrame(
    {
        "Actual": [100, 200, 700, 100, 300, 500, 400, 900, 800, 300, 400, 700],
        "Category": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"],
    }
)
graphs = vm.Page(
    title="Graphs",
    components=[
        vm.Graph(figure=px.pie(iris, names="species")),
        vm.Graph(figure=px.bar(gapminder_europe, x="country", y="lifeExp")),
    ],
)
graph = [
    vm.Graph(
        figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
        title="Relationships between Sepal Width and Sepal Length",
        header="""
                Each point in the scatter plot represents one of the 150 iris flowers, with colors indicating their
                types. The Setosa type is easily identifiable by its short and wide sepals.

                However, there is still overlap between the Versicolor and Virginica types when considering only sepal
                width and length.
                """,
        footer="""SOURCE: **Plotly iris data set, 2024**""",
    )
]

cards = vm.Page(
    title="Cards",
    components=[
        vm.Card(
            text="""
                Each point in the scatter plot represents one of the 150 iris flowers, with colors indicating their
                types. The Setosa type is easily identifiable by its short and wide sepals.

                However, there is still overlap between the Versicolor and Virginica types when considering only sepal
                width and length.
                """,
        ),
    ],
)
example_cards = [
    kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value"),
    kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with aggregation", agg_func="median"),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI with formatting",
        value_format="${value:.2f}",
    ),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI with icon",
        icon="shopping_cart",
    ),
]

example_reference_cards = [
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI reference (pos)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        agg_func="median",
        title="KPI reference (neg)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI reference with formatting",
        value_format="{value:.2f}€",
        reference_format="{delta:+.2f}€ vs. last year ({reference:.2f}€)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI reference with icon",
        icon="shopping_cart",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI reference (reverse color)",
        reverse_color=True,
    ),
]
components = [vm.Figure(figure=figure) for figure in example_cards + example_reference_cards]

components.extend(graph)

kpi_cards = vm.Page(
    title="KPI cards",
    # layout=vm.Flex(direction="row", wrap=True),
    layout=vm.Grid(grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 9, 9], [9, 9, 9], [9, 9, 9]]),
    # layout=vm.Grid(grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8]]),
    components=components,
)

tooltip = vm.Page(
    title="Tooltip",
    layout=vm.Grid(grid=[[0], [0], [1], [1], [1], [1], [1], [1], [2]]),
    components=[
        vm.Card(
            text="""
                The `description` argument enables you to add helpful context to your components by displaying an
                info icon next to its title. Hovering over the icon reveals a tooltip with the text you provide.

                Tooltips can be added to any Vizro component that has a `title` argument.
                You can provide a string to use the default info icon or `Tooltip` model to use any icon from the
                [Google Material Icons library](https://fonts.google.com/icons).
                Tooltips provide clean and lightweight way to add additional details to your dashboard.
            """
        ),
        vm.Graph(
            title="Relationships between Sepal Width and Sepal Length",
            figure=px.scatter(
                iris,
                x="sepal_width",
                y="sepal_length",
                color="species",
                size="petal_length",
            ),
            description="""
                **The Iris dataset** includes measurements of 150 iris flowers across three types: Setosa, Versicolor,
                and Virginica.
                While all samples are labeled by type, they can appear similar when looking at just some features -
                 making it a useful dataset for exploring patterns and challenges in classification.
            """,
        ),
        vm.Button(
            text="Export data",
            description="""
                Use this button to export the filtered data from the Iris dataset.
            """,
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                title="Species",
                description="""
                    Select one or more species to explore patterns
                    specific to Setosa, Versicolor, or Virginica.
                """,
            ),
        ),
    ],
    description="""
        This page provides overview of Tooltip functionality.
    """,
)

navigation = vm.Navigation(
    pages={"Group A": ["Graphs", "Cards"], "Group B": ["Tooltip", "KPI cards"]}, nav_selector=vm.NavBar()
)


dashboard = vm.Dashboard(
    pages=[graphs, cards, tooltip, kpi_cards],
    navigation=navigation,
    title="Scratch dev dashboard",
)

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
