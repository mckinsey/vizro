# How to use local or remote data

You can ask the LLM to create specific dashboards based on local or remote data if you already have an idea of what you want. Example prompts could be:

> _Create a Vizro dashboard with one page, a scatter chart, and a filter based on `<insert absolute file path or public URL>` data._

> _Create a simple two page Vizro dashboard, with first page being a correlation analysis of `<insert absolute file path or public URL>` data, and the second page being a map plot of `<insert absolute file path or public URL>` data_

You can find a set of sample CSVs to try out in the [Plotly repository](https://github.com/plotly/datasets/tree/master).

!!! Tip "PyCafe cannot display charts that use local data"

    Vizro-MCP will typically open your chart or dashboard code in PyCafe so you can visualize and interact with it. PyCafe can only work with data that can be downloaded from a public link. If your data is stored locally, you should copy the generated code into a `.py` file to run where it can access the data.

You can even ask for a dashboard without providing data:

> _Create a Vizro dashboard with one page, a scatter chart, and a filter._

In general, it helps to specify Vizro in the prompt and to keep it as precise (and simple) as possible.
