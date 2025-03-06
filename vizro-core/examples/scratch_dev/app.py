"""Example app from the official vizro user tutorial.

See: https://vizro.readthedocs.io/en/stable/pages/tutorials/explore-components/
"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


tips = px.data.tips()

page_one = vm.Page(
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

page_two = vm.Page(
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


page_three = vm.Page(
    title="Flex - default",
    layout=vm.Flex(),
    components=[vm.Card(text="""# Lorem Ipsum
    
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit. 
    In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum. 
    Nam ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum. 
    """) for i in range(6)],
)


page_four = vm.Page(
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

page_five = vm.Page(
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

page_six = vm.Page(
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


page_seven = vm.Page(
    title="Flex - Graphs",
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
    controls=[vm.Filter(column="day")],
)

page_eight = vm.Page(
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

page_nine = vm.Page(
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

page_ten = vm.Page(
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
    pages=[page_one, page_two, page_three, page_four, page_five, page_six, page_seven, page_eight, page_nine, page_ten],
    title="Test out Flex/Grid",
)




if __name__ == "__main__":
    Vizro().build(dashboard).run()
