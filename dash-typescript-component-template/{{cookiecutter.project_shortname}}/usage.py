import {{cookiecutter.project_shortname}}
import dash

app = dash.Dash(__name__)

app.layout = {{cookiecutter.project_shortname}}.{{cookiecutter.component_name}}(id='component')


if __name__ == '__main__':
    app.run_server(debug=True)
