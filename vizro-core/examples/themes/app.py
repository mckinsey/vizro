"""Example app to show Vizro-McK."""

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card, kpi_card_reference
from vizro.models._components.form._text_area import TextArea
from vizro.models._components.form._user_input import UserInput
from vizro.models.types import capture
from vizro.tables import dash_ag_grid
from vizro.themes import palettes

iris = px.data.iris()
tips = px.data.tips()
stocks = px.data.stocks(datetimes=True)
gapminder_2007 = px.data.gapminder().query("year == 2007")
df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})

waterfall_data = pd.DataFrame(
    {
        "x": [
            "Sales",
            "Consulting",
            "Net revenue",
            "Purchases",
            "Other expenses",
            "Profit before tax",
        ],
        "y": [60, 80, 0, -40, -20, 0],
        "measure": [
            "relative",
            "relative",
            "total",
            "relative",
            "relative",
            "total",
        ],
    }
)

sankey_data = pd.DataFrame(
    {
        "source": [
            "Production",
            "Production",
            "Imports",
            "Renewables",
            "Fossil",
            "Nuclear",
            "Renewables",
            "Fossil",
            "Nuclear",
            "Industry",
            "Heating",
            "Transport",
        ],
        "target": [
            "Renewables",
            "Fossil",
            "Fossil",
            "Industry",
            "Industry",
            "Industry",
            "Heating",
            "Heating",
            "Heating",
            "Losses",
            "Losses",
            "Losses",
        ],
        "value": [15, 45, 10, 12, 35, 8, 10, 12, 5, 25, 22, 23],
    }
)

vm.Container.add_type("components", vm.Dropdown)
vm.Container.add_type("components", vm.RadioItems)
vm.Container.add_type("components", vm.Checklist)
vm.Container.add_type("components", vm.Slider)
vm.Container.add_type("components", vm.RangeSlider)
vm.Container.add_type("components", vm.DatePicker)
vm.Container.add_type("components", vm.Text)
vm.Container.add_type("components", vm.Card)
vm.Container.add_type("components", UserInput)
vm.Container.add_type("components", TextArea)
vm.Container.add_type("components", vm.Button)


@capture("graph")
def waterfall(data_frame: pd.DataFrame, x: str, y: str, measure: list[str]):
    """Custom waterfall chart."""
    fig = go.Figure(
        data=go.Waterfall(
            x=data_frame[x],
            y=data_frame[y],
            measure=data_frame[measure],
            showlegend=False,
        ),
    )
    fig.update_layout(showlegend=False)
    return fig


@capture("graph")
def sankey(data_frame: pd.DataFrame, source: str, target: str, value: str):
    """Custom Sankey diagram."""
    labels = list(pd.unique(data_frame[[source, target]].values.ravel("K")))
    node_indices = {label: i for i, label in enumerate(labels)}
    fig = go.Figure(
        data=go.Sankey(
            node=dict(label=labels),
            link=dict(
                source=[node_indices[s] for s in data_frame[source]],
                target=[node_indices[t] for t in data_frame[target]],
                value=data_frame[value],
            ),
        ),
    )
    return fig


# PAGES ------------------------------------------------------------------

avg_lifeExp = (gapminder_2007["lifeExp"] * gapminder_2007["pop"]).sum() / gapminder_2007["pop"].sum()

continuous_color_scales = vm.Page(
    title="Continuous color scales",
    layout=vm.Grid(grid=[[0, 1, 2]]),
    components=[
        vm.Graph(
            title="Sequential",
            figure=px.choropleth(
                gapminder_2007, locations="iso_alpha", color="lifeExp", color_continuous_scale=palettes.sequential
            ),
            footer="Source: Plotly Gapminder data set, 2024",
        ),
        vm.Graph(
            title="Sequential Minus",
            figure=px.choropleth(
                gapminder_2007,
                locations="iso_alpha",
                color="lifeExp",
                color_continuous_midpoint=avg_lifeExp,
                color_continuous_scale=palettes.sequential_minus,
            ),
            footer="Source: Plotly Gapminder data set, 2024",
        ),
        vm.Graph(
            title="Diverging",
            figure=px.choropleth(
                gapminder_2007,
                locations="iso_alpha",
                color="lifeExp",
                color_continuous_midpoint=avg_lifeExp,
                color_continuous_scale=palettes.diverging,
            ),
            footer="Source: Plotly Gapminder data set, 2024",
        ),
    ],
)


