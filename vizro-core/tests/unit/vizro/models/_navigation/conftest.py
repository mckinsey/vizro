"""Fixtures to be shared across several tests."""

import pytest

import vizro.models as vm


# Refer to first page by ID, refer to second page by Title
# This tests if both are valid inputs - under the hood we convert the titles to IDs
@pytest.fixture()
def pages_as_list():
    return ["page_1", "Page 2"]


@pytest.fixture
def pages_as_dict():
    return {"Group": ["page_1", "Page 2"]}


@pytest.fixture()
def prebuilt_two_page_dashboard(vizro_app, page_1, page_2):
    dashboard = vm.Dashboard(pages=[page_1, page_2])
    dashboard.pre_build()
    return dashboard
