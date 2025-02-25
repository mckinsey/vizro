import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import filter_interaction, export_data
from vizro.models._action._action import capture_new_action, VizroState, VizroOutput
from vizro.models.types import capture

df_gapminder = px.data.gapminder().query("year == 2007")

page1 = vm.Page(
    title="Filter interaction",
    components=[
        vm.Graph(
            figure=px.box(
                df_gapminder,
                x="continent",
                y="lifeExp",
                color="continent",
                custom_data=["continent"],
            ),
            actions=[filter_interaction(targets=["scatter_relation_2007"])],
        ),
        vm.Graph(
            id="scatter_relation_2007",
            figure=px.scatter(
                df_gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
        vm.Button(
            text="Export data",
            actions=[export_data(targets=["scatter_relation_2007"])],
        ),
    ],
    controls=[
        vm.Filter(column="continent"),
        vm.Parameter(
            id="parameter_x",
            targets=["scatter_relation_2007.color"],
            selector=vm.RadioItems(options=["continent", "pop"], id="x"),
        ),
    ],
)


# @capture("action")
@capture_new_action
def my_custom_action(points_data: VizroState, output: VizroOutput):
    # Problem: have unused argument, but that is ok. Better than argument not existing. To improve linting give it _
    # name?
    """Custom action."""
    clicked_point = points_data["points"][0]
    x, y = clicked_point["x"], clicked_point["y"]
    species = clicked_point["customdata"][0]
    card_1_text = f"Clicked point has sepal length {x}, petal width {y}"
    # card_2_text = f"Clicked point has species {species}"
    return card_1_text  # , card_2_text


df = px.data.iris()

page2 = vm.Page(
    title="Example of a custom action with UI inputs and outputs",
    layout=vm.Layout(
        grid=[
            [0, 0],
            [0, 0],
            [0, 0],
            [1, 2],
        ],
        row_gap="25px",
    ),
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
            actions=[
                my_custom_action(
                    points_data="scatter_chart.clickData", output="my_card_1.children"
                ),  # Don't like this.
                # Alternatives - don't like these either but better? Could be shortcut for full vm.Action version.
                # {my_custom_action(points_data="scatter_chart.clickData"): "my_card_1"}, ##### PREFERRED as shortcut
                # syntax
                # could make NewCustomAction hashable by hasing model id
                # {"my_card_1.children": my_custom_action(points_data="scatter_chart.clickData")}, # This doesn't
                # work as well - what if have two actions with None output.
                # vm.GenericCustomAction(
                #     function=my_specific_action(points_data="scatter_chart.clickData"), outputs="my_card_1.children"
                # ), # ok
                # this is only sensible option but then what is point of removing inputs? c.f.
                # vm.GenericCustomAction(
                #     function=my_specific_action(),  # could supply static arguments here if you wanted to?? Or just
                #     ban them and make it my_specific_action without ()?
                #     inputs=dict(points_data="scatter_chart.clickData")),
                #     outputs="my_card_1.children"
                # )
                # Make this possible and consider shortcut syntax of {"my_card_1.children": my_custom_action(
                # points_data="scatter_chart.clickData")}.
                # {"function": ..., "outputs": ...} possible without explicit vm.Action
                # vm.ActionXXX(function: NewCustomAction, outputs: Optional ...)
                # XXX to distinguish from current
                # want to match inbuilt actions to this
                # but also want shortcut, so would be same plain unwrapped export_data(targets="a") as syntax
                # export_data is then subclass of vm.ActionXXX with its own fields inculding outputs,
                # just like current NewAction
                # <-- gives space to make trigger/non-triggering, alerts etc.
                # can have syntactic sugar shortcuts?
                # vm.Action(
                #     function=my_custom_action(),
                #     inputs=["scatter_chart.clickData"],
                #     outputs=["my_card_1.children", "my_card_2.children"],
                # ),
            ],
        ),
        vm.Card(id="my_card_1", text="Click on a point on the above graph."),
        vm.Card(id="my_card_2", text="Click on a point on the above graph."),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)

dashboard = vm.Dashboard(pages=[page1, page2])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
