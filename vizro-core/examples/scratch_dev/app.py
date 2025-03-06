"""Example app from the official vizro user tutorial.

See: https://vizro.readthedocs.io/en/stable/pages/tutorials/explore-components/
"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


tips = px.data.tips()

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
        vm.Card(text="""
               # Lorem Ipsum

               Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit. 
               In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum. 
               Nam ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum. 
           """) for i in range(6)],
)


page4 = vm.Page(
    title="Flex - gap",
    layout=vm.Flex(gap="40px"),
    components=[
        vm.Card(text="""
            # Lorem Ipsum

            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit. 
            In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum. 
            Nam ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum. 
        """) for i in range(6)],
)

page5 = vm.Page(
    title="Flex - row",
    layout=vm.Flex(direction="row"),
    components=[
        vm.Card(text="""
            # Lorem Ipsum

            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit. 
            In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum. 
            Nam ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum. 
        """) for i in range(6)],
)

page6 = vm.Page(
    id="page-flex-wrap-row",
    title="Flex - row/wrap",
    layout=vm.Flex(direction="row", wrap=True),
    components=[
        vm.Card(text="""
            # Lorem Ipsum

            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit. 
            In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum. 
            Nam ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum. 
        """) for i in range(6)],
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

page12 = vm.Page(
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

page13 = vm.Page(
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

dashboard = vm.Dashboard(
    pages=[page1, page2, page3, page4, page5, page6, page7, page8, page9, page10,
           page11, page12, page13],
    title="Test out Flex/Grid",
)




if __name__ == "__main__":
    Vizro().build(dashboard).run()
