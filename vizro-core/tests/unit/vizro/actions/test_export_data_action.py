import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

import vizro.models as vm
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.actions._actions_utils import (
    CallbackTriggerDict,
)
from vizro.managers import model_manager


@pytest.fixture
def target_scatter_filter_and_filter_interaction(request, gapminder_2007):
    pop_filter, continent_filter_interaction, country_table_filter_interaction = request.param
    data = gapminder_2007
    if pop_filter:
        data = data[data["pop"].between(pop_filter[0], pop_filter[1], inclusive="both")]
    if continent_filter_interaction:
        data = data[data["continent"].isin(continent_filter_interaction)]
    if country_table_filter_interaction:
        data = data[data["country"].isin(country_table_filter_interaction)]
    return data


@pytest.fixture
def target_box_filtered_pop(request, gapminder_2007):
    pop_filter = request.param
    data = gapminder_2007
    if pop_filter:
        data = data[data["pop"].between(pop_filter[0], pop_filter[1], inclusive="both")]
    return data


@pytest.fixture
def managers_one_page_without_graphs_one_button():
    """Instantiates a simple model_manager and data_manager with a page, and no graphs."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[vm.Button(id="button")],
    )
    Vizro._pre_build()


@pytest.fixture
def callback_context_export_data(request):
    """Mock dash.callback_context that represents filters and filter interactions applied."""
    targets, pop_filter, continent_filter_interaction, country_table_filter_interaction = request.param
    args_grouping_filter_interaction = []
    if continent_filter_interaction:
        args_grouping_filter_interaction.append(
            {
                "clickData": CallbackTriggerDict(
                    id="box_chart",
                    property="clickData",
                    value={
                        "points": [
                            {
                                "customdata": [continent_filter_interaction],
                            }
                        ]
                    },
                    str_id="box_chart",
                    triggered=False,
                )
            }
        )
    if country_table_filter_interaction:
        args_grouping_filter_interaction.append(
            {
                "active_cell": CallbackTriggerDict(
                    id="underlying_table_id",
                    property="active_cell",
                    value={"row": 0, "column": 0, "column_id": "country"},
                    str_id="underlying_table_id",
                    triggered=False,
                ),
                "derived_viewport_data": CallbackTriggerDict(
                    id="underlying_table_id",
                    property="derived_viewport_data",
                    value=[
                        {
                            "country": "Algeria",
                            "continent": "Africa",
                            "year": 2007,
                        },
                        {
                            "country": "Egypt",
                            "continent": "Africa",
                            "year": 2007,
                        },
                    ],
                    str_id="underlying_table_id",
                    triggered=False,
                ),
            }
        )
    mock_callback_context = {
        "args_grouping": {
            "filters": [
                CallbackTriggerDict(
                    id="pop_filter",
                    property="value",
                    value=pop_filter,
                    str_id="pop_filter",
                    triggered=False,
                )
            ]
            if pop_filter
            else [],
            "filter_interaction": args_grouping_filter_interaction,
        },
        "outputs_list": [
            {"id": {"action_id": "test_action", "target_id": target, "type": "download-dataframe"}, "property": "data"}
            for target in targets
        ],
    }
    context_value.set(AttributeDict(**mock_callback_context))
    return context_value


class TestExportData:
    @pytest.mark.usefixtures("managers_one_page_without_graphs_one_button")
    @pytest.mark.parametrize("callback_context_export_data", [([[], None, None, None])], indirect=True)
    def test_no_graphs_no_targets(self, callback_context_export_data):
        # Add action to relevant component
        model_manager["button"].actions = [vm.Action(id="test_action", function=export_data())]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result == {}

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "callback_context_export_data", [([["scatter_chart", "box_chart"], None, None, None])], indirect=True
    )
    def test_graphs_no_targets(self, callback_context_export_data, gapminder_2007):
        # Add action to relevant component
        model_manager["button"].actions = [vm.Action(id="test_action", function=export_data())]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["download-dataframe_scatter_chart"]["filename"] == "scatter_chart.csv"
        assert result["download-dataframe_scatter_chart"]["content"] == gapminder_2007.to_csv(index=False)

        assert result["download-dataframe_box_chart"]["filename"] == "box_chart.csv"
        assert result["download-dataframe_box_chart"]["content"] == gapminder_2007.to_csv(index=False)

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "callback_context_export_data, targets",
        [
            ([["scatter_chart", "box_chart"], None, None, None], None),
            ([["scatter_chart", "box_chart"], None, None, None], []),
        ],
        indirect=["callback_context_export_data"],
    )
    def test_graphs_false_targets(self, callback_context_export_data, targets, gapminder_2007):
        # Add action to relevant component
        model_manager["button"].actions = [vm.Action(id="test_action", function=export_data(targets=targets))]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["download-dataframe_scatter_chart"]["filename"] == "scatter_chart.csv"
        assert result["download-dataframe_scatter_chart"]["content"] == gapminder_2007.to_csv(index=False)

        assert result["download-dataframe_box_chart"]["filename"] == "box_chart.csv"
        assert result["download-dataframe_box_chart"]["content"] == gapminder_2007.to_csv(index=False)

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize("callback_context_export_data", [(["scatter_chart"], None, None, None)], indirect=True)
    def test_one_target(self, callback_context_export_data, gapminder_2007):
        # Add action to relevant component
        model_manager["button"].actions = [vm.Action(id="test_action", function=export_data(targets=["scatter_chart"]))]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["download-dataframe_scatter_chart"]["filename"] == "scatter_chart.csv"
        assert result["download-dataframe_scatter_chart"]["content"] == gapminder_2007.to_csv(index=False)

        assert "download-dataframe_box_chart" not in result

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "callback_context_export_data", [(["scatter_chart", "box_chart"], None, None, None)], indirect=True
    )
    def test_multiple_targets(self, callback_context_export_data, gapminder_2007):
        # Add action to relevant component
        model_manager["button"].actions = [
            vm.Action(id="test_action", function=export_data(targets=["scatter_chart", "box_chart"]))
        ]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["download-dataframe_scatter_chart"]["filename"] == "scatter_chart.csv"
        assert result["download-dataframe_scatter_chart"]["content"] == gapminder_2007.to_csv(index=False)

        assert result["download-dataframe_box_chart"]["filename"] == "box_chart.csv"
        assert result["download-dataframe_box_chart"]["content"] == gapminder_2007.to_csv(index=False)

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize("callback_context_export_data", [(["invalid_target_id"], None, None, None)], indirect=True)
    def test_invalid_target(
        self,
        callback_context_export_data,
    ):
        # Add action to relevant component
        model_manager["button"].actions = [
            vm.Action(id="test_action", function=export_data(targets=["invalid_target_id"]))
        ]

        with pytest.raises(ValueError, match="Component 'invalid_target_id' does not exist."):
            # Run action by picking the above added action function and executing it with ()
            model_manager["test_action"].function()

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "callback_context_export_data, " "target_scatter_filter_and_filter_interaction, " "target_box_filtered_pop",
        [
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], None, None],
                [[10**6, 10**7], None, None],
                [10**6, 10**7],
            ),
            ([["scatter_chart", "box_chart"], None, "Africa", None], [None, ["Africa"], None], None),
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], "Africa", None],
                [[10**6, 10**7], ["Africa"], None],
                [10**6, 10**7],
            ),
        ],
        indirect=True,
    )
    def test_multiple_targets_with_filter_and_filter_interaction(
        self,
        callback_context_export_data,
        target_scatter_filter_and_filter_interaction,
        target_box_filtered_pop,
    ):
        # Creating and adding a Filter object to the existing Page
        pop_filter = vm.Filter(column="pop", selector=vm.RangeSlider(id="pop_filter"))
        model_manager["test_page"].controls = [pop_filter]
        # Adds a default _filter Action to the filter selector objects
        pop_filter.pre_build()

        # Add filter_interaction Action to scatter_chart component
        model_manager["box_chart"].actions = [
            vm.Action(id="filter_interaction", function=filter_interaction(targets=["scatter_chart"]))
        ]

        # Add export_data action to relevant component
        model_manager["button"].actions = [
            vm.Action(id="test_action", function=export_data(targets=["scatter_chart", "box_chart"]))
        ]

        # Run action by picking the above added export_data action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["download-dataframe_scatter_chart"]["filename"] == "scatter_chart.csv"
        assert result["download-dataframe_scatter_chart"][
            "content"
        ] == target_scatter_filter_and_filter_interaction.to_csv(index=False)

        assert result["download-dataframe_box_chart"]["filename"] == "box_chart.csv"
        assert result["download-dataframe_box_chart"]["content"] == target_box_filtered_pop.to_csv(index=False)

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_table_one_button")
    @pytest.mark.parametrize(
        "callback_context_export_data, " "target_scatter_filter_and_filter_interaction, " "target_box_filtered_pop",
        [
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], None, "Algeria"],
                [[10**6, 10**7], None, ["Algeria"]],
                [10**6, 10**7],
            ),
            ([["scatter_chart", "box_chart"], None, "Africa", "Algeria"], [None, ["Africa"], ["Algeria"]], None),
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], "Africa", "Algeria"],
                [[10**6, 10**7], ["Africa"], ["Algeria"]],
                [10**6, 10**7],
            ),
        ],
        indirect=True,
    )
    def test_multiple_targets_with_filter_and_filter_interaction_and_table(
        self,
        callback_context_export_data,
        target_scatter_filter_and_filter_interaction,
        target_box_filtered_pop,
    ):
        # Creating and adding a Filter object to the existing Page
        pop_filter = vm.Filter(column="pop", selector=vm.RangeSlider(id="pop_filter"))
        model_manager["test_page"].controls = [pop_filter]
        # Adds a default _filter Action to the filter selector objects
        pop_filter.pre_build()

        # Add filter_interaction Action to scatter_chart component
        model_manager["box_chart"].actions = [
            vm.Action(id="filter_interaction", function=filter_interaction(targets=["scatter_chart"]))
        ]

        # Add table filter_interaction Action to scatter_chart component
        model_manager["vizro_table"].actions = [vm.Action(function=filter_interaction(targets=["scatter_chart"]))]
        model_manager["vizro_table"].pre_build()

        # Add export_data action to relevant component
        model_manager["button"].actions = [
            vm.Action(id="test_action", function=export_data(targets=["scatter_chart", "box_chart"]))
        ]

        # Run action by picking the above added export_data action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["download-dataframe_scatter_chart"]["filename"] == "scatter_chart.csv"
        assert result["download-dataframe_scatter_chart"][
            "content"
        ] == target_scatter_filter_and_filter_interaction.to_csv(index=False)

        assert result["download-dataframe_box_chart"]["filename"] == "box_chart.csv"
        assert result["download-dataframe_box_chart"]["content"] == target_box_filtered_pop.to_csv(index=False)
