import json
from collections import OrderedDict
from functools import partial

import dash
import dash_bootstrap_components as dbc
import plotly
import pytest
from dash import html
from pydantic import ValidationError

import vizro
import vizro.models as vm
from vizro.actions._action_loop._action_loop import ActionLoop
from vizro.models._dashboard import update_theme


@pytest.fixture()
def dashboard_container():
    return dbc.Container(
        id="dashboard_container_outer",
        children=[
            html.Div(id=f"vizro_version_{vizro.__version__}"),
            ActionLoop._create_app_callbacks(),
            dash.page_container,
        ],
        className="vizro_dark",
        fluid=True,
    )


@pytest.fixture()
def mock_page_registry(dashboard, page1, page2):
    return OrderedDict(
        {
            "Page 1": {
                "module": "Page 1",
                "supplied_path": "/",
                "path_template": None,
                "path": "/",
                "supplied_name": "Page 1",
                "name": "Page 1",
                "supplied_title": None,
                "title": "Page 1",
                "description": "",
                "order": 0,
                "supplied_order": 0,
                "supplied_layout": partial(dashboard._make_page_layout, page1),
                "supplied_image": None,
                "image": None,
                "image_url": None,
                "redirect_from": None,
                "layout": partial(dashboard._make_page_layout, page1),
                "relative_path": "/",
            },
            "Page 2": {
                "module": "Page 2",
                "supplied_path": "/page-2",
                "path_template": None,
                "path": "/page-2",
                "supplied_name": "Page 2",
                "name": "Page 2",
                "supplied_title": None,
                "title": "Page 2",
                "description": "",
                "order": 1,
                "supplied_order": 1,
                "supplied_layout": partial(dashboard._make_page_layout, page2),
                "supplied_image": None,
                "image": None,
                "image_url": None,
                "redirect_from": None,
                "layout": partial(dashboard._make_page_layout, page2),
                "relative_path": "/page-2",
            },
            "not_found_404": {
                "module": "not_found_404",
                "supplied_path": None,
                "path_template": None,
                "path": "/not-found-404",
                "supplied_name": None,
                "name": "Not found 404",
                "supplied_title": None,
                "title": "Not found 404",
                "description": "",
                "order": None,
                "supplied_order": None,
                "supplied_layout": dashboard._make_page_404_layout(),
                "supplied_image": None,
                "image": None,
                "image_url": None,
                "redirect_from": None,
                "layout": dashboard._make_page_404_layout(),
                "relative_path": "/not-found-404",
            },
        }
    )


class TestDashboardInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_dashboard_mandatory_only(self, page1, page2):
        dashboard = vm.Dashboard(pages=[page1, page2])
        assert hasattr(dashboard, "id")
        assert dashboard.pages == [page1, page2]
        assert dashboard.theme == "vizro_dark"
        assert dashboard.title is None

    def test_create_dashboard_mandatory_and_optional(self, page1, page2):
        dashboard = vm.Dashboard(pages=[page1, page2], theme="vizro_light", title="Vizro")
        assert hasattr(dashboard, "id")
        assert dashboard.pages == [page1, page2]
        assert dashboard.theme == "vizro_light"
        assert dashboard.title == "Vizro"

    def test_mandatory_pages_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Dashboard()

    def test_field_invalid_pages_empty_list(self):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.Dashboard(pages=[])

    def test_field_invalid_pages_input_type(self):
        with pytest.raises(ValidationError, match="4 validation errors for Dashboard"):
            vm.Dashboard(pages=[vm.Button()])

    def test_field_invalid_theme_input_type(self, page1):
        with pytest.raises(ValidationError, match="unexpected value; permitted: 'vizro_dark', 'vizro_light'"):
            vm.Dashboard(pages=[page1], theme="not_existing")


class TestDashboardPreBuild:
    """Tests dashboard pre_build method."""

    @pytest.mark.usefixtures("vizro_app")
    def test_dashboard_page_registry(self, dashboard, mock_page_registry):
        dashboard.pre_build()
        result = dash.page_registry
        expected = mock_page_registry
        # Str conversion required as comparison of OrderedDict values result in False otherwise
        assert str(result.items()) == str(expected.items())

    def test_create_layout_page_404(self, dashboard, mocker):
        mocker.patch("vizro.models._dashboard.get_relative_path")
        result = dashboard._make_page_404_layout()
        result_image = result.children[0]
        result_div = result.children[1]

        assert isinstance(result, html.Div)
        assert isinstance(result_image, html.Img)
        assert isinstance(result_div, html.Div)


@pytest.mark.usefixtures("vizro_app")
class TestDashboardBuild:
    """Tests dashboard build method."""

    def test_dashboard_build(self, dashboard_container, dashboard):
        dashboard.pre_build()
        dashboard.navigation.pre_build()
        result = json.loads(json.dumps(dashboard.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(dashboard_container, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected


@pytest.mark.parametrize("on, expected", [(True, "vizro_dark"), (False, "vizro_light")])
def test_update_theme(on, expected):
    result = update_theme(on)
    assert result == expected
