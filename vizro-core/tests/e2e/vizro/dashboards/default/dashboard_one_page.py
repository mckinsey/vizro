import e2e.vizro.constants as cnst
from pages.export_action_page import export_action_page

import vizro.models as vm
from vizro import Vizro

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[export_action_page],
    navigation=vm.Navigation(pages={cnst.EXPORT_PAGE}),
    theme="vizro_light",
)

app = Vizro(assets_folder="../assets").build(dashboard)

if __name__ == "__main__":
    app.run(debug=True)
