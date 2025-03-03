import e2e.vizro.constants as cnst
from pages.datepicker_page import datepicker_page
from pages.kpi_indicators_page import kpi_indicators_page
from pages.table_page import table_page

import vizro.models as vm
from vizro import Vizro

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[
        table_page,
        kpi_indicators_page,
        datepicker_page,
    ],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(
                    pages={
                        # configured accordion here to see that it is not shown with one page inside
                        cnst.AG_GRID_ACCORDION: [
                            cnst.TABLE_PAGE,
                        ],
                    },
                    icon="Arrow Back IOS",
                    label="Text to be used for Arrow Back IOS icon description",
                ),
                vm.NavLink(
                    pages={
                        cnst.GENERAL_ACCORDION: [
                            cnst.KPI_INDICATORS_PAGE,
                            cnst.DATEPICKER_PAGE,
                        ],
                    },
                    icon="Bolt",
                    label="Text to be used for Bolt icon description",
                ),
            ]
        )
    ),
    theme="vizro_light",
)

app = Vizro(assets_folder="../assets").build(dashboard)

if __name__ == "__main__":
    app.run(debug=True)
