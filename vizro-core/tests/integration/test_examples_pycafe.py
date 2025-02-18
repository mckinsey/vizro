import re

from playwright.sync_api import Page, expect


class TestExamplesPycafe:
    def test_render_pycafe(self, page: Page):
        url = "https://py.cafe/snippet/vizro/v1?#code=%23%20Vizro%20is%20an%20open-source%20toolkit%20for%20creating%20modular%20data%20visualization%20applications.%0A%23%20check%20out%20https%3A%2F%2Fgithub.com%2Fmckinsey%2Fvizro%20for%20more%20info%20about%20Vizro%0A%23%20and%20checkout%20https%3A%2F%2Fvizro.readthedocs.io%2Fen%2Fstable%2F%20for%20documentation.%0A%0Aimport%20vizro.plotly.express%20as%20px%0Afrom%20vizro%20import%20Vizro%0Aimport%20vizro.models%20as%20vm%0A%0Adf%20%3D%20px.data.iris()%0A%0Apage%20%3D%20vm.Page(%0A%20%20%20%20title%3D%22Vizro%20on%20PyCafe%22%2C%0A%20%20%20%20layout%3Dvm.Layout(grid%3D%5B%5B0%2C%201%5D%2C%20%5B2%2C%202%5D%2C%20%5B2%2C%202%5D%2C%20%5B3%2C%203%5D%2C%20%5B3%2C%203%5D%5D%2C%20row_min_height%3D%22140px%22)%2C%0A%20%20%20%20components%3D%5B%0A%20%20%20%20%20%20%20%20vm.Card(%0A%20%20%20%20%20%20%20%20%20%20%20%20text%3D%22%22%22%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%23%23%20What%20is%20Vizro%3F%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20An%20open-source%20toolkit%20for%20creating%20modular%20data%20visualization%20applications.%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Rapidly%20self-serve%20the%20assembly%20of%20customized%20dashboards%20in%20minutes%20-%20without%20the%20need%20for%20advanced%20coding%20or%20design%20experience%20-%20to%20create%20flexible%20and%20scalable%2C%20Python-enabled%20data%20visualization%20applications.%22%22%22%0A%20%20%20%20%20%20%20%20)%2C%0A%20%20%20%20%20%20%20%20vm.Card(%0A%20%20%20%20%20%20%20%20%20%20%20%20text%3D%22%22%22%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%23%23%20Github%0A%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Checkout%20Vizro's%20GitHub%20page%20for%20further%20information%20and%20release%20notes.%20Contributions%20are%20always%20welcome!%22%22%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20href%3D%22https%3A%2F%2Fgithub.com%2Fmckinsey%2Fvizro%22%2C%0A%20%20%20%20%20%20%20%20)%2C%0A%20%20%20%20%20%20%20%20vm.Graph(id%3D%22scatter_chart%22%2C%20figure%3Dpx.scatter(df%2C%20x%3D%22sepal_length%22%2C%20y%3D%22petal_width%22%2C%20color%3D%22species%22))%2C%0A%20%20%20%20%20%20%20%20vm.Graph(id%3D%22hist_chart%22%2C%20figure%3Dpx.histogram(df%2C%20x%3D%22sepal_width%22%2C%20color%3D%22species%22))%2C%0A%20%20%20%20%5D%2C%0A%20%20%20%20controls%3D%5Bvm.Filter(column%3D%22species%22)%2C%20vm.Filter(column%3D%22petal_length%22)%2C%20vm.Filter(column%3D%22sepal_width%22)%5D%2C%0A)%0A%0Adashboard%20%3D%20vm.Dashboard(pages%3D%5Bpage%5D)%0AVizro().build(dashboard).run()%0A&requirements=vizro%3E%3D0.1.24%0A&python=pyodide-v0.26.1"

        # Navigate to the page and wait for network to be idle
        page.goto(url, wait_until="networkidle")

        # Get the app frame
        frame = page.frame_locator("#app")

        # Wait for the title to appear (we know it should be "Vizro on PyCafe")
        frame.get_by_text("Vizro on PyCafe").wait_for()
