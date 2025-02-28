import dash_bootstrap_components as dbc
import e2e.vizro.constants as cnst
from dash import get_asset_url, html
from pages.homepage import homepage
from pages.kpi_indicators_page import kpi_indicators_page

import vizro.models as vm
from vizro import Vizro

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[
        homepage,
        kpi_indicators_page,
    ],
    navigation=vm.Navigation(
        pages={
            cnst.GENERAL_ACCORDION: [cnst.HOME_PAGE_ID],
            cnst.KPI_ACCORDION: [cnst.KPI_INDICATORS_PAGE],
        },
        nav_selector=vm.NavBar(),
    ),
)

app = Vizro(assets_folder="../assets").build(dashboard)
app.dash.layout.children.append(
    dbc.NavLink(
        [
            "Made with ",
            html.Img(src=get_asset_url("banner.svg"), id="banner", alt="Vizro logo"),
            "vizro",
        ],
        href="https://github.com/mckinsey/vizro",
        target="_blank",
        className="anchor-container",
    )
)

if __name__ == "__main__":
    app.run(debug=True)
