"""Example to show dashboard configuration specified as pydantic models."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from dash import html, dcc
from typing import Literal, Optional
import dash_bootstrap_components as dbc

class CodeClipboard(vm.VizroBaseModel):
    type: Literal["code_clipboard"] = "code_clipboard"
    title: str = "Code"
    text: str

    def build(self):
        return dbc.Accordion(
        [
            dbc.AccordionItem(
                dbc.Card([
            html.H3(self.title),
            dcc.Markdown(self.text, id=self.id, className="code-block"),
            dcc.Clipboard(target_id=self.id, className="code-clipboard")]), title="SHOW CODE"
            )
        ],
        start_collapsed=True,
    )



gapminder = px.data.gapminder()

vm.Page.add_type("components", CodeClipboard)


bar = vm.Page(
    title="Bar",
    layout=vm.Layout(grid=[[0, 0, 2, 2, 2],
                            [1, 1,2,2, 2]], col_gap="80px"),
    components=[
        vm.Card(
            text="""

            ### What is a bar chart?

            A Bar chart displays bars in lengths proportional to the values they represent. One axis of
            the chart shows the categories to compare and the other axis provides a value scale,
            starting with zero.

            &nbsp;

            ### When to use the bart chart?

            Select a Bar chart when you want to help your audience draw size comparisons and identify
            patterns between categorical data, i.e., data that presents **how many?** in each category. You can
            arrange your bars in any order to fit the message you wish to emphasise. Be mindful of labelling
            clearly when you have a large number of bars. You may need to include a legend,
            or use abbreviations in the chart with fuller descriptions below of the terms used.
            
        """
        ),
        CodeClipboard(text="""                
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro
                
                df = px.data.iris()
                
                page = vm.Page(
                    title="My first page",
                    components=[
                        vm.Graph(
                            figure=px.scatter_matrix(
                                df, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"], color="species"
                            ),
                        ),
                    ],
                    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
                )
                
                dashboard = vm.Dashboard(pages=[page])
                
                Vizro().build(dashboard).run()
                ```
                
                """),
        vm.Graph(figure=px.bar(data_frame=gapminder.query("country == 'Germany'"), x="year", y="pop")),
    ],
)


dashboard = vm.Dashboard(pages=[bar])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
