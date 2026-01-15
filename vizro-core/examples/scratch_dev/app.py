import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_ag_grid


df = px.data.iris()
df_6 = df.iloc[[0, 1, 50, 51, 100, 101]]


@capture("ag_grid")
def custom_dash_ag_grid_with_kwargs(data_frame, **kwargs):
    grid = dash_ag_grid(data_frame, **kwargs)()
    return grid


@capture("ag_grid")
def custom_dash_ag_grid_with_no_kwargs(data_frame, dash_grid_options=None):
    dash_grid_options = dash_grid_options or {}
    grid = dash_ag_grid(data_frame, dashGridOptions=dash_grid_options)()
    return grid


pre = "p1_"
page_1 = vm.Page(
    title="AgGrid automatic checkboxes test",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="dash_ag_grid",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_1",
                            title="Standard AgGrid",
                            figure=dash_ag_grid(df_6),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_2",
                            title="AgGrid with set_control",
                            figure=dash_ag_grid(df_6),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_3",
                            title="AgGrid with set_control and explicit checkboxes=False config",
                            figure=dash_ag_grid(
                                df_6, dashGridOptions=dict(rowSelection=dict(checkboxes=False, headerCheckbox=False))
                            ),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                    ],
                ),
                vm.Container(
                    title="Custom AgGrid figure functions with kwargs",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_4", title="Custom AgGrid", figure=custom_dash_ag_grid_with_kwargs(df_6)
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_5",
                            title="Custom AgGrid with set_control",
                            figure=custom_dash_ag_grid_with_kwargs(df_6),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_6",
                            title="Custom AgGrid with set_control and explicit checkboxes=False config",
                            figure=custom_dash_ag_grid_with_kwargs(
                                df_6, dashGridOptions=dict(rowSelection=dict(checkboxes=False, headerCheckbox=False))
                            ),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                    ],
                ),
                vm.Container(
                    title="Custom AgGrid figure functions with NO kwargs",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_7",
                            title="Custom AgGrid",
                            figure=custom_dash_ag_grid_with_no_kwargs(df_6),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_8",
                            title="Custom AgGrid with set_control",
                            figure=custom_dash_ag_grid_with_no_kwargs(df_6),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_9",
                            title="Custom AgGrid with set_control and explicit checkboxes=False config",
                            figure=custom_dash_ag_grid_with_no_kwargs(
                                df_6, dash_grid_options=dict(rowSelection=dict(checkboxes=False, headerCheckbox=False))
                            ),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                    ],
                ),
            ]
        ),
        vm.AgGrid(id=f"{pre}table", title="Control Target", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=[vm.Filter(id=f"{pre}filter_1", column="species", targets=[f"{pre}table"])],
)

pre = "p2_"
page_2 = vm.Page(
    title="Test old filter interaction",
    components=[
        vm.AgGrid(
            id=f"{pre}ag_grid_1",
            title="Source of Filter Interaction",
            figure=dash_ag_grid(px.data.iris()),
            actions=va.filter_interaction(targets=[f"{pre}ag_grid_2"]),
        ),
        vm.AgGrid(
            id=f"{pre}ag_grid_2",
            title="Target of Filter Interaction",
            figure=dash_ag_grid(px.data.iris()),
        ),
    ],
)

page_3 = vm.Page(
    title="Custom action test",
    components=[
        vm.AgGrid(
            title="AgGrid with Custom Action",
            figure=dash_ag_grid(px.data.iris()),
            actions=vm.Action(
                function=capture("action")(lambda _trigger: str(_trigger))(),
                outputs="text_id",
            ),
        ),
        vm.Text(id="text_id", text="Action Output"),
    ],
)


dashboard = vm.Dashboard(pages=[page_1, page_2, page_3])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
