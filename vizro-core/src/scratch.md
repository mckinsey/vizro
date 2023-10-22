# To think about

1. Shall we leverage callbacks or children of Tab? (Method 1 vs. 2) https://dash.plotly.com/dash-core-components/tab
   -> Start off with children of Tab and see when we hit performance issues
2. Shall we use dcc or dbc components?
   -> If we go for the "children of tab" method then dcc components are preferred, otherwise there is bug using the dbc components that seems to be solved by using the callback method
3. Tab and Container/Subpage model concepts look very similar in configurations - should we create a Tab model as a stand-alone of abstract to a higher level SubPage model?
4. Still to fix:
   - Fix CSS if using dcc.components
   - theme_update, on_page_load for charts --> chart do not update yet
   - If you apply parameter, some charts disappear?

```
class Page(VizroBaseModel):
    components: List[ComponentType]
    title: str = Field(..., description="Title to be displayed.")
    layout: Optional[Layout]
    controls: List[ControlType] = []
    path: Optional[str] = Field(None, description="Path to navigate to page.")


class Tab(VizroBaseModel):
    components: List[ComponentType]
    title: Optional[str]  # do we need this one?
    # layout: Optional[Layout]

    @_log_call
    def build(self):
        components = [component.build() for component in self.components]
        return dcc.Tab(
            html.Div(children=[html.H3(self.title, className="tab-title"), *components]),
            id=self.id,
            label=self.title,
        )


class Tabs(VizroBaseModel):
    type: Literal["tabs"] = "tabs"
    tabs: List[Tab] = []

    @_log_call
    def build(self):
        return html.Div(
            [
                dcc.Tabs(id=self.id, children=[tab.build() for tab in self.tabs], className="tabs_container"),
            ],
            className="tabs_container_outer",
        )
```
