from typing import Literal

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, callback_context, dcc, html

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.models.types import capture


def create_components_pages():
    df = px.data.iris()

    page_charts = vm.Page(
        title="Chart",
        path="component-chart",
        components=[
            vm.Graph(
                id="standard_chart",
                figure=px.scatter_matrix(
                    df, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"], color="species"
                ),
            ),
        ],
    )

    page_cards = vm.Page(
        title="Card",
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

    page_button = vm.Page(
        title="Button",
        layout=vm.Layout(grid=[[0], [0], [0], [0], [1]]),
        components=[
            vm.Graph(
                id="scatter_chart",
                figure=px.scatter(
                    df,
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
    )

    return [page_charts, page_cards, page_button]


def create_controls_pages():
    iris = px.data.iris()

    page_filter = vm.Page(
        title="Filter",
        path="controls-filter",
        components=[
            vm.Graph(
                id="scatter_chart_filter", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")
            ),
            vm.Graph(
                id="scatter_chart_filter_2", figure=px.scatter(iris, x="petal_length", y="sepal_width", color="species")
            ),
        ],
        controls=[
            vm.Filter(column="species"),
            vm.Filter(column="sepal_length", targets=["scatter_chart_filter"], selector=vm.RangeSlider(step=1)),
            vm.Filter(column="petal_length", targets=["scatter_chart_filter_2"], selector=vm.RangeSlider(step=1)),
        ],
    )

    page_parameter = vm.Page(
        title="Parameter",
        components=[
            vm.Graph(
                id="scatter_chart_param",
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
                id="bar_chart_param",
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
                targets=[
                    "scatter_chart_param.color_discrete_map.versicolor",
                    "bar_chart_param.color_discrete_map.versicolor",
                ],
                selector=vm.Dropdown(
                    options=["#D0F0C0", "#ff9222"],
                    multi=False,
                    value="#ff9222",
                ),
            ),
        ],
    )

    return [page_filter, page_parameter]


def create_actions_page():
    iris = px.data.iris()

    page_export_data = vm.Page(
        title="Export data",
        path="action-export-data",
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

    df_gapminder = px.data.gapminder().query("year == 2007")

    page_filter_interaction = vm.Page(
        title="Filter interaction",
        components=[
            vm.Graph(
                id="bar_relation_filter_interaction",
                figure=px.box(
                    df_gapminder,
                    x="continent",
                    y="lifeExp",
                    color="continent",
                    custom_data=["continent"],
                    labels={
                        "lifeExp": "Life expectancy",
                        "continent": "Continent",
                    },
                    color_discrete_map={
                        "Africa": "#00b4ff",
                        "Americas": "#ff9222",
                        "Asia": "#3949ab",
                        "Europe": "#ff5267",
                        "Oceania": "#08bdba",
                    },
                ),
                actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_filter_interaction"]))],
            ),
            vm.Graph(
                id="scatter_relation_filter_interaction",
                figure=px.scatter(
                    df_gapminder,
                    x="gdpPercap",
                    y="lifeExp",
                    size="pop",
                    color="continent",
                    labels={
                        "lifeExp": "Life expectancy",
                        "gdpPercap": "GDP per capita",
                        "continent": "Continent",
                    },
                    color_discrete_map={
                        "Africa": "#00b4ff",
                        "Americas": "#ff9222",
                        "Asia": "#3949ab",
                        "Europe": "#ff5267",
                        "Oceania": "#08bdba",
                    },
                ),
            ),
        ],
        controls=[vm.Filter(column="continent")],
    )

    return [page_export_data, page_filter_interaction]


def create_extensions_page():
    @capture("graph")
    def scatter_with_line(data_frame, x, y, color=None, size=None, hline=None):
        fig = px.scatter(data_frame=data_frame, x=x, y=y, color=color, size=size)
        fig.add_hline(y=hline, line_color="gray")
        return fig

    page_custom_chart_plotly = vm.Page(
        title="Custom plotly chart",
        path="custom-plotly-chart",
        components=[
            vm.Graph(
                id="enhanced_scatter",
                figure=scatter_with_line(
                    x="sepal_length",
                    y="sepal_width",
                    color="species",
                    size="petal_width",
                    hline=3,
                    data_frame=px.data.iris(),
                ),
            ),
        ],
        controls=[
            vm.Filter(column="petal_width"),
        ],
    )

    def waterfall_data():
        return pd.DataFrame(
            {
                "measure": ["relative", "relative", "total", "relative", "relative", "total"],
                "x": ["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"],
                "text": ["+60", "+80", "", "-40", "-20", "Total"],
                "y": [60, 80, 0, -40, -20, 0],
            }
        )

    @capture("graph")
    def waterfall(data_frame, measure, x, y, text, title=None):
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

    page_custom_chart_go = vm.Page(
        title="Custom graph object chart",
        components=[
            vm.Graph(
                id="waterfall",
                figure=waterfall(data_frame=waterfall_data(), measure="measure", x="x", y="y", text="text"),
            ),
        ],
        controls=[
            vm.Filter(column="x", selector=vm.Dropdown(title="Financial categories", multi=True)),
        ],
    )

    iris = px.data.iris()

    # 1. Create custom component - here based on the existing RangeSlider
    class TooltipNonCrossRangeSlider(vm.RangeSlider):
        """Custom numeric multi-selector `TooltipNonCrossRangeSlider`."""

        type: Literal["other_range_slider"] = "other_range_slider"

        def build(self):
            value = self.value or [self.min, self.max]  # type: ignore[list-item]

            output = [
                Output(f"{self.id}_start_value", "value"),
                Output(f"{self.id}_end_value", "value"),
                Output(self.id, "value"),
                Output(f"temp-store-range_slider-{self.id}", "data"),
            ]
            input = [
                Input(f"{self.id}_start_value", "value"),
                Input(f"{self.id}_end_value", "value"),
                Input(self.id, "value"),
                State(f"temp-store-range_slider-{self.id}", "data"),
            ]

            @callback(output=output, inputs=input)
            def update_slider_values(start, end, slider, input_store):
                trigger_id = callback_context.triggered_id
                if trigger_id == f"{self.id}_start_value" or trigger_id == f"{self.id}_end_value":
                    start_text_value, end_text_value = start, end
                elif trigger_id == self.id:
                    start_text_value, end_text_value = slider
                else:
                    start_text_value, end_text_value = input_store if input_store is not None else value

                start_value = min(start_text_value, end_text_value)
                end_value = max(start_text_value, end_text_value)
                start_value = max(self.min, start_value)
                end_value = min(self.max, end_value)
                slider_value = [start_value, end_value]
                return start_value, end_value, slider_value, (start_value, end_value)

            return html.Div(
                [
                    html.P(self.title, id="range_slider_title") if self.title else None,
                    html.Div(
                        [
                            dcc.RangeSlider(
                                id=self.id,
                                min=self.min,
                                max=self.max,
                                step=self.step,
                                marks=self.marks,
                                className="range_slider_control" if self.step else "range_slider_control_no_space",
                                value=value,
                                persistence=True,
                                allowCross=False,
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                            html.Div(
                                [
                                    dcc.Input(
                                        id=f"{self.id}_start_value",
                                        type="number",
                                        placeholder="start",
                                        min=self.min,
                                        max=self.max,
                                        className="slider_input_field_left"
                                        if self.step
                                        else "slider_input_field_no_space_left",
                                        value=value[0],
                                        size="24px",
                                        persistence=True,
                                    ),
                                    dcc.Input(
                                        id=f"{self.id}_end_value",
                                        type="number",
                                        placeholder="end",
                                        min=self.min,
                                        max=self.max,
                                        className="slider_input_field_right"
                                        if self.step
                                        else "slider_input_field_no_space_right",
                                        value=value[1],
                                        persistence=True,
                                    ),
                                    dcc.Store(id=f"temp-store-range_slider-{self.id}", storage_type="local"),
                                ],
                                className="slider_input_container",
                            ),
                        ],
                        className="range_slider_inner_container",
                    ),
                ],
                className="selector_container",
            )

    # 2. Add new components to expected type - here the selector of the parent components
    vm.Filter.add_type("selector", TooltipNonCrossRangeSlider)
    vm.Parameter.add_type("selector", TooltipNonCrossRangeSlider)

    page_custom_component_range_slider = vm.Page(
        title="Custom range slider",
        path="custom-range-slider",
        components=[
            vm.Graph(
                id="for_custom_chart",
                figure=px.scatter(iris, title="Foo", x="sepal_length", y="petal_width", color="sepal_width"),
            ),
        ],
        controls=[
            vm.Filter(
                column="sepal_length",
                targets=["for_custom_chart"],
                selector=TooltipNonCrossRangeSlider(),
            ),
            vm.Parameter(
                targets=["for_custom_chart.range_x"],
                selector=TooltipNonCrossRangeSlider(title="Select x-axis range", min=0, max=10),
            ),
        ],
    )

    # 1. Create new custom component
    class Jumbotron(vm.VizroBaseModel):
        """New custom component `Jumbotron`."""

        type: Literal["jumbotron"] = "jumbotron"
        title: str
        subtitle: str
        text: str

        def build(self):
            return html.Div(
                [
                    html.H2(self.title),
                    html.H3(self.subtitle),
                    html.P(self.text),
                ]
            )

    # 2. Add new components to expected type - here the selector of the parent components
    vm.Page.add_type("components", Jumbotron)

    page_custom_jumbotron = vm.Page(
        title="Custom jumbotron",
        path="custom-jumbotron",
        components=[
            Jumbotron(
                id="my_jumbotron",
                title="Jumbotron",
                subtitle="This is a subtitle to summarize some content.",
                text="This is the main body of text of the Jumbotron.",
            )
        ],
    )

    return [page_custom_chart_plotly, page_custom_chart_go, page_custom_component_range_slider, page_custom_jumbotron]


def create_home_page():
    """Function returns the homepage."""
    page_home = vm.Page(
        title="Vizro Features",
        path="vizro-features",
        layout=vm.Layout(grid=[[0, 1], [2, 3]], row_gap="16px", col_gap="24px"),
        components=[
            vm.Card(
                text="""
                        ![](assets/images/icons/features.svg#icon-top)

                        ### Components

                        Main components of vizro include **charts**, **cards** and **buttons**.

                    """,
                href="/component-chart",
            ),
            vm.Card(
                text="""
                        ![](assets/images/icons/features.svg#icon-top)

                        ### Controls

                        Vizro has two different control types **filters** and **parameters**.

                        """,
                href="/controls-filter",
            ),
            vm.Card(
                text="""
                        ![](assets/images/icons/features.svg#icon-top)

                        ### Actions

                        Standard predefined actions are made available including **export data** and **filer interactions**.
                    """,
                href="/action-export-data",
            ),
            vm.Card(
                text="""
                        ![](assets/images/icons/features.svg#icon-top)

                        ### Extensions

                        Vizro enables customization of **plotly charts** and **graph object charts** as well as customizing **existig component** and creating **new ones**.
                    """,
                href="/custom-plotly-chart",
            ),
        ],
    )
    return page_home


def retrieve_feature_pages():
    page_list = (
        [create_home_page()]
        + create_components_pages()
        + create_controls_pages()
        + create_actions_page()
        + create_extensions_page()
    )

    return page_list

dashboard = vm.Dashboard(
        pages=[create_home_page()]
        + create_components_pages()
        + create_controls_pages()
        + create_actions_page()
        + create_extensions_page(),
        navigation=vm.Navigation(
            nav_selector=vm.NavBar(
                items=[
                    vm.NavLink(label="Homepage", pages=["Vizro Features"], icon="Home"),
                    vm.NavLink(
                        label="Features",
                        pages={
                "Components": ["Chart", "Card", "Button"],
                "Controls": ["Filter", "Parameter"],
                "Actions": ["Export data", "Filter interaction"],
                "Extensions": [
                    "Custom plotly chart",
                    "Custom graph object chart",
                    "Custom range slider",
                    "Custom jumbotron",
                ],
            },
                        icon="Stacked Bar Chart",
                    ),
                ]
            ),

        ),
    )

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
