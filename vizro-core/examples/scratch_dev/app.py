"""Test app"""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

iris = px.data.iris()

page_home = vm.Page(
    title="Homepage",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Card(
            text="""
                        ### Paragraphs
                        Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                        Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                        Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                        Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.
                   """
        ),
        vm.Text(
            text="""
                        ### Paragraphs
                        Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                        Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                        Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                        Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.
                   """
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page_home])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
