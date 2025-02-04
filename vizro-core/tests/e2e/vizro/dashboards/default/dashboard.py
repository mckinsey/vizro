import e2e.vizro.constants as cnst
from pages.ag_grid_page import ag_grid_page
from pages.datepicker_page import datepicker_page
from pages.filters_page import filters_page
from pages.homepage import homepage
from pages.kpi_indicators_page import kpi_indicators_page
from pages.parameters_page import parameters_page

import vizro.models as vm
from vizro import Vizro

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[homepage, filters_page, parameters_page, kpi_indicators_page, datepicker_page, ag_grid_page],
    navigation=vm.Navigation(
        pages={
            cnst.GENERAL_ACCORDION: [
                cnst.HOME_PAGE_ID,
                cnst.FILTERS_PAGE,
                cnst.PARAMETERS_PAGE,
                cnst.KPI_INDICATORS_PAGE,
            ],
            cnst.DATEPICKER_ACCORDION: [cnst.DATEPICKER_PAGE],
            cnst.AG_GRID_ACCORDION: [cnst.TABLE_AG_GRID_PAGE],
        }
    ),
    theme="vizro_light",
)

app = Vizro(assets_folder="../assets").build(dashboard)

if __name__ == "__main__":
    app.run(debug=True)
