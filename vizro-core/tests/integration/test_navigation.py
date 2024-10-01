import pytest
from asserts import assert_component_equal

import vizro.models as vm
from vizro import Vizro


@pytest.fixture
def dashboard_result(request):
    # Inject the navigation into the dashboard. Note we need to call request.param since they are all lambda functions.
    # Ideally we would do Vizro._reset after yield dashboard, but that won't work since the fixture is used
    # indirectly and needs to be reset immediately after it's used rather than after running the test.
    Vizro._reset()

    dashboard = vm.Dashboard(
        pages=[
            vm.Page(title="Page 1", components=[vm.Button()]),
            vm.Page(title="Page 2", components=[vm.Button()]),
        ],
        navigation=request.param(),
    )
    Vizro()._pre_build()
    return dashboard


# Looks hacky but this is the easiest way to use the fixture twice in the same test.
dashboard_expected = dashboard_result

# All the cases need to built lazily - instantiating them directly would not raise validation errors that the
# specified page cannot be found in the page registry.
# In all test cases, the first lambda should be thought of as the "input" configuration, and the second is the
# configuration that results after we've filled in default values etc.
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
            nav_selector=vm.NavBar(items=[vm.NavLink(label="Page 1", pages=["Page 1"], icon="filter_1")])
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


@pytest.mark.parametrize(
    "dashboard_result, dashboard_expected", accordion_cases + navbar_flat_cases + navbar_grouped_cases, indirect=True
)
def test_navigation_build(dashboard_result, dashboard_expected):
    result = dashboard_result.navigation.build()
    expected = dashboard_expected.navigation.build()
    assert_component_equal(result, expected, keys_to_strip={"id", "target"})
