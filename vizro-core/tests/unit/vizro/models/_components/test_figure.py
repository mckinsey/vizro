"""Unit tests for vizro.models.Figure."""

import re

import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm
from vizro.figures import kpi_card
from vizro.managers import data_manager


@pytest.fixture
def kpi_card_with_str_dataframe():
    return kpi_card(
        data_frame="gapminder",
        value_column="lifeExp",
        agg_func="mean",
        value_format="{value:.3f}",
    )


class TestFigureInstantiation:
    def test_create_figure_mandatory_only(self, standard_kpi_card):
        figure = vm.Figure(figure=standard_kpi_card)

        assert hasattr(figure, "id")
        assert figure.type == "figure"
        assert figure.figure == standard_kpi_card
        assert figure._action_outputs == {
            "__default__": f"{figure.id}.children",
            "figure": f"{figure.id}.children",
        }

    def test_captured_callable_invalid(self, standard_go_chart):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "Invalid CapturedCallable. Supply a function imported from vizro.figures or "
                "defined with decorator @capture('figure')."
            ),
        ):
            vm.Figure(figure=standard_go_chart)

    def test_captured_callable_wrong_mode(self, standard_dash_table):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "CapturedCallable was defined with @capture('table') rather than @capture('figure') and so "
                "is not compatible with the model."
            ),
        ):
            vm.Figure(figure=standard_dash_table)

    def test_is_model_inheritable(self, standard_kpi_card):
        class MyFigure(vm.Figure):
            pass

        my_figure = MyFigure(figure=standard_kpi_card)

        assert hasattr(my_figure, "id")
        assert my_figure.type == "figure"
        assert my_figure.figure == standard_kpi_card


class TestDunderMethodsFigure:
    def test_getitem_known_args(self, standard_kpi_card):
        figure = vm.Figure(figure=standard_kpi_card)
        assert figure["value_column"] == "lifeExp"
        assert figure["agg_func"] == "mean"
        assert figure["value_format"] == "{value:.3f}"
        assert figure["type"] == "figure"

    def test_getitem_unknown_args(self, standard_kpi_card):
        figure = vm.Figure(figure=standard_kpi_card)
        with pytest.raises(KeyError):
            figure["unknown_args"]


class TestProcessFigureDataFrame:
    def test_process_figure_data_frame_str_df(self, kpi_card_with_str_dataframe, gapminder):
        data_manager["gapminder"] = gapminder
        figure = vm.Figure(figure=kpi_card_with_str_dataframe)
        assert data_manager[figure["data_frame"]].load().equals(gapminder)

    def test_process_figure_data_frame_df(self, standard_kpi_card, gapminder):
        figure = vm.Figure(figure=standard_kpi_card)
        assert data_manager[figure["data_frame"]].load().equals(gapminder)


class TestFigureBuild:
    def test_figure_build(self, standard_kpi_card, gapminder):
        figure = vm.Figure(id="figure-id", figure=standard_kpi_card).build()

        expected_figure = dcc.Loading(
            html.Div(
                id="figure-id",
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
        assert_component_equal(figure, expected_figure)
