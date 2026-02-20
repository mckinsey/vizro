from pages.export_action_page import export_action_page

import vizro.models as vm
from vizro import Vizro

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[export_action_page],
    theme="vizro_light",
)

app = Vizro(assets_folder="../assets_themed_logo").build(dashboard)

if __name__ == "__main__":
    app.run()
