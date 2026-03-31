from dash import html

import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.models.types import capture


df = px.data.iris()
df_6 = df.iloc[[0, 1, 50, 51, 100, 101]]

tips = px.data.tips()
pivot_tips = (
    tips.pivot_table(index="sex", columns="day", aggfunc="size", fill_value=0)
    .reindex(columns=["Thur", "Fri", "Sat", "Sun"])
    .reset_index()
)


@capture("ag_grid")
def custom_dash_ag_grid(data_frame, **kwargs):
    grid = dash_ag_grid(data_frame, **kwargs)()
    return grid


pre = "p1"
page_1 = vm.Page(
    title="AgGrid set_control",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="standard dash_ag_grid",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_1",
                            title="Standard AgGrid with no actions",
                            figure=dash_ag_grid(df_6),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_2",
                            title="AgGrid with set_control.value=column_name",
                            figure=dash_ag_grid(df_6),
                            actions=va.set_control(control=f"{pre}_filter_1", value="species"),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_3",
                            title="AgGrid with set_control.value=column_name and explicit checkboxes=False config",
                            figure=dash_ag_grid(
                                df_6, dashGridOptions=dict(rowSelection=dict(checkboxes=False, headerCheckbox=False))
                            ),
                            actions=va.set_control(control=f"{pre}_filter_1", value="species"),
                        ),
                    ],
                ),
                vm.Container(
                    title="Custom AgGrid",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.AgGrid(id=f"{pre}_ag_grid_4", title="Custom AgGrid", figure=dash_ag_grid(df_6)),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_5",
                            title="Custom AgGrid with set_control.value=column_name",
                            figure=custom_dash_ag_grid(df_6),
                            actions=va.set_control(control=f"{pre}_filter_1", value="species"),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_6",
                            title="Custom AgGrid with set_control.value=column_name and explicit checkboxes=False config",
                            figure=custom_dash_ag_grid(
                                df_6, dashGridOptions=dict(rowSelection=dict(checkboxes=False, headerCheckbox=False))
                            ),
                            actions=va.set_control(control=f"{pre}_filter_1", value="species"),
                        ),
                    ],
                ),
            ]
        ),
        vm.AgGrid(id=f"{pre}_target_table", title="Control Target", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=[vm.Filter(id=f"{pre}_filter_1", column="species", targets=[f"{pre}_target_table"])],
)


@capture("figure")
def dynamic_title(data_frame, cell_clicked=0):
    try:
        cell_clicked = int(cell_clicked)
    except ValueError:
        cell_clicked = 0

    return (html.H2(f"One tip one '|': {'|' * cell_clicked}"),)


page_2 = vm.Page(
    title="dash_ag_grid using cellClicked",
    components=[
        vm.AgGrid(
            title="set_control.value=COLUMN",
            figure=dash_ag_grid(pivot_tips),
            actions=[
                va.set_control(control="day_filter", value="COLUMN"),
            ],
        ),
        vm.AgGrid(
            title=" set_control.value=COLUMN + set_control.value=column_name",
            figure=dash_ag_grid(pivot_tips),
            actions=[
                va.set_control(control="day_filter", value="COLUMN"),
                va.set_control(control="sex_filter", value="sex"),
            ],
        ),
        vm.AgGrid(
            title="set_control.value=COLUMN + set_control.value=column_name + set_control.value=CELL",
            figure=dash_ag_grid(pivot_tips),
            actions=[
                va.set_control(control="day_filter", value="COLUMN"),
                va.set_control(control="sex_filter", value="sex"),
                va.set_control(control="cell_clicked", value="CELL"),
            ],
        ),
        vm.Container(
            layout=vm.Flex(direction="column"),
            components=[
                vm.Figure(id="tips_table_title", figure=dynamic_title(df_6, cell_clicked="")),
                vm.AgGrid(id="tips_table", figure=dash_ag_grid(tips)),
            ],
        ),
    ],
    controls=[
        vm.Filter(id="day_filter", column="day", targets=["tips_table"]),
        vm.Filter(id="sex_filter", column="sex", targets=["tips_table"]),
        vm.Parameter(
            id="cell_clicked",
            targets=["tips_table_title.cell_clicked"],
            visible=False,
            selector=vm.RadioItems(options=[str(x) for x in range(100)]),
        ),
    ],
)

page_3 = vm.Page(
    title="Filter Interaction",
    components=[
        vm.AgGrid(figure=dash_ag_grid(tips), actions=va.filter_interaction(targets=["fi_target"])),
        vm.AgGrid(id="fi_target", figure=dash_ag_grid(tips)),
    ],
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
