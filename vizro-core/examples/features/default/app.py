"""Example app to show all features of Vizro."""
from typing import Literal

import pandas as pd
import plotly.graph_objects as go
from dash import html

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.models.types import capture
from vizro.tables import dash_data_table

iris = px.data.iris()
gapminder_2007 = px.data.gapminder().query("year == 2007")
waterfall_df = pd.DataFrame(
    {
        "measure": ["relative", "relative", "total", "relative", "relative", "total"],
        "x": ["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"],
        "text": ["+60", "+80", "", "-40", "-20", "Total"],
        "y": [60, 80, 0, -40, -20, 0],
    }
)

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
            href="/custom-charts",
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

parameters = vm.Page(
    title="Parameters",
    components=[
        vm.Graph(
            id="scatter_chart_pm",
            figure=px.scatter(
                iris,
                x="sepal_width",
                y="sepal_length",
                color="species",
                size="petal_length",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
            ),
        ),
        vm.Graph(
            id="bar_chart_pm",
            figure=px.bar(
                iris,
                x="sepal_width",
                y="sepal_length",
                color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["scatter_chart_pm.color_discrete_map.virginica", "bar_chart_pm.color_discrete_map.virginica"],
            selector=vm.Dropdown(
                options=["#ff5267", "#3949ab"],
                multi=False,
                value="#3949ab",
            ),
        ),
    ],
)

# ACTIONS ---------------------------------------------------------------------
export_data = vm.Page(
    title="Export data",
    components=[
        vm.Graph(
            id="scatter_export_data",
            figure=px.scatter(iris, x="petal_length", y="sepal_length", color="species"),
        ),
        vm.Graph(
            id="hist_export_data",
            figure=px.histogram(iris, x="petal_length", color="species"),
        ),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(function=export_data()),
            ],
        ),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)


chart_interaction = vm.Page(
    title="Chart interaction",
    components=[
        vm.Graph(
            id="bar_relation_2007",
            figure=px.box(
                gapminder_2007,
                x="continent",
                y="lifeExp",
                color="continent",
                custom_data=["continent"],
            ),
            actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],
        ),
        vm.Graph(
            id="scatter_relation_2007",
            figure=px.scatter(
                gapminder_2007,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
    ],
)


# CUSTOM CHARTS ------------------------------------------------------------------
@capture("graph")
def scatter_with_line(data_frame, x, y, hline=None, title=None):
    """Custom scatter chart based on px."""
    fig = px.scatter(data_frame=data_frame, x=x, y=y, title=title)
    fig.add_hline(y=hline, line_color="orange")
    return fig


@capture("graph")
def waterfall(data_frame, measure, x, y, text, title=None):
    """Custom waterfall chart based on go."""
    fig = go.Figure()
    fig.add_traces(
        go.Waterfall(
            measure=data_frame[measure],
            x=data_frame[x],
            y=data_frame[y],
            text=data_frame[text],
            decreasing={"marker": {"color": "#ff5267"}},
            increasing={"marker": {"color": "#08bdba"}},
            totals={"marker": {"color": "#00b4ff"}},
        ),
    )
    fig.update_layout(title=title)
    return fig


custom_charts = vm.Page(
    title="Custom Charts",
    components=[
        vm.Graph(
            id="custom_scatter",
            figure=scatter_with_line(
                x="sepal_length",
                y="sepal_width",
                hline=3.5,
                data_frame=iris,
                title="Custom px chart",
            ),
        ),
        vm.Graph(
            id="custom_waterfall",
            figure=waterfall(
                data_frame=waterfall_df, measure="measure", x="x", y="y", text="text", title="Custom go chart"
            ),
        ),
    ],
    controls=[
        vm.Filter(column="petal_width", targets=["custom_scatter"]),
        vm.Filter(
            column="x", targets=["custom_waterfall"], selector=vm.Dropdown(title="Financial categories", multi=True)
        ),
    ],
)


# CUSTOM COMPONENTS -------------------------------------------------------------
# 1. Extend existing components
class TooltipNonCrossRangeSlider(vm.RangeSlider):
    """Custom numeric multi-selector `TooltipNonCrossRangeSlider`."""

    type: Literal["other_range_slider"] = "other_range_slider"

    def build(self):
        """Extend existing component by calling the super build and update properties."""
        range_slider_build_obj = super().build()
        range_slider_build_obj[self.id].allowCross = False
        range_slider_build_obj[self.id].tooltip = {"always_visible": True, "placement": "bottom"}
        return range_slider_build_obj


vm.Filter.add_type("selector", TooltipNonCrossRangeSlider)


# 2. Create new custom component
class Jumbotron(vm.VizroBaseModel):
    """New custom component `Jumbotron`."""

    type: Literal["jumbotron"] = "jumbotron"
    title: str
    subtitle: str
    text: str

    def build(self):
        """Build the new component based on Dash components."""
        return html.Div(
            [
                html.H2(self.title),
                html.H3(self.subtitle),
                html.P(self.text),
            ]
        )


vm.Page.add_type("components", Jumbotron)

custom_components = vm.Page(
    title="Custom Components",
    components=[
        Jumbotron(
            title="Custom component based on new creation",
            subtitle="This is a subtitle to summarize some content.",
            text="This is the main body of text of the Jumbotron.",
        ),
        vm.Graph(
            id="for_custom_chart",
            figure=px.scatter(iris, title="Iris Dataset", x="sepal_length", y="petal_width", color="sepal_width"),
        ),
    ],
    controls=[
        vm.Filter(
            column="sepal_length",
            targets=["for_custom_chart"],
            selector=TooltipNonCrossRangeSlider(title="Custom component based on extension"),
        )
    ],
)

# DASHBOARD -------------------------------------------------------------------
components = [graphs, table, cards, button]
controls = [filters, parameters]
actions = [export_data, chart_interaction]
extensions = [custom_charts, custom_components]

dashboard = vm.Dashboard(
    title="Vizro Features",
    pages=[home, *components, *controls, *actions, *extensions],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Homepage", pages=["Vizro Features"], icon="Home"),
                vm.NavLink(
                    label="Features",
                    pages={
                        "Components": ["Graphs", "Table", "Cards", "Button"],
                        "Controls": ["Filters", "Parameters"],
                        "Actions": ["Export data", "Chart interaction"],
                        "Extensions": ["Custom Charts", "Custom Components"],
                    },
                    icon="Library Add",
                ),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
