# To think about

1. Shall we leverage callbacks or children of Tab? (Method 1 vs. 2) https://dash.plotly.com/dash-core-components/tab
   -> probably children of Tabs as otherwise model build will be moved to callback
2. Tab and Page model look very similar in configurations (essentially Tabs are sub-pages within a Page) - should we do configurations differently?
3. Should we have Tabs and Tab as separate models? In Dash they are treated as separate models as well, but it kind of adds another layer of hierarchy
4. Shall we define components within tabs or globally on page and then reference as ID in tabs?
5. How should the filter/parameter flow look like?
   1. If no targets specified -> apply to all tabs or only visible tabs?
   2. If targets specified -> should enable ability to target specific figure in tab as normal
   3. If filters only affect a tab - should it still live on the left-side or be moved to the tab? Where should it go?
6. Still to fix:
   - CSS
   - Themes do not update on chart currently -> caused by the fact that theme_update in charts live in Page - should optimally be refactored out and live in the components

```
class Page(VizroBaseModel):
    components: List[ComponentType]
    title: str = Field(..., description="Title to be displayed.")
    layout: Optional[Layout]
    controls: List[ControlType] = []
    actions: List[ActionsChain] = []
    path


class Tab(VizroBaseModel):
    components: List[TabComponentType]
    label: str = Field(..., description="Tab Lable to be displayed.")
    title: Optional[str]  # do we need this one?
    # layout: Optional[Layout]
    # controls: List[ControlType] = []  -> should be done implicitly without configuring? -> tendency to remove it
    # actions: List[ActionsChain] = []  -> do we even need to make this configurable? -> tendency to remove it


class Tabs(VizroBaseModel):
    type: Literal["tabs"] = "tabs"
    title: str
    tabs: List[Tab] = []
```
