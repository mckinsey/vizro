import dash_bootstrap_components as dbc
import e2e.vizro.constants as cnst
from dash import get_asset_url, html
from pages.filter_interactions_page import filter_interactions_page
from pages.filters_page import filters_page
from pages.homepage import homepage
from pages.parameters_page import parameters_page

import vizro.models as vm
from vizro import Vizro

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[
        homepage,
        filters_page,
        parameters_page,
        filter_interactions_page,
    ],
    navigation=vm.Navigation(
        pages=[
            cnst.HOME_PAGE_ID,
            cnst.FILTERS_PAGE,
            cnst.PARAMETERS_PAGE,
            cnst.FILTER_INTERACTIONS_PAGE,
        ],
        nav_selector=vm.NavBar(),
    ),
    theme="vizro_light",
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
