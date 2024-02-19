# Get started with Vizro

This tutorial introduces Vizro. It is a step-by-step guide to create a first dashboard and is designed to equip you with the knowledge to explore the documentation further.

If you want a more complete tutorial exploring more of the available features, please see the [Explore Vizro tutorial](../tutorials/explore_components.md).


## Let's get started!

### 1. Install Vizro and its dependencies

If you haven't already installed Vizro, follow the [installation guide](../user_guides/install.md) to do so inside a virtual environment.

If you consider yourself a beginner to python and/or virtual environments, there is also a section that avoids any use of terminals and relies only upon a graphical user interface.

### 2. Open a Jupyter notebook

A good way to initially explore Vizro is from inside a Jupyter notebook. If you haven't used one of these before, you may need to install the Jupyter package:

```console
pip install jupyter
```

From the terminal window, with the virtual environment you installed Vizro in active, start a new notebook as follows:

```console
jupyter notebook
```

The command opens a browser tab and you can navigate to your preferred folder for this new project. Create a new notebook `Python 3 (ipykernel)` notebook from the "New" dropdown.

??? tip "Beginners/Code novices"
    If you followed the beginners steps in the the [installation guide](../user_guides/install.md), you should already be set, and you can continue below.


Confirm that Vizro is installed by typing the following into a cell in the notebook and running it.

```py
import vizro

print(vizro.__version__)
```

You should see a return output of the form `0.1.0`.

### 3. Create your first dashboard

You can now paste the below example into a jupyter notebook cell (or a python script), run it, and see the results.

!!! example "Dashboard Configuration Syntaxes"
    === "Code for the cell"
        ```py
        import vizro.plotly.express as px
        from vizro import Vizro
        import vizro.models as vm

        df = px.data.iris()

        page = vm.Page(
            title="My first dashboard",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
                vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
            ],
            controls=[
                vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "Result"
        [![Dashboard]][Dashboard]

    [Dashboard]: ../../assets/user_guides/dashboard/dashboard.png

After running the dashboard, you can access the dashboard by typing `localhost:8050` in the browser of your choice.

### 4. Explore further

You are now ready to explore our documentation further, as you can now easily evaluate all examples.

One place to start would be the more complete [Explore Vizro tutorial](../tutorials/explore_components.md).
