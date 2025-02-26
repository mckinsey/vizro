from custom_charts.table_custom import table_with_filtered_columns
from e2e.vizro import constants as cnst

import vizro.models as vm
import vizro.plotly.express as px

gapminder_2007 = px.data.gapminder().query("year == 2007")


parameters_multi_page = vm.Page(
    title=cnst.PARAMETERS_MULTI_PAGE,
    components=[
        vm.Table(
            id=cnst.TABLE_DROPDOWN,
            title="Dropdown",
            figure=table_with_filtered_columns(
                data_frame=gapminder_2007,
                chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"],
            ),
        ),
        vm.Table(
            id=cnst.TABLE_CHECKLIST,
            title="Checklist",
            figure=table_with_filtered_columns(
                data_frame=gapminder_2007,
                chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"],
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[f"{cnst.TABLE_CHECKLIST}.chosen_columns"],
            selector=vm.Checklist(id=cnst.CHECKLIST_PARAM, options=gapminder_2007.columns.to_list()),
        ),
        vm.Parameter(
            targets=[f"{cnst.TABLE_DROPDOWN}.chosen_columns"],
            selector=vm.Dropdown(
                id=cnst.DROPDOWN_PARAM_MULTI,
                options=gapminder_2007.columns.to_list(),
            ),
        ),
    ],
)
