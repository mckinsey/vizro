import e2e.vizro.constants as cnst
import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import export_data

iris = px.data.iris()
iris["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(iris), freq="D")

extras_page = vm.Page(
    title=cnst.EXTRAS_PAGE,
    description=vm.Tooltip(
        text=cnst.PAGE_TOOLTIP_TEXT,
        icon=cnst.PAGE_TOOLTIP_ICON,
    ),
    components=[
        vm.Container(
            title="container",
            description=vm.Tooltip(
                text=cnst.CONTAINER_TOOLTIP_TEXT,
                icon=cnst.CONTAINER_TOOLTIP_ICON,
            ),
            extra={"class_name": "bg-container", "fluid": False, "style": {"height": "900px"}},
            components=[
                vm.Graph(
                    title="graph title",
                    description=vm.Tooltip(
                        text=cnst.GRAPH_TOOLTIP_TEXT,
                        icon=cnst.GRAPH_TOOLTIP_ICON,
                    ),
                    figure=px.line(
                        iris,
                        x="sepal_length",
                        y="petal_width",
                        color="sepal_width",
                    ),
                ),
                vm.Card(
                    text="""
    ![icon-top](assets/images/icons/content/features.svg)

    Leads to the home page on click.
    """,
                    href="/",
                    extra={"style": {"backgroundColor": "#377a6b"}},
                ),
                vm.Button(
                    text="Export data",
                    extra={"color": "success", "outline": True},
                    actions=[
                        vm.Action(
                            function=export_data(
                                file_format="csv",
                            )
                        ),
                    ],
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                description=vm.Tooltip(
                    text=cnst.DROPDOWN_TOOLTIP_TEXT,
                    icon=cnst.DROPDOWN_TOOLTIP_ICON,
                    extra={"style": {"width": "150px"}},
                ),
                extra={"clearable": True, "placeholder": "Select an option...", "style": {"width": "150px"}},
            ),
        ),
        vm.Filter(
            column="species",
            selector=vm.RadioItems(
                description=cnst.RADIOITEMS_TOOLTIP_TEXT,
                options=["setosa", "versicolor", "virginica"],
                extra={"inline": True},
            ),
        ),
        vm.Filter(
            column="species",
            selector=vm.Checklist(
                description=vm.Tooltip(
                    text=cnst.CHECKLIST_TOOLTIP_TEXT,
                    icon=cnst.CHECKLIST_TOOLTIP_ICON,
                ),
                options=["setosa", "versicolor", "virginica"],
                extra={"switch": True, "inline": True},
            ),
        ),
        vm.Filter(
            column="petal_width",
            selector=vm.Slider(
                description=vm.Tooltip(
                    text=cnst.SLIDER_TOOLTIP_TEXT,
                    icon=cnst.SLIDER_TOOLTIP_ICON,
                ),
                step=0.5,
                extra={"tooltip": {"placement": "bottom", "always_visible": True}},
            ),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.RangeSlider(
                description=vm.Tooltip(
                    text=cnst.RANGESLIDER_TOOLTIP_TEXT,
                    icon=cnst.RANGESLIDER_TOOLTIP_ICON,
                ),
                step=1.0,
                extra={
                    "tooltip": {"placement": "bottom", "always_visible": True},
                    "pushable": 20,
                },
            ),
        ),
        vm.Filter(
            column="date_column",
            selector=vm.DatePicker(
                description=vm.Tooltip(
                    text=cnst.DATEPICKER_TOOLTIP_TEXT,
                    icon=cnst.DATEPICKER_TOOLTIP_ICON,
                ),
                title="Custom styled date picker",
                range=False,
                extra={
                    "size": "lg",
                    "valueFormat": "YYYY/MM/DD",
                    "placeholder": "Select a date",
                },
            ),
        ),
    ],
)
