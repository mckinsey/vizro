"""Unit tests for vizro.models.Graph."""

import re

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from dash.exceptions import MissingCallbackContextException
from pydantic import ValidationError

import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager
from vizro.models._action._action import Action


@pytest.fixture
def standard_px_chart_with_str_dataframe():
    return px.scatter(
        data_frame="gapminder",
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        size_max=60,
    )


@pytest.fixture
def standard_px_chart_with_title():
    return px.scatter(data_frame="gapminder", x="gdpPercap", y="lifeExp", title="Title")


class TestGraphInstantiation:
    def test_create_graph_mandatory_only(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart)

        assert hasattr(graph, "id")
        assert graph.type == "graph"
        assert graph.figure == standard_px_chart._captured_callable
        assert graph.actions == []
        assert graph.title == ""
        assert graph.header == ""
        assert graph.footer == ""
        assert graph.description is None
        assert graph._action_outputs == {"__default__": f"{graph.id}.figure"}

    def test_create_graph_mandatory_and_optional(self, standard_px_chart):
        graph = vm.Graph(
            id="graph-id",
            figure=standard_px_chart,
            title="Title",
            description="Test description",
            header="Header",
            footer="Footer",
        )

        assert graph.id == "graph-id"
        assert graph.type == "graph"
        assert graph.figure == standard_px_chart._captured_callable
        assert graph.actions == []
        assert graph.title == "Title"
        assert graph.header == "Header"
        assert graph.footer == "Footer"
        assert isinstance(graph.description, vm.Tooltip)
        assert graph._action_outputs == {
            "__default__": f"{graph.id}.figure",
            "title": f"{graph.id}_title.children",
            "header": f"{graph.id}_header.children",
            "footer": f"{graph.id}_footer.children",
            "description": f"{graph.description.id}-text.children",
        }

    def test_mandatory_figure_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Graph()

    def test_captured_callable_invalid(self, standard_go_chart):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "Invalid CapturedCallable. Supply a function imported from vizro.plotly.express or "
                "defined with decorator @capture('graph')."
            ),
        ):
            vm.Graph(figure=standard_go_chart)

    def test_captured_callable_wrong_mode(self, standard_ag_grid):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "CapturedCallable was defined with @capture('ag_grid') rather than @capture('graph') and so "
                "is not compatible with the model."
            ),
        ):
            vm.Graph(figure=standard_ag_grid)

    def test_is_model_inheritable(self, standard_px_chart):
        class MyGraph(vm.Graph):
            pass

        my_graph = MyGraph(figure=standard_px_chart)

        assert hasattr(my_graph, "id")
        assert my_graph.type == "graph"
        assert my_graph.figure == standard_px_chart._captured_callable
        assert my_graph.actions == []


class TestDunderMethodsGraph:
    def test_getitem_known_args(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart)

        assert graph["x"] == "gdpPercap"
        assert graph["type"] == "graph"

    def test_getitem_unknown_args(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart)
        with pytest.raises(KeyError):
            graph["unknown_args"]

    @pytest.mark.parametrize(
        "title, margin_t",
        [(None, None), ("Graph with title", 64), ("Graph with title..<br> and subtitle", 64)],
    )
    def test_title_layout_adjustments(self, gapminder, title, margin_t, mocker):
        # Mock out `set_props` so we don't need to supply mock callback context for this test.
        mocker.patch("vizro.models._components.graph.set_props", side_effect=MissingCallbackContextException)
        graph = vm.Graph(figure=px.bar(data_frame=gapminder, x="year", y="pop", title=title)).__call__()

        # These are the overwrites in graph._optimise_fig_layout_for_dashboard
        assert graph.layout.margin.t == margin_t

        # These are our defaults for the layout defined in `_templates.common_values`
        assert graph.layout.template.layout.margin.t == 64
        assert graph.layout.template.layout.margin.l == 80
        assert graph.layout.template.layout.margin.b == 64
        assert graph.layout.template.layout.margin.r == 24
        assert graph.layout.template.layout.title.pad.t == 24

    def test_update_theme_outside_callback(self, standard_px_chart, mocker):
        # Mock out set_props so we don't need to supply mock callback context for this test.
        mocker.patch("vizro.models._components.graph.set_props", side_effect=MissingCallbackContextException)
        graph = vm.Graph(figure=standard_px_chart).__call__()
        assert graph == standard_px_chart

    def test_set_action_via_validator(self, standard_px_chart, identity_action_function):
        graph = vm.Graph(figure=standard_px_chart, actions=[Action(function=identity_action_function())])
        actions_chain = graph.actions[0]
        assert actions_chain.trigger.component_property == "clickData"


class TestAttributesGraph:
    # Testing at this low implementation level as mocking callback contexts skips checking for creation of these objects
    def test_graph_filter_interaction_attributes(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart)
        assert hasattr(graph, "_filter_interaction_input")
        assert "modelID" in graph._filter_interaction_input


