"""Example to show dashboard configuration specified as pydantic models."""

from typing import Literal, Optional

import dash_mantine_components as dmc
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()


# class CodeHighlight(vm.VizroBaseModel):
#    type: Literal["code_highlight"] = "code_highlight"
#    language: Optional[str] = "python"
#    code: str

#    def build(self):
#        return dmc.CodeHighlight(
#            language=self.language,
#            code=self.code,
#        )
#vm.Page.add_type("components", CodeHighlight)


bar = vm.Page(
    title="Bar Chart",
    layout=vm.Layout(grid=[[0, 1, 1]]),
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
            patterns between categorical data, i.e., data that presents `how many?` in each category. You can
            arrange your bars in any order to fit the message you wish to emphasise. Be mindful of labelling
            clearly when you have a large number of bars. You may need to include a legend,
            or use abbreviations in the chart with fuller descriptions below of the terms used.
            
            &nbsp;
            
            ### Code
            ```python

            vm.Graph(figure=px.bar(data_frame=gapminder.query('country == 'Germany''), x='year', y='pop')

            ```
        """
        ),
        vm.Graph(figure=px.bar(data_frame=gapminder.query("country == 'Germany'"), x="year", y="pop")),
    ],
)





dashboard = vm.Dashboard(pages=[bar])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
