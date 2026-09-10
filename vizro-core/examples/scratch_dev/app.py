"""Scratch app for testing conditional notifications on built-in actions.

Built-in actions get sensible default notifications that are not configurable through a public field. Error
messages are action-specific but never leak *why* something failed.

What to look for while testing manually:
  * Filter / Parameter change -> no toast (silent refresh)            [update_targets]
  * "Apply controls"          -> no toast on success                  [update_targets]
  * Click a bar               -> "Control updated." (success)         [set_control]
  * "Export data"             -> "Exporting data..." then "Data exported." (progress -> success) [export_data]
  * Any failure               -> action-specific error toast (no reason shown to the end user)
"""

import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()
SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}


page = vm.Page(
    id="builtin_notifications",
    title="Built-in action notifications",
    layout=vm.Flex(),
    components=[
        vm.Graph(
            id="source_graph",
            title="Click a bar to set the species filter (set_control)",
            figure=px.bar(
                df,
                x="species",
                y="sepal_length",
                color="species",
                color_discrete_map=SPECIES_COLORS,
                custom_data="species",
            ),
            # set_control: on success shows "Control updated.", on failure shows "Setting the control failed."
            actions=va.set_control(control="species_filter", value="species"),
        ),
        vm.Container(
            layout=vm.Flex(direction="row"),
            components=[
                # export_data: shows "Exporting data..." (progress) then "Data exported." (success); on failure
                # shows "Exporting data failed."
                vm.Button(text="Export data", actions=va.export_data(targets=["target_graph"])),
                # update_targets on a button: no success toast; on failure shows "Updating figures failed."
                vm.Button(text="Apply controls", actions=va.update_targets(targets=["target_graph"])),
            ],
        ),
        vm.Graph(
            id="target_graph",
            title="Target graph (filtered / parameterized / exported)",
            figure=px.scatter(
                df,
                x="sepal_length",
                y="sepal_width",
                color="species",
                color_discrete_map=SPECIES_COLORS,
            ),
        ),
    ],
    controls=[
        # Filter change auto-runs update_targets -> silent refresh (no toast).
        vm.Filter(id="species_filter", column="species", targets=["target_graph"]),
        # Parameter change auto-runs update_targets -> silent refresh (no toast).
        vm.Parameter(
            targets=["target_graph.x"],
            selector=vm.RadioItems(options=["sepal_length", "sepal_width"], title="X axis"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
