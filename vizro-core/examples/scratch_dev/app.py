"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card
from vizro.tables import dash_ag_grid, dash_data_table

tips = px.data.tips()


justify_options = [
    "flex-start",
    "flex-end",
    "center",
    "space-between",
    "space-around",
    "space-evenly",
]

align_options = ["flex-start", "flex-end", "center", "stretch"]


page0 = vm.Page(
    title="Different justification option",
    layout=vm.Flex(direction="column"),
    components=[
        vm.Container(
            layout=vm.Flex(direction="row", extra={"justify": justify, "align": align}),
            title=f"{justify=} {align=}",
            components=[vm.Card(text="text")] * 2 + [vm.Card(text="text\n\ntext")],
        )
        for justify in justify_options
        for align in align_options
    ],
)


page1 = vm.Page(
    title="Default",
    components=[
        vm.Card(text="""# Good morning!"""),
        vm.Graph(
            title="Where do we get more tips?",
            figure=px.bar(tips, y="tip", x="day"),
        ),
        vm.Graph(
            title="Is the average driven by a few outliers?",
            figure=px.violin(tips, y="tip", x="day", color="day", box=True),
        ),
        vm.Graph(
            title="Which group size is more profitable?",
            figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
        ),
    ],
    controls=[vm.Filter(column="day")],
)

page2 = vm.Page(
    title="Grid",
    layout=vm.Layout(grid=[[0, -1], [1, 2], [3, 3]]),
    components=[
        vm.Card(text="""# Good morning!"""),
        vm.Graph(
            title="Where do we get more tips?",
            figure=px.bar(tips, y="tip", x="day"),
        ),
        vm.Graph(
            title="Is the average driven by a few outliers?",
            figure=px.violin(tips, y="tip", x="day", color="day", box=True),
        ),
        vm.Graph(
            title="Which group size is more profitable?",
            figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
        ),
    ],
    controls=[vm.Filter(column="day")],
)


page3 = vm.Page(
    title="Flex - default",
    layout=vm.Flex(),
    components=[
        vm.Card(
            text="""
               # Lorem Ipsum

               Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit.
               In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum.
               Name ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum.
           """
        )
        for i in range(6)
    ],
)


page4 = vm.Page(
    title="Flex - gap",
    layout=vm.Flex(gap="40%"),
    components=[
        vm.Card(
            text="""
            # Lorem Ipsum

            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit.
            In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum.
            Name ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum.
        """
        )
        for i in range(6)
    ],
)

page5 = vm.Page(
    title="Flex - row",
    layout=vm.Flex(direction="row"),
    components=[
        vm.Card(
            text="""
            # Lorem Ipsum

            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit.
            In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum.
            Name ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum.
        """
        )
        for i in range(6)
    ],
)

page6 = vm.Page(
    id="page-flex-wrap-row",
    title="Flex - row/wrap",
    layout=vm.Flex(direction="row", wrap=True),
    components=[
        vm.Card(
            text="""
            # Lorem Ipsum

            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit.
            In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum.
            Name ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum.
        """
        )
        for i in range(6)
    ],
)

page7 = vm.Page(
    title="Flex - default - graphs",
    layout=vm.Flex(),
    components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day", box=True)) for i in range(6)],
)


page8 = vm.Page(
    title="Flex - gap - graphs",
    layout=vm.Flex(gap="40px"),
    components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day", box=True)) for i in range(6)],
)

page9 = vm.Page(
    title="Flex - row - graphs",
    layout=vm.Flex(direction="row"),
    components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day", box=True)) for i in range(6)],
)

page10 = vm.Page(
    id="page-flex-wrap-row-graphs",
    title="Flex - row/wrap - graphs",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day", box=True)) for i in range(6)],
)

page11 = vm.Page(
    title="Flex - default - aggrid",
    layout=vm.Flex(),
    components=[vm.AgGrid(figure=dash_ag_grid(tips)) for i in range(3)],
)


page12 = vm.Page(
    title="Flex - gap - aggrid",
    layout=vm.Flex(gap="40px"),
    components=[vm.AgGrid(figure=dash_ag_grid(tips)) for i in range(3)],
)

page13 = vm.Page(
    title="Flex - row - aggrid",
    layout=vm.Flex(direction="row"),
    components=[vm.AgGrid(figure=dash_ag_grid(tips)) for i in range(3)],
)

