"""This is a test app to test the dashboard layout."""

import vizro.models as vm
from vizro import Vizro


code_example = """
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()

fig = px.pie(tips, values="tip", names="day", hole=0.4)

page = vm.Page(title="My page", components=[vm.Graph(figure=fig)])

"""


page = vm.Page(
    title="Test Page",
    components=[vm.Text(text=f"""```python{code_example}```""")],
)

dashboard = vm.Dashboard(
    pages=[
        page,
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
