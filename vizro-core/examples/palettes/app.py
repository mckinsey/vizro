import itertools

import plotly.io as pio
import vizro.models as vm
from charts import charts_by_category
from dash import Input, Output, State, clientside_callback, html
from palettes import DIVERGING_PALETTE, QUALITATIVE_PALETTE, SEQUENTIAL_PALETTE, SEQUENTIALMINUS_PALETTE
from vizro import Vizro





palettes = {"colorscale": {"sequential": SEQUENTIAL_PALETTE, "diverging": DIVERGING_PALETTE, "sequentialminus": SEQUENTIALMINUS_PALETTE}, "colorway": QUALITATIVE_PALETTE}

pio.templates["vizro_light"] = pio.templates.merge_templates("vizro_light", {"layout": palettes})
pio.templates["vizro_dark"] = pio.templates.merge_templates("vizro_dark", {"layout": palettes})


DISCRETE_TEXT = """
## Discrete
`px` functions have arguments `color_discrete_sequence` and `color_discrete_map`.

Palette is given by `template.layout.colorway`.
"""
CONTINUOUS_TEXT = """
## Continuous
`px` functions have arguments `color_continuous_scale`, `color_continuous_midpoint`, and `range_color`.

Palette is given by `template.layout.colorscale.sequential`, `template.layout.colorscale.diverging`, and `template.layout.colorscale.sequentialminus`.
"""

INTRODUCTION_TEXT = """
This page demonstrates all Plotly Express chart types (with the exception of `imshow` and deprecated `mapbox` functions) and the different discrete and continuous palettes available in Vizro.

### Features
* Change the continuous color scale using the dropdown in the header
* Change the container fill variant using the dropdown in the header
* Switch between light and dark themes using the theme toggle
* Hover over info icons to see the underlying trace type and Plotly Express function

### Chart Categories
{chart_categories_text}
"""

class CustomDashboard(vm.Dashboard):
    """Custom dashboard with page controls in header and no left panel.

    Overrides _inner_page to hide the left navigation panel and custom_header to place
    page controls (colorscale selector, container variant dropdown) in the header next to
    the theme switch instead of in the left sidebar.
    """

    def _inner_page(self, page):
        """Override to hide the left panel."""
        self._current_page = page
        inner_page = super()._inner_page(page)
        inner_page["nav-control-panel"] = html.Div(id="nav-control-panel", hidden=True)
        return inner_page

    def custom_header(self):
        """Add page controls to header next to theme switch."""
        if hasattr(self, "_current_page") and self._current_page.controls:
            return [control.build() for control in self._current_page.controls]
        return []

def make_chart_id(px_function, suffix):
    return f"{px_function.split('.')[1]}_{suffix}"


def make_chart_container(category, charts):
    graphs = []
    grid = []
    graph_index = 0

    for chart_type in charts:
        description = (
            f"**Plotly Express function:** `{chart_type.px_function}`  \n**Trace type:** `{chart_type.trace_type}`"
        )

        row = []
        for figure, suffix in [
            (chart_type.discrete_figure, "discrete"),
            (chart_type.continuous_figure, "continuous"),
        ]:
            if figure is not None:
                graphs.append(
                    vm.Graph(
                        id=make_chart_id(chart_type.px_function, suffix),
                        title=chart_type.title,
                        header=chart_type.extra_notes,
                        figure=figure,
                        description=description,
                    )
                )
                row.append(graph_index)
                graph_index += 1
            else:
                row.append(-1)

        grid.append(row)

    return vm.Container(
        title=category,
        layout=vm.Flex(),
        components=[
            vm.Container(
                layout=vm.Grid(grid=[[0, 1]]), components=[vm.Text(text=DISCRETE_TEXT), vm.Text(text=CONTINUOUS_TEXT)]
            ),
            vm.Container(layout=vm.Grid(grid=grid), components=graphs),
        ],
        variant="outlined",
    )


def generate_chart_categories_text():
    """Generate markdown text listing all chart categories and their charts."""
    lines = []
    for category, charts in charts_by_category.items():
        chart_titles = [chart.title.lower() for chart in charts]
        lines.append(f"* **{category}**: {', '.join(chart_titles)}")
    return "\n".join(lines)



introduction_container = vm.Container(
    title="Introduction", components=[vm.Text(text=INTRODUCTION_TEXT.format(chart_categories_text=generate_chart_categories_text()))], variant="outlined"
)


vm.Page.add_type("controls", vm.Dropdown)

chart_containers = [make_chart_container(category, charts) for category, charts in charts_by_category.items()]

page = vm.Page(
    title="",
    layout=vm.Flex(),
    components=[vm.Tabs(tabs=[introduction_container, *chart_containers])],
    controls=[
        vm.Parameter(
            targets=[
                f"{make_chart_id(chart_type.px_function, 'continuous')}.color_continuous_scale"
                for chart_type in itertools.chain.from_iterable(charts_by_category.values())
                if chart_type.continuous_figure is not None
            ],
            selector=vm.Dropdown(
                id="colorscale_selector",
                options=["sequential colorscale", "diverging colorscale", "sequentialminus colorscale"],
                multi=False,
                extra={"style": {"width": "220px"}, "optionHeight": 32},
            ),
        ),
        vm.Dropdown(
            id="container_variant",
            options=["outlined container", "filled container"],
            multi=False,
            extra={"style": {"width": "160px"}, "optionHeight": 32},
        ),
    ],
)

# Clientside callback to update container variant.
clientside_callback(
    """
    function(variant_value, ...container_ids) {
        const variants = {
            "plain container": "",
            "filled container": "bg-container p-3",
            "outlined container": "border p-3"
        };
        const className = variants[variant_value];
        return Array(container_ids.length).fill(className);
    }
    """,
    [Output(container.id, "class_name") for container in [introduction_container, *chart_containers]],
    Input("container_variant", "value"),
    *[State(container.id, "id") for container in [introduction_container, *chart_containers]],
)

dashboard = CustomDashboard(title="Plotly Express Charts with Vizro Palettes", pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
