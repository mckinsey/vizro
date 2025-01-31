# How to run your dashboard in development

Typically when you create a dashboard, there are two distinct stages:

1. Development. This is when you build your app. You make frequent changes to your code and want a simple way to see how the dashboard looks after each change. At this point, you may, or may not, want to make it possible for other people to access your dashboard.
1. Production. When you complete development of your app, you _deploy_ it to production. The dashboard should be accessible to other people.

This page describes methods to run your dashboard _in development_. When you are ready to deploy your app to production, read our [guide to deployment](deploy.md).

Vizro is built on top of [Dash](https://dash.plotly.com/), which itself uses [Flask](https://flask.palletsprojects.com/). Most of our guidance on how to run a Vizro app in development or production is very similar to guidance on Dash and Flask.

!!! note
    There are many possible workflows depending on your requirements. The above describes a simple workflow that applies to many people but is not suitable for everyone. For example:

    - If you are the only user of your app then the process is often simpler since you might never want to deploy to production.
    - If there are multiple people involved with development then you will need some way to coordinate code changes, such as a [GitHub repository](https://github.com/) or [Hugging Face Space](https://huggingface.co/spaces).
    - You might want to use _authentication_ to restrict access to your app.
    - You might want to update your dashboard after it has been put into production. There is then a cycle of repeated development and deployment.
    - There might be additional stages or _environments_ for Quality Assurance (QA) to test that the app works correctly before it is deployed.

## Development server

The most common way to run your dashboard in development is to run it _locally_ (on your own computer) using the Flask development server.

1. Create a Python file named `app.py` that ends with the line `Vizro().build(dashboard).run()`.
1. Run the command `python app.py` in your terminal.
1. Go to [http://127.0.0.1:8050/](http://127.0.0.1:8050/) to see your app.

```python
from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm

iris = px.data.iris()

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
```

The `run` method wraps [Dash's run method](https://dash.plotly.com/reference#app.run), and all arguments are passed through to Dash. Particularly useful ones are:

- `port`. If not specified, this defaults to `8050`. If you run multiple dashboards on your computer then you may need to avoid a clash by specifying a different port with, for example, `run(port=8051)`.
- `debug`. This is described more below in the [section on debugging](#automatic-reloading-and-debugging).
- `jupyter_mode`. This is described more below in the [section on Jupyter](#jupyter).

!!! warning "Use only for local development"
    The Flask development server is [intended for local development only](https://flask.palletsprojects.com/en/3.0.x/deploying/) and should not be used when deploying a Vizro dashboard to production. See our [guide to deployment](deploy.md) for information on how to deploy.

### Automatic reloading and debugging

While developing, you often make frequent changes to your code and want to see how the dashboard looks after each change. It can be slow and tedious to manually restart your dashboard every time you want to see your changes. You can set your dashboard to automatically refresh whenever code changes.

To do this, turn on [Dash Dev Tools](https://dash.plotly.com/devtools) by setting `debug=True` in the `run()` method: `Vizro().build(dashboard).run(debug=True)`. This switches on [code reloading and hot reloading](https://dash.plotly.com/devtools#code-reloading-&-hot-reloading) as well as several other features that are useful during development, such as detailed in-app error reporting. Some errors generated at run time can also be viewed via the browser console (for example, in Chrome, see `View > Developer > Developer Tools > Console`).

Dash Dev Tools can also be [configured using environment variables](https://dash.plotly.com/devtools#configuring-with-environment-variables). For example, setting the environment variable `DASH_DEBUG=true` is equivalent to setting `debug=True` in the `run()` method.

## Jupyter

If you develop in a Jupyter notebook or JupyterLab then you should use exactly the [same code as above](#development-server):

```python
from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm

iris = px.data.iris()

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
```

This runs Vizro using the Flask development server and shows the resulting dashboard inline in your notebook. You can change where the dashboard appears with the [`jupyter_mode` argument](https://dash.plotly.com/dash-in-jupyter). For example, `run(jupyter_mode="external")` provides a link to open the dashboard in a new window.

!!! note "Reloading and debugging"
    Code reloading and hot reloading do not work in Jupyter. There are two alternatve methods to reload the dashboard after you change your code:

    - Restart the Jupyter kernel and re-run your notebook.
    - Add a cell containing `from vizro import Vizro; Vizro._reset()` to the top of your notebook and re-run it before you re-run your code. With this method, there is no need to restart the Jupyter kernel.

## PyCafe

The easiest way to run a dashboard is to work on the code live on [PyCafe](https://py.cafe/).

Most of the Vizro documentation examples have a link below the code that reads "[Run and edit this code in PyCafe](https://py.cafe/vizro-official/vizro-iris-analysis)". Follow the link to open the code in PyCafe within an editor, such as the one below, which displays the dashboard and the code side by side.

<figure markdown="span">
  ![PyCafe editor](../../assets/user_guides/run/pycafe_editor.png)
  <figcaption>Enter your dashboard code on the left, and see the results immediately reflected in the app on the right.</figcaption>
</figure>

You can use [PyCafe](https://py.cafe/snippet/vizro/v1) snippet mode to experiment with your own Vizro dashboards by dropping code into a new project.
