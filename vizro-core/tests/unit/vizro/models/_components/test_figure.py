"""Unit tests for vizro.models.Figure."""

import pytest
from asserts import assert_component_equal
from dash import dcc, html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm
from vizro.figures import kpi_card
from vizro.managers import data_manager


@pytest.fixture
def kpi_card_with_dataframe(gapminder):
    return kpi_card(
        data_frame=gapminder,
        value_column="lifeExp",
        agg_func="mean",
        value_format="{value:.3f}",
    )


@pytest.fixture
def kpi_card_with_str_dataframe():
    return kpi_card(
        data_frame="gapminder",
        value_column="lifeExp",
        agg_func="mean",
        value_format="{value:.3f}",
    )


class TestFigureInstantiation:
    def test_create_figure_mandatory_only(self, kpi_card_with_dataframe):
        figure = vm.Figure(figure=kpi_card_with_dataframe)

        assert hasattr(figure, "id")
        assert figure.type == "figure"
        assert figure.figure == kpi_card_with_dataframe

    def test_mandatory_figure_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Figure()

    def test_wrong_captured_callable(self, standard_ag_grid):
        with pytest.raises(ValidationError, match="CapturedCallable mode mismatch."):
            vm.Figure(figure=standard_ag_grid)

    def test_failed_figure_with_no_captured_callable(self, standard_go_chart):
        with pytest.raises(ValidationError, match="must provide a valid CapturedCallable object"):
            vm.Figure(figure=standard_go_chart)


class TestDunderMethodsFigure:
    def test_getitem_known_args(self, kpi_card_with_dataframe):
        figure = vm.Figure(figure=kpi_card_with_dataframe)
        assert figure["value_column"] == "lifeExp"
        assert figure["agg_func"] == "mean"
        assert figure["value_format"] == "{value:.3f}"
        assert figure["type"] == "figure"

    def test_getitem_unknown_args(self, kpi_card_with_dataframe):
        figure = vm.Figure(figure=kpi_card_with_dataframe)
        with pytest.raises(KeyError):
            figure["unknown_args"]


class TestProcessFigureDataFrame:
    def test_process_figure_data_frame_str_df(self, kpi_card_with_str_dataframe, gapminder):
        data_manager["gapminder"] = gapminder
        figure = vm.Figure(figure=kpi_card_with_str_dataframe)
        assert data_manager[figure["data_frame"]].load().equals(gapminder)

    def test_process_figure_data_frame_df(self, kpi_card_with_dataframe, gapminder):
        figure = vm.Figure(figure=kpi_card_with_dataframe)
        assert data_manager[figure["data_frame"]].load().equals(gapminder)


class TestFigureBuild:
    def test_figure_build(self, kpi_card_with_dataframe, gapminder):
        figure = vm.Figure(id="figure-id", figure=kpi_card_with_dataframe).build()

        expected_figure = dcc.Loading(
            html.Div(
                kpi_card(
                    data_frame=gapminder,
                    value_column="lifeExp",
                    agg_func="mean",
                    title="Mean Lifeexp",
                    value_format="{value:.3f}",
                )(),
                className="figure-container",
                id="figure-id",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
        assert_component_equal(figure, expected_figure)
