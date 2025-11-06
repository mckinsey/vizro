import e2e.vizro.constants as cnst
from pages.actions_properties_shortcut_page import (
    action_ag_grid_underlying_id_shortcut_page,
    action_control_shortcut_page,
    action_model_field_shortcut_page,
)
from pages.ag_grid_interactions_page import ag_grid_interactions_page
from pages.ag_grid_page import ag_grid_page
from pages.collapsible_containers_pages import collapsible_containers_flex, collapsible_containers_grid
from pages.container_pages import container_variants_page
from pages.custom_components_page import custom_components_page
from pages.datepicker_page import datepicker_page
from pages.datepicker_parameters_page import datepicker_parameters_page
from pages.dynamic_data_page import dynamic_data_df_parameter_page, dynamic_data_page
from pages.dynamic_filters_pages import (
    dynamic_filters_categorical_page,
    dynamic_filters_datepicker_page,
    dynamic_filters_numerical_page,
)
from pages.export_action_page import export_action_page
from pages.extras_page import extras_page
from pages.filter_and_param_page import filter_and_param_page
from pages.filter_interactions_page import filter_interactions_page
from pages.filters_inside_containters_page import filters_inside_containers_page
from pages.filters_page import filters_page
from pages.homepage import homepage
from pages.kpi_indicators_page import kpi_indicators_page
from pages.layout_pages import (
    buttons_page,
    layout_flex_with_all_params_and_card,
    layout_flex_with_direction_param_and_graph,
    layout_flex_with_gap_param_and_table,
    layout_flex_with_wrap_param_and_ag_grid,
    layout_flex_without_params,
)
from pages.parameters_multi_page import parameters_multi_page
from pages.parameters_page import parameters_page
from pages.set_control_cross_filter_page import (
    cross_filter_ag_grid_page,
    cross_filter_card_graph_page,
    cross_filter_graph_page,
)
from pages.set_control_drill_down import drill_down_graph_page
from pages.set_control_drill_through import (
    drill_through_filter_ag_grid_source_page,
    drill_through_filter_ag_grid_target_page,
    drill_through_filter_graph_source_page,
    drill_through_filter_graph_target_page,
    drill_through_parameter_graph_source_page,
    drill_through_parameter_graph_target_page,
)
from pages.switch_control_page import switch_control_page
from pages.table_interactions_page import table_interactions_page
from pages.table_page import table_page
from pages.vizro_url_and_download_page import vizro_url_and_download_page

