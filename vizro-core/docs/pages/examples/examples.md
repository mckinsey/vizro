# Vizro examples

## Vizro live demo
For an example of Vizro in action, take a look at the live demo running at [vizro.mckinsey.com](https://vizro.mckinsey.com), which uses the [Plotly gapminder data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.gapminder).

The dashboard launches with a home page that offers four other pages:

* Variable analysis: Analyzes population, GDP per capita and life expectancy on country and continent level.
* Relationship analysis: Investigates the interconnection between population, GDP per capita and life expectancy.
* Benchmark analysis: Explores how the metrics differ for each country and offers the option to export data for further investigation.
* Continent summary: Summarizes the main findings for each continent.


You can find the code for each of the charts, for each page of the dashboard, in the `examples` folder of the `vizro-core` package, within [Vizro's GitHub repository](https://github.com/mckinsey/vizro). The code is available as a [`.py` file](https://github.com/mckinsey/vizro/blob/main/vizro-core/examples/demo/app.py) or as a [Jupyter Notebook](https://github.com/mckinsey/vizro/tree/main/vizro-core/examples/demo/jupyter_version).

!!! info

    If you have any problems running the example code, please [raise an issue](https://github.com/mckinsey/vizro/issues) on the Vizro repository.

The Vizro demo is deployed...

<!-- TO DO -- I need a bit of help here!

* Explain in brief how we deploy it, to help others wanting to do the same
* Probably should link to https://vizro.readthedocs.io/en/stable/pages/user-guides/run/#deployment
-->

## Vizro features
The [`examples/features` folder](https://github.com/mckinsey/vizro/tree/main/vizro-core/examples/features) of the `vizro-core` package within [Vizro's GitHub repository](https://github.com/mckinsey/vizro) contains an example that illustrates all Vizro's features. The code is available as a Python script, and there is an alternative `yaml_version` that offers the same example but via YAML configuration.

<!-- TO DO -- I need a bit of help here!

* Anything to add about the YAML config -- I don't think we've documented this much elsewhere in the docs have we?
* Any differences between the two
* Preferred way of working?
-->

## Example in the _dev folder

<!-- TO DO -- I need a bit of help here!

* What is this? Should a user be looking at it? Is the name suitable?
-->
