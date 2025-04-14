import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px

iris = px.data.iris()

homepage = vm.Page(
    title=cnst.HOME_PAGE,
    id=cnst.HOME_PAGE_ID,
    layout=vm.Grid(grid=[[0, 4], [1, 4], [2, 4], [3, 4]]),
    components=[
        vm.Card(
            text="""
                # This is an <h1> tag
                ## This is an <h2> tag
                ###### This is an <h6> tag
                \n
                >
                > Block quotes are used to highlight text.
                >
                \n
                * Item 1
                * Item 2
                \n
                 *This text will be italic*
                _This will also be italic_
                **This text will be bold**
                _You **can** combine them_
            """,
        ),
        vm.Card(
            text="""
            ![icon-top](assets/images/icons/content/hypotheses.svg)

            Leads to the filters page on click.
            """,
            href=cnst.FILTERS_PAGE_PATH,
        ),
        vm.Card(
            text="""
            ![icon-top](assets/images/icons/content/features.svg)

            Leads to the datepicker page on click.
            """,
            href=f"/{cnst.DATEPICKER_PAGE}",
        ),
        vm.Card(
            text="""
            ![icon-top](assets/images/icons/content/hypotheses.svg)

            Leads to the 404 page on click.
            """,
            href=cnst.PAGE_404_PATH,
        ),
        vm.Graph(
            id=cnst.AREA_GRAPH_ID,
            figure=px.area(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(id=cnst.DROPDOWN_FILTER_HOMEPAGEPAGE)),
    ],
)
