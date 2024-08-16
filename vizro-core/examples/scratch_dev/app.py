"""Dev app to try things out."""

import vizro.models as vm
from vizro import Vizro

# To check whether we need Roboto Mono
page = vm.Page(
    title="Page",
    components=[
        vm.Card(
            text="""

               Inline code snippet: `my_bool = True`

                Block code snippet:
                ```python

                def sum(a, b):
                    return a+b

                sum(2,2)

                ```

               """
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
