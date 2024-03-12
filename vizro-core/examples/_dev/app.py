"""Rough example used by developers."""

"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

first_page = vm.Page(
    title="First Page",
    components=[
        vm.Graph(
            id="scatter_chart", figure=px.scatter(px.data.iris(), x="sepal_length", y="petal_width", color="species")
        ),
        vm.Graph(id="hist_chart", figure=px.histogram(px.data.iris(), x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
    ],
)

home = vm.Page(
    title="Homepage",
    components=[
        vm.Card(
            text="""
              ### No Href
              Lorem ipsum dolor sit amet consectetur adipisicing elit. Maxime mollitia,
              molestiae quas vel sint commodi repudiandae consequuntur voluptatum laborum
              numquam blanditiis harum quisquam eius sed odit fugiat iusto fuga praesentium
              option, eaque rerum!
          """,
        ),
        vm.Card(
            text="""
            ### /first-page
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Maxime mollitia,
            molestiae quas vel sint commodi repudiandae consequuntur voluptatum laborum
            numquam blanditiis harum quisquam eius sed odit fugiat iusto fuga praesentium
            option, eaque rerum!
        """,
            href="/first-page",
        ),
        vm.Card(
            text="""
            ### https
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Maxime mollitia,
            molestiae quas vel sint commodi repudiandae consequuntur voluptatum laborum
            numquam blanditiis harum quisquam eius sed odit fugiat iusto fuga praesentium
            option, eaque rerum!
            """,
            href="https://www.google.com",
        ),
        vm.Card(
            text="""
            ### http
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Maxime mollitia,
            molestiae quas vel sint commodi repudiandae consequuntur voluptatum laborum
            numquam blanditiis harum quisquam eius sed odit fugiat iusto fuga praesentium
            option, eaque rerum!
            """,
            href="http://www.google.com",
        ),
    ],
)


dashboard = vm.Dashboard(pages=[home, first_page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
