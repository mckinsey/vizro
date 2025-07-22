# First dashboard tutorial

Vizro-MCP provides a prompt template called `create_starter_dashboard.txt` that you can use, if your MCP client allows templates, to generate a basic starter dashboard.

You can alternatively use this prompt to ask Vizro-MCP to create a dashboard:

```text
Create a Vizro dashboard to analyze the iris dataset. Make a scatter plot of sepal dimensions and a species filter. Use the dark theme.
```


Vizro-MCP calls the appropriate tools to plan the dashboard, access the public Iris dataset, and create the configuration automatically.  It will generate code similar to the following and open a link to display the dashboard in [PyCafe](https://py.cafe/). (If you want to see the dashboard for the code below, click on the **Run and edit this code in Py.Cafe** link).

!!! example "First dashboard"

    === "app.py"

        ```{.python pycafe-link}
		############ Imports ##############
		import vizro.plotly.express as px
		import vizro.models as vm
		from vizro import Vizro
		import pandas as pd
		from vizro.managers import data_manager
		
		
		####### Data Manager Settings #####
		data_manager["iris_data"] = pd.read_csv(
		    "https://raw.githubusercontent.com/plotly/datasets/master/iris-id.csv"
		)
		
		########### Model code ############
		model = vm.Dashboard(
		    pages=[
		        vm.Page(
		            components=[
		                vm.Graph(
		                    id="scatter_plot",
		                    type="graph",
		                    figure=px.scatter(
		                        data_frame="iris_data",
		                        x="sepal_length",
		                        y="sepal_width",
		                        color="species",
		                        hover_data=["petal_length", "petal_width"],
		                    ),
		                    title="Sepal Dimensions by Species",
		                )
		            ],
		            title="Iris Data Analysis",
		            controls=[
		                vm.Filter(
		                    id="species_filter",
		                    type="filter",
		                    column="species",
		                    targets=["scatter_plot"],
		                    selector=vm.Dropdown(type="dropdown", multi=True),
		                )
		            ],
		        )
		    ],
		    theme="vizro_dark",
		    title="Iris Dashboard",
		)
		
		Vizro().build(model).run()

        ```

    


