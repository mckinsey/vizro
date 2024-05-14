# Example dashboard code

This page explains the dashboard code examples found in the `examples` folder of the [Vizro GitHub repository](https://github.com/mckinsey/vizro/tree/main/vizro-core/examples).

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

## Vizro features
The [`examples/features` folder](https://github.com/mckinsey/vizro/tree/main/vizro-core/examples/features) of the `vizro-core` package within [Vizro's GitHub repository](https://github.com/mckinsey/vizro) contains an example that illustrates Vizro's features. The code is available as a Python script, plus there is an alternative `yaml_version` that offers the same example as the pydantic model but via YAML configuration.

!!! info "Ways to configure a dashboard"

    In most cases, the pydantic model should be your preferred method of dashboard configuration, but you can also [define a dashboard with YAML, JSON, or as a Python dictionary](../user-guides/dashboard.md).

## Examples from Vizro users

We maintain a separate, curated page of [videos, blog posts, and examples of Vizro usage from our community](your-examples.md).
