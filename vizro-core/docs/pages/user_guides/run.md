# How to launch the dashboard

This guide shows you how to launch your dashboard in different ways. By default, your dashboard apps run on localhost.

## Default built-in web server in flask

!!! example "Default flask server"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
- create a python file named app.py.
- type the command `python app.py` into your terminal.
- information below will be displayed in your terminal, go to the http link.
```
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app'
 * Debug mode: on
```

## Launch it in jupyter environment
The dashboard application can be launched in jupyter environment in `inline`, `external`, and `jupyterlab` mode.
!!! example "Run in jupyter notebook in inline mode"
    === "app.ipynb"
        ```py linenums="1"
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run(jupyter_mode="external")
        ```
- by default, the mode is set to `inline` in `run()` and the dashboard will be displayed inside your jupyter environment.
- you can specify `jupyter_mode="external"` and a link will be displayed to direct you to the localhost where the dashboard is running.
- you can use tab mode by `jupyter_mode="tab"` to automatically open the app in a new browser

## Deployment of Vizro app
!!!warning "In production"
    In production, it is recommended **not** to use the default flask server. One of the options here is gunicorn. It is easy to scale the application to serve more users or run more computations, run more "copies" of the app in separate processes.

A Vizro app wraps a Dash app, which itself wraps a Flask app. Hence to deploy a Vizro app, similar guidance applies as for the underlying frameworks:

- [Flask deployment documentation](https://flask.palletsprojects.com/en/2.0.x/deploying/)
- [Dash deployment documentation](https://dash.plotly.com/deployment)

In particular, `app = Vizro()` exposes the underyling Flask app through `app.dash.server`. This provides the application instance to a WSGI server such as [Gunicorn](https://gunicorn.org/).

!!! example "Use gunicorn"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        app = Vizro().build(dashboard)
        server = app.dash.server
        ```
To run using Gunicorn with four worker processes, execute
```bash
gunicorn app:server --workers 4
```
in the command line. For more Gunicorn configuration options, please refer to [Gunicorn documentation](https://docs.gunicorn.org/).

