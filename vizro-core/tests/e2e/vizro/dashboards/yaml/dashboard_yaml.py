from pathlib import Path

import yaml
from e2e.vizro.constants import YAML_PORT

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager

data_manager["iris"] = px.data.iris()
data_manager["gapminder"] = px.data.gapminder()
dashboard = yaml.safe_load(Path("tests/e2e/vizro/dashboards/yaml/dashboard.yaml").read_text(encoding="utf-8"))
dashboard = vm.Dashboard(**dashboard)

app = Vizro(assets_folder="../assets").build(dashboard)

if __name__ == "__main__":
    app.run(port=YAML_PORT, debug=True)