class TestProcessGraphDataFrame:
    def test_process_figure_data_frame_str_df(self, standard_px_chart_with_str_dataframe, gapminder):
        data_manager["gapminder"] = gapminder
        graph = vm.Graph(id="graph", figure=standard_px_chart_with_str_dataframe)
        assert data_manager[graph["data_frame"]].load().equals(gapminder)

    def test_process_figure_data_frame_df(self, standard_px_chart, gapminder):
        graph = vm.Graph(id="graph", figure=standard_px_chart)
        assert data_manager[graph["data_frame"]].load().equals(gapminder)


class TestPreBuildGraph:
    def test_warning_raised_figure_title(self, standard_px_chart_with_title):
        graph = vm.Graph(figure=standard_px_chart_with_title)
        with pytest.warns(
            UserWarning,
            match="Using the `title` argument in your Plotly chart function may cause misalignment with "
            "other component titles on the screen. To ensure consistent alignment, consider using "
            r"`vm.Graph\(title='Title', ...\)`.",
        ):
            graph.pre_build()


class TestBuildGraph:
    def test_graph_build_mandatory(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart).build()

        expected_graph = dcc.Loading(
            html.Div(
                [
                    None,
                    None,
                    dcc.Graph(
                        figure=go.Figure(
                            layout={
                                "paper_bgcolor": "rgba(0,0,0,0)",
                                "plot_bgcolor": "rgba(0,0,0,0)",
                                "xaxis": {"visible": False},
                                "yaxis": {"visible": False},
                            }
                        ),
                        config={
                            "autosizable": True,
                            "frameMargins": 0,
                            "responsive": True,
                            "modeBarButtonsToRemove": ["toImage"],
                        },
                    ),
                    None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
        assert_component_equal(graph, expected_graph, keys_to_strip={"id"})

    def test_graph_build_title_header_footer(self, standard_px_chart):
        graph = vm.Graph(
            figure=standard_px_chart, title="Title", header="""#### Subtitle""", footer="""SOURCE: **DATA**"""
        ).build()

        expected_graph = dcc.Loading(
            html.Div(
                [
                    html.H3([html.Span("Title"), None], className="figure-title"),
                    dcc.Markdown("""#### Subtitle""", className="figure-header"),
                    dcc.Graph(
                        figure=go.Figure(
                            layout={
                                "paper_bgcolor": "rgba(0,0,0,0)",
                                "plot_bgcolor": "rgba(0,0,0,0)",
                                "xaxis": {"visible": False},
                                "yaxis": {"visible": False},
                            }
                        ),
                        config={
                            "autosizable": True,
                            "frameMargins": 0,
                            "responsive": True,
                            "modeBarButtonsToRemove": ["toImage"],
                        },
                    ),
                    dcc.Markdown("""SOURCE: **DATA**""", className="figure-footer"),
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
        assert_component_equal(graph, expected_graph, keys_to_strip={"id"})

    def test_graph_build_with_description(self, standard_px_chart):
        graph = vm.Graph(
            figure=standard_px_chart,
            title="Title",
            description=vm.Tooltip(text="Tooltip test", icon="info", id="info"),
        ).build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=dcc.Markdown("Tooltip test", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]

        expected_graph = dcc.Loading(
            html.Div(
                [
                    html.H3([html.Span("Title"), *expected_description], className="figure-title"),
                    None,
                    dcc.Graph(
                        figure=go.Figure(
                            layout={
                                "paper_bgcolor": "rgba(0,0,0,0)",
                                "plot_bgcolor": "rgba(0,0,0,0)",
                                "xaxis": {"visible": False},
                                "yaxis": {"visible": False},
                            }
                        ),
                        config={
                            "autosizable": True,
                            "frameMargins": 0,
                            "responsive": True,
                            "modeBarButtonsToRemove": ["toImage"],
                        },
                    ),
                    None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
        assert_component_equal(graph, expected_graph, keys_to_strip={"id"})

    def test_graph_build_with_extra(self, standard_px_chart):
        graph = vm.Graph(
            figure=standard_px_chart,
            title="Title",
            extra={"className": "test", "config": {"displayModeBar": False}},
        ).build()

        expected_graph = dcc.Loading(
            html.Div(
                [
                    html.H3([html.Span("Title"), None], className="figure-title"),
                    None,
                    dcc.Graph(
                        figure=go.Figure(
                            layout={
                                "paper_bgcolor": "rgba(0,0,0,0)",
                                "plot_bgcolor": "rgba(0,0,0,0)",
                                "xaxis": {"visible": False},
                                "yaxis": {"visible": False},
                            }
                        ),
                        config={
                            "autosizable": True,
                            "frameMargins": 0,
                            "responsive": True,
                            "modeBarButtonsToRemove": ["toImage"],
                            "displayModeBar": False,
                        },
                        className="test",
                    ),
                    None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
        assert_component_equal(graph, expected_graph, keys_to_strip={"id"})
