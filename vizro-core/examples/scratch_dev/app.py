import vizro.models as vm
from vizro import Vizro


page = vm.Page(
    title="Text with extra argument",
    components=[
        vm.Text(
            text="""
              This example uses the block delimiter:
              $$
              \\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
              $$

              This example uses the inline delimiter:
              $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$
            """,
            extra={"mathjax": True},
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
