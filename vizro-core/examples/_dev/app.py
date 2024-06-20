"""Dev app to try things out."""

import vizro.models as vm
from vizro import Vizro

page = vm.Page(
    title="Card with icon",
    components=[
        vm.Card(
            text="""
            ![](assets/images/icons/hypotheses.svg#icon-top)

            ### Card Title

            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut fringilla dictum lacus eget fringilla.
            Maecenas in various nibh, quis venenatis nulla. Integer et libero ultrices, scelerisque velit sed.
            """,
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
