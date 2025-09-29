############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from vizro import Vizro
import pandas as pd
from vizro.managers import data_manager
import vizro.plotly.express as px
from vizro.models.types import capture


####### Function definitions ######
@capture("graph")
def life_expectancy_line_chart(data_frame):
    fig = px.line(
        data_frame,
        x="year",
        y="lifeExp",
        color="country",
    )
    return fig


@capture("graph")
def life_expectancy_bar_chart(data_frame):
    data_2007 = data_frame[data_frame["year"] == 2007].sort_values("lifeExp", ascending=True)
    fig = px.bar(
        data_2007,
        y="country",
        x="lifeExp"
    )

    return fig


####### Data Manager Settings #####
data_manager["gapminder_data"] = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)

########### Model code ############
dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            controls=[vm.Filter(column="continent", selector=vm.Dropdown(multi=False, value="FSU")), vm.Filter(column="year", selector=vm.RangeSlider(value=[1992, 2007]))],
            components=[
                vm.Graph(
                    id="life_exp_bar_chart",
                    figure=life_expectancy_bar_chart(data_frame="gapminder_data"),
                    title="Life Expectancy Ranking (2007)",
                ),
                vm.Graph(
                    id="life_exp_line_chart",
                    figure=life_expectancy_line_chart(data_frame="gapminder_data"),
                    title="Life Expectancy Over Time",
                ),
            ],
            title="Gapminder Life Expectancy Dashboard",
        )
    ],
    title="Gapminder Dashboard",
)

app = Vizro().build(dashboard)
if __name__ == "__main__":
    app.run(debug=True, port=8050)