"""Example app to show all features of Vizro."""

from time import sleep
from typing import List, Literal, Optional

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import dash_table, html
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table

iris = px.data.iris()
gapminder = px.data.gapminder()
tips = px.data.tips()
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
    title="Homepage",
    layout=vm.Layout(grid=[[0, 1], [2, 3]], row_gap="16px", col_gap="24px"),
    components=[
        vm.Card(
            text="""
                ![](assets/images/icons/line-chart.svg#icon-top)

                ### Components

                Main components of Vizro include **charts**, **tables**, **cards**, **containers**,
                **buttons** and **tabs**.
                """,
            href="/graphs",
        ),
        vm.Card(
            text="""
                ![](assets/images/icons/filters.svg#icon-top)

                ### Controls

                Vizro has two different control types **Filter** and **Parameter**.

                You can use any pre-existing selector inside the **Filter** or **Parameter**:

                * Dropdown
                * Checklist
                * RadioItems
                * RangeSlider
                * Slider
                """,
            href="/filters",
        ),
        vm.Card(
            text="""
                ![](assets/images/icons/download.svg#icon-top)

                ### Actions

                Standard predefined actions are made available including **export data** and **filter interactions**.
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
                iris,
                dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"],
                color="species",
            )
        )
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)

ag_grid = vm.Page(
    title="AG Grid",
    components=[
        vm.AgGrid(
            title="Dash AG Grid",
            figure=dash_ag_grid(data_frame=gapminder_2007),
        )
    ],
    controls=[vm.Filter(column="continent")],
)

table = vm.Page(
    title="Table",
    components=[
        vm.Table(
            title="Dash DataTable",
            figure=dash_data_table(data_frame=gapminder_2007),
        )
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
            """
        ),
        vm.Card(
            text="""
                 ### Paragraphs
                 Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                 Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                 Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                 Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.
            """
        ),
        vm.Card(
            text="""
                ### Block Quotes

                >
                > A block quote is a long quotation, indented to create a separate block of text.
                >
            """
        ),
        vm.Card(
            text="""
                ### Lists

                * Item A
                    * Sub Item 1
                    * Sub Item 2
                * Item B
            """
        ),
        vm.Card(
            text="""
                ### Emphasis

                This word will be *italic*

                This word will be **bold**

                This word will be _**bold and italic**_
            """
        ),
    ],
)

button = vm.Page(
    title="Button",
    layout=vm.Layout(grid=[[0], [0], [0], [0], [1]]),
    components=[
        vm.Graph(
            figure=px.scatter(
                iris,
                x="sepal_width",
                y="sepal_length",
                color="species",
                size="petal_length",
            ),
        ),
        vm.Button(text="Export data", actions=[vm.Action(function=export_data())]),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)

containers = vm.Page(
    title="Containers",
    components=[
        vm.Container(
            title="Container I",
            layout=vm.Layout(grid=[[0, 1]]),
            components=[
                vm.Graph(
                    figure=px.scatter(
                        iris,
                        x="sepal_length",
                        y="petal_width",
                        color="species",
                        title="Container I - Scatter",
                    )
                ),
                vm.Graph(
                    figure=px.bar(
                        iris,
                        x="sepal_length",
                        y="sepal_width",
                        color="species",
                        title="Container I - Bar",
                    )
                ),
            ],
        ),
        vm.Container(
            title="Container II",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        iris,
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        marginal_y="violin",
                        marginal_x="box",
                        title="Container II - Scatter",
                    )
                )
            ],
        ),
    ],
)

