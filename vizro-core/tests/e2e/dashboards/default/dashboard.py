import e2e_constants as cnst
from dashboard_pages import ag_grid_page, datepicker_page, filters_page, homepage, kpi_indicators_page, parameters_page

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