import vizro.models as vm
from vizro import Vizro

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[
        homepage,
        filters_page,
        filters_inside_containers_page,
        parameters_page,
        parameters_multi_page,
        filter_interactions_page,
        switch_control_page,
        kpi_indicators_page,
        export_action_page,
        datepicker_page,
        datepicker_parameters_page,
        ag_grid_page,
        ag_grid_interactions_page,
        table_page,
        table_interactions_page,
        dynamic_data_page,
        dynamic_data_df_parameter_page,
        dynamic_filters_categorical_page,
        dynamic_filters_numerical_page,
        dynamic_filters_datepicker_page,
        custom_components_page,
        filter_and_param_page,
        container_variants_page,
        layout_flex_without_params,
        layout_flex_with_all_params_and_card,
        layout_flex_with_direction_param_and_graph,
        layout_flex_with_gap_param_and_table,
        layout_flex_with_wrap_param_and_ag_grid,
        extras_page,
        buttons_page,
        collapsible_containers_grid,
        collapsible_containers_flex,
        vizro_url_and_download_page,
        cross_filter_graph_page,
        cross_filter_ag_grid_page,
        cross_filter_card_graph_page,
        drill_down_graph_page,
        drill_through_filter_graph_source_page,
        drill_through_filter_graph_target_page,
        drill_through_parameter_graph_source_page,
        drill_through_parameter_graph_target_page,
        drill_through_filter_ag_grid_source_page,
        drill_through_filter_ag_grid_target_page,
        action_model_field_shortcut_page,
        action_ag_grid_underlying_id_shortcut_page,
        action_control_shortcut_page,
    ],
    navigation=vm.Navigation(
        pages={
            cnst.GENERAL_ACCORDION: [
                cnst.HOME_PAGE_ID,
                cnst.FILTERS_PAGE,
                cnst.FILTERS_INSIDE_CONTAINERS_PAGE,
                cnst.PARAMETERS_PAGE,
                cnst.PARAMETERS_MULTI_PAGE,
                cnst.FILTER_INTERACTIONS_PAGE,
                cnst.SWITCH_CONTROL_PAGE,
                cnst.KPI_INDICATORS_PAGE,
                cnst.EXPORT_PAGE,
                cnst.CUSTOM_COMPONENTS_PAGE,
                cnst.FILTER_AND_PARAM_PAGE,
                cnst.VIZRO_URL_AND_DOWNLOAD_PAGE,
            ],
            cnst.DATEPICKER_ACCORDION: [
                cnst.DATEPICKER_PAGE,
                cnst.DATEPICKER_PARAMS_PAGE,
            ],
            cnst.AG_GRID_ACCORDION: [
                cnst.TABLE_PAGE,
                cnst.TABLE_INTERACTIONS_PAGE,
                cnst.TABLE_AG_GRID_PAGE,
                cnst.TABLE_AG_GRID_INTERACTIONS_PAGE,
            ],
            cnst.DYNAMIC_DATA_ACCORDION: [
                cnst.DYNAMIC_DATA_PAGE,
                cnst.DYNAMIC_DATA_DF_PARAMETER_PAGE,
                cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
                cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
                cnst.DYNAMIC_FILTERS_DATEPICKER_PAGE,
            ],
            cnst.CONTAINER_ACCORDION: [cnst.CONTAINER_VARIANTS_PAGE],
            cnst.LAYOUT_ACCORDION: [
                cnst.LAYOUT_FLEX_DEFAULT,
                cnst.LAYOUT_FLEX_ALL_PARAMS,
                cnst.LAYOUT_FLEX_DIRECTION_AND_GRAPH,
                cnst.LAYOUT_FLEX_GAP_AND_TABLE,
                cnst.LAYOUT_FLEX_WRAP_AND_AG_GRID,
                cnst.EXTRAS_PAGE,
                cnst.BUTTONS_PAGE,
                cnst.COLLAPSIBLE_CONTAINERS_GRID,
                cnst.COLLAPSIBLE_CONTAINERS_FLEX,
            ],
            cnst.ACTIONS_ACCORDION: [
                cnst.SET_CONTROL_GRAPH_CROSS_FILTER_PAGE,
                cnst.SET_CONTROL_TABLE_AG_GRID_CROSS_FILTER_PAGE,
                cnst.SET_CONTROL_CARD_GRAPH_CROSS_FILTER_PAGE,
                cnst.SET_CONTROL_DRILL_THROUGH_FILTER_GRAPH_SOURCE,
                cnst.SET_CONTROL_DRILL_THROUGH_FILTER_GRAPH_TARGET,
                cnst.SET_CONTROL_DRILL_THROUGH_PARAMETER_GRAPH_SOURCE,
                cnst.SET_CONTROL_DRILL_THROUGH_PARAMETER_GRAPH_TARGET,
                cnst.SET_CONTROL_DRILL_THROUGH_FILTER_AG_GRID_SOURCE,
                cnst.SET_CONTROL_DRILL_THROUGH_FILTER_AG_GRID_TARGET,
                cnst.SET_CONTROL_DRILL_DOWN_GRAPH_PAGE,
                cnst.ACTION_MODEL_FIELD_SHORTCUT_PAGE,
                cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_PAGE,
                cnst.ACTION_CONTROL_SHORTCUT_PAGE,
            ],
        }
    ),
    theme="vizro_light",
)

app = Vizro(assets_folder="../assets").build(dashboard)

if __name__ == "__main__":
    app.run(debug=True)