tab_1 = vm.Container(
    title="Tab I",
    components=[
        vm.Graph(
            figure=px.bar(
                gapminder_2007,
                title="Graph 1",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Graph(
            figure=px.box(
                gapminder_2007,
                title="Graph 2",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
    ],
)

tab_2 = vm.Container(
    title="Tab II",
    components=[
        vm.Graph(
            figure=px.scatter(
                gapminder_2007,
                title="Graph 3",
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
    ],
)

tabs = vm.Page(title="Tabs", components=[vm.Tabs(tabs=[tab_1, tab_2])], controls=[vm.Filter(column="continent")])

# CONTROLS --------------------------------------------------------------------
filters = vm.Page(
    title="Filters",
    components=[
        vm.Graph(
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
            )
        ),
        vm.Graph(
            id="scatter_chart2",
            figure=px.scatter(
                iris,
                x="petal_length",
                y="sepal_width",
                color="species",
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species"),
        vm.Filter(
            column="petal_length",
            targets=["scatter_chart2"],
            selector=vm.RangeSlider(),
        ),
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
            selector=vm.Dropdown(options=["#ff5267", "#3949ab"], multi=False, value="#3949ab"),
        )
    ],
)

selectors = vm.Page(
    title="Selectors",
    layout=vm.Layout(grid=[[0], [1], [1], [1], [2], [2], [2]], row_min_height="170px", row_gap="24px"),
    components=[
        vm.Card(
            text="""
        A selector can be used within the **Parameter** or **Filter** component to allow the user to select a value.

        The following selectors are available:
        * Dropdown (**categorical** multi and single option selector)
        * Checklist (**categorical** multi option selector only)
        * RadioItems (**categorical** single option selector only)
        * RangeSlider (**numerical** multi option selector only)
        * Slider (**numerical** single option selector only)

        """
        ),
        vm.Table(
            id="table-gapminder", figure=dash_data_table(data_frame=gapminder, page_size=10), title="Gapminder Data"
        ),
        vm.Table(id="table-tips", figure=dash_data_table(data_frame=tips, page_size=10), title="Tips Data"),
    ],
    controls=[
        vm.Filter(
            targets=["table-gapminder"],
            column="year",
            selector=vm.RangeSlider(title="Range Slider (Gapminder - year)", step=1, marks=None),
        ),
        vm.Filter(
            targets=["table-gapminder"],
            column="continent",
            selector=vm.Checklist(title="Checklist (Gapminder - continent)"),
        ),
        vm.Filter(
            targets=["table-gapminder"],
            column="country",
            selector=vm.Dropdown(title="Dropdown (Gapminder - country)"),
        ),
        vm.Filter(
            targets=["table-tips"],
            column="day",
            selector=vm.Dropdown(title="Dropdown (Tips - day)", multi=False, value="Sat"),
        ),
        vm.Filter(
            targets=["table-tips"],
            column="sex",
            selector=vm.RadioItems(title="Radio Items (Tips - sex)"),
        ),
        vm.Filter(
            targets=["table-tips"],
            column="size",
            selector=vm.Slider(title="Slider (Tips - size)", step=1, value=2),
        ),
    ],
)

# ACTIONS ---------------------------------------------------------------------
export_data_action = vm.Page(
    title="Export data",
    components=[
        vm.Graph(figure=px.scatter(iris, x="petal_length", y="sepal_length", color="species")),
        vm.Graph(figure=px.histogram(iris, x="petal_length", color="species")),
        vm.Button(text="Export data", actions=[vm.Action(function=export_data())]),
    ],
    controls=[vm.Filter(column="species")],
)


chart_interaction = vm.Page(
    title="Chart interaction",
    components=[
        vm.Graph(
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
def waterfall(data_frame, measure, x, y, text, title=None):  # noqa: PLR0913
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
        )
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
                data_frame=waterfall_df,
                measure="measure",
                x="x",
                y="y",
                text="text",
                title="Custom go chart",
            ),
        ),
    ],
    controls=[
        vm.Filter(column="petal_width", targets=["custom_scatter"]),
        vm.Filter(
            column="x",
            targets=["custom_waterfall"],
            selector=vm.Dropdown(title="Financial categories", multi=True),
        ),
    ],
)


# CUSTOM TABLE ------------------------------------------------------------------
@capture("table")
def my_custom_table(data_frame=None, chosen_columns: Optional[List[str]] = None):
    """Custom table with added logic to filter on chosen columns."""
    columns = [{"name": i, "id": i} for i in chosen_columns]
    defaults = {
        "style_as_list_view": True,
        "style_data": {"border_bottom": "1px solid var(--border-subtle-alpha-01)", "height": "40px"},
        "style_header": {
            "border_bottom": "1px solid var(--state-overlays-selected-hover)",
            "border_top": "1px solid var(--main-container-bg-color)",
            "height": "32px",
        },
    }
    return dash_table.DataTable(data=data_frame.to_dict("records"), columns=columns, **defaults)


custom_tables = vm.Page(
    title="Custom Tables",
    components=[
        vm.Table(
            id="custom_table",
            title="Custom Dash DataTable",
            figure=my_custom_table(
                data_frame=gapminder_2007,
                chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"],
            ),
        )
    ],
    controls=[
        vm.Parameter(
            targets=["custom_table.chosen_columns"],
            selector=vm.Dropdown(
                title="Choose columns",
                options=gapminder_2007.columns.to_list(),
                multi=True,
            ),
        )
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
        return html.Div([html.H2(self.title), html.H3(self.subtitle), html.P(self.text)])


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
            figure=px.scatter(
                iris,
                title="Iris Dataset",
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
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


# CUSTOM ACTIONS ---------------------------------------------------------------
@capture("action")
def my_custom_action(t: int):
    """Custom action."""
    sleep(t)


custom_actions = vm.Page(
    title="Custom Actions",
    components=[
        vm.Graph(
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
            )
        ),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(function=export_data()),
                vm.Action(function=my_custom_action(t=2)),
                vm.Action(function=export_data(file_format="xlsx")),
            ],
        ),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)

# DASHBOARD -------------------------------------------------------------------
components = [graphs, ag_grid, table, cards, button, containers, tabs]
controls = [filters, parameters, selectors]
actions = [export_data_action, chart_interaction]
extensions = [custom_charts, custom_tables, custom_components, custom_actions]

dashboard = vm.Dashboard(
    title="Vizro Features",
    pages=[home, *components, *controls, *actions, *extensions],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Homepage", pages=["Homepage"], icon="Home"),
                vm.NavLink(
                    label="Features",
                    pages={
                        "Components": ["Graphs", "AG Grid", "Table", "Cards", "Button", "Containers", "Tabs"],
                        "Controls": ["Filters", "Parameters", "Selectors"],
                        "Actions": ["Export data", "Chart interaction"],
                        "Extensions": ["Custom Charts", "Custom Tables", "Custom Components", "Custom Actions"],
                    },
                    icon="Library Add",
                ),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
