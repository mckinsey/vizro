# How to launch the dashboard

This guide shows you how to launch your dashboard in different ways. By default, your dashboard apps run on localhost.

## Default built-in Flask web server

!!! example "Default built-in Flask web server"
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

??? info "Debugging and Re-loading"

    #### Debugging

    Dash dev tools debug mode is turned off by default in Vizro apps. Dash dev tools debug mode can be turned on by using `debug=True` in the `run()` method, eg.

    `Vizro().build(dashboard).run(debug=True)`

    (Note: this is the equivalent of enabling Dash dev tools via the `app.run()` method as described in [Dash documentation](https://dash.plotly.com/devtools))

    In additon, some errors generated at run time can also be viewed via the browser console (for example in `Chrome` see `View > Developer > Developer Tools > Console`)

    #### Re-loading the dashboard

    [Code reloading and hot reloading](https://dash.plotly.com/devtools#code-reloading-&-hot-reloading) can be enabled by turning on debug mode (as described above)

    This can improve the developer experience by allowing the front-end to automatically refresh from the code, whenever dashboard configuration updates are made

## Jupyter
The dashboard application can be launched in a Jupyter environment in `inline`, `external`, and `jupyterlab` mode.
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

??? info "Debugging and Re-loading"

    #### Debugging

    Dash dev tools debug mode is turned off by default in Vizro apps. Dash dev tools debug mode can be turned on by using `debug=True` in the `run()` method, eg.

    `Vizro().build(dashboard).run(debug=True)`

    (Note: this is the equivalent of enabling Dash dev tools via the `app.run()` method as described in [Dash documentation](https://dash.plotly.com/devtools)).
    Code reloading and hot reloading does not work from a Jupyter notebook, even if Dash dev tools debug mode is enabled

    In additon, some errors generated at run time can also be viewed via the browser console (for example in `Chrome` see `View > Developer > Developer Tools > Console`)

    #### Re-loading the dashboard

    When reloading the dashboard to reflect changes in the dashboard configuration in Jupyter, the entire Jupyter kernel must currently be re-started and re-run

## Gunicorn
!!!warning "In production"
    In production, it is recommended **not** to use the default Flask server. One of the options here is Gunicorn. It is easy to scale the application to serve more users or run more computations, run more "copies" of the app in separate processes.

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
in the command line. For more Gunicorn configuration options, please refer to [Gunicorn documentation](https://docs.gunicorn.org/).

## Deployment

A Vizro app wraps a Dash app, which itself wraps a Flask app. Hence to deploy a Vizro app, similar guidance applies as for the underlying frameworks:

- [Flask deployment documentation](https://flask.palletsprojects.com/en/2.0.x/deploying/)
- [Dash deployment documentation](https://dash.plotly.com/deployment)

In particular, `app = Vizro()` exposes the Flask app through `app.dash.server`. As in the [above example with Gunicorn](#gunicorn), this provides the application instance to a WSGI server.

[`Vizro`][vizro.Vizro] accepts `**kwargs` that are passed through to `Dash`. This allows you to configure the underlying Dash app using the same [argumentst that are available](https://dash.plotly.com/reference#dash.dash) in `Dash`. For example, in a deployment context, you might like to specify a custom `url_base_pathname` to serve your Vizro app at a specific URL rather than at your domain root.
