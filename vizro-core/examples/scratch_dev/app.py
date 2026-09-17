"""Scratch app for testing customization of Page.actions (what runs on page load)."""

import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()


# By default a Page runs an on-page-load action that refreshes all figures and dynamic filters. Setting `Page.actions`
# replaces that default with your own chain, which runs on page load. The "Reset all" button always refreshes the
# page's figures and dynamic filters independently of `Page.actions`.

# Page 1: keep the default refresh AND greet the user. `va.update_targets()` re-applies the controls (the same work the
# default on-page-load does), then `va.show_notification` shows the welcome toast.
welcome_page = vm.Page(
    title="Welcome notification",
    components=[
        vm.Graph(id="welcome_graph", figure=px.bar(df, x="species", y="sepal_length", color="species")),
    ],
    controls=[vm.Filter(column="species")],
    actions=[va.update_targets(), va.show_notification(text="Welcome! Data refreshed for this page.")],
)


# Page 2: defer loading expensive data. `actions=[]` disables the automatic on-page-load refresh, so the figure renders
# empty until the user clicks the button, which triggers the refresh on demand.
lazy_page = vm.Page(
    title="Load on demand",
    components=[
        vm.Graph(id="lazy_graph", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
        vm.Button(text="Load data", actions=va.update_targets()),
    ],
    controls=[vm.Filter(column="species", selector=vm.Checklist(actions=None))],
    actions=None,
)


dashboard = vm.Dashboard(pages=[welcome_page, lazy_page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
