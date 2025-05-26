"""Custom filter action."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture


@capture("action")
def custom_action(value):
    return str(value)


df = px.data.iris()


page = vm.Page(
    title="Charts UI",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
        vm.Card(id="card-id", text="Blah"),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.RadioItems(
                id="radio_items",
                options=[1, 2, 3],
                actions=[
                    # Action is defined in the old fashion way so that the example can be easily reused with the
                    # vizro==0.1.37 (Checkout to -> c01752a000d1b8a70fd310775358825215794fc7) to prove that it works.
                    vm.Action(
                        function=custom_action(),
                        inputs=["radio_items.value"],
                        outputs=["card-id.children"],
                    )
                ],
            ),
        ),
    ],
    controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")],
)


page24 = vm.Page(
    title="Page with tabs and content- grid",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="tab1",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.Card(text="This is card inside first tab!"),
                        vm.Graph(figure=px.histogram(tips, x="tip")),
                    ],
                ),
                vm.Container(
                    title="tab2",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.Card(text="This is card inside second tab!"),
                        vm.Graph(figure=px.bar(tips, y="tip", x="day")),
                    ],
                ),
            ]
        ),
        vm.Card(text="This is card below the tabs!"),
        vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day", box=True)),
    ],
)


page25 = vm.Page(
    title="FlexItem - dimension - graphs",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day", box=True, width=300)) for i in range(6)],
)

page26 = vm.Page(
    title="FlexItem - dimension - tables",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.Table(figure=dash_data_table(tips, style_table={"width": "1000px"})) for i in range(3)],
)

page27 = vm.Page(
    title="FlexItem - dimension - aggrid",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.AgGrid(figure=dash_ag_grid(tips, style={"width": 1000})) for i in range(3)],
)

dashboard = vm.Dashboard(pages=[page])


Vizro().build(dashboard).run()
