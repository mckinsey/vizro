import json

import dash.development.base_component
import plotly
import pytest

import vizro.models as vm
from vizro import Vizro
from vizro.managers import model_manager

# Options:
# subclass dict the right way, alter __getitem__, assert function (could be registered), just assert in test
# AM: add more commment about what tests are doing and whether to reuse helper functions


def strip_ids(object):
    """Strips all entries with key "id" from a dictionary, regardless of how deeply it's nested.

    This makes it easy to compare dictionaries generated from Dash components we've created that contain random IDs.
    """
    ...
    if isinstance(object, dict):
        object = {key: strip_ids(value) for key, value in object.items() if key != "id"}
    elif isinstance(object, list):
        object = [strip_ids(item) for item in object]
    return object


def component_to_dict(component: dash.development.base_component.Component):
    dictionary = json.loads(json.dumps(component, cls=plotly.utils.PlotlyJSONEncoder))
    dictionary = strip_ids(dictionary)
    return dictionary


@pytest.fixture
def dashboard_result(request):
    # Inject the navigation into the dashboard. Note we need to call request.param since they are all lambda functions.
    dashboard = vm.Dashboard(
        pages=[
            vm.Page(title="Page 1", components=[vm.Button()]),
            vm.Page(title="Page 2", components=[vm.Button()]),
        ],
        navigation=request.param(),
    )
    Vizro()._pre_build()
    # Ideally we would do Vizro._reset after yield dashboard, but that won't work since the fixture is used
    # indirectly and needs to be reset immediately after it's used rather than after running the test.
    # We can't do Vizro._reset since current implementation of navigation uses dash.page_registry to look up a page,
    # so that must remain populated.
    model_manager._clear()
    return dashboard


# Looks hacky but this is the easiest way to use the fixture twice in the same test.
dashboard_expected = dashboard_result

# All the cases need to built lazily - instantiating them directly would not raise validation errors that the
# specified page cannot be found in the page registry.
# fmt: off
accordion_cases = [
    (
        lambda: None,
        lambda: vm.Navigation(nav_selector=vm.Accordion(pages=["Page 1", "Page 2"])),
    ),
    (
        lambda: vm.Navigation(),
        lambda: vm.Navigation(nav_selector=vm.Accordion(pages=["Page 1", "Page 2"])),
    ),
    (
        lambda: vm.Navigation(nav_selector=vm.Accordion()),
        lambda: vm.Navigation(nav_selector=vm.Accordion(pages=["Page 1", "Page 2"])),
    ),
    (
        lambda: vm.Navigation(pages=["Page 1"]),
        lambda: vm.Navigation(nav_selector=vm.Accordion(pages=["Page 1"]))),
    (
        lambda: vm.Navigation(pages=["Page 1"], nav_selector=vm.Accordion(pages=["Page 2"])),
        lambda: vm.Navigation(nav_selector=vm.Accordion(pages=["Page 2"])),
    ),
    (
        lambda: vm.Navigation(pages={"Group 1": ["Page 1"], "Group 2": ["Page 2"]}),
        lambda: vm.Navigation(nav_selector=vm.Accordion(pages={"Group 1": ["Page 1"], "Group 2": ["Page 2"]})),
    ),
]
# fmt: on

navbar_flat_cases = [
    (
        lambda: vm.Navigation(nav_selector=vm.NavBar()),
        lambda: vm.Navigation(nav_selector=vm.NavBar(pages=["Page 1", "Page 2"])),
    ),
    (
        lambda: vm.Navigation(nav_selector=vm.NavBar()),
        lambda: vm.Navigation(
            nav_selector=vm.NavBar(
                items=[
                    vm.NavLink(label="Page 1", pages=["Page 1"], icon="filter_1"),
                    vm.NavLink(label="Page 2", pages=["Page 2"], icon="filter_2"),
                ]
            )
        ),
    ),
    (
        lambda: vm.Navigation(pages=["Page 1"], nav_selector=vm.NavBar()),
        lambda: vm.Navigation(nav_selector=vm.NavBar(pages=["Page 1"])),
    ),
    (
        lambda: vm.Navigation(pages=["Page 1"], nav_selector=vm.NavBar(pages=["Page 2"])),
        lambda: vm.Navigation(nav_selector=vm.NavBar(pages=["Page 2"])),
    ),
    (
        lambda: vm.Navigation(pages=["Page 1"], nav_selector=vm.NavBar()),
        lambda: vm.Navigation(
            nav_selector=vm.NavBar(
                items=[
                    vm.NavLink(label="Page 1", pages=["Page 1"], icon="filter_1"),
                ]
            )
        ),
    ),
]

navbar_grouped_cases = [
    (
        lambda: vm.Navigation(pages={"Group 1": ["Page 1"], "Group 2": ["Page 2"]}, nav_selector=vm.NavBar()),
        lambda: vm.Navigation(nav_selector=vm.NavBar(pages={"Group 1": ["Page 1"], "Group 2": ["Page 2"]})),
    ),
    (
        lambda: vm.Navigation(pages={"Group 1": ["Page 1"], "Group 2": ["Page 2"]}, nav_selector=vm.NavBar()),
        lambda: vm.Navigation(
            nav_selector=vm.NavBar(
                items=[
                    vm.NavLink(label="Group 1", pages=["Page 1"], icon="filter_1"),
                    vm.NavLink(label="Group 2", pages=["Page 2"], icon="filter_2"),
                ]
            )
        ),
    ),
    (
        lambda: vm.Navigation(
            nav_selector=vm.NavBar(
                items=[
                    vm.NavLink(label="Group 1", pages={"Subgroup 1": ["Page 1"]}, icon="dashboard"),
                    vm.NavLink(label="Group 2", pages={"Subgroup 2": ["Page 2"]}),
                ]
            )
        ),
        lambda: vm.Navigation(
            nav_selector=vm.NavBar(
                items=[
                    vm.NavLink(label="Group 1", pages={"Subgroup 1": ["Page 1"]}, icon="dashboard"),
                    vm.NavLink(label="Group 2", pages={"Subgroup 2": ["Page 2"]}, icon="filter_2"),
                ]
            )
        ),
    ),
]


# Label the test cases to make it easier to see which one failed.
def label_cases(cases, label):
    return [pytest.param(*case, id=f"{label}-{case_id}") for case_id, case in enumerate(cases)]


accordion_cases = label_cases(accordion_cases, "accordion")
navbar_flat_cases = label_cases(navbar_flat_cases, "navbar_flat")
navbar_grouped_cases = label_cases(navbar_grouped_cases, "navbar_grouped")

print(accordion_cases + navbar_grouped_cases + navbar_flat_cases)


@pytest.mark.parametrize(
    "dashboard_result, dashboard_expected",
    accordion_cases + navbar_flat_cases + navbar_grouped_cases,
    indirect=True,
)
def test_navigation_build(dashboard_result, dashboard_expected):
    result = dashboard_result.navigation.build()
    expected = dashboard_expected.navigation.build()
    assert component_to_dict(result) == component_to_dict(expected)
