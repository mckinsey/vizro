# Example dashboard code

This page explains the dashboard code examples found in the `examples` folder of the [Vizro GitHub repository](https://github.com/mckinsey/vizro/tree/main/vizro-core/examples).

## Check out the gallery!
For a gallery of examples of Vizro in action, take a look at [vizro.mckinsey.com](https://vizro.mckinsey.com).

Among others, you'll find links to a multi-featured example dashboard that uses the [Plotly gapminder data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.gapminder). The dashboard launches with a home page that offers four other pages:

* Variable analysis: Analyzes population, GDP per capita and life expectancy on country and continent level.
* Relationship analysis: Investigates the interconnection between population, GDP per capita and life expectancy.
* Benchmark analysis: Explores how the metrics differ for each country and offers the option to export data for further investigation.
* Continent summary: Summarizes the main findings for each continent.


You can find the code for that dashboard on our [Hugging Face gapminder space](https://huggingface.co/spaces/vizro/demo-gapminder). The code is available as a [`.py` file](https://huggingface.co/spaces/vizro/demo-gapminder/blob/main/app.py).

!!! note

    If you have any problems running the example code, please [raise an issue](https://github.com/mckinsey/vizro/issues) on the Vizro repository.

## Vizro features
Within the GitHub repository, the [`examples/dev` folder](https://github.com/mckinsey/vizro/tree/main/vizro-core/examples/dev) of `vizro-core` contains example code as a Python script and as the alternative `yaml_version` that offers the same example as the pydantic model but via YAML configuration.

The pydantic model should be your preferred method of dashboard configuration, but you can also [define a dashboard with YAML, JSON, or as a Python dictionary](../user-guides/dashboard.md).

## Examples from Vizro users

We maintain a separate, curated page of [videos, blog posts, and examples of Vizro usage from our community](your-examples.md).
