import dash_bootstrap_components as dbc
import pandas as pd

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
from vizro.figures import kpi_card, kpi_card_reference
from vizro.actions import set_control
from vizro.models.types import capture


df = px.data.iris()
df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})


example_cards = [
    kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value"),
    kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with aggregation", agg_func="median"),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI with formatting",
        value_format="${value:.2f}",
    ),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI with icon",
        icon="Shopping Cart",
    ),
]

example_reference_cards = [
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI reference (pos)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        agg_func="median",
        title="KPI reference (neg)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI reference with formatting",
        value_format="{value:.2f}€",
        reference_format="{delta:+.2f}€ vs. last year ({reference:.2f}€)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI reference with icon",
        icon="Shopping Cart",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI reference (reverse color)",
        reverse_color=True,
    ),
]

page_1 = vm.Page(
    title="KPI cards",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.Figure(figure=figure) for figure in example_cards + example_reference_cards],
)


@capture("action")
def custom_action(_trigger):
    return f"The card is clicked: {_trigger} times."


page_2 = vm.Page(
    title="KPI cards trigger custom action",
    layout=vm.Flex(direction="row", wrap=True),
    components=[
        vm.Figure(
            figure=kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value"),
            actions=vm.Action(function=custom_action(), outputs="text_output")
        ),
        vm.Text(id="text_output", text="Click a card to see the action output here."),
    ],
)


page_3 = vm.Page(
    title="KPI cards trigger set_control",
    layout=vm.Flex(direction="row", wrap=True),
    components=[
        vm.Figure(
            figure=kpi_card(data_frame=df_kpi[df_kpi["Category"] == "A"], value_column="Actual", title="Actual for A"),
            actions=set_control(control="filter-id-1", value="A"),
        ),
        vm.Figure(
            figure=kpi_card(data_frame=df_kpi[df_kpi["Category"] == "B"], value_column="Actual", title="Actual for B"),
            actions=set_control(control="filter-id-1", value="B"),
        ),
        vm.Figure(
            figure=kpi_card(data_frame=df_kpi[df_kpi["Category"] == "C"], value_column="Actual", title="Actual for C"),
            actions=set_control(control="filter-id-1", value="C"),
        ),
        vm.Graph(
            id="graph-1",
            figure=px.bar(
                df_kpi, x="Category", y="Actual", color="Category",
                color_discrete_map={"A": "#00b4ff", "B": "#ff9222", "C": "#3949ab"}
            )
        )
    ],
    controls=[
        vm.Filter(id="filter-id-1", column="Category", targets=["graph-1"])
    ]
)


@capture("figure")
def button_as_figure(data_frame):
    return dbc.Button(children=f"Graph below shows {len(data_frame)} rows. Click to trigger two actions", color="primary", class_name="m-2")


page_4 = vm.Page(
    title="Custom button as a figure",
    components=[
        vm.Figure(
            id="figure-2",
            figure=button_as_figure(df),
            actions=[
                set_control(control="filter-id-2", value="setosa"),
                vm.Action(function=custom_action(), outputs="text-2")
            ],
        ),
        vm.Text(id="text-2", text="Click the button to see the action output here."),
        vm.Graph(
            id="graph-2",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")
        )
    ],
    controls=[
        vm.Filter(id="filter-id-2", column="species", targets=["graph-2", "figure-2"])
    ]
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4])
Vizro().build(dashboard).run()
