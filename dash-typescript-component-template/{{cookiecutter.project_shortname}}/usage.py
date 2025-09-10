import {{cookiecutter.project_shortname}}
import vizro.models as vm
from vizro import Vizro

{{cookiecutter.project_shortname}}_page = vm.Page(
    title="{{cookiecutter.project_shortname}}",
    components="add components to create {{cookiecutter.project_name}}"
)

# Create the dashboard
dashboard = vm.Dashboard(
    pages=[{{cookiecutter.project_shortname}}_page],
    title="{{cookiecutter.project_name}} Demo"
)

if __name__ == '__main__':
    # Build and run the Vizro app with theme switching enabled
    app = Vizro().build(dashboard)
    app.run(debug=True)
