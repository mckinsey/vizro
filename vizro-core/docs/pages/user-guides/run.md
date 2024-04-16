# How to launch the dashboard

This guide shows you how to launch your dashboard in different ways. By default, your dashboard apps run on localhost port 8050 so is accessible at [http://127.0.0.1:8050/](http://127.0.0.1:8050/).

## Default built-in Flask development server

!!! example "Default built-in Flask development server"
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
- create a Python file named `app.py`.
- type the command `python app.py` into your terminal.
- information below will be displayed in your terminal, go to [http://127.0.0.1:8050/](http://127.0.0.1:8050/).

```
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app'
 * Debug mode: off
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
```

!!! warning "In production"

    As per the above warning message, which is [further explained in the Flask documentation](https://flask.palletsprojects.com/en/3.0.x/deploying/), the Flask development server is intended for use only during local development and **should not** be used when deploying to production. Instead, you should instead use a production-ready solution such as [gunicorn](#gunicorn).

??? info "Automatic reloading and debugging"


    You can set up the front-end to automatically refresh whenever dashboard configuration updates are made, as described in the
    ["Code Reloading and Hot Reloading" section of the Dash Dev Tools documentation](https://dash.plotly.com/devtools#code-reloading-&-hot-reloading).
    This is turned off by default in Vizro apps but can be enabled by using `debug=True` in the `run()` method:

    `Vizro().build(dashboard).run(debug=True)`

    Setting `debug=True` enables [Dash Dev Tools](https://dash.plotly.com/devtools). In addition to hot reloading, this enables several other features that are useful during development, such as detailed in-app error reporting.

    In addition, some errors generated at run time can also be viewed via the browser console (for example in `Chrome` see `View > Developer > Developer Tools > Console`).


## Jupyter
The dashboard application can be launched in a Jupyter environment in `inline`, `external`, and `jupyterlab` mode.
!!! example "Run in a Jupyter Notebook in inline mode"

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
- by default, the mode is set to `inline` in `run()` and the dashboard will be displayed inside your Jupyter environment.
- you can specify `jupyter_mode="external"` and a link will be displayed to direct you to the localhost where the dashboard is running.
- you can use tab mode by `jupyter_mode="tab"` to automatically open the app in a new browser

??? info "Reloading and debugging"

     When working in a Jupyter Notebook, only some of the [Dash Dev Tools](https://dash.plotly.com/devtools) functionality is enabled by using `run(debug=True)`.
     In particular, code reloading and hot reloading do not work from a Jupyter Notebook. Instead, you must restart the entire Jupyter kernel to reload the dashboard and reflect changes in the dashboard configuration.

## Gunicorn

[Gunicorn](https://gunicorn.org/) is a production-ready Python WSGI server for deploying an app over multiple worker processes. It can be installed with `pip install gunicorn`.

!!! example "Use Gunicorn"
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
        server = app.dash.server # (1)!

        if __name__ == "__main__":  # (2)!
            app.run()
        ```

        1. Expose the underlying Flask app through `app.dash.server`; this will be used by Gunicorn.
        2. Enable the same app to still be run using the built-in Flask server with `python app.py` for development purposes.

To run using Gunicorn with four worker processes, execute
```bash
gunicorn app:server --workers 4
```
in the command line. For more Gunicorn configuration options, refer to [Gunicorn documentation](https://docs.gunicorn.org/).

!!! warning "In production"

    If your dashboard uses [dynamic data](data.md#dynamic-data) that can be refreshed while the dashboard is running then you should [configure your data manager cache](data.md#configure-cache) to use a backend that supports multiple processes.

## Deployment

A Vizro app wraps a Dash app, which itself wraps a Flask app. Hence to deploy a Vizro app, similar guidance applies as for the underlying frameworks:

- [Flask deployment documentation](https://flask.palletsprojects.com/en/2.0.x/deploying/)
- [Dash deployment documentation](https://dash.plotly.com/deployment)

In particular, `app = Vizro()` exposes the Flask app through `app.dash.server`. As in the [above example with Gunicorn](#gunicorn), this provides the application instance to a [WSGI](https://werkzeug.palletsprojects.com/en/3.0.x/terms/#wsgi) server.

[`Vizro`][vizro.Vizro] accepts `**kwargs` that are passed through to `Dash`. This enables you to configure the underlying Dash app using the same [arguments that are available](https://dash.plotly.com/reference#dash.dash) in `Dash`. For example, in a deployment context, you might like to specify a custom `url_base_pathname` to serve your Vizro app at a specific URL rather than at your domain root.
