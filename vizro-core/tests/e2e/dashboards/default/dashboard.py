from functools import partial

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
import yaml
from flask_caching import Cache
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.figures import kpi_card, kpi_card_reference
from vizro.managers import data_manager
from vizro.tables import dash_ag_grid, dash_data_table

import e2e_constants as cnst
from e2e_custom_feature_helpers.custom_actions.custom_actions import my_custom_action
from e2e_custom_feature_helpers.custom_charts.bar_custom import bar_with_highlight
from e2e_custom_feature_helpers.custom_components.new_dropdown import NewDropdown
from e2e_custom_feature_helpers.custom_components.range_slider_non_cross import RangeSliderNonCross

from dashboard_pages import homepage, filters_page, parameters_page, kpi_indicators_page, datepicker_page, ag_grid_page

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[
        homepage,
        filters_page,
        parameters_page,
        kpi_indicators_page,
        datepicker_page,
        ag_grid_page
    ],
    navigation=vm.Navigation(
        pages={
            cnst.GENERAL_ACCORDION: [
                cnst.HOME_PAGE_ID,
                cnst.FILTERS_PAGE,
                cnst.PARAMETERS_PAGE,
                cnst.KPI_INDICATORS_PAGE,
            ],
            cnst.DATEPICKER_ACCORDION: [
                cnst.DATEPICKER_PAGE
            ],
            cnst.AG_GRID_ACCORDION: [
                cnst.TABLE_AG_GRID_PAGE
            ],

        }
    ),
    theme="vizro_light",
)

app = Vizro(assets_folder="../assets").build(dashboard)

if __name__ == "__main__":
    app.run(debug=True)
