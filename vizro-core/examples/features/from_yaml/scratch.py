from typing import Literal

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, callback_context, dcc, html

import vizro.models as vm
import vizro.plotly.express as px
from vizro.models.types import capture

iris = px.data.iris()
gapminder_2007 = px.data.gapminder().query("year == 2007")


# EXTENSIONS ------------------------------------------------------------------
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
