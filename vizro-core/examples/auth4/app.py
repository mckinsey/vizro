from typing import Optional

from dash_auth import BasicAuth, protected

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm


# This method needs two custom classes, one for the Page and one for the overall Dashboard.
# Possible alternatives:
#  - alter dash.page_registry["page_id"]["layout"] directly. Should work basically the same way but less vizro-ic
#  - raise PreventUpdate in `page.build` (don't try and create a fake `html.Div` with all the right keys) - should
#     work fine and means less overriding of private things, but a bit more code gets executed before being cancelled
#     as unauthorised
class ProtectedPage(vm.Page):
    groups: Optional[list[str]] = None


class DashboardWithProtectedPages(vm.Dashboard):
    def _make_page_layout(self, page: ProtectedPage, **kwargs):
        if isinstance(page, ProtectedPage):
            return protected(self._make_page_404_layout, groups=page.groups)(super()._make_page_layout)(page, **kwargs)
        return super()._make_page_layout(page, **kwargs)


df = px.data.iris()

page_1 = vm.Page(title="Normal page", components=[vm.Text(text="Any authenticated user can see this")])
page_2 = ProtectedPage(title="Private page", groups=["admin"], components=[vm.Text(text="Top secret text")])

dashboard = DashboardWithProtectedPages(pages=[page_1, page_2])
app = Vizro().build(dashboard)

USER_PWD = {
    "username": "password",
    "admin": "password",
}

USER_GROUPS = {"username": ["user"], "admin": ["admin"]}

BasicAuth(app.dash, USER_PWD, user_groups=USER_GROUPS, secret_key="<PUT SOMETHING SUPER SECRET HERE>")
app.run()