page14 = vm.Page(
    title="Flex - default - table",
    layout=vm.Flex(),
    components=[vm.Table(figure=dash_data_table(tips)) for i in range(3)],
)


page15 = vm.Page(
    title="Flex - gap - table",
    layout=vm.Flex(gap="40px"),
    components=[vm.Table(figure=dash_data_table(tips)) for i in range(3)],
)

page16 = vm.Page(
    title="Flex - row - table",
    layout=vm.Flex(direction="row"),
    components=[vm.Table(figure=dash_data_table(tips)) for i in range(3)],
)

page17 = vm.Page(
    title="Flex - default - button",
    layout=vm.Flex(),
    components=[vm.Button() for i in range(9)],
)


page18 = vm.Page(
    title="Flex - gap - button",
    layout=vm.Flex(gap="40px"),
    components=[vm.Button() for i in range(9)],
)

page19 = vm.Page(
    title="Flex - row - button",
    layout=vm.Flex(direction="row"),
    components=[vm.Button() for i in range(9)],
)


page20 = vm.Page(
    title="Flex - Graphs with Card",
    layout=vm.Flex(),
    components=[
        vm.Card(text="""# Good morning!"""),
        vm.Graph(
            title="Where do we get more tips?",
            figure=px.bar(tips, y="tip", x="day"),
        ),
        vm.Graph(
            title="Is the average driven by a few outliers?",
            figure=px.violin(tips, y="tip", x="day", color="day", box=True),
        ),
        vm.Graph(
            title="Which group size is more profitable?",
            figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
        ),
    ],
    controls=[vm.Filter(column="day")],
)

page21 = vm.Page(
    title="Flex - Container",
    components=[
        vm.Container(
            title="Container inside grid with Flex",
            layout=vm.Flex(),
            components=[
                vm.Graph(
                    title="Where do we get more tips?",
                    figure=px.bar(tips, y="tip", x="day"),
                ),
                vm.Graph(
                    title="Is the average driven by a few outliers?",
                    figure=px.violin(tips, y="tip", x="day", color="day", box=True),
                ),
                vm.Graph(
                    title="Which group size is more profitable?",
                    figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
                ),
            ],
        )
    ],
    controls=[vm.Filter(column="day")],
)

page22 = vm.Page(
    title="Flex - Container with card",
    components=[
        vm.Container(
            title="Container inside grid with Flex with card",
            layout=vm.Flex(),
            components=[
                vm.Card(text="""# Good morning!"""),
                vm.Graph(
                    title="Where do we get more tips?",
                    figure=px.bar(tips, y="tip", x="day"),
                ),
                vm.Graph(
                    title="Is the average driven by a few outliers?",
                    figure=px.violin(tips, y="tip", x="day", color="day", box=True),
                ),
                vm.Graph(
                    title="Which group size is more profitable?",
                    figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
                ),
            ],
        )
    ],
    controls=[vm.Filter(column="day")],
)

page23 = vm.Page(
    id="page-flex-inside-flex",
    title="Flex inside flex",
    layout=vm.Flex(),
    components=[
        vm.Container(
            title="KPI Banner",
            layout=vm.Flex(direction="row"),
            components=[
                vm.Figure(
                    figure=kpi_card(
                        data_frame=tips,
                        value_column="total_bill",
                        agg_func="mean",
                        value_format="${value:.2f}",
                        title="Average Bill",
                    )
                )
                for i in range(4)
            ],
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Total Bill ($)",
                    components=[
                        vm.Graph(figure=px.histogram(tips, x="total_bill")),
                    ],
                ),
                vm.Container(
                    title="Total Tips ($)",
                    components=[
                        vm.Graph(figure=px.histogram(tips, x="tip")),
                    ],
                ),
            ],
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


dashboard = vm.Dashboard(
    pages=[
        page0,
        page1,
        page2,
        page3,
        page4,
        page5,
        page6,
        page7,
        page8,
        page9,
        page10,
        page11,
        page12,
        page13,
        page14,
        page15,
        page16,
        page17,
        page18,
        page19,
        page20,
        page21,
        page22,
        page23,
        page24,
        page25,
        page26,
        page27,
    ],
    title="Test out Flex/Grid",
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
