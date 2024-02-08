"""Fixtures to be shared across several tests."""

import pytest

import vizro.models as vm


@pytest.fixture()
def pages_as_list():
    return ["Page 1", "Page 2"]


@pytest.fixture
def pages_as_dict():
    return {"Group": ["Page 1", "Page 2"]}


@pytest.fixture()
def prebuilt_two_page_dashboard(vizro_app, page_1, page_2):
    dashboard = vm.Dashboard(pages=[page_1, page_2])
    dashboard.pre_build()
    return dashboard
