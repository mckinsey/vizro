import e2e.vizro.constants as cnst
from pages.ag_grid_page import ag_grid_page
from pages.datepicker_page import datepicker_page
from pages.dynamic_data_page import dynamic_data_page
from pages.dynamic_filters_pages import dynamic_filters_categorical_page, dynamic_filters_numerical_page
from pages.filter_interactions_page import filter_interactions_page
from pages.filters_page import filters_page
from pages.homepage import homepage
from pages.kpi_indicators_page import kpi_indicators_page
from pages.parameters_page import parameters_page
from pages.table_interactions_page import table_interactions_page
from pages.table_page import table_page

import vizro.models as vm
from vizro import Vizro

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[
        homepage,
        filters_page,
        parameters_page,
        filter_interactions_page,
        kpi_indicators_page,
        datepicker_page,
        ag_grid_page,
        table_page,
        table_interactions_page,
        dynamic_data_page,
        dynamic_filters_categorical_page,
        dynamic_filters_numerical_page,
    ],
    navigation=vm.Navigation(
        pages={
            cnst.GENERAL_ACCORDION: [
                cnst.HOME_PAGE_ID,
                cnst.FILTERS_PAGE,
                cnst.PARAMETERS_PAGE,
                cnst.FILTER_INTERACTIONS_PAGE,
                cnst.KPI_INDICATORS_PAGE,
            ],
            cnst.DATEPICKER_ACCORDION: [cnst.DATEPICKER_PAGE],
            cnst.AG_GRID_ACCORDION: [cnst.TABLE_PAGE, cnst.TABLE_INTERACTIONS_PAGE, cnst.TABLE_AG_GRID_PAGE],
            cnst.DYNAMIC_DATA_ACCORDION: [
                cnst.DYNAMIC_DATA_PAGE,
                cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
                cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
            ],
        }
    ),
    theme="vizro_light",
)

app = Vizro(assets_folder="../assets").build(dashboard)

if __name__ == "__main__":
    app.run(debug=True)
