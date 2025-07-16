from vizro import Vizro
import vizro.models as vm
import pandas as pd
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid


gapminder_2007 = px.data.gapminder().query("year == 2007")
stocks = px.data.stocks(datetimes=True)
tips = px.data.tips()
iris = px.data.iris()


test_options_30_chars = [
    # 24 characters seems to be the sweet spot for the dropdown width now
    "A" * 24,
    "Option B",
    "Option C",
]


# Test page for character width testing
character_test_page = vm.Page(
    title="Dropdown Character Width Test",
    components=[
        vm.Card(
            text="""
            ### Dropdown Character Width Test
            
            **Purpose:** Determine the optimal character count for dropdowns in the 300,jn px left panel.
            
            **Current setting:** 30 characters for left panel, 15 for containers
            
            **Instructions:**

            1. Look at the dropdown in the left panel
            2. Note where text starts wrapping to a second line
            3. The optimal character count is where text just fits on one line
            4. Test by selecting different options to see wrapping behavior
            
            **Expected:** Text should wrap around 25-28 characters for the new 280px width
            """
        ),
        vm.Graph(
            id="scatter",
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="sepal_width", 
                color="species",
                title="Sample Chart - Select filters to test dropdown behavior"
            )
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["scatter.title"],
            selector=vm.Dropdown(
                title="Check Char Count",
                options=test_options_30_chars,
                value=test_options_30_chars[0],
                multi=False,
            ),
        ),
    ],
)

selectors = vm.Page(
    title="Selectors",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [2], [2], [2], [3], [3], [3]], row_min_height="170px", row_gap="24px"),
    components=[
        vm.Card(
            text="""
        A selector can be used within the **Parameter** or **Filter** component to allow the user to select a value.

        The following selectors are available:
        * Dropdown (**categorical** multi and single option selector)
        * Checklist (**categorical** multi option selector only)
        * RadioItems (**categorical** single option selector only)
        * RangeSlider (**numerical** multi option selector only)
        * Slider (**numerical** single option selector only)
        * DatePicker(**temporal** multi and single option selector)

        """
        ),
        vm.AgGrid(
            id="table-gapminder",
            figure=dash_ag_grid(data_frame=gapminder_2007),
            title="Gapminder Data",
        ),
        vm.AgGrid(id="table-tips", figure=dash_ag_grid(data_frame=tips), title="Tips Data"),
        vm.Graph(
            id="graph-stocks",
            figure=px.line(stocks, x="date", y="GOOG", title="Stocks Data"),
        ),
    ],
    controls=[
        vm.Filter(
            targets=["table-gapminder"],
            column="lifeExp",
            selector=vm.RangeSlider(title="Range Slider (Gapminder - lifeExp)", step=1, marks=None),
        ),
        vm.Filter(
            targets=["table-gapminder"],
            column="continent",
            selector=vm.Checklist(title="Checklist (Gapminder - continent)"),
        ),
        vm.Filter(
            targets=["table-gapminder"],
            column="country",
            selector=vm.Dropdown(title="Dropdown (Gapminder - country)"),
        ),
        vm.Filter(
            targets=["table-tips"],
            column="day",
            selector=vm.Dropdown(title="Dropdown (Tips - day)", multi=False, value="Sat"),
        ),
        vm.Filter(
            targets=["table-tips"],
            column="sex",
            selector=vm.RadioItems(title="Radio Items (Tips - sex)"),
        ),
        vm.Filter(
            targets=["table-tips"],
            column="size",
            selector=vm.Slider(title="Slider (Tips - size)", step=1, value=2),
        ),
        vm.Filter(targets=["graph-stocks"], column="date", selector=vm.DatePicker(title="Date Picker (Stocks - date)")),
    ],
)


dashboard = vm.Dashboard(pages=[selectors, character_test_page])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
