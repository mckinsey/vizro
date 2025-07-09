from vizro import Vizro
import vizro.models as vm
import pandas as pd
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid


gapminder_2007 = px.data.gapminder().query("year == 2007")
stocks = px.data.stocks(datetimes=True)
tips = px.data.tips()

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


dashboard = vm.Dashboard(pages=[selectors])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
