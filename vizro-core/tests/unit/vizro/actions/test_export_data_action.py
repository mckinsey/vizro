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
def target_scatter_filtered_pop_filter_interaction_continent(request, gapminder_2007):
    pop_filter, continent_filter_interaction = request.param
    data = gapminder_2007
    if pop_filter:
        data = data[data["pop"].between(pop_filter[0], pop_filter[1], inclusive="both")]
    if continent_filter_interaction:
        data = data[data["continent"].isin(continent_filter_interaction)]
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
    """Mock dash.callback_context that represents on page load."""
    targets, pop_filter, continent_filter_interaction = request.param
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
            "filter_interaction": [
                CallbackTriggerDict(
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
            ]
            if continent_filter_interaction
            else [],
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
    @pytest.mark.parametrize("callback_context_export_data", [([[], None, None])], indirect=True)
    def test_no_graphs_no_targets(self, callback_context_export_data):
        # Add action to relevant component
        model_manager["button"].actions = [vm.Action(id="test_action", function=export_data())]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result == {}

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "callback_context_export_data", [([["scatter_chart", "box_chart"], None, None])], indirect=True
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
    @pytest.mark.parametrize("callback_context_export_data", [(["scatter_chart"], None, None)], indirect=True)
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
        "callback_context_export_data", [(["scatter_chart", "box_chart"], None, None)], indirect=True
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
    @pytest.mark.parametrize("callback_context_export_data", [(["invalid_target_id"], None, None)], indirect=True)
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
        "callback_context_export_data, "
        "target_scatter_filtered_pop_filter_interaction_continent, "
        "target_box_filtered_pop",
        [
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], None],
                [[10**6, 10**7], None],
                [10**6, 10**7],
            ),
            ([["scatter_chart", "box_chart"], None, "Africa"], [None, ["Africa"]], None),
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], "Africa"],
                [[10**6, 10**7], ["Africa"]],
                [10**6, 10**7],
            ),
        ],
        indirect=True,
    )
    def test_multiple_targets_with_filter_and_filter_interaction(
        self,
        callback_context_export_data,
        target_scatter_filtered_pop_filter_interaction_continent,
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
        ] == target_scatter_filtered_pop_filter_interaction_continent.to_csv(index=False)

        assert result["download-dataframe_box_chart"]["filename"] == "box_chart.csv"
        assert result["download-dataframe_box_chart"]["content"] == target_box_filtered_pop.to_csv(index=False)

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "callback_context_export_data", [(["scatter_chart", "box_chart"], None, None)], indirect=True
    )
    def test_invalid_file_format(
        self,
        callback_context_export_data,
    ):
        # Add action to relevant component
        model_manager["button"].actions = [
            vm.Action(
                id="test_action",
                function=export_data(
                    targets=["scatter_chart", "box_chart"],
                    file_format="invalid_file_format",
                ),
            )
        ]

        with pytest.raises(
            ValueError, match='Unknown "file_format": invalid_file_format.' ' Known file formats: "csv", "xlsx".'
        ):
            # Run action by picking the above added action function and executing it with ()
            model_manager["test_action"].function()