form = vm.Page(
    title="Form",
    layout=vm.Grid(grid=[[0, 1]], col_gap="80px"),
    components=[
        vm.Container(
            layout=vm.Flex(gap="40px"),
            components=[
                UserInput(title="User Input", placeholder="Enter your name"),
                TextArea(title="Text Area", placeholder="Enter your multi-line text"),
                vm.Dropdown(options=["Option 1", "Option 2", "Option 3"], title="Multi-select Dropdown"),
                vm.Dropdown(options=["Option 1", "Option 2", "Option 3"], title="Single-select Dropdown", multi=False),
                vm.RadioItems(options=["Option 1", "Option 2", "Option 3"], title="Radio Items"),
                vm.Checklist(options=["Option 1", "Option 2", "Option 3"], title="Checklist"),
            ],
        ),
        vm.Container(
            layout=vm.Flex(gap="30px"),
            components=[
                vm.Slider(min=0, max=10, step=1, title="Slider"),
                vm.RangeSlider(min=0, max=10, step=1, title="Range Slider"),
                vm.DatePicker(title="Date Picker", min="2025-01-01", max="2025-01-31"),
                vm.Container(
                    title="Buttons",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.Button(text="PRIMARY BUTTON", variant="filled"),
                        vm.Button(text="SECONDARY BUTTON", variant="outlined"),
                        vm.Button(text="TERTIARY BUTTON", variant="plain"),
                    ],
                ),
                vm.Card(
                    text="""
                    ### Card

                    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt
                    ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation.

                    """
                ),
                vm.Text(
                    text="""

                    ### Markdown

                    Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                    * Item A
                        * Sub Item 1
                        * Sub Item 2
                    * Item B



                    """
                ),
            ],
        ),
    ],
)

graphs = vm.Page(
    title="Graphs",
    layout=vm.Grid(grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8]]),
    components=[
        vm.Graph(
            figure=px.scatter(
                gapminder_2007,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                size_max=60,
                color="continent",
            )
        ),
        vm.Graph(figure=px.box(tips, y="total_bill", x="day", color="day")),
        vm.Graph(figure=px.histogram(tips, x="total_bill")),
        vm.Graph(
            figure=px.histogram(
                tips,
                y="day",
                x="total_bill",
                color="sex",
                barmode="group",
                orientation="h",
            )
        ),
        vm.Graph(figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f")),
        vm.Graph(figure=px.histogram(tips, x="sex", y="total_bill", color="day")),
        vm.Graph(figure=waterfall(waterfall_data, x="x", y="y", measure="measure")),
        vm.Graph(figure=px.pie(tips, values="tip", names="day", hole=0.85)),
        vm.Graph(
            figure=px.bar(
                gapminder_2007.query("country.isin(['United States', 'Pakistan', 'India', 'China', 'Indonesia'])"),
                x="pop",
                y="country",
                orientation="h",
            )
        ),
    ],
)

sankey_page = vm.Page(
    title="Sankey",
    components=[
        vm.Graph(
            title="Energy flow",
            figure=sankey(sankey_data, source="source", target="target", value="value"),
            footer="Sample energy flow from sources to sectors.",
        ),
    ],
)

ag_grid = vm.Page(
    title="AG Grid",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(data_frame=gapminder_2007, dashGridOptions={"pagination": True}),
            title="Gapminder Data Insights",
            header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
            footer="""SOURCE: **Plotly gapminder data set, 2024**""",
        )
    ],
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
        value_format="{value:.2f}$",
        reference_format="{delta:.2f}$ vs. last year ({reference:.2f}$)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI reference with icon",
        icon="shopping_cart",
    ),
]

figure = vm.Page(
    title="Figure",
    layout=vm.Grid(grid=[[0, 1, 2, 3], [4, 5, 6, 7], [-1, -1, -1, -1], [-1, -1, -1, -1]]),
    components=[vm.Figure(figure=figure) for figure in example_cards + example_reference_cards],
    controls=[vm.Filter(column="Category")],
)


containers = vm.Page(
    title="Containers",
    components=[
        vm.Container(
            title="Container I",
            layout=vm.Grid(grid=[[0, 1]]),
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

collapsible_container = vm.Page(
    title="Collapsible containers",
    layout=vm.Flex(),
    components=[
        vm.Container(
            title="Initially collapsed container",
            components=[vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"))],
            collapsed=True,
        ),
        vm.Container(
            title="Initially expanded container",
            components=[vm.Graph(figure=px.box(iris, x="species", y="sepal_length", color="species"))],
            collapsed=False,
        ),
    ],
)

tab_1 = vm.Container(
    title="Tab I",
    components=[
        vm.Graph(
            figure=px.histogram(
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


# DASHBOARD -------------------------------------------------------------------
dashboard = vm.Dashboard(
    title="Charts",
    pages=[
        graphs,
        sankey_page,
        continuous_color_scales,
        ag_grid,
        cards,
        figure,
        containers,
        collapsible_container,
        tabs,
        form,
    ],
)

if __name__ == "__main__":
    app = Vizro().build(dashboard).run()
