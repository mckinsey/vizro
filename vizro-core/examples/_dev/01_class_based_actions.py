"""Class based actions examples. Example below shows how the underlying class-based actions are configured and work in
a same way as before. So what's new?
1. Class-based actions implementation.
- Users will configure actions in the same way as before, so there is no compatibility breaking changes.
2. How the new validation system and action argument calculation works.
- Validation and action argument calculation happens in the build phase (The eager validation is introduced).
- See all test cases `examples/_dev/actions_targets_test_cases.xlsx`. (use it for unit tests implementation)
- There is a room for improvement in the validation system for filter/parameter actions.
See FilterAction._post_init # TO-DO-AV2-OQ: Rethink validation and calculation...
3. 'filter_action' and 'parameter_action' are now public which helps in overwriting default actions.
- See `02_overwriting_default_actions.py` for more.
4. A new action is here -> `update_figures`. It is very similar to old `on_page_load` action, but it's public.
- It is used as a default "Page.actions" action, if no actions are specified.
- It can be used to update figures data from its source. (similar to `update_data` we had in VizX).
5. Page.actions argument is now exposed.
- Any action set in the Page.actions will overwrite the default `update_figures` action.
- Overwriting Page.actions can be used to perform some calculation before/after the `update_figures` is called.
- See `02_overwriting_default_actions.py` for more.
"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.tables import dash_ag_grid

df = px.data.gapminder().query("year == 2007")
default_card_text = "Click on a cell in the table to filter the scatter plot."


dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Page_1",
            layout=vm.Layout(grid=[[0], [1], [1], [1], [2], [2], [2], [3]]),
            components=[
                vm.Card(id="card", text=default_card_text),
                vm.AgGrid(
                    id="ag_grid",
                    figure=dash_ag_grid(id="underlying_ag_grid", data_frame=df),
                    actions=[
                        # Below filter_interaction action uses the new actions implementation in the background.
                        vm.Action(function=filter_interaction(targets=["scatter"])),
                        # Try to set `targets=["scatter", "scatter_from_page_2"]` and see what happens.
                        # vm.Action(function=filter_interaction(targets=["scatter", "scatter_from_page_2"])),
                        # Try to set `targets=["scatter", "scatter_that_does_not_exists"]` and see what happens.
                        # vm.Action(function=filter_interaction(targets=["scatter", "scatter_that_does_not_exists"])),
                    ],
                ),
                vm.Graph(
                    id="scatter", figure=px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent")
                ),
                vm.Button(
                    text="Export data",
                    actions=[
                        # Below filter_interaction action uses the new actions implementation in the background.
                        vm.Action(function=export_data(targets=["scatter"])),
                        # Try to set `targets=["scatter", "scatter_from_page_2"]` and see what happens.
                        # vm.Action(function=export_data(targets=["scatter", "scatter_from_page_2"])),
                        # Try to set `targets=["scatter", "scatter_that_does_not_exists"]` and see what happens.
                        # vm.Action(function=export_data(targets=["scatter", "scatter_that_does_not_exists"])),
                    ],
                ),
            ],
            controls=[
                vm.Filter(column="continent"),
                vm.Parameter(selector=vm.RadioItems(options=["gdpPercap", "lifeExp"]), targets=["scatter.x"]),
            ],
            # because no actions are specified in the page.actions, the default action update_figures is used.
            # e.g. actions=[vm.Action(function=update_figures())],
        ),
        vm.Page(
            title="Page 2",
            components=[
                vm.Graph(
                    id="scatter_from_page_2",
                    figure=px.scatter(df, x="gdpPercap", y="lifeExp", color="continent"),
                ),
            ],
            controls=[vm.Filter(column="continent")],
        ),
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
